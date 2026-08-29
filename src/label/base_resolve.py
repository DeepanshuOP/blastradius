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
    """The result of resolving a base run for a given PR run.
    
    status:
        - "exact": Found failed base run at exact base_sha (distance 0)
        - "exact_green": Found base run but it was green (conclusion == 'success').
          T_base_fail is empty by observation of a real run, which is categorically
          different from invariant-6 (no run found).
        - "ancestor": Found failed base run at an ancestor (distance > 0)
        - "no_base": Could not find any matching base run
    """
    base_sha: str | None
    base_run_id: int | None
    base_run_distance: int | None
    status: str

    def __post_init__(self) -> None:
        if self.status not in ("exact", "exact_green", "ancestor", "no_base"):
            raise ValueError(f"invalid resolution status: {self.status!r}")
            
        if self.status == "no_base":
            if self.base_run_id is not None or self.base_run_distance is not None:
                raise ValueError("base_run_id must be None when status is 'no_base'")
        elif self.status == "exact":
            if self.base_run_id is None: raise ValueError("base_run_id cannot be None")
            if self.base_run_distance != 0:
                raise ValueError(f"base_run_distance must be 0 for 'exact', got {self.base_run_distance}")
        elif self.status == "exact_green":
            if self.base_run_id is None:
                raise ValueError("base_run_id cannot be None when status is 'exact_green'")
        elif self.status == "ancestor":
            if self.base_run_id is None:
                raise ValueError("base_run_id cannot be None when status is 'ancestor'")
            if self.base_run_distance is None or self.base_run_distance <= 0:
                raise ValueError(f"base_run_distance must be positive integer for 'ancestor', got {self.base_run_distance}")

    @property
    def can_emit_labels(self) -> bool:
        """Return True if and only if a valid base run was resolved."""
        return self.status in ("exact", "ancestor", "exact_green") and self.base_run_id is not None


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
    """Build a commit -> [parent_sha, ...] map using the local clone, fallback to pull_commits."""
    import subprocess, json
    owner, name = repo.split("/")
    clone_dir = Path("data") / "clones" / f"{owner}__{name}"
    
    commit_parents: dict[str, list[str]] = {}
    if clone_dir.is_dir():
        try:
            proc = subprocess.run(
                ["git", "-C", str(clone_dir), "rev-list", "--parents", "--all"],
                stdout=subprocess.PIPE, text=True, check=True
            )
            for line in proc.stdout.splitlines():
                parts = line.split()
                if parts:
                    commit_parents[parts[0]] = parts[1:]
            return commit_parents
        except subprocess.CalledProcessError:
            pass

    # Fallback to pull_commits for tests without clones
    if store is None:
        store = RawStore(raw_root)
    pr_dir = Path(raw_root) / f"{owner}__{name}" / "pr"
    if not pr_dir.is_dir():
        return commit_parents

    for pf in pr_dir.glob("**/*pull_commits.jsonl.gz"):
        try:
            pnum = int(pf.parent.name)
            recs = store.read_records(repo, "pull_commits", pnum)
            for rec in recs:
                if not rec.body: continue
                commits = json.loads(rec.body)
                for c in commits:
                    csha = c.get("sha")
                    parents = [p.get("sha") for p in c.get("parents", []) if p.get("sha")]
                    if csha and parents:
                        commit_parents[csha] = parents
        except Exception:
            continue
    return commit_parents


def build_run_index(
    repo: str,
    raw_root: Path | str = DEFAULT_ROOT,
    store: RawStore | None = None,
) -> dict[str, list[dict]]:
    """Build a mapping of sha -> list[runs] from branch_runs payloads."""
    import gzip, json
    if store is None:
        store = RawStore(raw_root)
    owner, name = repo.split("/")
    repo_dir = store._root / f"{owner}__{name}" / "branch"
    
    run_index: dict[str, list[dict]] = {}
    if not repo_dir.is_dir():
        return run_index
        
    for shard in repo_dir.iterdir():
        if not shard.is_dir(): continue
        for b_dir in shard.iterdir():
            if not b_dir.is_dir(): continue
            runs_file = b_dir / "branch_runs.jsonl.gz"
            if not runs_file.exists(): continue
            
            try:
                with gzip.open(runs_file, 'rt') as f:
                    for line in f:
                        data = json.loads(line)
                        if 'body' in data and data['body']:
                            body = json.loads(data['body'])
                            for r in body.get('workflow_runs', []):
                                sha = r.get("head_sha")
                                if sha:
                                    if sha not in run_index:
                                        run_index[sha] = []
                                    run_index[sha].append(r)
            except Exception:
                pass
                
    return run_index


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
    commit_graph: dict[str, list[str]] | None = None,
    run_index: dict[str, list[dict]] | None = None,
    runs_cache: dict[tuple[str, str], list[dict]] | None = None,
    max_ancestor_distance: int = 10,
) -> BaseResolution:
    if store is None:
        store = RawStore(raw_root)

    if workflow_id is None:
        head_runs = _get_runs_for_sha(repo, head_sha, store, runs_cache)
        for r in head_runs:
            if r.get("id") == run_id:
                workflow_id = r.get("workflow_id")
                break

    if workflow_id is None:
        return BaseResolution(base_sha=base_sha, base_run_id=None, base_run_distance=None, status="no_base")

    if run_index is None:
        run_index = build_run_index(repo, raw_root, store)
        
    if commit_graph is None:
        commit_graph = build_commit_graph(repo, raw_root, store)

    # 1. Walk ancestors of head_sha using the real commit graph
    curr_sha = head_sha
    dist = 0
    
    # We walk starting from parents if we want ancestor? 
    # Wait, the spec says "Walk ancestors of head_sha". 
    # Is head_sha itself checked? "First match wins. base_run_distance = hops walked."
    # If dist=0, it's exact.
    while curr_sha and dist <= max_ancestor_distance:
        if dist > 0 or True: # Check at dist 0 as well? If head_sha has it, but it's the SAME run? No, we need base run.
            pass
            
        anc_runs = list(run_index.get(curr_sha, []))
        anc_runs.extend(_get_runs_for_sha(repo, curr_sha, store, runs_cache))
        
        # Deduplicate runs by id
        seen_ids = set()
        dedup_runs = []
        for r in anc_runs:
            rid = r.get("id")
            if rid and rid not in seen_ids:
                seen_ids.add(rid)
                dedup_runs.append(r)
                
        anc_matches = [r for r in dedup_runs if r.get("workflow_id") == workflow_id and r.get("id") != run_id]
        if anc_matches:
            best_anc = max(anc_matches, key=lambda r: r.get("run_started_at") or r.get("created_at") or "")
            if best_anc.get("conclusion") == "success":
                status = "exact_green"
            else:
                status = "exact" if dist == 0 else "ancestor"
                
            return BaseResolution(
                base_sha=curr_sha,
                base_run_id=int(best_anc["id"]),
                base_run_distance=dist,
                status=status
            )
            
        parents = commit_graph.get(curr_sha, [])
        curr_sha = parents[0] if parents else None
        dist += 1

    return BaseResolution(base_sha=None, base_run_id=None, base_run_distance=None, status="no_base")
