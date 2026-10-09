"use client";

import { useEffect, useRef, useState } from "react";
import Markdown from "./Markdown";
import { Badge, Mono } from "./ui";

type Step = {
  agent: string;
  status: "ok" | "blocked" | "failed" | "skipped";
  headline: string;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  document: string;
};
type Scenario = {
  id: string; title: string; description: string; scope_policy: string; patch: string; outcome: string;
  baseline: Record<string, number>; steps: Step[];
  notifications: { ts: string; event: string; message: string; channels: string[] }[];
};
type AgentsDoc = { generated_at: string; story: string; title: string; note: string; scenarios: Scenario[] };

const FLOW: [string, string, string][] = [
  ["Impact Analysis", "user story + codebase", "impact analysis document"],
  ["Coding", "impact analysis + codebase", "changed files + pull request"],
  ["PR Reviewer", "PR + impact analysis", "review, merge, commit id"],
  ["Build & Deploy", "commit id + branch", "build, package, deploy / notify"],
  ["Regression Suite", "impact analysis + suite", "test report"],
];
const STEP_MS = 900;

const tone = (s: Step["status"]) => (s === "ok" ? "green" : s === "skipped" ? "slate" : s === "blocked" ? "amber" : "red") as "green" | "slate" | "amber" | "red";
const outcomeTone = (o: string) => (o === "Deployed" ? "green" : o.startsWith("Blocked") ? "amber" : "red") as "green" | "amber" | "red";

function Value({ v }: { v: unknown }) {
  if (Array.isArray(v)) {
    if (v.length && typeof v[0] === "object") {
      return <ul className="space-y-0.5">{(v as Record<string, unknown>[]).map((c, i) => (
        <li key={i} className="text-xs"><Badge tone={c.ok ? "green" : "red"}>{String(c.check)}</Badge> <span className="text-slate-600">{String(c.detail)}</span></li>))}</ul>;
    }
    return <ul className="space-y-0.5">{v.map((x, i) => <li key={i}><Mono>{String(x)}</Mono></li>)}</ul>;
  }
  if (typeof v === "boolean") return <span>{v ? "yes" : "no"}</span>;
  return <Mono>{v === null || v === undefined || v === "" ? "—" : String(v)}</Mono>;
}

function StepCard({ s, n }: { s: Step; n: number }) {
  const [open, setOpen] = useState(n === 1);
  return (
    <section className={`rounded-xl border bg-white p-5 shadow-sm ${s.status === "failed" ? "border-red-200" : s.status === "blocked" ? "border-amber-200" : "border-slate-200"}`}>
      <div className="flex flex-wrap items-center gap-3">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-orange-600 text-xs font-bold text-white">{n}</span>
        <h3 className="font-semibold text-slate-900">{s.agent}</h3>
        <Badge tone={tone(s.status)}>{s.status}</Badge>
      </div>
      <p className="mt-2 text-sm font-medium text-slate-800">{s.headline}</p>
      {s.status !== "skipped" && (
        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Input</p>
            <dl className="space-y-1 text-sm">{Object.entries(s.inputs).map(([k, v]) => <div key={k}><dt className="text-xs text-slate-500">{k}</dt><dd><Value v={v} /></dd></div>)}</dl>
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Output</p>
            <dl className="space-y-1 text-sm">{Object.entries(s.outputs).map(([k, v]) => <div key={k}><dt className="text-xs text-slate-500">{k}</dt><dd><Value v={v} /></dd></div>)}</dl>
          </div>
        </div>
      )}
      {s.document && (
        <div className="mt-3">
          <button onClick={() => setOpen(!open)} className="text-xs font-semibold text-orange-700 hover:underline">
            {open ? "Hide" : "Show"} the document this agent produced
          </button>
          {open && <div className="mt-2 max-h-[32rem] overflow-y-auto rounded-lg border border-slate-200 bg-white p-4"><Markdown text={s.document} /></div>}
        </div>
      )}
    </section>
  );
}

