"""E3 / RQ4: does change-awareness help an LLM repair a failure that a change introduced?

    uv run --env-file .env python -m analysis.rq4_repair run  --model openai/gpt-oss-120b   (live, Groq free tier)
    uv run python -m analysis.rq4_repair eval                                              (replay, offline)
    uv run --extra ml python -m analysis.rq4_repair estimate --model ... [--variant hard]  (dry run, no key, no request)

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
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from analysis import paper_md
from src.agents.llm import BedrockLLM, CostCapReached, DailyQuotaReached, GroqLLM, NetworkUnavailable, bedrock_spend
from src.agents.llm_cache import CacheMiss, LLMCache, model_slug
from src.agents.repair import (ARMS, SYSTEM, FailureReport, RepairAgent, build_prompt, index_functions,
                               select_chunks)
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
THIRD_MODEL = "qwen/qwen3.8-27b"   # D-62: exploratory; a Groq preview model, which can be withdrawn at short notice
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
    """Map a JUnit `classname::name` id to its test file: the longest dotted run that is a tracked file.

    pytest may prefix the classname with directories above the repo (`data.seeded.repos.x.tests.test_a`), so
    leading components are skipped as needed.
    """
    parts = test_id.split("::")[0].split(".")
    for i in range(len(parts)):
        for k in range(len(parts), i, -1):
            cand = "/".join(parts[i:k]) + ".py"
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
    rec: dict = {"task_id": task["task_id"], "repo": slug, "operator": task["operator"],
                 "variant": task.get("variant", "standard")}
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
                "distractor_chunks": sum(1 for c in ch if c.file in task["distractor_files"]
                                         or (c.file, c.qualname) in {(d["file"], d["function"]) for d in task.get("hard_distractors", [])}),
                "n": len(ch)}
        if not run_llm:
            return rec
        preexisting = set(task["preexisting_failures"])
        targets = [t["test_id"] for t in task["failing_tests"]]
        head_funcs = {(c.file, c.qualname): c for c in index_functions(repo, [task["gt_file"]])}
        gt_fn = head_funcs.get((task["gt_file"], task["gt_function"]))
        head_text = (repo / task["gt_file"]).read_text(encoding="utf-8")
        # the file as it should look once the mutant line is put back: the head text with that line replaced by the
        # original (the hard variant keeps its no-op edits, so the base file is not the right reference)
        hl = head_text.splitlines()
        near = sorted((i for i, l in enumerate(hl) if l == task["mutated_snippet"]),
                      key=lambda i: abs(i - (task["gt_line"] - 1)))
        if near:
            hl[near[0]] = task["original_snippet"]
        base_text = "\n".join(hl)
        hard_fn = {(d["file"], d["function"]) for d in task.get("hard_distractors", [])}
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


def mcnemar_onesided(b: int, c: int) -> float:
    """Exact one-sided McNemar: P(X >= b), X ~ Binomial(b + c, 0.5); b = first arm only, c = second arm only."""
    from scipy.stats import binom

    n = b + c
    return 1.0 if n == 0 else float(binom.sf(b - 1, n, 0.5))


def mcnemar_twosided(b: int, c: int) -> float:
    from scipy.stats import binomtest

    return 1.0 if b + c == 0 else float(binomtest(min(b, c), b + c, 0.5).pvalue)


def paired(recs: list[dict], a: str, b: str) -> tuple[int, int]:
    """`(a only, b only)` plausible fixes over tasks that have both arms."""
    both = [r for r in recs if a in r and b in r]
    return (sum(1 for r in both if r[a]["accepted"] and not r[b]["accepted"]),
            sum(1 for r in both if r[b]["accepted"] and not r[a]["accepted"]))


def is_groq(model: str) -> bool:
    """Groq model ids are `org/model` (or a bare name such as `allam-2-7b`); Bedrock ids never contain `/`."""
    return "/" in model or model.startswith("allam")


def model_usage(model: str) -> tuple[int, float, int]:
    """`(tokens, usd, calls)` recorded in a model's cache file."""
    path = CACHE_DIR / f"e3_{model_slug(model)}.jsonl"
    tok, usd, n = 0, 0.0, 0
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            u = json.loads(ln).get("usage") or {}
            tok += int(u.get("total_tokens", 0) or (u.get("inputTokens", 0) + u.get("outputTokens", 0)))
            usd += float(u.get("usd") or 0.0)
            n += 1
    return tok, usd, n


