"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Empty, Icon, SEG } from "./common";
import type { Data } from "./types";

export type DiffLine = { kind: "ctx" | "add" | "del" | "hunk"; text: string; old: number | null; new: number | null };
export type FileDiff = { path: string; lines: DiffLine[] };

/** A unified diff split per file, each line carrying its base-side and head-side line numbers. */
export function parseDiff(diff: string): FileDiff[] {
  const files: FileDiff[] = [];
  let cur: FileDiff | null = null;
  let o = 0, n = 0;
  for (const ln of diff.split("\n")) {
    if (ln.startsWith("diff --git ")) { cur = { path: ln.replace(/^diff --git a\/(.*) b\/.*$/, "$1"), lines: [] }; files.push(cur); continue; }
    if (!cur || ln.startsWith("index ") || ln.startsWith("--- ") || ln.startsWith("+++ ") || ln.startsWith("new file") || ln.startsWith("deleted file")) {
      if (cur && ln.startsWith("+++ b/")) cur.path = ln.slice(6);
      continue;
    }
    const m = /^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$/.exec(ln);
    if (m) { o = Number(m[1]); n = Number(m[2]); cur.lines.push({ kind: "hunk", text: m[3].trim(), old: null, new: null }); continue; }
    if (ln.startsWith("+")) cur.lines.push({ kind: "add", text: ln.slice(1), old: null, new: n++ });
    else if (ln.startsWith("-")) cur.lines.push({ kind: "del", text: ln.slice(1), old: o++, new: null });
    else if (ln.startsWith(" ")) cur.lines.push({ kind: "ctx", text: ln.slice(1), old: o++, new: n++ });
  }
  return files;
}

/** The head-side text of a file: the base text with the diff's hunks applied. */
export function applyFileDiff(before: string, f: FileDiff): string {
  const src = before.split("\n");
  const out: string[] = [];
  let i = 0;                                       // 0-based index into src
  for (const l of f.lines) {
    if (l.kind === "hunk") continue;
    if (l.old !== null) { while (i < l.old - 1) out.push(src[i++]); }
    if (l.kind === "ctx") { out.push(src[i++] ?? l.text); }
    else if (l.kind === "del") i++;
    else if (l.kind === "add") out.push(l.text);
  }
  while (i < src.length) out.push(src[i++]);
  return out.join("\n");
}

/** Base-side line numbers that a unified diff removes or edits, per file. */
export function oldChangedLines(diff: string): Record<string, Set<number>> {
  const out: Record<string, Set<number>> = {};
  parseDiff(diff).forEach((f) => { out[f.path] = new Set(f.lines.filter((l) => l.kind === "del").map((l) => l.old as number)); });
  return out;
}

const ROW = { add: "bg-green/15", del: "bg-red/15", ctx: "", hunk: "bg-blue/10 text-blue" } as const;
const MARK = { add: "+", del: "−", ctx: " ", hunk: "" } as const;

