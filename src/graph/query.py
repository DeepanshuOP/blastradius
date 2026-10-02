"""The five §10.5 graph query primitives, with a per-(repo, sha) DuckDB cache.

ROADMAP §10.5 (T2.5a) names exactly five primitives, and §10.5's last bullet plus
T2.5b require them cached per `(repo, sha)` in DuckDB with a <100 ms per-instance
benchmark — "recomputing shortest paths per instance is the thing that will make
your pipeline take a week instead of an hour". D-48 was amended to cover both.

| Primitive | Question |
|---|---|
| `shortest_path_length` | how far is this test from this changed file |
| `min_distance_to_any_changed` | the single most predictive feature in the literature |
| `k_hop_neighborhood` | the reachability baseline |
| `same_community` | does the test share a community with the change |
| `pagerank_delta` | how central is the changed set |

**What is cached and what is not.** Only the two expensive, instance-independent
things are: the single-source distance layers from each *changed* node, and the
community partition. Everything else is a dict lookup over those. The cache is
keyed by `(repo, sha, seed_node)` so two instances that touch the same file reuse
one BFS, which is where the saving actually comes from.

Distances are measured on the **undirected projection** of the stored
`MultiDiGraph`. Impact propagation is not a one-way street: a change to a callee
reaches its callers, so a directed traversal from the changed set would miss
exactly the tests that call into it. `with_cochange=False` is the only mode
available here — `co_changes` edges are T2.4, which stays CUT under D-48 — and
the parameter exists so the §10.5 "with and without co_changes" contract has a
place to land without pretending the data is there.

Per D-48 no number computed here reaches `make tables`, `release/` or the paper.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import networkx as nx

from src.graph.build import pagerank

__all__ = [
    "CACHE_SCHEMA_VERSION",
    "GraphQuery",
    "QueryCache",
    "feature_vector",
]

#: Bumped when a cached value's meaning changes, so a stale row is a miss rather
#: than a wrong answer.
CACHE_SCHEMA_VERSION = 1

#: Returned when no path exists. `None` would force every caller to special-case
#: it before arithmetic, and a sentinel that is not a number invites silent
#: coercion; a caller that needs "unreachable" tests for this value explicitly.
UNREACHABLE = -1


@dataclass(frozen=True)
class _Layers:
    """BFS distance layers from one seed node."""

    seed: str
    distance: dict[str, int]


class QueryCache:
    """DuckDB-backed cache for per-(repo, sha) query state.

    One table of blobs keyed by `(repo, sha, kind, seed, version)`. DuckDB is the
    project's system of record (**D-06**, §19.2) and needs no server, so the
    cache ships inside the artifact and a reviewer's `make` run reuses it.

    The connection is opened lazily and closed by `close()` or the context
    manager, so constructing a `GraphQuery` for a graph that answers everything
    from memory never touches disk.
    """

    def __init__(self, path: Path | str | None = Path("data/graphs/query_cache.duckdb")):
        """Open (lazily) a cache at `path`.

        Args:
            path: Database file, or None for an in-memory cache that is
                discarded with the process. Tests use None.
        """
        self._path = None if path is None else Path(path)
        self._connection = None
        self.hits = 0
        self.misses = 0

    def __enter__(self) -> "QueryCache":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def _connect(self):
        """Return the open connection, creating the schema on first use."""
        if self._connection is None:
            import duckdb

            if self._path is not None:
                self._path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = duckdb.connect(
                ":memory:" if self._path is None else str(self._path)
            )
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS query_cache (
                    repo     VARCHAR NOT NULL,
                    sha      VARCHAR NOT NULL,
                    kind     VARCHAR NOT NULL,
                    seed     VARCHAR NOT NULL,
                    version  INTEGER NOT NULL,
                    payload  VARCHAR NOT NULL,
                    PRIMARY KEY (repo, sha, kind, seed, version)
                )
                """
            )
        return self._connection

    def get(self, repo: str, sha: str, kind: str, seed: str = "") -> object | None:
        """Return a cached payload, or None on a miss.

        Args:
            repo: Repo in `owner/name` form.
            sha: The commit the graph was built at.
            kind: What is cached (`"layers"`, `"communities"`, `"pagerank"`).
            seed: The seed node, for per-node entries.

        Returns:
            The decoded payload, or None.
        """
        row = (
            self._connect()
            .execute(
                "SELECT payload FROM query_cache "
                "WHERE repo = ? AND sha = ? AND kind = ? AND seed = ? AND version = ?",
                [repo, sha, kind, seed, CACHE_SCHEMA_VERSION],
            )
            .fetchone()
        )
        if row is None:
            self.misses += 1
            return None
        self.hits += 1
        return json.loads(row[0])

    def put(self, repo: str, sha: str, kind: str, payload: object, seed: str = "") -> None:
        """Store a payload, replacing any entry with the same key.

        Args:
            repo: Repo in `owner/name` form.
            sha: The commit the graph was built at.
            kind: What is cached.
            payload: Any JSON-serialisable value.
            seed: The seed node, for per-node entries.
        """
        self._connect().execute(
            "INSERT OR REPLACE INTO query_cache VALUES (?, ?, ?, ?, ?, ?)",
            [
                repo,
                sha,
                kind,
                seed,
                CACHE_SCHEMA_VERSION,
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
            ],
        )

    def close(self) -> None:
        """Close the connection, if one was opened."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None


class GraphQuery:
    """The §10.5 primitives over one `(repo, sha)` graph.

    Build one per graph and reuse it across the instances at that SHA; that reuse
    is what the latency budget assumes.
    """

    def __init__(
        self,
        graph: nx.MultiDiGraph,
        *,
        repo: str | None = None,
        sha: str | None = None,
        cache: QueryCache | None = None,
    ):
        """Wrap a graph.

        Args:
            graph: A graph from `src.graph.build.load_graph`.
            repo: Repo in `owner/name` form. Defaults to the graph's own `meta`.
            sha: The commit. Defaults to the graph's own `meta`.
            cache: A `QueryCache`, or None to stay in memory for this process.
        """
        meta = dict(graph.graph.get("meta") or {})
        self.graph = graph
        self.repo = repo or str(meta.get("repo") or "")
        self.sha = sha or str(meta.get("sha") or "")
        self.cache = cache
        # Impact propagation runs both ways (a changed callee reaches its
        # callers), so distances are measured on the undirected projection.
        self._undirected = nx.Graph()
        self._undirected.add_nodes_from(graph.nodes())
        self._undirected.add_edges_from((src, dst) for src, dst in graph.edges())
        self._layers: dict[str, _Layers] = {}
        self._communities: dict[str, int] | None = None
        self._pagerank: dict[str, float] | None = None

    # -- state, cached ----------------------------------------------------

    def _layers_from(self, seed: str) -> _Layers:
        """Return BFS distance layers from `seed`, hitting the cache first."""
        if seed in self._layers:
            return self._layers[seed]
        if self.cache is not None and self.repo and self.sha:
            cached = self.cache.get(self.repo, self.sha, "layers", seed)
            if cached is not None:
                layers = _Layers(seed=seed, distance={k: int(v) for k, v in cached.items()})
                self._layers[seed] = layers
                return layers

        distance: dict[str, int] = {}
        if seed in self._undirected:
            distance[seed] = 0
            queue = deque([seed])
            while queue:
                current = queue.popleft()
                for neighbour in self._undirected.neighbors(current):
                    if neighbour not in distance:
                        distance[neighbour] = distance[current] + 1
                        queue.append(neighbour)
        layers = _Layers(seed=seed, distance=distance)
        self._layers[seed] = layers
        if self.cache is not None and self.repo and self.sha:
            self.cache.put(self.repo, self.sha, "layers", distance, seed)
        return layers

    def communities(self) -> dict[str, int]:
        """Return `{node_id: community_id}` from the stored partition.

        The partition is computed once at build time and stored on the nodes, so
        this reads it rather than re-clustering.
        """
        if self._communities is None:
            if self.cache is not None and self.repo and self.sha:
                cached = self.cache.get(self.repo, self.sha, "communities")
                if cached is not None:
                    self._communities = {k: int(v) for k, v in cached.items()}
                    return self._communities
            self._communities = {
                node: int(data["community_id"])
                for node, data in self.graph.nodes(data=True)
                if data.get("community_id") is not None
            }
            if self.cache is not None and self.repo and self.sha:
                self.cache.put(self.repo, self.sha, "communities", self._communities)
        return self._communities

    def pagerank(self) -> dict[str, float]:
        """Return `{node_id: pagerank}` from the stored scores."""
        if self._pagerank is None:
            if self.cache is not None and self.repo and self.sha:
                cached = self.cache.get(self.repo, self.sha, "pagerank")
                if cached is not None:
                    self._pagerank = {k: float(v) for k, v in cached.items()}
                    return self._pagerank
            scores = {
                node: float(data.get("pagerank") or 0.0)
                for node, data in self.graph.nodes(data=True)
            }
            # A graph written before PageRank was stored would read as all
            # zeroes, which is a silently wrong feature rather than a missing
            # one. Recompute in that case.
            if scores and not any(scores.values()):
                scores = pagerank(self.graph)
            self._pagerank = scores
            if self.cache is not None and self.repo and self.sha:
                self.cache.put(self.repo, self.sha, "pagerank", self._pagerank)
        return self._pagerank

    # -- the five primitives ---------------------------------------------

    def shortest_path_length(
        self, changed_file: str, test_node: str, *, with_cochange: bool = False
    ) -> int:
        """Return the hop distance between a changed node and a test node.

        Args:
            changed_file: The changed node's id.
            test_node: The test node's id.
            with_cochange: Include `co_changes` edges. Only False is supported:
                those edges are T2.4, which stays CUT under D-48.

        Returns:
            The number of hops, or `UNREACHABLE` (-1) when no path exists or
            either node is absent.

        Raises:
            NotImplementedError: When `with_cochange` is True.
        """
        if with_cochange:
            raise NotImplementedError(
                "co_changes edges are T2.4, which stays CUT under D-48; "
                "this graph has none, so including them would be a lie"
            )
        if changed_file not in self._undirected or test_node not in self._undirected:
            return UNREACHABLE
        return self._layers_from(changed_file).distance.get(test_node, UNREACHABLE)

    def min_distance_to_any_changed(
        self, test_node: str, changed_set: Iterable[str], *, with_cochange: bool = False
    ) -> int:
        """Return the distance from `test_node` to its nearest changed node.

        The single most predictive graph feature in the test-prioritisation
        literature, which is why it gets its own primitive rather than being
        left to callers to fold.

        Args:
            test_node: The test node's id.
            changed_set: Changed node ids.
            with_cochange: See `shortest_path_length`.

        Returns:
            The smallest hop count, or `UNREACHABLE` when nothing is reachable.
        """
        best = UNREACHABLE
        for changed in sorted(set(changed_set)):
            distance = self.shortest_path_length(
                changed, test_node, with_cochange=with_cochange
            )
            if distance == UNREACHABLE:
                continue
            if best == UNREACHABLE or distance < best:
                best = distance
        return best

    def k_hop_neighborhood(self, changed_set: Iterable[str], k: int) -> set[str]:
        """Return every node within `k` hops of any changed node.

        This is the reachability baseline: "everything the change can reach in
        `k` steps". Includes the changed nodes themselves, at distance 0.

        Args:
            changed_set: Changed node ids.
            k: Hop radius; `k < 0` yields the empty set.

        Returns:
            The reachable node ids.
        """
        if k < 0:
            return set()
        reached: set[str] = set()
        for changed in sorted(set(changed_set)):
            if changed not in self._undirected:
                continue
            for node, distance in self._layers_from(changed).distance.items():
                if distance <= k:
                    reached.add(node)
        return reached

    def same_community(self, test_node: str, changed_set: Iterable[str]) -> bool:
        """Return whether `test_node` shares a community with any changed node.

        Args:
            test_node: The test node's id.
            changed_set: Changed node ids.

        Returns:
            True when at least one changed node is in the same community. False
            when the test node has no community, which is the honest answer for
            a node the partitioner never placed.
        """
        communities = self.communities()
        own = communities.get(test_node)
        if own is None:
            return False
        return any(communities.get(changed) == own for changed in set(changed_set))

    def pagerank_delta(self, changed_set: Iterable[str]) -> float:
        """Return the share of total PageRank mass sitting on the changed set.

        "Centrality of changed nodes" (§10.5). Expressed as a share rather than a
        raw sum so it is comparable across graphs of different sizes: a change to
        a hub scores near 1, a change to a leaf near 0.

        Args:
            changed_set: Changed node ids.

        Returns:
            A value in [0, 1]; 0.0 for an empty changed set or an empty graph.
        """
        scores = self.pagerank()
        total = sum(scores.values())
        if not total:
            return 0.0
        changed = sum(scores.get(node, 0.0) for node in set(changed_set))
        return changed / total

    # -- the full per-instance feature set -------------------------------

    def features(
        self, test_node: str, changed_set: Iterable[str], *, k: int = 3
    ) -> dict[str, float | int | bool]:
        """Return every §10.5 primitive for one (test, changed set) pair.

        This is the unit the §19.4 latency budget is written against: "query
        latency, full feature set per instance ≤ 100 ms".

        Args:
            test_node: The test node's id.
            changed_set: Changed node ids.
            k: Hop radius for the reachability feature.

        Returns:
            The feature dict.
        """
        changed = sorted(set(changed_set))
        neighborhood = self.k_hop_neighborhood(changed, k)
        return {
            "min_distance_to_any_changed": self.min_distance_to_any_changed(
                test_node, changed
            ),
            "in_k_hop_neighborhood": test_node in neighborhood,
            "k_hop_neighborhood_size": len(neighborhood),
            "same_community": self.same_community(test_node, changed),
            "pagerank_delta": self.pagerank_delta(changed),
        }


def feature_vector(
    graph: nx.MultiDiGraph,
    test_node: str,
    changed_set: Iterable[str],
    *,
    k: int = 3,
    cache: QueryCache | None = None,
) -> dict[str, float | int | bool]:
    """Convenience wrapper: the full feature set for one instance.

    Args:
        graph: A graph from `src.graph.build.load_graph`.
        test_node: The test node's id.
        changed_set: Changed node ids.
        k: Hop radius for the reachability feature.
        cache: A `QueryCache`, or None.

    Returns:
        The feature dict.
    """
    return GraphQuery(graph, cache=cache).features(test_node, changed_set, k=k)
