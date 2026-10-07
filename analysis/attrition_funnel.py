"""Pipeline attrition funnels, every stage computed from local data.

Three funnels, one per unit, because a funnel only means something while its
unit does not change (a PR has many runs; a repo has many PRs):

  - repos:  SEART export -> CI-live -> test-intent -> sampled -> swept ->
            with a failed run -> with a strict instance;
  - PRs:    discovered -> with a failed run -> with a strict instance;
  - runs:   discovered -> failed -> with a failed-job log on disk -> with a parsed
            head test failure -> with a resolved base -> with a known base failure
            set -> with a strict label.

Each stage is the intersection of its own predicate with the previous stage's
set, so counts are non-increasing by construction, and this is asserted. Nothing
is hard-coded and nothing falls back: a missing input raises.

The repository-frame stages (SEART export to sample draw) come from
`data/frame/attrition_stage.csv` and `frame_v1.csv`, as the generator at
c042ea8 computed them.
"""

from __future__ import annotations

import pandas as pd

from analysis import paper_md
from src.harvest.rawstore import RawStore

FRAME_STAGE = "data/frame/attrition_stage.csv"
FRAME_SAMPLE = "data/frame/frame_v1.csv"
NOT_CI_LIVE = ("no_ci", "api_error")
KEPT = "kept"


def _names(df: pd.DataFrame) -> pd.Series:
    return df["owner"] + "/" + df["repo"]


def has_failed_job_log(row, store: RawStore) -> bool:
    """Whether any failed job of the run has its log in the local RawStore."""
    return any(conclusion == "failure" and store.exists(row.repo, "logs", int(job_id))
               for job_id, conclusion in zip(row.job_ids, row.job_conclusions))


def repo_chain(stage: pd.DataFrame, sample: pd.DataFrame, instances: pd.DataFrame, strict_runs: set) -> list[tuple]:
    """Repository funnel as `(stage, set, source)` rows."""
    names = _names(stage)
    assert names.is_unique, "attrition_stage.csv lists a repo twice"
    swept = set(instances["repo"])
    failed = set(instances.loc[instances["run_conclusion"] == "failure", "repo"])
    labelled = set(instances.loc[instances["run_id"].isin(strict_runs), "repo"])
    return [
        ("SEART export", set(names), FRAME_STAGE),
        ("CI-live (>= 100 runs in 90 days)", set(names[~stage["verdict"].isin(NOT_CI_LIVE)]), FRAME_STAGE),
        ("has a test-intent workflow", set(names[stage["verdict"] == KEPT]), FRAME_STAGE),
        ("sampled into the frame", set(_names(sample)), FRAME_SAMPLE),
        ("swept (>= 1 run harvested)", swept, "instances_raw.parquet"),
        ("with a failed run", failed, "instances_raw.parquet"),
        ("with a strict instance", labelled, "outcomes.parquet (split == strict)"),
    ]


def pr_chain(instances: pd.DataFrame, strict_runs: set) -> list[tuple]:
    """PR funnel as `(stage, set, source)` rows."""
    prs = instances.dropna(subset=["pr_number"])
    key = list(zip(prs["repo"], prs["pr_number"]))
    prs = prs.assign(key=key)
    return [
        ("PRs discovered", set(prs["key"]), "instances_raw.parquet"),
        ("with a failed run", set(prs.loc[prs["run_conclusion"] == "failure", "key"]), "instances_raw.parquet"),
        ("with a strict instance", set(prs.loc[prs["run_id"].isin(strict_runs), "key"]),
         "outcomes.parquet (split == strict)"),
    ]


def run_chain(instances: pd.DataFrame, parsed: pd.DataFrame, resolution: pd.DataFrame, base_out: pd.DataFrame,
              strict_runs: set, store: RawStore) -> list[tuple]:
    """Run (instance) funnel as `(stage, set, source)` rows."""
    failed = instances[instances["run_conclusion"] == "failure"]
    logged = failed[[has_failed_job_log(r, store) for r in failed.itertuples()]]
    resolved = set(resolution.loc[resolution["status"] != "no_base", "run_id"])
    known_base = set(resolution.loc[resolution["status"] == "exact_green", "run_id"]) | set(base_out["run_id"])
    return [
        ("runs discovered", set(instances["run_id"]), "instances_raw.parquet"),
        ("failed runs", set(failed["run_id"]), "instances_raw.parquet"),
        ("with a failed-job log on disk", set(logged["run_id"]), "RawStore (data/raw)"),
        ("with a parsed head test failure", set(parsed["run_id"]), "parsed_outcomes.parquet"),
        ("with a resolved base", resolved, "base_resolution_new.parquet (status != no_base)"),
        ("with a known base failure set", known_base, "base_resolution_new.parquet (exact_green) + base_outcomes.parquet"),
        ("with >= 1 strict label", strict_runs, "outcomes.parquet (split == strict)"),
    ]


