"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { STAGE_LABEL, StatusIcon, summarize, type Tone } from "./common";
import type { LabEvent, Stage } from "./types";

const TONE: Record<string, Tone> = { ok: "ok", failed: "failed", skipped: "skipped", running: "running" };

type Row = { kind: "event"; e: LabEvent } | { kind: "tests"; seq: number; ts: string; n: number; failed: number; total: number | null; done: boolean };

/** Per-test results folded into one line that updates as they arrive: "tests 143/297 · 12 failed". */
export function foldTests(events: LabEvent[], showTests: boolean): Row[] {
  if (showTests) return events.map((e) => ({ kind: "event", e }));
  const rows: Row[] = [];
  let agg: Extract<Row, { kind: "tests" }> | null = null;
  for (const e of events) {
    if (e.type === "test.result") {
      if (!agg) { agg = { kind: "tests", seq: e.seq, ts: e.ts, n: 0, failed: 0, total: null, done: false }; rows.push(agg); }
      agg.n += 1;
      agg.failed += e.data.outcome === "failed" || e.data.outcome === "error" ? 1 : 0;
      agg.total = (e.data.of as number | undefined) ?? agg.total;
      agg.ts = e.ts;
      continue;
    }
    if (e.type === "tests.done" && agg) { agg.done = true; agg.total = (e.data.counts?.total as number | undefined) ?? agg.total; }
    rows.push({ kind: "event", e });
  }
  return rows;
}

export function EventLog({ events, className = "" }: { events: LabEvent[]; className?: string }) {
  const [filter, setFilter] = useState<Stage | "all">("all");
  const [showTests, setShowTests] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  const stick = useRef(true);
  const shown = useMemo(() => foldTests(events.filter((e) => filter === "all" || e.stage === filter), showTests), [events, filter, showTests]);
  const stages = useMemo(() => Array.from(new Set(events.map((e) => e.stage))), [events]);
  const lastKey = shown.length ? `${shown.length}:${(shown[shown.length - 1] as { n?: number }).n ?? 0}` : "0";
  useEffect(() => {
    if (stick.current) end.current?.scrollIntoView({ block: "end" });
  }, [lastKey]);
  const t0 = events[0] ? Date.parse(events[0].ts) : 0;
  const at = (ts: string) => ((Date.parse(ts) - t0) / 1000).toFixed(2);
  return (
    <div className={`flex min-h-0 flex-col ${className}`}>
      <div className="flex flex-wrap items-center gap-1 border-b border-rule px-2 py-1.5">
        {(["all", ...stages] as (Stage | "all")[]).map((s) => (
          <button key={s} type="button" onClick={() => setFilter(s)} aria-pressed={filter === s}
            className={`ui rounded px-1.5 py-0.5 text-2xs ${filter === s ? "bg-ink text-page" : "text-muted hover:text-ink"}`}>
            {s === "all" ? "all" : STAGE_LABEL[s]}
          </button>
        ))}
        <label className="ui ml-auto flex items-center gap-1 text-2xs text-muted">
          <input type="checkbox" checked={showTests} onChange={(e) => setShowTests(e.target.checked)} /> per-test lines
        </label>
      </div>
      <div className="mono min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-2 py-1.5 text-xs"
        onScroll={(e) => { const el = e.currentTarget; stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 24; }}
        role="log" aria-live="off" aria-label="Event log">
        {shown.length === 0 && <p className="ui m-0 py-2 text-sm text-muted">Events stream here as each stage runs: the repository, the graph, the change, every test, triage, repair and the verdict.</p>}
        {shown.map((r) => {
          if (r.kind === "tests") {
            const text = `tests ${r.n}${r.total ? `/${r.total}` : ""} · ${r.failed} failed${r.done ? "" : " · running"}`;
            return (
              <div key={`t${r.seq}`} className="grid grid-cols-[3.6rem_4.4rem_minmax(0,1fr)] gap-x-2 py-px" title={text}>
                <span className="num text-right text-muted">{at(r.ts)}s</span>
                <span className="ui text-blue">Tests</span>
                <span className="flex min-w-0 items-center gap-1.5 overflow-hidden text-ellipsis whitespace-nowrap">
                  <StatusIcon tone={r.done ? (r.failed ? "failed" : "ok") : "running"} />
                  <span className="num">{text}</span>
                </span>
              </div>
            );
          }
          const e = r.e;
          const text = summarize(e.type, e.data, e.status);
          return (
            <div key={e.seq} className="grid grid-cols-[3.6rem_4.4rem_minmax(0,1fr)] gap-x-2 py-px" title={text}>
              <span className="num text-right text-muted">{at(e.ts)}s</span>
              <span className="ui text-blue">{STAGE_LABEL[e.stage]}</span>
              <span className={`flex min-w-0 items-start gap-1.5 ${e.status === "failed" ? "text-red" : e.status === "skipped" ? "text-muted" : "text-ink"}`}>
                <StatusIcon tone={TONE[e.status] ?? "ok"} className="mt-[3px]" />
                <span className="min-w-0 overflow-hidden text-ellipsis [overflow-wrap:normal] [word-break:normal]">{text}</span>
              </span>
            </div>
          );
        })}
        <div ref={end} />
      </div>
    </div>
  );
}

/** A slim bar at the bottom of the screen: the latest event, and a button that opens the full log in a drawer. */
export function Ticker({ events, onOpen }: { events: LabEvent[]; onOpen: () => void }) {
  const last = events[events.length - 1];
  let n = 0, failed = 0;
  for (const e of events) if (e.type === "test.result") { n += 1; failed += e.data.outcome === "failed" || e.data.outcome === "error" ? 1 : 0; }
  const text = !last ? "waiting for a run" : last.type === "test.result" ? `tests ${n}${last.data.of ? `/${last.data.of}` : ""} · ${failed} failed` : summarize(last.type, last.data, last.status);
  const tone = !last ? "pending" : last.type === "test.result" ? (failed ? "failed" : "running") : (TONE[last.status] ?? "ok");
  return (
    <div className="fixed inset-x-0 bottom-0 z-30 border-t border-rule bg-panel" role="status" aria-live="off">
      <div className="mx-auto flex h-9 max-w-[1760px] items-center gap-3 px-3">
        <StatusIcon tone={tone as Tone} />
        <span className="ui w-16 shrink-0 text-xs text-blue">{last ? STAGE_LABEL[last.stage] : "idle"}</span>
        <span className="mono min-w-0 flex-1 truncate text-xs" title={text}>{text}</span>
        <span className="num mono shrink-0 text-xs text-muted">{events.length} events</span>
        <button type="button" onClick={onOpen} className="ui shrink-0 rounded border border-rule px-2 py-0.5 text-xs hover:border-muted" aria-haspopup="dialog">Log</button>
      </div>
    </div>
  );
}
