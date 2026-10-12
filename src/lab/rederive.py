"""Re-derive the BlastRadius order and the arena of a recording made before the test-case rule (2026-10-12).

A recording stores every executed case with its measured duration, the graph of its base commit and the E1 ranking.
That is enough to apply the rule offline: the BlastRadius lane of the race and the BlastRadius row of the arena are
recomputed from the stored results (nothing is run), co-change is computed from the pin's upstream history when it can
be fetched, and the earlier numbers are kept next to the new ones as `order_rule.before`. Every event this touches is
marked `rederived`, and the run header says which events were rewritten. Events a rule cannot change (the model's
reply, the checks, the comment as posted) are left exactly as recorded.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.lab import arena, engine, order as case_order
from src.lab.events import now_iso

FAILED = ("failed", "error")


def _before(lane: dict) -> dict:
    return {"first_failure_position": lane["first_failure_position"], "first_failure_ms": lane["elapsed_to_first_failure_ms"],
            "basis": "as recorded: the order pytest ran (E1 file rank, then pytest's collection order)"}


def rederive_events(events: list[dict], view: dict, *, coverage: dict | None, cochange: tuple, cochange_info: dict) -> list[dict]:
    """The recording's events with `tests.race` and `arena.result` rewritten by the rule (inserted when absent)."""
    ev = [dict(e) for e in events]
    results = [e["data"] for e in ev if e["type"] == "test.result"]
    ranking = next(e["data"] for e in ev if e["type"] == "impact.ranking")
    change = next(e["data"] for e in ev if e["type"] == "change.applied")
    at_risk = ranking["at_risk_files"]
    rule = case_order.rule_payload(ranking["rows"], at_risk, view, change["changed_nodes"])

    i_race = next((k for k, e in enumerate(ev) if e["type"] == "tests.race"), None)
    if i_race is None:
        raise ValueError("no tests.race event: this recording did not run the suite")
    old_race = ev[i_race]["data"]
    old_risk = next(l for l in old_race["lanes"] if l["name"] == "risk-first")
    rc = engine.race(results, at_risk, None, rule, None, derived=True)
    rc["order_rule"]["before"] = _before(old_risk)
    ev[i_race] = {**ev[i_race], "data": rc, "rederived": True}

    n_failing = sum(1 for r in results if r["outcome"] in FAILED)
    old_arena = next((e["data"] for e in ev if e["type"] == "arena.result"), None)
    doc = arena.compute(results, order_files=at_risk, view=view, changed_nodes=change["changed_nodes"],
                        changed_fns=change["changed_functions"], coverage=coverage, history=[], cochange=cochange,
                        rule=rule, cochange_info=cochange_info)
    rows = {s["id"]: s for s in doc["strategies"]}
    hist_note = "this recording stored no arena, so the failure history it had is not known"
    for s in doc["strategies"]:
        if s["id"] == "history":
            old = next((x for x in (old_arena or {}).get("strategies", []) if x["id"] == "history"), None)
            if old:                                  # the history of that moment is not reproducible: keep what was recorded
                for k in ("status", "note", "selected", "pct", "caught", "n_failing", "recall", "first_failure_position",
                          "first_failure_ms", "ci_ms", "missed"):
                    s[k] = old[k]
                s["needs"] = f"earlier runs ({(old_arena.get('history') or {}).get('n_runs', 0)} in this repository's lab history, as recorded)"
            else:
                s.update(arena.score(results, None, note=hist_note))
                s["needs"] = "earlier runs (not known for this recording)"
            s["orders_all"] = False
    doc["takeaway"] = arena.takeaway(doc["strategies"], doc["n_cases"], n_failing)
    old_by_id = {x["id"]: x for x in (old_arena or {}).get("strategies", [])}
    doc["rederived"] = {
        "date": now_iso(), "rule": case_order.RULE_ID, "fixed": case_order.RULE_FIXED,
        "rows": ["blastradius", "cochange", "retest-all", "static-rts", "coverage"] if not old_arena else ["blastradius", "cochange"],
        "note": ("computed offline from this recording's stored results; the run itself was executed in the earlier order"
                 + ("" if old_arena else "; the arena did not exist when it was recorded")),
        "before": {sid: {"first_failure_position": old_by_id[sid]["first_failure_position"],
                         "first_failure_ms": old_by_id[sid]["first_failure_ms"], "status": old_by_id[sid]["status"]}
                   for sid in ("blastradius", "cochange") if sid in old_by_id}}
    doc["coverage"] = (old_arena or {}).get("coverage") or {k: v for k, v in (coverage or {}).items() if k != "tests"}
    doc["history"] = (old_arena or {}).get("history") or {"n_runs": None}
    doc["cochange"] = {"n_commits": cochange[1], "upstream": cochange_info, **({"reason": cochange[2]} if cochange[2] else {})}
    i_arena = next((k for k, e in enumerate(ev) if e["type"] == "arena.result"), None)
    node = {"stage": "arena", "type": "arena.result", "status": "ok", "dur_ms": 0.0, "data": doc, "rederived": True}
    if i_arena is not None:
        ev[i_arena] = {**ev[i_arena], **node}
    else:
        ev.insert(i_race + 1, {**{k: ev[i_race][k] for k in ("seq", "ts") if k in ev[i_race]}, **node})
    for k, e in enumerate(ev):                        # seq is the event's position
        e["seq"] = k
    for e in ev:
        if e["type"] == "report.summary" and e["data"].get("race"):
            e["data"]["race"] = {l["name"]: {k: l[k] for k in ("first_failure_position", "elapsed_to_first_failure_ms", "total_ms")}
                                 for l in rc["lanes"]}
        if e["type"] == "tests.done":
            e["data"] = {**e["data"], "as_run_order": "E1 file rank, then pytest's collection order (before the 2026-10-12 rule)"}
        if e["type"] == "run.header":
            e["data"] = {**e["data"], "rederived": {
                "date": doc["rederived"]["date"], "rule": case_order.RULE_ID, "events": ["tests.race", "arena.result"],
                "note": "the BlastRadius order and the arena were re-derived from this recording's stored results; "
                        "every other event is as recorded"}}
        if e["type"] == "run.end":
            e["data"] = {**e["data"], "seq_count": len(ev)}
    return ev


