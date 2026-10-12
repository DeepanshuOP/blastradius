"use client";

import { useMemo, useState } from "react";
import { Empty, OUTCOME_COLOR, Panel, Prov, fmtMs, short } from "./common";
import { SideBySide, UnifiedDiff } from "./Diff";
import type { Check, LabState, Lane } from "./types";

/** Impact: the E1 ranking with each file's score and its top three reasons. */
export function ImpactPanel({ s }: { s: LabState }) {
  const r = s.impact.ranking;
  const paths = s.impact.paths;
  return (
    <Panel id="panel-impact" title="Impact: which tests are most at risk" right={<Prov mode={s.mode} />}>
      {!r ? <Empty>Waiting for the change.</Empty> : (
        <>
          <p className="ui m-0 mb-2 text-[12.5px] text-muted">
            Ranker <span className="mono text-ink">{r.ranker}</span> over {r.n_test_files} test files for {r.changed_files.length} changed file(s), {r.changed_lines} changed lines.
            {paths ? <> {paths.reachability.n_reachable} of {paths.reachability.n_nodes} graph nodes lie within {paths.reachability.limit} hops of a changed node.</> : null}
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-[12.5px]">
              <thead><tr className="ui text-left text-[11px] uppercase text-muted"><th className="py-1 pr-2">#</th><th className="pr-2">Test file</th><th className="pr-2 text-right">Score</th><th className="pr-2">Top reasons</th><th>Graph path</th></tr></thead>
              <tbody>
                {(r.rows as { test: string; score: number; reasons: string[] }[]).slice(0, 10).map((row, i) => {
                  const p = (paths?.paths as { test_file: string; path: string[]; length: number | null }[] | undefined)?.find((x) => x.test_file === row.test);
                  return (
                    <tr key={row.test} className="border-t border-rule align-top">
                      <td className="py-1 pr-2 tabular-nums text-muted">{i + 1}</td>
                      <td className="mono break-all pr-2">{row.test}</td>
                      <td className="mono pr-2 text-right tabular-nums">{row.score.toFixed(2)}</td>
                      <td className="pr-2">{row.reasons.map((x) => <div key={x} className="mono text-[11.5px] text-muted">{x}</div>)}</td>
                      <td className="ui text-[12px] text-muted">{p ? (p.length === null ? "no path" : `${p.length} hop${p.length === 1 ? "" : "s"}: ${p.path.map((n) => n.split("_").slice(-2).join("_")).join(" → ")}`) : ""}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </Panel>
  );
}

function LaneRow({ lane, total, tone }: { lane: Lane; total: number; tone: string }) {
  const ff = lane.first_failure_position;
  return (
    <div className="mb-3">
      <div className="ui mb-1 flex flex-wrap items-baseline justify-between gap-2 text-[12.5px]">
        <span className="font-semibold">{lane.label}</span>
        <span className="text-muted">
          {ff ? <>first failure at position <span className="mono text-ink">{ff}</span> of {total} · <span className="mono text-ink">{fmtMs(lane.elapsed_to_first_failure_ms)}</span> {lane.name === "alphabetical" ? "(computed)" : "(summed measured durations)"}</> : "no failure"}
        </span>
      </div>
      <div className="relative flex h-6 w-full items-stretch gap-px overflow-hidden rounded-sm bg-page" role="img" aria-label={`${lane.label}: ${lane.ticks.length} tests`}>
        {lane.ticks.map((t) => (
          <span key={t.i} title={`${t.i}. ${t.id} ${t.outcome} ${fmtMs(t.ms)}`} className={`min-w-px flex-1 ${OUTCOME_COLOR[t.outcome] ?? "bg-muted"} ${tone}`} />
        ))}
        {ff && <span className="absolute inset-y-0 w-0.5 bg-accent" style={{ left: `${((ff - 0.5) / Math.max(total, 1)) * 100}%` }} />}
      </div>
      {ff && <div className="relative h-4"><span className="ui absolute -translate-x-1/2 whitespace-nowrap text-[11px] text-accent" style={{ left: `${Math.min(Math.max(((ff - 0.5) / Math.max(total, 1)) * 100, 6), 94)}%` }}>▲ first failure</span></div>}
      <p className="cap m-0 mt-1 text-[11.5px]">{lane.basis}</p>
    </div>
  );
}

/** Test race: two lanes over the same measured results. */
export function RacePanel({ s }: { s: LabState }) {
  const race = s.tests.race;
  const n = s.tests.results.length;
  const done = s.tests.done;
  const live = s.tests.results;
  return (
    <Panel id="panel-tests" title="Test race: retest-all against risk-first" right={<Prov mode={s.mode} />}>
      {!s.tests.started && !done ? <Empty>The suite has not started.</Empty> : done?.reason && !n ? <Empty>Tests were not run: {done.reason}</Empty> : (
        <>
          <p className="ui m-0 mb-3 text-[12.5px] text-muted">
            {n} test cases {done ? "ran" : "finished so far"}
            {done ? <> in {fmtMs(done.wall_s * 1000)}: {done.counts.passed} passed, {done.counts.failed} failed, {done.counts.error} errors, {done.counts.skipped} skipped.</> : "."}
            {race && !race.order_respected && <span className="text-amber"> {race.order_note}.</span>}
          </p>
          {race ? (
            <>
              <LaneRow lane={race.lanes[1]} total={n} tone="opacity-90" />
              <LaneRow lane={race.lanes[0]} total={n} tone="" />
              <p className="cap m-0 text-[12px]">
                The risk-first lane is the order pytest actually ran, enforced by a plugin that sorts collected tests by their file&apos;s rank. The retest-all lane is{" "}
                <strong>computed</strong> from this run&apos;s measured per-test durations in alphabetical id order; it was not run separately. {race.unit}.
                {race.lanes[0].measured_wall_to_first_failure_ms !== undefined && <> Measured wall time from suite start to the first failure in the real run, including pytest start-up: {fmtMs(race.lanes[0].measured_wall_to_first_failure_ms)}.</>}
              </p>
            </>
          ) : (
            <div className="flex h-6 w-full items-stretch gap-px overflow-hidden rounded-sm bg-page">
              {live.map((t) => <span key={t.index} className={`min-w-px flex-1 ${OUTCOME_COLOR[t.outcome] ?? "bg-muted"}`} />)}
            </div>
          )}
        </>
      )}
    </Panel>
  );
}

/** Triage board: mine, inherited, flaky. */
export function TriagePanel({ s }: { s: LabState }) {
  const t = s.triage;
  const [open, setOpen] = useState<string | null>(null);
  const cols: ("mine" | "inherited" | "flaky")[] = ["mine", "inherited", "flaky"];
  const tone = { mine: "border-accent", inherited: "border-blue", flaky: "border-amber" } as const;
  return (
    <Panel id="panel-triage" title="Triage: whose failure is it" right={<Prov mode={s.mode} />}>
      {!t ? <Empty>Triage runs when the suite has finished.</Empty> : t.skipped ? <Empty>{t.skipped}</Empty> : (
        <>
          <p className="ui m-0 mb-3 text-[12.5px] text-muted">
            Each failing test was re-run on the base commit. Unit: {t.unit ?? "unique test ids"}; {t.rows.length} failing ids from {t.failing_cases ?? "?"} failing cases. Model: <span className="mono">{t.model}</span>.
          </p>
          <div className="grid gap-3 md:grid-cols-3">
            {cols.map((c) => {
              const rows = t.rows.filter((r) => r.class === c);
              return (
                <div key={c} className={`rounded border-t-2 bg-page p-2 ${tone[c]}`}>
                  <div className="ui mb-2 flex items-baseline justify-between"><span className="font-semibold capitalize">{c}</span><span className="mono text-[12px] text-muted">{rows.length}</span></div>
                  <div className="max-h-72 space-y-1.5 overflow-y-auto pr-1">
                    {rows.length === 0 && <p className="ui m-0 text-[12px] text-muted">none</p>}
                    {rows.slice(0, 60).map((r) => (
                      <button key={r.test} type="button" onClick={() => setOpen(open === r.test ? null : r.test)}
                        className="block w-full rounded border border-rule bg-panel px-2 py-1.5 text-left hover:border-muted">
                        <span className="mono block break-all text-[11.5px]">{short(r.test, 96)}</span>
                        <span className="ui mt-0.5 block text-[11.5px] text-muted">
                          base <span className={r.base_outcome === "passed" || r.base_outcome === "absent" ? "text-green" : "text-red"}>{r.base_outcome}</span> · head <span className="text-red">{r.head_outcome}</span> · confidence <span className="mono text-ink">{r.confidence.toFixed(2)}</span>
                        </span>
                        {open === r.test && <span className="ui mt-1 block text-[11.5px] text-muted">{r.reason}{r.message ? ` · ${short(r.message, 140)}` : ""}</span>}
                      </button>
                    ))}
                    {rows.length > 60 && <p className="ui m-0 text-[11.5px] text-muted">{rows.length - 60} more not shown</p>}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </Panel>
  );
}

const CHECKS: { name: string; label: string }[] = [
  { name: "applies", label: "The patch applies cleanly" },
  { name: "syntax", label: "Python syntax compiles" },
  { name: "targeted", label: "The previously failing tests pass" },
  { name: "full", label: "The full suite passes" },
  { name: "scope", label: "No edits outside the changed or allowed files" },
];

function CheckList({ checks, attempt }: { checks: Check[]; attempt: number }) {
  return (
    <ol className="m-0 list-none space-y-1.5 p-0">
      {CHECKS.map((c) => {
        const x = checks.find((k) => k.attempt === attempt && k.name === c.name);
        const st = !x ? "pending" : x.status === "running" ? "running" : x.status === "skipped" ? "skipped" : x.ok ? "ok" : "failed";
        const mark = { pending: "○", running: "◐", skipped: "–", ok: "✓", failed: "✕" }[st];
        const col = { pending: "text-muted", running: "text-blue", skipped: "text-muted", ok: "text-green", failed: "text-red" }[st];
        return (
          <li key={c.name} className="flex gap-2">
            <span className={`mono w-4 shrink-0 text-center ${col} ${st === "running" ? "animate-pulse" : ""}`} aria-hidden="true">{mark}</span>
            <span className="ui min-w-0 text-[13px]"><span className={st === "pending" ? "text-muted" : ""}>{c.label}</span>
              {x && <span className="mono block break-words text-[11.5px] text-muted">{x.evidence}</span>}
            </span>
            <span className="sr-only">{st}</span>
          </li>
        );
      })}
    </ol>
  );
}

/** Repair studio: context, token count, reply, side-by-side diff, the five checks, the verdict. */
export function RepairPanel({ s }: { s: LabState }) {
  const r = s.repair;
  const [view, setView] = useState<"side" | "unified">("side");
  const [showReply, setShowReply] = useState(false);
  const attempts = useMemo(() => Array.from(new Set([...r.requests.map((x) => x.attempt as number), ...s.validate.checks.map((c) => c.attempt)])).sort(), [r.requests, s.validate.checks]);
  const lastAttempt = attempts[attempts.length - 1] ?? 1;
  const v = s.validate.verdict;
  const accepted = v?.accepted === true && v.status === "ok";
  return (
    <Panel id="panel-repair" title="Repair studio: generate a patch, then prove it" right={<><span className="mono text-[11.5px] text-muted">{s.tokens.total.toLocaleString()} tokens{s.tokens.cached ? ` (${s.tokens.cached.toLocaleString()} cached)` : ""}</span><Prov mode={s.mode} /></>}>
      {r.skipped && !r.requests.length ? <Empty>Repair skipped: {r.skipped}.</Empty> : null}
      {r.unavailable && (
        <p className="ui m-0 mb-3 rounded border border-amber p-2 text-[13px] text-amber">
          The model is unavailable ({r.unavailable.kind}): {r.unavailable.reason}. Nothing was retried. Use a recorded run to see this stage.
        </p>
      )}
      {!r.skipped && !r.chunks.length && !r.unavailable && <Empty>Repair starts when a failure is triaged mine.</Empty>}
      {r.chunks.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div>
            <h4 className="ui m-0 mb-1 text-[12px] font-semibold uppercase text-muted">Context shown to the model</h4>
            <ul className="m-0 list-none space-y-1 p-0">
              {r.chunks.map((c) => (
                <li key={`${c.file}:${c.qualname}`} className="rounded border border-rule bg-page px-2 py-1">
                  <span className="mono text-[12px]">{c.file}::{c.qualname}</span>
                  <span className="mono text-[11.5px] text-muted"> L{c.start}-{c.end}</span>
                  <span className="ui block text-[11.5px] text-muted">{c.why}</span>
                </li>
              ))}
            </ul>
            {r.requests.map((q) => (
              <p key={q.attempt} className="ui m-0 mt-2 text-[12.5px] text-muted">
                Attempt {q.attempt}: <span className="mono text-ink">{q.model}</span>, about <span className="mono text-ink">{q.prompt_tokens_estimate}</span> prompt tokens (estimate), temperature {q.params?.temperature ?? 0}{q.cached ? ", answered from the lab cache" : ""}.
                {r.replies.find((x) => x.attempt === q.attempt)?.usage && <> Used <span className="mono text-ink">{r.replies.find((x) => x.attempt === q.attempt)?.usage.total_tokens}</span> tokens.</>}
              </p>
            ))}
            {r.replies.length > 0 && (
              <div className="mt-2">
                <button type="button" onClick={() => setShowReply(!showReply)} className="ui text-[12.5px] text-blue underline" aria-expanded={showReply}>{showReply ? "Hide" : "Show"} the model&apos;s reply</button>
                {showReply && r.replies.map((x) => <pre key={x.attempt} className="mono mt-1 max-h-64 overflow-auto whitespace-pre-wrap rounded bg-page p-2 text-[11.5px]">{x.text}</pre>)}
              </div>
            )}
          </div>
          <div>
            <h4 className="ui m-0 mb-1 text-[12px] font-semibold uppercase text-muted">Validation{attempts.length > 1 ? ` (attempt ${lastAttempt} of ${attempts.length})` : ""}</h4>
            <CheckList checks={s.validate.checks} attempt={lastAttempt} />
            <div className={`ui mt-3 rounded border px-3 py-2 text-[13.5px] font-semibold ${accepted ? "border-green text-green" : v ? "border-red text-red" : "border-rule text-muted"}`} role="status">
              {accepted ? "Accepted: the full suite passed with this patch." : v ? (v.status === "skipped" ? `Not validated: ${v.reason}` : `Rejected: ${v.note}`) : s.running ? "Not accepted yet. A patch is accepted only after the full suite passes." : "No patch was accepted."}
            </div>
          </div>
        </div>
      )}
      {r.patch && r.patch.files?.length > 0 && (
        <div className="mt-4">
          <div className="mb-2 flex items-center gap-2">
            <h4 className="ui m-0 text-[12px] font-semibold uppercase text-muted">The patch</h4>
            <button type="button" onClick={() => setView("side")} aria-pressed={view === "side"} className={`ui rounded px-1.5 text-[11px] ${view === "side" ? "bg-ink text-page" : "text-muted"}`}>side by side</button>
            <button type="button" onClick={() => setView("unified")} aria-pressed={view === "unified"} className={`ui rounded px-1.5 text-[11px] ${view === "unified" ? "bg-ink text-page" : "text-muted"}`}>unified</button>
            {!accepted && <span className="ui text-[11.5px] text-amber">not accepted</span>}
          </div>
          {view === "unified" ? <UnifiedDiff diff={r.patch.diff} /> : (r.patch.files as { path: string; before: string; after: string }[]).map((f) => <SideBySide key={f.path} path={f.path} before={f.before} after={f.after} />)}
        </div>
      )}
    </Panel>
  );
}
