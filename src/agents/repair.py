"""Repair Agent (D-58): the ONLY module that may call an LLM.

Given a failing change, it triages the failure, retrieves at most three code chunks, asks
the model for one SEARCH/REPLACE patch, applies it strictly and accepts it only if the
FULL suite passes (target tests and every test that was green before).

Arms (same model, same caps, same output format; they differ only in how the <= 3 chunks
are chosen, which is retrieval and costs no tokens):

R0  no LLM: notify only (what Jenkins does)
R1  log-only: BM25 over every source function, queried with identifiers from the failing
    test ids and output (the inputs LogSage / CI-Bench / CI-Repair-Bench give the model)
R2  change-aware: functions touched by the PR diff, ranked by the same BM25; ties broken by
    the E1 model's score of the test file paired with the changed file; the triage class
    is stated in the prompt
R3  R2 plus up to two retries, each feeding back the failing output (<= 1,000 chars)
R4  (exploratory, v2.1, D-61) R2's task with retrieved context: chunks chosen by change-aware hybrid retrieval, plus the
    fix history of the top chunk and up to two similar functions of the same repository, input capped at 3,500 tokens.
    One attempt, like R2. R0-R3 prompts are unchanged.

One attempt is one LLM call with the input capped near 3,000 tokens.
"""

from __future__ import annotations

import ast
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.eval.baselines import path_token_list

log = logging.getLogger(__name__)

ARMS = ("R0", "R1", "R2", "R3")      # the pre-registered arms (033); everything that iterates ARMS is unchanged
RAG_ARMS = ("R4",)                    # exploratory (D-61)
ALL_ARMS = ARMS + RAG_ARMS
R4_INPUT_TOKENS = 3500                # system + user message, estimated as characters / 3.5 like `estimate_run`
MAX_CHUNKS = 3
CONTEXT_LINES = 20
OUTPUT_CHARS = 1500
RETRY_OUTPUT_CHARS = 1000
MAX_RETRIES = 2

SYSTEM = (
    "You are a careful software engineer fixing a failing test suite. Reply with SEARCH/REPLACE blocks only, "
    "no explanation. Each block is exactly:\n"
    "path/to/file.py\n<<<<<<< SEARCH\nexact lines to replace, copied verbatim\n=======\nreplacement lines\n"
    ">>>>>>> REPLACE\n"
    "The SEARCH text must appear exactly once in the file. Change as little as possible. Only edit files shown."
)
_BLOCK = re.compile(r"^(?P<path>[^\n<>=]+?)[ \t]*\n<<<<<<< SEARCH\n(?P<search>.*?)\n?=======\n(?P<replace>.*?)\n?>>>>>>> REPLACE",
                    re.S | re.M)
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_NOISE = {"assert", "self", "error", "none", "true", "false", "def", "return", "the", "and", "test", "tests",
          "traceback", "file", "line", "pytest", "python", "site", "packages", "lib", "raise", "failed", "assertionerror"}


@dataclass
class Chunk:
    """One candidate code location shown to the model."""

    file: str
    qualname: str
    start: int
    end: int
    focus: int
    score: float = 0.0
    text: str = ""


@dataclass
class FailureReport:
    """Everything the agent is told about one failing change."""

    failing: list[dict]            # [{"test_id": ..., "output": ...}]
    pr_diff: str = ""
    triage: str = "mine"           # mine | inherited | flaky
    changed_files: list[str] = field(default_factory=list)


@dataclass
class Attempt:
    """One model call and what became of its answer."""

    prompt_chars: int
    response: str
    usage: dict | None
    from_cache: bool
    applied: bool
    error: str = ""
    files: dict[str, str] = field(default_factory=dict)  # path -> patched content


@dataclass
class RepairResult:
    """Outcome of the agent on one failure."""

    arm: str
    action: str                    # repair | rerun | ignore | notify
    chunks: list[Chunk] = field(default_factory=list)
    attempts: list[Attempt] = field(default_factory=list)
    accepted: bool = False
    note: str = ""