def before_after(old: list[dict], new: list[dict]) -> dict:
    """First failure of the BlastRadius order before and after, from two event lists of the same run."""
    def lane(evs):
        r = next(e["data"] for e in evs if e["type"] == "tests.race")
        return next(l for l in r["lanes"] if l["name"] == "risk-first")
    o, n = lane(old), lane(new)
    return {"before": {"position": o["first_failure_position"], "ms": o["elapsed_to_first_failure_ms"]},
            "after": {"position": n["first_failure_position"], "ms": n["elapsed_to_first_failure_ms"]}}


def run(name: str, runs_dir: Path, write: bool = True) -> dict:
    """Re-derive one recording in place (graph and cochange from the prepared repository and its upstream cache)."""
    import shutil

    from src.lab.workspace import fetch_upstream_history, new_scratch, prepare_seeded

    path = runs_dir / f"{name}.jsonl"
    events = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if any(e.get("rederived") for e in events):
        raise ValueError(f"{name} was already re-derived")
    view = json.loads((runs_dir / f"{name}.graph.json").read_text(encoding="utf-8"))
    repo_info = next(e["data"] for e in events if e["type"] == "repo.info")
    change = next(e["data"] for e in events if e["type"] == "change.applied")
    slug = repo_info["name"]
    scratch = new_scratch("rederive")
    try:
        ws = prepare_seeded(slug, scratch)
        up = fetch_upstream_history(ws)
        try:
            cc = arena.cochange_counts(ws.repo_dir, change["base"], change["changed_files"])
        except Exception as exc:  # noqa: BLE001
            cc = (arena.Counter(), 0, f"git log failed: {exc}"[:200])
        if cc[2] and up["status"] == "unavailable":
            cc = (cc[0], cc[1], up["reason"])
        try:
            cov = arena.run_coverage(ws.repo_dir, change["base"], ws.python, slug) if ws.python else None
        except Exception as exc:  # noqa: BLE001
            cov = {"status": "skipped", "reason": f"{type(exc).__name__}: {exc}"[:300]}
        new = rederive_events(events, view, coverage=cov, cochange=cc,
                              cochange_info={"source": up["status"] if up["status"] in ("fetched", "cached") else None,
                                             "fetch_s": up.get("fetch_s", 0.0)})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    out = before_after(events, new)
    if write:
        path.write_text("".join(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n" for e in new), encoding="utf-8")
    return {"name": name, **out}
