# write graph to HTML and NetworkX node-link JSON
from __future__ import annotations
import hashlib
import html as _html
import json
import math
import os
import re
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path
import networkx as nx
from networkx.readwrite import json_graph
from graphify.security import sanitize_label
from graphify.analyze import _node_community_map
from graphify.build import edge_data
from graphify.paths import stem_filename_budget



# Artifacts worth preserving across rebuilds (non-regenerable without LLM or curation).
_BACKUP_ARTIFACTS = [
    "graph.json",
    "GRAPH_REPORT.md",
    ".graphify_labels.json",
    ".graphify_analysis.json",
    "manifest.json",
    ".graphify_semantic_marker",
    "cost.json",
]


def backup_if_protected(out_dir: Path) -> "Path | None":
    """Snapshot graph artifacts to a dated subfolder before an overwrite.

    Triggers when graph.json exists AND either:
    - .graphify_semantic_marker is present (graph cost real LLM tokens), or
    - .graphify_labels.json contains at least one non-default community label
      (graph has been curated by a human or skill).

    Returns the backup folder path, or None if no backup was taken.
    Never raises — backup failure prints a warning but never blocks the write.
    Set GRAPHIFY_NO_BACKUP=1 to disable.
    """
    if os.environ.get("GRAPHIFY_NO_BACKUP"):
        return None
    out = Path(out_dir)
    if not (out / "graph.json").exists():
        return None

    is_semantic = (out / ".graphify_semantic_marker").exists()
    is_curated = False
    labels_file = out / ".graphify_labels.json"
    if labels_file.exists():
        try:
            labels = json.loads(labels_file.read_text(encoding="utf-8"))
            is_curated = any(v != f"Community {k}" for k, v in labels.items())
        except Exception:
            pass

    if not is_semantic and not is_curated:
        return None

    reason = "+".join(filter(None, ["semantic" if is_semantic else "", "curated" if is_curated else ""]))
    today = date.today().isoformat()
    backup_dir = out / today
    graph_src = out / "graph.json"

    # Skip re-copying if today's backup already has identical graph.json content.
    # If content differs (graph changed since the last backup today), overwrite
    # the backup in place — one folder per day, always the latest pre-overwrite state.
    if backup_dir.exists() and (backup_dir / "graph.json").exists():
        src_hash = hashlib.sha256(graph_src.read_bytes()).hexdigest()
        bak_hash = hashlib.sha256((backup_dir / "graph.json").read_bytes()).hexdigest()
        if src_hash == bak_hash:
            return backup_dir  # identical content, nothing to do

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        for name in _BACKUP_ARTIFACTS:
            src = out / name
            if src.exists():
                try:
                    shutil.copy2(src, backup_dir / name)
                    copied += 1
                except Exception:
                    pass
        if copied:
            print(f"[graphify] backed up {reason} graph ({copied} files) -> {backup_dir.name}/")
        return backup_dir
    except Exception as exc:
        import sys
        print(f"[graphify] warning: backup failed ({exc}) - continuing with overwrite", file=sys.stderr)
        return None
def _strip_diacritics(text: str | None) -> str:
    import unicodedata
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))
from graphify.exporters.base import COMMUNITY_COLORS  # noqa: E402,F401

from graphify.exporters.html import to_html  # noqa: E402,F401


_CONFIDENCE_SCORE_DEFAULTS = {"EXTRACTED": 1.0, "INFERRED": 0.5, "AMBIGUOUS": 0.2}


def attach_hyperedges(G: nx.Graph, hyperedges: list) -> None:
    """Store hyperedges in the graph's metadata dict."""
    existing = G.graph.get("hyperedges", [])
    # Skip id-less persisted entries when seeding the dedup set (#2775): the
    # semantic extractor emits hyperedges with no `id` and build.py persists them
    # verbatim, so a prior graph.json can contain id-less hyperedges. A hard
    # `h["id"]` here raised `KeyError: 'id'` on every incremental re-extract,
    # symmetric with the `.get("id")` guard the loop below already applies to the
    # incoming set.
    seen_ids = {h["id"] for h in existing if h.get("id")}
    for h in hyperedges:
        if h.get("id") and h["id"] not in seen_ids:
            existing.append(h)
            seen_ids.add(h["id"])
    G.graph["hyperedges"] = existing


