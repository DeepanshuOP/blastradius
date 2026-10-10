"""Four recorded scenarios of the agent workflow on the ``shopcart`` sample repo.

Fully offline: impact analysis is keyword + code graph + the E1 model, the coding agent
applies the recorded change sets in ``patches/``, and a local forge (PRs as JSON, merges are
real ``git merge --no-ff``). Each scenario gets a fresh copy of the sample repo. Scenario 4 is
the one place a language model is involved: the Repair agent's single reply is REPLAYED from
``llm_cache.jsonl`` (recorded once from Groq's free tier with ``BR_DEMO_RECORD=1``), so
``make agents-demo`` stays offline and deterministic.

1. ``clean``       the change stays in scope: reviewed, merged, built, deployed, regression PASS.
2. ``blocked``     the change also edits receipts (out of scope): the reviewer requests changes; nothing merges.
3. ``build-fails`` the same change with the reviewer in warn mode: it merges, the full build
                   fails on the receipt tests, the deploy agent notifies, and the regression
                   report shows the failures the impact scope did not predict.
4. ``repaired``    the change introduces a bug (the cap becomes a floor). The suite fails before
                   review, the Triage agent says the failures are the change's own, the Repair agent
                   patches it, the full suite passes, the PR is approved, merged and deployed.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.agents import gitops
from src.agents.cli import pipeline
from src.agents.forge import LocalForge
from src.agents.llm import GroqLLM
from src.agents.llm_cache import LLMCache
from src.agents.regression import run_pytest

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "sample_repo"
PATCHES = HERE / "patches"
DEMO_CACHE = HERE / "llm_cache.jsonl"
REPAIR_MODEL = "openai/gpt-oss-120b"
STORY = ("As a shopper, I want to apply the discount code FESTIVE20 at checkout to get 20% off "
         "my cart total, capped at Rs 500.")
TITLE = "FESTIVE20 discount code"

SCENARIOS = [
    ("clean", "Clean change", "festive20.json", "strict",
     "The coding agent changes only what the story needs."),
    ("blocked", "Out-of-scope change blocked", "festive20_scope_creep.json", "strict",
     "The coding agent also rewrites receipt formatting, which the story never asked for."),
    ("build-fails", "Build fails, team notified", "festive20_scope_creep.json", "warn",
     "Same out-of-scope change, but the reviewer only warns, so it merges and the build has to catch it."),
]


def make_repo(dest: Path) -> Path:
    """Fresh git repo with the sample code, one commit on ``main``."""
    shutil.copytree(SAMPLE, dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    gitops.git(dest, "init", "-q", "-b", "main")
    gitops.git(dest, "config", "user.name", "shopcart maintainer")
    gitops.git(dest, "config", "user.email", "maintainer@shopcart.invalid")
    gitops.git(dest, "add", "-A")
    gitops.git(dest, "commit", "-q", "-m", "chore: initial shopcart library")
    gitops.exclude_state_dir(dest)
    return dest


def baseline(repo: Path) -> dict:
    """A nightly full regression run on main, recorded as failure history."""
    state = repo / ".blastradius"
    out = state / "reports" / "baseline"
    out.mkdir(parents=True, exist_ok=True)
    run = run_pytest(repo, None, out / "full.xml", "baseline")
    hist = state / "history" / "test_outcomes.jsonl"
    hist.parent.mkdir(parents=True, exist_ok=True)
    sha = gitops.head_sha(repo)
    with hist.open("a", encoding="utf-8") as fh:
        for r in run.results:
            fh.write(json.dumps({"ts": "baseline", "commit": sha, "test_id": r.test_id, "outcome": r.outcome}) + "\n")
    return run.counts()


def _read(path: str | Path | None) -> str:
    return Path(path).read_text(encoding="utf-8") if path and Path(path).exists() else ""


def run_scenario(root: Path, sid: str, title: str, patch: str, policy: str, desc: str) -> dict:
    """Run one scenario end to end and collect what each agent produced."""
    repo = make_repo(root / f"shopcart-{sid}")
    base_counts = baseline(repo)
    res = pipeline(repo, STORY, title=TITLE, provider="offline", patch=str(PATCHES / patch), scope_policy=policy)
    state = repo / ".blastradius"
    impact, coded, review = res["impact"], res["coding"], res["review"]
    pr = LocalForge(repo, state).get_pr(coded.pr_number)
    steps = [
        {"agent": "Impact Analysis Agent", "status": "ok",
         "headline": f"Risk {impact.risk.upper()}: {len(impact.change_files)} file(s) to change, {len(impact.tests)} of "
                     f"{len(impact.tests) + len(impact.unaffected_tests)} tests at risk",
         "inputs": {"user story": STORY, "codebase": f"shopcart @ {impact.base_sha[:12]}"},
         "outputs": {"files to change": impact.change_files, "tests at risk": [t.test_id for t in impact.tests]},
         "document": _read(state / "impact" / impact.base_sha[:12] / "impact.md")},
        {"agent": "Coding Agent", "status": "ok",
         "headline": f"PR #{coded.pr_number} opened from {coded.branch} ({len(coded.changed_files)} files changed)",
         "inputs": {"impact analysis": "impact.json", "codebase": "shopcart"},
         "outputs": {"branch": coded.branch, "commit": coded.commit[:12], "changed files": coded.changed_files, "mode": coded.mode},
         "document": f"# PR #{pr.number}: {pr.title}\n\n{pr.body}\n"},
        {"agent": "PR Reviewer Agent", "status": "ok" if review.verdict == "APPROVE" else "blocked",
         "headline": f"{review.verdict}" + (f": merged as {review.commit_id[:12]}" if review.merged else ": not merged"),
         "inputs": {"pull request": f"#{coded.pr_number}", "impact analysis": "impact.json", "scope policy": policy},
         "outputs": {"verdict": review.verdict, "merged": review.merged, "commit id": (review.commit_id or "")[:12],
                     "checks": review.checks},
         "document": _read(review.markdown_path)},
    ]
    notifications = []
    if "deploy" in res:
        dep, reg = res["deploy"], res["regression"]
        steps.append({"agent": "Build & Deploy Agent", "status": "ok" if dep.status == "deployed" else "failed",
                      "headline": ("Built and deployed " if dep.status == "deployed" else "Build FAILED for ") + f"{dep.commit[:12]} on {dep.branch}"
                                  + ("" if dep.status == "deployed" else "; notification sent, nothing deployed"),
                      "inputs": {"commit id": dep.commit[:12], "branch": dep.branch},
                      "outputs": {"status": dep.status, "build": dep.build_command, "exit code": dep.build_exit_code,
                                  "package": Path(dep.package).name if dep.package else None},
                      "document": "```\n" + "\n".join(dep.log_tail) + "\n```\n"})
        if dep.notification:
            notifications.append(dep.notification)
        steps.append({"agent": "Regression Suite Agent", "status": "ok" if reg.verdict == "PASS" else "failed",
                      "headline": f"{reg.verdict}: selected {reg.selected['counts']['passed']}/{reg.selected['counts']['total']} passed; "
                                  f"full suite {reg.full['counts']['passed']}/{reg.full['counts']['total']} passed; impact recall {reg.impact_recall}",
                      "inputs": {"impact analysis": "impact.json", "regression suite": "tests/ (full)"},
                      "outputs": {"verdict": reg.verdict, "selection": reg.selection_ratio, "impact recall": reg.impact_recall,
                                  "missed failures": reg.missed_failures},
                      "document": _read(reg.markdown_path)})
        outcome = "Deployed" if dep.status == "deployed" else "Build failed, team notified"
    else:
        steps += [{"agent": "Build & Deploy Agent", "status": "skipped", "headline": "Skipped: the PR was not merged",
                   "inputs": {}, "outputs": {}, "document": ""},
                  {"agent": "Regression Suite Agent", "status": "skipped", "headline": "Skipped: nothing was merged",
                   "inputs": {}, "outputs": {}, "document": ""}]
        outcome = "Blocked at review"
    return {"id": sid, "title": title, "description": desc, "scope_policy": policy, "patch": patch, "outcome": outcome,
            "baseline": base_counts, "repo": str(repo), "steps": steps, "notifications": notifications}


def _demo_llm():
    """The Repair agent's model for scenario 4: replay the recorded reply, or record one (BR_DEMO_RECORD=1)."""
    if os.environ.get("BR_DEMO_RECORD") == "1" and os.environ.get("GROQ_API_KEY"):
        return GroqLLM(api_key=os.environ["GROQ_API_KEY"], model=REPAIR_MODEL, cache=LLMCache(DEMO_CACHE))
    if not DEMO_CACHE.exists():
        return None
    return GroqLLM(api_key="replay", model=REPAIR_MODEL, cache=LLMCache(DEMO_CACHE, replay=True),
                   ledger=Path(os.devnull))