def arm_table(recs: list[dict]) -> str:
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
                    f"{np.mean([x['total_tokens'] for x in xs]):.0f}", f"{np.mean([x['attempts'] for x in xs]):.2f}"])
    return paper_md.table(
        ["arm", "n", "plausible fix (full suite green)", "bootstrap 95% CI", "edited seeded file", "edited seeded function",
         "exact restore", "overfit (target tests pass, suite fails)", "patch landed in a distractor file",
         "tokens / task", "model calls / task"], tab)


def breakdowns(recs: list[dict]) -> str:
    out = ""
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
        out += f"\n#### By {label} (plausible fixes)\n\n" + paper_md.table([label, "n", "R1", "R2", "R3"], rows)
    return out


def retrieval_table(recs: list[dict], title: str) -> str:
    n = len(recs)
    rows = []
    for arm, label in (("R1", "R1 log-only (BM25 over all functions)"),
                       ("R2", "R2 change-aware (functions touched by the diff)")):
        k = f"retrieval_{arm}"
        rows.append([label, pct(sum(r[k]["hit"] for r in recs), n), pct(sum(r[k]["file_hit"] for r in recs), n),
                     pct(sum(r[k]["distractor_chunks"] for r in recs), sum(r[k]["n"] for r in recs))])
    b = sum(1 for r in recs if r["retrieval_R2"]["hit"] and not r["retrieval_R1"]["hit"])
    c = sum(1 for r in recs if r["retrieval_R1"]["hit"] and not r["retrieval_R2"]["hit"])
    txt = f"\n### {title}\n\n" + paper_md.table(
        ["arm", "seeded function among the <= 3 chunks", "seeded file among them", "chunks that sit in a distractor"], rows)
    txt += (f"\nPaired, R2 hits where R1 misses: {b}; R1 hits where R2 misses: {c}; "
            f"exact McNemar (two-sided) p = {mcnemar_twosided(b, c):.4g} (n = {n}).\n")
    return txt


CAVEAT = ("On the standard variant the seeded edit lies inside the diff that R2 searches, so part of R2's retrieval "
          "advantage is by construction; the hard variant, which places 4-6 no-op edits inside functions the failing "
          "tests execute, measures how much remains.")