# ---- routing -------------------------------------------------------------------------------
def route(triage: str) -> str:
    """What to do with a failure of a given triage class.

    `mine` goes to repair; `flaky` gets a rerun suggestion; `inherited` is reported as
    already failing on the base and receives no patch.
    """
    return {"mine": "repair", "flaky": "rerun", "inherited": "ignore"}.get(triage, "repair")


# ---- retrieval -----------------------------------------------------------------------------
def index_functions(repo: Path, files: list[str]) -> list[Chunk]:
    """Every top-level function and method of the given source files, as chunks (unscored)."""
    out: list[Chunk] = []
    for f in files:
        try:
            src = (repo / f).read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        lines = src.splitlines()

        def visit(node: ast.AST, prefix: str) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    q = f"{prefix}{child.name}"
                    start = min([child.lineno] + [d.lineno for d in child.decorator_list])
                    out.append(Chunk(f, q, start, child.end_lineno, start, 0.0, "\n".join(lines[start - 1:child.end_lineno])))
                elif isinstance(child, ast.ClassDef):
                    visit(child, f"{prefix}{child.name}.")

        visit(tree, "")
    return out


def query_tokens(failing: list[dict], output_chars: int = OUTPUT_CHARS) -> list[str]:
    """Query for retrieval: tokens of the failing test ids plus identifiers in their output."""
    toks: list[str] = []
    for t in failing:
        toks += path_token_list(t["test_id"].replace("::", "/").replace(".", "/"))
    text = "\n".join(t.get("output", "") for t in failing)[:output_chars]
    for w in _WORD.findall(text):
        for part in path_token_list(w):
            if len(part) >= 3 and part not in _NOISE:
                toks.append(part)
    return [t for t in toks if t not in _NOISE]


def _doc_tokens(c: Chunk) -> list[str]:
    toks = path_token_list(c.qualname.replace(".", "/") + "/" + c.file)
    for w in _WORD.findall(c.text):
        toks += [p for p in path_token_list(w) if len(p) >= 3 and p not in _NOISE]
    return toks


def bm25_scores(docs: list[list[str]], query: list[str], k1: float = 1.2, b: float = 0.75) -> list[float]:
    """Okapi BM25 (same formula as `src.eval.baselines.bm25_scores`) with a hash-seed-independent summation order.

    The baseline sums over `set(query)`, whose iteration order depends on `PYTHONHASHSEED`; float addition is not
    associative, so scores could differ in the last bits between processes. Prompts must replay from the cache, so
    the terms are summed in sorted order here. The baseline itself is left alone: it feeds `make tables`.
    """
    n = len(docs)
    if n == 0 or not query:
        return [0.0] * n
    avgdl = sum(len(d) for d in docs) / n or 1.0
    df: Counter[str] = Counter(t for d in docs for t in set(d))
    out = [0.0] * n
    terms = sorted(set(query))
    for i, d in enumerate(docs):
        tf = Counter(d)
        norm = k1 * (1 - b + b * len(d) / avgdl)
        for t in terms:
            if t in tf:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                out[i] += idf * tf[t] * (k1 + 1) / (tf[t] + norm)
    return out


def changed_line_ranges(pr_diff: str) -> dict[str, list[int]]:
    """Added or replaced line numbers (post-image) per file in a unified diff."""
    out: dict[str, list[int]] = {}
    cur = None
    new_line = 0
    for ln in pr_diff.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:]
            out.setdefault(cur, [])
        elif ln.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", ln)
            new_line = int(m.group(1)) if m else 0
        elif cur is not None and ln.startswith("+") and not ln.startswith("+++"):
            out[cur].append(new_line)
            new_line += 1
        elif cur is not None and ln.startswith("-") and not ln.startswith("---"):
            pass  # a deletion consumes no post-image line
        elif cur is not None and ln.startswith(" "):
            new_line += 1
    return out


