"""The 2.0 delivery path: impact -> code -> regress -> triage -> repair -> review -> deploy.

Differs from the classic order (`cli.pipeline(stages="classic")`) in that the change is tested
BEFORE it is reviewed and merged. A failing test is triaged; only failures triaged `mine` are
sent to the Repair agent (at most two attempts), whose patch is accepted only if the FULL suite
passes. Whatever cannot be repaired is notified and nothing is merged.

Only the Repair agent calls an LLM (D-58); every other step is deterministic.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.agents import gitops
from src.agents.coding import CodingAgent, save_result
from src.agents.deploy import BuildDeployAgent
from src.agents.forge import get_forge
from src.agents.impact import ImpactAnalysisAgent
from src.agents.notify import notify
from src.agents.regression import RegressionSuiteAgent, run_pytest
from src.agents.repair import FailureReport, RepairAgent
from src.agents.review import PRReviewerAgent
from src.agents.triage import TriageAgent, failures_of
from src.eval.seeded.build import source_files

MAX_REPAIR_ATTEMPTS = 2


def _failing_ids(run) -> set[str]:
    return {r.test_id for r in run.failed}


def pipeline_v2(repo: Path, story: str, *, title: str | None = None, provider: str | None = None,
                forge_kind: str = "local", patch: str | None = None, scope_policy: str = "strict",
                build_cmd: str | None = None, state_dir: Path | None = None, repair_llm=None,
                python: str | None = None) -> dict:
    """Run the 2.0 workflow and return every step's output.

    Args:
        repo: Target working copy.
        story: The user story.
        title: PR title override.
        provider: Provider for the Impact / Coding / Review agents.
        forge_kind: `local` or `github`.
        patch: Recorded change set instead of an LLM change.
        scope_policy: Reviewer scope policy.
        build_cmd: Build command override.
        state_dir: Agents' state directory.
        repair_llm: An object with `chat(system, user, max_completion_tokens)` for the Repair agent
            (a `GroqLLM`, possibly replaying a cache); None means notify-only.
        python: Interpreter for the suite runs.

    Returns:
        A dict with `steps` plus the typed results (`impact`, `coding`, `regression`, `triage`,
        `repair`, `review`, `deploy`) of the stages that ran.
    """
    repo = Path(repo).resolve()
    state = state_dir or repo / ".blastradius"
    steps: list[dict] = []
    result: dict = {"repo": str(repo), "steps": steps, "stages": "2.0"}

    impact, out = ImpactAnalysisAgent(provider).run(story, repo, state, title=title)
    steps.append({"agent": "Impact Analysis Agent", "input": {"story": story, "codebase": repo.name},
                  "output": {"document": str(out / "impact.md"), "risk": impact.risk, "ranker": impact.ranker,
                             "change_files": impact.change_files, "tests_at_risk": len(impact.tests)}})
    forge = get_forge(forge_kind, repo, state)
    coded = CodingAgent(provider).run(impact, repo, forge, patch=patch)
    save_result(coded, state)
    steps.append({"agent": "Coding Agent", "input": {"impact": str(out / "impact.json")},
                  "output": {"branch": coded.branch, "commit": coded.commit, "changed_files": coded.changed_files,
                             "pr": coded.pr_number, "mode": coded.mode}})
    result.update(impact=impact, coding=coded)

    head = coded.commit
    report = RegressionSuiteAgent().run(impact, repo, state, commit=head, full=True, python=python)
    steps.append({"agent": "Regression Suite Agent", "input": {"commit": head, "order": impact.ranker},
                  "output": {"verdict": report.verdict, "selected": report.selected["counts"],
                             "full": report.full["counts"] if report.full else None,
                             "first_failure_position": report.first_failure_position,
                             "first_failure_test": report.first_failure_test, "report": report.markdown_path}})
    result["regression"] = report

    if report.verdict == "FAIL":
        fails = failures_of(report)
        tri = TriageAgent().run(fails, state / "history" / "test_outcomes.jsonl", branch=impact.base_branch,
                                commit=head)
        result["triage"] = tri
        steps.append({"agent": "Triage Agent", "input": {"failures": len(fails)},
                      "output": {"model": tri.model, "counts": tri.counts(),
                                 "failures": [{"test_id": f.test_id, "class": f.klass, "confidence": f.confidence,
                                               "reason": f.reason, "route": f.route} for f in tri.failures]}})
        mine = {f.test_id for f in tri.mine}
        if not mine:
            msg = ("every failing test was triaged inherited or flaky: no patch proposed, the change was not merged "
                   "(rerun the flaky ones, investigate the inherited ones on the base)")
            notify(state, "regression_failed", msg, {"commit": head, "triage": tri.counts()})
            steps.append({"agent": "Repair Agent", "skipped": "no failure was triaged mine"})
            result["outcome"] = "Regression failed, nothing mine to repair"
            return result

        by_id = {f["test_id"]: f for f in fails}
        base_failing = {t for t in by_id if t not in mine}
        fr = FailureReport(
            failing=[{"test_id": t, "output": by_id[t].get("message", "")} for t in sorted(mine)],
            pr_diff=gitops.diff_text(repo, impact.base_branch, coded.branch),
            triage="mine", changed_files=list(coded.changed_files))
        with gitops.worktree(repo, head) as tree:
            srcs = source_files(tree, {"src_dirs": sorted({p.split("/")[0] for p in gitops.tracked_files(tree)
                                                           if p.endswith(".py") and not p.startswith(("tests/", "test"))})})

            def validate(files: dict[str, str]) -> tuple[bool, str]:
                before = {p: (tree / p).read_text(encoding="utf-8") for p in files}
                try:
                    for p, text in files.items():
                        (tree / p).write_text(text, encoding="utf-8")
                    run = run_pytest(tree, None, state / "reports" / "repair-validate.xml", "repair", python)
                finally:
                    for p, text in before.items():
                        (tree / p).write_text(text, encoding="utf-8")
                bad = _failing_ids(run) - base_failing
                return (not bad and run.exit_code in (0, 1)), "\n".join(
                    f"{r.test_id}: {r.message}" for r in run.failed if r.test_id not in base_failing)[:1000]

            attempts = max(1, MAX_REPAIR_ATTEMPTS - 1)
            res = RepairAgent(repair_llm, "R3", max_retries=attempts).run(tree, srcs, fr, validate)
        result["repair"] = res
        accepted_files = next((a.files for a in res.attempts if a.applied and res.accepted), None)
        steps.append({"agent": "Repair Agent", "input": {"mine": sorted(mine), "arm": "R3 (change-aware, <= 2 attempts)"},
                      "output": {"action": res.action, "accepted": res.accepted, "attempts": len(res.attempts),
                                 "chunks": [f"{c.file}::{c.qualname}" for c in res.chunks],
                                 "tokens": sum(int((a.usage or {}).get("total_tokens", 0)) for a in res.attempts),
                                 "files": sorted(accepted_files or {}), "note": res.note}})
        if not res.accepted or not accepted_files:
            notify(state, "repair_failed", "the Repair agent could not produce a patch that makes the full suite "
                   "pass; the change was not merged", {"commit": head, "mine": sorted(mine)})
            result["outcome"] = "Repair failed, team notified"
            return result
        # commit the accepted patch onto the PR branch, then verify the whole suite at the new head
        gitops.git(repo, "checkout", "-q", coded.branch)
        try:
            for p, text in accepted_files.items():
                (repo / p).write_text(text, encoding="utf-8")
            gitops.git(repo, "add", "--", *sorted(accepted_files))
            gitops.git(repo, "commit", "-q", "-m", "fix: repair failing tests (BlastRadius Repair Agent)")
        finally:
            gitops.git(repo, "checkout", "-q", impact.base_branch)
        head = gitops.head_sha(repo, coded.branch)
        after = RegressionSuiteAgent().run(impact, repo, state, commit=head, full=True, python=python)
        steps.append({"agent": "Regression Suite Agent (after repair)", "input": {"commit": head},
                      "output": {"verdict": after.verdict, "full": after.full["counts"] if after.full else None,
                                 "report": after.markdown_path}})
        result["regression_after"] = after
        if after.verdict != "PASS":
            notify(state, "repair_failed", "the repaired change still fails the suite; not merged", {"commit": head})
            result["outcome"] = "Repair did not hold, team notified"
            return result

    review = PRReviewerAgent(provider).run(coded.pr_number, impact, repo, forge, state, scope_policy=scope_policy)
    steps.append({"agent": "PR Reviewer Agent", "input": {"pr": coded.pr_number},
                  "output": {"verdict": review.verdict, "merged": review.merged, "commit_id": review.commit_id,
                             "checks": review.checks, "review": review.markdown_path}})
    result["review"] = review
    if not review.merged:
        steps.append({"agent": "Build & Deploy Agent", "skipped": "the PR was not merged"})
        result["outcome"] = "Blocked at review"
        return result
    deploy = BuildDeployAgent().run(review.commit_id, impact.base_branch, repo, state, build_cmd=build_cmd)
    steps.append({"agent": "Build & Deploy Agent", "input": {"commit": review.commit_id, "branch": impact.base_branch},
                  "output": {"status": deploy.status, "build": deploy.build_command, "exit_code": deploy.build_exit_code,
                             "package": deploy.package, "deployed_to": deploy.deployed_to,
                             "notification": deploy.notification}})
    result["deploy"] = deploy
    result["outcome"] = "Deployed" if deploy.status == "deployed" else "Build failed, team notified"
    return result


def dump(result: dict, path: Path) -> None:
    """Write the step list as JSON."""
    path.write_text(json.dumps({"steps": result["steps"], "outcome": result.get("outcome")}, indent=2, default=str),
                    encoding="utf-8")
