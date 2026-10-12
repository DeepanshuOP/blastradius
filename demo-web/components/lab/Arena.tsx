"use client";

import { useState } from "react";
import { Empty, Icon, Id, StatusIcon, fmtMs, type Tone } from "./common";
import { UnifiedDiff } from "./Diff";
import { CHECKS } from "./Panels";
import type { LabState } from "./types";

/** One strategy, computed from this run's full-suite results (`src/lab/arena.py`). */
export interface Strategy {
  id: string; name: string; what: string; source: string; ours: boolean;
  kind: "selector" | "orderer"; needs: string; orders_all: boolean;
  status: "ok" | "cold-start" | "unavailable"; note: string;
  selected: number; pct: number; caught: number; n_failing: number; recall: number | null;
  first_failure_position: number | null; first_failure_ms: number | null; ci_ms: number; missed: string[];
}
export interface ArenaDoc {
  basis: string; unit: string; n_cases: number; n_failing: number; suite_ms: number; strategies: Strategy[]; takeaway: string;
  coverage: { status: string; wall_s?: number; cached?: boolean; n_tests?: number; n_functions?: number; reason?: string };
  history: { n_runs: number | null; store?: string };
  cochange: { n_commits: number; reason?: string; upstream?: { status: string; commits: number; fetch_s: number; reason: string } };
  rule?: { id: string; fixed: string; text: string };
  rederived?: { date: string; rule: string; rows: string[]; note: string; before: Record<string, { first_failure_position: number | null; first_failure_ms: number | null; status: string }> };
}
export interface RepairColumn {
  id: "R1" | "R2" | "push"; title: string; input: string; chunks: { file: string; qualname: string }[];
  tokens: number | null; from_cache: boolean | null; diff: string; accepted: boolean | null;
  checks: { name: string; ok: boolean | null; evidence: string }[]; note: string;
}
export interface RepairArenaDoc { failure: string[]; columns: RepairColumn[]; note: string; tokens: number }

export const arenaOf = (s: LabState): ArenaDoc | null => ([...s.events].reverse().find((e) => e.type === "arena.result")?.data as ArenaDoc | undefined) ?? null;
export const repairArenaOf = (s: LabState) => [...s.events].reverse().find((e) => e.type === "arena.repair");

const pct = (x: number | null) => (x === null ? "–" : `${(x * 100).toFixed(x === 1 || x === 0 ? 0 : 1)}%`);

/** The comparison tables: orderers (run every test, change the order) and selectors (run fewer tests), every number
 * computed from this run's results. */