def select_chunks(arm: str, repo: Path, source_files: list[str], report: FailureReport,
                  tie_break: Callable[[str], float] | None = None) -> list[Chunk]:
    """The <= 3 chunks an arm shows the model.

    Args:
        arm: `R1` (all functions) or `R2` / `R3` (functions touched by the diff).
        repo: Working tree in the state under repair (PR applied).
        source_files: Repo-relative non-test source files.
        report: The failure.
        tie_break: `file -> priority` (higher first) used only among equal BM25 scores (R2/R3).

    Returns:
        Up to :data:`MAX_CHUNKS` chunks, best first, with `focus` set to the line shown around.
    """
    funcs = index_functions(repo, source_files)
    if arm in ("R2", "R3"):
        ranges = changed_line_ranges(report.pr_diff)
        touched = []
        for c in funcs:
            hit = [ln for ln in ranges.get(c.file, []) if c.start <= ln <= c.end]
            if hit:
                c.focus = hit[0]
                touched.append(c)
        pool = touched or funcs
    else:
        pool = funcs
    q = query_tokens(report.failing)
    scores = bm25_scores([_doc_tokens(c) for c in pool], q)
    for c, s in zip(pool, scores):
        c.score = float(s)
    prio = tie_break or (lambda f: 0.0)
    ranked = sorted(pool, key=lambda c: (-round(c.score, 9), -prio(c.file), c.file, c.start))[:MAX_CHUNKS]
    if arm == "R1":  # focus on the line sharing most tokens with the query
        qs = set(q)
        for c in ranked:
            best, best_n = c.start, -1
            for i, ln in enumerate(c.text.splitlines()):
                n = len(qs & set(path_token_list(ln)))
                if n > best_n:
                    best, best_n = c.start + i, n
            c.focus = best
    return ranked


CLAMPED: list[str] = []   # one entry per chunk whose focus or range had to be clamped (each one is a bug)


def render_chunk(c: Chunk, repo: Path | None = None) -> str:
    """The function's lines within +-CONTEXT_LINES of its focus line, numbered, under a path header.

    Rendered from `c.text`, the exact text the chunk was indexed from, never from a second read of the file:
    a chunk's line numbers and the lines shown for them cannot come from two versions of the tree. `repo` is
    accepted for call compatibility and unused.

    A focus line outside the function is clamped into it and logged as an error (and recorded in
    :data:`CLAMPED`): it means the caller built the chunk from different content than it indexed.
    """
    body_lines = c.text.splitlines()
    end = min(c.end, c.start + len(body_lines) - 1)
    focus = c.focus
    if not c.start <= focus <= end:
        msg = (f"BUG: chunk {c.file}::{c.qualname} focus line {focus} outside its function ({c.start}-{end}); "
               "clamped. The chunk was built from different content than it was indexed from.")
        log.error(msg)
        CLAMPED.append(msg)
        focus = min(max(focus, c.start), end)
    lo, hi = max(c.start, focus - CONTEXT_LINES), min(end, focus + CONTEXT_LINES)
    body = "\n".join(f"{i:>5}| {body_lines[i - c.start]}" for i in range(lo, hi + 1))
    return f"### {c.file} :: {c.qualname} (lines {lo}-{hi})\n{body}"


_ADDR = re.compile(r"0x[0-9a-fA-F]{5,}")


def clean_feedback(text: str, repo: Path) -> str:
    """Make suite output deterministic before it enters a prompt (replay depends on it).

    Memory addresses in object reprs (`<Foo object at 0x7f3a...>`) and the absolute path of the working
    tree differ from run to run; both are masked. Nothing else is altered.
    """
    return _ADDR.sub("0xADDR", text).replace(str(repo), "<repo>")


def build_prompt(arm: str, report: FailureReport, chunks: list[Chunk], repo: Path, feedback: str = "") -> str:
    """User message: failing tests, output (<= 1,500 chars), triage (R2/R3), the chunks, optional retry feedback."""
    ids = "\n".join(f"- {t['test_id']}" for t in report.failing[:8])
    out = "\n".join(t.get("output", "") for t in report.failing)[:OUTPUT_CHARS]
    parts = [f"Failing tests:\n{ids}", f"Test output (truncated):\n{out}"]
    if arm in ("R2", "R3"):
        parts.append("Triage: this failure is MINE, i.e. caused by the change under review (the tests passed before it).\n"
                     "Files changed by the change: " + ", ".join(sorted(report.changed_files) or ["(unknown)"]))
    parts.append("Candidate code:\n" + "\n\n".join(render_chunk(c, repo) for c in chunks))
    if feedback:
        parts.append("Your previous patch did not make the whole suite pass. Output of the run:\n"
                     + clean_feedback(feedback, repo)[:RETRY_OUTPUT_CHARS])
    parts.append("Reply with SEARCH/REPLACE blocks only.")
    return "\n\n".join(parts)


