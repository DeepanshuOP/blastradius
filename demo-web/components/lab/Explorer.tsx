"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { BTN, Empty, Panel, SEG } from "./common";
import { GraphView, type GraphHandle, type LayoutMode } from "./GraphView";
import { NodeCard } from "./NodeDetails";
import { useGraphDoc } from "./LabPage";
import { initialState } from "./useLab";
import type { GraphDoc } from "./types";

const NODE_TYPES = ["file", "class", "function", "test"];
const EDGE_TYPES = ["call", "import", "contains", "tests", "ref"];
const LAYOUTS: { id: LayoutMode; label: string; note: string }[] = [
  { id: "groups", label: "Files as groups", note: "each file is a box holding its classes, functions and tests" },
  { id: "force", label: "Force", note: "a force-directed layout of every node and edge" },
  { id: "rings", label: "Rings", note: "rings by hop distance from the node you centre on (by node type until then)" },
];

const LABEL = "ui mb-1 block text-xs font-medium text-muted";

/** The whole graph of one repository: search, type filters, a path trace between two nodes, coverage statistics. */
export function GraphExplorer() {
  const [sources, setSources] = useState<{ id: string; label: string; url: string }[]>([]);
  const [src, setSrc] = useState("");
  const [note, setNote] = useState("");
  const [search, setSearch] = useState("");
  const [hideN, setHideN] = useState<string[]>([]);
  const [hideE, setHideE] = useState<string[]>([]);
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [trace, setTrace] = useState<string[]>([]);
  const [traceMsg, setTraceMsg] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [layout, setLayout] = useState<LayoutMode>("groups");
  const [centre, setCentre] = useState<string[]>([]);
  const ref = useRef<GraphHandle>(null);

  useEffect(() => {
    let alive = true;
    const out: { id: string; label: string; url: string }[] = [];
    (async () => {
      try {
        const r = await fetch("/api/lab/repos");
        if (r.ok) (await r.json() as { repos: { name: string }[] }).repos.forEach((x) => out.push({ id: `repo:${x.name}`, label: `${x.name} (prepared repository, live graph)`, url: `/api/lab/graph?repo=${x.name}` }));
      } catch { /* static build */ }
      try {
        const r = await fetch("/lab/runs/index.json", { cache: "no-store" });
        if (r.ok) (await r.json() as { name: string; title?: string }[]).forEach((x) => out.push({ id: `run:${x.name}`, label: `recorded run: ${x.title ?? x.name}`, url: `/lab/runs/${x.name}.graph.json` }));
      } catch { /* none */ }
      if (!alive) return;
      setSources(out);
      if (out.length) setSrc((out.find((x) => x.id === "repo:itsdangerous") ?? out[0]).id); else setNote("No graph is available: this static build has no server and no recorded run.");
    })();
    return () => { alive = false; };
  }, []);

  const url = sources.find((x) => x.id === src)?.url ?? null;
  const { doc: g, error } = useGraphDoc(url);
  useEffect(() => { setTrace([]); setTraceMsg(""); setSelected(null); setSearch(""); setCentre([]); }, [src]);

  const byLabel = useMemo(() => new Map((g?.nodes ?? []).map((n) => [n.id, n])), [g]);
  const find = (q: string) => {
    const t = q.trim().toLowerCase();
    if (!t) return null;
    const ns = g?.nodes ?? [];
    return ns.find((n) => n.id === q) ?? ns.find((n) => n.label.toLowerCase() === t) ?? ns.find((n) => `${n.file}::${n.label}`.toLowerCase().includes(t)) ?? null;
  };
  const doTrace = () => {
    const a = find(from), b = find(to);
    if (!a || !b || !g) { setTraceMsg("Both ends must match a node: type part of its name or its file."); setTrace([]); return; }
    const adj = new Map<string, string[]>();
    g.edges.forEach((e) => { (adj.get(e.source) ?? adj.set(e.source, []).get(e.source)!).push(e.target); (adj.get(e.target) ?? adj.set(e.target, []).get(e.target)!).push(e.source); });
    const prev = new Map<string, string | null>([[a.id, null]]);
    const q = [a.id];
    while (q.length && !prev.has(b.id)) { const c = q.shift()!; for (const nb of adj.get(c) ?? []) if (!prev.has(nb)) { prev.set(nb, c); q.push(nb); } }
    if (!prev.has(b.id)) { setTrace([]); setTraceMsg(`No path between ${a.label} and ${b.label}.`); return; }
    const path: string[] = [];
    for (let x: string | null = b.id; x; x = prev.get(x) ?? null) path.unshift(x);
    setTrace(path);
    setTraceMsg(`${path.length - 1} hop(s): ${path.map((id) => byLabel.get(id)?.label ?? id).join(" → ")}`);
  };
  const toggle = (arr: string[], set: (a: string[]) => void, v: string) => set(arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]);
  const cnt = g?.counts;
  const sel = g?.nodes.find((n) => n.id === selected) ?? null;
  const empty: GraphDoc = { nodes: [], edges: [] };
  const gg = g ?? empty;

  return (
    <div className="mx-auto max-w-[1760px] space-y-3 px-3 py-3">
      <Panel title="Graph Explorer" right={
        <select value={src} onChange={(e) => setSrc(e.target.value)} aria-label="Graph source" className="mono max-w-[26rem] px-2 py-1 text-xs">
          {sources.map((x) => <option key={x.id} value={x.id}>{x.label}</option>)}
        </select>}>
        {note && <Empty title="No graph to show.">{note}</Empty>}
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
          <div className="relative h-[clamp(480px,calc(100vh-200px),760px)] overflow-hidden rounded border border-rule bg-page">
            {!g && <p className="ui absolute inset-0 m-0 grid place-items-center px-8 text-center text-sm text-muted">{error ? `The graph could not be loaded: ${error}` : url ? "Loading the graph (the first build of a repository takes a few seconds)." : ""}</p>}
            <GraphView ref={ref} className="absolute inset-0" nodes={gg.nodes} edges={gg.edges} layout={layout} seeds={centre} hiddenNodeTypes={hideN} hiddenEdgeTypes={hideE}
              search={search} trace={trace} selected={selected} onSelect={setSelected} ariaLabel="Repository graph"
              renderCard={(id, info) => sel && g && sel.id === id ? (
                <NodeCard node={sel} nodes={g.nodes} edges={g.edges} repo={src.startsWith("repo:") ? src.slice(5) : null} s={initialState} info={info}
                  onClose={() => setSelected(null)} onSelect={(x) => { setSelected(x); ref.current?.center(x); }}
                  actions={<button type="button" className={BTN} onClick={() => { setCentre([sel.id]); setLayout("rings"); setSelected(null); }}>Centre the rings here</button>} />
              ) : null} />
          </div>
          <div className="ui space-y-4 text-sm">
            <fieldset className="m-0 border-0 p-0">
              <legend className={LABEL}>Layout</legend>
              <div className="flex flex-wrap gap-1">{LAYOUTS.map((l) => <button key={l.id} type="button" onClick={() => setLayout(l.id)} aria-pressed={layout === l.id} className={SEG(layout === l.id)} title={l.note}>{l.label}</button>)}</div>
              <p className="m-0 mt-1 text-xs text-muted">{LAYOUTS.find((l) => l.id === layout)?.note}{layout === "rings" && centre.length ? `: centred on ${byLabel.get(centre[0])?.label ?? centre[0]}` : ""}.</p>
            </fieldset>
            <div>
              <label className={LABEL} htmlFor="gx-search">Search</label>
              <input id="gx-search" type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="function, class or file" className="mono w-full px-2 py-1 text-xs" />
            </div>
            <fieldset className="m-0 border-0 p-0">
              <legend className={LABEL}>Node types</legend>
              <div className="flex flex-wrap gap-x-3 gap-y-1">{NODE_TYPES.map((t) => <label key={t} className="flex items-center gap-1 text-sm"><input type="checkbox" checked={!hideN.includes(t)} onChange={() => toggle(hideN, setHideN, t)} />{t}{cnt ? <span className="num text-muted"> {cnt.nodes[t] ?? 0}</span> : ""}</label>)}</div>
            </fieldset>
            <fieldset className="m-0 border-0 p-0">
              <legend className={LABEL}>Edge types</legend>
              <div className="flex flex-wrap gap-x-3 gap-y-1">{EDGE_TYPES.map((t) => <label key={t} className="flex items-center gap-1 text-sm"><input type="checkbox" checked={!hideE.includes(t)} onChange={() => toggle(hideE, setHideE, t)} />{t}{cnt ? <span className="num text-muted"> {cnt.edges[t] ?? 0}</span> : ""}</label>)}</div>
            </fieldset>
            <div>
              <span className={LABEL}>Trace a path from A to B</span>
              <input type="text" value={from} onChange={(e) => setFrom(e.target.value)} placeholder="A: name or file" className="mono mb-1 w-full px-2 py-1 text-xs" aria-label="Trace from" />
              <input type="text" value={to} onChange={(e) => setTo(e.target.value)} placeholder="B: name or file" className="mono mb-2 w-full px-2 py-1 text-xs" aria-label="Trace to" />
              <button type="button" onClick={doTrace} className={BTN}>Trace</button>
              {traceMsg && <p className="mono m-0 mt-1 text-xs text-muted [overflow-wrap:anywhere]">{traceMsg}</p>}
            </div>
            <div className="rounded border border-rule bg-page p-2">
              <span className="mb-1 block text-xs font-semibold">Build</span>
              {g ? (
                <dl className="m-0 text-xs">
                  {[["nodes", g.nodes.length], ["edges", g.edges.length], ["parse failures", `${g.parse_failures ?? "n/a"}${g.files_considered ? ` of ${g.files_considered} files` : ""}`], ["commit", (g.commit ?? "").slice(0, 10) || "n/a"]].map(([k, v]) => (
                    <div key={String(k)} className="flex justify-between gap-2"><dt className="text-muted">{k}</dt><dd className="num mono m-0">{v}</dd></div>
                  ))}
                </dl>
              ) : <p className="m-0 text-xs text-muted">no graph loaded</p>}
            </div>
          </div>
        </div>
      </Panel>
    </div>
  );
}