def _git_head(cwd: "str | Path | None" = None) -> str | None:
    """Return git HEAD for the repo containing ``cwd``, or None outside a repo.

    ``cwd`` selects the repository to ask, exactly as in watch._git_head
    (#2316). Without it the command inherits the caller's working directory,
    which stamps the *invoking* repo's commit when the graph being written
    describes a different repo — provenance must come from the repo the graph
    describes, so callers pass the graph's own location.
    """
    import subprocess as _sp
    try:
        r = _sp.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=3,
            cwd=str(cwd) if cwd is not None else None,
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


# Sentinel: an existing graph.json is present and non-empty but cannot be parsed
# into a node count (corrupt, mid-write, or structurally wrong). The caller must
# fail CLOSED on this — the same way to_json's #479 guard refuses to overwrite
# such a file — because we cannot prove the new graph isn't a silent shrink.
MALFORMED_GRAPH = object()


def existing_graph_node_count(path: "str | Path"):
    """Node count of an existing graph.json.

    Returns:
      - an ``int`` node count when the file parses;
      - ``None`` when there is verifiably nothing to protect — absent, empty, or
        over the size cap (matching how :func:`to_json` lets the new graph
        replace an empty/oversized file);
      - :data:`MALFORMED_GRAPH` when the file is present and non-empty but
        unparseable — the caller must treat this as fail-closed (refuse to
        overwrite), mirroring to_json's #479 handling of a corrupt/mid-write file.

    The raw ``--no-cluster`` write path uses this to apply the same #479 shrink
    guard that :func:`to_json` applies inline for the clustered path.
    """
    p = Path(path)
    if not p.exists():
        return None
    from graphify.security import check_graph_file_size_cap
    try:
        check_graph_file_size_cap(p)
    except Exception:
        # Oversized: reading it to compare would be the DoS the cap guards against.
        return None
    try:
        raw = p.read_text(encoding="utf-8")
    except Exception:
        # Present but unreadable: fail closed if it has bytes, else nothing to lose.
        try:
            return MALFORMED_GRAPH if p.stat().st_size > 0 else None
        except Exception:
            return None
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return MALFORMED_GRAPH
    nodes = data.get("nodes") if isinstance(data, dict) else None
    return len(nodes) if isinstance(nodes, list) else MALFORMED_GRAPH