def write_report(base: dict[str, list[dict]], runs: dict[tuple[str, str], list[dict]], pilot_ids: set[str],
                 notes: dict[tuple[str, str], str], primary: str) -> None:
    std, hard = base["standard"], base["hard"]
    text = paper_md.header("RQ4 / E3: change-aware repair on BR-Seeded", "analysis/rq4_repair.py",
                           "Produced by `make repair-eval` from cached LLM responses under D-58 / D-60. It is NOT part of "
                           "`make tables`, and its repair numbers depend on the recorded model replies "
                           "(`eval/llm_cache/`). Detection and retrieval need no model. Analysis plan: "
                           "`docs/phase/033-e3-preregistration.md`.")
    text += ("\nBR-Seeded: one mutation operator applied to a function covered by the suite (so at least one test fails), "
             "plus 2-3 harmless distractor edits in other files; the diff is the 'PR'. The **hard** variant is the same 70 "
             "mutants with 4-6 additional no-op edits (a comment line or redundant parentheses) inside functions the failing "
             "tests execute. A patch is accepted only if the FULL suite (minus tests already failing at the base) passes. "
             "Seeded bugs are simpler than real ones; this measures what retrieval and change-awareness add, not absolute "
             "repair ability.\n")
    by_repo = defaultdict(int)
    for r in std:
        by_repo[r["repo"]] += 1
    nh = sorted(int(r.get("n_hard", 0)) for r in hard)
    text += (f"\n## Tasks\n\n{len(std)} tasks: " + ", ".join(f"{k} {v}" for k, v in sorted(by_repo.items()))
             + f". Hard variant: {len(hard)} tasks; added no-op edits per task min {nh[0] if nh else 0} / median "
             f"{nh[len(nh) // 2] if nh else 0} / max {nh[-1] if nh else 0}; {sum(1 for n in nh if n >= 4)} of {len(nh)} tasks "
             "kept at least 4.\n")

    det = [r["detection"] for r in std if r.get("detection")]
    e1 = [d for d in det if "e1" in d]
    text += "\n## Detection (no model, all tasks with a resolvable failing test file)\n\n"
    if e1:
        text += paper_md.table(
            ["order", "tasks", "mean position of the first failing test file", "mean share of test files run before the first failure"],
            [["E1 model", len(e1), f"{np.mean([d['e1'] for d in e1]):.2f}", f"{np.mean([d['e1'] / d['n_files'] for d in e1]):.3f}"],
             ["alphabetical (B0, retest-all)", len(e1), f"{np.mean([d['alpha'] for d in e1]):.2f}",
              f"{np.mean([d['alpha'] / d['n_files'] for d in e1]):.3f}"],
             ["random (mean of 20 seeds)", len(e1), f"{np.mean([d['random'] for d in e1]):.2f}",
              f"{np.mean([d['random'] / d['n_files'] for d in e1]):.3f}"]])
        text += ("\nOn the seeded Python repositories, which have no failure history, ordering tests with the BR-Bench model puts "
                 f"the first failing test file at mean position {np.mean([d['e1'] for d in e1]):.2f}, against "
                 f"{np.mean([d['alpha'] for d in e1]):.2f} for alphabetical order and {np.mean([d['random'] for d in e1]):.2f} for "
                 "random order.\n")
    else:
        text += "E1 model unavailable or no failing test file resolved: detection not computed.\n"

    text += "\n## Retrieval hit rate (no model, all tasks)\n\n" + CAVEAT + "\n"
    text += retrieval_table(std, "Standard variant")
    text += retrieval_table(hard, "Hard variant (same 70 mutants plus 4-6 no-op edits in executed functions)")

    # ---- confirmatory ---------------------------------------------------------------------------
    cells = sorted(runs, key=lambda k: (k[1] != "standard", k[0] != primary, k[0]))
    text += "\n## Confirmatory results (pre-registered, `docs/phase/033-e3-preregistration.md`)\n"
    tests: list[tuple[str, int, int, str]] = []   # (label, b, c, cell)
    prim = runs.get((primary, "standard"))
    text += "\n### Primary test\n\n"
    if prim:
        b, c = paired(prim, "R2", "R1")
        n = len([r for r in prim if "R1" in r and "R2" in r])
        pv = mcnemar_onesided(b, c)
        text += (f"Standard variant, {primary}, n = {n}: R2 plausible-fix rate "
                 f"{sum(r['R2']['accepted'] for r in prim)}/{len(prim)} vs R1 {sum(r['R1']['accepted'] for r in prim)}/{len(prim)}; "
                 f"R2 only {b}, R1 only {c}; exact McNemar one-sided p = {pv:.4g} (alpha = 0.05): "
                 + ("**R2 > R1 supported**." if pv < 0.05 else "**R2 > R1 not supported at alpha = 0.05**.")
                 + (f" ({notes[(primary, 'standard')]})" if (primary, "standard") in notes else "") + "\n")
    else:
        text += f"Not available: no complete standard-variant run of {primary}.\n"
    for (m, v), recs in sorted(runs.items(), key=lambda kv: (kv[0][1] != "standard", kv[0][0] != primary, kv[0][0])):
        if not recs:
            continue
        if not (m == primary and v == "standard"):
            b, c = paired(recs, "R2", "R1")
            tests.append((f"R2 > R1, {m}, {v}", b, c, f"{m}|{v}"))
        b, c = paired(recs, "R3", "R2")
        tests.append((f"R3 > R2, {m}, {v}", b, c, f"{m}|{v}"))
    if tests:
        adj = S.holm_adjust([mcnemar_onesided(b, c) for _, b, c, _ in tests])
        text += (f"\n### Secondary tests (one-sided exact McNemar, Holm family of {len(tests)})\n\n"
                 + paper_md.table(["test", "first only", "second only", "p (unadjusted)", "Holm-adjusted p"],
                                  [[lab, b, c, f"{mcnemar_onesided(b, c):.4g}", f"{a:.4g}"]
                                   for (lab, b, c, _), a in zip(tests, adj)]))
    ledger = bedrock_spend()
    for (m, v), recs in sorted(runs.items(), key=lambda kv: (kv[0][1] != "standard", kv[0][0] != primary, kv[0][0])):
        tok, usd, calls = model_usage(m)
        text += f"\n### {m}, {v} variant (n = {len(recs)} tasks)\n\n"
        if (m, v) in notes:
            text += f"**{notes[(m, v)]}**\n\n"
        if not recs:
            text += "No complete tasks.\n"
            continue
        text += arm_table(recs)
        text += breakdowns(recs)
    # ---- pilot ----------------------------------------------------------------------------------
    text += "\n## Pilot (n = 20, standard variant): not confirmatory\n\n"
    text += ("The 20-task operator-stratified subset run on 2026-10-10 before the pre-registration was written. Reported "
             "as a pilot; the 20 tasks are part of the 70 above and are not an independent sample.\n")
    for (m, v), recs in sorted(runs.items()):
        if v != "standard":
            continue
        sub = [r for r in recs if r["task_id"] in pilot_ids]
        if sub:
            b, c = paired(sub, "R2", "R1")
            text += (f"\n### {m} (pilot, n = {len(sub)})\n\n" + arm_table(sub)
                     + f"\nPaired R2 vs R1: R2 only {b}, R1 only {c}, exact McNemar two-sided p = {mcnemar_twosided(b, c):.4g}.\n")
    # ---- cost -----------------------------------------------------------------------------------
    rows = []
    for m in sorted({k[0] for k in runs}):
        tok, usd, calls = model_usage(m)
        rows.append([m, "Groq free tier" if is_groq(m) else "Amazon Bedrock", calls, f"{tok:,}",
                     "0.00" if is_groq(m) else f"{usd:.4f}"])
    text += ("\n## Cost\n\n" + paper_md.table(["model", "provider", "recorded calls", "tokens", "USD"], rows)
             + f"\nBedrock USD total in `eval/llm_cache/usage.jsonl`: **{ledger:.4f}** (project cap USD 45).\n"
             "Groq is the free tier (USD 0); the Bedrock figure is computed from the operator-set per-million-token prices.\n")
    paper_md.write(RESULT_MD, text)


