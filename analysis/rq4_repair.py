"""E3 / RQ4: does change-awareness help an LLM repair a failure that a change introduced?

    uv run --env-file .env python -m analysis.rq4_repair run  --model openai/gpt-oss-120b   (live, Groq free tier)
    uv run python -m analysis.rq4_repair eval                                              (replay, offline)

`run` calls the model through `src/agents/llm.py` (D-58) and caches every request and response in
`eval/llm_cache/e3_<model-slug>.jsonl`. `eval` replays every cache file with the network
forbidden (`BR_LLM_REPLAY=1`) and regenerates `paper/generated/rq4_repair.md`. This file is NOT part of
`make tables`: it depends on a model, and the numbers are only as reproducible as the recorded replies.

Detection (position of the first failing test file under E1 ordering vs alphabetical vs random) and
retrieval (is the seeded function among the <= 3 chunks) need no model and run on ALL tasks. The LLM arms
run on a deterministic operator-stratified subset (`BR_E3_TASKS`, default 20, seed 0), identical for
every arm and model. Spend is zero (free tier); tokens are reported instead of a price.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

from analysis import paper_md
from src.agents.llm import DailyQuotaReached, GroqLLM, get_llm
from src.agents.llm_cache import CacheMiss, LLMCache, model_slug
from src.agents.repair import ARMS, FailureReport, RepairAgent, build_prompt, index_functions, select_chunks
from src.eval import stats as S
from src.eval.seeded.build import SEEDED, source_files
from src.eval.seeded.validate import head_state, make_validator
from src.features.online import diff_stats, rank_tests, tracked_files
from src.parse.changeset import is_conventional_test_file

OUT = Path("eval/seeded")
CACHE_DIR = Path("eval/llm_cache")
TASKS = OUT / "tasks.jsonl"
REPOS_JSON = OUT / "repos.json"
RESULT_MD = "rq4_repair.md"
DEFAULT_MODELS = ("openai/gpt-oss-120b", "openai/gpt-oss-20b")
RANDOM_SEEDS = tuple(range(20))


def load_tasks() -> list[dict]:
    return [json.loads(ln) for ln in TASKS.read_text(encoding="utf-8").splitlines() if ln.strip()]


def subset(tasks: list[dict], n: int, seed: int = 0) -> list[dict]:
    """Deterministic operator-stratified subset: round-robin over operators, shuffled within each."""
    rng = random.Random(seed)
    by_op: dict[str, list[dict]] = defaultdict(list)
    for t in sorted(tasks, key=lambda t: t["task_id"]):
        by_op[t["operator"]].append(t)
    for op in by_op:
        rng.shuffle(by_op[op])
    out: list[dict] = []
    ops = sorted(by_op)
    while len(out) < min(n, len(tasks)):
        for op in ops:
            if by_op[op] and len(out) < n:
                out.append(by_op[op].pop())
    return sorted(out, key=lambda t: t["task_id"])


def test_file_of(test_id: str, files: set[str]) -> str | None:
    """Map a JUnit `classname::name` id to its test file by the longest dotted prefix that is a file."""
    cls = test_id.split("::")[0]
    parts = cls.split(".")
    for k in range(len(parts), 0, -1):
        cand = "/".join(parts[:k]) + ".py"
        if cand in files:
            return cand
    return None


def detection(repo: Path, task: dict, files: list[str]) -> dict:
    """First failing test file's position under E1 order, alphabetical order, and random order."""
    fileset = set(files)
    failing = {test_file_of(t["test_id"], fileset) for t in task["failing_tests"]} - {None}
    cands = sorted(f for f in files if is_conventional_test_file(f))
    if not failing or not cands:
        return {}
    changed, n_lines = diff_stats(task["pr_diff"])
    e1 = rank_tests(repo, changed, n_lines, explain_top=0)
    out = {"n_files": len(cands)}
    out["alpha"] = min(i for i, f in enumerate(cands, 1) if f in failing)
    if e1:
        order = [r.test_file for r in e1]
        out["e1"] = min(i for i, f in enumerate(order, 1) if f in failing)
    rnd = []
    for s in RANDOM_SEEDS:
        perm = cands[:]
        random.Random(f"{task['task_id']}-{s}").shuffle(perm)
        rnd.append(min(i for i, f in enumerate(perm, 1) if f in failing))
    out["random"] = float(np.mean(rnd))
    return out


