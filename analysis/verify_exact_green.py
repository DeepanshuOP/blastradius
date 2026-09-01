"""Verify every `exact_green` base run by actually parsing its logs.

Phase 016-A established that `exact_green` is assigned from the base run's
`conclusion == "success"` field alone, without ever reading a base log. Per
ROADMAP §21.3 and integrity invariant 6, a base run with no parsed test results
is `no_base` and emits nothing — a successful run that executed a linter and no
tests is not evidence that the failing head tests were ever green.

This script re-derives the verdict from evidence. For each `exact_green` base
run it enumerates EVERY job (`fetch_all_jobs`, paginated to `total_count`),
fetches every job log it can, classifies each log, and unions the per-job
verdicts per D-12.

Job metadata does not expire; job logs 410 at 90 days. That asymmetry is the
difference between "we know" and "we cannot know", so it is recorded in the
data rather than in a footnote: `base_jobs_total` versus `base_jobs_retrieved`,
and a `base_parse_status` that never merges a confirmed verdict with an
unverifiable one.

`base_parse_status` values, and the `new_status` each implies:

===========================  ==================  =====================================
base_parse_status            new_status          meaning
===========================  ==================  =====================================
green_verified               exact_green         every job retrieved, tests ran, none failed
green_verified_partial       exact_green         some jobs 410, tests ran in what was read
base_failed                  exact               a test failed: the base was never green
no_tests_confirmed           no_base             every job retrieved, zero tests anywhere
no_tests_unverifiable        no_base             some jobs 410, zero tests in what was read
unretrievable                no_base             every job log was fetched; none readable
inferred_expired             no_base             ONE probed job log 410'd; rest INFERRED expired
oversize_unread              no_base             log(s) exceeded the 15 MB ceiling: retrievable but unread
not_processed                exact_green         time budget expired before this run
===========================  ==================  =====================================

`no_tests_confirmed` and the unverifiable statuses all demote per invariant 6,
but they are different epistemic claims and must never be summed into one
number. The datasheet reports them separately.

`inferred_expired` is kept apart from `unretrievable` for the same reason. It
rests on log retention being per-RUN, not per-job — measured before use over 33
qualifying runs drawn at three disjoint offsets (32 all-410, 1 410+404, **0
mixed**), including four 27-job apache/beam runs whose logs expired together.
`classify_retention` is unit-tested to prove the MIXED branch is reachable, so
that zero is measured rather than structural. It is still an inference, and it
is labelled as one in the data.

Importing this module has no side effects. Run it with::

    uv run --env-file .env python analysis/verify_exact_green.py [--limit N] [--as-of ISO8601]
"""

from __future__ import annotations

import argparse
import datetime
import json
import time
from typing import Any

import pandas as pd
import requests

from analysis.fetch_base_logs import fetch_all_jobs
from src.harvest.ratelimit import TokenPool, get_with_backoff
from src.harvest.rawstore import RawRecord, RawStore
from src.parse.dispatch import classify_dispatch_log

RESOLUTION_PARQUETS = (
    "data/interim/base_resolution_targeted.parquet",
    "data/interim/base_resolution_new.parquet",
)
DEFAULT_OUT = "data/interim/exact_green_verification.parquet"

#: 45 minutes, per the network-harvesting runtime budget.
DEFAULT_TIME_BUDGET_S = 45 * 60

STATUS_TO_NEW_STATUS = {
    "green_verified": "exact_green",
    "green_verified_partial": "exact_green",
    "base_failed": "exact",
    "no_tests_confirmed": "no_base",
    "no_tests_unverifiable": "no_base",
    "unretrievable": "no_base",
    "inferred_expired": "no_base",
    "oversize_unread": "no_base",
    "not_processed": "exact_green",
}