def run_repair_scenario(root: Path) -> dict:
    """Scenario 4: a bug introduced by the change is triaged as mine, repaired, verified and deployed."""
    sid = "repaired"
    repo = make_repo(root / f"shopcart-{sid}")
    base_counts = baseline(repo)
    llm = _demo_llm()
    res = pipeline(repo, STORY, title=TITLE, provider="offline", patch=str(PATCHES / "festive20_bug.json"),
                   stages="2.0", repair_llm=llm)
    state = repo / ".blastradius"
    impact, coded = res["impact"], res["coding"]
    pr = LocalForge(repo, state).get_pr(coded.pr_number)
    reg = res["regression"]
    steps = [
        {"agent": "Impact Analysis Agent", "status": "ok",
         "headline": f"Risk {impact.risk.upper()}: {len(impact.tests)} of {len(impact.tests) + len(impact.unaffected_tests)} "
                     f"tests at risk, ranked by the {impact.ranker} model",
         "inputs": {"user story": STORY, "codebase": f"shopcart @ {impact.base_sha[:12]}"},
         "outputs": {"files to change": impact.change_files, "tests at risk": [t.test_id for t in impact.tests],
                     "ranker": impact.ranker},
         "document": _read(state / "impact" / impact.base_sha[:12] / "impact.md")},
        {"agent": "Coding Agent", "status": "ok",
         "headline": f"PR #{coded.pr_number} opened from {coded.branch} ({len(coded.changed_files)} files changed)",
         "inputs": {"impact analysis": "impact.json"},
         "outputs": {"branch": coded.branch, "commit": coded.commit[:12], "changed files": coded.changed_files, "mode": coded.mode},
         "document": f"# PR #{pr.number}: {pr.title}\n\n{pr.body}\n"},
        {"agent": "Regression Suite Agent", "status": "ok" if reg.verdict == "PASS" else "failed",
         "headline": f"{reg.verdict} before review: first failing test at position {reg.first_failure_position} "
                     f"of the run, full suite {reg.full['counts']['passed']}/{reg.full['counts']['total']} passed",
         "inputs": {"commit": coded.commit[:12], "order": impact.ranker},
         "outputs": {"verdict": reg.verdict, "first failure position": reg.first_failure_position,
                     "first failing test": reg.first_failure_test, "full": reg.full["counts"]},
         "document": _read(reg.markdown_path)},
    ]
    notifications = []
    if "triage" in res:
        tri = res["triage"]
        steps.append({"agent": "Triage Agent", "status": "ok",
                      "headline": f"{len(tri.failures)} failing test(s): " + ", ".join(f"{n} {k}" for k, n in tri.counts().items() if n),
                      "inputs": {"failures": len(tri.failures), "history": "history/test_outcomes.jsonl"},
                      "outputs": {"model": tri.model, "classes": {f.test_id: f.klass for f in tri.failures}},
                      "document": "\n".join(f"- `{f.test_id}`: **{f.klass}** ({f.confidence:.2f}): {f.reason}" for f in tri.failures)})
    if "repair" in res:
        rp = res["repair"]
        fixed = next((a.files for a in rp.attempts if a.applied and rp.accepted), {})
        steps.append({"agent": "Repair Agent", "status": "ok" if rp.accepted else "failed",
                      "headline": ("Patch accepted: the full suite passes" if rp.accepted else "No patch made the suite pass")
                                  + f" ({len(rp.attempts)} attempt(s), arm R3)",
                      "inputs": {"failing (mine)": [f.test_id for f in res["triage"].mine],
                                 "chunks shown to the model": [f"{c.file}::{c.qualname}" for c in rp.chunks]},
                      "outputs": {"accepted": rp.accepted, "files": sorted(fixed),
                                  "tokens": sum(int((a.usage or {}).get("total_tokens", 0)) for a in rp.attempts)},
                      "document": "\n\n".join(f"```\n{a.response}\n```" for a in rp.attempts)})
    if "regression_after" in res:
        aft = res["regression_after"]
        steps.append({"agent": "Regression Suite Agent (after repair)", "status": "ok" if aft.verdict == "PASS" else "failed",
                      "headline": f"{aft.verdict}: full suite {aft.full['counts']['passed']}/{aft.full['counts']['total']} passed",
                      "inputs": {"commit": "repaired PR head"}, "outputs": {"verdict": aft.verdict, "full": aft.full["counts"]},
                      "document": _read(aft.markdown_path)})
    if "review" in res:
        review = res["review"]
        steps.append({"agent": "PR Reviewer Agent", "status": "ok" if review.verdict == "APPROVE" else "blocked",
                      "headline": f"{review.verdict}" + (f": merged as {review.commit_id[:12]}" if review.merged else ": not merged"),
                      "inputs": {"pull request": f"#{coded.pr_number}"},
                      "outputs": {"verdict": review.verdict, "merged": review.merged, "commit id": (review.commit_id or "")[:12],
                                  "checks": review.checks},
                      "document": _read(review.markdown_path)})
    if "deploy" in res:
        dep = res["deploy"]
        steps.append({"agent": "Build & Deploy Agent", "status": "ok" if dep.status == "deployed" else "failed",
                      "headline": ("Built and deployed " if dep.status == "deployed" else "Build FAILED for ") + f"{dep.commit[:12]} on {dep.branch}",
                      "inputs": {"commit id": dep.commit[:12], "branch": dep.branch},
                      "outputs": {"status": dep.status, "build": dep.build_command, "exit code": dep.build_exit_code},
                      "document": "```\n" + "\n".join(dep.log_tail) + "\n```\n"})
    log = state / "notifications.jsonl"
    if log.exists():
        notifications = [json.loads(ln) for ln in log.read_text().splitlines() if ln.strip()]
    return {"id": sid, "title": "Bug introduced, repaired, deployed",
            "description": "The change turns the discount cap into a floor. The suite fails before review, the failures are "
                           "triaged as the change's own, the Repair agent patches them, the full suite passes, and the PR merges.",
            "scope_policy": "strict", "patch": "festive20_bug.json", "outcome": res.get("outcome", ""),
            "baseline": base_counts, "repo": str(repo), "steps": steps, "notifications": notifications}


