"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { STAGE_LABEL, summarize } from "./common";
import type { LabEvent, Stage } from "./types";

const COLOR: Record<string, string> = { ok: "text-ink", failed: "text-red", skipped: "text-muted", running: "text-blue" };

export function EventLog({ events, className = "" }: { events: LabEvent[]; className?: string }) {
  const [filter, setFilter] = useState<Stage | "all">("all");
  const [hideTests, setHideTests] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  const stick = useRef(true);
  const box = useRef<HTMLDivElement>(null);
  const shown = useMemo(
    () => events.filter((e) => (filter === "all" || e.stage === filter) && !(hideTests && e.type === "test.result")),
    [events, filter, hideTests],
  );
  const stages = useMemo(() => Array.from(new Set(events.map((e) => e.stage))), [events]);
  useEffect(() => {
    if (stick.current) end.current?.scrollIntoView({ block: "end" });
  }, [shown.length]);
  const t0 = events[0] ? Date.parse(events[0].ts) : 0;
  return (
    <div className={`flex min-h-0 flex-col ${className}`}>
      <div className="flex flex-wrap items-center gap-1 border-b border-rule px-2 py-1.5">
        {(["all", ...stages] as (Stage | "all")[]).map((s) => (
          <button key={s} type="button" onClick={() => setFilter(s)} aria-pressed={filter === s}
            className={`ui rounded px-1.5 py-0.5 text-[11px] ${filter === s ? "bg-ink text-page" : "text-muted hover:text-ink"}`}>
            {s === "all" ? "all" : STAGE_LABEL[s]}
          </button>
        ))}
        <label className="ui ml-auto flex items-center gap-1 text-[11px] text-muted">
          <input type="checkbox" checked={hideTests} onChange={(e) => setHideTests(e.target.checked)} /> hide per-test lines
        </label>
      </div>
      <div ref={box} className="mono min-h-0 flex-1 overflow-y-auto px-2 py-1.5 text-[11.5px] leading-[1.55]"
        onScroll={(e) => { const el = e.currentTarget; stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 24; }}>
        {shown.length === 0 && <p className="ui m-0 text-muted">No events yet. Choose a scenario and press Run.</p>}
        {shown.map((e) => (
          <div key={e.seq} className={`grid grid-cols-[3.4rem_4.2rem_1fr] gap-x-2 ${COLOR[e.status] ?? ""}`}>
            <span className="text-right text-muted">{((Date.parse(e.ts) - t0) / 1000).toFixed(2)}s</span>
            <span className="text-blue">{STAGE_LABEL[e.stage]}</span>
            <span className="min-w-0 break-all">{summarize(e.type, e.data, e.status)}</span>
          </div>
        ))}
        <div ref={end} />
      </div>
    </div>
  );
}
