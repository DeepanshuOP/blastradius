"""Build `data/processed/e1_features.parquet`: one row per (instance, candidate test file).

Instances are the 734 RQ1 ground-truth instances (strict labels bound to a test
file). Candidates, features and the D-57 split come from `src/features/` and are
the same code the agents run online. Prints the denominators E1 is judged on.

Split (D-57): instances ordered by `(run_started_at, run_id)`; the first 60%
(floor) are `train`, the next 20% (floor) `val`, the rest `test`.

No network, no LLM. Reads `data/interim/*` and the pinned clones' trees.
"""

from __future__ import annotations

import sys
from bisect import bisect_left
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.rq1_divergence import ground_truth, load_data, run_ts
from src.features.candidates import candidates_for, load_repo_candidates
from src.features.context import BrBenchHistory, ChangeContext
from src.features.test_features import FEATURE_COLS, featurize
from src.parse.changeset import is_conventional_test_file

OUT = Path("data/processed/e1_features.parquet")
TRAIN_FRAC, VAL_FRAC = 0.6, 0.2


def assign_split(keys: list[tuple]) -> dict[tuple, str]:
    """D-57 split of `(started_at, run_id, repo)`-sortable instance keys.

    Args:
        keys: One `(run_started_at, run_id, repo)` tuple per instance.

    Returns:
        `{(repo, run_id): "train" | "val" | "test"}`; first 60% / next 20% / rest, floors.
    """
    order = sorted(keys, key=lambda k: (k[0], k[1]))
    n = len(order)
    n_train, n_val = int(n * TRAIN_FRAC), int(n * VAL_FRAC)
    out = {}
    for i, (_, run_id, repo) in enumerate(order):
        out[(repo, run_id)] = "train" if i < n_train else "val" if i < n_train + n_val else "test"
    return out


def make_context(repo: str, run_id: int, pr: str, started: str, head_sha: str | None, files: list[str],
                 g: pd.DataFrame | None) -> ChangeContext:
    """One :class:`ChangeContext` from a run's PR changeset rows.

    Args:
        repo: `owner/name`.
        run_id: Workflow run id.
        pr: PR number as a string.
        started: `run_started_at`.
        head_sha: The run's head commit.
        files: Changed paths (RQ1's union over the PR's head shas).
        g: The PR's rows of `changesets.parquet`, or None when there is no changeset.

    Returns:
        The context. Lines come from the rows of the run's own head sha when present, else all rows
        (de-duplicated by filename); the touches flags are `any`, `is_docs_only` is `all` over the PR's rows.
    """
    lines, tt, tb, tc, docs = 0, False, False, False, False
    if g is not None:
        sub = g[g["head_sha"] == head_sha] if head_sha in set(g["head_sha"]) else g
        sub = sub.drop_duplicates("filename", keep="last")
        lines = int(sub["additions"].sum() + sub["deletions"].sum())
        tt, tb, tc = bool(g["touches_test_file"].any()), bool(g["touches_build_config"].any()), bool(g["touches_ci_config"].any())
        docs = bool(g["is_docs_only"].all())
    return ChangeContext(repo=repo, instance_key=(repo, run_id), ts=run_ts(started), changed_files=tuple(sorted(files)),
                         n_lines_changed=lines, touches_test_file=tt, touches_build_config=tb, touches_ci_config=tc,
                         is_docs_only=docs, head_sha=head_sha)


def load_changesets_by_pr() -> dict:
    """`changesets.parquet` grouped by `(repo, pr_number as str)`."""
    cs = pd.read_parquet("data/interim/changesets.parquet")
    cs["pr_number"] = cs["pr_number"].astype(str)
    return {k: g for k, g in cs.groupby(["repo", "pr_number"])}


def build_contexts(data, gt: dict) -> list[tuple[ChangeContext, str]]:
    """One :class:`ChangeContext` per ground-truth instance, with its `run_started_at` string.

    Args:
        data: `Rq1Data`.
        gt: `ground_truth(data)`.

    Returns:
        `(context, run_started_at)` per instance, unordered.
    """
    by_pr = load_changesets_by_pr()
    out = []
    for _, r in data.valid_runs.iterrows():
        key = (r["repo"], r["run_id"])
        if key not in gt:
            continue
        pr = str(r["pr_number"])
        files = sorted(data.pr_to_changed.get((r["repo"], pr), set()))
        ctx = make_context(r["repo"], r["run_id"], pr, r["run_started_at"], data.head_sha_of.get(r["run_id"]),
                           files, by_pr.get((r["repo"], pr)))
        out.append((ctx, r["run_started_at"]))
    return out


