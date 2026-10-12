"""PR bot (D-63, exploratory): one Markdown comment on a pull request, composed from the existing stages.

    python -m src.agents bot --repo R --base BASE_SHA --head HEAD_SHA --pr N [--no-post]

Stages, in order:

1. **impact**   E1 ranker (`src.features.online.rank_tests`, SHAP reasons) over the files the PR changes. A pull
                request has changed files, not a user story, so the story-keyed Impact agent is not used; its
                ranker is.
2. **regression** `RegressionSuiteAgent`: the at-risk test files first, then the full suite, at the PR head.
3. **triage**   `TriageAgent` per failing test. Each failing test is also run at the base commit and recorded in
                the history first, so "inherited" rests on a run, not only on past history.
4. **repair**   `RepairAgent` arm R3 with up to two retries (<= 3 attempts) for failures triaged `mine`; a patch is
                *validated* only if the FULL suite passes with it (minus tests already failing at the base).
5. **render**   one comment (< 65,000 characters). A suggestion block appears only for a validated patch; any other
                patch is a collapsed diff marked "not validated".

The bot only comments: it never pushes, merges or approves. Writes go through `GitHubForge._write`; its own previous
comment (found by a hidden marker) is edited instead of posting a new one. Inline `suggestion` review comments are
posted only for hunks that lie in the PR diff, because GitHub renders the Apply button only there.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.agents import gitops
from src.agents.impact import ImpactAnalysis, ImpactedTest
from src.agents.regression import RegressionSuiteAgent, run_pytest
from src.agents.repair import FailureReport, RepairAgent, apply_blocks
from src.agents.triage import TriageAgent, failures_of
from src.eval.seeded.build import source_files
from src.features.online import diff_stats, rank_tests
from src.parse.changeset import is_conventional_test_file

MARKER = "<!-- blastradius-bot -->"
SUGGESTION_MARKER = "<!-- blastradius-suggestion:{h} -->"
MAX_COMMENT = 65_000
AT_RISK_ROWS = 10
RESULT_ROWS = 40
TRIAGE_ROWS = 20
MAX_REPAIR_RETRIES = 2          # R3: up to 2 retries, each carrying the failure feedback (3 attempts in all)
MAX_REPAIR_ATTEMPTS = 1 + MAX_REPAIR_RETRIES
_GUTTER = re.compile(r"^\s*\d+\|[ ]?")


@dataclass
class Suggestion:
    """One replace-these-lines hunk of a validated patch, in PR-head coordinates."""

    path: str
    start: int          # first head line replaced (1-based)
    end: int            # last head line replaced
    lines: list[str]    # replacement lines

    def body(self) -> str:
        """The review-comment body with a GitHub suggestion block."""
        text = "\n".join(self.lines)
        return f"```suggestion\n{text}\n```" if self.lines else "```suggestion\n```"


@dataclass
class BotOutcome:
    """Everything one bot run produced."""

    comment: str
    suggestions: list[Suggestion] = field(default_factory=list)
    validated: bool = False
    stats: dict = field(default_factory=dict)


# ---- diff geometry --------------------------------------------------------------------------------
def diff_visible_lines(diff: str) -> dict[str, set[int]]:
    """Head-side line numbers shown in each file's hunks (the lines a review comment may attach to)."""
    out: dict[str, set[int]] = {}
    cur: str | None = None
    n = 0
    for ln in diff.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:]
            out.setdefault(cur, set())
        elif ln.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", ln)
            n = int(m.group(1)) if m else 0
        elif cur is not None and ln.startswith("-") and not ln.startswith("---"):
            continue
        elif cur is not None and (ln.startswith("+") or ln.startswith(" ")) and not ln.startswith("+++"):
            out[cur].add(n)
            n += 1
    return out


def patch_hunks(head_files: dict[str, str], patched: dict[str, str]) -> list[Suggestion]:
    """Replace-lines hunks turning each head file into its patched text (pure insertions anchor on the line above)."""
    out: list[Suggestion] = []
    for path in sorted(patched):
        old, new = head_files.get(path, "").splitlines(), patched[path].splitlines()
        sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            if i1 == i2:                       # insertion: keep the previous line and add after it
                if i1 == 0:
                    continue
                out.append(Suggestion(path, i1, i1, [old[i1 - 1], *new[j1:j2]]))
            else:
                out.append(Suggestion(path, i1 + 1, i2, new[j1:j2]))
    return out


def unified(head_files: dict[str, str], patched: dict[str, str]) -> str:
    """Unified diff of a patch, for the collapsed 'not validated' block."""
    chunks = []
    for path in sorted(patched):
        d = difflib.unified_diff(head_files.get(path, "").splitlines(), patched[path].splitlines(),
                                 f"a/{path}", f"b/{path}", lineterm="", n=2)
        chunks.append("\n".join(d))
    return "\n".join(chunks)


