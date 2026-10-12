"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CodePanel } from "./CodePanel";
import { Panel, Prov } from "./common";
import { GraphView, type GraphHandle } from "./GraphView";
import { EventLog } from "./Log";
import { NodeDetails } from "./NodeDetails";
import { ImpactPanel, RacePanel, RepairPanel, TriagePanel } from "./Panels";
import { Picker, type Change, type RepoInfo, type RunInfo, type Scenario } from "./Picker";
import { PipelineRail } from "./Rail";
import { IntegrityDrawer, ReportPanel } from "./Report";
import { TopBar } from "./TopBar";
import type { GEdge, GNode, GraphDoc } from "./types";
import { useLab } from "./useLab";

const MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"];
const LEGEND: [string, string][] = [["file", "bg-blue"], ["class", "bg-amber"], ["function", "bg-muted"], ["test", "border-2 border-green"], ["changed", "bg-accent"]];

/** Maps a result's canonical id onto graph test nodes (file + function name, parameters stripped). */
function outcomeMap(nodes: GNode[], results: { id: string; outcome: string }[]): Record<string, "passed" | "failed"> {
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

export function useGraphDoc(url: string | null): GraphDoc | null {
  const [doc, setDoc] = useState<GraphDoc | null>(null);
  useEffect(() => {
    setDoc(null);
    if (!url) return;
    let alive = true;
    fetch(url).then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status))))).then((j: GraphDoc) => alive && setDoc(j)).catch(() => undefined);
    return () => { alive = false; };
  }, [url]);
  return doc;
}

