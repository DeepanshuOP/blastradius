"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ArenaPanel } from "./Arena";
import { CodePanel } from "./CodePanel";
import { BTN, Icon, Panel, Prov, StatusIcon, type Tone } from "./common";
import { GraphView, type GraphHandle } from "./GraphView";
import { EventLog } from "./Log";
import { NodeCard } from "./NodeDetails";
import { ImpactPanel, RacePanel, RepairPanel, TriagePanel, stageFailure } from "./Panels";
import { Picker, type Change, type RepoInfo, type RunInfo, type Scenario } from "./Picker";
import { Presenter } from "./Presenter";
import { PipelineRail } from "./Rail";
import { IntegrityPanel, ReportPanel } from "./Report";
import { TopBar } from "./TopBar";
import type { GEdge, GNode, GraphDoc, LabState, Stage } from "./types";
import { useLab } from "./useLab";

const MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"];

export type TabId = "impact" | "race" | "arena" | "triage" | "repair" | "comment" | "integrity";
export const RESULT_TABS: { id: TabId; label: string; stages: Stage[] }[] = [
  { id: "impact", label: "Impact", stages: ["repo", "graph", "change", "impact"] },
  { id: "race", label: "Test race", stages: ["tests"] },
  { id: "arena", label: "Strategy arena", stages: ["arena"] },
  { id: "triage", label: "Triage", stages: ["triage"] },
  { id: "repair", label: "Repair", stages: ["repair", "validate"] },
  { id: "comment", label: "PR comment", stages: ["report"] },
  { id: "integrity", label: "Integrity", stages: [] },
];
export const tabOf = (st: Stage): TabId => RESULT_TABS.find((t) => t.stages.includes(st))?.id ?? "impact";

function tabTone(s: LabState, stages: Stage[]): Tone {
  const xs = stages.map((k) => s.stage[k]?.status).filter(Boolean);
  if (!xs.length) return "pending";
  return xs.includes("failed") ? "failed" : xs.includes("running") ? "running" : xs.every((x) => x === "skipped") ? "skipped" : "ok";
}

/** Maps a result's canonical id onto graph test nodes (file + function name, parameters stripped). */
export function outcomeMap(nodes: GNode[], results: { id: string; outcome: string }[]): Record<string, "passed" | "failed"> {
  const byKey = new Map<string, string[]>();
  nodes.forEach((n) => {
    if (n.type === "test") {
      const k = `${n.file}::${n.label.replace(/^\./, "").replace(/\(\)$/, "")}`;
      (byKey.get(k) ?? byKey.set(k, []).get(k)!).push(n.id);
    }
  });
  const fileNode = new Map(nodes.filter((n) => n.type === "file").map((n) => [n.file, n.id]));
  const out: Record<string, "passed" | "failed"> = {};
  const mark = (id: string, failed: boolean) => { if (failed || out[id] === undefined) out[id] = failed ? "failed" : "passed"; };
  results.forEach((r) => {
    const parts = r.id.split("::");
    const failed = r.outcome === "failed" || r.outcome === "error";
    const name = parts[parts.length - 1].replace(/\[.*$/, "");
    byKey.get(`${parts[0]}::${name}`)?.forEach((id) => mark(id, failed));
    const f = fileNode.get(parts[0]);
    if (f) mark(f, failed);
  });
  return out;
}

export function useGraphDoc(url: string | null): { doc: GraphDoc | null; error: string | null } {
  const [doc, setDoc] = useState<GraphDoc | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    setDoc(null); setError(null);
    if (!url) return;
    let alive = true;
    fetch(url).then(async (r) => (r.ok ? r.json() : Promise.reject(new Error((await r.json().catch(() => ({}))).error ?? `HTTP ${r.status}`))))
      .then((j: GraphDoc) => alive && setDoc(j)).catch((e) => alive && setError(String(e.message ?? e)));
    return () => { alive = false; };
  }, [url]);
  return { doc, error };
}