def nest(chain: list[tuple]) -> list[tuple[str, set, str]]:
    """Intersect each stage with the previous one and assert the counts do not rise."""
    out, prev = [], None
    for name, members, source in chain:
        members = set(members) if prev is None else set(members) & prev
        assert prev is None or len(members) <= len(prev), f"{name} exceeds its predecessor"
        out.append((name, members, source))
        prev = members
    return out


def render(title: str, unit: str, chain: list[tuple[str, set, str]]) -> str:
    """Markdown table: count, share of the previous stage, share of the first stage (both n/d)."""
    first = len(chain[0][1])
    rows, prev = [], None
    for name, members, source in chain:
        n = len(members)
        rows.append([name, f"{n:,}", "-" if prev is None else paper_md.rate(n, prev),
                     "-" if prev is None else paper_md.rate(n, first), source])
        prev = n
    return (f"\n## {title}\n\nUnit: {unit}.\n\n"
            + paper_md.table(["stage", "count", "of previous stage", "of first stage", "source"], rows))


def main() -> None:
    stage = pd.read_csv(FRAME_STAGE)
    sample = pd.read_csv(FRAME_SAMPLE)
    instances = pd.read_parquet("data/interim/instances_raw.parquet")
    outcomes = pd.read_parquet("data/interim/outcomes.parquet")
    parsed = pd.read_parquet("data/interim/parsed_outcomes.parquet")
    resolution = pd.read_parquet("data/interim/base_resolution_new.parquet")
    base_out = pd.read_parquet("data/interim/base_outcomes.parquet")
    strict_runs = set(outcomes.loc[outcomes["split"] == "strict", "run_id"])

    repos = nest(repo_chain(stage, sample, instances, strict_runs))
    prs = nest(pr_chain(instances, strict_runs))
    runs = nest(run_chain(instances, parsed, resolution, base_out, strict_runs, RawStore()))

    # Base failure set, counted without nesting, for the reconciliation note.
    exact_green = set(resolution.loc[resolution["status"] == "exact_green", "run_id"])
    with_base_outcomes = set(base_out["run_id"])
    standalone = len(exact_green | with_base_outcomes)

    text = paper_md.header("Pipeline attrition funnels", "analysis/attrition_funnel.py",
                           "Every stage is computed from local data and is the intersection of its predicate with the "
                           "previous stage, so each count is at most its predecessor's (asserted).")
    text += render("Repositories", "repos", repos)
    text += render("Pull requests", "(repo, PR number)", prs)
    text += render("Runs (benchmark instances)", "workflow runs", runs)
    text += "\n## Base failure sets\n\n" + paper_md.table(["measure", "n/d"], [
        ["runs whose base was an exact_green run", paper_md.rate(len(exact_green), len(resolution))],
        ["runs with a failure set parsed from a base log (`base_outcomes.parquet`)",
         paper_md.rate(len(with_base_outcomes), len(resolution))],
        ["runs with a known base failure set, either way", paper_md.rate(standalone, len(resolution))],
        ["... of which in the run funnel above (also has a failed-job log, a parsed head failure, a resolved base)",
         paper_md.rate(len(runs[5][1]), standalone)]])
    text += ("\n`parse_base_logs.py` reports the same quantity (instances with both head and base failure sets). "
             "It counts a head run once its base run's parser returned any record, but `base_outcomes.parquet` only "
             "holds records whose identifier normalised to a canonical test id. A base run whose every identifier "
             "failed to normalise was counted by the first and absent from the second, which was the whole of the "
             "one-run difference between the two. `parse_base_logs.py` now sets the flag only after normalisation, "
             "so both count the runs in the 'either way' row.\n")
    text += ("\n## Stages not computed\n\n"
             "- Log-level stages (logs captured, not expired, parsed, with test output): omitted. Their unit is logs, "
             "which do not nest into runs; 'with a failed-job log on disk' is the run-level replacement.\n"
             "- Graph-build and binding stages: omitted here. They are measured outside the funnel "
             "(`binding.md`, `gates.md`); no local artefact records a per-run graph build outcome that nests with runs.\n")
    paper_md.write("attrition_funnel.md", text)

    for title, chain in (("repos", repos), ("PRs", prs), ("runs", runs)):
        print(f"\n{title}")
        prev = None
        for name, members, _ in chain:
            n = len(members)
            print(f"  {name:<45} {n:>9,d}  {'' if prev is None else paper_md.rate(n, prev)}")
            prev = n


if __name__ == "__main__":
    main()
