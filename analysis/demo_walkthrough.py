"""Plain-language walkthrough of ONE strict instance, end to end.

Read-only, offline and deterministic. It reads `data/interim/*.parquet`, the
local `RawStore` and the graph store; it writes nothing under the repository, makes no
network call (git lazy fetch is disabled) and uses no randomness: candidates
are ordered by `(repo, pr_number, run_id, test_id)` and the first that clears
every gate is shown.

Gates, in order (the counts that survive each are printed):
  1. strict label, in a repo listed in `docs/MINI_CORPUS.md`
  2. the failing test binds to a test file (`binding.parquet`, status `exact`)
  3. no head job of the run is a holdout log (never shown, never parsed here)
  4. the raw log of the failing job is in the local RawStore
  5. a graph exists at the resolved base SHA in `data/graphs/`, or (the default
     when it does not) the tree is fully local so the graph can be built

Among the instances that clear gates 1-4, the failing test's failure message is
classified (`analysis/failure_class.py`) and a code-level failure (assertion or
expected-vs-actual) is preferred over an unknown one, then a timeout, then a strict
environment failure (CUDA/GPU unavailable, OOM, connection or DNS error, missing
service). The classification is printed in the selection report.

A missing graph is built by default, in a throw-away temp dir from local git
objects only (`GIT_NO_LAZY_FETCH=1`; the corpus clones are `--filter=blob:none`,
so a tree with missing blobs is skipped, never fetched), and the output says
so. `--no-build-graph` restores the strict "graph must already be in
`data/graphs/`" behaviour; `--build-graph-offline` is accepted and is now a no-op.

Exit status: 0 walkthrough printed; 2 no instance cleared the gates.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd

from analysis.failure_class import CODE, ENVIRONMENT, TIMEOUT, UNKNOWN, classify

MINI_CORPUS_DOC = Path("docs/MINI_CORPUS.md")
HOLDOUT_EXCLUSION = Path("docs/session/holdout-exclusion.txt")
HOLDOUT_FIXTURE_GLOB = "tests/fixtures/holdout*/*.txt"
INTERIM = Path("data/interim")
GRAPH_DIR = Path("data/graphs")
MAX_LOG_LINES = 10
MAX_LINE_CHARS = 200
COCHANGE_K = 10

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_FAIL_WORDS = re.compile(r"FAIL|ERROR|Error|error|<<<|Exception|assert", re.IGNORECASE)


@dataclass(frozen=True)
class Candidate:
    """One instance that cleared every gate."""

    repo: str
    pr: int
    run_id: int
    head_sha: str
    base_sha: str
    test_id: str
    job_id: int
    graph_dir: Path | None  # None: built offline into a temp dir
    failure_message: str = ""
    failure_class: str = UNKNOWN
    failure_rule: str = "empty"


def mini_corpus_repos(doc: Path = MINI_CORPUS_DOC) -> list[str]:
    """Read the selected repos out of the `Selected repos` table of the doc.

    Args:
        doc: Path to `docs/MINI_CORPUS.md`.

    Returns:
        Sorted `owner/name` slugs.
    """
    text = doc.read_text(encoding="utf-8")
    section = text.split("## Selected repos", 1)[1].split("\n## ", 1)[0]
    repos = re.findall(r"^\|[^|]*\|\s*`([\w.-]+/[\w.-]+)`", section, re.MULTILINE)
    return sorted(set(repos))


def holdout_job_ids(
    fixture_glob: str = HOLDOUT_FIXTURE_GLOB, exclusion: Path = HOLDOUT_EXCLUSION
) -> tuple[set[int], bool]:
    """Collect every job id that belongs to a holdout log.

    Only file NAMES under the holdout fixture directories are read (the trailing
    job id), never their contents, plus the integers in the exclusion file when
    that file exists on this machine.

    Args:
        fixture_glob: Glob of holdout fixture logs, relative to the repo root.
        exclusion: The operator's exclusion list.

    Returns:
        `(job_ids, exclusion_file_present)`.
    """
    ids = {
        int(m.group(1))
        for p in Path(".").glob(fixture_glob)
        if (m := re.search(r"__(\d{9,})\.txt$", p.name))
    }
    present = exclusion.exists()
    if present:
        ids |= {int(x) for x in re.findall(r"\b(\d{9,})\b", exclusion.read_text("utf-8"))}
    return ids, present


def short_name(test_id: str) -> str:
    """The method/function token a log line would carry for `test_id`.

    Args:
        test_id: Canonical `file::name[params]` or `pkg.Class#method[params]`.

    Returns:
        The last name component with any parameter suffix removed.
    """
    tail = re.split(r"::|#", test_id)[-1]
    return tail.split("[", 1)[0].strip()


def log_excerpt(body: str, test_id: str, limit: int = MAX_LOG_LINES) -> list[str]:
    """Pick up to `limit` raw log lines that show `test_id` failing.

    Lines naming the test AND carrying a failure word come first, in file order;
    lines that only name the test fill the remainder. ANSI colour is removed and
    long lines are cut, nothing else is altered.

    Args:
        body: Decoded job log.
        test_id: The failing test.
        limit: Maximum lines.

    Returns:
        The selected lines.
    """
    name = short_name(test_id)
    lines = [_ANSI.sub("", ln).rstrip() for ln in body.splitlines()]
    hits = [ln for ln in lines if name and name in ln]
    strong = [ln for ln in hits if _FAIL_WORDS.search(ln)]
    weak = [ln for ln in hits if ln not in strong]
    return [ln[:MAX_LINE_CHARS] for ln in (strong + weak)[:limit]]


def tree_is_local(clone: Path, sha: str) -> bool:
    """True when every blob of `sha`'s tree is already in the local object store.

    Args:
        clone: Clone directory.
        sha: Commit.

    Returns:
        False when the commit or any blob is missing (never fetches).
    """
    env = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}
    ls = subprocess.run(
        ["git", "-C", str(clone), "ls-tree", "-r", sha],
        capture_output=True, text=True, env=env,
    )
    if ls.returncode != 0:
        return False
    blobs = [ln.split()[2] for ln in ls.stdout.splitlines() if ln.split()[1] == "blob"]
    chk = subprocess.run(
        ["git", "-C", str(clone), "cat-file", "--batch-check"],
        input="\n".join(blobs) + "\n", capture_output=True, text=True, env=env,
    )
    return chk.returncode == 0 and " missing" not in chk.stdout


def clone_dir(repo: str) -> Path:
    """Clone location for `repo`."""
    return Path("data/clones") / repo.replace("/", "__")


def _read(name: str) -> pd.DataFrame:
    return duckdb.sql(f"select * from read_parquet('{INTERIM / name}.parquet')").df()


def gated_rows() -> tuple[pd.DataFrame, list[str]]:
    """Apply gates 1-4 and classify the failure message of every surviving row.

    Returns:
        `(rows, report_lines)`: one row per (label, job) that cleared gates 1-4,
        sorted by preference `(rank, repo, pr_number, run_id, test_id, job_id)`,
        with `failure_class`, `failure_rule` and `rank` columns.
    """
    from src.harvest.rawstore import RawStore

    report: list[str] = []
    repos = mini_corpus_repos()
    holdout, present = holdout_job_ids()
    report.append(f"mini-corpus repos (docs/MINI_CORPUS.md): {', '.join(repos)}")
    report.append(
        f"holdout exclusion: {len(holdout)} job ids from tests/fixtures/holdout*/ names"
        + ("" if present else f"; {HOLDOUT_EXCLUSION} ABSENT on this machine, fixture names only")
    )

    out, inst = _read("outcomes"), _read("instances_raw")
    res, bind, par = _read("base_resolution_new"), _read("binding"), _read("parsed_outcomes")

    strict = out[out["split"] == "strict"][["run_id", "test_id"]]
    strict = strict.merge(inst[["run_id", "repo", "pr_number", "head_sha"]], on="run_id")
    strict = strict[strict["repo"].isin(repos)]
    report.append(f"gate 1 strict labels in mini-corpus repos: {len(strict)} labels, "
                  f"{strict['run_id'].nunique()} instances")

    exact = bind[bind["status"] == "exact"][["repo", "test_id"]]
    strict = strict.merge(exact, on=["repo", "test_id"])
    strict = strict.merge(res[res["status"] != "no_base"][["run_id", "base_sha"]], on="run_id")
    strict = strict[strict["base_sha"].notna()]
    report.append(f"gate 2 with a bound test and a resolved base: {len(strict)} labels, "
                  f"{strict['run_id'].nunique()} instances")

    jobs = par[["run_id", "test_id", "job_id", "failure_message"]].copy()
    jobs["failure_message"] = jobs["failure_message"].fillna("")
    jobs = jobs.sort_values(["run_id", "test_id", "job_id", "failure_message"])
    jobs = jobs.drop_duplicates(["run_id", "test_id", "job_id"])
    bad_runs = set(jobs[jobs["job_id"].isin(holdout)]["run_id"])
    strict = strict[~strict["run_id"].isin(bad_runs)]
    report.append(f"gate 3 not touching a holdout job: {strict['run_id'].nunique()} instances")

    strict = strict.merge(jobs, on=["run_id", "test_id"])
    store = RawStore()
    logged = strict[[store.exists(r.repo, "logs", int(r.job_id)) for r in strict.itertuples()]].copy()
    report.append(f"gate 4 raw log in local RawStore: {logged['run_id'].nunique()} instances, "
                  f"{len(logged)} (label, job) rows")

    cls = [classify(m) for m in logged["failure_message"]]
    logged["failure_class"] = [c for c, _ in cls]
    logged["failure_rule"] = [r for _, r in cls]
    counts = logged["failure_class"].value_counts()
    report.append("failure-message classification of those rows (analysis/failure_class.py): "
                  + ", ".join(f"{k} {int(counts.get(k, 0))}/{len(logged)}"
                              for k in (CODE, UNKNOWN, TIMEOUT, ENVIRONMENT)))
    rank = {CODE: 0, UNKNOWN: 1, TIMEOUT: 2, ENVIRONMENT: 3}
    logged["rank"] = logged["failure_class"].map(rank)
    logged = logged.sort_values(["rank", "repo", "pr_number", "run_id", "test_id", "job_id"])
    return logged, report


def find_candidate(build_offline: bool) -> tuple[Candidate | None, list[str]]:
    """Walk the gates in sorted order and return the first instance that clears all.

    Args:
        build_offline: Allow a temp-dir graph when `data/graphs/` has none.

    Returns:
        `(candidate_or_None, report_lines)` where the report names the survivors
        of each gate.
    """
    from src.graph.build import graph_path

    logged, report = gated_rows()
    on_disk = [graph_path(r.repo, r.base_sha, GRAPH_DIR).exists() for r in logged.itertuples()]
    n_graph = int(sum(on_disk))
    report.append(f"gate 5 graph in {GRAPH_DIR}/: {logged[on_disk]['run_id'].nunique()} instances "
                  f"({len(list(GRAPH_DIR.glob('graph_*.json.gz'))) if GRAPH_DIR.exists() else 0} graphs on disk)")
    logged["on_disk"] = on_disk

    local_cache: dict[tuple[str, str], bool] = {}

    def buildable(repo: str, sha: str) -> bool:
        if (repo, sha) not in local_cache:
            local_cache[(repo, sha)] = clone_dir(repo).exists() and tree_is_local(clone_dir(repo), sha)
        return local_cache[(repo, sha)]

    chosen, gdir = None, None
    for rk in (0, 1, 2):
        tier = logged[logged["rank"] == rk]
        graphed = tier[tier["on_disk"]]
        if len(graphed):
            chosen, gdir = graphed.iloc[0], GRAPH_DIR
            break
        if build_offline:
            for row in tier.itertuples():
                if buildable(row.repo, row.base_sha):
                    chosen, gdir = tier.loc[row.Index], None
                    break
            if chosen is not None:
                break
    if build_offline:
        n_checked = len(local_cache)
        report.append(f"gate 5 (offline build) (repo, base SHA) pairs checked for a fully local tree: "
                      f"{n_checked}, buildable {sum(local_cache.values())}")
    if chosen is None:
        return None, report
    r = chosen
    report.append(f"selected: failure class {r['failure_class']} (rule '{r['failure_rule']}'), "
                  f"preference code-level > unknown > timeout > environment")
    return Candidate(r["repo"], int(r["pr_number"]), int(r["run_id"]), r["head_sha"], r["base_sha"],
                     r["test_id"], int(r["job_id"]), gdir, r["failure_message"],
                     r["failure_class"], r["failure_rule"]), report


def run_flaky(run_id: int, head_sha: str, test_ids: set[str], res: pd.DataFrame,
              inst: pd.DataFrame, par: pd.DataFrame) -> tuple[set[str], int]:
    """Re-derive the same-SHA flip rule of `src/label/fault_revealing.py` for one run.

    A test is flaky when, across the runs of the same workflow on the same head
    SHA, it fails in some but not all of them.

    Args:
        run_id: The instance's run.
        head_sha: Its head commit.
        test_ids: T_head_fail for the run.
        res: `base_resolution_new` rows.
        inst: `instances_raw` rows.
        par: `parsed_outcomes` rows.

    Returns:
        `(flaky_test_ids, n_runs_on_that_sha_and_workflow)`.
    """
    wf = inst.loc[inst["run_id"] == run_id, "workflow_id"].iloc[0]
    sibling = inst[(inst["head_sha"] == head_sha) & (inst["workflow_id"] == wf)]["run_id"]
    sibling = set(sibling) & set(res["run_id"])
    flaky = set()
    for t in sorted(test_ids):
        failing = set(par[(par["test_id"] == t) & par["run_id"].isin(sibling)]["run_id"])
        if len(failing) < len(sibling):
            flaky.add(t)
    return flaky, len(sibling)


def main() -> int:
    """Print the walkthrough.

    Returns:
        Process exit status.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--build-graph-offline", action="store_true",
                    help="no-op: building a missing graph offline is now the default")
    ap.add_argument("--no-build-graph", action="store_true",
                    help="require the graph to already be in data/graphs/ (never build one)")
    args = ap.parse_args()
    os.environ["GIT_NO_LAZY_FETCH"] = "1"

    cand, report = find_candidate(not args.no_build_graph)
    print("SELECTION (sorted by repo, PR, run, test; first instance clearing every gate)")
    for line in report:
        print(f"  {line}")
    if cand is None:
        print("\nNO QUALIFYING INSTANCE: nothing cleared every gate, so nothing is shown.")
        print("  (no fully local tree or graph for any candidate; see docs/REPRODUCE.md)")
        return 2

    from src.harvest.rawstore import RawStore

    inst, res, par = _read("instances_raw"), _read("base_resolution_new"), _read("parsed_outcomes")
    bout, out, bind = _read("base_outcomes"), _read("outcomes"), _read("binding")
    row = inst[inst["run_id"] == cand.run_id].iloc[0]
    rres = res[res["run_id"] == cand.run_id].iloc[0]

    print("\n1) THE CHANGE")
    print(f"  repo        {cand.repo}")
    print(f"  pull request #{cand.pr}  (workflow '{row['workflow_name']}', run {cand.run_id})")
    print(f"  head commit {cand.head_sha}")
    print(f"  base commit {cand.base_sha}   (resolved base, status '{rres['status']}')")

    print(f"\n2) THE RAW CI LOG  (job {cand.job_id}, lines that name the failing test)")
    body = RawStore().read_records(cand.repo, "logs", cand.job_id)[0].body.decode("utf-8", "replace")
    for ln in log_excerpt(body, cand.test_id) or ["(no line names the test)"]:
        print(f"  | {ln}")

    print("\n3) THE PARSED OUTCOME")
    po = par[(par["run_id"] == cand.run_id) & (par["test_id"] == cand.test_id)].iloc[0]
    print(f"  canonical test_id  {po['test_id']}")
    print(f"  status {po['status']}, harness {po['harness']}, parser confidence "
          f"{po['parser_confidence']:.2f}, fqcn-qualified {po['is_fqcn_qualified']}")
    print(f"  failure message ({cand.failure_class}, rule '{cand.failure_rule}'): "
          f"{(cand.failure_message or '(none recorded)')[:MAX_LINE_CHARS]!r}")

    print("\n4) THE BASE RUN")
    brid = rres["base_run_id"]
    if pd.isna(brid):
        print("  no base run id recorded")
        concl = None
    else:
        brow = inst[inst["run_id"] == int(brid)]
        concl = brow["run_conclusion"].iloc[0] if len(brow) else None
        print(f"  base run {int(brid)}, distance {rres['base_run_distance']:g} commits, "
              f"conclusion {concl if concl else 'not captured'}")
    t_base = set(bout[bout["run_id"] == cand.run_id]["test_id"])
    at_base = "FAILED" if cand.test_id in t_base else "no failure recorded"
    print(f"  this test at the base run: {at_base}")

    print("\n5) THE FAULT-REVEALING VERDICT")
    t_head = set(par[par["run_id"] == cand.run_id]["test_id"])
    flaky, n_sib = run_flaky(cand.run_id, cand.head_sha, t_head, res, inst, par)
    verdict = t_head - t_base - flaky
    print(f"  T_head_fail  = {len(t_head)} tests failed at head")
    print(f"  T_base_fail  = {len(t_base)} tests failed at base")
    print(f"  flaky        = {len(flaky)} (fail in some but not all of {n_sib} run(s) of this "
          f"workflow on this head SHA)")
    print(f"  T_reveal     = T_head_fail - T_base_fail - flaky = {len(verdict)} tests")
    print(f"  this test: in head {cand.test_id in t_head}, in base {cand.test_id in t_base}, "
          f"flaky {cand.test_id in flaky}  ->  fault-revealing {cand.test_id in verdict}")
    recorded = set(out[(out["run_id"] == cand.run_id) & (out["split"] == "strict")]["test_id"])
    print(f"  agrees with outcomes.parquet (strict split): {recorded == verdict}"
          f" ({len(recorded)} recorded)")

    print("\n6) THE BOUND TEST FILE")
    brow = bind[(bind["repo"] == cand.repo) & (bind["test_id"] == cand.test_id)].iloc[0]
    print(f"  {brow['resolved_path']}  (binding '{brow['status']}', "
          f"{brow['candidates_considered']} candidate file(s) considered)")

    print("\n7) GRAPH CONTEXT  (graph at the base commit; hops on the undirected projection)")
    changed = print_graph(cand, brow["resolved_path"])

    print("\n8) CO-CHANGE vs WHAT ACTUALLY FAILED")
    print_cochange(cand, changed, out, bind)
    return 0


