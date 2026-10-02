"""Commit-pinned graph builder over the stripped Graphify fork (ROADMAP §10.2, §19).

Graphify builds one graph for a working directory. BlastRadius needs a graph *at a
specific commit* — the base SHA of an instance — so this module adds the missing
notion of history:

1. `git worktree add --detach` at the SHA (never a clone per commit),
2. the stripped, LLM-free tree-sitter extractor over `.java` and `.py` only,
3. compressed NetworkX node-link JSON at `data/graphs/graph_{repo}_{sha}.json.gz`,
4. per-(repo, sha) build statistics: node/edge counts, orphan rate and
   parse-failure rate per language, with a flag above the §19.4 20% ceiling.

Determinism is a requirement (D-17, and the §10.2 step 6 equivalence assertion
depends on it): every collection written to disk is sorted, clustering is seeded,
no wall-clock value enters the graph payload, and no network or LLM call happens
on the extraction path. Build timings and `built_at` live in the sibling
`.stats.json`, which keeps the graph file itself byte-reproducible.

This is graph-layer code. Per D-48 no number produced here reaches `make tables`,
`release/` or the paper.
"""

from __future__ import annotations

import gzip
import json
import shutil
import subprocess
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import networkx as nx

__all__ = [
    "GRAPH_FORMAT_VERSION",
    "PARSE_FAILURE_CEILING",
    "SOURCE_SUFFIXES",
    "BuildStats",
    "REVERSE_HOP_RELATIONS",
    "build_graph_at",
    "build_graph_incremental",
    "cache_miss_files",
    "changed_source_files",
    "collect_source_files",
    "graph_path",
    "language_of",
    "load_graph",
    "pagerank",
    "repo_slug",
    "worktree_at",
    "write_graph",
]

#: Bumped whenever the on-disk node-link payload changes shape. A graph written
#: by an older version is not comparable with one written by a newer one, so the
#: incremental path refuses to reuse across versions.
GRAPH_FORMAT_VERSION = 1

#: ROADMAP §19.4: a (repo, sha) above this parse-failure rate is flagged, with a
#: reason, rather than silently feeding the frame.
PARSE_FAILURE_CEILING = 0.20

#: The only extensions this layer dispatches. Java and Python are the corpus
#: languages (D-03); TypeScript is an explicit non-goal.
SOURCE_SUFFIXES: dict[str, str] = {".java": "java", ".py": "python"}

#: Directories never worth extracting: build output, vendored trees and VCS
#: metadata. Sorted and matched on path parts so the result is checkout-independent.
_SKIP_DIR_PARTS = frozenset(
    {
        ".git",
        ".gradle",
        ".idea",
        ".mvn",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "node_modules",
        "out",
        "target",
        "venv",
    }
)

_GIT_ENV = {"GIT_TERMINAL_PROMPT": "0"}


@dataclass(frozen=True)
class BuildStats:
    """Per-(repo, sha) build record (ROADMAP §19.1 step 5, §10.2 step 5).

    Attributes:
        repo: Owner/name slug as it appears in `instances_raw.parquet`.
        sha: The commit the graph was built at.
        graph_path: Where the compressed node-link JSON was written.
        n_nodes: Node count.
        n_edges: Edge count.
        n_orphan_nodes: Nodes with total degree zero.
        orphan_rate: `n_orphan_nodes / n_nodes`, or 0.0 for an empty graph.
        n_files_considered: Source files found at this SHA, per `SOURCE_SUFFIXES`.
        n_parse_failures: Files that produced no node, or that the extractor
            reported in `failed_sources`.
        parse_failure_rate: `n_parse_failures / n_files_considered`.
        per_language: `{language: {"files": n, "failures": n, "rate": f}}`.
        flagged: True when `parse_failure_rate` exceeds `PARSE_FAILURE_CEILING`.
        flag_reason: Why it was flagged, or None.
        n_communities: Size of the seeded partition.
        incremental_from: The SHA this build reused, or None for a cold build.
        communities_inherited: True when the partition was carried over rather
            than recomputed (ROADMAP §19.1 step 4).
        graphify_commit: Pinned upstream Graphify SHA from `vendor/GRAPHIFY_COMMIT.txt`.
        built_at: UTC ISO-8601 build time. Deliberately absent from the graph
            payload so the graph file stays byte-reproducible.
        wall_seconds: End-to-end build time.
        extract_seconds: Time inside the extractor.
        n_files_changed: Source files differing from `incremental_from`, or 0
            for a cold build.
        n_files_reverse_hop: Files one reverse relation hop from the changed set
            (ROADMAP §19.1 step 3).
        n_files_reextracted: Files actually parsed this run — the content-cache
            misses. The rest were replayed from their cache entries.
        failed_source_files: Sorted repo-relative paths that failed to parse.
    """

    repo: str
    sha: str
    graph_path: str
    n_nodes: int
    n_edges: int
    n_orphan_nodes: int
    orphan_rate: float
    n_files_considered: int
    n_parse_failures: int
    parse_failure_rate: float
    per_language: dict[str, dict[str, float]]
    flagged: bool
    flag_reason: str | None
    n_communities: int
    incremental_from: str | None
    communities_inherited: bool
    graphify_commit: str
    built_at: str
    wall_seconds: float
    extract_seconds: float
    n_files_changed: int = 0
    n_files_reverse_hop: int = 0
    n_files_reextracted: int = 0
    failed_source_files: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        """Return a JSON-serialisable copy of this record."""
        return asdict(self)


