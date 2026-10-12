"use client";

import { fmtMs, sha } from "./common";
import type { LabState } from "./types";

export function ModeBadge({ s, avail }: { s: LabState; avail: { checked: boolean; live: boolean } }) {
  if (s.mode === "live")
    return <span className="ui inline-flex items-center gap-1.5 rounded border border-green px-2 py-0.5 text-[12px] font-semibold text-green" role="status"><span className="inline-block h-2 w-2 animate-pulse rounded-full bg-green" />LIVE</span>;
  if (s.mode === "replay")
    return <span className="ui inline-flex items-center gap-1.5 rounded border border-amber px-2 py-0.5 text-[12px] font-semibold text-amber" role="status">REPLAY · recorded {String(s.header?.date ?? "").slice(0, 10) || "?"}</span>;
  return <span className="ui inline-flex items-center gap-1.5 rounded border border-rule px-2 py-0.5 text-[12px] text-muted" role="status">{!avail.checked ? "CHECKING" : avail.live ? "READY · live available" : "READY · replay only"}</span>;
}

export function TopBar({ s, avail, model, canRun, onRun, onReset, onIntegrity }: {
  s: LabState; avail: { checked: boolean; live: boolean }; model: string; canRun: boolean; onRun: () => void; onReset: () => void; onIntegrity: () => void;
}) {
  const h = s.header;
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-md border border-rule bg-panel px-3 py-2">
      <ModeBadge s={s} avail={avail} />
      <div className="ui min-w-0 text-[13px]">
        <span className="text-muted">repo </span><span className="mono">{s.repo?.name ?? "none"}</span>
        <span className="text-muted"> @ </span><span className="mono">{sha(s.repo?.commit)}</span>
      </div>
      <div className="ui text-[13px]"><span className="text-muted">model </span><span className="mono">{h ? (h.model ?? "none") : model}</span></div>
      <div className="ui text-[13px]"><span className="text-muted">tokens </span><span className="mono">{s.tokens.total.toLocaleString()}</span>{s.tokens.cached > 0 && <span className="text-muted"> ({s.tokens.cached.toLocaleString()} cached)</span>}</div>
      <div className="ui text-[13px]"><span className="text-muted">elapsed </span><span className="mono">{s.startedAt ? fmtMs(s.running ? s.elapsedMs : Number(s.report.summary?.total_ms ?? s.elapsedMs)) : "0 s"}</span></div>
      <div className="ml-auto flex items-center gap-2">
        {s.events.length > 0 && <button type="button" onClick={onIntegrity} className="ui rounded border border-rule px-2.5 py-1 text-[12.5px] hover:border-muted">Integrity</button>}
        <button type="button" onClick={onReset} className="ui rounded border border-rule px-3 py-1 text-[13px] hover:border-muted">Reset</button>
        <button type="button" onClick={onRun} disabled={!canRun || s.running} className="ui rounded bg-accent px-4 py-1 text-[13px] font-semibold text-white disabled:opacity-40">{s.running ? "Running" : "Run"}</button>
      </div>
    </div>
  );
}
