"""Base-run resolution for broken-trunk filtering and ground-truth labelling.

Per ROADMAP §21.3 (T1.3a) and Invariant 6 (§5):
An empty base failure set is NEVER "base was green". If no base run is found,
status="no_base" makes it structurally impossible for a caller to emit labels.

Resolution Strategy:
1. "exact": A run of the SAME workflow_id exists at base_sha (base_run_distance = 0).
2. "ancestor": Nearest ancestor commit of base_sha with a run of the same workflow_id
   (base_run_distance = number of commit hops, up to max_distance=10).
3. "no_base": No matching workflow run found at base_sha or any inspected ancestor
   within max_distance. base_run_id is None, base_run_distance is None.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.harvest.rawstore import RawStore, DEFAULT_ROOT, TruncatedRecordError

__all__ = [
    "BaseResolution",
    "NoBaseRunError",
    "resolve_base_run",
    "build_commit_graph",
]

_logger = logging.getLogger(__name__)


class NoBaseRunError(Exception):
    """Raised when attempting to access a base run ID or emit labels from a no_base resolution."""


@dataclass(frozen=True)
class BaseResolution:
    """Outcome of resolving a base workflow run for an instance.
    
    Attributes:
        base_sha: The base commit SHA (or ancestor commit SHA where base run was found).
        base_run_id: The resolved workflow run ID on the base side (None for 'no_base').
        base_run_distance: Commit hops from original base_sha (0 for exact, >0 for ancestor, None for no_base).
        status: One of 'exact', 'ancestor', or 'no_base'.
    """
    base_sha: str | None
    base_run_id: int | None
    base_run_distance: int | None
    status: str  # "exact" | "ancestor" | "no_base"

    def __post_init__(self) -> None:
        if self.status not in ("exact", "ancestor", "no_base"):
            raise ValueError(
                f"invalid resolution status: {self.status!r}; must be 'exact', 'ancestor', or 'no_base'"
            )
        if self.status == "no_base":
            if self.base_run_id is not None:
                raise ValueError("base_run_id must be None when status is 'no_base'")
            if self.base_run_distance is not None:
                raise ValueError("base_run_distance must be None when status is 'no_base'")
        elif self.status == "exact":
            if self.base_run_id is None:
                raise ValueError("base_run_id cannot be None when status is 'exact'")
            if self.base_run_distance != 0:
                raise ValueError(
                    f"base_run_distance must be 0 for 'exact', got {self.base_run_distance}"
                )
        elif self.status == "ancestor":
            if self.base_run_id is None:
                raise ValueError("base_run_id cannot be None when status is 'ancestor'")
            if self.base_run_distance is None or self.base_run_distance <= 0:
                raise ValueError(
                    f"base_run_distance must be positive integer for 'ancestor', got {self.base_run_distance}"
                )

    @property
    def can_emit_labels(self) -> bool:
        """Return True if and only if a valid base run was resolved."""
        return self.status in ("exact", "ancestor") and self.base_run_id is not None

    def require_base_run_id(self) -> int:
        """Return the resolved base_run_id or raise NoBaseRunError.
        
        Enforces Invariant 6: callers cannot accidentally treat an unresolved
        base as a green base with 0 failures.
        """
        if not self.can_emit_labels or self.base_run_id is None:
            raise NoBaseRunError(
                f"Cannot emit labels: base run unresolved (status={self.status!r}, "
                f"base_sha={self.base_sha!r})"
            )
        return self.base_run_id


def build_commit_graph(
    repo: str,
    raw_root: Path | str = DEFAULT_ROOT,
    store: RawStore | None = None,
) -> dict[str, list[str]]:
    """Build a commit -> [parent_sha, ...] map for a repository from pull_commits payloads."""
    if store is None:
        store = RawStore(raw_root)
    root = Path(raw_root)
    owner, name = repo.split("/")
    pr_dir = root / f"{owner}__{name}" / "pr"
    
    commit_parents: dict[str, list[str]] = {}
    if not pr_dir.is_dir():
        return commit_parents

    for pf in pr_dir.glob("**/*pull_commits.jsonl.gz"):
        try:
            pnum = int(pf.parent.name)
            recs = store.read_records(repo, "pull_commits", pnum)
            for rec in recs:
                if not rec.body:
                    continue
                commits = json.loads(rec.body)
                for c in commits:
                    csha = c.get("sha")
                    parents = [p.get("sha") for p in c.get("parents", []) if p.get("sha")]
                    if csha and parents:
                        commit_parents[csha] = parents
        except (TruncatedRecordError, ValueError, OSError) as exc:
            _logger.debug("Skipping unreadable pull_commits %s: %s", pf, exc)
            continue

    return commit_parents


def _get_runs_for_sha(
    repo: str,
    sha: str,
    store: RawStore,
    runs_cache: dict[tuple[str, str], list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Retrieve list of workflow run dicts for (repo, sha), using optional cache."""
    cache_key = (repo, sha)
    if runs_cache is not None and cache_key in runs_cache:
        return runs_cache[cache_key]

    if not store.exists(repo, "runs", sha):
        if runs_cache is not None:
            runs_cache[cache_key] = []
        return []

    try:
        recs = store.read_records(repo, "runs", sha)
        if recs and recs[0].body:
            body = json.loads(recs[0].body)
            runs = body.get("workflow_runs", [])
            if runs_cache is not None:
                runs_cache[cache_key] = runs
            return runs
    except (TruncatedRecordError, json.JSONDecodeError, OSError) as exc:
        _logger.debug("Could not read runs for %s @ %s: %s", repo, sha, exc)

    if runs_cache is not None:
        runs_cache[cache_key] = []
    return []