/** The run's graph, the derived highlights (paths, at-risk files, outcomes) and the selection. */
export function useRunGraph(s: LabState, preview: GraphDoc | null) {
  const [full, setFull] = useState<GraphDoc | null>(null);
  useEffect(() => { setFull(null); }, [s.startedAt]);
  const runGraph: GraphDoc | null = full ?? (s.graph && s.graph.nodes.length ? (s.graph as GraphDoc) : preview);
  const nodes = useMemo(() => runGraph?.nodes ?? [], [runGraph]);
  const edges: GEdge[] = useMemo(() => runGraph?.edges ?? [], [runGraph]);
  const outcomes = useMemo(() => outcomeMap(nodes, s.tests.results), [nodes, s.tests.results.length]); // eslint-disable-line react-hooks/exhaustive-deps
  const paths = useMemo(() => ((s.impact.paths?.paths ?? []) as { path: string[] }[]).map((p) => p.path).filter((p) => p.length > 1), [s.impact.paths]);
  const atRisk = useMemo(() => {
    const files = new Set<string>((s.impact.ranking?.at_risk_files ?? []) as string[]);
    return nodes.filter((n) => n.type === "file" && files.has(n.file)).map((n) => n.id);
  }, [nodes, s.impact.ranking]);
  const changed = useMemo(() => (s.change?.changed_nodes as string[] | undefined) ?? [], [s.change]);
  const loadFull = async () => {
    const id = s.graph?.graph_id;
    if (!id) return;
    for (const u of [`/api/lab/graph?run=${id}`, `/lab/runs/${id}.graph.json`]) {
      try { const r = await fetch(u); if (r.ok) { setFull((await r.json()) as GraphDoc); return; } } catch { /* try next */ }
    }
  };
  return { runGraph, nodes, edges, outcomes, paths, atRisk, changed, full, loadFull };
}

export function GraphLegend({ outcomes }: { outcomes: Record<string, "passed" | "failed"> }) {
  const passed = Object.values(outcomes).filter((x) => x === "passed").length;
  const failed = Object.values(outcomes).length - passed;
  return (
    <div className="ui flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
      <span className="flex items-center gap-1"><span className="inline-block h-2.5 w-3 rounded-sm bg-blue" />file</span>
      <span className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5 rotate-45 bg-amber" />class</span>
      <span className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5 rounded-full bg-muted" />function</span>
      <span className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5 rounded-full border-2 border-green" />test</span>
      <span className="flex items-center gap-1 text-accent"><Icon name="bolt" />changed</span>
      <span className="flex items-center gap-1"><StatusIcon tone="passed" />passed</span>
      <span className="flex items-center gap-1"><StatusIcon tone="failed" />failed</span>
      {passed + failed > 0 && <span>test nodes: <span className="num text-ink">{passed}</span> passed, <span className="num text-ink">{failed}</span> with a failure</span>}
    </div>
  );
}