def file_node(graph, path: str) -> str | None:
    """The file-level node (`source_location` L1) of `path`, or None."""
    return next((n for n, d in sorted(graph.nodes(data=True))
                 if d.get("source_file") == path and d.get("source_location") == "L1"), None)


def map_nodes(graph, test_id: str, test_file: str,
              changed: list[str]) -> tuple[str | None, str, list[tuple[str, str | None]]]:
    """Locate the test node and each changed file's node in a bound graph.

    Args:
        graph: A graph with `bind_test_ids` already applied.
        test_id: The failing test.
        test_file: Its bound test file.
        changed: The PR's changed files.

    Returns:
        `(test_node, how_it_was_found, [(changed_file, node_or_None)])`.
    """
    tnodes = sorted(n for n, d in graph.nodes(data=True) if d.get("test_id") == test_id)
    if tnodes:
        tnode, how = tnodes[0], "the test's own node"
    else:
        tnode, how = file_node(graph, test_file), "its test FILE node (no node carries this test_id)"
    return tnode, how, [(f, file_node(graph, f)) for f in changed]


def print_graph(cand: Candidate, test_file: str) -> list[str]:
    """Print changed files and their distance to the failing test via `GraphQuery`.

    Args:
        cand: The selected instance.
        test_file: The bound test file.

    Returns:
        The PR's changed filenames (sorted), for step 8.
    """
    from src.graph.build import build_graph_at, graph_path, load_graph
    from src.graph.query import UNREACHABLE, GraphQuery
    from src.graph.test_nodes import bind_test_ids

    cs = _read("changesets")
    cs = cs[(cs["repo"] == cand.repo) & (cs["pr_number"].astype(str) == str(cand.pr))
            & (cs["head_sha"] == cand.head_sha)]
    changed = sorted(cs["filename"])
    print(f"  the PR changed {len(changed)} file(s)")

    tmp = None
    gdir = cand.graph_dir
    if gdir is None:
        tmp = tempfile.TemporaryDirectory(prefix="br-demo-")
        gdir = Path(tmp.name)
        print("  graph: built into a throw-away temp dir from local git objects "
              "(data/graphs/ has none for this SHA)")
        # The extractor narrates progress; swallow it so the output is the walkthrough.
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            build_graph_at(cand.repo, cand.base_sha, clone_dir=clone_dir(cand.repo), out_dir=gdir)
    else:
        print(f"  graph: {graph_path(cand.repo, cand.base_sha, gdir)}")
    try:
        graph = load_graph(graph_path(cand.repo, cand.base_sha, gdir))
        bind_test_ids(graph, [cand.test_id], repo=cand.repo)
        tnode, how, mapped = map_nodes(graph, cand.test_id, test_file, changed)
        print(f"  test node: {tnode} [{how}]")
        q = GraphQuery(graph, repo=cand.repo, sha=cand.base_sha)
        for f, node in mapped[:MAX_LOG_LINES]:
            if node is None:
                print(f"    {f}: not in the base graph (added/non-source)")
            else:
                d = q.shortest_path_length(node, tnode) if tnode else UNREACHABLE
                print(f"    {f}: " + ("unreachable" if d == UNREACHABLE else f"{d} hop(s) to the test"))
        if len(mapped) > MAX_LOG_LINES:
            print(f"    ... {len(mapped) - MAX_LOG_LINES} more")
        nodes = [n for _, n in mapped if n]
        if tnode and nodes:
            m = q.min_distance_to_any_changed(tnode, nodes)
            print(f"  min_distance_to_any_changed = " + ("unreachable" if m == UNREACHABLE else f"{m} hop(s)"))
        else:
            print("  min_distance_to_any_changed = n/a (no mapped changed node or test node)")
    finally:
        if tmp is not None:
            tmp.cleanup()
    return changed