def load_exact_green_instances() -> pd.DataFrame:
    """Load every instance currently carrying `status == "exact_green"`.

    Returns:
        One row per (repo, run_id) with its `base_run_id`.
    """
    frames = [pd.read_parquet(p) for p in RESOLUTION_PARQUETS]
    res = pd.concat(frames, ignore_index=True)
    eg = res[res["status"] == "exact_green"].copy()
    eg = eg.dropna(subset=["base_run_id"])
    eg["base_run_id"] = eg["base_run_id"].astype("int64")
    return eg.drop_duplicates(subset=["repo", "run_id"])[
        ["repo", "run_id", "base_run_id"]
    ]


def order_base_runs(eg: pd.DataFrame, python_first: bool = True) -> pd.DataFrame:
    """Reduce instances to distinct base runs, Python first per D-40.

    Args:
        eg: Instance-level frame from :func:`load_exact_green_instances`.
        python_first: Order Python base runs ahead of every other language.

    Returns:
        One row per (repo, base_run_id) with a `language` column.
    """
    inst = pd.read_parquet("data/interim/instances_raw.parquet")
    inst = inst.drop_duplicates("run_id")[["run_id", "repo", "language"]]
    merged = eg.merge(inst, on=["run_id", "repo"], how="left")

    runs = merged.drop_duplicates(subset=["repo", "base_run_id"])[
        ["repo", "base_run_id", "language"]
    ].copy()
    if python_first:
        runs["__order"] = (runs["language"] != "Python").astype(int)
        runs = runs.sort_values(["__order", "repo", "base_run_id"]).drop(columns="__order")
    return runs.reset_index(drop=True)


def head_ran_tests_map() -> dict[int, bool]:
    """Which head runs produced any parsed test outcome at all.

    An instance whose head run ran no tests should never have entered the
    corpus; this makes that countable rather than anecdotal.

    Returns:
        Mapping of head `run_id` to whether any outcome was parsed for it.
    """
    parsed = pd.read_parquet("data/interim/parsed_outcomes.parquet")
    return {int(r): True for r in parsed["run_id"].dropna().unique()}


