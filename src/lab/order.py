"""The BlastRadius test-case order, from a code graph and the E1 ranking (Live Lab, D-65).

The rule itself is `src/lab/plugin/br_order.py` (stdlib only, so the pytest plugin can apply it while the suite
runs). This module builds its two inputs: the tier of every test file from E1's scores, and the graph hop distance of
every test function to the changed functions. Nothing here calls a model or touches E1.
"""

from __future__ import annotations

from src.lab import graphview
from src.lab.plugin import br_order

RULE_ID, RULE_FIXED, RULE_TEXT = br_order.RULE_ID, br_order.RULE_FIXED, br_order.RULE_TEXT


def tiers_from_rows(rows: list[dict], at_risk_files: list[str]) -> dict[str, int]:
    """Test file -> tier. Files with the same E1 score (as stored in the ranking rows, 4 decimals) share a tier; a
    file the ranking lists without a score goes into a tier after every scored one."""
    score = {r["test"]: float(r["score"]) for r in rows}
    files = list(dict.fromkeys([*at_risk_files, *score]))
    distinct = sorted({s for s in score.values()}, reverse=True)
    tier_of = {s: k for k, s in enumerate(distinct)}
    return {f: tier_of[score[f]] if f in score else len(distinct) for f in files}


def hop_table(view: dict, changed_nodes: list[str]) -> dict[str, int]:
    """`"file::Class::function"` -> hop distance (undirected, unbounded) from the nearest changed node, for every
    reached function node of a test file; plus `"file::*::function"`, the minimum over classes."""
    if not view.get("nodes") or not changed_nodes:
        return {}
    u = graphview.undirected(view)
    dist = graphview.hops_from(u, [c for c in changed_nodes if c in u], limit=10 ** 6)
    by_id = {n["id"]: n for n in view["nodes"]}
    owner: dict[str, str] = {}
    for e in view["edges"]:
        if e["type"] == "contains" and by_id.get(e["source"], {}).get("type") == "class":
            owner[e["target"]] = by_id[e["source"]]["label"]
    out: dict[str, int] = {}
    for n in view["nodes"]:
        if n["type"] not in ("test", "function") or not n.get("is_test_file") or n["id"] not in dist:
            continue
        leaf = n["label"].lstrip(".")
        leaf = leaf[:-2] if leaf.endswith("()") else leaf
        d = dist[n["id"]]
        for k in ((f"{n['file']}::{owner[n['id']]}::{leaf}",) if n["id"] in owner else ()) + (f"{n['file']}::*::{leaf}",):
            out[k] = min(out.get(k, d), d)
    return out


def rule_payload(rows: list[dict], at_risk_files: list[str], view: dict, changed_nodes: list[str]) -> dict:
    """What the pytest plugin needs to run a suite in the rule's order (JSON-serialisable)."""
    return {"id": RULE_ID, "tiers": tiers_from_rows(rows, at_risk_files), "hops": hop_table(view, changed_nodes)}


def derive(results: list[dict], payload: dict) -> list[int]:
    """The rule's order over measured results, as indices into `results`."""
    return br_order.order(results, payload["tiers"], payload["hops"])


def old_order(results: list[dict], native: list[str], at_risk_files: list[str]) -> list[int]:
    """The order before the rule: E1 file rank, pytest's own collection order inside a file (what the plugin did
    until 2026-10-12). `native` is the collection order as node ids; results are matched by node id."""
    rank = {f: k for k, f in enumerate(at_risk_files)}
    pos = {nid: k for k, nid in enumerate(native)}
    file_of = lambda r: (r.get("nodeid") or r["id"]).split("::")[0]  # noqa: E731
    return sorted(range(len(results)), key=lambda i: (rank.get(file_of(results[i]), len(rank)),
                                                      pos.get(results[i].get("nodeid") or "", 10 ** 9), i))
