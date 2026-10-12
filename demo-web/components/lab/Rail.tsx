"use client";

import { useEffect, useState } from "react";
import { STAGE_LABEL, fmtMs } from "./common";
import { STAGES, type LabState, type Stage, type Status } from "./types";

const DOT: Record<Status | "pending", string> = { pending: "bg-rule", running: "bg-blue animate-pulse", ok: "bg-green", failed: "bg-red", skipped: "bg-muted" };

function jump(stage: Stage) {
  const map: Partial<Record<Stage, string>> = { repo: "panel-code", graph: "panel-graph", change: "panel-code", impact: "panel-impact", tests: "panel-tests", triage: "panel-triage", repair: "panel-repair", validate: "panel-repair", report: "panel-report" };
  document.getElementById(map[stage] ?? "panel-graph")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

const JENKINS: { name: string; stages: Stage[] }[] = [
  { name: "Checkout", stages: ["repo", "graph", "change"] },
  { name: "Predict", stages: ["impact"] },
  { name: "Test risk-first", stages: ["tests"] },
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

export function PipelineRail({ s }: { s: LabState }) {
  const [jenkins, setJenkins] = useState(false);
  const [snippet, setSnippet] = useState(false);
  return (
    <div className="rounded-md border border-rule bg-panel px-3 py-2">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <span className="ui text-[12px] font-semibold uppercase tracking-wide text-muted">{jenkins ? "Jenkins stage view (illustration)" : "Pipeline"}</span>
        <div className="flex items-center gap-3">
          <button type="button" onClick={() => setSnippet(!snippet)} className="ui text-[12px] text-blue underline" aria-expanded={snippet}>Jenkinsfile</button>
          <label className="ui flex cursor-pointer items-center gap-1.5 text-[12px] text-muted">
            <input type="checkbox" checked={jenkins} onChange={(e) => setJenkins(e.target.checked)} /> Show as Jenkins stage view
          </label>
        </div>
      </div>
      {!jenkins ? (
        <ol className="m-0 flex list-none items-stretch gap-1 overflow-x-auto p-0">
          {STAGES.map((k) => {
            const x = s.stage[k];
            return (
              <li key={k} className="min-w-[88px] flex-1">
                <button type="button" onClick={() => jump(k)} className="w-full rounded border border-rule bg-page px-2 py-1.5 text-left hover:border-muted" aria-label={`${STAGE_LABEL[k]}: ${x?.status ?? "pending"}`}>
                  <span className="flex items-center gap-1.5"><span className={`inline-block h-2 w-2 rounded-full ${DOT[x?.status ?? "pending"]}`} /><span className="ui text-[12.5px] font-medium">{STAGE_LABEL[k]}</span></span>
                  <span className="mono mt-0.5 block text-[11px] text-muted">{x ? (x.status === "running" ? "running" : x.status === "skipped" ? "skipped" : fmtMs(x.dur_ms)) : "pending"}</span>
                </button>
              </li>
            );
          })}
        </ol>
      ) : (
        <>
          <div className="grid grid-cols-7 gap-1.5" style={{ background: "var(--panel2)" }}>
            {JENKINS.map((c) => {
              const m = merged(s, c.stages);
              const col = { pending: "bg-rule/40", running: "bg-blue/30", ok: "bg-green/25", failed: "bg-red/30", skipped: "bg-muted/20" }[m.status];
              return (
                <div key={c.name} className="p-1 text-center">
                  <div className="ui mb-1 truncate text-[12px] font-semibold">{c.name}</div>
                  <div className={`rounded px-1 py-3 ${col}`}>
                    <div className="mono text-[12px]">{m.status === "pending" ? "–" : m.status === "running" ? "…" : fmtMs(m.dur)}</div>
                    <div className="ui text-[10.5px] uppercase text-muted">{m.status}</div>
                  </div>
                </div>
              );
            })}
          </div>
          <p className="cap m-0 mt-2 text-[11.5px]">The same stages and durations as this run, laid out as Jenkins draws a pipeline. No Jenkins server was involved: this shows where the stages would sit in an existing job. The example Jenkinsfile is not deployed.</p>
        </>
      )}
      {snippet && <JenkinsSnippet />}
    </div>
  );
}

function JenkinsSnippet() {
  const [text, setText] = useState<string | null>(null);
  useEffect(() => {
    fetch("/data/use_it.json").then((r) => r.json()).then((j: { jenkinsfile: string }) => setText(j.jenkinsfile)).catch(() => setText("(the Jenkinsfile could not be loaded)"));
  }, []);
  return <pre className="mono mt-2 max-h-72 overflow-auto rounded bg-page p-2 text-[11.5px]">{text ?? "loading"}</pre>;
}
