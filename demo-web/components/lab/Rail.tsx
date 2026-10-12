"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import { STAGE_LABEL, StatusIcon, fmtMs, summarize, type Tone } from "./common";
import { foldTests } from "./Log";
import { STAGES, type LabState, type Stage, type Status } from "./types";

const JENKINS: { name: string; stages: Stage[] }[] = [
  { name: "Checkout", stages: ["repo", "graph", "change"] },
  { name: "Predict", stages: ["impact"] },
  { name: "Test risk-first", stages: ["tests", "arena"] },
  { name: "Triage", stages: ["triage"] },
  { name: "Repair", stages: ["repair"] },
  { name: "Validate", stages: ["validate"] },
  { name: "Report", stages: ["report"] },
];

function merged(s: LabState, stages: Stage[]): { status: Status | "pending"; dur: number } {
  const xs = stages.map((k) => s.stage[k]).filter(Boolean);
  if (!xs.length) return { status: "pending", dur: 0 };
  const dur = xs.reduce((a, x) => a + x.dur_ms, 0);
  const st = xs.some((x) => x.status === "failed") ? "failed" : xs.some((x) => x.status === "running") ? "running" : xs.every((x) => x.status === "skipped") ? "skipped" : "ok";
  return { status: st, dur };
}

const tone = (st: Status | "pending"): Tone => (st === "pending" ? "pending" : st);
const BOX: Record<Status | "pending", string> = {
  pending: "border-rule bg-page", running: "border-blue bg-blue/10", ok: "border-green/70 bg-green/10", failed: "border-red bg-red/10", skipped: "border-rule bg-panel2/60",
};

/** The pipeline: one chip per stage (status icon, label, duration). A chip opens that stage's result tab. */
export function PipelineRail({ s, stages = STAGES, active, onPick }: { s: LabState; stages?: Stage[]; active?: Stage | null; onPick: (st: Stage) => void }) {
  const [jenkins, setJenkins] = useState(false);
  const [snippet, setSnippet] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="rounded-md border border-rule bg-panel px-3 py-2">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h2 className="ui m-0 text-sm font-semibold">{jenkins ? "Jenkins stage view (illustration)" : "Pipeline"}</h2>
        <div className="flex items-center gap-3">
          <button type="button" onClick={() => setSnippet(!snippet)} className="ui text-xs text-blue underline" aria-expanded={snippet}>Jenkinsfile</button>
          <label className="ui flex cursor-pointer items-center gap-1.5 text-xs text-muted">
            <input type="checkbox" checked={jenkins} onChange={(e) => { setJenkins(e.target.checked); setOpen(null); }} /> Jenkins stage view
          </label>
        </div>
      </div>
      {!jenkins ? (
        <ol className="m-0 flex list-none items-stretch gap-1 overflow-x-auto p-0" aria-label="Pipeline stages">
          {stages.map((k) => {
            const x = s.stage[k];
            const st = x?.status ?? "pending";
            return (
              <li key={k} className="min-w-[84px] flex-1">
                <button type="button" onClick={() => onPick(k)} aria-current={active === k ? "step" : undefined}
                  className={`w-full rounded border px-2 py-1.5 text-left hover:border-muted ${active === k ? "border-ink" : "border-rule"} ${st === "running" ? "bg-blue/10" : "bg-page"}`}>
                  <span className="flex items-center gap-1.5"><StatusIcon tone={tone(st)} /><span className="ui text-sm font-medium">{STAGE_LABEL[k]}</span></span>
                  <span className="num mono mt-0.5 block text-2xs text-muted">{x ? (st === "running" ? "running" : st === "skipped" ? "skipped" : st === "failed" ? `failed · ${fmtMs(x.dur_ms)}` : fmtMs(x.dur_ms)) : "pending"}</span>
                </button>
              </li>
            );
          })}
        </ol>
      ) : (
        <JenkinsView s={s} open={open} setOpen={setOpen} />
      )}
      {snippet && <JenkinsSnippet />}
    </div>
  );
}

function JenkinsView({ s, open, setOpen }: { s: LabState; open: string | null; setOpen: (x: string | null) => void }) {
  const col = JENKINS.find((c) => c.name === open);
  const lines = useMemo(() => (col ? foldTests(s.events.filter((e) => col.stages.includes(e.stage)), false) : []), [col, s.events]);
  return (
    <>
      <div className="flex items-stretch overflow-x-auto pb-1" role="list" aria-label="Jenkins stages">
        {JENKINS.map((c, i) => {
          const m = merged(s, c.stages);
          return (
            <Fragment key={c.name}>
              {i > 0 && <div className="flex w-5 shrink-0 items-center" aria-hidden="true"><div className={`h-0.5 w-full ${m.status === "pending" ? "bg-rule" : "bg-muted"}`} /></div>}
              <div role="listitem" className="min-w-[112px] flex-1">
              <button type="button" onClick={() => setOpen(open === c.name ? null : c.name)} aria-expanded={open === c.name}
                className={`h-full w-full rounded border px-2.5 py-2 text-left ${BOX[m.status]} ${open === c.name ? "ring-1 ring-ink" : ""}`}>
                <span className="ui block truncate text-xs font-semibold">{c.name}</span>
                <span className="mt-1 flex items-center justify-between gap-2">
                  <StatusIcon tone={tone(m.status)} text className="text-2xs" />
                  <span className="num mono text-xs">{m.status === "pending" ? "–" : m.status === "running" ? "…" : fmtMs(m.dur)}</span>
                </span>
              </button>
              </div>
            </Fragment>
          );
        })}
      </div>
      {col && (
        <div className="mono mt-2 max-h-48 overflow-y-auto rounded border border-rule bg-page px-2 py-1.5 text-xs" aria-label={`${col.name} log`}>
          {lines.length === 0 && <p className="ui m-0 text-muted">This stage has not produced any lines yet.</p>}
          {lines.map((r, i) => (
            <div key={i} className="truncate" title={r.kind === "event" ? summarize(r.e.type, r.e.data, r.e.status) : undefined}>
              {r.kind === "event" ? `[${STAGE_LABEL[r.e.stage]}] ${summarize(r.e.type, r.e.data, r.e.status)}` : `[Tests] tests ${r.n}${r.total ? `/${r.total}` : ""} · ${r.failed} failed`}
            </div>
          ))}
        </div>
      )}
      <p className="cap m-0 mt-2 text-xs">The same stages and durations as this run, drawn the way Jenkins draws a pipeline. No Jenkins server was involved: this shows where the stages would sit in an existing job. The example Jenkinsfile is not deployed. Click a stage for its log lines.</p>
    </>
  );
}

function JenkinsSnippet() {
  const [text, setText] = useState<string | null>(null);
  useEffect(() => {
    fetch("/data/use_it.json").then((r) => r.json()).then((j: { jenkinsfile: string }) => setText(j.jenkinsfile)).catch(() => setText("(the Jenkinsfile could not be loaded)"));
  }, []);
  return <pre className="mono mt-2 max-h-72 overflow-auto rounded bg-page p-2 text-xs">{text ?? "loading"}</pre>;
}