export function ArenaTable({ a, large = false }: { a: ArenaDoc; large?: boolean }) {
  const T = large ? "text-lg" : "text-sm";
  const S = large ? "text-base" : "text-xs";
  const orderers = a.strategies.filter((x) => (x.kind ?? (x.id === "retest-all" || x.ours ? "orderer" : "selector")) === "orderer");
  const selectors = a.strategies.filter((x) => !orderers.includes(x));
  const name = (x: Strategy) => (
    <td className={`pr-4 ${large ? "py-2" : "py-1.5"}`}>
      <span className="ui font-semibold">{x.name}</span>{x.ours && <span className={`ui ml-2 rounded bg-accent/20 px-1.5 ${S} font-semibold text-accent`}>ours</span>}
      <span className={`ui block ${S} text-muted`}>{x.status === "ok" || x.kind === "orderer" ? x.what : x.note}</span>
    </td>
  );
  const needs = (x: Strategy) => <td className={`ui ${S} text-muted`}>{x.needs ?? "–"}</td>;
  const head = (cols: string[]) => (
    <thead>
      <tr className={`ui text-left ${S} uppercase tracking-wide text-muted`}>
        {cols.map((c, k) => <th key={c} className={`py-1 pr-4 font-medium ${k > 0 && k < cols.length - 1 ? "text-right" : ""}`}>{c}</th>)}
      </tr>
    </thead>
  );
  return (
    <div className="space-y-4 overflow-x-auto">
      <section aria-label="Orderers">
        <h4 className={`ui m-0 mb-1 ${S} font-semibold uppercase tracking-wide text-muted`}>Orderers: run all {a.n_cases} tests, change the order</h4>
        <table className={`w-full ${T}`}>
          {head(["Strategy", "Tests until first failure", "Time to first failure", "Orders all", "Needs"])}
          <tbody>
            {orderers.map((x) => (
              <tr key={x.id} className={`border-t border-rule align-top ${x.ours ? "bg-accent/10" : ""}`}>
                {name(x)}
                <td className="num mono whitespace-nowrap pr-4 text-right">{x.status === "unavailable" ? "–" : x.first_failure_position ? `#${x.first_failure_position}` : a.n_failing === 0 ? "no failure" : "–"}</td>
                <td className="num mono whitespace-nowrap pr-4 text-right">{x.first_failure_ms !== null && x.first_failure_ms !== undefined ? fmtMs(x.first_failure_ms) : "–"}</td>
                <td className="num mono whitespace-nowrap pr-4 text-right">{x.status === "unavailable" ? "–" : x.orders_all ? `all ${a.n_cases}` : `${x.selected}`}</td>
                {needs(x)}
              </tr>
            ))}
          </tbody>
        </table>
        {a.rule && !large && <p className={`ui m-0 mt-2 ${S} text-muted`}>BlastRadius order rule, fixed on {a.rule.fixed}, after the PR 1 case was seen: {a.rule.text.replace(/ Fixed on .*$/, "")}</p>}
      </section>
      <section aria-label="Selectors">
        <h4 className={`ui m-0 mb-1 ${S} font-semibold uppercase tracking-wide text-muted`}>Selectors: run fewer tests, can miss failures</h4>
        <table className={`w-full ${T}`}>
          {head(large ? ["Strategy", "Tests run", "Failures caught", "Needs"] : ["Strategy", "Tests run", "Failures caught", "Needs", "Missed"])}
          <tbody>
            {selectors.map((x) => (
              <tr key={x.id} className="border-t border-rule align-top">
                {name(x)}
                <td className="num mono whitespace-nowrap pr-4 text-right">{x.status === "unavailable" ? "–" : <>{x.selected}<span className="text-muted"> · {x.pct.toFixed(0)}%</span></>}</td>
                <td className="num mono whitespace-nowrap pr-4 text-right">{x.status === "unavailable" ? "–" : a.n_failing === 0 ? "no failures" : <>{x.caught}/{a.n_failing}<span className="text-muted"> · {pct(x.recall)}</span></>}</td>
                {needs(x)}
                {!large && <td className={`${S}`}>{x.status !== "ok" || a.n_failing === 0 ? "–" : x.missed.length === 0 ? <span className="flex items-center gap-1 text-green"><Icon name="check" />none</span> : <MissedList ids={x.missed} />}</td>}
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <p className={`ui m-0 ${S} text-muted`}>
        Every row: {a.basis}. Unit: {a.unit}; {a.n_cases} in the suite, {a.n_failing} failing. Each strategy is an approach re-implemented here, not the vendor&apos;s product.
        {a.rederived && <> Rows re-derived on {a.rederived.date.slice(0, 10)} from this recording&apos;s stored results ({a.rederived.rows.join(", ")}); the run itself was executed in the earlier order.</>}
      </p>
    </div>
  );
}

function MissedList({ ids }: { ids: string[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button type="button" onClick={() => setOpen(!open)} aria-expanded={open} className="ui flex items-center gap-1 text-red hover:underline"><Icon name="cross" />{ids.length} missed</button>
      {open && <ul className="m-0 mt-1 list-none space-y-0.5 p-0">{ids.slice(0, 30).map((t) => <li key={t}><Id id={t} n={46} className="text-2xs" /></li>)}{ids.length > 30 && <li className="ui text-2xs text-muted">{ids.length - 30} more</li>}</ul>}
    </div>
  );
}

/** One chart: for each strategy, the share of the suite it runs against the share of failures it catches. */
export function ArenaChart({ a }: { a: ArenaDoc }) {
  const [hover, setHover] = useState<string | null>(null);
  const rows = a.strategies.filter((x) => x.status !== "unavailable" && x.kind === "selector");
  const hasRecall = a.n_failing > 0;
  return (
    <figure className="m-0">
      <figcaption className="ui mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted">
        <span className="text-sm font-semibold text-ink">Selectors: failures caught against share of the suite run</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-chart1" />share of the suite run</span>
        {hasRecall && <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-chart2" />failures caught (recall)</span>}
      </figcaption>
      <div className="space-y-2.5" role="table" aria-label="Share of the suite run and failures caught, per strategy">
        {rows.map((x) => {
          const run = Math.min(x.pct, 100);
          const rec = x.recall === null ? null : x.recall * 100;
          const tip = `${x.name}: runs ${x.selected} of ${a.n_cases} tests (${x.pct.toFixed(1)}%)${rec === null ? "" : `, catches ${x.caught} of ${a.n_failing} failures (${rec.toFixed(1)}%)`}`;
          return (
            <div key={x.id} role="row" className="grid grid-cols-[9.5rem_minmax(0,1fr)] items-center gap-3" onMouseEnter={() => setHover(x.id)} onMouseLeave={() => setHover(null)} title={tip}>
              <span role="rowheader" className={`ui truncate text-xs ${x.ours ? "font-semibold text-ink" : "text-muted"}`}>{x.name}</span>
              <div role="cell" className="relative space-y-[2px]">
                <div className="flex items-center gap-2"><div className="h-2 rounded-r bg-chart1" style={{ width: `${Math.max(run, 0.6)}%` }} /><span className="num mono text-2xs text-muted">{x.pct.toFixed(0)}%</span></div>
                {hasRecall && <div className="flex items-center gap-2"><div className="h-2 rounded-r bg-chart2" style={{ width: `${Math.max(rec ?? 0, 0.6)}%` }} /><span className="num mono text-2xs text-ink">{rec === null ? "–" : `${rec.toFixed(0)}%`}</span></div>}
                {hover === x.id && <div className="ui pointer-events-none absolute -top-9 left-0 z-10 whitespace-nowrap rounded border border-rule bg-panel px-2 py-1 text-xs shadow-[0_4px_16px_rgb(0_0_0/0.4)]">{tip}</div>}
              </div>
            </div>
          );
        })}
        <div className="grid grid-cols-[9.5rem_minmax(0,1fr)] gap-3" aria-hidden="true"><span /><div className="num mono flex justify-between border-t border-rule pt-1 text-2xs text-muted"><span>0%</span><span>50%</span><span>100%</span></div></div>
      </div>
    </figure>
  );
}

const CHECK_TONE = (c: { ok: boolean | null } | undefined): Tone => (!c ? "pending" : c.ok === null ? "skipped" : c.ok ? "ok" : "failed");

/** R1 (log-only) against R2 (change-aware) on the same failure, and what an unvalidated push would have shipped. */
export function RepairArena({ s }: { s: LabState }) {
  const ev = repairArenaOf(s);
  if (!ev) return null;
  if (ev.status === "running") return <p className="ui m-0 text-sm text-blue">Repair arena: the R1 (log-only) call is running…</p>;
  if (ev.status === "skipped") return <Empty title="The repair arena did not run.">{String(ev.data.reason)}</Empty>;
  const d = ev.data as RepairArenaDoc;
  return (
    <div>
      <h4 className="ui m-0 mb-1 text-sm font-semibold">Repair arena: the same failure, three behaviours</h4>
      <p className="ui m-0 mb-3 text-xs text-muted">{d.note}</p>
      <div className="grid gap-3 lg:grid-cols-3">
        {d.columns.map((c) => (
          <div key={c.id} className={`min-w-0 rounded-md border p-3 ${c.id === "R2" ? "border-accent/60" : "border-rule"} bg-page`}>
            <p className="ui m-0 text-sm font-semibold">{c.title}</p>
            <p className="ui m-0 mb-2 text-xs text-muted">{c.input}</p>
            {c.tokens !== null && <p className="ui m-0 mb-2 text-xs text-muted"><span className="num mono text-ink">{c.tokens.toLocaleString()}</span> tokens{c.from_cache ? " (from the lab cache)" : ""}</p>}
            <ol className="m-0 mb-2 list-none space-y-1 p-0">
              {CHECKS.map((k) => {
                const x = c.checks.find((y) => y.name === k.name);
                if (!x && c.id === "push") return null;
                return <li key={k.name} className="flex gap-1.5 text-xs" title={x?.evidence}><StatusIcon tone={CHECK_TONE(x)} className="mt-[2px]" /><span className="ui">{k.label}</span></li>;
              })}
            </ol>
            <p className={`ui m-0 mb-2 flex items-center gap-1.5 text-sm font-semibold ${c.accepted ? "text-green" : c.accepted === false ? "text-red" : "text-muted"}`}>
              <Icon name={c.accepted ? "check" : c.accepted === false ? "cross" : "minus"} />{c.note}
            </p>
            {c.diff ? <UnifiedDiff diff={c.diff} /> : <p className="ui m-0 text-xs text-muted">no applicable patch</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

/** The arena tab: the table, the chart, the generated takeaway, and the repair arena when it ran. */
export function ArenaPanel({ s }: { s: LabState }) {
  const a = arenaOf(s);
  const cov = [...s.events].reverse().find((e) => e.type === "arena.coverage");
  if (!a) {
    if (cov?.status === "running") return <p className="ui m-0 flex items-center gap-2 text-sm text-blue"><span className="br-pulse inline-block h-2 w-2 rounded-full bg-blue" />Recording per-test coverage at the base commit (one-time cost per repository and commit)…</p>;
    return <Empty title="Six test-selection strategies are compared here once the full suite has run.">Retest-all, static reachability, per-test coverage, failure history, co-change and BlastRadius, each scored on this run&apos;s measured results: tests run, failures caught, first failure and CI time.</Empty>;
  }
  return (
    <div className="space-y-5">
      <p className="ui m-0 rounded border border-rule bg-page px-3 py-2 text-base"><span className="font-semibold">Takeaway.</span> {a.takeaway}</p>
      <ArenaTable a={a} />
      <div className="max-w-3xl"><ArenaChart a={a} /></div>
      <dl className="ui m-0 grid gap-3 text-xs sm:grid-cols-3">
        <div><dt className="text-muted">Per-test coverage (one-time cost)</dt><dd className="m-0">{a.coverage.status === "ok" ? <><span className="num mono">{a.coverage.wall_s?.toFixed(1)} s</span> for {a.coverage.n_tests} tests at the base commit{a.coverage.cached ? ", read from the cache this run" : ", recorded this run"}</> : a.coverage.reason}</dd></div>
        <div><dt className="text-muted">Failure history</dt><dd className="m-0">{a.history.n_runs === null ? "not known for this recording" : <>history: {a.history.n_runs} earlier lab run{a.history.n_runs === 1 ? "" : "s"} of this repository on this machine{a.history.n_runs === 0 ? " (cold start)" : ""}</>}</dd></div>
        <div><dt className="text-muted">Co-change</dt><dd className="m-0">{a.cochange.reason ?? `${a.cochange.n_commits} commits of git history before the base${a.cochange.upstream?.status === "fetched" ? `, fetched from upstream in ${a.cochange.upstream.fetch_s.toFixed(1)} s` : a.cochange.upstream?.status === "cached" ? ", from the upstream cache" : ""}`}</dd></div>
      </dl>
      <RepairArena s={s} />
    </div>
  );
}