def cache_models() -> list[str]:
    """Models that have an E3 cache file (original model name from the first record)."""
    out = []
    for p in sorted(CACHE_DIR.glob("e3_*.jsonl")):
        first = p.read_text(encoding="utf-8").splitlines()[:1]
        if first:
            out.append(json.loads(first[0])["request"]["model"])
    return out


def load_variant(variant: str) -> list[dict]:
    if variant == "hard":
        path = OUT / "tasks_hard.jsonl"
        recs = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return recs
    return load_tasks()


def make_llm(model: str, replay: bool):
    """The provider object for a cache file: Groq for gpt-oss models, Bedrock otherwise."""
    cache = LLMCache(CACHE_DIR / f"e3_{model_slug(model)}.jsonl", replay=replay)
    if replay:
        if is_groq(model):
            return GroqLLM(api_key="replay", model=model, cache=cache, ledger=Path(os.devnull))
        return BedrockLLM(api_key="replay", model=model, cache=cache, ledger=Path(os.devnull))
    if is_groq(model):
        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            raise SystemExit("repair arms not run (no API key): set GROQ_API_KEY (`uv run --env-file .env ...`)")
        return GroqLLM(api_key=key, model=model, cache=cache)
    key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
    if not key:
        raise SystemExit("repair arms not run (no AWS_BEARER_TOKEN_BEDROCK)")
    pi, po = os.environ.get("BR_PRICE_IN"), os.environ.get("BR_PRICE_OUT")
    return BedrockLLM(api_key=key, model=model, region=os.environ.get("BR_BEDROCK_REGION") or "ap-south-1", cache=cache,
                      price_in=float(pi) if pi else None, price_out=float(po) if po else None,
                      max_usd=float(os.environ.get("BR_BEDROCK_MAX_USD") or 10))


@dataclass
class Estimate:
    """Worst-case cost of the requests a run would still have to send (cache hits excluded)."""

    tasks: int = 0
    tasks_live: int = 0            # tasks with at least one first call (R1 or R2) not in the cache
    calls_cached: int = 0          # R1 / R2 first calls found in the cache
    calls_live: int = 0            # R1 / R2 first calls that would go to the API
    retries_cached: int = 0        # recorded R3 retries found for those R2 prompts
    tin: int = 0
    tout: int = 0
    usd: float | None = None
    live_tasks: list[str] = field(default_factory=list)