export default function LabPage() {
  const { state: s, avail, startLive, startReplay, reset } = useLab();
  const [repos, setRepos] = useState<RepoInfo[] | null>(null);
  const [runs, setRuns] = useState<RunInfo[]>([]);
  const [scenario, setScenario] = useState<Scenario>(null);
  const [change, setChange] = useState<Change>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [repairArena, setRepairArena] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [logOpen, setLogOpen] = useState(false);
  const [codeOpen, setCodeOpen] = useState(false);
  const [waveKey, setWaveKey] = useState(0);
  const [tab, setTab] = useState<TabId>("impact");
  const [presenting, setPresenting] = useState(false);
  const lastReplay = useRef<{ name: string; speed: number } | null>(null);
  const pinnedAt = useRef<Stage | null>(null);
  const graphRef = useRef<GraphHandle>(null);
  const results = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let alive = true;
    fetch("/lab/runs/index.json", { cache: "no-store" }).then((r) => (r.ok ? r.json() : [])).then((j: RunInfo[]) => alive && setRuns(j)).catch(() => undefined);
    if (avail.live) {
      fetch("/api/lab/repos").then((r) => r.json()).then((j: { repos: RepoInfo[]; runs: RunInfo[] }) => {
        if (!alive) return;
        setRepos(j.repos);
        if (j.runs.length) setRuns(j.runs);
      }).catch(() => alive && setRepos([]));
    }
    return () => { alive = false; };
  }, [avail.live]);

  const previewUrl = s.mode !== "idle" ? null : scenario?.kind === "repo" ? `/api/lab/graph?repo=${scenario.name}` : scenario?.kind === "replay" ? `/lab/runs/${scenario.name}.graph.json` : null;
  const preview = useGraphDoc(previewUrl);
  const g = useRunGraph(s, preview.doc);
  useEffect(() => { setSelected(null); setTab("impact"); pinnedAt.current = null; }, [s.startedAt]);

  const changeEv = useMemo(() => s.events.find((e) => e.type === "change.applied"), [s.events]);
  useEffect(() => { if (changeEv) setWaveKey(changeEv.seq); }, [changeEv]);

  // the active tab follows the running stage, unless the reader picked a tab while that stage was running
  const runningStage = useMemo(() => [...s.events].reverse().find((e) => e.stage !== "meta")?.stage ?? null, [s.events]);
  useEffect(() => {
    if (!runningStage) return;
    if (pinnedAt.current && pinnedAt.current === runningStage) return;
    pinnedAt.current = null;
    setTab(tabOf(runningStage));
  }, [runningStage]);
  const pick = (t: TabId) => { setTab(t); pinnedAt.current = runningStage; };
  const pickStage = (st: Stage) => { pick(tabOf(st)); results.current?.scrollIntoView({ behavior: "smooth", block: "start" }); };

  const sel = g.nodes.find((n) => n.id === selected) ?? null;
  const repoName = (s.repo?.prepared ? s.repo.name : null) ?? (scenario?.kind === "repo" ? scenario.name : null);
  const q = avail.quota?.[model];
  const quotaReason = q && !q.ok ? `the daily token quota of ${model} is used up (${q.used.toLocaleString()} of ${q.cap.toLocaleString()} tokens in the last 24 h, E3 and lab ledgers together)${q.resume_after ? `; the next call is possible after ${q.resume_after.replace("T", " ")} UTC` : ""}` : "";
  const modelOk = avail.llm && !quotaReason;
  const canRun = scenario !== null && (scenario.kind === "replay" || change !== null) && !s.running && (scenario.kind === "replay" || avail.live);
  const run = useCallback(() => {
    if (!scenario) return;
    if (scenario.kind === "replay") {
      lastReplay.current = { name: scenario.name, speed: Number(new URLSearchParams(window.location.search).get("speed")) || 1 };
      startReplay(lastReplay.current.name, lastReplay.current.speed);
      return;
    }
    lastReplay.current = null;
    if (!change) return;
    const body: Record<string, unknown> = { model, ...(scenario.kind === "repo" ? { repo: scenario.name } : { url: scenario.url }) };
    if (change.kind === "task") Object.assign(body, { task: change.id, variant: change.variant });
    if (change.kind === "inject") body.inject = { file: change.file, function: change.function, operator: change.operator, ...(change.line ? { line: change.line } : {}) };
    if (change.kind === "edit") body.edit = { file: change.file, text: change.text };
    if (!avail.llm) body.noLlm = true;
    if (repairArena && modelOk) body.repairArena = true;
    startLive(body);
  }, [scenario, change, model, avail.llm, repairArena, modelOk, startLive, startReplay]);

  const graphFail = stageFailure(s, "graph");
  const counts = s.graph?.counts ?? g.runGraph?.counts;
  const graphEmpty = s.running ? "Building the code graph of the base commit." : graphFail ? "" : preview.error ? `The graph could not be loaded: ${preview.error}` : scenario ? "Loading the graph (the first build of a repository takes a few seconds)." : "Pick a repository or a recorded run: its code graph appears here, and when the run applies the change the graph re-forms into rings around it.";

  return (
    <div className="mx-auto max-w-[1760px] space-y-3 px-3 py-3">
      <TopBar s={s} avail={avail} model={model} canRun={canRun} onRun={run} onReset={() => { reset(); setScenario(null); setChange(null); }}
        onIntegrity={() => { pick("integrity"); results.current?.scrollIntoView({ behavior: "smooth", block: "start" }); }} onPresent={() => setPresenting(true)} />
      {presenting && (
        <Presenter s={s} g={{ nodes: g.nodes, edges: g.edges, changed: g.changed, paths: g.paths, atRisk: g.atRisk, outcomes: g.outcomes }} onClose={() => setPresenting(false)}
          onRestart={() => { if (s.mode === "replay" && lastReplay.current) startReplay(lastReplay.current.name, lastReplay.current.speed); }} />
      )}
      {s.mode === "idle" && (
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <label className="ui text-xs text-muted" htmlFor="model">Model for the repair step</label>
          <select id="model" value={model} onChange={(e) => setModel(e.target.value)} className="mono px-2 py-1 text-xs">{MODELS.map((m) => <option key={m}>{m}</option>)}</select>
          <label className={`ui flex items-center gap-1.5 text-xs ${modelOk ? "text-ink" : "text-muted"}`} title={modelOk ? "Adds one model call: R1 (log-only) on the same failure, and what an unvalidated push would ship" : quotaReason || avail.reason}>
            <input type="checkbox" checked={repairArena && modelOk} disabled={!modelOk} onChange={(e) => setRepairArena(e.target.checked)} />
            Repair arena (one extra model call){avail.checked && !modelOk ? `: unavailable, ${quotaReason ? "quota used up" : avail.live ? "no model key on the server" : "static build"}` : ""}
          </label>
          {avail.checked && !avail.llm && avail.live && <span className="ui text-xs text-amber">{avail.reason}</span>}
          {quotaReason && <span className="ui text-xs text-amber" role="status">Repair is unavailable: {quotaReason}. Live runs still go through graph, prediction, tests, arena and triage.</span>}
        </div>
      )}
      <PipelineRail s={s} active={null} onPick={pickStage} />
      {s.error && <p className="ui m-0 flex items-center gap-2 rounded border border-red px-3 py-2 text-sm text-red" role="alert"><Icon name="warn" />{s.error}</p>}
      {s.repo && s.repo.tests_runnable === false && s.repo.reason && (
        <p className="ui m-0 rounded border border-amber px-3 py-2 text-sm text-amber" role="status">Tests were not run: {s.repo.reason}. The graph and the impact ranking are still real.</p>
      )}
      {s.mode === "idle" && (
        <Picker repos={repos} runs={runs} live={avail.live} reason={avail.reason} scenario={scenario} setScenario={setScenario} change={change} setChange={setChange} disabled={s.running} />
      )}

      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_320px] lab:grid-cols-[380px_minmax(0,1fr)_340px]">
        <Panel id="panel-code" title="The change" className="hidden min-h-0 flex-col lab:flex" bodyClass="flex min-h-0 flex-1 flex-col" right={<Prov mode={s.change ? s.mode : "idle"} />}>
          <CodePanel change={s.change} className="h-[clamp(420px,calc(100vh-300px),640px)]" />
        </Panel>
        <Panel id="panel-graph" title="Blast radius" bodyClass="p-0" right={
          <>
            <Prov mode={s.graph ? s.mode : "idle"} />
            <button type="button" onClick={() => setCodeOpen(true)} className={`${BTN} lab:hidden`} aria-haspopup="dialog">Change</button>
            <button type="button" onClick={() => setLogOpen(true)} className={`${BTN} lg:hidden`} aria-haspopup="dialog">Log</button>
            <button type="button" onClick={() => graphRef.current?.fit()} className={BTN} aria-label="Fit the graph">fit</button>
            <button type="button" onClick={() => graphRef.current?.zoomIn()} className={BTN} aria-label="Zoom in">+</button>
            <button type="button" onClick={() => graphRef.current?.zoomOut()} className={BTN} aria-label="Zoom out">−</button>
          </>}>
          <div className="relative h-[clamp(420px,calc(100vh-300px),640px)] overflow-hidden bg-page">
            {g.nodes.length === 0 && (
              <div className="absolute inset-0 grid place-items-center px-8 text-center">
                {graphFail ? <div className="max-w-md text-left"><p className="ui m-0 text-sm font-semibold text-red">The graph could not be built.</p><p className="mono m-0 mt-1 text-xs">{String(graphFail.data.reason)}</p><p className="ui m-0 mt-1 text-xs text-muted">Next: the run continues without it (ranking, tests and triage do not need the graph). Check the file named above, or pick a prepared repository.</p></div>
                  : <p className="ui m-0 max-w-md text-sm text-muted">{graphEmpty}</p>}
              </div>
            )}
            <GraphView ref={graphRef} className="absolute inset-0" nodes={g.nodes} edges={g.edges} layout="rings"
              changed={g.changed} waveKey={waveKey} paths={g.paths} atRisk={g.atRisk} outcomes={g.outcomes} selected={selected} onSelect={setSelected}
              ariaLabel="Blast-radius graph"
              renderCard={(id, info) => sel && sel.id === id ? (
                <NodeCard node={sel} nodes={g.nodes} edges={g.edges} repo={repoName} s={s} info={info} onClose={() => setSelected(null)} onSelect={(x) => { setSelected(x); graphRef.current?.center(x); }} />
              ) : null} />
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-rule px-3 py-2">
            <GraphLegend outcomes={g.outcomes} />
            {g.runGraph && <span className="num mono ml-auto text-xs text-muted">{s.graph?.n_nodes ?? g.nodes.length} nodes · {s.graph?.n_edges ?? g.edges.length} edges{counts ? ` · ${counts.nodes.test ?? 0} tests` : ""} · {s.graph?.parse_failures ?? g.runGraph.parse_failures ?? 0} parse failures</span>}
          </div>
          {s.graph?.truncated && !g.full && (
            <p className="ui m-0 border-t border-rule px-3 py-1.5 text-xs text-amber">Showing files and the 2-hop neighbourhood of the change ({s.graph.streamed_nodes ?? g.nodes.length} of {s.graph.n_nodes} nodes). <button type="button" className="underline" onClick={g.loadFull}>Load the full graph</button></p>
          )}
        </Panel>
        <Panel id="panel-log" title="Event log" className="hidden min-h-0 flex-col lg:flex" bodyClass="flex min-h-0 flex-1 flex-col" right={<Prov mode={s.mode} />}>
          <EventLog events={s.events} className="h-[clamp(420px,calc(100vh-300px),640px)]" />
        </Panel>
      </div>

      {codeOpen && (
        <Drawer side="left" title="The change" onClose={() => setCodeOpen(false)}>
          <CodePanel change={s.change} className="min-h-0 flex-1" />
        </Drawer>
      )}
      {logOpen && (
        <Drawer side="right" title="Event log" onClose={() => setLogOpen(false)}>
          <EventLog events={s.events} className="min-h-0 flex-1" />
        </Drawer>
      )}

      <section ref={results} id="results" className="scroll-mt-16 rounded-md border border-rule bg-panel" aria-label="Results">
        <div className="flex flex-wrap items-center gap-1 border-b border-rule px-2 pt-2" role="tablist" aria-label="Result views">
          {RESULT_TABS.map((t) => (
            <button key={t.id} type="button" role="tab" id={`tab-${t.id}`} aria-selected={tab === t.id} aria-controls={`tabpanel-${t.id}`} onClick={() => pick(t.id)}
              className={`ui -mb-px flex items-center gap-1.5 rounded-t border border-b-0 px-3 py-1.5 text-sm ${tab === t.id ? "border-rule bg-panel font-semibold text-ink" : "border-transparent text-muted hover:text-ink"}`}>
              {t.stages.length > 0 && <StatusIcon tone={tabTone(s, t.stages)} className="text-xs" />}{t.label}
            </button>
          ))}
          <span className="ml-auto pb-1.5 pr-1"><Prov mode={s.mode} /></span>
        </div>
        <div role="tabpanel" id={`tabpanel-${tab}`} aria-labelledby={`tab-${tab}`} className="p-4">
          {tab === "impact" && <ImpactPanel s={s} />}
          {tab === "race" && <RacePanel s={s} />}
          {tab === "arena" && <ArenaPanel s={s} />}
          {tab === "triage" && <TriagePanel s={s} />}
          {tab === "repair" && <RepairPanel s={s} />}
          {tab === "comment" && <ReportPanel s={s} />}
          {tab === "integrity" && <IntegrityPanel s={s} />}
        </div>
      </section>
    </div>
  );
}

export function Drawer({ side, title, onClose, children }: { side: "left" | "right"; title: string; onClose: () => void; children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const prev = document.activeElement as HTMLElement | null;
    ref.current?.focus();
    const on = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", on);
    return () => { window.removeEventListener("keydown", on); prev?.focus?.(); };
  }, [onClose]);
  return (
    <>
      <div className="fixed inset-0 z-30 bg-page/60" onClick={onClose} aria-hidden="true" />
      <aside ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={title}
        className={`fixed inset-y-0 z-40 flex w-full max-w-[520px] flex-col border-rule bg-panel shadow-[0_0_40px_rgb(0_0_0/0.5)] outline-none ${side === "left" ? "left-0 border-r" : "right-0 border-l"}`}>
        <header className="flex items-center justify-between border-b border-rule px-3 py-2"><h3 className="ui m-0 text-sm font-semibold">{title}</h3><button type="button" onClick={onClose} className={BTN}>Close</button></header>
        {children}
      </aside>
    </>
  );
}