export default function LabPage() {
  const { state: s, avail, startLive, startReplay, reset } = useLab();
  const [repos, setRepos] = useState<RepoInfo[] | null>(null);
  const [runs, setRuns] = useState<RunInfo[]>([]);
  const [scenario, setScenario] = useState<Scenario>(null);
  const [change, setChange] = useState<Change>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [selected, setSelected] = useState<string | null>(null);
  const [logOpen, setLogOpen] = useState(false);
  const [integrity, setIntegrity] = useState(false);
  const [full, setFull] = useState<GraphDoc | null>(null);
  const [waveKey, setWaveKey] = useState(0);
  const graphRef = useRef<GraphHandle>(null);

  // repositories and recorded runs
  useEffect(() => {
    let alive = true;
    fetch("/lab/runs/index.json", { cache: "no-store" }).then((r) => (r.ok ? r.json() : [])).then((j: RunInfo[]) => alive && setRuns(j)).catch(() => undefined);
    if (avail.live) {
      fetch("/api/lab/repos").then((r) => r.json()).then((j: { repos: RepoInfo[]; runs: RunInfo[] }) => {
        if (!alive) return;
        setRepos(j.repos);
        if (j.runs.length) setRuns(j.runs);
      }).catch(() => undefined);
    }
    return () => { alive = false; };
  }, [avail.live]);

  // a graph to look at before anything runs: the chosen prepared repository, or a recorded run's stored graph
  const previewUrl = s.mode !== "idle" ? null : scenario?.kind === "repo" ? `/api/lab/graph?repo=${scenario.name}` : scenario?.kind === "replay" ? `/lab/runs/${scenario.name}.graph.json` : null;
  const preview = useGraphDoc(previewUrl);
  const runGraph: GraphDoc | null = full ?? (s.graph && s.graph.nodes.length ? (s.graph as GraphDoc) : preview);
  useEffect(() => { setFull(null); setSelected(null); }, [s.startedAt]);

  const changeEv = useMemo(() => s.events.find((e) => e.type === "change.applied"), [s.events]);
  useEffect(() => { if (changeEv) setWaveKey(changeEv.seq); }, [changeEv]);

  const nodes = runGraph?.nodes ?? [];
  const edges: GEdge[] = runGraph?.edges ?? [];
  const outcomes = useMemo(() => outcomeMap(nodes, s.tests.results), [nodes, s.tests.results.length]); // eslint-disable-line react-hooks/exhaustive-deps
  const paths = useMemo(() => ((s.impact.paths?.paths ?? []) as { path: string[] }[]).map((p) => p.path).filter((p) => p.length > 1), [s.impact.paths]);
  const atRisk = useMemo(() => {
    const files = new Set<string>((s.impact.ranking?.at_risk_files ?? []) as string[]);
    return nodes.filter((n) => n.type === "file" && files.has(n.file)).map((n) => n.id);
  }, [nodes, s.impact.ranking]);
  const sel = nodes.find((n) => n.id === selected) ?? null;
  const repoName = (s.repo?.prepared ? s.repo.name : null) ?? (scenario?.kind === "repo" ? scenario.name : null);

  const canRun = scenario !== null && (scenario.kind === "replay" || change !== null) && !s.running && (scenario.kind === "replay" || avail.live);
  const run = useCallback(() => {
    if (!scenario) return;
    if (scenario.kind === "replay") { startReplay(scenario.name, Number(new URLSearchParams(window.location.search).get("speed")) || 1); return; }
    if (!change) return;
    const body: Record<string, unknown> = { model, ...(scenario.kind === "repo" ? { repo: scenario.name } : { url: scenario.url }) };
    if (change.kind === "task") Object.assign(body, { task: change.id, variant: change.variant });
    if (change.kind === "inject") body.inject = { file: change.file, function: change.function, operator: change.operator, ...(change.line ? { line: change.line } : {}) };
    if (change.kind === "edit") body.edit = { file: change.file, text: change.text };
    if (!avail.llm) body.noLlm = true;
    startLive(body);
  }, [scenario, change, model, avail.llm, startLive, startReplay]);

  const loadFull = async () => {
    const id = s.graph?.graph_id;
    if (!id) return;
    for (const u of [`/api/lab/graph?run=${id}`, `/lab/runs/${id}.graph.json`]) {
      try { const r = await fetch(u); if (r.ok) { setFull((await r.json()) as GraphDoc); return; } } catch { /* try next */ }
    }
  };

  const counts = s.graph?.counts ?? runGraph?.counts;
  return (
    <div className="mx-auto max-w-[1760px] space-y-3 px-3 py-3">
      <TopBar s={s} avail={avail} model={model} canRun={canRun} onRun={run} onReset={() => { reset(); setScenario(null); setChange(null); }} onIntegrity={() => setIntegrity(true)} />
      {s.mode === "idle" && (
        <div className="flex flex-wrap items-center gap-3 text-[12.5px]">
          <label className="ui text-muted" htmlFor="model">Model</label>
          <select id="model" value={model} onChange={(e) => setModel(e.target.value)} className="mono px-2 py-1 text-[12px]">{MODELS.map((m) => <option key={m}>{m}</option>)}</select>
          {avail.checked && !avail.llm && avail.live && <span className="ui text-amber">{avail.reason}</span>}
        </div>
      )}
      <PipelineRail s={s} />
      {s.error && <p className="ui m-0 rounded border border-red px-3 py-2 text-[13px] text-red" role="alert">{s.error}</p>}
      {s.repo && s.repo.tests_runnable === false && s.repo.reason && (
        <p className="ui m-0 rounded border border-amber px-3 py-2 text-[13px] text-amber" role="status">Tests were not run: {s.repo.reason}. The graph and the impact ranking above are still real.</p>
      )}
      {s.mode === "idle" && (
        <Picker repos={repos} runs={runs} live={avail.live} reason={avail.reason} scenario={scenario} setScenario={setScenario} change={change} setChange={setChange} disabled={s.running} />
      )}

      <div className="grid gap-3 wide:grid-cols-[minmax(260px,0.95fr)_minmax(420px,1.6fr)_minmax(300px,1fr)]">
        <div className="grid min-w-0 gap-3 lg:grid-cols-[minmax(0,1fr)] wide:block">
          <CodePanel repo={repoName} change={s.change} />
        </div>
        <div className="min-w-0 space-y-3">
          <Panel id="panel-graph" title="Code graph" right={
            <>
              <Prov mode={s.graph ? s.mode : "idle"} />
              <button type="button" onClick={() => graphRef.current?.fit()} className="ui rounded border border-rule px-1.5 text-[12px]" aria-label="Fit graph">fit</button>
              <button type="button" onClick={() => graphRef.current?.zoomIn()} className="ui rounded border border-rule px-1.5 text-[12px]" aria-label="Zoom in">+</button>
              <button type="button" onClick={() => graphRef.current?.zoomOut()} className="ui rounded border border-rule px-1.5 text-[12px]" aria-label="Zoom out">−</button>
              <button type="button" onClick={() => setLogOpen(true)} className="ui rounded border border-rule px-1.5 text-[12px] wide:hidden">log</button>
            </>}>
            <div className="relative h-[430px] overflow-hidden rounded border border-rule bg-page">
              {nodes.length === 0 && <p className="ui absolute inset-0 m-0 grid place-items-center px-6 text-center text-[13px] text-muted">{s.running ? "Building the graph." : "Pick a repository to see its code graph."}</p>}
              <GraphView ref={graphRef} className="absolute inset-0" nodes={nodes} edges={edges}
                changed={(s.change?.changed_nodes as string[] | undefined) ?? []} hops={s.change?.wave?.hops} waveKey={waveKey}
                paths={paths} atRisk={atRisk} outcomes={outcomes} selected={selected} onSelect={setSelected} />
            </div>
            <div className="ui mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11.5px] text-muted">
              {LEGEND.map(([k, c]) => <span key={k} className="flex items-center gap-1"><span className={`inline-block h-2.5 w-2.5 rounded-sm ${c}`} />{k}</span>)}
              <span className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5 rounded-sm bg-green" />passed</span>
              <span className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5 rounded-sm bg-red" />failed</span>
              {runGraph && <span className="ml-auto mono">{s.graph?.n_nodes ?? nodes.length} nodes · {s.graph?.n_edges ?? edges.length} edges{counts ? ` · ${counts.nodes.test ?? 0} tests` : ""} · {s.graph?.parse_failures ?? runGraph.parse_failures ?? 0} parse failures</span>}
            </div>
            {s.graph?.truncated && !full && (
              <p className="ui m-0 mt-1 text-[12px] text-amber">Showing files and the 2-hop neighbourhood of the change ({s.graph.streamed_nodes ?? nodes.length} of {s.graph.n_nodes} nodes). <button type="button" className="underline" onClick={loadFull}>Load the full graph</button></p>
            )}
          </Panel>
          {sel && <NodeDetails node={sel} nodes={nodes} edges={edges} repo={repoName} s={s} onClose={() => setSelected(null)} onSelect={(id) => { setSelected(id); graphRef.current?.center(id); }} />}
        </div>
        <Panel id="panel-log" title="Event log" className="hidden wide:block" right={<Prov mode={s.mode} />}>
          <EventLog events={s.events} className="h-[470px]" />
        </Panel>
      </div>

      {logOpen && (
        <aside className="fixed inset-y-0 right-0 z-40 flex w-full max-w-md flex-col border-l border-rule bg-panel shadow-2xl wide:hidden" aria-label="Event log">
          <header className="flex items-center justify-between border-b border-rule px-3 py-2"><h3 className="ui m-0 text-[13px] font-semibold uppercase text-muted">Event log</h3><button type="button" onClick={() => setLogOpen(false)} className="ui rounded border border-rule px-2 py-0.5 text-[12px]">Close</button></header>
          <EventLog events={s.events} className="min-h-0 flex-1" />
        </aside>
      )}

      <ImpactPanel s={s} />
      <RacePanel s={s} />
      <TriagePanel s={s} />
      <RepairPanel s={s} />
      <ReportPanel s={s} />
      {integrity && <IntegrityDrawer s={s} onClose={() => setIntegrity(false)} />}
    </div>
  );
}