# ---- rendering ------------------------------------------------------------------------------------
def _cell(s: object, n: int = 110) -> str:
    t = str(s).replace("|", "\\|").replace("\n", " ").strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def render_comment(*, pr: int, base: str, head: str, risk: list[dict], ranker: str, results: list[dict],
                   n_total: int, first_failure: int | None, triage: list[dict], repair: dict | None,
                   model: str, tokens: int, notes: list[str] | None = None) -> str:
    """The comment body.

    Args:
        pr: Pull request number.
        base: Base commit.
        head: Head commit.
        risk: At-risk tests, best first: `[{"test", "score", "why"}]`.
        ranker: `e1-lgbm-v1` or `heuristic`.
        results: Test results in execution order (risk first): `[{"test", "outcome", "message"}]`.
        n_total: Number of tests in the full run.
        first_failure: 1-based position of the first failing test in execution order.
        triage: `[{"test", "class", "confidence", "reason"}]` for failing tests.
        repair: None, or `{"validated", "suggestions": [Suggestion], "diff", "files", "attempts", "note"}`.
        model: Model id (or "none").
        tokens: Total tokens used by repair.
        notes: Extra caveats to print.

    Returns:
        Markdown under `MAX_COMMENT` characters. A `suggestion` fence appears only when `repair["validated"]`.
    """
    failed_cases = [r for r in results if r["outcome"] in ("failed", "error")]
    results = _unique_ids(results)            # one row per canonical test id, a failure wins over a pass
    failed = [r for r in results if r["outcome"] in ("failed", "error")]
    # Unit: the canonical test id (the project's join key). It drops the subclass, so an inherited test method run
    # under several subclasses is several executed cases but one id; both counts are printed when they differ.
    ids_note = "" if len(results) == n_total else f" ({n_total} executed cases, inherited methods share ids)"
    cases_note = "" if len(failed) == len(failed_cases) else f" ({len(failed_cases)} failing cases)"
    L = [MARKER, "## BlastRadius", "",
         f"PR #{pr} · `{base[:10]}` → `{head[:10]}` · {len(results)} unique test ids{ids_note} · "
         f"**{len(failed)} failing ids**{cases_note}"
         + (f" · first failure at case {first_failure} of {n_total}" if first_failure else ""), ""]
    L += [f"### 1. Tests most at risk ({ranker})", ""]
    if risk:
        L += ["| # | Test file | Score | Why |", "|--:|---|--:|---|"]
        L += [f"| {i} | `{_cell(r['test'], 80)}` | {r['score']:.2f} | {_cell(r['why'])} |"
              for i, r in enumerate(risk[:AT_RISK_ROWS], 1)]
    else:
        L += ["No ranking available for this repository."]
    L += ["", "### 2. Results, risk-first", ""]
    shown = failed + [r for r in results if r["outcome"] not in ("failed", "error")]
    if not results:
        L += ["No tests ran."]
    else:
        L += ["| Test | Outcome | Message |", "|---|---|---|"]
        L += [f"| `{_cell(r['test'], 90)}` | {r['outcome']} | {_cell(r.get('message', ''), 80)} |"
              for r in shown[:RESULT_ROWS]]
        if len(shown) > RESULT_ROWS:
            L += ["", f"_{len(shown) - RESULT_ROWS} more passing tests not shown._"]
    if triage:
        counts = {c: sum(1 for t in triage if t["class"] == c) for c in ("mine", "inherited", "flaky")}
        order = {"mine": 0, "inherited": 1, "flaky": 2}
        rows_ = sorted(triage, key=lambda t: (order.get(t["class"], 3), t["test"]))
        L += ["", "### 3. Triage of each failure", "",
              f"{counts['mine']} mine, {counts['inherited']} inherited, {counts['flaky']} flaky "
              f"(of {len(triage)} failing).", "",
              "| Failing test | Class | Confidence | Why |", "|---|---|--:|---|"]
        L += [f"| `{_cell(t['test'], 80)}` | **{t['class']}** | {t['confidence']:.2f} | {_cell(t['reason'], 120)} |"
              for t in rows_[:TRIAGE_ROWS]]
        if len(rows_) > TRIAGE_ROWS:
            L += ["", f"_{len(rows_) - TRIAGE_ROWS} more failures not shown._"]
        L += ["", "_mine = caused by this change; inherited = already failing on the base; flaky = reruns flip._"]
    if repair is not None:
        L += ["", "### 4. Proposed fix", ""]
        if repair.get("validated"):
            L += [f"Validated: the full suite passed with this patch ({repair['attempts']} attempt(s)). "
                  "Review it, then accept the suggestion on the diff.", ""]
            for s in repair["suggestions"]:
                where = f"line {s.start}" if s.start == s.end else f"lines {s.start}-{s.end}"
                L += [f"`{s.path}` {where}:", "", s.body(), ""]
        else:
            L += [f"**Not validated** ({repair.get('note', 'the full suite did not pass')}). This patch is shown for "
                  "information only and is not offered as a suggestion.", "",
                  "<details><summary>patch (not validated)</summary>", "", "```diff", repair.get("diff", ""), "```", "",
                  "</details>"]
    elif triage and not any(t["class"] == "mine" for t in triage):
        L += ["", "### 4. Proposed fix", "", "No failure was triaged **mine**, so no patch was proposed."]
    for n in notes or []:
        L += ["", f"_{n}_"]
    status = ("validated: full suite passed" if repair and repair.get("validated")
              else "validated: no patch to validate" if repair is None else "validated: no (see above)")
    L += ["", "---", f"<sub>BlastRadius (exploratory) · model `{model}` · {tokens:,} tokens · {status} · "
          "this bot only comments; it never pushes or merges.</sub>"]
    text = "\n".join(L) + "\n"
    if len(text) > MAX_COMMENT:           # shed the longest, least important parts, never the failures or the suggestion
        text = _shrink(text)
    return text