def e1_priority(repo: Path, changed: list[str], n_lines: int):
    """`file -> priority` for R2 ties: best E1 score of a test file whose name pairs with the source file."""
    ranked = rank_tests(repo, changed, n_lines, explain_top=0)
    if not ranked:
        return lambda f: 0.0
    stem_scores: dict[str, float] = {}
    for r in ranked:
        stem = Path(r.test_file).stem.replace("test_", "").replace("_test", "")
        stem_scores[stem] = max(stem_scores.get(stem, float("-inf")), r.score)
    return lambda f: stem_scores.get(Path(f).stem, 0.0)


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", "", s)


def run_task(task: dict, llm, arms: tuple[str, ...], pins: dict, run_llm: bool) -> dict:
    """Evaluate one task: retrieval and detection always, repair arms when `run_llm`."""
    slug = task["repo"]
    repo = SEEDED / "repos" / slug
    py = SEEDED / "venvs" / slug / "bin" / "python"
    if not repo.exists() or not py.exists():
        raise SystemExit(f"{repo} or its venv is missing: run `make seeded` first (needs the network once)")
    src_dirs = pins[slug]["src_dirs"]
    rec: dict = {"task_id": task["task_id"], "repo": slug, "operator": task["operator"]}
    with head_state(repo, task["pr_diff"]):
        files = tracked_files(repo)
        srcs = source_files(repo, {"src_dirs": src_dirs})
        changed, n_lines = diff_stats(task["pr_diff"])
        report = FailureReport(failing=task["failing_tests"], pr_diff=task["pr_diff"], triage="mine",
                               changed_files=[c for c in changed])
        tie = e1_priority(repo, changed, n_lines)
        rec["detection"] = detection(repo, task, files)
        for arm in ("R1", "R2"):
            ch = select_chunks(arm, repo, srcs, report, tie if arm == "R2" else None)
            rec[f"retrieval_{arm}"] = {
                "hit": any(c.file == task["gt_file"] and c.qualname == task["gt_function"] for c in ch),
                "file_hit": any(c.file == task["gt_file"] for c in ch),
                "distractor_chunks": sum(1 for c in ch if c.file in task["distractor_files"]), "n": len(ch)}
        if not run_llm:
            return rec
        preexisting = set(task["preexisting_failures"])
        targets = [t["test_id"] for t in task["failing_tests"]]
        head_funcs = {(c.file, c.qualname): c for c in index_functions(repo, [task["gt_file"]])}
        gt_fn = head_funcs.get((task["gt_file"], task["gt_function"]))
        head_text = (repo / task["gt_file"]).read_text(encoding="utf-8")
        base_text = head_text  # replaced below with the pre-mutation text
        import subprocess
        base_text = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{task['gt_file']}"], capture_output=True,
                                   text=True, check=True).stdout
        for arm in arms:
            verdicts: list = []
            validate = make_validator(repo, py, preexisting, targets, on_verdict=verdicts.append)
            t0 = time.time()
            res = RepairAgent(llm, arm).run(repo, srcs, report, validate, tie if arm in ("R2", "R3") else None)
            wall = time.time() - t0
            last = next((a for a in reversed(res.attempts) if a.applied), None)
            edited_file = edited_fn = restore = False
            distractor_patch = False
            if last is not None:
                edited_file = task["gt_file"] in last.files
                distractor_patch = any(p in task["distractor_files"] for p in last.files)
                if edited_file and gt_fn is not None:
                    new_lines = last.files[task["gt_file"]].splitlines()
                    old_lines = head_text.splitlines()
                    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
                    touched = [i + 1 for tag, i1, i2, _, _ in sm.get_opcodes() if tag != "equal"
                               for i in range(i1, max(i2, i1 + 1))]
                    edited_fn = any(gt_fn.start <= i <= gt_fn.end for i in touched)
                    restore = norm_ws(last.files[task["gt_file"]]) == norm_ws(base_text)
            usage = [a.usage or {} for a in res.attempts]
            rec[arm] = {
                "action": res.action, "accepted": res.accepted, "attempts": len(res.attempts),
                "applied": any(a.applied for a in res.attempts),
                "overfit": (not res.accepted) and bool(verdicts) and verdicts[-1].overfit,
                "edited_gt_file": edited_file, "edited_gt_function": edited_fn, "exact_restore": bool(res.accepted and restore),
                "patch_in_distractor": distractor_patch,
                "prompt_tokens": sum(int(u.get("prompt_tokens", 0)) for u in usage),
                "completion_tokens": sum(int(u.get("completion_tokens", 0)) for u in usage),
                "total_tokens": sum(int(u.get("total_tokens", 0)) for u in usage),
                "wall_s": round(wall, 2)}
    return rec


