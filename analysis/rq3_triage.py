"""E2 / RQ3: triage a failing test as `mine`, `inherited` or `flaky`.

Offline, deterministic, no network, no LLM. Labels at (run_id, test_id) over the 897
runs whose base is known (`data/interim/outcomes.parquet`):

  mine       strict: fails at head, passed at base (caused by the change)
  inherited  `all` minus `relaxed`: fails at head AND already failed at base
  flaky      `relaxed` minus `strict`: the same commit's reruns flip

The positive class of the main metric is NOT-MINE (inherited + flaky): that is the
failure a developer can stop investigating. Dangerous error: a `mine` failure that is
cleared (predicted not-mine) -- reported prominently.

Split D-57: runs ordered by `(run_started_at, run_id)`, 60/20/20. The test split has
fewer than 30 not-mine pairs, so a leave-one-repo-out pooled evaluation over every
run is reported too and labelled "small sample".

Writes `paper/generated/rq3_triage.md`, `models/e2_triage_v1.txt` (+ `.json`) and
`data/processed/e2_features.parquet`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from analysis import paper_md
from analysis.build_e1_features import load_changesets_by_pr, make_context
from analysis.rq1_divergence import COCHANGE_PIN, load_history, run_ts
from src.features.test_features import featurize
from src.features.triage_features import (RULE_BRANCH_N, TRIAGE_COLS, TriageHistory, fclass_onehot, message_hash)

OUT_FEATURES = Path("data/processed/e2_features.parquet")
MODEL_PATH = Path("models/e2_triage_v1.txt")
SEED = 0
TRAIN_FRAC, VAL_FRAC = 0.6, 0.2
SMALL_SAMPLE_MIN = 30
LGB_GRID = [{"num_leaves": nl, "learning_rate": lr, "min_data_in_leaf": md}
            for nl in (7, 15) for lr in (0.05, 0.1) for md in (5, 20)]


class CochangeView:
    """`HistoryView` that answers only co-change (E2 uses the E1 `prox_` / `cochg_` raw features)."""

    def __init__(self, history: dict) -> None:
        self._h = history

    def failures_before(self, test_file, ts):
        return []

    def head_failures_before(self, test_file, ts):
        return []

    def cofailure_count(self, changed_file, test_file, ts):
        return 0

    def cochange_partners(self, changed_file, ts, exclude_sha=None):
        rh = self._h.get(self._repo)
        return {p.path: (p.support, p.confidence) for p in rh.partners(changed_file, ts, exclude_sha)} if rh else {}

    def cochange_stats(self, changed_file, test_file, ts, exclude_sha=None):
        return self.cochange_partners(changed_file, ts, exclude_sha).get(test_file, (0, 0.0))

    def for_repo(self, repo: str) -> "CochangeView":
        v = CochangeView(self._h)
        v._repo = repo
        return v


def load_labels() -> pd.DataFrame:
    """One row per (run_id, test_id) of the known-base runs, with `label` and run metadata."""
    o = pd.read_parquet("data/interim/outcomes.parquet")
    inst = pd.read_parquet("data/interim/instances_raw.parquet",
                           columns=["run_id", "repo", "run_started_at", "base_ref", "head_sha", "pr_number"])
    piv = (o.drop_duplicates(["run_id", "test_id", "split"]).assign(v=1)
           .pivot_table(index=["run_id", "test_id"], columns="split", values="v", fill_value=0).reset_index())
    piv["label"] = "mine"
    piv.loc[(piv["all"] == 1) & (piv["relaxed"] == 0), "label"] = "inherited"
    piv.loc[(piv["relaxed"] == 1) & (piv["strict"] == 0), "label"] = "flaky"
    # a pair that is in `strict` is mine regardless of the other splits
    piv.loc[piv["strict"] == 1, "label"] = "mine"
    return piv[["run_id", "test_id", "label"]].merge(inst, on="run_id", how="left")


def split_runs(df: pd.DataFrame) -> dict[int, str]:
    """D-57 split of the runs: first 60% train, next 20% validation, rest test (floors)."""
    runs = df.drop_duplicates("run_id").sort_values(["run_started_at", "run_id"])["run_id"].tolist()
    n = len(runs)
    a, b = int(n * TRAIN_FRAC), int(n * (TRAIN_FRAC + VAL_FRAC))
    return {r: ("train" if i < a else "val" if i < b else "test") for i, r in enumerate(runs)}


def head_rows() -> pd.DataFrame:
    """Parsed head failures (one row per (run, test)), with message hash and run metadata."""
    p = pd.read_parquet("data/interim/parsed_outcomes.parquet")
    inst = pd.read_parquet("data/interim/instances_raw.parquet",
                           columns=["run_id", "repo", "run_started_at", "base_ref", "head_sha", "pr_number"])
    g = (p.sort_values(["run_id", "test_id", "job_id"]).groupby(["run_id", "test_id", "repo"], sort=False)
         .agg(status_error=("status", lambda s: int((s == "error").any())), n_job_rows=("job_id", "size"),
              duration_s=("duration_s", "mean"), message=("failure_message", "first")).reset_index())
    g = g.merge(inst.drop(columns=["repo"]), on="run_id", how="left")
    g["ts"] = g["run_started_at"].map(run_ts)
    g["msg_hash"] = g["message"].map(message_hash)
    return g


def build_features(pairs: pd.DataFrame, hist: TriageHistory, cochange: CochangeView) -> pd.DataFrame:
    """Feature matrix (`TRIAGE_COLS`) for (run, test) pairs that carry head-row columns.

    Args:
        pairs: Rows from :func:`head_rows` (optionally with `label`, `split`).
        hist: Failure history over all parsed runs.
        cochange: Trailing co-change view of the repos.

    Returns:
        `pairs` with the feature columns added.
    """
    binding = pd.read_parquet("data/interim/binding.parquet")
    bound = binding[binding["status"] == "exact"].set_index(["repo", "test_id"])["resolved_path"].to_dict()
    by_pr = load_changesets_by_pr()
    df = pairs.copy()
    df["test_file"] = [bound.get((r, t)) for r, t in zip(df["repo"], df["test_id"])]
    rows = []
    for r in df.itertuples():
        ts = int(r.ts)
        f = {"prior_head_fail_7d": hist.prior_failures(r.repo, r.test_id, ts, 7),
             "prior_head_fail_30d": hist.prior_failures(r.repo, r.test_id, ts, 30),
             "failed_prev3_branch": int(hist.failed_in_previous(r.repo, r.base_ref, r.test_id, ts, RULE_BRANCH_N)),
             "failed_prev10_branch": int(hist.failed_in_previous(r.repo, r.base_ref, r.test_id, ts, 10)),
             "msg_hash_seen": int(hist.message_seen(r.repo, r.msg_hash, ts)),
             **fclass_onehot(r.message), "bound": int(isinstance(r.test_file, str))}
        rows.append(f)
    feat = pd.DataFrame(rows, index=df.index)
    # E1 raw proximity / co-change features of the bound file, one featurize() call per run
    extra = []
    for (repo, run_id), g in df.groupby(["repo", "run_id"], sort=False):
        files = sorted({t for t in g["test_file"] if isinstance(t, str)})
        if not files:
            continue
        first = g.iloc[0]
        pr = str(int(first["pr_number"])) if pd.notna(first["pr_number"]) else ""
        cs = by_pr.get((repo, pr))
        changed = sorted(cs["filename"].unique()) if cs is not None else []
        ctx = make_context(repo, int(run_id), pr, first["run_started_at"], first["head_sha"], changed, cs)
        ff = featurize(ctx, files, cochange.for_repo(repo))
        extra.append(ff.assign(repo=repo, run_id=run_id))
    cols = [c for c in TRIAGE_COLS if c.startswith(("prox_", "cochg_"))]
    if extra:
        ex = pd.concat(extra, ignore_index=True)[["repo", "run_id", "test_file", *cols]]
        df = df.join(feat)
        df = df.merge(ex, on=["repo", "run_id", "test_file"], how="left")
    else:
        df = df.join(feat)
        for c in cols:
            df[c] = np.nan
    return df


def metrics(y_not: np.ndarray, pred_not: np.ndarray, score: np.ndarray | None, label: np.ndarray) -> dict:
    """E2 metrics for one prediction vector (positive class = not-mine)."""
    tp = int((y_not & pred_not).sum())
    fp = int((~y_not & pred_not).sum())
    fn = int((y_not & ~pred_not).sum())
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * p * r / (p + r) if tp and p + r else 0.0
    mine = ~y_not
    mine_pred = ~pred_not
    mp = int((mine & mine_pred).sum()) / int(mine_pred.sum()) if mine_pred.sum() else float("nan")
    mr = int((mine & mine_pred).sum()) / int(mine.sum()) if mine.sum() else float("nan")
    out = {"n": len(y_not), "not_mine": int(y_not.sum()), "p": p, "r": r, "f1": f1, "mine_p": mp, "mine_r": mr,
           "inherited_cleared": int(((label == "inherited") & pred_not).sum()),
           "inherited_total": int((label == "inherited").sum()),
           "flaky_cleared": int(((label == "flaky") & pred_not).sum()), "flaky_total": int((label == "flaky").sum()),
           "mine_wrongly_cleared": int((mine & pred_not).sum()), "mine_total": int(mine.sum()),
           "pr_auc": float("nan"), "roc_auc": float("nan")}
    if score is not None and 0 < y_not.sum() < len(y_not):
        out["pr_auc"] = float(average_precision_score(y_not, score))
        out["roc_auc"] = float(roc_auc_score(y_not, score))
    return out


def cluster_ci(y_not, pred_not, label, runs, key: str, n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Percentile 95% CI of one metric, resampling RUNS (pairs of a run are not independent)."""
    rng = np.random.default_rng(seed)
    uniq = np.unique(runs)
    idx_of = {r: np.flatnonzero(runs == r) for r in uniq}
    vals = []
    for _ in range(n_boot):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        ix = np.concatenate([idx_of[r] for r in pick])
        v = metrics(y_not[ix], pred_not[ix], None, label[ix])[key]
        if not np.isnan(v):
            vals.append(v)
    return (float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))) if vals else (float("nan"),) * 2


