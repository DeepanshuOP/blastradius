"""What the `exact_green` verification moved, with every superseded figure named.

Phase 017 Phase 4. Applies the verdicts from
`analysis/verify_exact_green.py` to the resolution frame the labeller actually
reads (`data/interim/base_resolution_new.parquet`), re-derives the splits, and
prints each figure beside the one it supersedes. No number is replaced silently.

Two scenarios are reported, because the sweep is incomplete and collapsing them
into one figure would be dishonest in opposite directions:

* **EVIDENCE-ONLY** — apply verdicts only where a base run was actually
  verified. Instances not yet swept keep `exact_green` and are labelled
  PROVISIONAL. This measures what the verification has proved so far.
* **INVARIANT-6** — what `src/label/base_resolve.py` now produces: a successful
  base with no parsed log evidence is `no_base`, verified or not. This is the
  defensible corpus, and it is a floor that rises as the sweep completes.

The truth is bracketed by the two. Quote both or neither.
"""

from __future__ import annotations

import argparse

import pandas as pd

from src.label.base_resolve import GREEN_VERDICTS
from src.label.fault_revealing import compute_labels

RESOLUTION = "data/interim/base_resolution_new.parquet"
VERIFICATION = "data/interim/exact_green_verification.parquet"

#: Workflows that visibly never run a test, identified by name during the
#: Phase 017 census of the 4,245 exact_green instances.
TEST_FREE_WORKFLOW_NAMES = (
    "Clang format linter",
    "PR Lint",
    "CodeQL",
    "CodeQL Advanced",
    "lint",
    "Auto PR V2 Deployment",
)

#: The figures this round supersedes, and where each came from.
SUPERSEDED = {
    "no_base_rate": ("43.88%", "Phase 014-A"),
    "exact_green": ("4,245", "Phase 016-A"),
    "strict_instances": ("778", "Phase 014-A"),
    "strict_labels": ("4,194", "Phase 014-A / D-44"),
    "gate1": ("4,194 / 5,000", "D-44"),
    "published_strict": ("524", "Phase 007-B, published"),
}


def apply_verdicts(res: pd.DataFrame, ver: pd.DataFrame, scenario: str) -> pd.DataFrame:
    """Rewrite `exact_green` rows using verification evidence.

    Args:
        res: Resolution frame the labeller reads.
        ver: Verification frame from `verify_exact_green.run`.
        scenario: "evidence_only" or "invariant_6".

    Returns:
        A copy of `res` with `status` and `base_parse_status` updated.
    """
    vmap = (
        ver.drop_duplicates(subset=["repo", "run_id"])
        .set_index(["repo", "run_id"])[["base_parse_status", "new_status"]]
        .to_dict("index")
    )
    out = res.copy()

    def new_status(row):
        if row["status"] != "exact_green":
            return row["status"]
        v = vmap.get((row["repo"], row["run_id"]))
        if v is None:
            return "no_base" if scenario == "invariant_6" else "exact_green"
        if v["base_parse_status"] == "not_processed":
            return "no_base" if scenario == "invariant_6" else "exact_green"
        return v["new_status"]

    def parse_status(row):
        if row["status"] != "exact_green":
            return None
        v = vmap.get((row["repo"], row["run_id"]))
        return v["base_parse_status"] if v else "unverified"

    out["base_parse_status"] = out.apply(parse_status, axis=1)
    out["status"] = out.apply(new_status, axis=1)
    return out


def splits_for(res: pd.DataFrame) -> dict[str, tuple[int, int]]:
    """Re-derive the three splits from a resolution frame.

    Args:
        res: Resolution frame with a `status` column.

    Returns:
        Mapping of split name to (instances, labels).
    """
    instances = pd.read_parquet("data/interim/instances_raw.parquet")
    head_parsed = pd.read_parquet("data/interim/parsed_outcomes.parquet")
    base_parsed = pd.read_parquet("data/interim/base_outcomes.parquet")
    outcomes, _stats = compute_labels(res, instances, head_parsed, base_parsed)
    return {
        s: (
            outcomes[outcomes["split"] == s]["run_id"].nunique(),
            len(outcomes[outcomes["split"] == s]),
        )
        for s in ("all", "relaxed", "strict")
    }