# ---- report --------------------------------------------------------------------------------------
def pct(n: int, d: int) -> str:
    return paper_md.rate(n, d)


def ci(vals: list[int]) -> str:
    if not vals:
        return "n/a"
    lo, hi = S.bootstrap_ci([float(v) for v in vals], n_boot=5000, seed=0)
    return f"[{lo:.2f}, {hi:.2f}]"


def write_report(all_recs: list[dict], per_model: dict[str, list[dict]], quota_note: dict[str, str]) -> None:
    n = len(all_recs)
    text = paper_md.header("RQ4 / E3: change-aware repair on BR-Seeded", "analysis/rq4_repair.py",
                           "Produced by `make repair-eval` from cached LLM responses under D-58. It is NOT part of "
                           "`make tables`, and its repair numbers depend on the recorded model replies "
                           "(`eval/llm_cache/`). Detection and retrieval need no model.")
    text += ("\nBR-Seeded: one mutation operator applied to a function covered by the suite (so at least one test "
             "fails), plus 2-3 harmless distractor edits in other files; the diff is the 'PR'. A patch is accepted "
             "only if the FULL suite (minus tests already failing at the base) passes. Seeded bugs are simpler than "
             "real ones; this measures what retrieval and change-awareness add, not absolute repair ability.\n")
    by_repo = defaultdict(int)
    for r in all_recs:
        by_repo[r["repo"]] += 1
    text += f"\n## Tasks\n\n{n} tasks: " + ", ".join(f"{k} {v}" for k, v in sorted(by_repo.items())) + ".\n"

    # detection
    det = [r["detection"] for r in all_recs if r.get("detection")]
    e1 = [d for d in det if "e1" in d]
    text += "\n## Detection (no model, all tasks with a resolvable failing test file)\n\n"
    if e1:
        text += paper_md.table(
            ["order", "tasks", "mean position of the first failing test file", "mean share of test files run before the first failure"],
            [["E1 model", len(e1), f"{np.mean([d['e1'] for d in e1]):.2f}",
              f"{np.mean([d['e1'] / d['n_files'] for d in e1]):.3f}"],
             ["alphabetical (B0, retest-all)", len(e1), f"{np.mean([d['alpha'] for d in e1]):.2f}",
              f"{np.mean([d['alpha'] / d['n_files'] for d in e1]):.3f}"],
             ["random (mean of 20 seeds)", len(e1), f"{np.mean([d['random'] for d in e1]):.2f}",
              f"{np.mean([d['random'] / d['n_files'] for d in e1]):.3f}"]])
        text += ("\nThe E1 model was trained on BR-Bench (Java-heavy GitHub Actions failures, history features); on these "
                 "repos there is no failure history, so only proximity and change features are informative.\n")
    else:
        text += "E1 model unavailable or no failing test file resolved: detection not computed.\n"

    # retrieval
    text += "\n## Retrieval hit rate (no model, all tasks)\n\n"
    rows = []
    for arm in ("R1", "R2"):
        k = f"retrieval_{arm}"
        h = sum(r[k]["hit"] for r in all_recs)
        f_ = sum(r[k]["file_hit"] for r in all_recs)
        d = sum(r[k]["distractor_chunks"] for r in all_recs)
        c = sum(r[k]["n"] for r in all_recs)
        rows.append([arm + (" log-only (BM25 over all functions)" if arm == "R1" else " change-aware (functions touched by the diff)"),
                     pct(h, n), pct(f_, n), pct(d, c)])
    text += paper_md.table(["arm", "seeded function among the <= 3 chunks", "seeded file among them",
                            "chunks that sit in a distractor file"], rows)
    b = sum(1 for r in all_recs if r["retrieval_R2"]["hit"] and not r["retrieval_R1"]["hit"])
    c_ = sum(1 for r in all_recs if r["retrieval_R1"]["hit"] and not r["retrieval_R2"]["hit"])
    if b + c_:
        from scipy.stats import binomtest
        text += (f"\nPaired, R2 hits where R1 misses: {b}; R1 hits where R2 misses: {c_}; "
                 f"exact McNemar p = {binomtest(min(b, c_), b + c_, 0.5).pvalue:.4g}.\n")

    # repair, per model
    for model, recs in per_model.items():
        m = len(recs)
        text += f"\n## Repair: {model} (n = {m} tasks, the same subset for every arm and model)\n\n"
        if quota_note.get(model):
            text += f"**{quota_note[model]}**\n\n"
        if not recs:
            text += "No repair results for this model.\n"
            continue
        tab = []
        for arm in ARMS:
            xs = [r[arm] for r in recs if arm in r]
            if not xs:
                continue
            acc = [int(x["accepted"]) for x in xs]
            tab.append([arm, len(xs), pct(sum(acc), len(xs)), ci(acc),
                        pct(sum(x["edited_gt_file"] for x in xs), len(xs)),
                        pct(sum(x["edited_gt_function"] for x in xs), len(xs)),
                        pct(sum(x["exact_restore"] for x in xs), len(xs)),
                        sum(x["overfit"] for x in xs), pct(sum(x["patch_in_distractor"] for x in xs), len(xs)),
                        f"{np.mean([x['total_tokens'] for x in xs]):.0f}", f"{np.mean([x['attempts'] for x in xs]):.2f}",
                        f"{np.mean([x['wall_s'] for x in xs]):.1f}"])
        text += paper_md.table(
            ["arm", "n", "plausible fix (full suite green)", "bootstrap 95% CI", "edited seeded file",
             "edited seeded function", "exact restore", "overfit (target tests pass, suite fails)",
             "patch landed in a distractor file", "tokens / task", "model calls / task", "wall s / task"], tab)
        text += ("\nCost: USD 0 on the Groq free tier; tokens are the resource that is spent. R0 makes no model call. "
                 "`wall s` for cached calls is the measured wall time of the validation run only.\n")
        both = [r for r in recs if "R1" in r and "R2" in r]
        if both:
            b2 = sum(1 for r in both if r["R2"]["accepted"] and not r["R1"]["accepted"])
            c2 = sum(1 for r in both if r["R1"]["accepted"] and not r["R2"]["accepted"])
            from scipy.stats import binomtest
            p = binomtest(min(b2, c2), b2 + c2, 0.5).pvalue if b2 + c2 else 1.0
            text += (f"\nPaired R2 vs R1 on plausible fix: R2 only {b2}, R1 only {c2}, exact McNemar p = {p:.4g} "
                     f"(n = {len(both)}).\n")
        for label, key in (("operator", "operator"), ("repo", "repo")):
            groups: dict[str, list] = defaultdict(list)
            for r in recs:
                groups[r[key]].append(r)
            rows = []
            for g in sorted(groups):
                cells = [g, len(groups[g])]
                for arm in ("R1", "R2", "R3"):
                    xs = [r[arm]["accepted"] for r in groups[g] if arm in r]
                    cells.append(f"{sum(xs)}/{len(xs)}" if xs else "n/a")
                rows.append(cells)
            text += f"\n### By {label} (plausible fixes)\n\n" + paper_md.table([label, "n", "R1", "R2", "R3"], rows)
    paper_md.write(RESULT_MD, text)


