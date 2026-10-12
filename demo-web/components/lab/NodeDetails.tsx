"use client";

import { useEffect, useState, type ReactNode } from "react";
import { Icon } from "./common";
import type { CardInfo } from "./GraphView";
import type { GEdge, GNode, LabState } from "./types";

/** The source lines of a node, read from the prepared repository (or the run's base text of a changed file). */
function useExcerpt(node: GNode, repo: string | null, before?: Record<string, string>): string | null {
  const [src, setSrc] = useState<string | null>(null);
  useEffect(() => {
    setSrc(null);
    if (!node.file) return;
    const cut = (text: string) => {
      const lines = text.split("\n");
      const at = Math.max((node.line ?? 1) - 1, 0);
      return lines.slice(at, at + 10).map((l, i) => `${String(at + i + 1).padStart(4)}  ${l}`).join("\n");
    };
    if (before?.[node.file] !== undefined) { setSrc(cut(before[node.file])); return; }
    if (!repo) return;
    let alive = true;
    fetch(`/api/lab/file?repo=${encodeURIComponent(repo)}&path=${encodeURIComponent(node.file)}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("no source"))))
      .then((j: { text: string }) => alive && setSrc(cut(j.text)))
      .catch(() => alive && setSrc(null));
    return () => { alive = false; };
  }, [node.id, node.file, node.line, repo, before]);
  return src;
}

/** Why a node is (or is not) at risk, in one sentence, from this run's events only. */
export function whyAtRisk(node: GNode, s: LabState, info: CardInfo | null): string {
  const changed = (s.change?.changed_nodes as string[] | undefined)?.includes(node.id);
  const rows = (s.impact.ranking?.rows as { test: string; score: number; reasons: string[] }[] | undefined) ?? [];
  const rank = rows.findIndex((r) => r.test === node.file);
  const path = (s.impact.paths?.paths as { test_file: string; path: string[] }[] | undefined)?.find((p) => p.path.includes(node.id));
  if (changed) return "This node is part of the change.";
  if (rank >= 0) return `Its test file is ranked ${rank + 1} of ${rows.length} at risk (score ${rows[rank].score.toFixed(2)}): ${rows[rank].reasons.join("; ")}.`;
  if (path) return `It lies on the shortest graph path from the change to ${path.test_file}.`;
  if (!s.change) return "No change has been applied yet, so nothing is at risk.";
  if (info && info.hop !== null) return `It is ${info.hop} hop${info.hop === 1 ? "" : "s"} from a changed node, but no ranked test file sits here.`;
  return "No path in the graph connects it to the change.";
}

export function NodeCard({ node, nodes, edges, repo, s, info, onClose, onSelect, actions }: {
  node: GNode; nodes: GNode[]; edges: GEdge[]; repo: string | null; s: LabState; info: CardInfo | null;
  onClose: () => void; onSelect: (id: string) => void; actions?: ReactNode;
}) {
  const src = useExcerpt(node, repo, s.change?.before as Record<string, string> | undefined);
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const out = edges.filter((e) => e.source === node.id);
  const inn = edges.filter((e) => e.target === node.id);
  const hop = info?.mode === "change" ? (info.hop === null ? "not reachable" : info.hop === 0 ? "the change" : `${info.hop} hop${info.hop === 1 ? "" : "s"}`) : "no change yet";
  return (
    <div className="ui rounded-md border border-rule bg-panel p-3 shadow-[0_8px_28px_rgb(0_0_0/0.45)]" role="dialog" aria-label={`Node ${node.label}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="m-0 text-2xs font-semibold uppercase tracking-wide text-muted">{node.type}</p>
          <p className="mono m-0 truncate text-sm font-semibold" title={node.label}>{node.label}</p>
        </div>
        <button type="button" onClick={onClose} className="rounded p-1 text-muted hover:text-ink" aria-label="Close the node card"><Icon name="close" /></button>
      </div>
      <dl className="m-0 mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 text-xs">
        <dt className="text-muted">where</dt><dd className="mono m-0 truncate" title={`${node.file}${node.line ? `:${node.line}` : ""}`}>{node.file}{node.line ? `:${node.line}` : ""}</dd>
        <dt className="text-muted">distance</dt><dd className="num m-0">{hop}</dd>
      </dl>
      <p className="m-0 mt-2 text-xs text-ink">{whyAtRisk(node, s, info)}</p>
      {src && <pre className="mono m-0 mt-2 max-h-40 overflow-auto rounded bg-page p-2 text-2xs leading-[17px]">{src}</pre>}
      {actions && <div className="mt-2 flex flex-wrap gap-2">{actions}</div>}
      <details className="mt-2 text-xs">
        <summary className="text-muted hover:text-ink">Edges: {out.length} out, {inn.length} in</summary>
        <ul className="m-0 mt-1 max-h-28 list-none overflow-y-auto p-0">
          {[...out.map((e) => [e, "out"] as const), ...inn.map((e) => [e, "in"] as const)].slice(0, 60).map(([e, dir]) => {
            const other = byId.get(dir === "out" ? e.target : e.source);
            return (
              <li key={`${dir}${e.id}`}>
                <button type="button" className="mono w-full truncate text-left text-2xs hover:text-blue" onClick={() => other && onSelect(other.id)}>
                  <span className="text-muted">{dir === "out" ? "→" : "←"} {e.type} </span>{other?.label ?? (dir === "out" ? e.target : e.source)}
                </button>
              </li>
            );
          })}
        </ul>
      </details>
    </div>
  );
}