def estimate_tokens(text: str) -> int:
    """Input-token estimate used by the R4 cap (characters / 3.5, the estimator of `analysis.rq4_repair`)."""
    return int(len(text) / 3.5)


def _r4_sections(report: FailureReport, chunks: list[Chunk], repo: Path, history: list[str], similar: list[Chunk],
                 feedback: str) -> str:
    ids = "\n".join(f"- {t['test_id']}" for t in report.failing[:8])
    out = "\n".join(t.get("output", "") for t in report.failing)[:OUTPUT_CHARS]
    parts = [f"Failing tests:\n{ids}", f"Test output (truncated):\n{out}",
             "Triage: this failure is MINE, i.e. caused by the change under review (the tests passed before it).\n"
             "Files changed by the change: " + ", ".join(sorted(report.changed_files) or ["(unknown)"]),
             "Candidate code:\n" + "\n\n".join(render_chunk(c, repo) for c in chunks)]
    if history:
        parts.append(f"Earlier commits that changed {chunks[0].qualname} (project history, for context):\n"
                     + "\n\n".join(history))
    if similar:
        parts.append("Similar code elsewhere in this repository (reference only, do not edit):\n"
                     + "\n\n".join(render_chunk(c, repo) for c in similar))
    if feedback:
        parts.append("Your previous patch did not make the whole suite pass. Output of the run:\n"
                     + clean_feedback(feedback, repo)[:RETRY_OUTPUT_CHARS])
    parts.append("Reply with SEARCH/REPLACE blocks only.")
    return "\n\n".join(parts)


def build_prompt_r4(report: FailureReport, chunks: list[Chunk], repo: Path, history: list[str], similar: list[Chunk],
                    feedback: str = "", cap: int = R4_INPUT_TOKENS) -> tuple[str, dict]:
    """R4 user message: R2's sections, then fix history, then similar code, within `cap` input tokens.

    Trimming rule (deterministic): while system + user exceeds `cap`, drop the last fix-history item, then (once
    history is empty) the last similar chunk. The target chunks are never trimmed, even if they alone exceed the cap.

    Returns:
        `(prompt, info)` where info has `history`, `similar` (counts kept) and `tokens` (estimate).
    """
    h, sim = list(history), list(similar)
    while True:
        prompt = _r4_sections(report, chunks, repo, h, sim, feedback)
        tokens = estimate_tokens(SYSTEM) + estimate_tokens(prompt)
        if tokens <= cap or not (h or sim):
            return prompt, {"history": len(h), "similar": len(sim), "tokens": tokens}
        if h:
            h.pop()
        else:
            sim.pop()