def repo_slug(repo: str) -> str:
    """Convert an `owner/name` repo to its on-disk slug.

    Matches the existing `data/clones/` convention (`castorini__anserini`).

    Args:
        repo: Repo in `owner/name` form.

    Returns:
        The slug with `/` replaced by `__`.
    """
    return repo.replace("/", "__")


def graph_path(repo: str, sha: str, out_dir: Path | str = Path("data/graphs")) -> Path:
    """Return the canonical graph path for a (repo, sha).

    Args:
        repo: Repo in `owner/name` form.
        sha: Commit SHA.
        out_dir: Directory graphs live in.

    Returns:
        `<out_dir>/graph_{slug}_{sha}.json.gz`.
    """
    return Path(out_dir) / f"graph_{repo_slug(repo)}_{sha}.json.gz"


def language_of(path: Path | str) -> str | None:
    """Return the language this layer assigns to a path, or None if unsupported.

    Args:
        path: Any file path.

    Returns:
        `"java"`, `"python"`, or None.
    """
    return SOURCE_SUFFIXES.get(Path(path).suffix.lower())


def _git(repo_dir: Path, *args: str, check: bool = True) -> str:
    """Run git in `repo_dir` and return stdout.

    Args:
        repo_dir: Repository or worktree directory.
        *args: Arguments after `git`.
        check: Raise on a non-zero exit.

    Returns:
        Captured stdout.

    Raises:
        RuntimeError: When `check` and git exited non-zero.
    """
    proc = subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=True,
        env={**_GIT_ENV, **_os_environ()},
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed in {repo_dir} "
            f"(exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def _os_environ() -> dict[str, str]:
    """Return the process environment.

    Isolated in a helper so `_git` stays trivially testable.

    Returns:
        A copy of `os.environ`.
    """
    import os

    return dict(os.environ)


@contextmanager
def worktree_at(clone_dir: Path | str, sha: str) -> Iterator[Path]:
    """Yield a detached git worktree of `clone_dir` checked out at `sha`.

    ROADMAP §19.1 step 1: a worktree, never a clone per commit. The worktree is
    removed and pruned on exit even if the body raises.

    Args:
        clone_dir: An existing clone (a `--filter=blob:none` clone is fine; the
            checkout lazily fetches the blobs it needs).
        sha: The commit to detach at.

    Yields:
        The worktree root.

    Raises:
        RuntimeError: When the SHA is not a commit in the clone, or git fails.
    """
    clone_dir = Path(clone_dir).resolve()
    kind = _git(clone_dir, "cat-file", "-t", f"{sha}^{{commit}}", check=False).strip()
    if kind != "commit":
        raise RuntimeError(f"{sha} is not a commit in {clone_dir} (got {kind!r})")

    holder = Path(tempfile.mkdtemp(prefix=f"br-wt-{uuid.uuid4().hex[:8]}-"))
    tree = holder / "tree"
    try:
        _git(clone_dir, "worktree", "add", "--detach", "--quiet", str(tree), sha)
        yield tree
    finally:
        _git(clone_dir, "worktree", "remove", "--force", str(tree), check=False)
        _git(clone_dir, "worktree", "prune", check=False)
        shutil.rmtree(holder, ignore_errors=True)


