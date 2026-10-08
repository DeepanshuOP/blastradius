import type { GraphPath } from "./types";

const W = 900;
const ROW = 110;
const NODE_W = 150;
const NODE_H = 40;
const PAD_X = 12;

function clip(s: string, n = 22) {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

/** Shortest paths from the test node (left) to the nearest changed files (right). */
export default function GraphPaths({ paths, testLabel }: { paths: GraphPath[]; testLabel: string }) {
  if (!paths.length) {
    return <p className="text-slate-500">No changed file is reachable from the test node in the base-commit graph.</p>;
  }
  const H = paths.length * ROW + 30;
  const leftX = PAD_X;
  const rightX = W - PAD_X - NODE_W;
  const testY = H / 2 - NODE_H / 2;

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full min-w-[640px]" role="img"
        aria-label="Shortest paths from the failing test to the changed files">
        <defs>
          <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="#94a3b8" />
          </marker>
        </defs>
        {paths.map((p, i) => {
          const y = 20 + i * ROW + (ROW - NODE_H) / 2 - 10;
          const mids = p.nodes.slice(1, -1);
          const changedNode = p.nodes[p.nodes.length - 1];
          const xs = mids.map((_, j) => leftX + NODE_W + ((rightX - leftX - NODE_W) * (j + 1)) / (mids.length + 1) - NODE_W / 2);
          const pts: { x: number; y: number }[] = [
            { x: leftX + NODE_W, y: testY + NODE_H / 2 },
            ...xs.flatMap((x) => [{ x, y: y + NODE_H / 2 }, { x: x + NODE_W, y: y + NODE_H / 2 }]),
            { x: rightX, y: y + NODE_H / 2 },
          ];
          const segs = [];
          for (let s = 0; s + 1 < pts.length; s += 2) segs.push([pts[s], pts[s + 1]]);
          return (
            <g key={p.changed_file}>
              {p.hops === 0 ? (
                <path d={`M${leftX + NODE_W},${testY + NODE_H / 2} C${W / 2},${testY + NODE_H / 2} ${W / 2},${y + NODE_H / 2} ${rightX},${y + NODE_H / 2}`}
                  fill="none" stroke="#cbd5e1" strokeDasharray="5 4" />
              ) : (
                segs.map(([a, b], s) => (
                  <g key={s}>
                    <path d={`M${a.x},${a.y} C${(a.x + b.x) / 2},${a.y} ${(a.x + b.x) / 2},${b.y} ${b.x},${b.y}`}
                      fill="none" stroke="#94a3b8" strokeWidth={1.5} markerEnd="url(#arr)" />
                    {p.edges[s] && (
                      <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 6} textAnchor="middle" fontSize="11" fill="#64748b">
                        {p.edges[s].relation}
                      </text>
                    )}
                  </g>
                ))
              )}
              {mids.map((n, j) => (
                <g key={n.id}>
                  <rect x={xs[j]} y={y} width={NODE_W} height={NODE_H} rx={6} fill="#f8fafc" stroke="#cbd5e1" />
                  <text x={xs[j] + NODE_W / 2} y={y + 17} textAnchor="middle" fontSize="12" fill="#334155">{clip(n.label)}</text>
                  <text x={xs[j] + NODE_W / 2} y={y + 31} textAnchor="middle" fontSize="10" fill="#94a3b8">{clip(n.file ?? "", 26)}</text>
                  <title>{`${n.label} — ${n.file ?? ""}`}</title>
                </g>
              ))}
              <rect x={rightX} y={y} width={NODE_W} height={NODE_H} rx={6} fill="#fffbeb" stroke="#f59e0b" />
              <text x={rightX + NODE_W / 2} y={y + 17} textAnchor="middle" fontSize="12" fill="#92400e">{clip(changedNode.label)}</text>
              <text x={rightX + NODE_W / 2} y={y + 31} textAnchor="middle" fontSize="10" fill="#b45309">
                {p.hops} hop{p.hops === 1 ? "" : "s"}{p.hops === 0 ? " · the test file itself" : ""}
              </text>
              <title>{p.changed_file}</title>
            </g>
          );
        })}
        <rect x={leftX} y={testY} width={NODE_W} height={NODE_H} rx={6} fill="#fef2f2" stroke="#ef4444" />
        <text x={leftX + NODE_W / 2} y={testY + 17} textAnchor="middle" fontSize="12" fill="#991b1b">{clip(testLabel)}</text>
        <text x={leftX + NODE_W / 2} y={testY + 31} textAnchor="middle" fontSize="10" fill="#b91c1c">failing test</text>
      </svg>
      <div className="mt-2 flex flex-wrap gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded border border-red-500 bg-red-50" /> failing test</span>
        <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded border border-slate-300 bg-slate-50" /> intermediate code node</span>
        <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded border border-amber-500 bg-amber-50" /> changed file</span>
      </div>
    </div>
  );
}