def classify_base_run(
    repo: str,
    base_run_id: int,
    pool: TokenPool,
    store: RawStore,
    stats: dict[str, Any],
) -> dict[str, Any]:
    """Enumerate, fetch and classify every job of one base run.

    Args:
        repo: Owner/name slug.
        base_run_id: The base workflow run to verify.
        pool: Token pool for `get_with_backoff`.
        store: Raw store; cached job logs are reused rather than re-fetched.
        stats: Mutable counters updated in place.

    Returns:
        Dict with `base_parse_status`, `base_jobs_total`, `base_jobs_retrieved`.
    """
    jobs, http_status, reqs = fetch_all_jobs(repo, base_run_id, pool)
    stats["requests"] += reqs

    if http_status != 200 or not jobs:
        stats[f"jobs_meta_{http_status}"] = stats.get(f"jobs_meta_{http_status}", 0) + 1
        return {
            "base_parse_status": "unretrievable",
            "base_jobs_total": len(jobs),
            "base_jobs_retrieved": 0,
        }

    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{base_run_id}/jobs"
    if not store.exists(repo, "jobs", int(base_run_id)):
        store.write_records(
            repo,
            "jobs",
            int(base_run_id),
            [
                RawRecord(
                    url=jobs_url,
                    status=http_status,
                    fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    etag=None,
                    body=json.dumps({"total_count": len(jobs), "jobs": jobs}).encode("utf-8"),
                )
            ],
        )

    # Probe-then-infer: if the FIRST job log has expired, every log of the run
    # has (measured: per-run retention, 33/33 runs, 0 mixed). Recorded as
    # `inferred_expired`, never as the measured `unretrievable`.
    if len(jobs) > 1 and not store.exists(repo, "logs", int(jobs[0]["id"])):
        probe_url = f"https://api.github.com/repos/{repo}/actions/jobs/{int(jobs[0]['id'])}/logs"
        probe_status = None
        try:
            probe_resp = get_with_backoff(probe_url, pool=pool)
            probe_status = probe_resp.status_code
        except requests.HTTPError as exc:
            probe_status = exc.response.status_code if exc.response is not None else 0
        except Exception:
            probe_status = None
        stats["requests"] += 1
        if probe_status == 410:
            stats["inferred_expired_runs"] = stats.get("inferred_expired_runs", 0) + 1
            stats["inferred_expired_jobs_skipped"] = (
                stats.get("inferred_expired_jobs_skipped", 0) + len(jobs) - 1
            )
            return {
                "base_parse_status": "inferred_expired",
                "base_jobs_total": len(jobs),
                "base_jobs_retrieved": 0,
            }

    retrieved = 0
    oversize = 0
    saw_tests = False
    saw_failure = False

    for job in jobs:
        job_id = int(job["id"])
        body_text = None

        if store.exists(repo, "logs", job_id):
            try:
                recs = store.read_records(repo, "logs", job_id)
                if recs and recs[0].body:
                    body_text = recs[0].body.decode("utf-8", errors="replace")
                    stats["logs_cached"] += 1
            except Exception:
                body_text = None

        if body_text is None:
            log_url = f"https://api.github.com/repos/{repo}/actions/jobs/{job_id}/logs"
            try:
                resp = get_with_backoff(log_url, pool=pool)
                log_status = resp.status_code
            except requests.HTTPError as exc:
                # get_with_backoff RAISES on non-retryable 4xx (404, 410, ...)
                # rather than returning the response. A 410 is an expired log:
                # the run is real, we simply cannot read it, ever.
                resp = None
                log_status = exc.response.status_code if exc.response is not None else 0
            except Exception as exc:
                # Record WHICH failure. A 15 MB ByteCeilingExceeded is a
                # retrievable log we chose not to hold, not an expired one, and
                # collapsing the two would misreport the unverifiable count.
                key = f"err_{type(exc).__name__}"
                stats[key] = stats.get(key, 0) + 1
                stats["err"] += 1
                if type(exc).__name__ == "ByteCeilingExceeded":
                    # Retrievable but unread: neither expired nor measured.
                    oversize += 1
                continue
            stats["requests"] += 1
            stats[f"log_{log_status}"] = stats.get(f"log_{log_status}", 0) + 1
            if resp is None or log_status != 200:
                continue
            store.write_records(
                repo,
                "logs",
                job_id,
                [
                    RawRecord(
                        url=log_url,
                        status=resp.status_code,
                        fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        etag=resp.headers.get("etag"),
                        body=resp.content,
                    )
                ],
            )
            body_text = resp.content.decode("utf-8", errors="replace")
            stats["logs_fetched"] += 1

        retrieved += 1
        try:
            classification, _failing, _trunc = classify_dispatch_log(body_text)
        except Exception:
            stats["unreadable"] += 1
            continue

        # D-12: union across legs. One failing leg makes the base non-green;
        # one leg that ran tests makes the base test-bearing.
        if classification == "TEST_FAILURE":
            saw_failure = True
            saw_tests = True
        elif classification == "TEST_RAN_CLEAN":
            saw_tests = True

    complete = retrieved == len(jobs)

    unread = len(jobs) - retrieved

    if saw_failure:
        status = "base_failed"
    elif saw_tests:
        status = "green_verified" if complete else "green_verified_partial"
    elif unread > 0 and oversize == unread:
        # Every unread job was over the 15 MB ceiling, not expired. We declined
        # to hold those bytes; that is our limit, not GitHub's retention.
        status = "oversize_unread"
    elif retrieved == 0:
        status = "unretrievable"
    elif complete:
        status = "no_tests_confirmed"
    else:
        status = "no_tests_unverifiable"

    return {
        "base_parse_status": status,
        "base_jobs_total": len(jobs),
        "base_jobs_retrieved": retrieved,
    }