def _unique_ids(results: list[dict]) -> list[dict]:
    """First row per test id, in order; an id that failed in any case is reported as failed."""
    out: dict[str, dict] = {}
    for r in results:
        cur = out.get(r["test"])
        if cur is None or (cur["outcome"] not in ("failed", "error") and r["outcome"] in ("failed", "error")):
            out[r["test"]] = r
    return list(out.values())


def _shrink(text: str) -> str:
    """Bring an over-long comment under the cap without cutting a code fence in half."""
    text = re.sub(r"(\| `[^`]*` \| passed \|[^\n]*\n)+", "", text)
    if len(text) <= MAX_COMMENT:
        return text
    note = "\n\n_(comment truncated to fit GitHub's size limit)_\n"
    cut = text[: MAX_COMMENT - len(note) - 8]
    if cut.count("```") % 2:
        cut += "\n```"
    return cut + note


# ---- posting --------------------------------------------------------------------------------------
def upsert_comment(forge, pr: int, body: str) -> dict:
    """Edit the bot's previous comment on the PR (found by its marker) or create it. Returns the comment."""
    for c in forge.list_comments(pr):
        if MARKER in c["body"]:
            return forge.update_comment(pr, c["id"], body)
    return forge.create_comment(pr, body)


def post_suggestions(forge, pr: int, head: str, suggestions: list[Suggestion], visible: dict[str, set[int]]) -> int:
    """One review of inline `suggestion` comments for hunks inside the PR diff; skips ones already posted.

    Returns:
        The number of inline suggestions submitted.
    """
    if not hasattr(forge, "review_suggestions"):
        return 0
    seen = " ".join(c["body"] for c in forge.list_review_comments(pr)) if hasattr(forge, "list_review_comments") else ""
    comments = []
    for s in suggestions:
        if not all(n in visible.get(s.path, set()) for n in range(s.start, s.end + 1)):
            continue
        h = hashlib.sha256(f"{s.path}:{s.start}:{s.end}:{head}:{'|'.join(s.lines)}".encode()).hexdigest()[:12]
        mark = SUGGESTION_MARKER.format(h=h)
        if mark in seen:
            continue
        c = {"path": s.path, "side": "RIGHT", "line": s.end, "body": f"{s.body()}\n{mark}"}
        if s.start != s.end:
            c["start_line"], c["start_side"] = s.start, "RIGHT"
        comments.append(c)
    if comments:
        forge.review_suggestions(pr, head, "BlastRadius: a fix that made the full suite pass (validated). "
                                           "Accept it with one click, or ignore it.", comments)
    return len(comments)


# ---- the run ----------------------------------------------------------------------------------------
def build_impact(repo: Path, base: str, head: str, pr: int) -> tuple[ImpactAnalysis, list[dict], str]:
    """E1-ranked impact of the PR's changed files as an `ImpactAnalysis` the regression agent can run.

    Returns:
        `(impact, risk rows, ranker name)`.
    """
    diff = gitops.diff_text(repo, base, head, max_chars=10 ** 7)
    changed, n_lines = diff_stats(diff)
    files = sorted(f for f in gitops.tracked_files(repo) if is_conventional_test_file(f))
    ranked = rank_tests(repo, list(changed), n_lines, explain_top=3)
    if ranked:
        rows = [{"test": r.test_file, "score": r.score,
                 "why": "; ".join(r.top_features) or "no single feature dominates"} for r in ranked]
        name = "e1-lgbm-v1"
    else:
        rows = [{"test": f, "score": 0.0, "why": "E1 model unavailable: alphabetical order"} for f in files]
        name = "heuristic"
    top = rows[:AT_RISK_ROWS]
    tests = [ImpactedTest(r["test"], r["test"], 0, r["score"], [r["why"]]) for r in top]
    impact = ImpactAnalysis(
        title=f"PR #{pr}", story=f"changes in PR #{pr}", repo=repo.name, base_branch="base", base_sha=base,
        generated_at="", provider="e1", interpretation="", acceptance_criteria=[], files=[], tests=tests,
        unaffected_tests=[r["test"] for r in rows[AT_RISK_ROWS:]], risk="unknown", risk_reasons=[], gaps=[],
        cochange_hints=[], history_used=False, graph_stats={}, ranker=name)
    return impact, rows, name


