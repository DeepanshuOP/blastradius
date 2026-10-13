"use client";

import { useState } from "react";
import { BTN_PRIMARY, Empty, Icon, Prov, StatusIcon, short, type Tone } from "./common";
import type { AuditRecord, LabState } from "./types";

const DECISION_TONE: Record<AuditRecord["decision"], Tone> = { accept: "ok", reject: "failed", retry: "running", skip: "skipped", wait: "pending", done: "ok" };
const DECISION_CLS: Record<AuditRecord["decision"], string> = {
  accept: "border-green/60 text-green", reject: "border-red/70 text-red", retry: "border-amber text-amber",
  skip: "border-rule text-muted", wait: "border-blue/60 text-blue", done: "border-green/60 text-green",
};

/** Chain linkage as the browser can check it: each record's prev_hash is the previous record's hash. The hash itself
 * is recomputed by `python -m src.agents.audit verify` (its result arrives as the run's `audit.verify` event). */
export function chainLinks(recs: AuditRecord[]): boolean[] {
  return recs.map((r, i) => (i === 0 ? r.prev_hash === "0".repeat(64) || r.seq > 1 : r.prev_hash === recs[i - 1].hash && r.seq === recs[i - 1].seq + 1));
}

function Evidence({ ev }: { ev: Record<string, unknown> }) {
  const [open, setOpen] = useState(false);
  const keys = Object.keys(ev ?? {});
  if (!keys.length) return null;
  const text = JSON.stringify(ev, null, 1);
  return (
    <div className="mt-1">
      <button type="button" onClick={() => setOpen(!open)} className="ui text-2xs text-muted underline">{open ? "hide" : "evidence"} ({keys.slice(0, 4).join(", ")}{keys.length > 4 ? ", …" : ""})</button>
      {open && <pre className="mono m-0 mt-1 max-h-48 overflow-auto whitespace-pre-wrap rounded bg-panel2 p-2 text-2xs">{short(text, 4000)}</pre>}
    </div>
  );
}

