"""The Live Lab event stream: one JSON object per line.

    {"seq", "ts", "stage", "type", "status": "running|ok|failed|skipped", "dur_ms", "data"}

stdout carries events and nothing else; diagnostics go to stderr.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from typing import IO

STAGES = ("meta", "repo", "graph", "change", "impact", "tests", "arena", "triage", "repair", "validate", "report", "audit")
STATUSES = ("running", "ok", "failed", "skipped")
#: Event types each stage may carry (the schema `validate_event` checks recorded runs against).
TYPES: dict[str, tuple[str, ...]] = {
    "meta": ("run.header", "run.end"),
    "repo": ("repo.info",),
    "graph": ("graph.built",),
    "change": ("change.applied",),
    "impact": ("impact.ranking", "impact.paths"),
    "tests": ("tests.start", "test.result", "tests.done", "tests.race"),
    "arena": ("arena.coverage", "arena.upstream", "arena.result", "arena.gap", "arena.repair", "arena.probe"),
    "triage": ("triage.result",),
    "repair": ("localize.result", "repair.chunks", "repair.request", "repair.reply", "repair.blocks", "repair.patch", "repair.skipped",
               "repair.unavailable"),
    "validate": ("validate.check", "validate.verdict"),
    "report": ("report.comment", "report.summary"),
    "audit": ("audit.record", "audit.verify"),
}
REQUIRED_DATA: dict[str, tuple[str, ...]] = {
    "repo.info": ("name", "url", "commit", "language", "n_files", "tests_runnable"),
    "graph.built": ("nodes", "edges", "counts", "parse_failures", "truncated"),
    "change.applied": ("diff", "changed_files", "changed_nodes", "source"),
    "impact.ranking": ("ranker", "rows", "changed_files"),
    "impact.paths": ("paths", "reachability"),
    "test.result": ("id", "outcome", "duration_s"),
    "tests.done": ("counts",),
    "tests.race": ("lanes",),
    "arena.result": ("strategies", "basis", "takeaway"),
    "arena.repair": ("columns",),
    "arena.gap": ("file", "line", "old", "new", "covering", "sentence"),
    "triage.result": ("rows", "counts"),
    "validate.check": ("name", "ok", "evidence"),
    "validate.verdict": ("accepted",),
    "report.comment": ("comment",),
    "report.summary": ("stages", "mode"),
    "audit.record": ("v", "run_id", "seq", "stage", "decision", "reason", "prev_hash", "hash"),
    "audit.verify": ("ok", "records", "run_id"),
}


def now_iso() -> str:
    """UTC timestamp with milliseconds."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Emitter:
    """Numbers events, stamps them and writes them (optionally also to a recording)."""

    def __init__(self, out: IO[str] | None = None, record: IO[str] | None = None, replay: bool = False) -> None:
        self.out = out if out is not None else sys.stdout
        self.record = record
        self.replay = replay
        self.seq = 0
        self.started: dict[str, float] = {}
        self.history: list[dict] = []
        self._last: float | None = None

    def emit(self, stage: str, type_: str, status: str, data: dict | None = None, dur_ms: float | None = None) -> dict:
        """Write one event. `dur_ms` defaults to the time since the stage's first event."""
        t = time.perf_counter()
        # a stage starts when the previous event was emitted (the work between two events belongs to the later one)
        self.started.setdefault(stage, self._last if self._last is not None else t)
        self._last = t
        self.seq += 1
        ev = {"seq": self.seq, "ts": now_iso(), "stage": stage, "type": type_, "status": status,
              "dur_ms": round(dur_ms if dur_ms is not None else (t - self.started[stage]) * 1000, 1),
              "data": data or {}}
        if self.replay:
            ev["replay"] = True
        self.history.append(ev)
        line = json.dumps(ev, ensure_ascii=False, separators=(",", ":"))
        self.out.write(line + "\n")
        self.out.flush()
        if self.record is not None:
            self.record.write(line + "\n")
            self.record.flush()
        return ev


def validate_event(ev: dict) -> list[str]:
    """Problems with one event against the schema (empty when it conforms)."""
    bad: list[str] = []
    for k in ("seq", "ts", "stage", "type", "status", "dur_ms", "data"):
        if k not in ev:
            bad.append(f"missing {k}")
    if bad:
        return bad
    if ev["stage"] not in STAGES:
        bad.append(f"unknown stage {ev['stage']!r}")
    elif ev["type"] not in TYPES[ev["stage"]]:
        bad.append(f"type {ev['type']!r} not allowed in stage {ev['stage']!r}")
    if ev["status"] not in STATUSES:
        bad.append(f"unknown status {ev['status']!r}")
    if not isinstance(ev["data"], dict):
        bad.append("data is not an object")
    else:
        for k in REQUIRED_DATA.get(ev["type"], ()):
            if k not in ev["data"] and ev["status"] not in ("skipped", "running"):
                bad.append(f"{ev['type']}: data lacks {k!r}")
    return bad