def apply_blocks_tolerant(repo: Path, blocks: list[tuple[str, str, str]], allowed: set[str] | None = None) -> dict[str, str]:
    """`repair.apply_blocks`, falling back to an indentation-insensitive match when the exact one fails.

    The prompt shows code as `  141|<space><line>`; models routinely copy the gutter separator, or shift a whole
    block by a few columns, and the strict applier then finds the SEARCH text 0 times. Here, a SEARCH that does
    not match verbatim is retried as: a leading `NNN| ` gutter stripped, then compared line by line with
    surrounding whitespace ignored. It must still match exactly one place, the replacement is shifted by the same
    indentation offset, and the full-suite validation gate is unchanged. The strict `apply_blocks` (E3, R0-R3
    arms) is untouched.

    Raises:
        ValueError: As :func:`repair.apply_blocks`; the message of a miss says what to fix, because it is
            the retry feedback the model sees.
    """
    if not blocks:
        return apply_blocks(repo, blocks, allowed)
    files: dict[str, str] = {}
    for path, search, replace in blocks:
        if allowed is not None and path not in allowed:
            raise ValueError(f"{path} was not one of the files shown")
        p = repo / path
        if not p.is_file() or ".." in Path(path).parts:
            raise ValueError(f"{path} does not exist")
        text = files.get(path, p.read_text(encoding="utf-8"))
        if search and text.count(search) == 1:
            files[path] = text.replace(search, replace, 1)
        else:
            files[path] = _tolerant_replace(text, path, search, replace)
    return files


def _tolerant_replace(text: str, path: str, search: str, replace: str) -> str:
    gut = [_GUTTER.sub("", ln) for ln in search.split("\n")]
    want = [ln.strip() for ln in gut]
    while want and not want[0]:
        want.pop(0), gut.pop(0)
    while want and not want[-1]:
        want.pop(), gut.pop()
    lines = text.split("\n")
    hits = [i for i in range(len(lines) - len(want) + 1)
            if want and all(lines[i + k].strip() == w for k, w in enumerate(want))]
    if len(hits) != 1:
        first = next((w for w in want if w), "")
        raise ValueError(
            f"SEARCH text matches {len(hits)} times in {path} (must be exactly once); copy the lines verbatim, "
            f"with the file's own indentation and without the 'NNN|' line-number gutter; the first SEARCH line "
            f"was `{first[:80]}`")
    i = hits[0]
    first_real = next(k for k, w in enumerate(want) if w)
    delta = (len(lines[i + first_real]) - len(lines[i + first_real].lstrip())) - (
        len(gut[first_real]) - len(gut[first_real].lstrip()))
    out = []
    for ln in (_GUTTER.sub("", r) for r in replace.split("\n")):
        if not ln.strip():
            out.append("")
        elif delta >= 0:
            out.append(" " * delta + ln)
        else:
            drop = min(-delta, len(ln) - len(ln.lstrip()))
            out.append(ln[drop:])
    return "\n".join(lines[:i] + out + lines[i + len(want):])


EventFn = Callable[[str, str, str, dict], None]
"""`on_event(stage, type, status, data)`: called between the stages of :func:`run_bot` (Live Lab)."""


class _RepairUnavailable(RuntimeError):
    """The model could not be reached or has no quota left; carries the reason shown to the reader."""


