import json
from pathlib import Path
from typing import Any, Sequence
from dataclasses import dataclass
from src.harvest.rawstore import RawStore, DEFAULT_ROOT

@dataclass
class BaseResolution:
    base_sha: str | None
    base_run_id: int | None
    base_run_distance: int | None
    status: str
    base_time_gap_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.status not in ("exact", "exact_green", "ancestor", "branch_prior", "no_base"):
            raise ValueError(f"invalid resolution status {self.status!r}")
        if self.status == "no_base" and self.base_run_id is not None:
            raise ValueError("base_run_id must be None when status is 'no_base'")
        if self.status == "no_base" and self.base_run_distance is not None:
            raise ValueError("base_run_distance must be None when status is 'no_base'")
        if self.status != "no_base" and self.base_run_id is None:
            raise ValueError(f"base_run_id cannot be None when status is {self.status!r}")
        if self.status in ("exact", "exact_green"):
            # Wait, exact_green can be exact or ancestor. Let's just check exact here.
            pass
        if self.status == "exact" and self.base_run_distance != 0:
            raise ValueError("base_run_distance must be 0 when status is 'exact'")
        if self.status == "ancestor" and self.base_run_distance is not None and self.base_run_distance <= 0:
            raise ValueError("base_run_distance must be positive for 'ancestor'")
        if self.status == "branch_prior" and self.base_run_distance is not None:
            raise ValueError("base_run_distance must be None when status is 'branch_prior'")

    @property
    def can_emit_labels(self) -> bool:
        return self.status != "no_base"

    def require_base_run_id(self) -> int:
        from src.label.base_resolve import NoBaseRunError
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
    runs_cache: dict[tuple[str, str], list[dict]] | None = None,
) -> list[dict]:
    cache_key = (repo, sha)
    if runs_cache is not None and cache_key in runs_cache:
        return runs_cache[cache_key]

    if not store.exists(repo, "runs", sha):
        if runs_cache is not None:
            runs_cache[cache_key] = []
        return []

    try:
        from src.harvest.rawstore import TruncatedRecordError
        recs = store.read_records(repo, "runs", sha)
        if recs and recs[0].body:
            body = json.loads(recs[0].body)
            runs = body.get("workflow_runs", [])
            if runs_cache is not None:
                runs_cache[cache_key] = runs
            return runs
    except Exception:
        pass

    if runs_cache is not None:
        runs_cache[cache_key] = []
    return []

class NoBaseRunError(Exception):
    pass

def parse_iso(ts: str) -> float:
    import datetime
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.datetime.fromisoformat(ts).timestamp()

def _get_head_info(repo, head_sha, run_id, store, runs_cache):
    head_runs = _get_runs_for_sha(repo, head_sha, store, runs_cache)
    for r in head_runs:
        if r.get("id") == run_id:
            return r
    return None

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
    branch_prior_index: dict[str, list[dict]] | None = None, # repo -> sorted list of runs
) -> BaseResolution:
    if store is None:
        store = RawStore(raw_root)

    head_run = _get_head_info(repo, head_sha, run_id, store, runs_cache)

    if workflow_id is None:
        if head_run:
            workflow_id = head_run.get("workflow_id")

    if workflow_id is None:
        return BaseResolution(base_sha=base_sha, base_run_id=None, base_run_distance=None, status="no_base")

    if not base_sha and head_run:
        prs = head_run.get("pull_requests", [])
        if prs and isinstance(prs[0], dict):
            base_obj = prs[0].get("base") or {}
            base_sha = base_obj.get("sha")

    # 1 & 2 & 3. Exact and Ancestor logic at base_sha
    if base_sha:
        if commit_graph is None:
            commit_graph = build_commit_graph(repo, raw_root, store)
        if run_index is None:
            run_index = build_run_index(repo, raw_root, store)
            
        curr_sha = base_sha
        dist = 0
        while curr_sha and dist <= max_ancestor_distance:
            anc_runs = list(run_index.get(curr_sha, []))
            anc_runs.extend(_get_runs_for_sha(repo, curr_sha, store, runs_cache))
            
            seen = set()
            dedup_anc = []
            for r in anc_runs:
                if r.get('id') not in seen:
                    seen.add(r.get('id'))
                    dedup_anc.append(r)
                    
            anc_matches = [r for r in dedup_anc if r.get("workflow_id") == workflow_id and r.get("id") != run_id]
            if anc_matches:
                best_anc_run = max(anc_matches, key=lambda r: r.get("run_started_at") or r.get("created_at") or "")
                conclusion = best_anc_run.get("conclusion")
                
                # Check for exact vs ancestor
                if conclusion == "success":
                    status = "exact_green"
                else:
                    status = "exact" if dist == 0 else "ancestor"
                    
                return BaseResolution(
                    base_sha=curr_sha,
                    base_run_id=int(best_anc_run["id"]),
                    base_run_distance=dist,
                    status=status
                )
                
            parents = commit_graph.get(curr_sha, [])
            curr_sha = parents[0] if parents else None
            dist += 1

    # 4. branch_prior fallback
    if branch_prior_index is not None and repo in branch_prior_index and head_run:
        head_ts_str = head_run.get("run_started_at") or head_run.get("created_at")
        if head_ts_str:
            head_ts = parse_iso(head_ts_str)
            sorted_runs = branch_prior_index[repo]
            
            # Extract base_ref from PR metadata if possible
            base_ref = None
            prs = head_run.get("pull_requests", [])
            if prs and isinstance(prs[0], dict):
                base_ref = prs[0].get("base", {}).get("ref")
            
            # Binary search for the latest run strictly before head_ts
            # Wait, Python bisect works on keys.
            import bisect
            # To find strictly before, we can bisect_left and then step back.
            # We also need to match workflow_id and base_ref (if available).
            # But the list could contain other workflows/branches.
            # It's better to filter during indexing or just walk backwards from the bisect point.
            idx = bisect.bisect_left(sorted_runs, head_ts, key=lambda r: r["_ts"])
            for i in range(idx - 1, -1, -1):
                r = sorted_runs[i]
                if r.get("workflow_id") != workflow_id:
                    continue
                # If we have base_ref, require it to match head_branch of the run
                if base_ref and r.get("head_branch") != base_ref:
                    continue
                
                # Found it!
                conclusion = r.get("conclusion")
                status = "exact_green" if conclusion == "success" else "branch_prior"
                return BaseResolution(
                    base_sha=r.get("head_sha"),
                    base_run_id=int(r["id"]),
                    base_run_distance=None,
                    status=status,
                    base_time_gap_seconds=head_ts - r["_ts"]
                )

    return BaseResolution(base_sha=base_sha, base_run_id=None, base_run_distance=None, status="no_base")