def build(data=None) -> tuple[pd.DataFrame, dict]:
    """Build the feature table.

    Args:
        data: Preloaded `Rq1Data` (loaded when omitted).

    Returns:
        `(features, stats)`; `stats` holds the printed denominators.
    """
    data = data or load_data()
    gt = ground_truth(data)
    ctxs = build_contexts(data, gt)
    split = assign_split([(started, ctx.instance_key[1], ctx.repo) for ctx, started in ctxs])
    hist = BrBenchHistory(data)

    seen: dict[str, list[tuple[int, str]]] = {}  # repo -> sorted (ts, bound GT path)
    for r in data.hist_all.itertuples():
        seen.setdefault(r.repo, []).append((run_ts(r.run_started_at), r.resolved_path))
    for v in seen.values():
        v.sort()
    seen_ts = {k: [t for t, _ in v] for k, v in seen.items()}
    repo_rc = {repo: load_repo_candidates(repo) for repo in sorted({c.repo for c, _ in ctxs})}

    frames, per_inst = [], []
    n_pos_unseen_nonconv = 0
    for ctx, started in sorted(ctxs, key=lambda x: (x[1], x[0].instance_key[1])):
        repo, run_id = ctx.instance_key
        before = {p for _, p in seen.get(repo, [])[:bisect_left(seen_ts.get(repo, []), ctx.ts)]}
        own = set(gt[ctx.instance_key])
        cands = candidates_for(repo_rc[repo], before, own)
        df = featurize(ctx, cands, hist.for_repo(repo))
        df.insert(0, "label", df["test_file"].isin(own).astype("int8"))
        df.insert(0, "split", split[ctx.instance_key])
        df.insert(0, "ts", np.int64(ctx.ts))
        df.insert(0, "run_id", np.int64(run_id))
        df.insert(0, "repo", repo)
        frames.append(df)
        present = len(own & set(cands))
        n_pos_unseen_nonconv += sum(1 for f in own if f not in before and not is_conventional_test_file(f))
        per_inst.append((len(cands), len(own), present, len(own)))
    feats = pd.concat(frames, ignore_index=True)
    for c in FEATURE_COLS:  # the dtypes docs/SCHEMAS.md declares
        if feats[c].dtype.kind == "i":
            feats[c] = feats[c].astype("int8" if c.startswith(("prox_in", "prox_name", "prox_same", "chg_touches", "chg_docs")) else "int32")
        else:
            feats[c] = feats[c].astype("float64")
    cand_n = np.array([p[0] for p in per_inst])
    pos_n = np.array([p[1] for p in per_inst])
    stats = {
        "instances": len(ctxs),
        "no_changeset": sum(1 for c, _ in ctxs if not c.changed_files),
        "cand_min_med_max": (int(cand_n.min()), float(np.median(cand_n)), int(cand_n.max())),
        "pos_min_med_max": (int(pos_n.min()), float(np.median(pos_n)), int(pos_n.max())),
        "gt_files": int(sum(p[3] for p in per_inst)),
        "gt_present": int(sum(p[2] for p in per_inst)),
        "rows": len(feats),
        "split_counts": {s: int((feats.groupby(["repo", "run_id"]).first()["split"] == s).sum())
                         for s in ("train", "val", "test")},
        "sources": {repo: rc.source for repo, rc in repo_rc.items()},
        "pos_unseen_nonconventional": n_pos_unseen_nonconv,
    }
    return feats, stats


def main() -> int:
    feats, s = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    feats.to_parquet(OUT, index=False)
    print(f"instances: {s['instances']} (without a changeset: {s['no_changeset']})")
    print(f"split (instances): {s['split_counts']}")
    print(f"rows: {s['rows']}")
    print("candidates per instance (min / median / max): %d / %g / %d" % s["cand_min_med_max"])
    print("positives per instance (min / median / max): %d / %g / %d" % s["pos_min_med_max"])
    pct = 100 * s["gt_present"] / s["gt_files"]
    print(f"ground-truth files among candidates: {s['gt_present']}/{s['gt_files']} ({pct:.2f}%)")
    print(f"candidate sources: { {k: sum(1 for v in s['sources'].values() if v == k) for k in set(s['sources'].values())} }")
    print(f"positives that are non-conventional and unseen before (candidate only because they are labels): "
          f"{s['pos_unseen_nonconventional']}")
    print(f"wrote {OUT}")
    if s["gt_present"] != s["gt_files"] or s["instances"] != 734:
        print("HARD STOP 1: ground-truth coverage or instance count off", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