def make_lr() -> object:
    """Standardised, median-imputed, class-balanced logistic regression."""
    return make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(),
                         LogisticRegression(class_weight="balanced", max_iter=2000, random_state=SEED))


def lgb_params(extra: dict, pos_weight: float) -> dict:
    return {"objective": "binary", "metric": "average_precision", "deterministic": True, "force_row_wise": True,
            "num_threads": 1, "verbosity": -1, "seed": SEED, "bagging_seed": SEED, "feature_fraction_seed": SEED,
            "data_random_seed": SEED, "scale_pos_weight": pos_weight, **extra}


def fit_lgb(X: pd.DataFrame, y: np.ndarray, params: dict, rounds: int | None = None, Xv=None, yv=None):
    """LightGBM binary on not-mine; early stopping on validation average precision when `Xv` is given."""
    pos_w = float((y == 0).sum() / max(1, (y == 1).sum()))
    p = lgb_params(params, pos_w)
    ds = lgb.Dataset(X.to_numpy(dtype=float), label=y, feature_name=list(X.columns))
    if Xv is not None:
        dv = lgb.Dataset(Xv.to_numpy(dtype=float), label=yv, feature_name=list(X.columns))
        return lgb.train(p, ds, 300, valid_sets=[dv], valid_names=["val"],
                         callbacks=[lgb.early_stopping(30, verbose=False)])
    return lgb.train(p, ds, rounds or 50)