def estimate_run(tasks: list[dict], pins: dict, llm) -> Estimate:
    """Worst-case cost of the requests of R1 + R2 (+ R3's two retries) that are NOT in the cache, without any call.

    Prompts are built exactly as the agent builds them (retrieval needs no model) and looked up with the
    provider's own cache key, so recorded replies cost nothing and are not counted. A recorded R3 retry is found
    by its prompt prefix; whether a *cached* R2 reply still needs a retry depends on the suite verdict of its
    patch and is not estimated (the quota guard in `chat` still protects the day's budget).
    """
    est = Estimate(tasks=len(tasks))
    cache = getattr(llm, "cache", None)
    recorded = cache.user_messages() if cache is not None else []
    tail = "\n\nReply with SEARCH/REPLACE blocks only."
    for t in tasks:
        slug = t["repo"]
        repo = SEEDED / "repos" / slug
        live = False
        with head_state(repo, t["pr_diff"]):
            srcs = source_files(repo, {"src_dirs": pins[slug]["src_dirs"]})
            changed, n_lines = diff_stats(t["pr_diff"])
            rep = FailureReport(failing=t["failing_tests"], pr_diff=t["pr_diff"], triage="mine", changed_files=changed)
            tie = e1_priority(repo, changed, n_lines)
            for arm in ("R1", "R2"):
                ch = select_chunks(arm, repo, srcs, rep, tie if arm == "R2" else None)
                prompt = build_prompt(arm, rep, ch, repo)
                chars = len(SYSTEM) + len(prompt)
                if cache is not None and llm.request_key(SYSTEM, prompt, 1500) in cache:
                    est.calls_cached += 1
                    if arm == "R2":
                        head = prompt[:-len(tail)] if prompt.endswith(tail) else prompt
                        est.retries_cached += sum(1 for u in recorded if u.startswith(head) and u != prompt)
                    continue
                live = True
                est.calls_live += 1
                calls = 1 + (2 if arm == "R2" else 0)  # R3 shares R2's first call; its retries add up to two
                est.tin += int(chars / 3.5) * calls + (int(1000 / 3.5) * 2 if arm == "R2" else 0)
                est.tout += 1500 * calls
        if live:
            est.tasks_live += 1
            est.live_tasks.append(t["task_id"])
    if getattr(llm, "price_in", None) is not None and getattr(llm, "price_out", None) is not None:
        est.usd = est.tin * llm.price_in / 1e6 + est.tout * llm.price_out / 1e6
    return est