def load_checkpoint(out_parquet: str | None) -> dict[tuple[str, int], dict[str, Any]]:
    """Recover already-verified base runs from a previous slice.

    The sweep is resumable so it can run as bounded foreground slices on a VM
    that has died mid-run before. Only rows carrying a real verdict are
    restored; `not_processed` rows are left to be redone.

    Args:
        out_parquet: Path written by a previous run, or None.

    Returns:
        Mapping of (repo, base_run_id) to its recorded verdict fields.
    """
    if not out_parquet:
        return {}
    try:
        prior = pd.read_parquet(out_parquet)
    except (FileNotFoundError, OSError):
        return {}

    done = prior[prior["base_parse_status"] != "not_processed"]
    verdicts: dict[tuple[str, int], dict[str, Any]] = {}
    for r in done.drop_duplicates(subset=["repo", "base_run_id"]).itertuples():
        verdicts[(r.repo, int(r.base_run_id))] = {
            "base_parse_status": r.base_parse_status,
            "base_jobs_total": int(r.base_jobs_total),
            "base_jobs_retrieved": int(r.base_jobs_retrieved),
        }
    return verdicts


def sample_unswept_java(
    runs: pd.DataFrame,
    verified_keys: set[tuple[str, int]],
    n: int,
    seed: int,
) -> pd.DataFrame:
    """Draw a RANDOM sample of not-yet-verified Java base runs.

    Checkpoint order is not random — it is repo- and id-sorted, so extending the
    sweep by taking the next N biases the sample toward whatever that ordering
    favours (in practice, `apache/beam`). Sampling instead makes the Java arm an
    estimate with a defensible confidence interval.

    Args:
        runs: Ordered base-run frame from :func:`order_base_runs`.
        verified_keys: (repo, base_run_id) pairs already verified.
        n: Number of unswept Java runs to draw.
        seed: RNG seed, stated in the report so the draw is reproducible.

    Returns:
        The sampled rows, plus every already-verified run so resumption still
        skips them.
    """
    java = runs[runs["language"] == "Java"].copy()
    unswept = java[
        ~java.apply(lambda r: (r["repo"], int(r["base_run_id"])) in verified_keys, axis=1)
    ]
    take = min(n, len(unswept))
    drawn = unswept.sample(n=take, random_state=seed)
    print(f"random sample: {take} of {len(unswept)} unswept Java base runs (seed={seed})")
    already = runs[
        runs.apply(lambda r: (r["repo"], int(r["base_run_id"])) in verified_keys, axis=1)
    ]
    return pd.concat([already, drawn], ignore_index=True)