def run_bot(repo_dir: Path | str, base_sha: str, head_sha: str, pr_number: int, *, llm=None,
            state_dir: Path | None = None, python: str | None = None, on_event: EventFn | None = None,
            timeout: float | None = None) -> BotOutcome:
    """Run impact, regression, triage and repair on one PR and render the comment.

    Args:
        repo_dir: Working copy containing both commits (full history).
        base_sha: Base commit.
        head_sha: PR head commit.
        pr_number: Pull request number.
        llm: Object with `chat(system, user, max_completion_tokens)`; None skips repair (stated in the comment).
        state_dir: Agents' state directory (default `<repo>/.blastradius`).
        python: Interpreter for the target's test suites (default: this one).
        on_event: Optional `(stage, type, status, data)` callback invoked as each stage produces something
            (impact ranking, every finished test, triage rows, repair chunks / request / reply / patch, the five
            validation checks, the comment). With it, the suite is run once, at-risk files first, and streamed;
            without it nothing changes and the comment is byte-identical to earlier runs.
        timeout: Seconds allowed for each pytest process when `on_event` is given.

    Returns:
        The rendered comment, the suggestions of a validated patch, and run statistics.
    """
    emit = on_event or (lambda *_a: None)
    repo = Path(repo_dir).resolve()
    state = Path(state_dir) if state_dir else repo / ".blastradius"
    gitops.exclude_state_dir(repo)
    base, head = gitops.head_sha(repo, base_sha), gitops.head_sha(repo, head_sha)
    impact, risk, ranker = build_impact(repo, base, head, pr_number)
    if on_event:
        diff_all = gitops.diff_text(repo, base, head, max_chars=10 ** 7)
        changed_files, n_changed_lines = diff_stats(diff_all)
        emit("impact", "impact.ranking", "ok", {
            "ranker": ranker, "changed_files": sorted(changed_files), "changed_lines": n_changed_lines,
            "n_test_files": len(risk), "at_risk_files": [t.file for t in impact.tests],
            "rows": [{"test": r["test"], "score": round(float(r["score"]), 4),
                      "reasons": [x for x in str(r["why"]).split("; ") if x][:3], "why": r["why"]} for r in risk]})
        emit("tests", "tests.start", "running", {"order_files": [t.file for t in impact.tests],
                                                 "order_enforced_by": "pytest plugin: stable sort of collected items "
                                                                      "by the position of their file in order_files"})

    report = RegressionSuiteAgent().run(
        impact, repo, state, commit=head, full=True, python=python,
        **({"on_test": lambda r: emit("tests", "test.result", "ok", r), "single_pass": True, "timeout": timeout}
           if on_event else {}))
    full = report.full or report.selected
    results = [{"test": r["test_id"], "outcome": r["outcome"], "message": r["message"]} for r in full["results"]]
    risk_files = [t.file for t in impact.tests]
    results.sort(key=lambda r: (r["outcome"] not in ("failed", "error"),
                                next((i for i, f in enumerate(risk_files) if r["test"].startswith(f)), 10 ** 6),
                                r["test"]))
    if on_event:
        emit("tests", "tests.done", "failed" if report.timed_out else "ok",
             {"verdict": report.verdict, "counts": (report.full or report.selected)["counts"],
              "wall_s": (report.full or report.selected)["wall_s"], "timed_out": report.timed_out,
              "first_failure_position": report.first_failure_position,
              "first_failure_test": report.first_failure_test})
    fails_cases = failures_of(report)
    by_first: dict[str, dict] = {}
    for f in fails_cases:
        by_first.setdefault(f["test_id"], f)          # unique ids, first case wins, order kept
    fails = list(by_first.values())
    triage_rows: list[dict] = []
    repair: dict | None = None
    notes: list[str] = []
    model, tokens = "none", 0
    base_failing: set[str] = set()
    mine: set[str] = set()
    if fails:
        ids = sorted(f["test_id"] for f in fails)
        with gitops.worktree(repo, base) as tree:      # run the failing tests on the base: inherited = fails there too
            base_run = run_pytest(tree, sorted({i.split("::")[0] for i in ids if (tree / i.split("::")[0]).is_file()}),
                                  state / "reports" / "base-failing.xml", "base", python,
                                  **({"timeout": timeout} if on_event else {}))
        base_failing = {r.test_id for r in base_run.failed}
        hist = state / "history" / "test_outcomes.jsonl"
        hist.parent.mkdir(parents=True, exist_ok=True)
        with hist.open("a", encoding="utf-8") as fh:
            for r in base_run.results:
                fh.write(json.dumps({"ts": "2000-01-01T00:00:00+00:00", "commit": base, "test_id": r.test_id,
                                     "outcome": r.outcome, "message": r.message, "branch": "base"}) + "\n")
        # The wall-clock duration of a test is measured on this machine and varies by tens of milliseconds between
        # identical runs; it is an input of the E2 model, so passing it made the rendered confidence (and a replayed
        # comment) depend on machine load. The bot triages on history and failure class only.
        tri = TriageAgent().run([{**f, "duration_s": None} for f in fails], hist, branch="base", commit=head)
        triage_rows = [{"test": f.test_id, "class": "inherited" if f.test_id in base_failing else f.klass,
                        "confidence": f.confidence, "reason": ("fails on the base commit too" if f.test_id in base_failing
                                                               else f.reason)} for f in tri.failures]
        mine = {t["test"] for t in triage_rows if t["class"] == "mine"}
        if on_event:
            base_by_id = {r.test_id: r for r in base_run.results}
            head_by_id = {f["test_id"]: f for f in fails}
            for t in triage_rows:
                b = base_by_id.get(t["test"])
                t.update({"head_outcome": head_by_id[t["test"]]["outcome"], "base_outcome": b.outcome if b else "absent",
                          "message": head_by_id[t["test"]].get("message", "")})
            emit("triage", "triage.result", "ok", {
                "model": tri.model, "rows": triage_rows, "counts": {c: sum(1 for t in triage_rows if t["class"] == c)
                                                                      for c in ("mine", "inherited", "flaky")},
                "unit": "unique canonical test ids", "failing_cases": len(fails_cases),
                "base_command": base_run.command[1:], "base_timed_out": base_run.timed_out})
        if mine and llm is None:
            notes.append("No model is configured (GROQ_API_KEY missing or offline mode), so no patch was attempted.")
            emit("repair", "repair.skipped", "skipped", {"reason": "no model is configured (offline mode or no key)",
                                                          "mine": len(mine)})
        elif mine:
            try:
                repair, model, tokens = _repair(repo, state, impact, report, sorted(mine), fails, base, head, llm,
                                                python, emit if on_event else None, timeout if on_event else None)
            except _RepairUnavailable as exc:
                notes.append(f"No patch was attempted: {exc}")
    if on_event and not fails:
        emit("triage", "triage.result", "skipped", {"rows": [], "counts": {"mine": 0, "inherited": 0, "flaky": 0},
                                                    "reason": "no test failed"})
        emit("repair", "repair.skipped", "skipped", {"reason": "no test failed; the model was not called", "mine": 0})
    elif on_event and fails and not mine:
        emit("repair", "repair.skipped", "skipped", {"reason": "no failure was triaged mine; the model was not called",
                                                      "mine": 0})
    order = [r["test"] for r in results]
    ff = next((i for i, r in enumerate(results, 1) if r["outcome"] in ("failed", "error")), None)
    comment = render_comment(pr=pr_number, base=base, head=head, risk=risk, ranker=ranker, results=results,
                             n_total=len(order), first_failure=report.first_failure_position or ff, triage=triage_rows,
                             repair=repair, model=model, tokens=tokens, notes=notes)
    sugg = repair["suggestions"] if repair and repair.get("validated") else []
    if on_event:
        emit("report", "report.comment", "ok", {"comment": comment, "validated": bool(repair and repair.get("validated"))})
    return BotOutcome(comment, sugg, bool(repair and repair.get("validated")),
                      {"failing": len(fails), "failing_cases": len(fails_cases), "tests": len({r["test"] for r in results}),
                       "cases": len(results), "unit": "unique canonical test ids", "mine": len(mine), "tokens": tokens, "model": model,
                       "diff": gitops.diff_text(repo, base, head, max_chars=10 ** 7)})


