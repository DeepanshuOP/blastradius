"""E1 / RQ2: can a learned ranker predict WHICH test files a change breaks, better than the proxies?

Offline, deterministic, no network, no LLM. Reads `data/processed/e1_features.parquet`
(`analysis/build_e1_features.py`). Splits are D-57 (chronological 60/20/20 by
`run_started_at`; never random) plus leave-one-repo-out.

Methods on the test split: B0-B7 (`src/eval/baselines.py`) and `ours`, a LightGBM
lambdarank over all feature families. Hyperparameters are tuned on the validation
split only; the final model is refit on train+validation with the chosen
configuration and the number of rounds early stopping found. Seeds 0-4.

Writes `paper/generated/rq2_predictor.md`, `rq2_ablation.md`, `rq2_features.md`,
`data/processed/e1_scores.parquet` (test split; B1 is seed 0 only) and
`data/processed/rq2_results.json` (read by `analysis/rq2_figures.py`).
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import paper_md
from src.eval import baselines as B
from src.eval import metrics as M
from src.eval import stats as S
from src.features.test_features import FAMILIES, FEATURE_COLS
from src.models import e1_ranker as R

FEATURES = Path("data/processed/e1_features.parquet")
SCORES = Path("data/processed/e1_scores.parquet")
RESULTS = Path("data/processed/rq2_results.json")
MODEL_PATH = Path("models/e1_lgbm_v1.txt")
SEEDS = (0, 1, 2, 3, 4)
EXPECTED_INSTANCES, EXPECTED_SPLIT = 734, {"train": 440, "val": 146, "test": 148}
FRACTIONS = (0.2, 0.4, 0.6, 0.8, 1.0)
CURVE_FRACS = (0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0)
GATE_DELTA = 0.147
METRIC_COLS = ["r1", "r5", "r10", "r10pct", "r20pct", "ap", "rr", "apfd", "first", "frac_full"]
METRIC_LABELS = {"r1": "Recall@1", "r5": "Recall@5", "r10": "Recall@10", "r10pct": "Recall@10%",
                 "r20pct": "Recall@20%", "ap": "MAP", "rr": "MRR", "apfd": "APFD",
                 "first": "first-fail pos.", "frac_full": "suite frac. for full recall"}


class Frame:
    """The feature table with per-instance row indices, so a method is just a score vector."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.files = df["test_file"].to_numpy(dtype=object)
        self.label = df["label"].to_numpy()
        self.idx = {k: np.asarray(v) for k, v in df.groupby(["repo", "run_id"], sort=False).indices.items()}
        self.order = list(self.idx)  # chronological: the table is written in (run_started_at, run_id) order
        self.split = {k: df["split"].iat[v[0]] for k, v in self.idx.items()}

    def keys(self, split: str | None = None, repos: set[str] | None = None) -> list[tuple]:
        return [k for k in self.order if (split is None or self.split[k] == split)
                and (repos is None or k[0] in repos)]


def instance_metrics(files: np.ndarray, label: np.ndarray, scores: np.ndarray) -> dict:
    """All E1 metrics of one instance for one score vector (ties by path: rows are path-sorted)."""
    order = np.argsort(-scores, kind="stable")
    ranked = files[order].tolist()
    gt = set(files[label == 1].tolist())
    first = M.first_fail_position(ranked, gt)
    ff = M.suite_fraction_for_full_recall(ranked, gt)
    return {"r1": M.recall_at_k(ranked, gt, 1), "r5": M.recall_at_k(ranked, gt, 5),
            "r10": M.recall_at_k(ranked, gt, 10), "r10pct": M.recall_at_fraction(ranked, gt, 0.10),
            "r20pct": M.recall_at_fraction(ranked, gt, 0.20), "ap": M.average_precision(ranked, gt),
            "rr": M.reciprocal_rank(ranked, gt), "apfd": M.apfd(ranked, gt),
            "first": float(first) if first is not None else float("nan"),
            "frac_full": float(ff) if ff is not None else float("nan"),
            "hits10": len(set(ranked[:10]) & gt), "n_gt": len(gt), "n_cand": len(ranked)}


