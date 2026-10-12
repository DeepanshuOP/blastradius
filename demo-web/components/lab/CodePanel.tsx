"use client";

import { useEffect, useMemo, useState } from "react";
import { Empty, Panel } from "./common";
import { UnifiedDiff } from "./Diff";
import type { Data } from "./types";

/** Old-side (base commit) line numbers that a unified diff removes or edits, per file. */
export function oldChangedLines(diff: string): Record<string, Set<number>> {
  const out: Record<string, Set<number>> = {};
  let cur: string | null = null;
  let old = 0;
  for (const ln of diff.split("\n")) {
    if (ln.startsWith("--- a/")) { cur = ln.slice(6); out[cur] = out[cur] ?? new Set(); }
    else if (ln.startsWith("@@")) { const m = /@@ -(\d+)/.exec(ln); old = m ? Number(m[1]) : 0; }
    else if (cur && ln.startsWith("-") && !ln.startsWith("---")) { out[cur].add(old); old++; }
    else if (cur && ln.startsWith("+") && !ln.startsWith("+++")) { out[cur].add(Math.max(old - 1, 1)); }
    else if (cur && ln.startsWith(" ")) old++;
  }
  return out;
}

/** The change as a diff and the repository's files as a tree and viewer. */
export function CodePanel({ repo, change, className = "" }: { repo: string | null; change: Data | null; className?: string }) {
  const [files, setFiles] = useState<string[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [text, setText] = useState<string | null>(null);
  const [view, setView] = useState<"diff" | "file">("diff");
  const changedFiles: string[] = change?.changed_files ?? [];
  const marks = useMemo(() => (change?.diff ? oldChangedLines(change.diff) : {}), [change?.diff]);

  useEffect(() => {
    setFiles([]); setActive(null); setText(null);
    if (!repo) return;
    let alive = true;
    fetch(`/api/lab/file?repo=${encodeURIComponent(repo)}&tree=1`).then((r) => (r.ok ? r.json() : Promise.reject(new Error("no tree")))).then((j: { files: string[] }) => alive && setFiles(j.files)).catch(() => undefined);
    return () => { alive = false; };
  }, [repo]);

  useEffect(() => { if (change) setView("diff"); }, [change?.head]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    setText(null);
    if (!active) return;
    const before = change?.before?.[active] as string | undefined;
    if (before !== undefined) { setText(before); return; }
    if (!repo) return;
    let alive = true;
    fetch(`/api/lab/file?repo=${encodeURIComponent(repo)}&path=${encodeURIComponent(active)}`).then((r) => r.json()).then((j: { text: string }) => alive && setText(j.text)).catch(() => alive && setText(null));
    return () => { alive = false; };
  }, [active, repo, change?.before]);

  const shownFiles = useMemo(() => [...new Set([...changedFiles, ...files])], [changedFiles, files]);
  const lines = text?.split("\n") ?? [];
  return (
    <Panel id="panel-code" title="Code and change" className={className}
      right={<div className="flex gap-1">
        {(["diff", "file"] as const).map((v) => <button key={v} type="button" onClick={() => setView(v)} aria-pressed={view === v}
          className={`ui rounded px-1.5 py-0.5 text-[11.5px] ${view === v ? "bg-ink text-page" : "text-muted hover:text-ink"}`}>{v}</button>)}
      </div>}>
      <div className="grid h-[430px] grid-rows-[120px_minmax(0,1fr)] gap-2">
        <div className="min-h-0 overflow-y-auto rounded border border-rule bg-page py-1" role="tree" aria-label="Files">
          {shownFiles.length === 0 && <p className="ui m-0 px-2 text-[12px] text-muted">{repo ? "loading files" : "no file tree for this source"}</p>}
          {shownFiles.map((f) => (
            <button key={f} type="button" role="treeitem" aria-selected={active === f} onClick={() => { setActive(f); setView("file"); }}
              className={`mono block w-full truncate px-2 py-0.5 text-left text-[11.5px] ${active === f ? "bg-panel2" : "hover:bg-panel2"} ${changedFiles.includes(f) ? "text-accent" : ""}`} title={f}>
              {changedFiles.includes(f) ? "● " : ""}{f}
            </button>
          ))}
        </div>
        <div className="min-h-0 overflow-auto rounded border border-rule bg-page">
          {view === "diff" ? (
            change ? <UnifiedDiff diff={change.diff || "(the change produced no diff)"} /> : <div className="p-3"><Empty>The diff appears when a change is applied.</Empty></div>
          ) : !active ? <div className="p-3"><Empty>Choose a file.</Empty></div> : text === null ? <div className="p-3"><Empty>loading</Empty></div> : (
            <pre className="mono m-0 py-1 text-[11.5px] leading-[1.5]">
              {lines.map((l, i) => (
                <div key={i} className={`flex ${marks[active]?.has(i + 1) ? "bg-accent/20" : ""}`}>
                  <span className="w-10 shrink-0 select-none pr-2 text-right text-muted">{i + 1}</span>
                  <span className="whitespace-pre-wrap break-all">{l || " "}</span>
                </div>
              ))}
            </pre>
          )}
        </div>
      </div>
      {change && <p className="cap m-0 mt-2 text-[12px]">Base {String(change.base).slice(0, 10)} → head {String(change.head).slice(0, 10)}, committed in a scratch worktree. {change.changed_functions?.length ? `Changed: ${change.changed_functions.map((f: { function: string }) => f.function).join(", ")}.` : ""}</p>}
    </Panel>
  );
}