class _EventLLM:
    """Wraps an LLM so each call is announced (request, reply) and a quota / network failure becomes an event."""

    def __init__(self, inner, emit: EventFn) -> None:
        self.inner, self.emit, self.n = inner, emit, 0

    @property
    def model(self) -> str:
        return getattr(self.inner, "model", "model")

    def _cached(self, system: str, user: str, n: int) -> tuple[bool, str | None]:
        c = getattr(self.inner, "cache", None)
        if c is None or not hasattr(self.inner, "request_key"):
            return False, None
        key = self.inner.request_key(system, user, n)
        hit = key in c
        return hit, (c.origin(key) if hit and hasattr(c, "origin") else None)

    def chat(self, system: str, user: str, max_completion_tokens: int = 1500):
        from src.agents.llm import DailyQuotaReached, LLMError, NetworkUnavailable
        from src.agents.llm_cache import CacheMiss

        self.n += 1
        est = int((len(system) + len(user)) / 3.5)
        self.emit("repair", "repair.request", "running", {
            "attempt": self.n, "model": self.model, "prompt_tokens_estimate": est, "prompt_chars": len(system) + len(user),
            "max_completion_tokens": max_completion_tokens, "system": system[:2000], "prompt": user[:8000],
            "params": getattr(self.inner, "request_params", lambda *_: {})(max_completion_tokens),
            "cached": self._cached(system, user, max_completion_tokens)[0],
            "cache_file": self._cached(system, user, max_completion_tokens)[1]})
        t0 = time.perf_counter()
        try:
            res = self.inner.chat(system, user, max_completion_tokens)
        except DailyQuotaReached as exc:
            reason = f"the model's daily token quota is used up (next call possible after {exc.resume_after} UTC)"
            self.emit("repair", "repair.unavailable", "failed", {"kind": "quota", "reason": reason})
            raise _RepairUnavailable(reason) from exc
        except NetworkUnavailable as exc:
            self.emit("repair", "repair.unavailable", "failed", {"kind": "network", "reason": str(exc)})
            raise _RepairUnavailable(str(exc)) from exc
        except CacheMiss as exc:
            self.emit("repair", "repair.unavailable", "failed", {"kind": "cache-miss", "reason": str(exc)[:300]})
            raise _RepairUnavailable("replay forbids a network call and this request was not recorded") from exc
        except LLMError as exc:
            self.emit("repair", "repair.unavailable", "failed", {"kind": "provider", "reason": str(exc)[:300]})
            raise _RepairUnavailable(str(exc)[:200]) from exc
        self.emit("repair", "repair.reply", "ok", {
            "attempt": self.n, "model": res.model, "text": res.text, "usage": res.usage, "from_cache": res.from_cache,
            "latency_s": res.latency_s if res.latency_s is not None else round(time.perf_counter() - t0, 3)})
        return res


