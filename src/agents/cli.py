"""Command line for the five agents and the end-to-end pipeline.

    python -m src.agents impact   --repo R --story "..."            -> impact.md + impact.json
    python -m src.agents code     --repo R --impact impact.json      -> branch, commit, PR
    python -m src.agents review   --repo R --impact impact.json --pr N -> verdict, merge commit id
    python -m src.agents deploy   --repo R --commit C --branch B     -> build, package, deploy / notify
    python -m src.agents regress  --repo R --impact impact.json      -> test report (E1 order first)
    python -m src.agents triage   --repo R --report report.json      -> mine / inherited / flaky per failure
    python -m src.agents repair   --repo R --report report.json      -> patch for the failures triaged mine
    python -m src.agents pipeline --repo R --story "..."             -> impact, code, regress, triage, repair, review, deploy
    python -m src.agents pipeline --stages classic ...               -> the original five-agent order
    python -m src.agents demo                                        -> four recorded scenarios, offline
    python -m src.agents ask      --repo R --question "..."          -> answer with [S1]..[S8] citations (exploratory RAG)
    python -m src.agents bot      --repo R --base B --head H --pr N  -> the PR comment (posts it on GitHub Actions)

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
             state_dir: Path | None = None, stages: str = "classic", repair_llm=None) -> dict:
    """Run the agents in order and return every step's output.

    ``stages="classic"`` is the original five-agent order (review and merge, then deploy and regress).
    ``stages="2.0"`` is impact, code, regress, triage, repair (<= 2 attempts), review, deploy
    (:func:`src.agents.flow.pipeline_v2`); only its Repair step may call an LLM, passed as ``repair_llm``.
    """
    if stages == "2.0":
        from src.agents.flow import pipeline_v2

        return pipeline_v2(Path(repo), story, title=title, provider=provider, forge_kind=forge_kind, patch=patch,
                           scope_policy=scope_policy, build_cmd=build_cmd, state_dir=state_dir, repair_llm=repair_llm)
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


def _repair_llm(state: Path):
    """The Repair agent's model for the pipeline: Groq (cached under the state dir) when a key is set, else None."""
    import os

    if os.environ.get("BR_OFFLINE") == "1" or not os.environ.get("GROQ_API_KEY"):
        return None
    from src.agents.llm import GroqLLM
    from src.agents.llm_cache import LLMCache

    return GroqLLM(api_key=os.environ["GROQ_API_KEY"], model=os.environ.get("BR_AGENT_MODEL") or "openai/gpt-oss-120b",
                   cache=LLMCache(state / "llm_cache.jsonl"))


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
    sp = sub.add_parser("triage", help="regression report + history -> mine / inherited / flaky per failure")
    sp.add_argument("--repo", required=True); sp.add_argument("--state-dir")
    sp.add_argument("--report", required=True, help="report.json from the Regression Suite Agent")
    sp.add_argument("--branch", default="main"); sp.add_argument("--commit", default="")
    sp.add_argument("--rules-only", action="store_true", help="ignore the E2 model; use R-branch / R-msg")
    sp = sub.add_parser("repair", help="failure triaged mine -> patch, accepted only if the full suite passes")
    sp.add_argument("--repo", required=True); sp.add_argument("--state-dir")
    sp.add_argument("--report", required=True, help="report.json from the Regression Suite Agent")
    sp.add_argument("--arm", choices=["R0", "R1", "R2", "R3"], default="R3")
    sp.add_argument("--provider", choices=["offline", "groq"], help="LLM provider (default: groq if GROQ_API_KEY is set)")
    sp.add_argument("--apply", action="store_true", help="write the accepted patch into the working tree")
    sp = sub.add_parser("ask", help="question about a change or failing test -> answer with citations (exploratory RAG)")
    sp.add_argument("--repo", required=True); sp.add_argument("--question", required=True)
    sp.add_argument("--state-dir"); sp.add_argument("--provider", choices=["offline", "groq"],
                                                    help="LLM provider (default: groq if GROQ_API_KEY is set)")
    sp.add_argument("--interim", default="data/interim", help="BR-Bench interim tables for the failure-history source")
    sp.add_argument("--no-dense", action="store_true", help="BM25 only (no embedding model)")
    sp = sub.add_parser("bot", help="PR bot: impact, regression, triage, validated repair -> one comment")
    sp.add_argument("--repo", required=True); sp.add_argument("--base", required=True); sp.add_argument("--head", required=True)
    sp.add_argument("--pr", type=int, required=True); sp.add_argument("--state-dir")
    sp.add_argument("--python", help="interpreter for the target's test suites (default: this one)")
    sp.add_argument("--provider", choices=["offline", "groq"], help="LLM provider (default: groq if GROQ_API_KEY is set)")
    sp.add_argument("--forge", choices=["local", "github"], help="where to post (default: github on GitHub Actions, else local)")
    g = sp.add_mutually_exclusive_group()
    g.add_argument("--post", action="store_true", help="post the comment (default on GitHub Actions)")
    g.add_argument("--no-post", action="store_true", help="only print the comment")
    sp.add_argument("--audit-run", help="decision-log run id under logs/agent/ (D-71); default bot-pr<N>-<UTC stamp>")
    sp.add_argument("--fix-mode", choices=["suggest", "ask", "auto"], help="D-70 gate (default: BR_FIX_MODE or suggest)")
    sp.add_argument("--slug", help="owner/name of the GitHub repository (needed for a fix PR)")
    sp.add_argument("--head-branch", help="the PR's head branch (the fix PR's base)")
    sp = sub.add_parser("pipeline", help="impact, code, regress, triage, repair, review, deploy"); common(sp)
    sp.add_argument("--stages", choices=["2.0", "classic"], default="2.0")
    sp.add_argument("--story"); sp.add_argument("--story-file"); sp.add_argument("--title"); sp.add_argument("--patch")
    sp.add_argument("--scope-policy", choices=["strict", "warn"], default="strict"); sp.add_argument("--build-cmd")
    sp = sub.add_parser("demo", help="four recorded scenarios on a sample repo, fully offline")
    sp.add_argument("--workdir", help="where to create the sample repos (default: a temp dir)")
    sp.add_argument("--export", help="also write the demo summary JSON here (e.g. demo-web/public/data/agents.json)")

    args = p.parse_args(argv)
    if args.cmd == "demo":
        from src.agents.demo.run_demo import run_demo

        summary = run_demo(Path(args.workdir) if args.workdir else None, Path(args.export) if args.export else None)
        _emit({"workdir": summary["workdir"], "scenarios": [{k: s[k] for k in ("id", "title", "outcome")} for s in summary["scenarios"]]})
        return 0
    if args.cmd == "triage":
        from src.agents.triage import TriageAgent, failures_of

        state = _state(args)
        rep = json.loads(Path(args.report).read_text(encoding="utf-8"))
        res = TriageAgent(use_model=not args.rules_only).run(failures_of(rep), state / "history" / "test_outcomes.jsonl",
                                                             branch=args.branch, commit=args.commit)
        _emit({"model": res.model, "counts": res.counts(), "failures": [asdict(f) for f in res.failures]})
        return 0
    if args.cmd == "repair":
        from src.agents.llm import GroqLLM, get_llm
        from src.agents.llm_cache import LLMCache
        from src.agents.repair import FailureReport, RepairAgent
        from src.agents.triage import TriageAgent, failures_of
        from src.eval.seeded.build import source_files

        repo = Path(args.repo).resolve()
        state = _state(args)
        rep = json.loads(Path(args.report).read_text(encoding="utf-8"))
        fails = failures_of(rep)
        tri = TriageAgent().run(fails, state / "history" / "test_outcomes.jsonl")
        mine = {f.test_id for f in tri.mine}
        by_id = {f["test_id"]: f for f in fails}
        llm = get_llm(args.provider or ("groq" if __import__("os").environ.get("GROQ_API_KEY") else "offline"))
        if isinstance(llm, GroqLLM):
            llm.cache = LLMCache(state / "llm_cache.jsonl")
        report = FailureReport([{"test_id": t, "output": by_id[t].get("message", "")} for t in sorted(mine)] or
                               [{"test_id": t, "output": by_id[t].get("message", "")} for t in sorted(by_id)],
                               triage="mine" if mine else tri.failures[0].klass if tri.failures else "mine")
        dirs = sorted({p.split("/")[0] for p in __import__("src.agents.gitops", fromlist=["x"]).tracked_files(repo)
                       if p.endswith(".py") and not p.startswith(("tests/", "test"))})
        srcs = source_files(repo, {"src_dirs": dirs})
        files_out: dict = {}

        def validate(files: dict[str, str]) -> tuple[bool, str]:
            files_out.update(files)
            return True, ""  # the CLI proposes; `pipeline` validates against the full suite

        res = RepairAgent(llm, args.arm).run(repo, srcs, report, validate)
        if args.apply and files_out:
            for p, text in files_out.items():
                (repo / p).write_text(text, encoding="utf-8")
        _emit({"triage": tri.counts(), "action": res.action, "note": res.note, "chunks": [f"{c.file}::{c.qualname}" for c in res.chunks],
               "attempts": len(res.attempts), "proposed_files": sorted(files_out), "applied": bool(args.apply and files_out)})
        return 0

    if args.cmd == "bot":
        import os

        from src.agents import bot as botmod
        from src.agents.ask import chat_llm

        repo = Path(args.repo).resolve()
        state = _state(args)
        on_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        provider = args.provider or ("groq" if os.environ.get("GROQ_API_KEY") else "offline")
        from src.agents.llm_provider import with_fallback

        cache_path = state / "bot_llm_cache.jsonl"
        llm = with_fallback(chat_llm(provider, cache_path), os.environ.get("BR_AGENT_MODEL") or "openai/gpt-oss-120b",
                            cache_path) if provider != "offline" else None
        from datetime import datetime, timezone

        from src.agents import fixpr
        from src.agents.audit import DecisionLog

        mode = args.fix_mode or fixpr.fix_mode()
        run_id = args.audit_run or f"bot-pr{args.pr}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        log = DecisionLog(run_id)
        out = botmod.run_bot(repo, args.base, args.head, args.pr, llm=llm,
                             state_dir=state, python=args.python, audit=log, fix_mode=mode)
        print(out.comment)
        posted = args.post or (on_actions and not args.no_post)
        if posted:
            forge = get_forge(args.forge or ("github" if on_actions else "local"), repo, state)
            print(json.dumps(botmod.post(out, forge, args.pr, args.head)), file=sys.stderr)
        fix = out.stats.get("fix")
        result: dict = {"audit_run": run_id, "log": str(log.path), "fix_mode": mode, "validated": out.validated}
        if fix and mode != "suggest":
            if not (args.slug and args.head_branch):
                log.record("system", "pr", "gate", "reject", "No --slug or --head-branch was given, so no fix PR can be "
                           "opened", {"mode": mode})
            else:
                from src.agents.audit import sha256

                loc = fix.get("localize") or {}
                plan = fixpr.FixPlan(repo_dir=str(repo), slug=args.slug, pr_number=args.pr, head_branch=args.head_branch,
                                     head_sha=out.stats["head"], files=fix["files"], checks=fix["checks"],
                                     patch_sha256=sha256(fix["diff"]), ranked=out.stats.get("risk", []),
                                     triage=out.stats.get("triage", []), evidence_path=loc.get("paths", []),
                                     diff=fix["diff"])
                plan.save(log)
                result.update(fixpr.apply_fix(plan, log, mode=mode))
        elif mode == "suggest" and out.validated:
            fixpr.apply_fix(fixpr.FixPlan(str(repo), args.slug or "", args.pr, args.head_branch or "", out.stats["head"],
                                          {}, [], ""), log, mode="suggest")
        print(json.dumps(result), file=sys.stderr)
        return 0

    if args.cmd == "ask":
        from src.agents.ask import AskAgent, chat_llm
        from src.rag.knowledge import Knowledge, code_docs, load_failure_docs, load_repo_docs

        repo = Path(args.repo).resolve()
        state = _state(args)
        embedder = None
        if not args.no_dense:
            try:
                from src.rag.index import FastEmbedder

                embedder = FastEmbedder()
            except Exception as exc:   # no fastembed or no weights on disk: BM25 only, said in the output
                print(f"dense retrieval unavailable ({type(exc).__name__}); BM25 only", file=sys.stderr)
        docs = code_docs(repo) + load_repo_docs(repo)
        interim = Path(args.interim)
        if (interim / "parsed_outcomes.parquet").exists():
            docs += load_failure_docs(interim)
        kb = Knowledge(docs, embedder)
        provider = args.provider or ("groq" if __import__("os").environ.get("GROQ_API_KEY") else "offline")
        llm = chat_llm(provider, state / "ask_llm_cache.jsonl")
        _emit(AskAgent(kb, repo, llm).ask(args.question).to_json())
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
                       patch=args.patch, scope_policy=args.scope_policy, build_cmd=args.build_cmd, state_dir=state,
                       stages=args.stages, repair_llm=_repair_llm(state))
        _emit({"steps": res["steps"]})
    return 0
