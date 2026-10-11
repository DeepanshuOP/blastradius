"""Ask BlastRadius (exploratory, D-61): a retrieval-grounded assistant with citations.

A developer asks about a change or a failing test; the agent retrieves from three sources (code, BR-Bench failure
history, the repo's docs), shows the model only that context and asks it to cite every claim as `[S1]`...`[S8]`.
For impact questions the E1 ranker's top-5 tests with their SHAP reasons are one more context block.

Only this module's `AskAgent.ask` may call an LLM (through `src.agents.llm`, cached and replayable); retrieval,
question routing and citation checking are deterministic. Nothing here is imported by E1, E2 or `make tables`.
"""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.rag.knowledge import KDoc, Knowledge

QUESTION_TYPES = ("impact", "history", "test-failure", "general")
K_TOTAL = 8
PER_SOURCE = 4
# Which sources a question type searches (the rest default to all three). A "has this failed before" question is
# answered from failure history only: code and docs cannot say when a test failed, and they crowd out the evidence.
SOURCES_BY_TYPE = {"history": ("failure",)}
ITEM_CHARS = 1200
MAX_COMPLETION = 800
NOT_IN_CONTEXT = "not in the context"

SYSTEM = (
    "You are BlastRadius, an assistant for developers reading CI results. Answer ONLY from the numbered context "
    "items you are given. Cite every claim with the item number in square brackets, for example [S2]; a sentence "
    "with no citation is not allowed. Never cite a number that is not in the context. If the context does not "
    f"contain the answer, reply exactly: {NOT_IN_CONTEXT}. Do not use outside knowledge. Keep the answer under 150 words."
)

# Question routing: first matching rule wins. Plain rules, no model.
_IMPACT = re.compile(r"\b(at risk|risk|impact|blast radius|what breaks|affected|affect|if i (change|edit|modify|touch))\b", re.I)
_HISTORY = re.compile(r"\b(before|earlier|previous(ly)?|history|again|last time|happened|ever|recurr\w*|seen)\b", re.I)
_FAILURE = re.compile(r"\b(why|fail\w*|error|broken|break|breaks|traceback|exception)\b|test_\w+|::", re.I)
_TEST_ID = re.compile(r"[\w./-]+::[\w.\[\]-]+|\btest_\w+")
_FILE = re.compile(r"[\w./-]+\.(?:py|java)\b")
_CITE = re.compile(r"\[S(\d+)\]")


def classify_question(question: str) -> str:
    """`impact`, `history`, `test-failure` or `general` (rule order: impact, history, test-failure)."""
    if _IMPACT.search(question):
        return "impact"
    if _HISTORY.search(question):
        return "history"
    if _FAILURE.search(question):
        return "test-failure"
    return "general"


def parse_citations(answer: str) -> list[int]:
    """The `[Sk]` numbers in an answer, in order of first appearance."""
    seen: list[int] = []
    for m in _CITE.finditer(answer or ""):
        n = int(m.group(1))
        if n not in seen:
            seen.append(n)
    return seen


@dataclass
class Citation:
    """One context item the answer may cite."""

    id: str            # S1
    source: str        # code | failure | doc | e1
    ref: str           # file:line, run id, or section
    title: str


@dataclass
class AskResult:
    """What `AskAgent.ask` returns."""

    question: str
    qtype: str
    answer: str | None             # None when no model was available (retrieval only)
    citations: list[Citation]
    context: list[dict]            # [{"id", "source", "ref", "text"}] exactly what the model saw
    cited: list[int] = field(default_factory=list)
    faithful: bool | None = None   # every [Sk] points to a retrieved item (None without an answer)
    model: str = ""
    tokens: int = 0
    from_cache: bool = False
    notes: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        """Plain dict for JSON."""
        return asdict(self)


def check_citations(answer: str, n_items: int) -> tuple[list[int], bool]:
    """`(cited numbers, every one is within 1..n_items)`."""
    cited = parse_citations(answer)
    return cited, all(1 <= c <= n_items for c in cited)


def _clip(text: str) -> str:
    return text if len(text) <= ITEM_CHARS else text[:ITEM_CHARS] + " ..."


def build_user(question: str, items: list[dict]) -> str:
    """The user message: the question, then the numbered context."""
    ctx = "\n\n".join(f"[{it['id']}] ({it['source']}, {it['ref']})\n{_clip(it['text'])}" for it in items)
    return f"Question: {question}\n\nContext:\n{ctx}\n\nAnswer with citations like [S1]."