def to_json(G: nx.Graph, communities: dict[int, list[str]], output_path: str, *, force: bool = False, built_at_commit: str | None = None, community_labels: dict[int, str] | None = None) -> bool:
    # Safety check: refuse to silently shrink an existing graph (#479)
    existing_path = Path(output_path)
    if not force and existing_path.exists():
        from graphify.security import check_graph_file_size_cap
        try:
            check_graph_file_size_cap(existing_path)
        except Exception:
            # Existing graph.json trips the size cap; reading it to compare would
            # be the very DoS the cap guards against. Can't verify — let the new
            # graph replace the oversized file.
            oversized = True
        else:
            oversized = False
        if not oversized:
            try:
                raw = existing_path.read_text(encoding="utf-8")
            except Exception:
                raw = ""
            if not raw.strip():
                # Empty/whitespace existing file (e.g. a freshly touched path):
                # no nodes to lose, so any new graph is a growth — proceed.
                existing_n = 0
            else:
                try:
                    existing_data = json.loads(raw)
                    existing_n = len(existing_data.get("nodes", []))
                except Exception as exc:
                    # Non-empty but unparseable existing graph (corrupt or a
                    # mid-write): we cannot verify the new graph is not a silent
                    # shrink. Fail SAFE — refuse rather than overwrite. A
                    # fail-OPEN here (the prior behavior) is the silent data-loss
                    # path #479 exists to prevent: a transiently unreadable
                    # graph.json would let a partial rebuild clobber a good one.
                    import sys as _sys
                    print(
                        f"[graphify] WARNING: existing {existing_path} could not be "
                        f"read to verify the new graph is not smaller ({exc}). "
                        f"Refusing to overwrite; pass force=True to override.",
                        file=_sys.stderr,
                    )
                    return False
            new_n = G.number_of_nodes()
            if new_n < existing_n:
                import sys as _sys
                print(
                    f"[graphify] WARNING: new graph has {new_n} nodes but existing "
                    f"graph.json has {existing_n} (net -{existing_n - new_n}). "
                    f"Refusing to overwrite. Possible causes: missing chunk files from "
                    f"a previous session, or fuzzy dedup collapsed same-named symbols "
                    f"across files during an --update on an already-current graph. "
                    f"Run a full rebuild (/graphify .) to be safe, or pass force=True "
                    f"only if you have verified the reduction is legitimate.",
                    file=_sys.stderr,
                )
                return False

    node_community = _node_community_map(communities)
    _labels: dict[int, str] = {int(k): v for k, v in (community_labels or {}).items()}
    try:
        data = json_graph.node_link_data(G, edges="links")
    except TypeError:
        data = json_graph.node_link_data(G)

    def _json_sort_key(item: dict) -> str:
        return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    for node in data["nodes"]:
        cid = node_community.get(node["id"])
        node["community"] = cid
        if cid is not None and _labels:
            node["community_name"] = _labels.get(cid, f"Community {cid}")
        node["norm_label"] = _strip_diacritics(node.get("label", "")).lower()
    for link in data["links"]:
        if "confidence_score" not in link:
            conf = link.get("confidence", "EXTRACTED")
            link["confidence_score"] = _CONFIDENCE_SCORE_DEFAULTS.get(conf, 1.0)
        # Restore original edge direction. Undirected NetworkX storage may
        # canonicalize endpoint order, flipping `calls` and other directional
        # edges in graph.json. The build path stashes the true endpoints in
        # _src/_tgt for exactly this purpose (#563).
        true_src = link.pop("_src", None)
        true_tgt = link.pop("_tgt", None)
        if true_src is not None and true_tgt is not None:
            link["source"] = true_src
            link["target"] = true_tgt
    data["nodes"].sort(key=_json_sort_key)
    data["links"].sort(key=_json_sort_key)
    if "hyperedges" not in getattr(G, "graph", {}):
        # Hardening (#2485): a graph with NO hyperedges key at all was built by
        # a path that never engaged hyperedge metadata — distinct from an
        # intentional empty set ([], which build_from_json now stores
        # explicitly after a full-wipeout revalidation). If the file on disk
        # already holds a non-empty set, emptying it without a trace is silent
        # data loss; warn loudly so the wipeout is attributable. We still write
        # the graph's truth rather than preserving the stale set — resurrecting
        # hyperedges whose members may no longer exist would reintroduce the
        # dangling-member shape #1916 removed.
        _prev_hyperedges = None
        try:
            if existing_path.exists():
                from graphify.security import check_graph_file_size_cap
                check_graph_file_size_cap(existing_path)
                _prev = json.loads(existing_path.read_text(encoding="utf-8"))
                if isinstance(_prev, dict):
                    _prev_hyperedges = _prev.get("hyperedges")
        except Exception:
            _prev_hyperedges = None
        if _prev_hyperedges:
            print(
                f"[graphify] WARNING: graph carries no hyperedge metadata but "
                f"{existing_path} already holds {len(_prev_hyperedges)} "
                f"hyperedge(s); writing an empty set. Rebuild from the original "
                f"extraction if this is unexpected.",
                file=sys.stderr,
            )
    hyperedges = sorted(getattr(G, "graph", {}).get("hyperedges", []), key=_json_sort_key)
    if isinstance(data.get("graph"), dict) and "hyperedges" in data["graph"]:
        data["graph"]["hyperedges"] = hyperedges
    data["hyperedges"] = hyperedges
    # Fallback provenance comes from the repo the graph is being written INTO
    # (output_path lives in <target>/graphify-out/), never the shell's cwd —
    # the same cwd-anchoring mistake #2316 fixed for `update`.
    commit = built_at_commit if built_at_commit is not None else _git_head(Path(output_path).resolve().parent)
    if commit:
        data["built_at_commit"] = commit
    from graphify.paths import write_json_atomic
    # Atomic write: a crash/ENOSPC mid-write must not truncate a good graph.json.
    write_json_atomic(output_path, data, indent=2)
    return True


def prune_dangling_edges(graph_data: dict) -> tuple[dict, int]:
    """Remove edges whose source or target node is not in the node set.

    Returns the cleaned graph_data dict and the number of pruned edges.
    """
    node_ids = {n["id"] for n in graph_data["nodes"]}
    links_key = "links" if "links" in graph_data else "edges"
    before = len(graph_data[links_key])
    graph_data[links_key] = [
        e for e in graph_data[links_key]
        if e["source"] in node_ids and e["target"] in node_ids
    ]
    return graph_data, before - len(graph_data[links_key])
_CYPHER_IDENT_RE = re.compile(r"[^A-Za-z0-9_]")
generate_html = to_html
_DEDUP_SUFFIX_RESERVE = 5

# Prefix the community overview notes carry ("_COMMUNITY_Backend.md").
_COMMUNITY_PREFIX = "_COMMUNITY_"
