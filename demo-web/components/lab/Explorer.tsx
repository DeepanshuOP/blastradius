"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Empty, Panel } from "./common";
import { GraphView, type GraphHandle } from "./GraphView";
import { NodeDetails } from "./NodeDetails";
import { useGraphDoc } from "./LabPage";
import { initialState } from "./useLab";
import type { GraphDoc } from "./types";

const NODE_TYPES = ["file", "class", "function", "test"];
const EDGE_TYPES = ["call", "import", "contains", "tests", "ref"];

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
  const g: GraphDoc | null = useGraphDoc(url);
  useEffect(() => { setTrace([]); setTraceMsg(""); setSelected(null); setSearch(""); }, [src]);

  const byLabel = useMemo(() => new Map((g?.nodes ?? []).map((n) => [n.id, n])), [g]);
  const find = (q: string) => {
    const t = q.trim().toLowerCase();
    if (!t) return null;
    const ns = g?.nodes ?? [];
    return ns.find((n) => n.id === q) ?? ns.find((n) => n.label.toLowerCase() === t) ?? ns.find((n) => `${n.file}::${n.label}`.toLowerCase().includes(t)) ?? null;
  };
  const doTrace = () => {
    const a = find(from), b = find(to);
    if (!a || !b || !g) { setTraceMsg("Both ends must match a node (type part of its name or file)."); setTrace([]); return; }
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

  return (
    <div className="mx-auto max-w-[1760px] space-y-3 px-3 py-3">
      <Panel title="Graph Explorer" right={
        <select value={src} onChange={(e) => setSrc(e.target.value)} aria-label="Graph source" className="mono max-w-[26rem] px-2 py-1 text-[12px]">
          {sources.map((x) => <option key={x.id} value={x.id}>{x.label}</option>)}
        </select>}>
        {note && <Empty>{note}</Empty>}
        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="relative h-[560px] overflow-hidden rounded border border-rule bg-page">
            {!g && <p className="ui absolute inset-0 m-0 grid place-items-center text-[13px] text-muted">{url ? "Loading the graph (the first build of a repository takes a few seconds)." : ""}</p>}
            <GraphView ref={ref} className="absolute inset-0" nodes={g?.nodes ?? []} edges={g?.edges ?? []} hiddenNodeTypes={hideN} hiddenEdgeTypes={hideE}
              search={search} trace={trace} selected={selected} onSelect={setSelected} />
          </div>
          <div className="space-y-3">
            <div>
              <label className="ui block text-[12px] text-muted" htmlFor="gx-search">Search</label>
              <input id="gx-search" type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="function, class or file" className="mono w-full px-2 py-1 text-[12px]" />
            </div>
            <div>
              <span className="ui block text-[12px] text-muted">Node types</span>
              <div className="flex flex-wrap gap-2">{NODE_TYPES.map((t) => <label key={t} className="ui flex items-center gap-1 text-[12px]"><input type="checkbox" checked={!hideN.includes(t)} onChange={() => toggle(hideN, setHideN, t)} />{t}{cnt ? ` (${cnt.nodes[t] ?? 0})` : ""}</label>)}</div>
              <span className="ui mt-1 block text-[12px] text-muted">Edge types</span>
              <div className="flex flex-wrap gap-2">{EDGE_TYPES.map((t) => <label key={t} className="ui flex items-center gap-1 text-[12px]"><input type="checkbox" checked={!hideE.includes(t)} onChange={() => toggle(hideE, setHideE, t)} />{t}{cnt ? ` (${cnt.edges[t] ?? 0})` : ""}</label>)}</div>
            </div>
            <div>
              <span className="ui block text-[12px] text-muted">Trace a path from A to B</span>
              <input type="text" value={from} onChange={(e) => setFrom(e.target.value)} placeholder="A: name or file" className="mono mb-1 w-full px-2 py-1 text-[12px]" aria-label="Trace from" />
              <input type="text" value={to} onChange={(e) => setTo(e.target.value)} placeholder="B: name or file" className="mono mb-1 w-full px-2 py-1 text-[12px]" aria-label="Trace to" />
              <button type="button" onClick={doTrace} className="ui rounded bg-ink px-2 py-1 text-[12px] text-page">Trace</button>
              {traceMsg && <p className="mono m-0 mt-1 break-words text-[11.5px] text-muted">{traceMsg}</p>}
            </div>
            <div className="rounded border border-rule bg-page p-2">
              <span className="ui block text-[12px] font-semibold">Coverage</span>
              {g ? (
                <dl className="mono m-0 text-[12px]">
                  <div className="flex justify-between"><dt className="text-muted">nodes</dt><dd className="m-0">{g.nodes.length}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted">edges</dt><dd className="m-0">{g.edges.length}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted">parse failures</dt><dd className="m-0">{g.parse_failures ?? "n/a"}{g.files_considered ? ` of ${g.files_considered} files` : ""}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted">commit</dt><dd className="m-0">{(g.commit ?? "").slice(0, 10) || "n/a"}</dd></div>
                </dl>
              ) : <Empty>no graph loaded</Empty>}
            </div>
          </div>
        </div>
      </Panel>
      {sel && g && <NodeDetails node={sel} nodes={g.nodes} edges={g.edges} repo={src.startsWith("repo:") ? src.slice(5) : null} s={{ ...initialState }} onClose={() => setSelected(null)} onSelect={(id) => { setSelected(id); ref.current?.center(id); }} />}
    </div>
  );
}