def evaluate(fr: Frame, keys: list[tuple], scores: np.ndarray) -> pd.DataFrame:
    """Per-instance metrics for the given instances; `scores` is aligned with `fr.df` rows."""
    rows = []
    for k in keys:
        ix = fr.idx[k]
        rows.append({"repo": k[0], "run_id": k[1], **instance_metrics(fr.files[ix], fr.label[ix], scores[ix])})
    return pd.DataFrame(rows)


def baseline_scores(fr: Frame, changed: dict, which: str, seed: int = 0) -> np.ndarray:
    """Full-length score vector of a rule baseline."""
    out = np.zeros(len(fr.df))
    for k, ix in fr.idx.items():
        g = fr.df.iloc[ix]
        if which == "B0":
            s = B.score_b0(g)
        elif which == "B1":
            s = B.score_b1(g, seed, k[1])
        elif which == "B2":
            s = B.score_b2(g)
        elif which == "B3":
            s = B.score_b3(g)
        elif which == "B4":
            s = B.score_b4(g)
        elif which == "B5":
            s = B.score_b5(g, changed.get(k, []))
        else:
            raise ValueError(which)
        out[ix] = s
    return out


def tune(df: pd.DataFrame, cols: list[str]) -> tuple[dict, int, list[dict]]:
    """Grid search on validation NDCG@10 (seed 0); returns (best params, best rounds, all trials)."""
    trials = []
    for p in R.grid_params():
        b = R.train(df, cols, 0, p)
        trials.append({"params": p, "val_ndcg10": float(b.best_score["val"]["ndcg@10"]),
                       "rounds": int(b.best_iteration)})
    best = max(trials, key=lambda t: (t["val_ndcg10"], -t["rounds"]))
    return best["params"], max(best["rounds"], 1), trials


def fit_final(df: pd.DataFrame, cols: list[str], params: dict, rounds: int, seed: int):
    """Refit on train+validation with the chosen configuration and round count."""
    return R.train(df, cols, seed, params, fit_splits=("train", "val"), valid_split=None, n_rounds=rounds)


