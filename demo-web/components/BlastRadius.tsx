"use client";

import { useMemo, useState } from "react";
import type { BlastDoc, BlastNode } from "./types";

const SIZE = 760;
const C = SIZE / 2;
const RING_LABELS = ["changed", "1 hop", "2 hops", "3 hops", "4 hops", "outer / unreachable"];
const ORANGE = "#ea580c";
const BLUE = "#2563eb";

function ringRadius(i: number, centreCount: number): number {
  if (i === 0) return centreCount <= 1 ? 0 : 55;
  return 55 + i * 62;
}

/** Radial blast-radius view: changed files at the centre, one ring per hop. */
export default function BlastRadius({ b }: { b: BlastDoc }) {
  const [showCo, setShowCo] = useState(true);
  const [showHist, setShowHist] = useState(true);
  const [hover, setHover] = useState<{ n: BlastNode; x: number; y: number } | null>(null);

  const pos = useMemo(() => {
    const rings: BlastNode[][] = Array.from({ length: b.max_hops + 2 }, () => []);
    for (const n of b.nodes) rings[n.hop === null ? b.max_hops + 1 : n.hop].push(n);
    const out = new Map<string, { x: number; y: number }>();
    rings.forEach((ring, i) => {
      const r = ringRadius(i, rings[0].length);
      [...ring].sort((a, z) => (a.id < z.id ? -1 : a.id > z.id ? 1 : 0)).forEach((n, j) => {
        const a = (2 * Math.PI * j) / Math.max(ring.length, 1) - Math.PI / 2 + i * 0.37;
        out.set(n.id, { x: C + r * Math.cos(a), y: C + r * Math.sin(a) });
      });
    });
    return { out, counts: rings.map((r) => r.length) };
  }, [b]);

  const nodeR = (n: BlastNode) => (n.kind === "file" || n.kind === "test" || !n.in_graph ? 5.5 : 3.5);
  const fill = (n: BlastNode) =>
    n.changed ? "#0f172a" : n.actual_failing ? "#dc2626" : n.kind === "test" ? "#fca5a5" : n.in_graph ? "#cbd5e1" : "#e2e8f0";
  const coHits = b.nodes.filter((n) => n.cochange_pred && n.actual_failing).length;
  const histHits = b.nodes.filter((n) => n.history_pred && n.actual_failing).length;

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-4 text-xs text-slate-600">
        <label className="flex cursor-pointer items-center gap-1.5">
          <input type="checkbox" checked={showCo} onChange={(e) => setShowCo(e.target.checked)} className="accent-orange-600" />
          co-change predictions ({b.nodes.filter((n) => n.cochange_pred).length}, {coHits} hit{coHits === 1 ? "" : "s"})
        </label>
        <label className="flex cursor-pointer items-center gap-1.5">
          <input type="checkbox" checked={showHist} onChange={(e) => setShowHist(e.target.checked)} className="accent-blue-600" />
          history predictions ({b.nodes.filter((n) => n.history_pred).length}, {histHits} hit{histHits === 1 ? "" : "s"})
        </label>
      </div>
      <div className="relative mx-auto max-w-[760px]" onMouseLeave={() => setHover(null)}>
        <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="h-auto w-full" role="img"
          aria-label="Code-graph neighbourhood of the changed files, one ring per hop">
          {pos.counts.map((cnt, i) => {
            const r = ringRadius(i, pos.counts[0]);
            if (r === 0) return null;
            return (
              <g key={i}>
                <circle cx={C} cy={C} r={r} fill="none" stroke={i === b.max_hops + 1 ? "#cbd5e1" : "#e2e8f0"}
                  strokeDasharray={i === b.max_hops + 1 ? "4 4" : undefined} />
                <text x={C} y={C - r - 4} textAnchor="middle" fontSize="10" fill="#94a3b8">
                  {RING_LABELS[i]} · {cnt}
                </text>
              </g>
            );
          })}
          {b.edges.map((e) => {
            const s = pos.out.get(e.source), t = pos.out.get(e.target);
            if (!s || !t) return null;
            return <line key={`${e.source}|${e.target}`} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#94a3b8" strokeOpacity={0.22} />;
          })}
          {b.nodes.map((n) => {
            const p = pos.out.get(n.id)!;
            const r = nodeR(n);
            return (
              <g key={n.id} onMouseEnter={() => setHover({ n, x: p.x, y: p.y })} className="cursor-pointer">
                {showHist && n.history_pred && (
                  <circle cx={p.x} cy={p.y} r={r + 6} stroke={BLUE} strokeWidth={1.6}
                    fill={n.actual_failing ? BLUE : "none"} fillOpacity={n.actual_failing ? 0.35 : 0} />
                )}
                {showCo && n.cochange_pred && (
                  <circle cx={p.x} cy={p.y} r={r + 3} stroke={ORANGE} strokeWidth={1.6}
                    fill={n.actual_failing ? ORANGE : "none"} fillOpacity={n.actual_failing ? 0.5 : 0} />
                )}
                <circle cx={p.x} cy={p.y} r={r} fill={fill(n)} stroke="#fff" strokeWidth={0.8} />
                <circle cx={p.x} cy={p.y} r={10} fill="transparent" />
              </g>
            );
          })}
        </svg>
        {hover && (
          <div className="pointer-events-none absolute z-10 max-w-xs -translate-x-1/2 rounded-md bg-slate-900 px-2.5 py-1.5 text-[11px] text-white shadow-lg"
            style={{ left: `${(hover.x / SIZE) * 100}%`, top: `calc(${(hover.y / SIZE) * 100}% + 14px)` }}>
            <div className="break-all font-mono">{hover.n.path ?? hover.n.label}</div>
            {hover.n.kind !== "file" && hover.n.in_graph && <div className="text-slate-300">{hover.n.kind} · {hover.n.label}</div>}
            <div className="text-slate-300">
              {hover.n.hop === null ? (hover.n.in_graph ? "beyond 4 hops" : "not reachable / not in graph") : `${hover.n.hop} hop${hover.n.hop === 1 ? "" : "s"} from a changed file`}
              {[hover.n.changed && "changed", hover.n.actual_failing && "actually failed", hover.n.cochange_pred && "co-change predicted",
                hover.n.history_pred && "history predicted"].filter(Boolean).map((x) => ` · ${x}`).join("")}
            </div>
          </div>
        )}
      </div>
      <div className="mt-3 flex flex-wrap justify-center gap-x-5 gap-y-2 text-xs text-slate-600">
        <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-full bg-slate-900" /> changed file</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-full bg-red-600" /> actually failing test file</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-full bg-red-300" /> other test node</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-full bg-slate-300" /> code node</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-3.5 w-3.5 rounded-full border-2 border-orange-600" /> co-change prediction</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-3.5 w-3.5 rounded-full border-2 border-blue-600" /> history prediction</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-3.5 w-3.5 rounded-full border-2 border-orange-600 bg-orange-300" /> filled ring = hit</span>
      </div>
      <p className="mt-2 text-center text-xs text-slate-500">
        {b.nodes.length} of {b.within_hops_total.toLocaleString()} nodes within {b.max_hops} hops shown
        {b.truncated.nodes ? ` (capped at ${b.caps.nodes}, priority: changed, failing, predicted, shortest paths, nearest)` : ""}
        ; {b.edges.length} edges{b.truncated.edges ? ` (capped at ${b.caps.edges})` : ""}. {b.note}.
      </p>
    </div>
  );
}