def collect_source_files(root: Path | str) -> list[Path]:
    """Return the sorted `.java`/`.py` files under `root`, skipping build output.

    Sorting is what makes extraction order — and therefore node-id collision
    resolution and the dedup survivor — reproducible across machines.

    Args:
        root: Directory to walk.

    Returns:
        Absolute paths, sorted by their path relative to `root`.
    """
    root = Path(root)
    found: list[Path] = []
    for path in root.rglob("*"):
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if _SKIP_DIR_PARTS.intersection(rel.parts[:-1]):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        found.append(path)
    return sorted(found, key=lambda p: p.relative_to(root).as_posix())


def graphify_commit(vendor_file: Path | str = Path("vendor/GRAPHIFY_COMMIT.txt")) -> str:
    """Return the pinned upstream Graphify commit SHA.

    Args:
        vendor_file: Path to `GRAPHIFY_COMMIT.txt`.

    Returns:
        The SHA, or `"unknown"` when the file is absent.
    """
    path = Path(vendor_file)
    return path.read_text(encoding="utf-8").strip() if path.is_file() else "unknown"


def _extract(
    paths: list[Path], root: Path, cache_root: Path | None, *, parallel: bool = True
) -> dict:
    """Run the stripped extractor over `paths`.

    Graphify's `ProcessPoolExecutor` extraction collects per-file results by
    index, so worker count and completion order cannot reach the output: a
    parallel run is identical to a serial one, node attributes and all. That is
    pinned by `test_parallel_and_serial_extraction_agree`, because determinism
    is a requirement here rather than a nicety (D-17).

    Args:
        paths: Files to extract, already filtered and sorted.
        root: Anchor for `source_file` relativization and node ids.
        cache_root: Where Graphify's SHA-256 content cache lives. Sharing one
            cache_root across the SHAs of a repo is what makes an incremental
            build cheap (ROADMAP §19.1).
        parallel: Use the multiprocess extractor. Only a test turns this off.

    Returns:
        The extractor's `{nodes, edges, failed_sources, ...}` dict. An empty
        input yields the same shape with empty collections.
    """
    if not paths:
        return {"nodes": [], "edges": [], "failed_sources": []}
    from graphify.extract import extract as graphify_extract

    return graphify_extract(
        list(paths),
        cache_root=cache_root,
        root=root,
        parallel=parallel,
    )


def _node_sort_key(node: dict) -> tuple[str, str, str]:
    """Return a total order over nodes that does not depend on walk order."""
    return (
        str(node.get("source_file") or ""),
        str(node.get("source_location") or ""),
        str(node.get("id") or ""),
    )


def _edge_sort_key(edge: dict) -> tuple[str, str, str, str]:
    """Return a total order over edges that does not depend on walk order."""
    return (
        str(edge.get("source") or ""),
        str(edge.get("target") or ""),
        str(edge.get("edge_type") or edge.get("relation") or ""),
        str(edge.get("source_location") or ""),
    )


def _start_line(value: object) -> int | None:
    """Parse Graphify's `L<n>` source_location into a line number.

    Args:
        value: A `source_location` attribute, e.g. `"L42"` or `"L42-L50"`.

    Returns:
        The first line number, or None when it cannot be read.
    """
    text = str(value or "")
    if not text.startswith("L"):
        return None
    head = text[1:].split("-", 1)[0].strip()
    return int(head) if head.isdigit() else None


def _confidence_score(confidence: object) -> float:
    """Map Graphify's confidence vocabulary to a numeric score.

    `EXTRACTED` is an AST fact and scores 1.0; `INFERRED` and `AMBIGUOUS` are
    heuristics (ROADMAP §10.3 step 4). An edge that already carries its own
    `confidence_score` keeps it — the test→source binder sets per-strategy
    scores (§29.6).

    Args:
        confidence: The edge's `confidence` attribute.

    Returns:
        A score in [0, 1].
    """
    return {"EXTRACTED": 1.0, "INFERRED": 0.5, "AMBIGUOUS": 0.25}.get(
        str(confidence or "EXTRACTED"), 0.5
    )