def resolve_base_run(
    repo: str,
    head_sha: str,
    run_id: int,
    workflow_id: int | None = None,
    base_sha: str | None = None,
    pr_number: int | None = None,
    raw_root: Path | str = DEFAULT_ROOT,
    store: RawStore | None = None,
    commit_graph: Mapping[str, Sequence[str]] | None = None,
    runs_cache: dict[tuple[str, str], list[dict[str, Any]]] | None = None,
    max_ancestor_distance: int = 10,
) -> BaseResolution:
    """Resolve the baseline workflow run for a given workflow run instance.
    
    Args:
        repo: Repository name in 'owner/repo' format.
        head_sha: Commit SHA of the head run.
        run_id: Workflow run ID of the head instance.
        workflow_id: Target workflow ID that base run must match.
        base_sha: Optional base commit SHA. If None, looked up from raw store.
        pr_number: Optional PR number for context.
        raw_root: Path to raw data directory root.
        store: Optional pre-instantiated RawStore.
        commit_graph: Optional pre-built commit -> parents mapping for fast batch resolution.
        runs_cache: Optional cache mapping (repo, sha) -> list of workflow_run dicts.
        max_ancestor_distance: Maximum commit hops to walk when searching for ancestor base run (default 10).
        
    Returns:
        BaseResolution with status "exact", "ancestor", or "no_base".
    """
    if store is None:
        store = RawStore(raw_root)

    # 1. If workflow_id is missing, derive it from head_sha runs payload
    if workflow_id is None:
        head_runs = _get_runs_for_sha(repo, head_sha, store, runs_cache)
        for r in head_runs:
            if r.get("id") == run_id:
                workflow_id = r.get("workflow_id")
                break

    if workflow_id is None:
        return BaseResolution(
            base_sha=base_sha,
            base_run_id=None,
            base_run_distance=None,
            status="no_base",
        )

    # 2. If base_sha is missing, try to locate from run pull_requests or PR metadata
    if not base_sha:
        head_runs = _get_runs_for_sha(repo, head_sha, store, runs_cache)
        for r in head_runs:
            if r.get("id") == run_id:
                prs = r.get("pull_requests", [])
                if prs and isinstance(prs[0], dict):
                    base_obj = prs[0].get("base") or {}
                    base_sha = base_obj.get("sha")
                break

    if not base_sha:
        return BaseResolution(
            base_sha=None,
            base_run_id=None,
            base_run_distance=None,
            status="no_base",
        )

    # 3. Check for exact match at base_sha
    base_runs = _get_runs_for_sha(repo, base_sha, store, runs_cache)
    exact_matches = [r for r in base_runs if r.get("workflow_id") == workflow_id]
    if exact_matches:
        best_run = max(
            exact_matches,
            key=lambda r: r.get("run_started_at") or r.get("created_at") or "",
        )
        return BaseResolution(
            base_sha=base_sha,
            base_run_id=int(best_run["id"]),
            base_run_distance=0,
            status="exact",
        )

    # 4. Check ancestors of base_sha up to max_ancestor_distance
    if commit_graph is None:
        commit_graph = build_commit_graph(repo, raw_root=raw_root, store=store)

    curr_sha = base_sha
    dist = 0
    while curr_sha in commit_graph and dist < max_ancestor_distance:
        parents = commit_graph[curr_sha]
        if not parents:
            break
        curr_sha = parents[0]
        dist += 1
        anc_runs = _get_runs_for_sha(repo, curr_sha, store, runs_cache)
        anc_matches = [r for r in anc_runs if r.get("workflow_id") == workflow_id]
        if anc_matches:
            best_anc_run = max(
                anc_matches,
                key=lambda r: r.get("run_started_at") or r.get("created_at") or "",
            )
            return BaseResolution(
                base_sha=curr_sha,
                base_run_id=int(best_anc_run["id"]),
                base_run_distance=dist,
                status="ancestor",
            )

    # 5. No base run found
    return BaseResolution(
        base_sha=base_sha,
        base_run_id=None,
        base_run_distance=None,
        status="no_base",
    )
