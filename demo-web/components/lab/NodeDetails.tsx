"use client";

import { useEffect, useState } from "react";
import { Panel } from "./common";
import type { GEdge, GNode, LabState } from "./types";

/** What the clicked node is, where it lives, what touches it, and why it is (not) at risk. */
export function NodeDetails({ node, nodes, edges, repo, s, onClose, onSelect }: {
  node: GNode; nodes: GNode[]; edges: GEdge[]; repo: string | null; s: LabState; onClose: () => void; onSelect: (id: string) => void;
}) {
  const [src, setSrc] = useState<string | null>(null);
  useEffect(() => {
    setSrc(null);
    if (!repo || !node.file) return;
    let alive = true;
    fetch(`/api/lab/file?repo=${encodeURIComponent(repo)}&path=${encodeURIComponent(node.file)}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("no source"))))
      .then((j: { text: string }) => {
        if (!alive) return;
        const lines = j.text.split("\n");
        const at = Math.max((node.line ?? 1) - 1, 0);
        setSrc(lines.slice(at, at + 14).map((l, i) => `${String(at + i + 1).padStart(4)}| ${l}`).join("\n"));
      })
      .catch(() => alive && setSrc(null));
    return () => { alive = false; };
  }, [node.id, node.file, node.line, repo]);
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const out = edges.filter((e) => e.source === node.id);
  const inn = edges.filter((e) => e.target === node.id);
  const hop = s.change?.wave?.hops?.[node.id] as number | undefined;
  const changed = (s.change?.changed_nodes as string[] | undefined)?.includes(node.id);
  const rank = (s.impact.ranking?.rows as { test: string; score: number; reasons: string[] }[] | undefined)?.find((r) => r.test === node.file);
  const path = (s.impact.paths?.paths as { test_file: string; path: string[] }[] | undefined)?.find((p) => p.path.includes(node.id));
  const why = changed ? "This node is part of the change."
    : rank ? `Its file is ranked ${(s.impact.ranking?.rows as { test: string }[]).findIndex((r) => r.test === node.file) + 1} at risk (score ${rank.score.toFixed(2)}): ${rank.reasons.join("; ")}.`
    : path ? `It lies on the shortest graph path from a changed function to ${path.test_file}.`
    : hop !== undefined ? `It is ${hop} hop${hop === 1 ? "" : "s"} from a changed node.`
    : s.change ? "It is not within 4 hops of any changed node." : "No change has been applied yet.";
  const Row = ({ e, dir }: { e: GEdge; dir: "out" | "in" }) => {
    const other = byId.get(dir === "out" ? e.target : e.source);
    return <li><button type="button" className="mono text-left text-[11.5px] hover:text-blue" onClick={() => other && onSelect(other.id)}><span className="text-muted">{dir === "out" ? "→" : "←"} {e.type} </span>{other?.label ?? (dir === "out" ? e.target : e.source)}</button></li>;
  };
  return (
    <Panel title={<>Node · {node.type}</>} right={<button type="button" onClick={onClose} className="ui rounded border border-rule px-2 py-0.5 text-[12px]">Close</button>}>
      <p className="mono m-0 break-all text-[13px]">{node.label}</p>
      <p className="ui m-0 mb-2 text-[12px] text-muted">{node.file}{node.line ? `:${node.line}` : ""}</p>
      <p className="ui m-0 mb-2 text-[12.5px]">{why}</p>
      {src && <pre className="mono m-0 mb-2 max-h-48 overflow-auto rounded bg-page p-2 text-[11px]">{src}</pre>}
      <div className="grid grid-cols-2 gap-3">
        <div><h5 className="ui m-0 mb-1 text-[11px] uppercase text-muted">Out ({out.length})</h5><ul className="m-0 max-h-32 list-none overflow-y-auto p-0">{out.slice(0, 40).map((e) => <Row key={e.id} e={e} dir="out" />)}</ul></div>
        <div><h5 className="ui m-0 mb-1 text-[11px] uppercase text-muted">In ({inn.length})</h5><ul className="m-0 max-h-32 list-none overflow-y-auto p-0">{inn.slice(0, 40).map((e) => <Row key={e.id} e={e} dir="in" />)}</ul></div>
      </div>
    </Panel>
  );
}
