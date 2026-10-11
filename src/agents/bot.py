"""PR bot (D-63, exploratory): one Markdown comment on a pull request, composed from the existing stages.

    python -m src.agents bot --repo R --base BASE_SHA --head HEAD_SHA --pr N [--no-post]

Stages, in order:

1. **impact**   E1 ranker (`src.features.online.rank_tests`, SHAP reasons) over the files the PR changes. A pull
                request has changed files, not a user story, so the story-keyed Impact agent is not used; its
                ranker is.
2. **regression** `RegressionSuiteAgent`: the at-risk test files first, then the full suite, at the PR head.
3. **triage**   `TriageAgent` per failing test. Each failing test is also run at the base commit and recorded in
                the history first, so "inherited" rests on a run, not only on past history.
4. **repair**   `RepairAgent` arm R3 with one retry (<= 2 attempts) for failures triaged `mine`; a patch is
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
from dataclasses import dataclass, field
from pathlib import Path

from src.agents import gitops
from src.agents.impact import ImpactAnalysis, ImpactedTest
from src.agents.regression import RegressionSuiteAgent, run_pytest
from src.agents.repair import FailureReport, RepairAgent
from src.agents.triage import TriageAgent, failures_of
from src.eval.seeded.build import source_files
from src.features.online import diff_stats, rank_tests
from src.parse.changeset import is_conventional_test_file

MARKER = "<!-- blastradius-bot -->"
SUGGESTION_MARKER = "<!-- blastradius-suggestion:{h} -->"
MAX_COMMENT = 65_000
AT_RISK_ROWS = 10
RESULT_ROWS = 40
MAX_REPAIR_ATTEMPTS = 2


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
    failed = [r for r in results if r["outcome"] in ("failed", "error")]
    L = [MARKER, "## BlastRadius", "",
         f"PR #{pr} · `{base[:10]}` → `{head[:10]}` · {n_total} tests · **{len(failed)} failing**"
         + (f" · first failure at position {first_failure} of {n_total}" if first_failure else ""), ""]
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
        L += ["", "### 3. Triage of each failure", "",
              "| Failing test | Class | Confidence | Why |", "|---|---|--:|---|"]
        L += [f"| `{_cell(t['test'], 80)}` | **{t['class']}** | {t['confidence']:.2f} | {_cell(t['reason'], 120)} |"
              for t in triage]
        L += ["", "_mine = caused by this change; inherited = already failing on the base; flaky = reruns flip._"]
    if repair is not None:
        L += ["", "### 4. Proposed fix", ""]
        if repair.get("validated"):
            L += [f"Validated: the full suite passed with this patch ({repair['attempts']} attempt(s)). "
                  "Review it, then accept the suggestion on the diff.", ""]
            for s in repair["suggestions"]:
                span = f"{s.start}" if s.start == s.end else f"{s.start}-{s.end}"
                L += [f"`{s.path}` lines {span}:", "", s.body(), ""]
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


def run_bot(repo_dir: Path | str, base_sha: str, head_sha: str, pr_number: int, *, llm=None,
            state_dir: Path | None = None, python: str | None = None) -> BotOutcome:
    """Run impact, regression, triage and repair on one PR and render the comment.

    Args:
        repo_dir: Working copy containing both commits (full history).
        base_sha: Base commit.
        head_sha: PR head commit.
        pr_number: Pull request number.
        llm: Object with `chat(system, user, max_completion_tokens)`; None skips repair (stated in the comment).
        state_dir: Agents' state directory (default `<repo>/.blastradius`).
        python: Interpreter for the target's test suites (default: this one).

    Returns:
        The rendered comment, the suggestions of a validated patch, and run statistics.
    """
    repo = Path(repo_dir).resolve()
    state = Path(state_dir) if state_dir else repo / ".blastradius"
    gitops.exclude_state_dir(repo)
    base, head = gitops.head_sha(repo, base_sha), gitops.head_sha(repo, head_sha)
    impact, risk, ranker = build_impact(repo, base, head, pr_number)

    report = RegressionSuiteAgent().run(impact, repo, state, commit=head, full=True, python=python)
    full = report.full or report.selected
    results = [{"test": r["test_id"], "outcome": r["outcome"], "message": r["message"]} for r in full["results"]]
    risk_files = [t.file for t in impact.tests]
    results.sort(key=lambda r: (r["outcome"] not in ("failed", "error"),
                                next((i for i, f in enumerate(risk_files) if r["test"].startswith(f)), 10 ** 6),
                                r["test"]))
    fails = failures_of(report)
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
                                  state / "reports" / "base-failing.xml", "base", python)
        base_failing = {r.test_id for r in base_run.failed}
        hist = state / "history" / "test_outcomes.jsonl"
        hist.parent.mkdir(parents=True, exist_ok=True)
        with hist.open("a", encoding="utf-8") as fh:
            for r in base_run.results:
                fh.write(json.dumps({"ts": "2000-01-01T00:00:00+00:00", "commit": base, "test_id": r.test_id,
                                     "outcome": r.outcome, "message": r.message, "branch": "base"}) + "\n")
        tri = TriageAgent().run(fails, hist, branch="base", commit=head)
        triage_rows = [{"test": f.test_id, "class": "inherited" if f.test_id in base_failing else f.klass,
                        "confidence": f.confidence, "reason": ("fails on the base commit too" if f.test_id in base_failing
                                                               else f.reason)} for f in tri.failures]
        mine = {t["test"] for t in triage_rows if t["class"] == "mine"}
        if mine and llm is None:
            notes.append("No model is configured (GROQ_API_KEY missing or offline mode), so no patch was attempted.")
        elif mine:
            repair, model, tokens = _repair(repo, state, impact, report, sorted(mine), fails, base, head, llm, python)
    order = [r["test"] for r in results]
    ff = next((i for i, r in enumerate(results, 1) if r["outcome"] in ("failed", "error")), None)
    comment = render_comment(pr=pr_number, base=base, head=head, risk=risk, ranker=ranker, results=results,
                             n_total=len(order), first_failure=report.first_failure_position or ff, triage=triage_rows,
                             repair=repair, model=model, tokens=tokens, notes=notes)
    sugg = repair["suggestions"] if repair and repair.get("validated") else []
    return BotOutcome(comment, sugg, bool(repair and repair.get("validated")),
                      {"failing": len(fails), "mine": len(mine), "tokens": tokens, "model": model,
                       "diff": gitops.diff_text(repo, base, head, max_chars=10 ** 7)})


def _repair(repo: Path, state: Path, impact: ImpactAnalysis, report, mine: list[str], fails: list[dict], base: str,
            head: str, llm, python: str | None) -> tuple[dict, str, int]:
    by_id = {f["test_id"]: f for f in fails}
    others = {t for t in by_id if t not in mine}
    fr = FailureReport(failing=[{"test_id": t, "output": by_id[t].get("message", "")} for t in mine],
                       pr_diff=gitops.diff_text(repo, base, head, max_chars=10 ** 7), triage="mine",
                       changed_files=gitops.changed_files(repo, base, head))
    with gitops.worktree(repo, head) as tree:
        dirs = sorted({p.split("/")[0] for p in gitops.tracked_files(tree)
                       if p.endswith(".py") and not is_conventional_test_file(p)})
        srcs = source_files(tree, {"src_dirs": dirs})

        def validate(files: dict[str, str]) -> tuple[bool, str]:
            before = {p: (tree / p).read_text(encoding="utf-8") for p in files}
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

        res = RepairAgent(llm, "R3", max_retries=MAX_REPAIR_ATTEMPTS - 1).run(tree, srcs, fr, validate)
        head_files = {}
        for a in res.attempts:
            for p in a.files:
                head_files.setdefault(p, (tree / p).read_text(encoding="utf-8"))
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