class AskAgent:
    """Retrieve, then answer from the retrieved context only."""

    def __init__(self, knowledge: Knowledge, repo: Path | None = None, llm=None, ranker=None) -> None:
        """Create the agent.

        Args:
            knowledge: The index over code, failure history and docs.
            repo: Working copy for impact questions (E1 ranker); None disables the ranker block.
            llm: Object with `chat(system, user, max_completion_tokens)`; None answers with retrieval only.
            ranker: `rank_tests`-compatible callable (default: `src.features.online.rank_tests`).
        """
        self.kb, self.repo, self.llm, self._ranker = knowledge, repo, llm, ranker

    def _e1_block(self, question: str) -> tuple[dict | None, str]:
        """The E1 ranker's top-5 tests as one context item, and a note when it cannot be produced."""
        if self.repo is None:
            return None, "impact question but no repository was given: E1 ranker not run"
        from src.features.online import rank_tests, tracked_files

        tracked = tracked_files(self.repo)
        named = [f for f in _FILE.findall(question)]
        changed = sorted({t for n in named for t in tracked if t == n or t.endswith("/" + n)})
        if not changed:
            return None, "no tracked source file named in the question: E1 ranker not run"
        ranked = (self._ranker or rank_tests)(self.repo, changed, 0, explain_top=3)
        if not ranked:
            return None, "E1 model unavailable for this repository: ranker block omitted"
        lines = [f"E1 ranker (LightGBM, trained on BR-Bench), tests most at risk if {', '.join(changed)} changes:"]
        for i, r in enumerate(ranked[:5], 1):
            why = "; ".join(r.top_features) if r.top_features else "no single feature dominates"
            lines.append(f"{i}. {r.test_file} score {r.score:.3f} because {why}")
        return {"source": "e1", "ref": "src/models/e1_ranker.py", "title": "E1 ranker top-5",
                "text": "\n".join(lines)}, ""

    def ask(self, question: str, k: int = K_TOTAL) -> AskResult:
        """Answer one question.

        Returns:
            The result: answer (None without a model), citations for every retrieved item, and the context.
        """
        qtype = classify_question(question)
        notes: list[str] = []
        block = None
        if qtype == "impact":
            block, note = self._e1_block(question)
            if note:
                notes.append(note)
        only = SOURCES_BY_TYPE.get(qtype)
        hits: list[KDoc] = self.kb.search(question, k - (1 if block else 0), PER_SOURCE if only is None else k,
                                          sources=only)
        items: list[dict] = []
        cites: list[Citation] = []
        for d in hits:
            sid = f"S{len(items) + 1}"
            items.append({"id": sid, "source": d.source, "ref": d.ref, "text": d.text})
            cites.append(Citation(sid, d.source, d.ref, f"{d.file} :: {d.qualname}"))
        if block:
            sid = f"S{len(items) + 1}"
            items.append({"id": sid, "source": "e1", "ref": block["ref"], "text": block["text"]})
            cites.append(Citation(sid, "e1", block["ref"], block["title"]))
        res = AskResult(question, qtype, None, cites, items, notes=notes)
        if self.llm is None or not hasattr(self.llm, "chat"):
            res.notes.append("no model configured: retrieval only")
            return res
        r = self.llm.chat(SYSTEM, build_user(question, items), MAX_COMPLETION)
        res.answer = r.text.strip()
        res.model, res.from_cache = r.model, r.from_cache
        res.tokens = int((r.usage or {}).get("total_tokens", 0))
        res.cited, res.faithful = check_citations(res.answer, len(items))
        return res


def score_answers(results: list[AskResult]) -> dict:
    """Citation faithfulness over answered questions: every `[Sk]` real, and at least one citation."""
    ans = [r for r in results if r.answer is not None]
    n = len(ans)
    abstain = [r for r in ans if NOT_IN_CONTEXT in r.answer.lower()]
    return {"answered": n,
            "all_citations_real": sum(1 for r in ans if r.faithful and r.cited),
            "all_citations_real_or_none": sum(1 for r in ans if r.faithful),
            "cites_at_least_one": sum(1 for r in ans if r.cited),
            "abstained": len(abstain)}


def chat_llm(provider: str | None, cache_path: Path):
    """A provider with `.chat` (Groq, cached at `cache_path`), or None for the offline provider.

    `BR_LLM_CACHE_DIR` overrides the cache directory (the PR-bot workflow uploads it as an artifact).
    """
    from src.agents.llm import GroqLLM, get_llm
    from src.agents.llm_cache import LLMCache

    llm = get_llm(provider)
    if isinstance(llm, GroqLLM):
        d = os.environ.get("BR_LLM_CACHE_DIR")
        llm.cache = LLMCache(Path(d) / cache_path.name if d else cache_path)
    return llm if hasattr(llm, "chat") else None