def pagerank(
    graph: nx.DiGraph,
    *,
    alpha: float = 0.85,
    tol: float = 1.0e-10,
    max_iter: int = 200,
) -> dict[str, float]:
    """Return PageRank by power iteration, with no SciPy dependency.

    `networkx.pagerank` dispatches to a SciPy sparse solver, and SciPy is outside
    this project's `graph` extra. This is the textbook formulation instead:
    uniform personalisation, dangling mass redistributed uniformly, and nodes
    visited in sorted order so the floating-point accumulation — and therefore
    the result — is identical on every run and every machine.

    Args:
        graph: Any directed graph.
        alpha: Damping factor.
        tol: L1 convergence threshold on the whole vector.
        max_iter: Iteration cap; the last iterate is returned if it is hit.

    Returns:
        `{node_id: score}` summing to 1.0 for a non-empty graph, `{}` otherwise.
    """
    nodes = sorted(graph.nodes())
    n = len(nodes)
    if n == 0:
        return {}
    rank = {node: 1.0 / n for node in nodes}
    out_degree = {node: graph.out_degree(node) for node in nodes}
    dangling = [node for node in nodes if out_degree[node] == 0]
    predecessors = {node: sorted(graph.predecessors(node)) for node in nodes}

    for _ in range(max_iter):
        leaked = alpha * sum(rank[node] for node in dangling) / n
        base = (1.0 - alpha) / n + leaked
        nxt = {}
        for node in nodes:
            inflow = sum(
                rank[src] / out_degree[src] for src in predecessors[node] if out_degree[src]
            )
            nxt[node] = base + alpha * inflow
        delta = sum(abs(nxt[node] - rank[node]) for node in nodes)
        rank = nxt
        if delta < tol:
            break
    return rank


def _annotate(graph: nx.DiGraph, communities: dict[int, list[str]]) -> None:
    """Add the derived node/edge attributes this layer owns, in place.

    Conforms to the field names `docs/SCHEMAS.md` already defines for
    `graph_nodes` / `graph_edges` (`community_id`, `degree`, `start_line`,
    `edge_type`, `confidence_score`). Everything it does not define stays
    graph-internal and is documented in `src/graph/README.md`.

    Args:
        graph: The built graph, mutated in place.
        communities: `{community_id: [node_id, ...]}` from the seeded partition.
    """
    member_of = {
        node: cid for cid, members in communities.items() for node in members
    }
    scores = pagerank(graph) if graph.number_of_edges() else {}
    for node, data in graph.nodes(data=True):
        data["community_id"] = member_of.get(node)
        data["degree"] = graph.degree(node)
        data["pagerank"] = round(float(scores.get(node, 0.0)), 12)
        data["start_line"] = _start_line(data.get("source_location"))
        data.setdefault("parse_status", "ok")
    for _, _, data in graph.edges(data=True):
        data["edge_type"] = data.get("edge_type") or data.get("relation") or "contains"
        data.setdefault("confidence", "EXTRACTED")
        if "confidence_score" not in data:
            data["confidence_score"] = _confidence_score(data.get("confidence"))
        data.setdefault("weight", 1.0)