def run(resolution: str = RESOLUTION, verification: str = VERIFICATION) -> dict:
    """Print every Phase 4 supersession.

    Args:
        resolution: Resolution parquet the labeller reads.
        verification: Verification parquet from the exact_green sweep.

    Returns:
        Dict of the computed figures, keyed by scenario.
    """
    res = pd.read_parquet(resolution)
    ver = pd.read_parquet(verification)

    n = len(res)
    old_no_base = int((res["status"] == "no_base").sum())
    old_eg = int((res["status"] == "exact_green").sum())
    old = splits_for(res)

    print("=" * 78)
    print("PHASE 4 — WHAT MOVED. Each figure names the one it supersedes.")
    print("=" * 78)
    print(f"\nBASELINE (as committed, from {resolution}):")
    print(f"  instances:      {n}")
    print(f"  no_base:        {old_no_base} / {n} ({old_no_base/n:.2%})")
    print(f"  exact_green:    {old_eg}")
    print(f"  strict:         {old['strict'][0]} instances, {old['strict'][1]} labels")

    results = {"baseline": {"no_base": old_no_base, "exact_green": old_eg, **old}}

    for scenario, title in (
        ("evidence_only", "EVIDENCE-ONLY (verified verdicts applied; unswept stay PROVISIONAL)"),
        ("invariant_6", "INVARIANT-6 (what src/label/base_resolve.py now produces)"),
    ):
        adj = apply_verdicts(res, ver, scenario)
        nb = int((adj["status"] == "no_base").sum())
        eg = int((adj["status"] == "exact_green").sum())
        ex = int((adj["status"] == "exact").sum())
        sp = splits_for(adj)
        results[scenario] = {"no_base": nb, "exact_green": eg, "exact": ex, **sp}

        print(f"\n{'-' * 78}\n{title}\n{'-' * 78}")
        print(f"4a. no_base rate ......... {nb} / {n} ({nb/n:.2%})"
              f"   supersedes {SUPERSEDED['no_base_rate'][0]} ({SUPERSEDED['no_base_rate'][1]})")
        print(f"4b. exact_green count .... {eg}"
              f"   supersedes {SUPERSEDED['exact_green'][0]} ({SUPERSEDED['exact_green'][1]})")
        print(f"    (of which reclassified to `exact` because the base FAILED: {ex - int((res['status']=='exact').sum())})")
        print(f"4c. strict instances ..... {sp['strict'][0]}"
              f"   supersedes {SUPERSEDED['strict_instances'][0]} ({SUPERSEDED['strict_instances'][1]})")
        print(f"4d. strict labels ........ {sp['strict'][1]}"
              f"   supersedes {SUPERSEDED['strict_labels'][0]} ({SUPERSEDED['strict_labels'][1]})")
        print(f"4e. Gate 1 (D-44, labels)  {sp['strict'][1]} / 5,000 — NOT MET"
              f"   supersedes {SUPERSEDED['gate1'][0]}")
        pub = 524
        delta = sp["strict"][0] - pub
        word = "LARGER" if delta > 0 else "SMALLER"
        print(f"4f. versus the published {pub} strict instances: {word} by {abs(delta)} "
              f"({sp['strict'][0]} vs {pub})")
        print(f"    all: {sp['all'][0]} inst / {sp['all'][1]} labels · "
              f"relaxed: {sp['relaxed'][0]} inst / {sp['relaxed'][1]} labels")

    # ---- 4g: corpus-inclusion defect -------------------------------------
    print(f"\n{'-' * 78}\n4g. TEST-FREE WORKFLOWS SURVIVING INTO STRICT\n{'-' * 78}")
    inst = pd.read_parquet("data/interim/instances_raw.parquet").drop_duplicates("run_id")
    tf = inst[inst["workflow_name"].isin(TEST_FREE_WORKFLOW_NAMES)]
    tf_runs = set(tf["run_id"])
    eg_runs = set(res[res["status"] == "exact_green"]["run_id"])
    tf_eg = tf_runs & eg_runs
    print(f"  workflows counted: {', '.join(TEST_FREE_WORKFLOW_NAMES)}")
    print(f"  exact_green instances in a visibly test-free workflow: {len(tf_eg)}")

    for scenario in ("evidence_only", "invariant_6"):
        adj = apply_verdicts(res, ver, scenario)
        instances = pd.read_parquet("data/interim/instances_raw.parquet")
        head_parsed = pd.read_parquet("data/interim/parsed_outcomes.parquet")
        base_parsed = pd.read_parquet("data/interim/base_outcomes.parquet")
        outcomes, _stats = compute_labels(adj, instances, head_parsed, base_parsed)
        strict_runs = set(outcomes[outcomes["split"] == "strict"]["run_id"])
        survivors = tf_eg & strict_runs
        print(f"  [{scenario}] surviving into strict: {len(survivors)} / {len(tf_eg)}")
        if survivors:
            print("    -> corpus-inclusion defect, not a labelling one.")

    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--resolution", default=RESOLUTION)
    parser.add_argument("--verification", default=VERIFICATION)
    args = parser.parse_args()
    run(resolution=args.resolution, verification=args.verification)


if __name__ == "__main__":
    main()