def run(
    as_of: str | None = None,
    limit: int | None = None,
    python_first: bool = True,
    time_budget_s: float = DEFAULT_TIME_BUDGET_S,
    out_parquet: str | None = DEFAULT_OUT,
    resume: bool = True,
    sample_java: int | None = None,
    seed: int = 20260901,
    pool: TokenPool | None = None,
    store: RawStore | None = None,
) -> pd.DataFrame:
    """Verify every `exact_green` base run and write the per-instance verdicts.

    Args:
        as_of: Recorded on every row for provenance; does not filter.
        limit: Process at most this many distinct base runs.
        python_first: Order Python base runs first, per D-40.
        time_budget_s: Wall-clock cap. Unprocessed runs are reported, never guessed.
        out_parquet: Destination parquet, or None to skip writing.
        resume: Skip base runs already verified in `out_parquet`.
        sample_java: Draw this many unswept Java runs at random instead of
            continuing in checkpoint order.
        seed: RNG seed for that draw.
        pool: Token pool; built from the environment when omitted.
        store: Raw store; a default one is built when omitted.

    Returns:
        One row per `exact_green` instance with its verified status.
    """
    eg = load_exact_green_instances()
    runs = order_base_runs(eg, python_first=python_first)

    if sample_java:
        prior = load_checkpoint(out_parquet) if resume else {}
        runs = sample_unswept_java(runs, set(prior), sample_java, seed)

    if limit is not None:
        runs = runs.head(limit)

    print(f"exact_green instances:        {len(eg)}")
    print(f"distinct base runs to verify: {len(runs)}")
    print(runs["language"].value_counts(dropna=False).to_string())

    pool = pool or TokenPool.from_env()
    store = store or RawStore()

    stats: dict[str, Any] = {
        "requests": 0,
        "logs_fetched": 0,
        "logs_cached": 0,
        "unreadable": 0,
        "err": 0,
    }

    # ---- Stage A: enumerate every job of every base run -------------------
    # Job metadata does not expire, so this stage always completes and gives a
    # MEASURED job count before any log budget is committed.
    verdicts: dict[tuple[str, int], dict[str, Any]] = (
        load_checkpoint(out_parquet) if resume else {}
    )
    already = len(verdicts)
    print(f"resumed from checkpoint:      {already} base runs already verified")

    head_tests = head_ran_tests_map()

    def build_frame() -> pd.DataFrame:
        """Expand the current base-run verdicts back to one row per instance."""
        unprocessed = {
            "base_parse_status": "not_processed",
            "base_jobs_total": 0,
            "base_jobs_retrieved": 0,
        }
        rows = []
        for r in eg.itertuples():
            v = verdicts.get((r.repo, int(r.base_run_id)), unprocessed)
            rows.append(
                {
                    "repo": r.repo,
                    "run_id": int(r.run_id),
                    "base_run_id": int(r.base_run_id),
                    "base_parse_status": v["base_parse_status"],
                    "base_jobs_total": int(v["base_jobs_total"]),
                    "base_jobs_retrieved": int(v["base_jobs_retrieved"]),
                    "new_status": STATUS_TO_NEW_STATUS[v["base_parse_status"]],
                    "head_ran_tests": bool(head_tests.get(int(r.run_id), False)),
                    "as_of": as_of,
                }
            )
        return pd.DataFrame(rows)

    start = time.time()
    processed = 0

    for row in runs.itertuples():
        key = (row.repo, int(row.base_run_id))
        if key in verdicts:
            continue

        elapsed = time.time() - start
        if elapsed > time_budget_s:
            print(f"\nTIME BUDGET REACHED at {elapsed/60:.1f} min after {processed} base runs this slice.")
            break

        verdicts[key] = classify_base_run(
            row.repo, int(row.base_run_id), pool, store, stats
        )
        processed += 1

        # Checkpoint often. A single base run with many large logs can overrun
        # the budget check between iterations and be killed by an outer
        # timeout; without this, the whole slice's fetches are lost.
        if out_parquet and processed % 25 == 0:
            build_frame().to_parquet(out_parquet, index=False)

        if processed % 100 == 0:
            elapsed = time.time() - start
            rpm = stats["requests"] / (elapsed / 60) if elapsed else 0.0
            print(
                f"Heartbeat: {len(verdicts)}/{len(runs)} base runs "
                f"({processed} this slice) | {elapsed/60:.1f} min | "
                f"{stats['requests']} req | {rpm:.1f} req/min | "
                f"logs {stats['logs_fetched']} fetched / {stats['logs_cached']} cached"
            )

    print(f"\nBase runs verified: {len(verdicts)} / {len(runs)}  ({processed} this slice)")
    print(f"Stats: {stats}")

    total_jobs = sum(v["base_jobs_total"] for v in verdicts.values())
    retrieved_jobs = sum(v["base_jobs_retrieved"] for v in verdicts.values())
    print(f"MEASURED total jobs across processed base runs: {total_jobs}")
    print(f"MEASURED job logs retrieved:                    {retrieved_jobs}")

    # ---- Expand base-run verdicts back to instances -----------------------
    out = build_frame()

    print("\n--- base_parse_status, instance-weighted ---")
    for status, n in out["base_parse_status"].value_counts().items():
        print(f"  {status:<24} {n} / {len(out)}")
    print("\n--- new_status, instance-weighted ---")
    for status, n in out["new_status"].value_counts().items():
        print(f"  {status:<24} {n} / {len(out)}")
    print(f"\nhead_ran_tests == False: {int((~out['head_ran_tests']).sum())} / {len(out)}")

    if out_parquet:
        out.to_parquet(out_parquet, index=False)
        print(f"\nWrote {out_parquet} ({len(out)} rows)")

    return out


#: base_parse_status values that mean "we read every job we needed to".
CONFIRMED_STATUSES = ("green_verified", "no_tests_confirmed", "base_failed")