def write_graph(graph: nx.DiGraph, meta: dict, path: Path | str) -> Path:
    """Write `graph` as deterministic gzipped NetworkX node-link JSON.

    The payload carries no timestamp and every collection is sorted, so two
    builds of the same commit produce byte-identical files. `mtime=0` keeps the
    gzip header stable too.

    Args:
        graph: The graph to serialise.
        meta: Graph-level metadata stored under the payload's `meta` key.
        path: Destination; parent directories are created.

    Returns:
        The path written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = nx.node_link_data(graph, edges="links")
    payload["nodes"] = sorted(payload.get("nodes", []), key=_node_sort_key)
    payload["links"] = sorted(payload.get("links", []), key=_edge_sort_key)
    payload["meta"] = {k: meta[k] for k in sorted(meta)}
    payload.pop("graph", None)
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    tmp = path.with_suffix(path.suffix + ".tmp")
    with gzip.GzipFile(filename="", mode="wb", fileobj=tmp.open("wb"), mtime=0) as fh:
        fh.write(text.encode("utf-8"))
    tmp.replace(path)
    return path


def load_graph(path: Path | str) -> nx.DiGraph:
    """Load a graph written by `write_graph`.

    Args:
        path: Path to a `graph_*.json.gz`.

    Returns:
        The graph, with `meta` available as `graph.graph["meta"]`.
    """
    with gzip.open(Path(path), "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    meta = payload.pop("meta", {})
    graph = nx.node_link_graph(payload, directed=True, multigraph=False, edges="links")
    graph.graph["meta"] = meta
    return graph


def _cached_parse_errors(path: Path, root: Path, cache_root: Path | None) -> dict | None:
    """Return the per-file `parse_errors` record from Graphify's content cache.

    `extract()` aggregates its per-file results and reports syntax errors only
    as a stderr warning, so the structural signal is unreachable from its return
    value. It does survive in the SHA-256 content cache entry, which is keyed by
    file content, so reading it back is both exact and free of a second parse.

    Args:
        path: The extracted file.
        root: The anchor the content hash was computed against.
        cache_root: Where the cache lives, or None when caching was off.

    Returns:
        The `parse_errors` dict, `{}` when the file parsed cleanly, or None when
        there is no cache entry at all (Graphify's zero-node skip refuses to
        cache a file that produced nothing).
    """
    if cache_root is None:
        return {}
    from graphify.cache import cache_dir, file_hash

    try:
        digest = file_hash(path, root, cache_root=cache_root)
        entry = cache_dir(cache_root, "ast") / f"{digest}.json"
        if not entry.is_file():
            return None
        return json.loads(entry.read_text(encoding="utf-8")).get("parse_errors") or {}
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def _parse_failure_report(
    files: list[Path],
    root: Path,
    nodes: list[dict],
    failed_sources: list[str],
    cache_root: Path | None = None,
) -> tuple[dict[str, dict[str, float]], list[str]]:
    """Attribute parse failures to languages (ROADMAP §10.2 step 5, §19.4).

    A file counts as a parse failure when any of these holds:

    * the extractor named it in `failed_sources`;
    * it contributed no node at all;
    * tree-sitter recovered from a syntax error in it. tree-sitter is
      error-tolerant, so a badly broken file still yields its file node and
      never reaches `failed_sources` — counting only hard failures would report
      a 0% rate on a corpus the parser is silently mangling. The structural
      marker is the cached `parse_errors` record.

    Args:
        files: The files handed to the extractor, absolute.
        root: Extraction anchor, for relativization.
        nodes: Extracted nodes.
        failed_sources: The extractor's own failure list.
        cache_root: Content-cache location, for the syntax-error signal.

    Returns:
        `(per_language, sorted_failed_relative_paths)`.
    """
    produced = {str(node.get("source_file") or "") for node in nodes}
    reported = {Path(p).as_posix() for p in failed_sources}
    reported |= {Path(p).name for p in failed_sources}

    per_language: dict[str, dict[str, float]] = {}
    failures: list[str] = []
    for path in files:
        lang = language_of(path) or "other"
        rel = path.relative_to(root).as_posix()
        bucket = per_language.setdefault(lang, {"files": 0, "failures": 0, "rate": 0.0})
        bucket["files"] += 1
        failed = rel in reported or Path(rel).name in reported or rel not in produced
        if not failed:
            errors = _cached_parse_errors(path, root, cache_root)
            failed = errors is None or bool(errors)
        if failed:
            bucket["failures"] += 1
            failures.append(rel)
    for bucket in per_language.values():
        bucket["rate"] = (
            round(bucket["failures"] / bucket["files"], 6) if bucket["files"] else 0.0
        )
    return {k: per_language[k] for k in sorted(per_language)}, sorted(set(failures))


def _build_stats(
    *,
    repo: str,
    sha: str,
    out_path: Path,
    graph: nx.DiGraph,
    communities: dict[int, list[str]],
    files: list[Path],
    root: Path,
    nodes: list[dict],
    failed_sources: list[str],
    incremental_from: str | None,
    communities_inherited: bool,
    wall_seconds: float,
    extract_seconds: float,
    cache_root: Path | None = None,
    n_files_changed: int = 0,
    n_files_reverse_hop: int = 0,
    n_files_reextracted: int = 0,
) -> BuildStats:
    """Assemble the `BuildStats` record for one build."""
    per_language, failures = _parse_failure_report(
        files, root, nodes, failed_sources, cache_root
    )
    n_nodes = graph.number_of_nodes()
    orphans = [n for n in graph if graph.degree(n) == 0]
    rate = round(len(failures) / len(files), 6) if files else 0.0
    flagged = rate > PARSE_FAILURE_CEILING
    reason = None
    if flagged:
        worst = sorted(
            per_language.items(), key=lambda kv: (-kv[1]["rate"], kv[0])
        )
        detail = ", ".join(
            f"{lang} {int(b['failures'])}/{int(b['files'])}" for lang, b in worst
        )
        reason = (
            f"parse-failure rate {len(failures)}/{len(files)} = {rate:.4f} exceeds the "
            f"ROADMAP §19.4 ceiling of {PARSE_FAILURE_CEILING:.2f} ({detail})"
        )
    return BuildStats(
        repo=repo,
        sha=sha,
        graph_path=str(out_path),
        n_nodes=n_nodes,
        n_edges=graph.number_of_edges(),
        n_orphan_nodes=len(orphans),
        orphan_rate=round(len(orphans) / n_nodes, 6) if n_nodes else 0.0,
        n_files_considered=len(files),
        n_parse_failures=len(failures),
        parse_failure_rate=rate,
        per_language=per_language,
        flagged=flagged,
        flag_reason=reason,
        n_communities=len(communities),
        incremental_from=incremental_from,
        communities_inherited=communities_inherited,
        graphify_commit=graphify_commit(),
        built_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        wall_seconds=round(wall_seconds, 3),
        extract_seconds=round(extract_seconds, 3),
        n_files_changed=n_files_changed,
        n_files_reverse_hop=n_files_reverse_hop,
        n_files_reextracted=n_files_reextracted,
        failed_source_files=failures,
    )


def _assemble(extractions: list[dict], root: Path) -> nx.DiGraph:
    """Merge extraction results into an annotated, clustered directed graph.

    Args:
        extractions: One or more `{nodes, edges}` dicts, in merge order.
        root: Extraction anchor, so `source_file` values stay relative.

    Returns:
        The graph with community, degree, pagerank and edge-type attributes set.
    """
    from graphify.build import build as graphify_build
    from graphify.cluster import cluster as graphify_cluster

    sorted_extractions = [
        {
            "nodes": sorted(ext.get("nodes", []), key=_node_sort_key),
            "edges": sorted(ext.get("edges", []), key=_edge_sort_key),
        }
        for ext in extractions
    ]
    graph = graphify_build(sorted_extractions, directed=True, dedup=True, root=root)
    # cluster() canonicalises into a sorted graph and seeds its partitioner, so
    # the partition is reproducible. graspologic (Leiden) is outside the `graph`
    # extra, so this is NetworkX's seeded Louvain — see src/graph/README.md.
    communities = graphify_cluster(graph) if graph.number_of_nodes() else {}
    _annotate(graph, communities)
    return graph, communities


def build_graph_at(
    repo: str,
    sha: str,
    *,
    clone_dir: Path | str | None = None,
    clones_root: Path | str = Path("data/clones"),
    out_dir: Path | str = Path("data/graphs"),
    cache_root: Path | str | None = None,
    force: bool = False,
) -> BuildStats:
    """Build (or reuse) the graph of `repo` at `sha` and return its statistics.

    The cold path of ROADMAP §10.2: worktree at the SHA, stripped extractor over
    `.java`/`.py`, compressed node-link JSON keyed by (repo, sha).

    Args:
        repo: Repo in `owner/name` form.
        sha: The commit to build at.
        clone_dir: An existing clone. Defaults to `<clones_root>/<slug>`.
        clones_root: Where clones live.
        out_dir: Where graphs are written.
        cache_root: Anchor for Graphify's SHA-256 content cache. Defaults to a
            per-repo directory under `out_dir`, shared across that repo's SHAs.
        force: Rebuild even when the graph file already exists.

    Returns:
        The `BuildStats` for this build. When the graph already exists and
        `force` is False, the recorded stats are reloaded from the sidecar.

    Raises:
        FileNotFoundError: When the clone is missing.
        RuntimeError: When the SHA is not a commit in the clone.
    """
    started = time.perf_counter()
    clone = Path(clone_dir) if clone_dir else Path(clones_root) / repo_slug(repo)
    if not (clone / ".git").exists() and not (clone / "HEAD").exists():
        raise FileNotFoundError(f"no clone at {clone} for {repo}")

    out_path = graph_path(repo, sha, out_dir)
    stats_path = out_path.with_suffix("").with_suffix(".stats.json")
    if out_path.exists() and stats_path.exists() and not force:
        return BuildStats(**json.loads(stats_path.read_text(encoding="utf-8")))

    cache = Path(cache_root) if cache_root else Path(out_dir) / "cache" / repo_slug(repo)
    cache.mkdir(parents=True, exist_ok=True)

    with worktree_at(clone, sha) as tree:
        files = collect_source_files(tree)
        misses = cache_miss_files(files, tree, cache)
        extract_started = time.perf_counter()
        result = _extract(files, tree, cache)
        extract_seconds = time.perf_counter() - extract_started
        graph, communities = _assemble([result], tree)
        stats = _build_stats(
            repo=repo,
            sha=sha,
            out_path=out_path,
            graph=graph,
            communities=communities,
            files=files,
            root=tree,
            nodes=result.get("nodes", []),
            failed_sources=result.get("failed_sources", []),
            incremental_from=None,
            communities_inherited=False,
            wall_seconds=time.perf_counter() - started,
            extract_seconds=extract_seconds,
            cache_root=cache,
            n_files_reextracted=len(misses),
        )

    write_graph(
        graph,
        {
            "repo": repo,
            "sha": sha,
            "format_version": GRAPH_FORMAT_VERSION,
            "graphify_commit": stats.graphify_commit,
            "n_nodes": stats.n_nodes,
            "n_edges": stats.n_edges,
            "n_communities": stats.n_communities,
            "parse_failure_rate": stats.parse_failure_rate,
            "communities_inherited": stats.communities_inherited,
            "languages": sorted(SOURCE_SUFFIXES.values()),
        },
        out_path,
    )
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    stats_path.write_text(
        json.dumps(stats.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return stats


#: Relations followed in reverse to find the files whose edges a dirty file can
#: invalidate (ROADMAP §19.1 step 3). The spec names the reverse-`imports` hop;
#: the call and inheritance relations are included because an unchanged caller's
#: `calls` edge into a changed callee goes stale the same way, and leaving it
#: behind is exactly the "stale edges pointing at deleted symbols" failure §19.1
#: warns about.
REVERSE_HOP_RELATIONS = frozenset(
    {
        "calls",
        "extends",
        "implements",
        "imports",
        "imports_from",
        "inherits",
        "references",
    }
)

def changed_source_files(clone_dir: Path | str, prev_sha: str, sha: str) -> list[str]:
    """Return the `.java`/`.py` files that differ between two commits.

    Args:
        clone_dir: The clone to diff in.
        prev_sha: The earlier commit.
        sha: The later commit.

    Returns:
        Sorted repo-relative paths, including deletions (a deleted file must
        still invalidate its nodes).
    """
    out = _git(
        Path(clone_dir),
        "diff",
        "--name-only",
        "--no-renames",
        f"{prev_sha}..{sha}",
    )
    return sorted(
        {line for line in out.splitlines() if line and language_of(line) is not None}
    )


def _reverse_hop(graph: nx.DiGraph, dirty: set[str]) -> set[str]:
    """Return the source files one reverse relation hop from `dirty`.

    ROADMAP §19.1 step 3: resolving only the dirty files leaves stale edges
    pointing at symbols that moved or vanished, so the files that reference them
    are re-extracted too.

    Args:
        graph: The previous graph.
        dirty: Repo-relative paths that changed.

    Returns:
        Repo-relative paths of files holding a node that points into `dirty`.
    """
    targets = {
        node
        for node, data in graph.nodes(data=True)
        if str(data.get("source_file") or "") in dirty
    }
    importers: set[str] = set()
    for node in targets:
        for src, _, data in graph.in_edges(node, data=True):
            relation = str(data.get("relation") or data.get("edge_type") or "")
            if relation not in REVERSE_HOP_RELATIONS:
                continue
            source_file = str(graph.nodes[src].get("source_file") or "")
            if source_file:
                importers.add(source_file)
    return importers - dirty


def cache_miss_files(
    files: list[Path], root: Path, cache_root: Path
) -> list[Path]:
    """Return the files with no entry in Graphify's SHA-256 content cache.

    These are the files an extraction will actually parse; the rest are replayed
    from the cache. Reported so an incremental build's cost is attributable
    rather than asserted.

    Args:
        files: Candidate files, absolute.
        root: The anchor the content hash is computed against.
        cache_root: Where the cache lives.

    Returns:
        The subset of `files` that will be re-extracted, in input order.
    """
    from graphify.cache import cache_dir, file_hash

    directory = cache_dir(cache_root, "ast")
    missing = []
    for path in files:
        try:
            if not (directory / f"{file_hash(path, root, cache_root=cache_root)}.json").is_file():
                missing.append(path)
        except OSError:
            missing.append(path)
    return missing


def build_graph_incremental(
    repo: str,
    sha: str,
    prev_sha: str,
    *,
    clone_dir: Path | str | None = None,
    clones_root: Path | str = Path("data/clones"),
    out_dir: Path | str = Path("data/graphs"),
    cache_root: Path | str | None = None,
) -> BuildStats:
    """Build the graph at `sha` incrementally, reusing the work done at `prev_sha`.

    Incrementality comes from Graphify's SHA-256 content cache (ROADMAP §19.1:
    "reuse Graphify's content cache rather than adding a second caching layer").
    Both SHAs of a repo share one `cache_root`, so a file whose content is
    unchanged is replayed from its cache entry and only genuinely changed files
    are parsed. The dirty set from `git diff` and its reverse relation hop are
    computed and recorded, and the files actually re-extracted are reported as
    `n_files_reextracted`.

    **Why the file list handed to the extractor is not narrowed to the dirty
    set.** §19.1 step 3 describes splicing a re-extracted subgraph into the
    previous graph. Graphify's Java import resolution
    (`extractors/resolution.py::_resolve_cross_file_java_imports`) builds its
    `{ClassName: [(node_id, package)]}` index *only* from the files extracted in
    that call, and `resolution_context_nodes` does not reach it — it feeds the
    direct-call index, the callable guard and the member-call resolvers, not the
    import resolver. A narrowed call therefore leaves every `imports` edge of a
    re-extracted Java file pointing at an unresolved placeholder id
    (`org_saiku_service_datasource_idatasourcemanager`) instead of the defining
    class node
    (`saiku_core_..._idatasourcemanager_idatasourcemanager`) — measured on five
    real consecutive commits of `spiculedata/saiku`, where it produced 2 to 207
    spurious nodes and up to 1,443 wrong edges per commit. That is exactly the
    "stale edges pointing at deleted symbols" failure §19.1 warns about, and it
    would make the dataset untrustworthy (§10.2 step 6 calls divergence
    release-blocking, not a known issue).

    Handing the extractor the full file list keeps the cross-file resolvers
    whole, so the incremental graph is equal to the cold graph *by
    construction* rather than by hope, while the content cache still removes the
    parsing work. The remaining per-SHA cost is the resolver's package re-parse
    plus assembly, clustering and PageRank — whole-corpus passes that no
    caching layer at this level can avoid.

    Args:
        repo: Repo in `owner/name` form.
        sha: The commit to build at.
        prev_sha: The already-built commit whose cache this build reuses.
        clone_dir: An existing clone. Defaults to `<clones_root>/<slug>`.
        clones_root: Where clones live.
        out_dir: Where graphs are written.
        cache_root: Content-cache anchor. Defaults to the same per-repo
            directory the cold path uses, which is what makes the reuse happen.

    Returns:
        The `BuildStats` for this build, with `incremental_from` set to
        `prev_sha` and the delta fields populated.

    Raises:
        FileNotFoundError: When the clone is missing.
        RuntimeError: When either SHA is not a commit in the clone.
    """
    started = time.perf_counter()
    clone = Path(clone_dir) if clone_dir else Path(clones_root) / repo_slug(repo)
    if not (clone / ".git").exists() and not (clone / "HEAD").exists():
        raise FileNotFoundError(f"no clone at {clone} for {repo}")

    out_path = graph_path(repo, sha, out_dir)
    cache = Path(cache_root) if cache_root else Path(out_dir) / "cache" / repo_slug(repo)
    cache.mkdir(parents=True, exist_ok=True)

    dirty = set(changed_source_files(clone, prev_sha, sha))
    previous = graph_path(repo, prev_sha, out_dir)
    hop: set[str] = set()
    if previous.is_file():
        hop = _reverse_hop(load_graph(previous), dirty)

    with worktree_at(clone, sha) as tree:
        files = collect_source_files(tree)
        misses = cache_miss_files(files, tree, cache)
        extract_started = time.perf_counter()
        result = _extract(files, tree, cache)
        extract_seconds = time.perf_counter() - extract_started
        graph, communities = _assemble([result], tree)
        stats = _build_stats(
            repo=repo,
            sha=sha,
            out_path=out_path,
            graph=graph,
            communities=communities,
            files=files,
            root=tree,
            nodes=result.get("nodes", []),
            failed_sources=result.get("failed_sources", []),
            incremental_from=prev_sha,
            communities_inherited=False,
            wall_seconds=time.perf_counter() - started,
            extract_seconds=extract_seconds,
            cache_root=cache,
            n_files_changed=len(dirty),
            n_files_reverse_hop=len(hop),
            n_files_reextracted=len(misses),
        )

    write_graph(
        graph,
        {
            "repo": repo,
            "sha": sha,
            "format_version": GRAPH_FORMAT_VERSION,
            "graphify_commit": stats.graphify_commit,
            "n_nodes": stats.n_nodes,
            "n_edges": stats.n_edges,
            "n_communities": stats.n_communities,
            "parse_failure_rate": stats.parse_failure_rate,
            "communities_inherited": stats.communities_inherited,
            "languages": sorted(SOURCE_SUFFIXES.values()),
        },
        out_path,
    )
    stats_path = out_path.with_suffix("").with_suffix(".stats.json")
    stats_path.write_text(
        json.dumps(stats.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return stats