# ---- applying a patch ----------------------------------------------------------------------
def parse_blocks(text: str) -> list[tuple[str, str, str]]:
    """`(path, search, replace)` triples in a model reply (code fences tolerated)."""
    cleaned = "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("```"))
    return [(m["path"].strip(), m["search"], m["replace"]) for m in _BLOCK.finditer(cleaned)]


def apply_blocks(repo: Path, blocks: list[tuple[str, str, str]], allowed: set[str] | None = None) -> dict[str, str]:
    """Apply SEARCH/REPLACE blocks strictly; returns `{path: new content}` without writing.

    Raises:
        ValueError: If there are no blocks, a path is not allowed or missing, or a SEARCH
            text does not occur exactly once in the file as edited so far.
    """
    if not blocks:
        raise ValueError("no SEARCH/REPLACE blocks in the reply")
    files: dict[str, str] = {}
    for path, search, replace in blocks:
        if allowed is not None and path not in allowed:
            raise ValueError(f"{path} was not one of the files shown")
        p = repo / path
        if not p.is_file() or ".." in Path(path).parts:
            raise ValueError(f"{path} does not exist")
        text = files.get(path, p.read_text(encoding="utf-8"))
        n = text.count(search)
        if not search or n != 1:
            raise ValueError(f"SEARCH text matches {n} times in {path} (must be exactly once)")
        files[path] = text.replace(search, replace, 1)
    return files


class RepairAgent:
    """Triage-routed, retrieval-grounded, validation-gated repair."""

    def __init__(self, llm, arm: str = "R2", max_retries: int = MAX_RETRIES, rag=None, applier=None,
                 context: list[Chunk] | None = None) -> None:
        """Create the agent.

        Args:
            llm: An object with `chat(system, user, max_completion_tokens) -> ChatResult`
                (`GroqLLM`), or an offline provider (then only R0 behaviour is possible).
            arm: One of :data:`ALL_ARMS`.
            max_retries: Extra attempts for R3.
            rag: For R4 only: an object with `select(repo, source_files, report, tie_break) -> list[Chunk]` and
                `extras(repo, chunks, source_files) -> (history: list[str], similar: list[Chunk])`
                (`src.rag.context.RagContext`).
            applier: Replacement for :func:`apply_blocks` with the same signature (the PR bot passes an
                indentation-tolerant one). The default keeps the pre-registered strict behaviour.
            context: Chunks to show instead of the arm's own retrieval (the PR bot's ``BR_LOCALIZE=graph`` passes
                graph-localised chunks). None, the default and the only value E3 uses, keeps the arm's retrieval.
        """
        if arm not in ALL_ARMS:
            raise ValueError(f"unknown arm {arm!r}")
        if arm == "R4" and rag is None:
            raise ValueError("arm R4 needs a RAG context provider (src.rag.context.RagContext)")
        self.llm, self.arm, self.max_retries, self.rag = llm, arm, max_retries, rag
        self.applier = applier or apply_blocks
        self.context = context

    def run(self, repo: Path, source_files: list[str], report: FailureReport,
            validate: Callable[[dict[str, str]], tuple[bool, str]],
            tie_break: Callable[[str], float] | None = None) -> RepairResult:
        """Handle one failure.

        Args:
            repo: Working tree in the failing state (never modified here).
            source_files: Repo-relative non-test source files.
            report: The failure.
            validate: Runs the FULL suite on `{path: content}` applied to a copy and returns
                `(accepted, failing_output)`; accepted means every non-pre-existing test passes.
            tie_break: See :func:`select_chunks`.

        Returns:
            The result. `accepted` is True only when `validate` accepted a patch.
        """
        action = route(report.triage)
        if action == "rerun":
            return RepairResult(self.arm, "rerun", note="triaged flaky: rerun the test, no patch proposed")
        if action == "ignore":
            return RepairResult(self.arm, "ignore", note="triaged inherited: already failing on the base, no patch")
        if self.arm == "R0" or not hasattr(self.llm, "chat"):
            return RepairResult(self.arm, "notify", note="notification only, no model call")
        history: list[str] = []
        similar: list[Chunk] = []
        if self.arm == "R4":
            chunks = self.rag.select(repo, source_files, report, tie_break)
            history, similar = self.rag.extras(repo, chunks, source_files) if chunks else ([], [])
        elif self.context:
            chunks = list(self.context)
        else:
            chunks = select_chunks("R1" if self.arm == "R1" else "R2", repo, source_files, report, tie_break)
        res = RepairResult(self.arm, "repair", chunks)
        feedback = ""
        tries = 1 + (self.max_retries if self.arm == "R3" else 0)
        for i in range(tries):
            if self.arm == "R4":
                prompt, _ = build_prompt_r4(report, chunks, repo, history, similar, feedback)
            else:
                prompt = build_prompt(self.arm, report, chunks, repo, feedback)
            r = self.llm.chat(SYSTEM, prompt, 1500)
            att = Attempt(len(SYSTEM) + len(prompt), r.text, r.usage, r.from_cache, False)
            res.attempts.append(att)
            try:
                att.files = self.applier(repo, parse_blocks(r.text), {c.file for c in chunks})
                att.applied = True
            except ValueError as exc:
                att.error = str(exc)
                feedback = f"(your reply could not be applied: {exc})"
                continue
            ok, out = validate(att.files)
            if ok:
                res.accepted = True
                return res
            feedback = out
        return res
