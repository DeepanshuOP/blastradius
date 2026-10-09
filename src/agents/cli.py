"""Command line for the five agents and the end-to-end pipeline.

    python -m src.agents impact   --repo R --story "..."            -> impact.md + impact.json
    python -m src.agents code     --repo R --impact impact.json      -> branch, commit, PR
    python -m src.agents review   --repo R --impact impact.json --pr N -> verdict, merge commit id
    python -m src.agents deploy   --repo R --commit C --branch B     -> build, package, deploy / notify
    python -m src.agents regress  --repo R --impact impact.json      -> test report
    python -m src.agents pipeline --repo R --story "..."             -> all five, in order
    python -m src.agents demo                                        -> three recorded scenarios, offline

Every command prints one JSON object on stdout. Run from the BlastRadius repo
root with ``uv run --extra graph``.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

from src.agents.coding import CodingAgent, save_result
from src.agents.deploy import BuildDeployAgent
from src.agents.forge import get_forge
from src.agents.impact import ImpactAnalysis, ImpactAnalysisAgent
from src.agents.regression import RegressionSuiteAgent
from src.agents.review import PRReviewerAgent


def _emit(obj) -> None:
    print(json.dumps(asdict(obj) if is_dataclass(obj) else obj, indent=2, default=str))


def _state(args) -> Path:
    return Path(args.state_dir) if args.state_dir else Path(args.repo).resolve() / ".blastradius"


def _story(args) -> str:
    if args.story_file:
        return Path(args.story_file).read_text(encoding="utf-8").strip()
    if not args.story:
        sys.exit("give --story or --story-file")
    return args.story


def pipeline(repo: Path, story: str, *, title: str | None = None, provider: str | None = None, forge_kind: str = "local",
             patch: str | None = None, scope_policy: str = "strict", full: bool = True, build_cmd: str | None = None,
             state_dir: Path | None = None) -> dict:
    """Run the five agents in order and return every step's output."""
    repo = Path(repo).resolve()
    state = state_dir or repo / ".blastradius"
    steps: list[dict] = []
    impact, out = ImpactAnalysisAgent(provider).run(story, repo, state, title=title)
    steps.append({"agent": "Impact Analysis Agent", "input": {"story": story, "codebase": repo.name},
                  "output": {"document": str(out / "impact.md"), "risk": impact.risk, "change_files": impact.change_files,
                             "tests_at_risk": len(impact.tests), "unaffected_tests": len(impact.unaffected_tests)}})
    forge = get_forge(forge_kind, repo, state)
    coded = CodingAgent(provider).run(impact, repo, forge, patch=patch)
    save_result(coded, state)
    steps.append({"agent": "Coding Agent", "input": {"impact": str(out / "impact.json")},
                  "output": {"branch": coded.branch, "commit": coded.commit, "changed_files": coded.changed_files,
                             "pr": coded.pr_number, "mode": coded.mode}})
    review = PRReviewerAgent(provider).run(coded.pr_number, impact, repo, forge, state, scope_policy=scope_policy)
    steps.append({"agent": "PR Reviewer Agent", "input": {"pr": coded.pr_number, "impact": str(out / "impact.json")},
                  "output": {"verdict": review.verdict, "merged": review.merged, "commit_id": review.commit_id,
                             "checks": review.checks, "review": review.markdown_path}})
    result = {"repo": str(repo), "impact": impact, "coding": coded, "review": review, "steps": steps}
    if not review.merged:
        steps.append({"agent": "Build & Deploy Agent", "skipped": "the PR was not merged"})
        steps.append({"agent": "Regression Suite Agent", "skipped": "nothing was merged"})
        return result
    deploy = BuildDeployAgent().run(review.commit_id, impact.base_branch, repo, state, build_cmd=build_cmd)
    steps.append({"agent": "Build & Deploy Agent", "input": {"commit": review.commit_id, "branch": impact.base_branch},
                  "output": {"status": deploy.status, "build": deploy.build_command, "exit_code": deploy.build_exit_code,
                             "package": deploy.package, "deployed_to": deploy.deployed_to,
                             "notification": deploy.notification}})
    report = RegressionSuiteAgent().run(impact, repo, state, commit=review.commit_id, full=full)
    steps.append({"agent": "Regression Suite Agent", "input": {"impact": str(out / "impact.json"), "suite": "tests/"},
                  "output": {"verdict": report.verdict, "selected": report.selected["counts"],
                             "full": report.full["counts"] if report.full else None, "impact_recall": report.impact_recall,
                             "missed_failures": report.missed_failures, "report": report.markdown_path}})
    result.update(deploy=deploy, regression=report)
    return result


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    p = argparse.ArgumentParser(prog="python -m src.agents", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, impact: bool = False):
        sp.add_argument("--repo", required=True, help="git working copy of the target codebase")
        sp.add_argument("--state-dir", help="where agent outputs go (default <repo>/.blastradius)")
        sp.add_argument("--provider", choices=["offline", "anthropic"], help="LLM provider (default: anthropic if ANTHROPIC_API_KEY is set)")
        sp.add_argument("--forge", choices=["local", "github"], default="local")
        if impact:
            sp.add_argument("--impact", required=True, help="impact.json from the Impact Analysis Agent")

    sp = sub.add_parser("impact", help="user story + codebase -> impact analysis document"); common(sp)
    sp.add_argument("--story"); sp.add_argument("--story-file"); sp.add_argument("--title")
    sp = sub.add_parser("code", help="impact analysis + codebase -> changed files + PR"); common(sp, True)
    sp.add_argument("--patch", help="recorded change set (JSON) instead of an LLM"); sp.add_argument("--branch")
    sp = sub.add_parser("review", help="PR + impact analysis -> review, merge, commit id"); common(sp, True)
    sp.add_argument("--pr", type=int, required=True); sp.add_argument("--no-merge", action="store_true")
    sp.add_argument("--scope-policy", choices=["strict", "warn"], default="strict")
    sp = sub.add_parser("deploy", help="commit id + branch -> build and deploy; notify on failure"); common(sp)
    sp.add_argument("--commit", required=True); sp.add_argument("--branch", required=True)
    sp.add_argument("--build-cmd"); sp.add_argument("--deploy-dir"); sp.add_argument("--github-workflow", help="dispatch this workflow instead of building locally")
    sp = sub.add_parser("regress", help="impact analysis + regression suite -> test report"); common(sp, True)
    sp.add_argument("--commit"); sp.add_argument("--full", action="store_true")
    sp.add_argument("--runner-cmd", help="non-Python runner, e.g. 'mvn -q test -Dtest={tests}'"); sp.add_argument("--junit-glob", default="**/TEST-*.xml")
    sp = sub.add_parser("pipeline", help="all five agents in order"); common(sp)
    sp.add_argument("--story"); sp.add_argument("--story-file"); sp.add_argument("--title"); sp.add_argument("--patch")
    sp.add_argument("--scope-policy", choices=["strict", "warn"], default="strict"); sp.add_argument("--build-cmd")
    sp = sub.add_parser("demo", help="three recorded scenarios on a sample repo, fully offline")
    sp.add_argument("--workdir", help="where to create the sample repos (default: a temp dir)")
    sp.add_argument("--export", help="also write the demo summary JSON here (e.g. demo-web/public/data/agents.json)")

    args = p.parse_args(argv)
    if args.cmd == "demo":
        from src.agents.demo.run_demo import run_demo

        summary = run_demo(Path(args.workdir) if args.workdir else None, Path(args.export) if args.export else None)
        _emit({"workdir": summary["workdir"], "scenarios": [{k: s[k] for k in ("id", "title", "outcome")} for s in summary["scenarios"]]})
        return 0

    state = _state(args)
    if args.cmd == "impact":
        analysis, out = ImpactAnalysisAgent(args.provider).run(_story(args), args.repo, state, title=args.title)
        _emit({"document": str(out / "impact.md"), "json": str(out / "impact.json"), "risk": analysis.risk,
               "change_files": analysis.change_files, "tests_at_risk": [t.test_id for t in analysis.tests]})
    elif args.cmd == "code":
        res = CodingAgent(args.provider).run(ImpactAnalysis.load(args.impact), args.repo, get_forge(args.forge, Path(args.repo).resolve(), state),
                                             patch=args.patch, branch=args.branch)
        save_result(res, state)
        _emit(res)
    elif args.cmd == "review":
        _emit(PRReviewerAgent(args.provider).run(args.pr, ImpactAnalysis.load(args.impact), args.repo,
                                                 get_forge(args.forge, Path(args.repo).resolve(), state), state,
                                                 merge=not args.no_merge, scope_policy=args.scope_policy))
    elif args.cmd == "deploy":
        agent = BuildDeployAgent()
        if args.github_workflow:
            _emit(agent.run_github(args.commit, args.branch, args.repo, get_forge("github", Path(args.repo).resolve(), state), args.github_workflow, state))
        else:
            _emit(agent.run(args.commit, args.branch, args.repo, state, build_cmd=args.build_cmd, deploy_dir=args.deploy_dir))
    elif args.cmd == "regress":
        _emit(RegressionSuiteAgent().run(ImpactAnalysis.load(args.impact), args.repo, state, commit=args.commit, full=args.full,
                                         runner_cmd=args.runner_cmd, junit_glob=args.junit_glob))
    elif args.cmd == "pipeline":
        res = pipeline(Path(args.repo), _story(args), title=args.title, provider=args.provider, forge_kind=args.forge,
                       patch=args.patch, scope_policy=args.scope_policy, build_cmd=args.build_cmd, state_dir=state)
        _emit({"steps": res["steps"]})
    return 0