def print_cochange(cand: Candidate, changed: list[str], out: pd.DataFrame, bind: pd.DataFrame) -> None:
    """Print the co-change prediction against the actual failing test files.

    Mirrors `analysis/rq1_divergence.py`: top-k partners of every changed file,
    minus the changed files, against the bound test files of the strict labels.
    Ties on confidence are broken by file name, which rq1 leaves unspecified.

    Args:
        cand: The selected instance.
        changed: The PR's changed files.
        out: `outcomes.parquet`.
        bind: `binding.parquet`.
    """
    co = _read("cochange")
    co = co[co["repo_full"] == cand.repo]
    predicted: set[str] = set()
    for f in changed:
        part = co[co["file_a"] == f].sort_values(["conf_a_to_b", "file_b"], ascending=[False, True])
        predicted.update(part["file_b"].head(COCHANGE_K))
    predicted -= set(changed)
    tests = out[(out["run_id"] == cand.run_id) & (out["split"] == "strict")]["test_id"]
    paths = bind[(bind["repo"] == cand.repo) & (bind["status"] == "exact")
                 & bind["test_id"].isin(tests)]["resolved_path"]
    actual = set(paths)
    if not predicted:
        print("  no co-change predictions exist for this instance's changed files "
              "(the proxy is silent here)")
        print(f"  actual failing test files: {len(actual)}")
        return
    hit = predicted & actual
    p = len(hit) / len(predicted)
    r = len(hit) / len(actual) if actual else 0.0
    j = len(hit) / len(predicted | actual)
    print(f"  co-change set (top {COCHANGE_K} partners per changed file): {len(predicted)} files")
    print(f"  actual failing set (bound test files): {len(actual)} files")
    print(f"  overlap: {len(hit)}   precision {p:.3f}  recall {r:.3f}  jaccard {j:.3f}")
    for name, s in (("predicted", predicted), ("actual", actual), ("overlap", hit)):
        print(f"    {name}: " + (", ".join(sorted(s)[:5]) + (" ..." if len(s) > 5 else "") if s else "-"))


if __name__ == "__main__":
    sys.exit(main())