def report(path: str = DEFAULT_OUT) -> pd.DataFrame:
    """Print the six buckets as fractions with both numbers written out.

    CONFIRMED and UNVERIFIABLE demotions are never summed: they demote alike
    under invariant 6 but they are different epistemic claims, and the
    datasheet reports them separately.

    Args:
        path: Verification parquet written by :func:`run`.

    Returns:
        The verified subset of the frame (excludes `not_processed`).
    """
    df = pd.read_parquet(path)
    inst = pd.read_parquet("data/interim/instances_raw.parquet")
    inst = inst.drop_duplicates("run_id")[["run_id", "repo", "language", "workflow_name"]]
    df = df.merge(inst, on=["run_id", "repo"], how="left")

    verified = df[df["base_parse_status"] != "not_processed"]
    n_all, n_ver = len(df), len(verified)

    print("=" * 78)
    print("EXACT_GREEN VERIFICATION")
    print("=" * 78)
    print(f"exact_green instances in corpus:        {n_all}")
    print(f"instances covered by the sweep:         {n_ver} / {n_all} ({n_ver/n_all:.1%})")

    runs_all = df.drop_duplicates(subset=["repo", "base_run_id"])
    runs_ver = verified.drop_duplicates(subset=["repo", "base_run_id"])
    print(f"distinct base runs in corpus:           {len(runs_all)}")
    print(f"distinct base runs verified:            {len(runs_ver)} / {len(runs_all)} "
          f"({len(runs_ver)/len(runs_all):.1%})")

    print("\n-- sweep coverage by language (base runs, D-40 ordered Python first) --")
    for lang, grp in runs_all.groupby("language", dropna=False):
        done = len(grp[grp["base_parse_status"] != "not_processed"])
        print(f"  {str(lang):<10} {done} / {len(grp)} ({done/len(grp):.1%})")

    print(f"\n-- the six buckets, instance-weighted over the {n_ver} VERIFIED instances --")
    order = [
        ("green_verified", "retrievable(all jobs) + TEST_RAN_CLEAN", "stays exact_green"),
        ("green_verified_partial", "partial + tests found in retrieved legs", "stays exact_green"),
        ("base_failed", "retrievable + TEST_FAILURE", "reclassify as `exact`"),
        ("no_tests_confirmed", "retrievable(all jobs) + NO_TEST_OUTPUT", "demote, CONFIRMED test-free"),
        ("no_tests_unverifiable", "partial + no tests in retrieved legs", "demote, UNVERIFIABLE"),
        ("unretrievable", "all jobs 410 (every job fetched)", "demote, UNVERIFIABLE"),
        ("inferred_expired", "probe 410 -> rest INFERRED expired", "demote, INFERRED"),
        ("oversize_unread", "log over 15 MB ceiling: unread, not expired", "demote, UNREAD"),
    ]
    counts = verified["base_parse_status"].value_counts().to_dict()
    for key, label, consequence in order:
        n = counts.get(key, 0)
        pct = f"{n/n_ver:.1%}" if n_ver else "n/a"
        print(f"  {label:<42} {n} / {n_ver} ({pct:>6})  -> {consequence}")

    confirmed = counts.get("no_tests_confirmed", 0)
    unverifiable = sum(counts.get(k, 0) for k in ("no_tests_unverifiable", "unretrievable"))
    inferred = counts.get("inferred_expired", 0)
    print(f"\n  demotions, CONFIRMED test-free:       {confirmed} / {n_ver}")
    print(f"  demotions, UNVERIFIABLE (measured):   {unverifiable} / {n_ver}")
    print(f"  demotions, INFERRED expired:          {inferred} / {n_ver}")
    print("  (never summed: three different epistemic claims)")

    print("\n-- 410 exposure, both bases --")
    ur_inst = counts.get("unretrievable", 0)
    ur_runs = len(runs_ver[runs_ver["base_parse_status"] == "unretrievable"])
    print(f"  instance-weighted: {ur_inst} / {n_ver} ({ur_inst/n_ver:.1%}) fully unretrievable")
    print(f"  run-weighted:      {ur_runs} / {len(runs_ver)} ({ur_runs/len(runs_ver):.1%}) fully unretrievable")

    print("\n-- job retrievability --")
    jt = int(verified.drop_duplicates(subset=["repo", "base_run_id"])["base_jobs_total"].sum())
    jr = int(verified.drop_duplicates(subset=["repo", "base_run_id"])["base_jobs_retrieved"].sum())
    print(f"  jobs enumerated (metadata never expires): {jt}")
    print(f"  job logs retrieved (logs expire at 90d):  {jr} / {jt} ({jr/jt:.1%})" if jt else "  none")

    print("\n-- head_ran_tests --")
    no_head = int((~df["head_ran_tests"]).sum())
    print(f"  exact_green instances whose HEAD run parsed zero tests: {no_head} / {n_all} ({no_head/n_all:.1%})")

    # ---- 2c: what the every-job fix reversed ------------------------------
    # The old base-side path skipped every job whose conclusion was not
    # "failure". Measure, from the stored job payloads, how many verified base
    # runs contain zero such jobs: for those the old path parsed nothing and
    # NO_TEST_OUTPUT was its guaranteed verdict.
    store = RawStore()
    zero_failure_runs = set()
    missing_payload = 0
    for r in runs_ver.itertuples():
        try:
            recs = store.read_records(r.repo, "jobs", int(r.base_run_id))
        except Exception:
            recs = []
        if not recs or not recs[0].body:
            missing_payload += 1
            continue
        jobs = json.loads(recs[0].body.decode("utf-8")).get("jobs", [])
        if not any(j.get("conclusion") == "failure" for j in jobs):
            zero_failure_runs.add((r.repo, int(r.base_run_id)))

    in_zero = verified[
        verified.apply(lambda x: (x["repo"], int(x["base_run_id"])) in zero_failure_runs, axis=1)
    ]
    reversed_rows = in_zero[in_zero["new_status"] != "no_base"]

    print("\n-- 2c: demotions the every-job fix REVERSED --")
    print(f"  verified base runs with ZERO conclusion=='failure' jobs: "
          f"{len(zero_failure_runs)} / {len(runs_ver)}")
    if missing_payload:
        print(f"  (job payload unreadable for {missing_payload} runs, excluded)")
    print(f"  instances the OLD path would have demoted on those runs:  {len(in_zero)}")
    print(f"  instances the every-job fix KEEPS (not demoted):          {len(reversed_rows)}")
    print("  -> that count is the difference between a bug and a finding.")

    return verified


