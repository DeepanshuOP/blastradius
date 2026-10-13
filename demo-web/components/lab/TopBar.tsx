"use client";

import { BTN, Icon, fmtMs } from "./common";
import { GlossaryButton } from "./Glossary";
import { Info } from "./Info";
import { Scoreboard, type Tally } from "./Scoreboard";
import type { LabState } from "./types";
import type { Availability } from "./useLab";

/** Whether the repair model can be called right now, and if not the exact reason, from the server's status
 * (`python -m src.lab status`), the quota ledgers and the options of the current live run. */
export function modelStatus(s: LabState, avail: Availability, model: string): { ready: boolean; text: string; detail: string } {
  const name = model.replace(/^openai\//, "");
  const off = (why: string, detail = why) => ({ ready: false, text: `Model: offline \u2014 ${why}`, detail });
  if (!avail.checked) return { ready: false, text: "Model: checking\u2026", detail: "asking the local server" };
  if (!avail.live) return off("no server (static build)", avail.reason);
  if (!avail.llm) return off("no key", "GROQ_API_KEY is not set in .env on the server");
  const q = avail.quota?.[model];
  if (q && !q.ok) return off("quota", `${q.used.toLocaleString("en-US")} of ${q.cap.toLocaleString("en-US")} tokens used in the last 24 h${q.resume_after ? `; next call after ${q.resume_after.replace("T", " ")} UTC` : ""}`);
  if (s.mode === "live" && String(s.header?.llm ?? "").startsWith("disabled")) return off("disabled by option", "this run was started with --no-llm");
  if (s.mode === "live" && s.repair.unavailable) return off(s.repair.unavailable.kind, s.repair.unavailable.reason);
  return { ready: true, text: `Model: ready (${name})`, detail: q ? `${q.used.toLocaleString("en-US")} of ${q.cap.toLocaleString("en-US")} tokens used in the last 24 h` : "key present" };
}

export function ModelChip({ s, avail, model }: { s: LabState; avail: Availability; model: string }) {
  const m = modelStatus(s, avail, model);
  return (
    <span role="status" title={m.detail} data-testid="model-chip"
      className={`ui inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${m.ready ? "border-green text-green" : avail.checked ? "border-amber text-amber" : "border-rule text-muted"}`}>
      <span className={`inline-block h-2 w-2 rounded-full ${m.ready ? "bg-green" : avail.checked ? "bg-amber" : "bg-muted"}`} aria-hidden="true" />{m.text}
    </span>
  );
}

export function ModeBadge({ s, avail }: { s: LabState; avail: { checked: boolean; live: boolean } }) {
  if (s.mode === "live")
    return <span className="ui inline-flex items-center gap-1.5 rounded border border-green px-2 py-0.5 text-xs font-semibold text-green" role="status"><span className="br-pulse inline-block h-2 w-2 rounded-full bg-green" />LIVE</span>;
  if (s.mode === "replay")
    return <span className="ui inline-flex items-center gap-1.5 rounded border border-amber px-2 py-0.5 text-xs font-semibold text-amber" role="status">REPLAY · {String(s.header?.date ?? "").slice(0, 10) || "?"}</span>;
  return <span className="ui inline-flex items-center gap-1.5 rounded border border-rule px-2 py-0.5 text-xs text-muted" role="status">{!avail.checked ? "CHECKING" : avail.live ? "READY · live" : "READY · replay only"}</span>;
}

/** The Explain switch: off by default; while it is off the screen carries no explanatory sentences. */
function ExplainSwitch({ on, set }: { on: boolean; set: (v: boolean) => void }) {
  return (
    <button type="button" role="switch" aria-checked={on} onClick={() => set(!on)}
      className="ui inline-flex min-h-[32px] items-center gap-2 rounded border border-rule px-2.5 text-sm hover:border-muted">
      <span className={`relative inline-block h-4 w-7 rounded-full transition-colors ${on ? "bg-accent" : "bg-panel2"}`} aria-hidden="true">
        <span className={`absolute top-0.5 h-3 w-3 rounded-full bg-ink transition-all ${on ? "left-[14px]" : "left-0.5"}`} />
      </span>
      Explain
    </button>
  );
}

export function TopBar({ s, avail, model, tally, explain, setExplain, onReset, onIntegrity, onPresent }: {
  s: LabState; avail: Availability; model: string; tally: Tally; explain: boolean; setExplain: (v: boolean) => void;
  onReset: () => void; onIntegrity: () => void; onPresent?: () => void;
}) {
  const h = s.header;
  const elapsed = s.startedAt ? fmtMs(s.running ? s.elapsedMs : Number(s.report.summary?.total_ms ?? s.elapsedMs)) : "0 s";
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2 rounded-md border border-rule bg-panel px-3 py-2">
      <ModeBadge s={s} avail={avail} />
      <ModelChip s={s} avail={avail} model={model} />
      <span className="ui flex items-baseline gap-1.5 text-sm">
        <span className="mono">{s.repo?.name ?? "no repo"}</span>
        {s.repo?.commit && <span className="num mono text-xs text-muted">@{String(s.repo.commit).slice(0, 7)}</span>}
        <Info label="Run details">
          <span className="block"><span className="text-muted">model</span> <span className="mono">{h ? (h.model ?? "none") : model}</span></span>
          <span className="mt-1 block"><span className="text-muted">elapsed</span> <span className="num mono">{elapsed}</span></span>
          <span className="mt-1 block"><span className="text-muted">tokens this run</span> <span className="num mono">{s.tokens.total.toLocaleString()}{s.tokens.cached > 0 ? ` (${s.tokens.cached.toLocaleString()} cached)` : ""}</span></span>
        </Info>
      </span>
      <div className="min-w-0 flex-1"><Scoreboard t={tally} /></div>
      <div className="flex items-center gap-2">
        <ExplainSwitch on={explain} set={setExplain} />
        <GlossaryButton />
        {s.events.length > 0 && <button type="button" onClick={onIntegrity} className={BTN}>Integrity</button>}
        {onPresent && <button type="button" onClick={onPresent} disabled={!s.events.length} className={BTN} title={s.events.length ? "Full-screen walkthrough of this run" : "Run or replay a scenario first"}><Icon name="present" />Present</button>}
        <button type="button" onClick={onReset} className={BTN}>Reset</button>
      </div>
    </div>
  );
}