def mean_over(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Average per-instance metrics across seeds (rows aligned by construction)."""
    out = frames[0].copy()
    for c in METRIC_COLS + ["hits10"]:
        out[c] = np.mean([f[c].to_numpy() for f in frames], axis=0)
    return out


def row_for(name: str, ev: pd.DataFrame, per_seed: list[pd.DataFrame] | None = None) -> list:
    """One result-table row: means (macro) plus micro Recall@10 and, for seeded methods, the seed std."""
    cells = [name, len(ev)]
    for c in METRIC_COLS:
        cell = f"{ev[c].mean():.3f}"
        if per_seed and len(per_seed) > 1 and c in ("r10", "ap"):
            cell += f" ± {np.std([f[c].mean() for f in per_seed]):.3f}"
        cells.append(cell)
    cells.append(paper_md.rate(int(round(ev["hits10"].sum())), int(ev["n_gt"].sum())))
    return cells


def stratum_of(n_files: int) -> str:
    return "1" if n_files == 1 else "2-5" if n_files <= 5 else ">5"


def main() -> int:
    df = pd.read_parquet(FEATURES)
    fr = Frame(df)
    counts = {s: sum(1 for k in fr.order if fr.split[k] == s) for s in ("train", "val", "test")}
    assert len(fr.order) == EXPECTED_INSTANCES, f"HARD STOP 1: {len(fr.order)} instances, expected {EXPECTED_INSTANCES}"
    assert counts == EXPECTED_SPLIT, f"split drifted: {counts}"
    print(f"instances {len(fr.order)}, split {counts}")

    # changed files and language per instance (RQ1's own loader: same ground truth, same changesets)
    from analysis.build_e1_features import build_contexts
    from analysis.rq1_divergence import ground_truth, load_data
    from src.eval.baselines import reproduce_rq1
    from src.features.context import BrBenchHistory

    data = load_data()
    gt = ground_truth(data)
    ctx_pairs = build_contexts(data, gt)
    changed = {c.instance_key: list(c.changed_files) for c, _ in ctx_pairs}
    language = {c.instance_key: data.language_of.get(c.instance_key[1]) for c, _ in ctx_pairs}
    repro = reproduce_rq1(data, {c.instance_key: (c, s) for c, s in ctx_pairs}, BrBenchHistory(data), gt, k=10)
    print("RQ1 reproduction (k=10, proxy-fires subset):", repro)

    test_keys = fr.keys("test")
    all_keys = fr.order

    # ---- rule baselines ------------------------------------------------------------------
    scores_all: dict[str, np.ndarray] = {w: baseline_scores(fr, changed, w) for w in ("B0", "B2", "B3", "B4", "B5")}
    b1_runs = [baseline_scores(fr, changed, "B1", s) for s in B.RANDOM_SEEDS]
    scores_all["B1"] = b1_runs[0]

    # ---- learned models: B6, B7, ours ----------------------------------------------------
    learned = {"B6": B.B6_COLS, "B7": B.B7_COLS, "ours": FEATURE_COLS}
    chosen: dict[str, dict] = {}
    seed_scores: dict[str, list[np.ndarray]] = {}
    for name, cols in learned.items():
        params, rounds, trials = tune(df, cols)
        chosen[name] = {"params": params, "rounds": rounds, "trials": trials, "cols": cols}
        seed_scores[name] = [R.predict(fit_final(df, cols, params, rounds, s), df, cols) for s in SEEDS]
        scores_all[name] = seed_scores[name][0]
        print(f"{name}: chosen {params}, rounds {rounds}, val NDCG@10 "
              f"{max(t['val_ndcg10'] for t in trials):.4f}")

    # ---- evaluation on the test split ----------------------------------------------------
    per_inst: dict[str, pd.DataFrame] = {}
    per_seed: dict[str, list[pd.DataFrame]] = {}
    for w in ("B0", "B2", "B3", "B4", "B5"):
        per_inst[w] = evaluate(fr, test_keys, scores_all[w])
    per_seed["B1"] = [evaluate(fr, test_keys, s) for s in b1_runs]
    per_inst["B1"] = mean_over(per_seed["B1"])
    for name in learned:
        per_seed[name] = [evaluate(fr, test_keys, s) for s in seed_scores[name]]
        per_inst[name] = mean_over(per_seed[name])

    method_names = {**B.BASELINE_NAMES, "ours": "BlastRadius ranker (all families)"}
    order_methods = ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "ours"]
    r10 = {m: per_inst[m]["r10"].to_numpy() for m in order_methods}
    baselines = [m for m in order_methods if m != "ours"]
    best_b = max(baselines, key=lambda m: (r10[m].mean(), m))
    # one Holm family over every test in this file: ours vs each baseline, plus the two learned baselines vs B4
    extra = [("B6", "B4"), ("B7", "B4")]
    pvals = [S.wilcoxon_p(r10["ours"], r10[m]) for m in baselines] + [S.wilcoxon_p(r10[a], r10[b]) for a, b in extra]
    adj_all = S.holm_adjust(pvals)
    adj = adj_all[:len(baselines)]
    stat_rows = []
    for m, p, a in zip(baselines, pvals, adj):
        d = S.cliffs_delta(r10["ours"], r10[m])
        stat_rows.append([f"ours vs {m} {method_names[m]}", f"{r10[m].mean():.3f}", f"{p:.4g}", f"{a:.4g}",
                          f"{d:+.3f}", S.cliffs_label(d)])
    learned_vs_hist = []
    for (a_, b_), p, ad in zip(extra, pvals[len(baselines):], adj_all[len(baselines):]):
        d = S.cliffs_delta(r10[a_], r10[b_])
        learned_vs_hist.append({"pair": f"{a_} vs {b_}", "p": p, "adj": ad, "delta": d})
        stat_rows.append([f"{a_} {method_names[a_]} vs {b_} {method_names[b_]}", f"{r10[b_].mean():.3f}", f"{p:.4g}",
                          f"{ad:.4g}", f"{d:+.3f}", S.cliffs_label(d)])
    i_best = baselines.index(best_b)
    d_best = S.cliffs_delta(r10["ours"], r10[best_b])
    beats = r10["ours"].mean() > r10[best_b].mean()
    met = beats and adj[i_best] < 0.05 and abs(d_best) >= GATE_DELTA
    lo, hi = S.bootstrap_ci(r10["ours"])
    verdict = (f"Gate 3 (ROADMAP §37.1) is {'MET' if met else 'NOT MET'}: on the {len(test_keys)} test instances the "
               f"ranker's Recall@10 is {r10['ours'].mean():.3f} (95% bootstrap CI [{lo:.3f}, {hi:.3f}]) against "
               f"{r10[best_b].mean():.3f} for the best baseline ({best_b} {method_names[best_b]}); "
               f"Holm-adjusted Wilcoxon p = {adj[i_best]:.4g}, Cliff's delta = {d_best:+.3f} "
               f"({S.cliffs_label(d_best)}). The criterion is: higher mean, adjusted p < 0.05 and |delta| >= {GATE_DELTA}.")
    print(verdict)

    main_rows = [row_for(f"{m} {method_names[m]}", per_inst[m], per_seed.get(m)) for m in order_methods]
    ci_rows = []
    for m in order_methods:
        a, b_ = S.bootstrap_ci(r10[m])
        ci_rows.append([f"{m} {method_names[m]}", f"{r10[m].mean():.3f}", f"[{a:.3f}, {b_:.3f}]"])

    # micro / macro recall
    cand = per_inst["ours"]["n_cand"]
    text = paper_md.header("RQ2 / E1: learned test-file ranker vs baselines", "analysis/rq2_predictor.py")
    text += ("\nTest-file level: a change is scored on how early the test FILES that really failed (strict "
             "ground truth bound to files) appear in the ranked candidate list. Split D-57 (chronological, "
             f"train {counts['train']} / validation {counts['val']} / test {counts['test']} instances). All "
             "numbers are macro means over test instances unless marked micro. `±` is the standard deviation "
             "over seeds 0-4 of the test mean (the seed drives `feature_fraction` sampling and the row sample "
             "LightGBM uses to build feature bins). B1 is the mean over 20 random seeds.\n")
    def size_row(split: str) -> list:
        ks = fr.keys(split)
        n = np.array([len(fr.idx[k]) for k in ks])
        pz = np.array([int(fr.label[fr.idx[k]].sum()) for k in ks])
        return [split, len(ks), f"{n.min()} / {np.median(n):g} / {n.max()}", f"{pz.min()} / {np.median(pz):g} / {pz.max()}",
                int(pz.sum())]

    text += "\n## Candidates and positives per instance\n\n" + paper_md.table(
        ["split", "instances", "candidates per instance (min / median / max)",
         "positives per instance (min / median / max)", "positive files in total"],
        [size_row("train"), size_row("val"), size_row("test")])
    by_repo_test: dict[str, int] = defaultdict(int)
    by_lang_test: dict[str, int] = defaultdict(int)
    for k in test_keys:
        by_repo_test[k[0]] += 1
        by_lang_test[language.get(k) or "unknown"] += 1
    only = (len(by_lang_test) == 1)
    text += ("\n## Test split composition\n\n"
             + paper_md.table(["repo", "test instances"], [[r, n] for r, n in sorted(by_repo_test.items(), key=lambda t: (-t[1], t[0]))])
             + "\n" + paper_md.table(["language", "test instances"], [[l, n] for l, n in sorted(by_lang_test.items())])
             + "\n" + (f"The chronological test split contains only {next(iter(by_lang_test))} instances "
                        f"({len(test_keys)} of {len(test_keys)})." if only else
                        "The chronological test split contains: " + ", ".join(f"{l} {n}" for l, n in sorted(by_lang_test.items())) + ".")
             + "\n")

    text += "\n## Main result (test split)\n\n" + paper_md.table(
        ["method", "n", *[METRIC_LABELS[c] for c in METRIC_COLS], "micro Recall@10 (hits/actual)"], main_rows)
    text += "\n## Recall@10 with bootstrap 95% CI (10,000 resamples, seed 0)\n\n" + paper_md.table(
        ["method", "mean Recall@10", "95% CI"], ci_rows)
    def ms(m: str, c: str) -> str:
        if m in per_seed and len(per_seed[m]) > 1:
            v = [f[c].mean() for f in per_seed[m]]
            return f"{np.mean(v):.3f} ± {np.std(v):.3f}"
        return f"{per_inst[m][c].mean():.3f} ± 0.000 (deterministic)"
    text += ("\n## Side by side: Recall@10 and MAP, mean ± std over seeds 0-4\n\n"
             f"B1 (random, mean over 20 seeds, std over those 20) is the floor; B4 has no randomness. Candidate test files per "
             f"test instance: median {np.median([len(fr.idx[k]) for k in test_keys]):g}, max {max(len(fr.idx[k]) for k in test_keys)}.\n\n"
             + paper_md.table(["method", "Recall@10", "MAP"],
                              [[f"{m} {method_names[m]}", ms(m, "r10"), ms(m, "ap")] for m in ("ours", "B7", "B6", "B4", "B1")]))
    text += (f"\n## Paired statistics (Recall@10, per test instance)\n\n"
             f"Wilcoxon signed-rank (two-sided, zero_method=zsplit). One Holm family of {len(pvals)} tests: ours vs each of the "
             f"{len(baselines)} baselines, plus B6 vs B4 and B7 vs B4. Cliff's delta is the first method minus the second; "
             "'second method mean' is the Recall@10 of the second method.\n\n"
             + paper_md.table(["comparison", "second method mean", "p", "Holm-adjusted p", "Cliff's delta", "magnitude"],
                              stat_rows))
    text += f"\n## Gate 3 verdict\n\n{verdict}\n"
    text += ("\n## Tuning (validation only)\n\n"
             + "\n".join(f"- {n}: `{json.dumps(c['params'], sort_keys=True)}`, {c['rounds']} rounds, best "
                         f"validation NDCG@10 {max(t['val_ndcg10'] for t in c['trials']):.4f} over "
                         f"{len(c['trials'])} grid points" for n, c in chosen.items()) + "\n")
    text += ("\n## Reproduction check\n\nRQ1 baselines recomputed from the E1 building blocks on the RQ1 subset "
             f"(k = 10; {repro['n']} instances, {repro['actual']:,} labels): co-change hits {repro['co_hits']}, "
             f"changed files {repro['changed_hits']}, failure history {repro['hist_hits']} "
             f"({repro['hist_hits_path_ties']} with this script's path tie-break). They equal "
             "`paper/generated/rq1.md`; `tests/test_e1_baselines.py` asserts it.\n")

    # ---- LORO ----------------------------------------------------------------------------
    n_per_repo = defaultdict(int)
    for k in all_keys:
        n_per_repo[k[0]] += 1
    loro_repos = sorted(r for r, n in n_per_repo.items() if n >= 20)
    p_best, rounds_best = chosen["ours"]["params"], chosen["ours"]["rounds"]
    loro_rows, loro_json = [], {}
    for repo in loro_repos:
        held = df["repo"].eq(repo)
        tmp = df.assign(split=np.where(held, "heldout", "train"))
        b = R.train(tmp, FEATURE_COLS, 0, p_best, fit_splits=("train",), valid_split=None, n_rounds=rounds_best)
        sc = R.predict(b, df, FEATURE_COLS)
        keys = [k for k in all_keys if k[0] == repo]
        e_o, e_4, e_5 = (evaluate(fr, keys, s) for s in (sc, scores_all["B4"], scores_all["B5"]))
        loro_rows.append([repo, len(keys), f"{e_o['r10'].mean():.3f}", f"{e_4['r10'].mean():.3f}",
                          f"{e_5['r10'].mean():.3f}"])
        loro_json[repo] = {"n": len(keys), "ours": float(e_o["r10"].mean()), "B4": float(e_4["r10"].mean()),
                           "B5": float(e_5["r10"].mean())}
    repo_lang: dict[str, str] = {}
    lang_votes: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for k in all_keys:
        lang_votes[k[0]][language.get(k) or "unknown"] += 1
    for r_, v_ in lang_votes.items():
        repo_lang[r_] = max(sorted(v_), key=lambda l: v_[l])
    wins = sum(1 for v in loro_json.values() if v["ours"] > max(v["B4"], v["B5"]))
    lang_tables = ""
    for lang in sorted(set(repo_lang.values())):
        rows_l = [r for r in loro_rows if repo_lang.get(r[0]) == lang]
        py_all = sorted((r_, n_per_repo[r_]) for r_ in repo_lang if repo_lang[r_] == lang)
        lang_tables += (f"\n### {lang}: held-out repos with >= 20 instances ({len(rows_l)} of {len(py_all)} {lang} repos)\n\n"
                        + (paper_md.table(["held-out repo", "instances", "ours Recall@10", "B4 Recall@10", "B5 Recall@10"], rows_l)
                           if rows_l else f"No {lang} repo has >= 20 instances.\n")
                        + f"\nAll {lang} repos and their instance counts: "
                        + ", ".join(f"{r_} {n_}" for r_, n_ in sorted(py_all, key=lambda t: (-t[1], t[0]))) + ".\n")
    text += ("\n## Leave-one-repo-out (repos with >= 20 instances)\n\nTrain on every other repo (all splits, "
             f"configuration and round count fixed from the chronological tuning: `{json.dumps(p_best, sort_keys=True)}`, "
             f"{rounds_best} rounds), test on all instances of the held-out repo. History features still look at "
             "the held-out repo's own past, strictly before each instance.\n\n"
             + paper_md.table(["held-out repo", "instances", "ours Recall@10", "B4 Recall@10", "B5 Recall@10"], loro_rows)
             + f"\nOurs beats both B4 and B5 on {wins} of {len(loro_repos)} held-out repos.\n"
             + "\n### By language\n" + lang_tables)
    paper_md.write("rq2_predictor.md", text)

    # ---- ablation, learning curve, stratified ---------------------------------------------
    abl_rows = []
    full_r10, full_ap = per_inst["ours"]["r10"].mean(), per_inst["ours"]["ap"].mean()
    abl_json = {}
    abl_std: dict[str, tuple[float, float]] = {}
    for fam, fcols in FAMILIES.items():
        if fam == "graph_":
            continue
        cols = [c for c in FEATURE_COLS if c not in fcols]
        evs = []
        for s in SEEDS:
            b = R.train(df, cols, s, p_best)
            evs.append(evaluate(fr, test_keys, R.predict(b, df, cols)))
        ev = mean_over(evs)
        sd = float(np.std([e_["r10"].mean() for e_ in evs]))
        abl_std[fam] = (float(ev["r10"].mean()), sd)
        abl_json[fam] = {"r10": float(ev["r10"].mean()), "ap": float(ev["ap"].mean())}
        abl_rows.append([f"without `{fam}`", len(cols), f"{ev['r10'].mean():.3f}",
                         f"{ev['r10'].mean() - full_r10:+.3f}", f"{ev['ap'].mean():.3f}",
                         f"{ev['ap'].mean() - full_ap:+.3f}"])
    # families alone (what each carries by itself)
    alone_rows = []
    for fam, fcols in FAMILIES.items():
        if fam == "graph_":
            continue
        evs = [evaluate(fr, test_keys, R.predict(R.train(df, fcols, s, p_best), df, fcols)) for s in SEEDS]
        ev = mean_over(evs)
        alone_rows.append([f"only `{fam}`", len(fcols), f"{ev['r10'].mean():.3f}", f"{ev['ap'].mean():.3f}"])

    train_keys = fr.keys("train")
    curve_rows, curve_json = [], {}
    for frac in FRACTIONS:
        keep = set(train_keys[len(train_keys) - max(1, int(round(frac * len(train_keys)))):])
        sub = df[(df["split"] != "train") | pd.Series(list(zip(df["repo"], df["run_id"]))).isin(keep).to_numpy()]
        evs = []
        for s in SEEDS:
            b = R.train(sub, FEATURE_COLS, s, p_best)
            evs.append(evaluate(fr, test_keys, R.predict(b, df, FEATURE_COLS)))
        ev = mean_over(evs)
        curve_rows.append([f"{int(frac * 100)}%", len(keep), f"{ev['r10'].mean():.3f}", f"{ev['ap'].mean():.3f}"])
        curve_json[str(frac)] = {"n": len(keep), "r10": float(ev["r10"].mean()), "ap": float(ev["ap"].mean())}

    strat_rows = []
    for label, keyfn in (("language", lambda k: language.get(k) or "unknown"),
                         ("change size (files)", lambda k: stratum_of(len(changed.get(k, []))))):
        groups: dict[str, list[tuple]] = defaultdict(list)
        for k in test_keys:
            groups[keyfn(k)].append(k)
        for g in sorted(groups):
            ks = groups[g]
            cells = [label, g, len(ks)]
            for m in ("ours", "B2", "B4", "B5"):
                ix = per_inst[m].set_index(["repo", "run_id"]).loc[ks]
                cells.append(f"{ix['r10'].mean():.3f}")
            strat_rows.append(cells)

    text = paper_md.header("RQ2 / E1: ablation, learning curve, strata", "analysis/rq2_predictor.py")
    text += ("\nTest split, macro mean over test instances and seeds 0-4. The chosen configuration "
             f"(`{json.dumps(p_best, sort_keys=True)}`) is reused unchanged; each variant keeps early stopping "
             f"on validation. Full model: Recall@10 {full_r10:.3f}, MAP {full_ap:.3f}.\n")
    text += "\n## Ablation: drop one feature family\n\n" + paper_md.table(
        ["variant", "features", "Recall@10", "Δ Recall@10", "MAP", "Δ MAP"], abl_rows)
    full_sd = float(np.std([f_["r10"].mean() for f_ in per_seed["ours"]]))
    text += ("\n## Ablation deltas against seed variability (test Recall@10)\n\n"
             f"Full model: {full_r10:.3f} ± {full_sd:.3f} (std over seeds 0-4). Each variant is retrained on seeds 0-4.\n\n"
             + paper_md.table(["removed family", "Recall@10 (mean over seeds)", "std over seeds", "delta vs full",
                               "full model std", "|delta| > both stds"],
                              [[f"`{f}`", f"{m_:.3f}", f"{sd_:.3f}", f"{m_ - full_r10:+.3f}", f"{full_sd:.3f}",
                                "yes" if abs(m_ - full_r10) > max(sd_, full_sd) else "no"]
                               for f, (m_, sd_) in abl_std.items()]))
    text += "\n## One family alone\n\n" + paper_md.table(["variant", "features", "Recall@10", "MAP"], alone_rows)
    text += ("\n## Learning curve\n\nTrain on the most recent X% of the training instances (validation and test "
             "unchanged).\n\n" + paper_md.table(["training share", "train instances", "Recall@10", "MAP"], curve_rows))
    text += ("\n## Stratified (test split, Recall@10)\n\n"
             + paper_md.table(["stratum type", "stratum", "n", "ours", "B2", "B4", "B5"], strat_rows))
    paper_md.write("rq2_ablation.md", text)

    # ---- SHAP importance -----------------------------------------------------------------
    final0 = fit_final(df, FEATURE_COLS, p_best, rounds_best, 0)
    test_df = df[df["split"] == "test"]
    contrib = R.explain(final0, test_df, FEATURE_COLS)[:, :-1]
    imp = np.abs(contrib).mean(axis=0)
    fam_of = {c: f for f, cs in FAMILIES.items() for c in cs}
    total = imp.sum() or 1.0
    feat_rows = [[c, fam_of[c], f"{v:.4f}", f"{v / total:.1%}"]
                 for c, v in sorted(zip(FEATURE_COLS, imp), key=lambda t: (-t[1], t[0]))]
    fam_imp = defaultdict(float)
    for c, v in zip(FEATURE_COLS, imp):
        fam_imp[fam_of[c]] += v
    fam_rows = [[f, f"{v:.4f}", f"{v / total:.1%}"] for f, v in sorted(fam_imp.items(), key=lambda t: -t[1])]
    text = paper_md.header("RQ2 / E1: SHAP feature importance", "analysis/rq2_predictor.py")
    text += (f"\nMean |SHAP| (LightGBM `pred_contrib=True`, raw ranking score units) of the final seed-0 model over "
             f"all {len(test_df):,} candidate rows of the {len(test_keys)} test instances.\n\n"
             "Caveat: `chg_*` and `cochg_n_files_with_partner` are identical on every candidate of an instance, so they "
             "can change a ranking only through interactions with candidate-level features; their SHAP share says "
             "how much the model uses them, not that they rank files by themselves (see the ablation).\n"
             "\n## By family\n\n" + paper_md.table(["family", "mean |SHAP| (sum)", "share"], fam_rows)
             + "\n## By feature\n\n" + paper_md.table(["feature", "family", "mean |SHAP|", "share"], feat_rows))
    paper_md.write("rq2_features.md", text)

    # ---- artefacts -----------------------------------------------------------------------
    R.save(final0, MODEL_PATH, {
        "seed": 0, "params": {**R.BASE_PARAMS, **p_best}, "rounds": rounds_best,
        "n_train_instances": counts["train"] + counts["val"], "n_val_instances_used_for_tuning": counts["val"],
        "n_test_instances": counts["test"], "trained_by_script": "analysis/rq2_predictor.py",
        "fit_on": "train+val", "train_date_range": [
            str(pd.to_datetime(df.loc[df["split"] != "test", "ts"].min(), unit="s", utc=True)),
            str(pd.to_datetime(df.loc[df["split"] != "test", "ts"].max(), unit="s", utc=True))],
        "d57_split": counts})
    rows = []
    for m in order_methods:
        seeds = SEEDS if m in ("B6", "B7", "ours") else (0,)
        for si, s in enumerate(seeds):
            sc = seed_scores[m][si] if m in learned else scores_all[m]
            for k in test_keys:
                ix = fr.idx[k]
                o = np.argsort(-sc[ix], kind="stable")
                rk = np.empty(len(ix), dtype=np.int32)
                rk[o] = np.arange(1, len(ix) + 1)
                rows.append(pd.DataFrame({"method": m, "seed": np.int32(s) if m in learned else pd.NA, "repo": k[0],
                                          "run_id": np.int64(k[1]), "test_file": fr.files[ix], "score": sc[ix],
                                          "rank": rk, "split": "test"}))
    scores_df = pd.concat(rows, ignore_index=True)
    scores_df["seed"] = scores_df["seed"].astype("Int32")
    scores_df.to_parquet(SCORES, index=False)

    curves = {}
    fracs = np.array(CURVE_FRACS)
    for m in order_methods:
        sc_list = b1_runs if m == "B1" else [scores_all[m]]
        ys = []
        for f in fracs:
            vals = []
            for sc in sc_list:
                for k in test_keys:
                    ix = fr.idx[k]
                    ranked = fr.files[ix][np.argsort(-sc[ix], kind="stable")].tolist()
                    vals.append(M.recall_at_fraction(ranked, set(fr.files[ix][fr.label[ix] == 1].tolist()), float(f)))
            ys.append(float(np.mean(vals)))
        curves[m] = ys
    RESULTS.write_text(json.dumps({
        "verdict": verdict, "gate3_met": bool(met), "counts": counts, "methods": method_names, "order": order_methods,
        "main": {m: {c: float(per_inst[m][c].mean()) for c in METRIC_COLS} for m in order_methods},
        "r10_ci": {m: S.bootstrap_ci(r10[m]) for m in order_methods}, "best_baseline": best_b,
        "ablation": abl_json, "curve_fracs": list(CURVE_FRACS), "recall_vs_suite": curves,
        "learning_curve": curve_json, "family_importance": {f: float(v / total) for f, v in fam_imp.items()},
        "loro": loro_json, "tuning": {n: {"params": c["params"], "rounds": c["rounds"]} for n, c in chosen.items()},
        "stat_rows": stat_rows, "learned_vs_history": learned_vs_hist}, indent=1, sort_keys=True), encoding="utf-8")
    print("wrote paper/generated/rq2_predictor.md, rq2_ablation.md, rq2_features.md,", SCORES, RESULTS, MODEL_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