export function DecisionsPanel({ s, records }: { s: LabState; records: AuditRecord[] }) {
  if (!records.length) return <Empty title="Each step of the agent is logged here as a hash-chained decision record." >Run or replay a scenario; recordings made before the decision log existed have none.</Empty>;
  const links = chainLinks(records);
  const v = s.audit.verify;
  const verified = v?.ok === true && Number(v.records) === s.audit.records.length;
  const cost = records.reduce((t, r) => t + Number(r.model?.cost_usd ?? 0), 0);
  const runName = String(s.header?.run_id ?? "");
  const logHref = s.mode === "replay" && runName ? `/lab/runs/audit/${runName}.jsonl` : null;
  return (
    <div className="space-y-3" data-testid="decisions">
      <div className="ui flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
        <Prov mode={s.mode} />
        <span><span className="num mono">{records.length}</span> records</span>
        <span className={verified ? "text-green" : v ? "text-red" : "text-muted"} data-testid="decisions-verify">
          {verified ? "audit verify: OK" : v ? `audit verify: ${v.ok ? "OK at end of run" : "FAILED"}` : "audit verify: not run yet"}
        </span>
        <span className="text-muted">model cost USD <span className="num mono">{cost.toFixed(6)}</span></span>
        <span className="mono text-2xs text-muted" title={records[records.length - 1].hash}>head {records[records.length - 1].hash.slice(0, 16)}</span>
        {logHref && <a href={logHref} className="text-accent underline" target="_blank" rel="noreferrer">raw log</a>}
      </div>
      <ol className="m-0 list-none space-y-0 p-0">
        {records.map((r, i) => (
          <li key={`${r.seq}-${r.hash}`} className="grid grid-cols-[2.2rem_6.5rem_1fr_auto] items-start gap-2 border-t border-rule py-2 first:border-t-0" data-stage={r.stage} data-decision={r.decision}>
            <span className="num mono pt-0.5 text-xs text-muted">#{r.seq}</span>
            <span className="ui flex flex-col gap-1">
              <span className="text-sm font-semibold">{r.stage}</span>
              <span className={`inline-flex w-fit items-center gap-1 rounded border px-1.5 text-2xs font-semibold uppercase ${DECISION_CLS[r.decision]}`}><StatusIcon tone={DECISION_TONE[r.decision]} />{r.decision}</span>
            </span>
            <span className="min-w-0">
              <span className="ui block text-sm">{r.reason}</span>
              <span className="ui block text-2xs text-muted"><span className="mono">{r.action}</span> · {r.actor} · {r.ts.replace("T", " ").replace("Z", " UTC")}</span>
              {r.model && <span className="ui block text-2xs text-muted">model <span className="mono">{r.model.provider}/{r.model.model}</span> · in {r.model.tokens_in ?? "?"} · out {r.model.tokens_out ?? "?"} · USD {r.model.cost_usd == null ? "n/a" : Number(r.model.cost_usd).toFixed(6)}{r.model.cache_hit ? " · cache hit" : ""} · prompt <span className="mono">{r.model.prompt_sha256.slice(0, 10)}</span> · reply <span className="mono">{r.model.reply_sha256.slice(0, 10)}</span></span>}
              {r.artifacts && Object.values(r.artifacts).some(Boolean) && <span className="ui block text-2xs text-muted">{r.artifacts.branch && <>branch <span className="mono">{r.artifacts.branch}</span> </>}{r.artifacts.commit && <>commit <span className="mono">{r.artifacts.commit.slice(0, 10)}</span> </>}{r.artifacts.patch_sha256 && <>patch <span className="mono">{r.artifacts.patch_sha256.slice(0, 10)}</span> </>}{r.artifacts.pr_url && <a href={r.artifacts.pr_url} className="text-accent underline" target="_blank" rel="noreferrer">{r.artifacts.pr_url}</a>}</span>}
              <Evidence ev={r.evidence} />
            </span>
            <span className={`ui flex items-center gap-1 pt-0.5 text-xs ${links[i] ? "text-green" : "text-red"}`} title={`hash ${r.hash}\nprev ${r.prev_hash}`} data-testid="hash-ok">
              <span className="mono">{r.hash.slice(0, 8)}</span>{links[i] ? <Icon name="check" /> : <Icon name="cross" />}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

/** Ask mode (D-70): the run stopped at an approval wait; the operator may approve opening the fix PR. */
export function approvalState(records: AuditRecord[]): "none" | "waiting" | "approved" | "opened" | "refused" {
  if (records.some((r) => r.stage === "pr" && r.action === "open_fix_pr" && r.decision === "accept")) return "opened";
  const gate = [...records].reverse().find((r) => r.stage === "approve" || (r.stage === "pr" && r.action === "gate") || r.stage === "git");
  if (!gate) return "none";
  if (gate.decision === "reject") return "refused";
  if (gate.stage === "approve" && gate.decision === "wait") return "waiting";
  if (gate.stage === "approve" && gate.decision === "accept") return "approved";
  return "none";
}

export function ApproveFix({ records, mode, live, onRecords }: { records: AuditRecord[]; mode: string; live: boolean; onRecords: (r: AuditRecord[]) => void }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  if (mode !== "ask") return null;
  const st = approvalState(records);
  if (st === "none") return null;
  const run = records[0]?.run_id;
  const pr = records.find((r) => r.artifacts?.pr_url)?.artifacts?.pr_url;
  const last = [...records].reverse().find((r) => r.stage === "approve" || r.stage === "pr" || r.stage === "git");
  const approve = async () => {
    setBusy(true); setErr(null);
    try {
      const r = await fetch("/api/lab/approve", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ run }) });
      const j = await r.json();
      if (Array.isArray(j.records)) onRecords(j.records as AuditRecord[]);
      if (!r.ok || !j.ok) setErr(String(j.error ?? j.result?.reason ?? `HTTP ${r.status}`));
    } catch (e) { setErr(String(e)); } finally { setBusy(false); }
  };
  return (
    <div className="mb-3 flex flex-wrap items-center gap-3 rounded border border-blue/60 bg-panel px-3 py-2" data-testid="approve-fix" data-state={st}>
      <span className="ui text-sm font-semibold">Fix PR (ask mode)</span>
      <span className="ui min-w-0 flex-1 text-sm text-muted">{st === "opened" ? <>opened: <a className="text-accent underline" href={pr ?? "#"} target="_blank" rel="noreferrer">{pr}</a></> : last?.reason}</span>
      {st === "waiting" && <button type="button" className={BTN_PRIMARY} disabled={busy || !live} onClick={approve} title={live ? "Record your approval in the decision log, then open the fix PR on its own branch" : "Needs the local server"}>{busy ? "Approving…" : "Approve fix"}</button>}
      {err && <span className="ui text-xs text-red" role="alert">{short(err, 200)}</span>}
    </div>
  );
}