def cache_models() -> list[str]:
    """Models that have an E3 cache file (slug -> original name via the first record)."""
    out = []
    for p in sorted(CACHE_DIR.glob("e3_*.jsonl")):
        first = p.read_text(encoding="utf-8").splitlines()[:1]
        if first:
            out.append(json.loads(first[0])["request"]["model"])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["run", "eval"])
    ap.add_argument("--model", default=os.environ.get("MODEL") or os.environ.get("BR_AGENT_MODEL") or DEFAULT_MODELS[0])
    args = ap.parse_args(argv)
    tasks = load_tasks()
    pins = json.loads(REPOS_JSON.read_text())
    n_sub = int(os.environ.get("BR_E3_TASKS") or 20)
    sub = subset(tasks, n_sub)
    quota_note: dict[str, str] = {}

    if args.mode == "run":
        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            print("repair arms not run (no API key): set GROQ_API_KEY (`uv run --env-file .env ...`)", file=sys.stderr)
            return 0
        cache = LLMCache(CACHE_DIR / f"e3_{model_slug(args.model)}.jsonl")
        llm = GroqLLM(api_key=key, model=args.model, cache=cache)
        # estimate before spending anything: R1 + R2 prompts per task, plus R3's two worst-case retries
        est = 0
        for t in sub:
            est += 2 * (GroqLLM.estimate_tokens("x" * 700, "x" * 9000, 1500)) + 2 * GroqLLM.estimate_tokens("x" * 700, "x" * 10000, 1500)
        used, _ = llm._day_total()
        remaining = llm.tpd - used
        print(f"{args.model}: {len(sub)} tasks, worst-case estimate {est:,} tokens, {max(remaining, 0):,} left today "
              f"(TPD {llm.tpd:,})", flush=True)
        done: list[dict] = []
        try:
            for t in sub:
                done.append(run_task(t, llm, ("R1", "R2", "R3"), pins, True))
                print(f"  {t['task_id']}: " + ", ".join(f"{a}={'ok' if done[-1][a]['accepted'] else 'no'}" for a in ("R1", "R2", "R3")),
                      flush=True)
        except DailyQuotaReached as exc:
            print(f"{exc}: {len(done)} of {len(sub)} tasks done; cached calls are kept, re-run to resume.")
            quota_note[args.model] = f"Stopped at the daily quota: {len(done)} of {len(sub)} tasks done."
        print(f"cache: {cache.path} ({len(cache)} records)")
        return 0

    # eval: replay only, no network
    os.environ["BR_LLM_REPLAY"] = "1"
    os.environ["BR_OFFLINE"] = "1"
    base = [run_task(t, None, (), pins, False) for t in tasks]
    per_model: dict[str, list[dict]] = {}
    models = cache_models()
    if not models:
        quota_note["(none)"] = "repair arms not run (no cached model responses)"
    for model in models:
        cache = LLMCache(CACHE_DIR / f"e3_{model_slug(model)}.jsonl", replay=True)
        llm = GroqLLM(api_key="replay", model=model, cache=cache, ledger=Path(os.devnull))
        recs = []
        try:
            for t in sub:
                recs.append(run_task(t, llm, ("R0", "R1", "R2", "R3"), pins, True))
        except CacheMiss as exc:
            quota_note[model] = f"Cache incomplete ({exc}); {len(recs)} of {len(sub)} tasks replayed."
        per_model[model] = recs
    if not models:
        per_model["(no model run)"] = []
    write_report(base, per_model, quota_note)
    print(f"wrote paper/generated/{RESULT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
