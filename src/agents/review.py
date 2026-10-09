"""PR Reviewer Agent: pull request + impact analysis -> review, merge, merge commit id.

Checks, in order:

1. **Scope.** Every changed file should be inside the impact scope (files to
   change, their dependents, and the tests at risk). A source file outside it is
   flagged; under ``scope_policy="strict"`` (the default) that blocks the merge.
2. **Static.** Every changed ``.py`` file compiles at the PR head.
3. **Tests.** The impact analysis's tests at risk run at the PR head (Regression
   Suite Agent, selected scope) and must pass. On GitHub the PR's check runs must
   also be green.
4. **Test change.** If the story needed new behaviour but no test file changed, that is noted.
5. **Model review** (only with an LLM): comments on the diff against the story.

The verdict is APPROVE or REQUEST_CHANGES; on APPROVE with ``merge=True`` the PR
is merged and the merge commit id is returned.
"""

from __future__ import annotations

import json
import py_compile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from src.agents import gitops
from src.agents.codebase import is_test_path
from src.agents.forge import GitHubForge, LocalForge
from src.agents.impact import ImpactAnalysis
from src.agents.llm import LLMError, OfflineLLM, get_llm
from src.agents.regression import run_pytest


@dataclass
class ReviewResult:
    """The reviewer's output."""

    pr_number: int
    verdict: str  # APPROVE | REQUEST_CHANGES
    merged: bool
    commit_id: str | None
    checks: list[dict] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)
    markdown_path: str = ""


class PRReviewerAgent:
    """Pull request + impact analysis -> review decision, merge, commit id."""

    def __init__(self, provider: str | None = None) -> None:
        self.llm = get_llm(provider)

    def run(self, pr_number: int, impact: ImpactAnalysis, repo: Path | str, forge: LocalForge | GitHubForge,
            state_dir: Path | str | None = None, *, merge: bool = True, scope_policy: str = "strict",
            python: str | None = None) -> ReviewResult:
        """Review PR ``pr_number`` against ``impact`` and merge it if it passes."""
        repo = Path(repo).resolve()
        state = Path(state_dir) if state_dir else repo / ".blastradius"
        pr = forge.get_pr(pr_number)
        changed = forge.changed_files(pr)
        checks: list[dict] = []
        comments: list[str] = []

        out_of_scope = [f for f in changed if f not in impact.scope_files and not is_test_path(f)]
        scope_ok = not out_of_scope or scope_policy == "warn"
        checks.append({"check": "scope", "ok": not out_of_scope,
                       "detail": "all changed files are inside the impact scope" if not out_of_scope
                       else f"outside the impact scope: {', '.join(out_of_scope)}"
                            + (" (warn mode: not blocking)" if scope_policy == "warn" else "")})

        compile_errors = []
        test_run = None
        with gitops.worktree(repo, pr.head_sha) as tree:
            for f in changed:
                if f.endswith(".py") and (tree / f).exists():
                    try:
                        py_compile.compile(str(tree / f), doraise=True)
                    except py_compile.PyCompileError as exc:
                        compile_errors.append(f"{f}: {exc.msg}")
            out = state / "reviews" / f"pr-{pr.number}"
            out.mkdir(parents=True, exist_ok=True)
            # Tests at risk, plus any test file the PR itself added or changed.
            ids = [t.test_id for t in impact.tests]
            new_test_files = [f for f in changed if is_test_path(f) and f.endswith(".py") and (tree / f).exists()]
            test_run = run_pytest(tree, ids + [f for f in new_test_files if not any(i.startswith(f + "::") for i in ids)],
                                  out / "tests.xml", "review", python)
        checks.append({"check": "compile", "ok": not compile_errors,
                       "detail": "all changed Python files compile" if not compile_errors else "; ".join(compile_errors)})
        c = test_run.counts()
        tests_ok = not test_run.failed and test_run.exit_code in (0, 5)
        checks.append({"check": "tests at risk", "ok": tests_ok,
                       "detail": f"{c['passed']} passed, {c['failed']} failed, {c['error']} errors "
                                 f"({len(impact.tests)} from the impact analysis, {len(new_test_files)} changed test file(s))"
                                 + ("" if tests_ok else ": " + ", ".join(r.test_id for r in test_run.failed))})
        ci = forge.ci_status(pr)
        if ci != "none":
            checks.append({"check": "CI", "ok": ci == "success", "detail": f"check runs: {ci}"})
        if impact.change_files and not any(is_test_path(f) for f in changed):
            comments.append("No test file changed; the story adds behaviour, so a test for it is expected.")
        for g in impact.gaps:
            comments.append(f"Impact analysis gap: {g}")

        if not isinstance(self.llm, OfflineLLM):
            try:
                reply = self.llm.complete_json(
                    "You are a strict code reviewer.",
                    f"Story:\n{impact.story}\n\nDiff:\n{forge.diff(pr)}\n\nReturn JSON: "
                    '{"comments": [specific review comments], "blocking": true if the diff is wrong or unsafe}.')
                comments += [f"Model review: {x}" for x in reply.get("comments", [])]
                if reply.get("blocking"):
                    checks.append({"check": "model review", "ok": False, "detail": "the model flagged a blocking issue"})
            except LLMError as exc:
                comments.append(f"Model review unavailable: {exc}")

        blocking = [ch for ch in checks if not ch["ok"] and not (ch["check"] == "scope" and scope_ok)]
        verdict = "REQUEST_CHANGES" if blocking else "APPROVE"
        merged, commit_id = False, None
        if verdict == "APPROVE" and merge:
            commit_id = forge.merge(pr)
            merged = True

        md = self._markdown(pr, verdict, checks, comments, merged, commit_id)
        path = state / "reviews" / f"pr-{pr.number}" / "review.md"
        path.write_text(md, encoding="utf-8")
        record = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "verdict": verdict,
                  "checks": checks, "comments": comments, "markdown": md}
        forge.add_review(forge.get_pr(pr.number) if merged else pr, record)
        result = ReviewResult(pr.number, verdict, merged, commit_id, checks, comments, str(path))
        (path.parent / "review.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
        return result

    @staticmethod
    def _markdown(pr, verdict: str, checks: list[dict], comments: list[str], merged: bool, commit_id: str | None) -> str:
        L = [f"# Review of PR #{pr.number}: {pr.title}", "",
             f"**Verdict: {verdict}**" + (f" — merged as `{commit_id[:12]}`" if merged and commit_id else ""), "",
             "| Check | Result | Detail |", "|---|---|---|"]
        L += [f"| {c['check']} | {'pass' if c['ok'] else 'FAIL'} | {c['detail']} |" for c in checks]
        if comments:
            L += ["", "## Comments", ""] + [f"- {x}" for x in comments]
        L += ["", "_Reviewed by the BlastRadius PR Reviewer Agent._", ""]
        return "\n".join(L)