def classify_retention(statuses: list[int]) -> str | None:
    """Classify one run's per-job log HTTP statuses for the retention probe.

    Pure and separately tested, so the "0 MIXED" result the probe reports is a
    measured zero rather than an unreachable branch — see the zero-is-not-
    evidence rule in `docs/AGENT_RULES.md`.

    Args:
        statuses: HTTP status per job log of a single run.

    Returns:
        ``None`` if the run does not qualify (no 410 present), else
        ``"all_410"``, ``"expired_404"``, or ``"MIXED"``. MIXED means a readable
        log survived alongside an expired one, which makes one-probe inference
        unsound.
    """
    if 410 not in statuses:
        return None
    if all(s == 410 for s in statuses):
        return "all_410"
    if 200 in statuses:
        return "MIXED"
    return "expired_404"


def probe_retention(sample: int = 30, language: str = "Java", offset: int = 0) -> dict[str, Any]:
    """Test whether GitHub Actions log expiry is per-RUN or per-JOB.

    The probe-then-infer optimisation rests on the claim that if one job log of
    a run has expired, all of them have. That claim is load-bearing — it would
    let one request stand in for eleven — so it is measured, not assumed.

    Samples base runs until `sample` of them have at least one job log return
    410, fetching EVERY job log of each. A run is classified:

    * ``all_410``      — every job returned 410. Inference safe.
    * ``expired_404``  — 410s plus 404s, no 200. Still unreadable; the 404 root
      cause is a separate known defect.
    * ``MIXED``        — at least one 410 AND at least one 200. **The inference
      is unsound if this is non-zero**: a readable job survived alongside an
      expired one, so one probe cannot speak for the run.

    Args:
        sample: Number of qualifying runs to collect.
        language: Language arm to sample from.
        offset: Skip this many candidate runs first, so successive calls draw
            disjoint samples instead of re-probing the same prefix.

    Returns:
        Counts per class plus the qualifying-run total.
    """
    eg = load_exact_green_instances()
    runs = order_base_runs(eg, python_first=False)
    inst = pd.read_parquet("data/interim/instances_raw.parquet")
    inst = inst.drop_duplicates("run_id")[["run_id", "repo", "language"]]
    runs = runs[runs["language"] == language].iloc[offset:]

    pool = TokenPool.from_env()
    store = RawStore()

    classes = {"all_410": 0, "expired_404": 0, "MIXED": 0}
    mixed_examples: list[str] = []
    qualifying = 0
    scanned = 0

    for row in runs.itertuples():
        if qualifying >= sample:
            break
        scanned += 1
        jobs, http_status, _ = fetch_all_jobs(row.repo, int(row.base_run_id), pool)
        if http_status != 200 or not jobs:
            continue

        statuses: list[int] = []
        for job in jobs:
            job_id = int(job["id"])
            url = f"https://api.github.com/repos/{row.repo}/actions/jobs/{job_id}/logs"
            try:
                resp = get_with_backoff(url, pool=pool)
                statuses.append(resp.status_code)
            except requests.HTTPError as exc:
                statuses.append(exc.response.status_code if exc.response is not None else 0)
            except Exception:
                statuses.append(0)

        cls = classify_retention(statuses)
        if cls is None:
            continue

        qualifying += 1
        classes[cls] += 1
        if cls == "MIXED":
            mixed_examples.append(f"{row.repo} run {row.base_run_id}: {statuses}")

        print(
            f"[{qualifying}/{sample}] {row.repo} run {row.base_run_id}: "
            f"{len(jobs)} jobs, statuses={sorted(set(statuses))}"
        )

    print("\n--- PER-RUN LOG RETENTION PROBE ---")
    print(f"runs scanned to find qualifying ones: {scanned}")
    print(f"qualifying runs (>=1 job log 410):    {qualifying}")
    for k in ("all_410", "expired_404", "MIXED"):
        print(f"  {k:<14} {classes[k]} / {qualifying}")
    if classes["MIXED"]:
        print("\nINFERENCE UNSOUND — mixed runs found:")
        for e in mixed_examples[:10]:
            print(f"  {e}")
    else:
        print("\nInference SAFE on this sample: no run mixed an expired log with a readable one.")

    return {"qualifying": qualifying, "scanned": scanned, **classes}


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--as-of", type=str, help="ISO-8601 UTC pin, recorded on every row")
    parser.add_argument("--limit", type=int, help="Limit number of distinct base runs")
    parser.add_argument(
        "--time-budget-s",
        type=float,
        default=DEFAULT_TIME_BUDGET_S,
        help="Wall-clock cap in seconds (default 2700 = 45 min)",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, help="Destination parquet")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Re-verify every base run instead of resuming from --out",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Print the buckets from an existing --out; issue no HTTP requests",
    )
    parser.add_argument(
        "--probe-retention",
        type=int,
        metavar="N",
        help="Test whether log expiry is per-run: sample N runs with >=1 410 job log",
    )
    parser.add_argument(
        "--sample-java",
        type=int,
        metavar="N",
        help="Randomly sample N unswept Java base runs instead of checkpoint order",
    )
    parser.add_argument(
        "--seed", type=int, default=20260901, help="RNG seed for --sample-java"
    )
    parser.add_argument(
        "--probe-offset",
        type=int,
        default=0,
        help="Skip this many candidate runs, for a disjoint follow-up sample",
    )
    args = parser.parse_args()

    if args.report_only:
        report(args.out)
        return

    if args.probe_retention:
        probe_retention(sample=args.probe_retention, offset=args.probe_offset)
        return

    run(
        as_of=args.as_of,
        limit=args.limit,
        time_budget_s=args.time_budget_s,
        out_parquet=args.out,
        resume=not args.no_resume,
        sample_java=args.sample_java,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