/** The change: one diff view with a file picker and line numbers; "full file" shows the head-side file at the change. */
export function CodePanel({ change, className = "" }: { change: Data | null; className?: string }) {
  const files = useMemo(() => (change?.diff ? parseDiff(String(change.diff)) : []), [change?.diff]);
  const [active, setActive] = useState(0);
  const [view, setView] = useState<"diff" | "file">("diff");
  const scroller = useRef<HTMLDivElement>(null);
  const firstChange = useRef<HTMLDivElement>(null);
  useEffect(() => { setActive(Math.max(0, files.findIndex((f) => (change?.changed_functions ?? []).some((c: { file: string; function: string }) => c.file === f.path && c.function !== "<module>")))); setView("diff"); }, [change?.head]); // eslint-disable-line react-hooks/exhaustive-deps
  const f = files[active];
  const before = f ? (change?.before?.[f.path] as string | undefined) : undefined;
  const after = useMemo(() => (f && before !== undefined ? applyFileDiff(before, f) : null), [f, before]);
  const changedNew = useMemo(() => new Set(f ? f.lines.filter((l) => l.kind === "add").map((l) => l.new as number) : []), [f]);
  useEffect(() => {                                // the full-file view opens at the first changed line
    if (view === "file") window.requestAnimationFrame(() => firstChange.current?.scrollIntoView({ block: "center" }));
    else scroller.current?.scrollTo({ top: 0 });
  }, [view, active]);
  const fns = (change?.changed_functions ?? []) as { file: string; function: string; line: number }[];

  return (
    <div className={`flex min-h-0 flex-col ${className}`}>
      <div className="flex flex-wrap items-center gap-2 border-b border-rule px-3 py-2">
        {files.length > 0 ? (
          <label className="flex min-w-0 flex-1 items-center gap-1.5 text-xs text-muted">
            <span className="ui">file</span>
            <select value={active} onChange={(e) => setActive(Number(e.target.value))} className="mono min-w-0 flex-1 truncate px-1.5 py-0.5 text-xs" aria-label="Changed file">
              {files.map((x, i) => <option key={x.path} value={i}>{x.path} (+{x.lines.filter((l) => l.kind === "add").length} −{x.lines.filter((l) => l.kind === "del").length})</option>)}
            </select>
          </label>
        ) : <span className="ui flex-1 text-xs text-muted">no change yet</span>}
        <div className="flex gap-1" role="group" aria-label="View">
          <button type="button" onClick={() => setView("diff")} aria-pressed={view === "diff"} className={SEG(view === "diff")}>diff</button>
          <button type="button" onClick={() => setView("file")} aria-pressed={view === "file"} disabled={after === null} className={`${SEG(view === "file")} disabled:opacity-40`}>full file</button>
        </div>
      </div>
      <div ref={scroller} className="mono min-h-0 flex-1 overflow-auto text-xs" tabIndex={0} aria-label="Code">
        {!f ? (
          <div className="px-3"><Empty title="The diff appears here when the run commits the change.">Choose a repository and a change above, then press Run. Changed lines are highlighted and numbered on both sides.</Empty></div>
        ) : view === "diff" ? (
          <table className="w-full border-collapse">
            <tbody>
              {f.lines.map((l, i) => (
                <tr key={i} className={ROW[l.kind]}>
                  {l.kind === "hunk" ? (
                    <td colSpan={4} className="px-3 py-0.5 text-2xs">@@ {l.text}</td>
                  ) : (<>
                    <td className="num w-10 select-none pl-2 pr-1 text-right align-top text-muted">{l.old ?? ""}</td>
                    <td className="num w-10 select-none pr-1 text-right align-top text-muted">{l.new ?? ""}</td>
                    <td className={`w-4 select-none text-center align-top ${l.kind === "add" ? "text-green" : l.kind === "del" ? "text-red" : ""}`} aria-label={l.kind === "add" ? "added" : l.kind === "del" ? "removed" : undefined}>{MARK[l.kind]}</td>
                    <td className="whitespace-pre pr-3">{l.text || " "}</td>
                  </>)}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="py-1">
            {(after ?? "").split("\n").map((l, i) => {
              const ch = changedNew.has(i + 1);
              const first = ch && !Array.from(changedNew).some((x) => x < i + 1);
              return (
                <div key={i} ref={first ? firstChange : undefined} className={`flex ${ch ? "bg-accent/15" : ""}`}>
                  <span className="num w-10 shrink-0 select-none pr-2 text-right text-muted">{i + 1}</span>
                  <span className={`w-4 shrink-0 select-none text-center ${ch ? "text-accent" : ""}`}>{ch ? <Icon name="bolt" className="text-2xs" title="changed line" /> : ""}</span>
                  <span className="whitespace-pre pr-3">{l || " "}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
      {change && (
        <p className="ui m-0 border-t border-rule px-3 py-1.5 text-xs text-muted">
          <span className="mono">{String(change.base).slice(0, 10)}</span> → <span className="mono">{String(change.head).slice(0, 10)}</span>, committed in a scratch worktree.
          {fns.filter((x) => x.function !== "<module>").length ? <> Changed: <span className="mono text-ink">{fns.filter((x) => x.function !== "<module>").map((x) => x.function).join(", ")}</span>.</> : null}
        </p>
      )}
    </div>
  );
}
