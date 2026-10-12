"use client";

import type { ReactNode } from "react";
import { BTN, BTN_PRIMARY, Icon, fmtMs } from "./common";
import type { LabState } from "./types";

export function ModeBadge({ s, avail }: { s: LabState; avail: { checked: boolean; live: boolean } }) {
  if (s.mode === "live")
    return <span className="ui inline-flex items-center gap-1.5 rounded border border-green px-2 py-0.5 text-xs font-semibold text-green" role="status"><span className="br-pulse inline-block h-2 w-2 rounded-full bg-green" />LIVE</span>;
  if (s.mode === "replay")
    return <span className="ui inline-flex items-center gap-1.5 rounded border border-amber px-2 py-0.5 text-xs font-semibold text-amber" role="status">REPLAY · recorded {String(s.header?.date ?? "").slice(0, 10) || "?"}</span>;
  return <span className="ui inline-flex items-center gap-1.5 rounded border border-rule px-2 py-0.5 text-xs text-muted" role="status">{!avail.checked ? "CHECKING" : avail.live ? "READY · live available" : "READY · replay only"}</span>;
}

/** One metric: a small muted label and a tabular value at the same size, so no number shouts over its neighbours. */
function Metric({ label, children }: { label: string; children: ReactNode }) {
  return <div className="ui flex items-baseline gap-1.5 text-sm"><span className="text-xs text-muted">{label}</span><span className="num mono">{children}</span></div>;
}

export function TopBar({ s, avail, model, canRun, onRun, onReset, onIntegrity, onPresent }: {
  s: LabState; avail: { checked: boolean; live: boolean }; model: string; canRun: boolean; onRun: () => void; onReset: () => void; onIntegrity: () => void; onPresent?: () => void;
}) {
  const h = s.header;
  const elapsed = s.startedAt ? fmtMs(s.running ? s.elapsedMs : Number(s.report.summary?.total_ms ?? s.elapsedMs)) : "0 s";
  return (
    <div className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-x-5 gap-y-2 rounded-md border border-rule bg-panel px-3 py-2">
      <ModeBadge s={s} avail={avail} />
      <div className="flex min-w-0 flex-wrap items-center gap-x-5 gap-y-0.5">
      <Metric label="repo">{s.repo?.name ?? "none"} @ {s.repo?.commit ? String(s.repo.commit).slice(0, 7) : "n/a"}</Metric>
      <Metric label="model">{h ? (h.model ?? "none") : model}</Metric>
      <Metric label="tokens">{s.tokens.total.toLocaleString()}{s.tokens.cached > 0 ? ` (${s.tokens.cached.toLocaleString()} cached)` : ""}</Metric>
      <Metric label="elapsed">{elapsed}</Metric>
      </div>
      <div className="flex items-center gap-2">
        {s.events.length > 0 && <button type="button" onClick={onIntegrity} className={BTN}>Integrity</button>}
        {onPresent && <button type="button" onClick={onPresent} disabled={!s.events.length} className={BTN} title={s.events.length ? "Full-screen walkthrough of this run" : "Run or replay a scenario first"}><Icon name="present" />Present</button>}
        <button type="button" onClick={onReset} className={BTN}>Reset</button>
        <button type="button" onClick={onRun} disabled={!canRun || s.running} className={BTN_PRIMARY}>{s.running ? "Running" : "Run"}</button>
      </div>
    </div>
  );
}
