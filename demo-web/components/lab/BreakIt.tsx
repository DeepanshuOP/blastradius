"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { BTN, BTN_PRIMARY, Empty, Icon, Id, StatusIcon, fmtMs } from "./common";
import { SideBySide } from "./Diff";
import { applyMutation, type FnMut, type Mutation } from "./Picker";
import type { GNode, LabEvent, LabState } from "./types";

/** The function of a mutation listing that a graph node stands for: same leaf name, the nearest definition at or
 * after the node's line (overloads share one graph node, the first definition). */
export function matchFunction(node: GNode, fns: FnMut[]): FnMut | null {
  const leaf = node.label.replace(/^\./, "").replace(/\(\)$/, "");
  const cand = fns.filter((f) => f.function.split(".").slice(-1)[0] === leaf);
  if (cand.length <= 1) return cand[0] ?? null;
  const line = node.line ?? 0;
  return cand.slice().sort((a, b) => Math.abs((a.start ?? 0) - line) - Math.abs((b.start ?? 0) - line))[0];
}

/** Right-click (or long-press) menu on a function node: its real mutation operators, a diff preview, and Run. */
export function InjectMenu({ node, repo, x, y, box, disabled, onRun, onClose }: {
  node: GNode; repo: string; x: number; y: number; box: HTMLElement | null; disabled: boolean;
  onRun: (c: { file: string; function: string; operator: string; line: number }) => void; onClose: () => void;
}) {
  const [fn, setFn] = useState<FnMut | null | undefined>(undefined);
  const [text, setText] = useState<string | null>(null);
  const [pick, setPick] = useState<Mutation | null>(null);
  const [err, setErr] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number } | null>(null);
  useEffect(() => {
    let alive = true;
    setFn(undefined); setText(null); setPick(null); setErr("");
    Promise.all([
      fetch(`/api/lab/mutations?repo=${repo}&file=${encodeURIComponent(node.file)}`).then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))),
      fetch(`/api/lab/file?repo=${repo}&path=${encodeURIComponent(node.file)}`).then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))),
    ]).then(([m, f]: [{ functions: FnMut[] }, { text: string }]) => {
      if (!alive) return;
      setFn(matchFunction(node, m.functions ?? []));
      setText(f.text);
    }).catch((e) => alive && setErr(String(e.message ?? e)));
    return () => { alive = false; };
  }, [node, repo]);
  useEffect(() => {
    ref.current?.focus({ preventScroll: true });
    const on = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", on);
    return () => window.removeEventListener("keydown", on);
  }, [onClose]);
  // Fixed position in the viewport, anchored at the node and clamped so the whole menu, footer included, stays on screen.
  // Re-measured when the content changes (mutations load, a diff opens) and when the window or zoom changes.
  useLayoutEffect(() => {
    const place = () => {
      const el = ref.current;
      if (!el) return;
      const r = box?.getBoundingClientRect();
      const w = el.offsetWidth, h = el.offsetHeight;
      const left = Math.min(Math.max(8, (r?.left ?? 0) + x - 20), Math.max(8, window.innerWidth - w - 8));
      const top = Math.min(Math.max(8, (r?.top ?? 0) + y + 14), Math.max(8, window.innerHeight - h - 8));
      setPos((q) => (q && q.left === left && q.top === top ? q : { left, top }));
    };
    place();
    window.addEventListener("resize", place);
    return () => window.removeEventListener("resize", place);
  }, [box, x, y, fn, pick, err, text]);
  if (typeof document === "undefined") return null;
  return createPortal(
    <div ref={ref} tabIndex={-1} role="menu" aria-label={`Inject a bug in ${node.label}`} data-testid="inject-menu"
      className="ui fixed z-50 flex w-[420px] max-w-[calc(100vw-16px)] flex-col rounded-md border border-rule bg-panel shadow-[0_8px_28px_rgb(0_0_0/0.5)] outline-none"
      style={{ left: pos?.left ?? 8, top: pos?.top ?? 8, maxHeight: "calc(100vh - 16px)", visibility: pos ? "visible" : "hidden" }}>
      <div className="flex items-start justify-between gap-2 px-3 pb-2 pt-3">
        <p className="m-0 flex items-center gap-1.5 text-sm font-semibold"><Icon name="bug" className="text-accent" />Break this function</p>
        <button type="button" onClick={onClose} className="rounded p-0.5 text-muted hover:text-ink" aria-label="Close the menu"><Icon name="close" /></button>
      </div>
      {err ? <p className="m-0 px-3 pb-3 text-xs text-red">Could not list mutations: {err}</p>
        : fn === undefined ? <p className="m-0 px-3 pb-3 text-xs text-muted">Reading the function&apos;s mutation operators…</p>
        : fn === null ? <div className="px-3 pb-3"><Empty title="No mutation operator applies to this function." /></div>
        : (
          <>
            <p className="mono m-0 mb-2 truncate px-3 text-xs text-muted" title={`${node.file}::${fn.function}`}>{node.file}::{fn.function}</p>
            {/* ONE scroll area for the operators and the diff; the buttons below never scroll away */}
            <div className="min-h-0 overflow-y-auto px-3" style={{ maxHeight: "min(460px, calc(100vh - 220px))" }} data-testid="inject-scroll">
            <div className="space-y-1" role="group" aria-label="Mutation operators">
              {fn.mutations.map((m) => (
                <button key={`${m.operator}${m.line}${m.col}`} type="button" role="menuitemradio" aria-checked={pick === m} onClick={() => setPick(m)}
                  title={`${m.old} → ${m.new}`}
                  className={`flex w-full items-baseline gap-2 rounded border px-2 py-1 text-left text-xs ${pick === m ? "border-accent bg-accent/10" : "border-rule hover:border-muted"}`}>
                  <span className="mono font-semibold">{m.operator}</span><span className="num mono text-muted">L{m.line}</span>
                  <span className="mono min-w-0 truncate text-muted">{m.old} → {m.new}</span>
                </button>
              ))}
            </div>
            {pick && text !== null && <div className="mt-2"><SideBySide path={node.file} before={text} after={applyMutation(text, pick)} context={2} /></div>}
            </div>
            <div className="mt-2 flex shrink-0 items-center justify-end gap-2 border-t border-rule px-3 py-2">
              <button type="button" onClick={onClose} className={BTN}>Cancel</button>
              <button type="button" disabled={!pick || disabled} onClick={() => pick && onRun({ file: node.file, function: fn.function, operator: pick.operator, line: pick.line })} className={BTN_PRIMARY}>
                Break it
              </button>
            </div>
            {disabled && <p className="m-0 px-3 pb-2 text-xs text-muted">A run is in progress.</p>}
          </>
        )}
    </div>,
    document.body,
  );
}