def run_demo(workdir: Path | None = None, export: Path | None = None) -> dict:
    """Run all three scenarios; return (and optionally export) the summary."""
    root = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="br-agents-demo-"))
    root.mkdir(parents=True, exist_ok=True)
    for sid, *_ in SCENARIOS:
        shutil.rmtree(root / f"shopcart-{sid}", ignore_errors=True)
    scenarios = [run_scenario(root, *s) for s in SCENARIOS]
    shutil.rmtree(root / "shopcart-repaired", ignore_errors=True)
    if _demo_llm() is not None:
        scenarios.append(run_repair_scenario(root))
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "story": STORY, "title": TITLE, "workdir": str(root),
        "sample_repo": {"name": "shopcart", "files": sorted(str(p.relative_to(SAMPLE)) for p in SAMPLE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)},
        "note": "Recorded offline: impact analysis is keyword + code graph + the E1 model, change sets are recorded, the forge is "
                "local. The one model reply (scenario 4, Repair agent) is replayed from a cache recorded with Groq's free tier.",
        "scenarios": scenarios,
    }
    (root / "agents_demo.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    if export:
        export.parent.mkdir(parents=True, exist_ok=True)
        # No machine-local path leaves the temp dir: every occurrence of it becomes "<temp>".
        text = json.dumps(summary, indent=2, ensure_ascii=False).replace(str(root.resolve()), "<temp>").replace(str(root), "<temp>")
        export.write_text(text, encoding="utf-8")
    return summary