def best_threshold(y: np.ndarray, score: np.ndarray) -> float:
    """Threshold on validation scores maximising not-mine F1 (ties: the higher threshold)."""
    best, best_f = 0.5, -1.0
    for t in np.unique(np.round(score, 6)):
        f = metrics(y.astype(bool), score >= t, None, np.where(y, "inherited", "mine"))["f1"]
        if f >= best_f:
            best, best_f = float(t), f
    return best


def fmt(x: float, nd: int = 3) -> str:
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def main() -> int:
    labels = load_labels()
    assert labels["run_id"].nunique() == 897, labels["run_id"].nunique()
    split = split_runs(labels)
    labels["split"] = labels["run_id"].map(split)
    counts = labels.groupby(["split", "label"]).size().unstack(fill_value=0)
    print("class counts per split:\n", counts.to_string())

    heads = head_rows()
    events = heads[["repo", "run_id", "ts", "test_id", "base_ref", "msg_hash"]]
    hist = TriageHistory(events)

    spans = {}
    all_rows = heads
    for repo, g in all_rows.groupby("repo"):
        spans[repo] = (int(g["ts"].min()), int(g["ts"].max()))
    pin = json.loads(COCHANGE_PIN.read_text())
    cochange = CochangeView(load_history(spans, pin["window_days"], pin["support_threshold"], run_ts(pin["as_of"])))

    pairs = labels.merge(heads.drop(columns=["repo", "run_started_at", "base_ref", "head_sha", "pr_number"]),
                         on=["run_id", "test_id"], how="left")
    pairs = pairs.rename(columns={})
    pairs["ts"] = pairs["run_started_at"].map(run_ts)
    pairs["message"] = pairs["message"].astype(object)
    feats = build_features(pairs, hist, cochange)
    feats["not_mine"] = (feats["label"] != "mine").astype("int8")
    keep = ["repo", "run_id", "test_id", "test_file", "label", "split", *TRIAGE_COLS]
    out = feats[keep].copy()
    OUT_FEATURES.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_FEATURES, index=False)

    X = feats[TRIAGE_COLS].astype(float)
    y = feats["not_mine"].to_numpy()
    sp = feats["split"].to_numpy()
    lab = feats["label"].to_numpy()
    runs = feats["run_id"].to_numpy()
    tr, va, te = sp == "train", sp == "val", sp == "test"

    # ---- models, tuned on validation only -------------------------------------------------
    lr = make_lr().fit(X[tr], y[tr])
    lr_val = lr.predict_proba(X[va])[:, 1]
    thr_lr = best_threshold(y[va], lr_val)
    best = None
    for g in LGB_GRID:
        b = fit_lgb(X[tr], y[tr], g, Xv=X[va], yv=y[va])
        ap = float(b.best_score["val"]["average_precision"])
        if best is None or ap > best[0]:
            best = (ap, g, int(b.best_iteration))
    _, g_best, rounds = best
    booster = fit_lgb(X[tr], y[tr], g_best, rounds=rounds)
    thr_gb = best_threshold(y[va], booster.predict(X[va].to_numpy(dtype=float)))
    print(f"LightGBM: {g_best}, {rounds} rounds, val AP {best[0]:.3f}, threshold {thr_gb:.3f}; LR threshold {thr_lr:.3f}")

    def predict_all(Xa: pd.DataFrame, lr_m, gb_m) -> dict:
        return {"lr": lr_m.predict_proba(Xa)[:, 1], "gb": gb_m.predict(Xa.to_numpy(dtype=float))}

    def evaluate(mask: np.ndarray, scores: dict, thr_l: float, thr_g: float) -> list[dict]:
        yy, ll, rr = y[mask].astype(bool), lab[mask], runs[mask]
        sub = feats[mask]
        methods = [("Blame-all (everything is mine)", np.zeros(mask.sum(), bool), None),
                   (f"R-branch (failed in any of the previous {RULE_BRANCH_N} runs of the branch)",
                    sub["failed_prev3_branch"].to_numpy() == 1, sub["failed_prev3_branch"].to_numpy(float)),
                   ("R-msg (failure message seen in an earlier run)", sub["msg_hash_seen"].to_numpy() == 1,
                    sub["msg_hash_seen"].to_numpy(float)),
                   ("Logistic regression", scores["lr"][mask] >= thr_l, scores["lr"][mask]),
                   ("LightGBM", scores["gb"][mask] >= thr_g, scores["gb"][mask])]
        res = []
        for name, pred, sc in methods:
            m = metrics(yy, pred, sc, ll)
            m["name"] = name
            for k in ("p", "r", "f1", "mine_wrongly_cleared"):
                m[f"{k}_ci"] = cluster_ci(yy, pred, ll, rr, k, n_boot=1000)
            res.append(m)
        return res

    scores_chrono = predict_all(X, lr, booster)
    chrono = evaluate(te, scores_chrono, thr_lr, thr_gb)

    # ---- leave-one-repo-out pooled over every run (small-sample remedy) -------------------
    lo_lr, lo_gb = np.zeros(len(feats)), np.zeros(len(feats))
    for repo in sorted(feats["repo"].unique()):
        held = (feats["repo"] == repo).to_numpy()
        if held.sum() == 0 or (~held).sum() == 0 or y[~held].sum() == 0:
            continue
        l_m = make_lr().fit(X[~held], y[~held])
        g_m = fit_lgb(X[~held], y[~held], g_best, rounds=rounds)
        lo_lr[held] = l_m.predict_proba(X[held])[:, 1]
        lo_gb[held] = g_m.predict(X[held].to_numpy(dtype=float))
    pooled = evaluate(np.ones(len(feats), bool), {"lr": lo_lr, "gb": lo_gb}, thr_lr, thr_gb)

    # ---- final model for the agents and the descriptive application -----------------------
    trva = tr | va
    final = fit_lgb(X[trva], y[trva], g_best, rounds=rounds)
    final.save_model(str(MODEL_PATH))
    MODEL_PATH.with_suffix(".json").write_text(json.dumps({
        "git_sha": paper_md.git_sha(), "feature_list": TRIAGE_COLS, "params": lgb_params(g_best, 0.0),
        "rounds": rounds, "threshold_not_mine": thr_gb, "seed": SEED, "positive_class": "not-mine",
        "n_train_pairs": int(trva.sum()), "n_test_pairs": int(te.sum()), "lightgbm": lgb.__version__,
        "trained_by_script": "analysis/rq3_triage.py", "fit_on": "train+val",
        "n_runs": int(feats["run_id"].nunique())}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # descriptive application: head failures of runs with no resolvable base (no ground truth)
    base = pd.read_parquet("data/interim/base_resolution_new.parquet")
    nb_runs = set(base.loc[base["status"] == "no_base", "run_id"]) & set(heads["run_id"]) - set(labels["run_id"])
    app = heads[heads["run_id"].isin(nb_runs)].copy()
    app_dist = None
    if len(app):
        app_f = build_features(app.assign(label="unknown"), hist, cochange)
        sc = final.predict(app_f[TRIAGE_COLS].astype(float).to_numpy(dtype=float))
        pred_not = sc >= thr_gb
        app_dist = {"runs": int(app["run_id"].nunique()), "pairs": len(app_f), "pred_not_mine": int(pred_not.sum()),
                    "pred_mine": int((~pred_not).sum()),
                    "rbranch": int((app_f["failed_prev3_branch"] == 1).sum()),
                    "rmsg": int((app_f["msg_hash_seen"] == 1).sum())}
        print("application:", app_dist)

    # ---- report ----------------------------------------------------------------------------
    cols = ["method", "pairs", "not-mine P", "not-mine R", "not-mine F1", "PR-AUC", "ROC-AUC", "mine P", "mine R",
            "inherited cleared", "flaky cleared", "mine WRONGLY CLEARED"]

    def rows_of(res: list[dict]) -> list[list]:
        out_rows = []
        for m in res:
            def with_ci(k):
                lo, hi = m[f"{k}_ci"]
                return f"{fmt(m[k])} [{fmt(lo)}, {fmt(hi)}]"
            out_rows.append([m["name"], m["n"], with_ci("p"), with_ci("r"), with_ci("f1"), fmt(m["pr_auc"]),
                             fmt(m["roc_auc"]), fmt(m["mine_p"]), fmt(m["mine_r"]),
                             f"{m['inherited_cleared']}/{m['inherited_total']}",
                             f"{m['flaky_cleared']}/{m['flaky_total']}",
                             f"**{m['mine_wrongly_cleared']}/{m['mine_total']}**"])
        return out_rows

    n_not_test = int(y[te].sum())
    small = n_not_test < SMALL_SAMPLE_MIN
    text = paper_md.header("RQ3 / E2: failure triage (mine / inherited / flaky)", "analysis/rq3_triage.py")
    text += ("\nLabels at (run_id, test_id) over the 897 known-base runs. Positive class of the main metric: "
             "**not-mine** (inherited + flaky), the failures a developer can stop investigating. 95% CIs are cluster "
             "bootstraps over runs (1,000 resamples, seed 0). Features use only events strictly before the run "
             "(`src/features/triage_features.py`). The parsed corpus holds failures only, so 'the previous runs "
             "of the branch' means the previous runs that have parsed failures.\n")
    text += "\n## Class counts per split (pairs)\n\n" + paper_md.table(
        ["split", "mine", "inherited", "flaky", "runs"],
        [[s, int(counts.loc[s].get("mine", 0)), int(counts.loc[s].get("inherited", 0)),
          int(counts.loc[s].get("flaky", 0)), int(feats.loc[feats["split"] == s, "run_id"].nunique())]
         for s in ("train", "val", "test")])
    text += (f"\n## Chronological test split (D-57)" + (" -- SMALL SAMPLE" if small else "")
             + f"\n\n{int(te.sum())} pairs, {n_not_test} not-mine"
             + (f" (< {SMALL_SAMPLE_MIN}: the intervals are wide and the point estimates should not be "
                "over-read; the pooled leave-one-repo-out table below uses every run)" if small else "")
             + ".\n\n" + paper_md.table(cols, rows_of(chrono)))
    text += (f"\n## Leave-one-repo-out, pooled over all {int(len(feats))} pairs"
             + (" -- SMALL SAMPLE (per-repo folds are tiny; pooled predictions are each made by a model that "
                "never saw that repo)" if small else "") + "\n\n"
             + f"{int(y.sum())} not-mine pairs. Rules need no fitting; LR and LightGBM use the configuration "
             "and thresholds chosen on the chronological validation split.\n\n"
             + paper_md.table(cols, rows_of(pooled)))
    dangerous = {m["name"]: m["mine_wrongly_cleared"] for m in pooled}
    text += ("\n## The dangerous error\n\nA `mine` failure predicted not-mine is a real regression a developer would "
             "be told to ignore. Pooled leave-one-repo-out: "
             + "; ".join(f"{k}: {v}/{pooled[0]['mine_total']}" for k, v in dangerous.items())
             + f". Chronological test split: "
             + "; ".join(f"{m['name']}: {m['mine_wrongly_cleared']}/{m['mine_total']}" for m in chrono) + ".\n")
    text += (f"\n## Tuning (validation only)\n\nLightGBM `{json.dumps(g_best, sort_keys=True)}`, {rounds} rounds, "
             f"validation average precision {best[0]:.3f}, decision threshold {thr_gb:.3f}; logistic regression "
             f"threshold {thr_lr:.3f} (both maximise validation not-mine F1).\n")
    if app_dist:
        text += ("\n## Descriptive application (NO ground truth)\n\nThe final model (train+validation) applied to head "
                 "failures of runs whose base could not be resolved, where today's labelling must emit nothing. "
                 "These are model predictions, not measurements.\n\n"
                 + paper_md.table(["measure", "n"], [
                     ["runs with parsed head failures and no base", app_dist["runs"]],
                     ["failing (run, test) pairs", app_dist["pairs"]],
                     ["predicted not-mine (inherited or flaky)", paper_md.rate(app_dist["pred_not_mine"], app_dist["pairs"])],
                     ["predicted mine", paper_md.rate(app_dist["pred_mine"], app_dist["pairs"])],
                     ["R-branch fires", paper_md.rate(app_dist["rbranch"], app_dist["pairs"])],
                     ["R-msg fires", paper_md.rate(app_dist["rmsg"], app_dist["pairs"])]]))
    paper_md.write("rq3_triage.md", text)
    print("wrote paper/generated/rq3_triage.md,", MODEL_PATH, OUT_FEATURES)
    return 0


if __name__ == "__main__":
    sys.exit(main())
