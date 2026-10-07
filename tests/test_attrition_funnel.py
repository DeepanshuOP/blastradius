"""Attrition funnels on hand-built frames and a real RawStore under tmp_path."""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.attrition_funnel import has_failed_job_log, nest, pr_chain, render, repo_chain, run_chain
from src.harvest.rawstore import RawRecord, RawStore


def stage_frame() -> pd.DataFrame:
    return pd.DataFrame({
        "owner": list("abcdef"), "repo": ["r"] * 6,
        "verdict": ["kept", "kept", "no_ci", "api_error", "no_test_workflow", "kept"]})


def instances_frame() -> pd.DataFrame:
    def row(run_id, repo, pr, conclusion, jobs, job_conc):
        return dict(run_id=run_id, repo=repo, pr_number=pr, run_conclusion=conclusion,
                    job_ids=np.array(jobs), job_conclusions=np.array(job_conc, dtype=object))
    return pd.DataFrame([
        row(1, "a/r", 10, "failure", [101, 102], ["success", "failure"]),
        row(2, "a/r", 10, "success", [103], ["success"]),
        row(3, "b/r", 11, "failure", [104], ["failure"]),
        row(4, "z/r", 12, "failure", [105], ["failure"]),  # repo not in the frame: dropped by nesting
        row(5, "a/r", None, "failure", [106], ["failure"]),  # not a PR run
    ])


def test_repo_chain_follows_the_frame_verdicts_and_nests() -> None:
    sample = pd.DataFrame({"owner": ["a", "b"], "repo": ["r", "r"]})
    chain = nest(repo_chain(stage_frame(), sample, instances_frame(), strict_runs={1}))
    assert [(name, len(m)) for name, m, _ in chain] == [
        ("SEART export", 6),
        ("CI-live (>= 100 runs in 90 days)", 4),   # a..f minus no_ci (c) and api_error (d)
        ("has a test-intent workflow", 3),          # kept: a, b, f
        ("sampled into the frame", 2),
        ("swept (>= 1 run harvested)", 2),          # z/r is swept but was never in the frame
        ("with a failed run", 2),
        ("with a strict instance", 1),
    ]


def test_pr_chain_ignores_runs_without_a_pr() -> None:
    chain = nest(pr_chain(instances_frame(), strict_runs={1}))
    assert [len(m) for _, m, _ in chain] == [3, 3, 1]  # PRs (a/r,10) (b/r,11) (z/r,12); run 5 has no PR


def test_failed_job_log_is_looked_up_in_a_real_raw_store(tmp_path) -> None:
    store = RawStore(tmp_path)
    store.write_records("a/r", "logs", 102, [RawRecord(url="u", status=200, fetched_at="2026-01-01T00:00:00+00:00",
                                                       etag=None, body=b"log")])
    store.write_records("a/r", "logs", 101, [RawRecord(url="u", status=200, fetched_at="2026-01-01T00:00:00+00:00",
                                                       etag=None, body=b"log")])
    rows = {r.run_id: r for r in instances_frame().itertuples()}
    assert has_failed_job_log(rows[1], store)      # job 102 failed and has a log
    assert not has_failed_job_log(rows[3], store)  # job 104 failed, no log on disk
    only_green_log = instances_frame().iloc[[0]].assign(job_ids=[np.array([101])],
                                                        job_conclusions=[np.array(["success"], dtype=object)])
    assert not has_failed_job_log(next(only_green_log.itertuples()), store)  # a log exists but not of a failed job


def test_run_chain_is_nested_and_counts_are_hand_computed(tmp_path) -> None:
    store = RawStore(tmp_path)
    for job in (102, 104):
        store.write_records("a/r" if job == 102 else "b/r", "logs", job,
                            [RawRecord(url="u", status=200, fetched_at="2026-01-01T00:00:00+00:00", etag=None, body=b"l")])
    parsed = pd.DataFrame({"run_id": [1, 3, 99]})  # 99 is not a failed run
    resolution = pd.DataFrame({"run_id": [1, 3, 4], "status": ["exact", "no_base", "exact_green"]})
    base_out = pd.DataFrame({"run_id": [1]})
    chain = nest(run_chain(instances_frame(), parsed, resolution, base_out, strict_runs={1, 4}, store=store))
    assert [(n, len(m)) for n, m, _ in chain] == [
        ("runs discovered", 5), ("failed runs", 4), ("with a failed-job log on disk", 2),
        ("with a parsed head test failure", 2), ("with a resolved base", 1),  # run 3 is no_base
        ("with a known base failure set", 1), ("with >= 1 strict label", 1)]


def test_nesting_never_lets_a_stage_exceed_its_predecessor() -> None:
    chain = nest([("a", {1, 2, 3}, "s"), ("b", {2, 3, 4, 5}, "s"), ("c", {3}, "s")])
    assert [len(m) for _, m, _ in chain] == [3, 2, 1]
    assert chain[1][1] == {2, 3}


def test_render_prints_n_over_d_against_previous_and_first_stage() -> None:
    text = render("Repos", "repos", nest([("a", set(range(10)), "src"), ("b", set(range(5)), "src")]))
    assert "| b | 5 | 5/10 (50.00%) | 5/10 (50.00%) | src |" in text
    assert "| a | 10 | - | - | src |" in text