def describe(model: str, variant: str, est: Estimate, llm) -> str:
    """One status block: what is cached, what is left, tokens, and the days it needs at the daily cap."""
    total = est.tin + est.tout
    lines = [f"{model} [{variant}]: {est.tasks} tasks; first calls (R1+R2): {est.calls_cached} cached, {est.calls_live} to send "
             f"({est.tasks_live} tasks need at least one live call, {est.tasks - est.tasks_live} fully cached; "
             f"{est.retries_cached} recorded retries)",
             f"  uncached remainder, worst case: {est.tin:,} input + {est.tout:,} output = {total:,} tokens"]
    if isinstance(llm, GroqLLM):
        used, _ = llm._day_total()
        left = max(llm.tpd - used, 0)
        days = -(-total // llm.tpd) if llm.tpd else 0
        lines.append(f"  quota: {left:,} tokens left today by the client-side ledger (TPD {llm.tpd:,}); the remainder needs "
                     f"{days} day(s) at {llm.tpd:,} tokens/day (the first day may start with less)")
    if est.usd is not None:
        lines.append(f"  estimated USD {est.usd:.2f}, ledger USD {bedrock_spend():.2f}, cap USD {llm.max_usd:.2f}")
    return "\n".join(lines)


def estimator_llm(model: str):
    """A provider object with the real cache and ledger but no key, for dry runs (it can never reach the network)."""
    cache = LLMCache(CACHE_DIR / f"e3_{model_slug(model)}.jsonl")
    if is_groq(model):
        return GroqLLM(api_key="estimate-only", model=model, cache=cache)
    pi, po = os.environ.get("BR_PRICE_IN"), os.environ.get("BR_PRICE_OUT")
    return BedrockLLM(api_key="estimate-only", model=model, cache=cache, price_in=float(pi) if pi else None,
                      price_out=float(po) if po else None, max_usd=float(os.environ.get("BR_BEDROCK_MAX_USD") or 10))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["run", "eval", "estimate"])
    ap.add_argument("--model", default=os.environ.get("MODEL") or os.environ.get("BR_AGENT_MODEL") or DEFAULT_MODELS[0])
    ap.add_argument("--variant", choices=["standard", "hard"], default="standard")
    args = ap.parse_args(argv)
    pins = json.loads(REPOS_JSON.read_text())
    n_sub = int(os.environ.get("BR_E3_TASKS") or 20)
    pilot_ids = {t["task_id"] for t in subset(load_tasks(), 20)}

    if args.mode == "estimate":   # dry run: no key needed, no request can be sent
        sub = subset(load_variant(args.variant), n_sub)
        llm = estimator_llm(args.model)
        print(describe(args.model, args.variant, estimate_run(sub, pins, llm), llm), flush=True)
        return 0

    if args.mode == "run":
        tasks_all = load_variant(args.variant)
        sub = subset(tasks_all, n_sub)
        llm = make_llm(args.model, replay=False)
        est = estimate_run(sub, pins, llm)
        print(describe(args.model, args.variant, est, llm), flush=True)
        if isinstance(llm, BedrockLLM):
            llm.check_budget(est.usd or 0.0) if est.usd is not None else llm.estimate_usd("", "", 0)
        print("subset:", ", ".join(t["task_id"] for t in sub), flush=True)
        done = 0
        current = ""
        try:
            for t in sub:
                current = t["task_id"]
                rec = run_task(t, llm, ("R1", "R2", "R3"), pins, True)
                done += 1
                print(f"  {t['task_id']}: " + ", ".join(f"{a}={'ok' if rec[a]['accepted'] else 'no'}" for a in ("R1", "R2", "R3")),
                      flush=True)
        except (DailyQuotaReached, CostCapReached, NetworkUnavailable) as exc:
            print(f"{exc}: stopped at {current} (a request that was not in the cache, or the provider was unreachable); {done} of {len(sub)} tasks done; "
                  "cached calls are kept, re-run the same command to resume.")
        if isinstance(llm, BedrockLLM):
            print(f"Bedrock ledger total: USD {bedrock_spend():.4f} (cap USD {llm.max_usd:.2f})")
        print(f"cache: {llm.cache.path} ({len(llm.cache)} records)")
        return 0

    # eval: replay only, no network
    os.environ["BR_LLM_REPLAY"] = "1"
    os.environ["BR_OFFLINE"] = "1"
    base: dict[str, list[dict]] = {}
    tasks_by_variant: dict[str, list[dict]] = {}
    for v in ("standard", "hard"):
        try:
            tasks_by_variant[v] = load_variant(v)
        except FileNotFoundError:
            tasks_by_variant[v] = []
        base[v] = []
        for t in tasks_by_variant[v]:
            r = run_task(t, None, (), pins, False)
            r["n_hard"] = t.get("n_hard_distractors", 0)
            base[v].append(r)
    runs: dict[tuple[str, str], list[dict]] = {}
    notes: dict[tuple[str, str], str] = {}
    models = cache_models()
    primary = DEFAULT_MODELS[0]
    for model in models:
        llm = make_llm(model, replay=True)
        for v in ("standard", "hard"):
            tasks = tasks_by_variant[v]
            recs, missed = [], 0
            for t in tasks:
                try:
                    recs.append(run_task(t, llm, ("R0", "R1", "R2", "R3"), pins, True))
                except CacheMiss:
                    missed += 1
            if not recs and v == "hard":
                continue
            runs[(model, v)] = recs
            if missed:
                notes[(model, v)] = f"{len(recs)} of {len(tasks)} tasks done; {missed} not run (cache incomplete)"
    write_report(base, runs, pilot_ids, notes, primary)
    print(f"wrote paper/generated/{RESULT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