export const gapOf = (s: LabState) => [...s.events].reverse().find((e) => e.type === "arena.gap")?.data as
  | { file: string; function: string; operator: string; line: number; old: string; new: string; before: string; after: string; n_cases: number;
      covering: string[]; coverage_status: string; graph_files: string[]; sentence: string } | undefined;

/** The test-gap sentence of the main screen, built from the event's own numbers (the presenter shows the full one). */
function shortGap(g: NonNullable<ReturnType<typeof gapOf>>): string {
  const n = g.coverage_status === "ok" ? g.covering.length : g.graph_files.length;
  const who = g.coverage_status === "ok" ? `${n} test${n === 1 ? "" : "s"} run ${g.function}` : `${n} test file${n === 1 ? "" : "s"} reach it`;
  return `All ${g.n_cases} tests passed. ${who}; none tells the two lines apart.`;
}

/** A known semantic change that the whole suite let through. */
export function TestGapPanel({ s, large = false }: { s: LabState; large?: boolean }) {
  const g = gapOf(s);
  if (!g) return null;
  return (
    <section className={`rounded-md border-2 border-amber bg-amber/10 ${large ? "p-6" : "p-4"}`} aria-labelledby="gap-title" role="alert">
      <h2 id="gap-title" className={`ui m-0 flex items-center gap-2 font-semibold text-amber ${large ? "text-2xl" : "text-lg"}`}><Icon name="warn" />Test gap: this bug survived the whole suite</h2>
      <div className={`mono mt-3 overflow-hidden rounded border border-rule bg-page ${large ? "text-lg leading-[30px]" : "text-sm"}`}>
        <div className="flex bg-red/15"><span className="num w-14 shrink-0 pr-2 text-right text-muted">{g.line}</span><span className="w-5 text-red">−</span><span className="whitespace-pre">{g.before.trimStart()}</span></div>
        <div className="flex bg-green/15"><span className="num w-14 shrink-0 pr-2 text-right text-muted">{g.line}</span><span className="w-5 text-green">+</span><span className="whitespace-pre">{g.after.trimStart()}</span></div>
      </div>
      <p className={`ui m-0 mt-3 ${large ? "text-xl" : "text-base"}`}>{large ? g.sentence : shortGap(g)}</p>
      {!large && (
        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <div>
            <p className="ui m-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted">Tests that execute {g.function} (coverage at the base commit)</p>
            {g.coverage_status !== "ok" ? <p className="ui m-0 text-xs text-muted">coverage was not recorded for this run</p> : g.covering.length === 0 ? <p className="ui m-0 text-xs">none</p> : (
              <ul className="m-0 list-none space-y-0.5 p-0">{g.covering.slice(0, 8).map((t) => <li key={t} className="flex items-center gap-1.5"><StatusIcon tone="passed" /><Id id={t} n={60} className="text-xs" /></li>)}
                {g.covering.length > 8 && <li className="ui text-xs text-muted">and {g.covering.length - 8} more, all passed</li>}</ul>
            )}
          </div>
          <div>
            <p className="ui m-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted">Test files that reach it in the graph</p>
            <ul className="m-0 list-none space-y-0.5 p-0">{g.graph_files.map((f) => <li key={f}><Id id={f} n={60} className="text-xs" /></li>)}</ul>
          </div>
        </div>
      )}
    </section>
  );
}