def _repair(repo: Path, state: Path, impact: ImpactAnalysis, report, mine: list[str], fails: list[dict], base: str,
            head: str, llm, python: str | None, emit: EventFn | None = None,
            timeout: float | None = None) -> tuple[dict, str, int]:
    by_id = {f["test_id"]: f for f in fails}
    others = {t for t in by_id if t not in mine}
    fr = FailureReport(failing=[{"test_id": t, "output": by_id[t].get("message", "")} for t in mine],
                       pr_diff=gitops.diff_text(repo, base, head, max_chars=10 ** 7), triage="mine",
                       changed_files=gitops.changed_files(repo, base, head))
    def note(kind: str, status: str, data: dict) -> None:
        if emit:
            emit("validate" if kind.startswith("validate") else "repair", kind, status, data)

    with gitops.worktree(repo, head) as tree:
        dirs = sorted({p.split("/")[0] for p in gitops.tracked_files(tree)
                       if p.endswith(".py") and not is_conventional_test_file(p)})
        srcs = source_files(tree, {"src_dirs": dirs})
        if emit:                                   # the chunks the agent will show, chosen by the same call it makes
            from src.agents.repair import changed_line_ranges, select_chunks

            ranges = changed_line_ranges(fr.pr_diff)
            chosen = select_chunks("R2", tree, srcs, fr)
            note("repair.chunks", "ok", {"chunks": [
                {"file": c.file, "qualname": c.qualname, "start": c.start, "end": c.end, "focus": c.focus,
                 "bm25": round(c.score, 4), "rank": i + 1,
                 "why": ("changed function (the diff touches line " + str(c.focus) + ")"
                         if any(c.start <= ln <= c.end for ln in ranges.get(c.file, [])) else "BM25 rank")
                        + f"; BM25 rank {i + 1}, score {c.score:.3f}"} for i, c in enumerate(chosen)],
                "failing": [t["test_id"] for t in fr.failing[:8]]})
            allowed_edit = {c.file for c in chosen} | set(fr.changed_files)
        counters = {"attempt": 0, "validate": 0}

        def applier(repo_: Path, blocks: list[tuple[str, str, str]], allowed: set[str] | None = None) -> dict[str, str]:
            counters["attempt"] += 1
            try:
                out = apply_blocks_tolerant(repo_, blocks, allowed)
            except ValueError as exc:
                note("repair.blocks", "failed", {"attempt": counters["attempt"], "error": str(exc), "blocks": [
                    {"path": p_, "search": s_, "replace": r_} for p_, s_, r_ in blocks]})
                note("validate.check", "failed", {"attempt": counters["attempt"], "name": "applies",
                                                  "ok": False, "evidence": str(exc)[:400]})
                raise
            note("repair.blocks", "ok", {"attempt": counters["attempt"], "blocks": [
                {"path": p_, "search": s_, "replace": r_} for p_, s_, r_ in blocks], "files": sorted(out)})
            return out

        def check(name: str, ok: bool | None, evidence: str) -> None:
            note("validate.check", "running" if ok is None else ("ok" if ok else "failed"),
                 {"attempt": counters["attempt"], "name": name, "ok": ok, "evidence": evidence})

        def validate(files: dict[str, str]) -> tuple[bool, str]:
            before = {p: (tree / p).read_text(encoding="utf-8") for p in files}
            if emit is None:
                try:
                    for p, text in files.items():
                        (tree / p).write_text(text, encoding="utf-8")
                    run = run_pytest(tree, None, state / "reports" / "bot-validate.xml", "validate", python)
                finally:
                    for p, text in before.items():
                        (tree / p).write_text(text, encoding="utf-8")
                bad = {r.test_id for r in run.failed} - others
                return (not bad and run.exit_code in (0, 1)), "\n".join(
                    f"{r.test_id}: {r.message}" for r in run.failed if r.test_id not in others)[:1000]
            tmo = {"timeout": timeout} if timeout else {}
            check("applies", True, f"{len(files)} file(s) patched; every SEARCH text matched exactly once")
            errors = []
            for p, text in files.items():
                if p.endswith(".py"):
                    try:
                        compile(text, p, "exec")
                    except SyntaxError as exc:
                        errors.append(f"{p}:{exc.lineno}: {exc.msg}")
            check("syntax", not errors, "; ".join(errors) or f"{sum(p.endswith('.py') for p in files)} Python file(s) compile")
            if errors:
                for n in ("targeted", "full", "scope"):
                    note("validate.check", "skipped", {"attempt": counters["attempt"], "name": n, "ok": None,
                                                       "evidence": "skipped: the patch does not compile"})
                return False, "SyntaxError: " + "; ".join(errors)
            try:
                for p, text in files.items():
                    (tree / p).write_text(text, encoding="utf-8")
                tfiles = sorted({t.split("::")[0] for t in mine if (tree / t.split("::")[0]).is_file()})
                check("targeted", None, f"running {len(tfiles)} test file(s) holding the {len(mine)} failing id(s)")
                trun = run_pytest(tree, tfiles, state / "reports" / "lab-targeted.xml", "targeted", python, **tmo)
                still = sorted({r.test_id for r in trun.failed} & set(mine))
                check("targeted", not still and not trun.timed_out,
                      "timed out" if trun.timed_out else (f"{len(mine) - len(still)}/{len(mine)} previously failing ids "
                                                           f"pass ({len(trun.results)} cases run)" if not still else
                                                           f"{len(still)} still fail, e.g. {still[0]}"))
                check("full", None, "running the full suite with the patch applied")
                run = run_pytest(tree, None, state / "reports" / "bot-validate.xml", "validate", python, **tmo)
            finally:
                for p, text in before.items():
                    (tree / p).write_text(text, encoding="utf-8")
            bad = {r.test_id for r in run.failed} - others
            full_ok = not bad and run.exit_code in (0, 1) and not run.timed_out
            c = run.counts()
            check("full", full_ok, ("timed out" if run.timed_out else
                                    f"{c['passed']} passed, {c['failed']} failed, {c['error']} errors, {c['skipped']} "
                                    f"skipped of {c['total']} cases" + (f"; {len(others)} id(s) were already failing "
                                                                          "and are excluded" if others else "")))
            outside = sorted(set(files) - allowed_edit)
            check("scope", not outside, ("edits outside the changed or shown files: " + ", ".join(outside)) if outside
                  else "edited: " + ", ".join(sorted(files)) + " (all in the changed or shown files)")
            ok = full_ok and not still and not outside
            return ok, "\n".join(f"{r.test_id}: {r.message}" for r in run.failed if r.test_id not in others)[:1000]

        agent_llm = _EventLLM(llm, emit) if emit else llm
        res = RepairAgent(agent_llm, "R3", max_retries=MAX_REPAIR_RETRIES,
                          applier=applier if emit else apply_blocks_tolerant).run(tree, srcs, fr, validate)
        head_files = {}
        for a in res.attempts:
            for p in a.files:
                head_files.setdefault(p, (tree / p).read_text(encoding="utf-8"))
        if emit:
            last_ = next((a for a in reversed(res.attempts) if a.applied), None)
            patched = last_.files if last_ else {}
            note("repair.patch", "ok" if last_ else "failed", {
                "files": [{"path": p, "before": head_files.get(p, "")[:80000], "after": patched[p][:80000]}
                          for p in sorted(patched)],
                "diff": unified(head_files, patched) if patched else "", "attempts": len(res.attempts)})
            note("validate.verdict", "ok" if res.accepted else "failed", {
                "accepted": res.accepted, "attempts": len(res.attempts),
                "note": "the full suite passed with the patch" if res.accepted else
                        ("the model's reply could not be applied" if not last_ else "the full suite still failed with it")})
    tokens = sum(int((a.usage or {}).get("total_tokens", 0)) for a in res.attempts)
    model = getattr(llm, "model", "model")
    last = next((a for a in reversed(res.attempts) if a.applied), None)
    if res.accepted and last is not None:
        return ({"validated": True, "attempts": len(res.attempts), "files": last.files,
                 "suggestions": patch_hunks(head_files, last.files)}, model, tokens)
    if last is not None:
        return ({"validated": False, "attempts": len(res.attempts), "files": last.files,
                 "diff": unified(head_files, last.files), "note": "the full suite still failed with it",
                 "suggestions": []}, model, tokens)
    return ({"validated": False, "attempts": len(res.attempts), "files": {}, "diff": "(no applicable patch)",
             "note": "the model's reply could not be applied", "suggestions": []}, model, tokens)


def post(outcome: BotOutcome, forge, pr: int, head: str) -> dict:
    """Edit-or-create the comment and submit inline suggestions for a validated patch."""
    c = upsert_comment(forge, pr, outcome.comment)
    n = 0
    if outcome.validated:
        visible = diff_visible_lines(outcome.stats.get("diff", ""))
        n = post_suggestions(forge, pr, head, outcome.suggestions, visible)
    return {"comment_id": c["id"], "inline_suggestions": n}