/** The five-agent workflow, replayed from data/agents.json (written by `make agents-demo`). */
export default function Agents() {
  const [doc, setDoc] = useState<AgentsDoc | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [sid, setSid] = useState("clean");
  const [shown, setShown] = useState(0);
  const [running, setRunning] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    fetch("/data/agents.json", { cache: "no-store" })
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setDoc).catch((e) => setErr(String(e)));
    return () => { if (timer.current) clearInterval(timer.current); };
  }, []);

  if (err) return <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">Could not load /data/agents.json ({err}). Run <Mono>make agents-demo</Mono>.</p>;
  if (!doc) return <p className="text-sm text-slate-500">Loading…</p>;
  const sc = doc.scenarios.find((s) => s.id === sid) ?? doc.scenarios[0];
  const stop = () => { if (timer.current) clearInterval(timer.current); timer.current = null; };
  const run = () => {
    stop(); setShown(0); setRunning(true);
    let n = 0;
    timer.current = setInterval(() => { n += 1; setShown(n); if (n >= sc.steps.length) { stop(); setRunning(false); } }, STEP_MS);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">From user story to deployed, regression-tested change</h2>
        <p className="mt-1 max-w-3xl text-sm text-slate-600">
          Five agents hand work to each other. The impact analysis uses the BlastRadius code graph to decide which tests a change puts at risk,
          and every later agent checks the work against it.
        </p>
      </div>
      <ol className="grid gap-3 sm:grid-cols-5">
        {FLOW.map(([name, input, output], i) => (
          <li key={name} className="relative rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
            <span className="text-[11px] font-semibold text-orange-600">AGENT {i + 1}</span>
            <p className="font-semibold text-slate-900">{name}</p>
            <p className="mt-1 text-xs text-slate-500">in: {input}</p>
            <p className="text-xs text-slate-700">out: {output}</p>
            {i < FLOW.length - 1 && <span aria-hidden className="absolute -right-2.5 top-1/2 hidden -translate-y-1/2 text-slate-400 sm:block">→</span>}
          </li>
        ))}
      </ol>
      <div className="rounded-lg border border-orange-200 bg-orange-50 px-4 py-3 text-sm text-orange-950">
        <span className="font-semibold">User story: </span>{doc.story}
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        {doc.scenarios.map((s) => (
          <button key={s.id} disabled={running} onClick={() => { stop(); setSid(s.id); setShown(0); }}
            className={`rounded-lg border p-4 text-left transition ${s.id === sc.id ? "border-slate-900 bg-white shadow" : "border-slate-200 bg-white/70 hover:border-slate-400"}`}>
            <div className="flex items-center justify-between gap-2">
              <span className="font-semibold text-slate-900">{s.title}</span>
              <Badge tone={outcomeTone(s.outcome)}>{s.outcome}</Badge>
            </div>
            <p className="mt-1 text-xs text-slate-600">{s.description}</p>
            <p className="mt-1 text-[11px] text-slate-500">reviewer scope policy: {s.scope_policy}</p>
          </button>
        ))}
      </div>
      <div className="flex items-center gap-4">
        <button onClick={run} disabled={running}
          className="rounded-md bg-slate-900 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400">
          {running ? "Running…" : shown >= sc.steps.length ? "Run again" : "Run the five agents"}
        </button>
        {shown > 0 && (
          <div className="flex-1">
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
              <div className="h-full rounded-full bg-orange-600 transition-all duration-500" style={{ width: `${(shown / sc.steps.length) * 100}%` }} />
            </div>
          </div>
        )}
      </div>
      <div className="space-y-4">
        {sc.steps.slice(0, shown).map((s, i) => <StepCard key={`${sc.id}-${i}`} s={s} n={i + 1} />)}
        {shown >= sc.steps.length && sc.notifications.map((n, i) => (
          <div key={i} className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-900">
            <p className="font-semibold">Notification sent ({n.event})</p>
            <p className="mt-1">{n.message}</p>
            <p className="mt-1 text-xs text-red-700">channels: {n.channels.join(", ")} · set BR_NOTIFY_WEBHOOK to also post to Slack or Discord</p>
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-500">{doc.note} Recorded with <Mono>make agents-demo</Mono>; run any agent live with <Mono>python -m src.agents</Mono>.</p>
    </div>
  );
}