type ProbeRow = { i: number; operator: string; line: number; old: string; new: string; caught: boolean; failed: number; first_failed: string | null; wall_s: number; timed_out: boolean };
export type ProbeState = { running: boolean; fn: string; current: LabEvent | null; done: { rows: ProbeRow[]; caught: number; survived: number; n: number; wall_s: number; note: string } | null; error: string | null; skipped: string | null };

/** Suite strength on one function: streams `python -m src.lab probe` through the run route. */
export function useProbe() {
  const [p, setP] = useState<ProbeState | null>(null);
  const start = useCallback(async (repo: string, file: string, fn: string) => {
    setP({ running: true, fn, current: null, done: null, error: null, skipped: null });
    try {
      const r = await fetch("/api/lab/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ repo, probe: { file, function: fn } }) });
      if (!r.ok || !r.body) { const j = await r.json().catch(() => ({})); setP((x) => x && { ...x, running: false, error: j.error ?? `HTTP ${r.status}` }); return; }
      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i: number;
        while ((i = buf.indexOf("\n\n")) >= 0) {
          const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
          if (!chunk.startsWith("data: ")) continue;
          const ev = JSON.parse(chunk.slice(6)) as LabEvent;
          if (ev.type === "arena.probe") setP((x) => x && (ev.status === "running" ? { ...x, current: ev } : ev.status === "skipped" ? { ...x, skipped: String(ev.data.reason) } : { ...x, done: ev.data as ProbeState["done"] }));
          if (ev.type === "run.end" && ev.status === "failed") setP((x) => x && { ...x, error: String(ev.data.reason ?? "the probe failed") });
        }
      }
      setP((x) => x && { ...x, running: false });
    } catch (e) { setP((x) => x && { ...x, running: false, error: String(e) }); }
  }, []);
  return { probe: p, startProbe: start, clearProbe: () => setP(null) };
}

export function ProbePanel({ p, onClose }: { p: ProbeState; onClose: () => void }) {
  const c = p.current?.data;
  return (
    <section className="rounded-md border border-rule bg-panel p-4" aria-label="Suite strength">
      <div className="mb-2 flex items-center justify-between gap-2">
        <h2 className="ui m-0 text-base font-semibold">Suite strength: <span className="mono">{p.fn}</span></h2>
        <button type="button" onClick={onClose} disabled={p.running} className={BTN}>Close</button>
      </div>
      {p.error && <p className="ui m-0 text-sm text-red" role="alert">{p.error}</p>}
      {p.skipped && <Empty title="Nothing to probe.">{p.skipped}</Empty>}
      {p.running && c && !p.done && <p className="ui m-0 mb-2 flex items-center gap-2 text-sm text-blue" role="status"><span className="br-pulse inline-block h-2 w-2 rounded-full bg-blue" />mutant {c.i} of {c.n}: <span className="mono">{c.operator} L{c.line} {c.old} → {c.new}</span>, running the full suite…</p>}
      {p.done && (
        <>
          <p className="ui m-0 mb-2 text-sm"><span className="num font-semibold">{p.done.caught}</span> caught · <span className="num font-semibold">{p.done.survived}</span> survived · <span className="num">{fmtMs(p.done.wall_s * 1000)}</span>. {p.done.note}.</p>
          <table className="w-full text-sm">
            <thead><tr className="ui text-left text-2xs uppercase tracking-wide text-muted"><th className="py-1 pr-3 font-medium">Mutant</th><th className="pr-3 font-medium">Result</th><th className="pr-3 text-right font-medium">Failing tests</th><th className="font-medium">First failing test</th></tr></thead>
            <tbody>
              {p.done.rows.map((r) => (
                <tr key={r.i} className="border-t border-rule align-top">
                  <td className="py-1 pr-3"><span className="mono">{r.operator}</span> <span className="num mono text-muted">L{r.line}</span><span className="mono block text-xs text-muted">{r.old} → {r.new}</span></td>
                  <td className="pr-3">{r.caught ? <span className="ui flex items-center gap-1 text-green"><Icon name="check" />caught</span> : <span className="ui flex items-center gap-1 font-semibold text-amber"><Icon name="warn" />survived</span>}</td>
                  <td className="num mono pr-3 text-right">{r.failed}</td>
                  <td>{r.first_failed ? <Id id={r.first_failed} n={56} className="text-xs" /> : <span className="ui text-xs text-muted">none: the suite passed</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="cap m-0 mt-2 text-xs">LIVE: each mutant was applied in a scratch copy and the full suite run against it, one at a time, with no model. Caught means at least one test failed.</p>
        </>
      )}
    </section>
  );
}
