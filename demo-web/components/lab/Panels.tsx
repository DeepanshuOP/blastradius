"use client";

import { useMemo, useState } from "react";
import { Empty, Icon, Id, OUTCOME_COLOR, SEG, StageError, StatusIcon, fmtMs, midEllipsis, type Tone } from "./common";
import { SideBySide, UnifiedDiff } from "./Diff";
import type { Check, LabEvent, LabState, Lane } from "./types";

/** The failure event of a stage, if it failed (its reason, from the event itself). */
export function stageFailure(s: LabState, stage: string): LabEvent | undefined {
  return s.stage[stage]?.status === "failed" ? [...s.events].reverse().find((e) => e.stage === stage && e.status === "failed") : undefined;
}

const NEXT: Record<string, string> = {
  graph: "the impact ranking still runs from the diff; check that the repository parses (the reason above names the file) or pick a prepared repository.",
  impact: "the suite still runs in collection order; read the reason, then retry or pick a prepared repository.",
  tests: "check the reason (a timeout or a missing interpreter); prepared repositories run with their own virtualenv.",
  repair: "switch to a recorded run for this step, or retry after the quota window named above.",
  validate: "open the Repair tab: the check that failed names the evidence.",
};

/** Impact: the E1 ranking with each file's score, its top three reasons and its graph path. */
export function ImpactPanel({ s }: { s: LabState }) {
  const r = s.impact.ranking;
  const paths = s.impact.paths;
  const fail = stageFailure(s, "impact");
  if (fail) return <StageError what="The impact ranking failed." reason={String(fail.data.reason ?? "no reason recorded")} next={NEXT.impact} />;
  if (!r) return <Empty title="The ranked test files appear here once the change is committed.">The E1 ranker scores every test file against the diff; each row shows its score, its top three reasons and the shortest graph path from the change.</Empty>;
  const pathOf = (f: string) => (paths?.paths as { test_file: string; path: string[]; length: number | null }[] | undefined)?.find((x) => x.test_file === f);
  return (
    <>
      <p className="ui m-0 mb-3 text-sm text-muted">
        Ranker <span className="mono text-ink">{r.ranker}</span> over <span className="num">{r.n_test_files}</span> test files for <span className="num">{r.changed_files.length}</span> changed file(s), <span className="num">{r.changed_lines}</span> changed lines.
        {paths ? <> <span className="num">{paths.reachability.n_reachable}</span> of <span className="num">{paths.reachability.n_nodes}</span> graph nodes lie within {paths.reachability.limit} hops of a changed node.</> : null}
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="ui text-left text-2xs uppercase tracking-wide text-muted"><th className="py-1 pr-3 font-medium">#</th><th className="pr-3 font-medium">Test file</th><th className="pr-3 text-right font-medium">Score</th><th className="pr-3 font-medium">Top reasons</th><th className="font-medium">Graph path</th></tr></thead>
          <tbody>
            {(r.rows as { test: string; score: number; reasons: string[] }[]).slice(0, 10).map((row, i) => {
              const p = pathOf(row.test);
              const atRisk = (r.at_risk_files as string[] | undefined)?.includes(row.test);
              return (
                <tr key={row.test} className="border-t border-rule align-top">
                  <td className="num py-1.5 pr-3 text-muted">{i + 1}</td>
                  <td className="pr-3"><Id id={row.test} n={48} />{atRisk && <span className="ui ml-1.5 rounded bg-accent/15 px-1 text-2xs font-semibold text-accent">at risk</span>}</td>
                  <td className="num mono pr-3 text-right">{row.score.toFixed(2)}</td>
                  <td className="pr-3">{row.reasons.map((x) => <div key={x} className="mono text-xs text-muted">{x}</div>)}</td>
                  <td className="ui text-xs text-muted">{p ? (p.length === null ? "no path in the graph" : `${p.length} hop${p.length === 1 ? "" : "s"}: ${p.path.map((n) => n.split("_").slice(-2).join("_")).join(" → ")}`) : "–"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}

function LaneRow({ lane, total, failed }: { lane: Lane; total: number; failed: number }) {
  const ff = lane.first_failure_position;
  const pos = ff ? Math.min(Math.max(((ff - 0.5) / Math.max(total, 1)) * 100, 0), 100) : 0;
  return (
    <div className="mb-4">
      <div className="ui mb-1 flex flex-wrap items-baseline justify-between gap-2 text-sm">
        <span className="font-semibold">{lane.label}</span>
        <span className="text-muted">
          {ff ? <>first failure at <span className="num mono text-ink">{ff}</span> of <span className="num">{total}</span> · <span className="num mono text-ink">{fmtMs(lane.elapsed_to_first_failure_ms)}</span> {lane.name === "alphabetical" ? "(computed)" : "(measured durations, summed)"}</> : "no failure"}
        </span>
      </div>
      <div className="relative flex h-7 w-full items-end gap-px overflow-hidden rounded-sm bg-page" role="img" aria-label={`${lane.label}: ${total} tests, ${failed} failed${ff ? `, first failure at position ${ff}` : ""}`}>
        {lane.ticks.map((t) => {
          const bad = t.outcome === "failed" || t.outcome === "error";
          return <span key={t.i} title={`${t.i}. ${t.id} ${t.outcome} ${fmtMs(t.ms)}`} className={`min-w-px flex-1 ${OUTCOME_COLOR[t.outcome] ?? "bg-muted"} ${bad ? "h-full" : "h-1/2 opacity-80"}`} />;
        })}
        {ff && <span className="absolute inset-y-0 w-0.5 bg-ink" style={{ left: `${pos}%` }} />}
      </div>
      {ff && <div className="relative h-5"><span className="ui absolute flex -translate-x-1/2 items-center gap-1 whitespace-nowrap text-2xs text-ink" style={{ left: `${Math.min(Math.max(pos, 7), 93)}%` }}><Icon name="target" />first failure</span></div>}
      <p className="cap m-0 text-xs">{lane.basis}</p>
    </div>
  );
}

/** Test race: two lanes over the same measured results. */
export function RacePanel({ s }: { s: LabState }) {
  const race = s.tests.race;
  const n = s.tests.results.length;
  const done = s.tests.done;
  const failedN = s.tests.results.filter((t) => t.outcome === "failed" || t.outcome === "error").length;
  const total = (s.tests.results[s.tests.results.length - 1] as { of?: number } | undefined)?.of ?? done?.counts?.total;
  const fail = stageFailure(s, "tests");
  if (!s.tests.started && !done) return <Empty title="Two lanes race here once the suite starts.">Every tick is one test case: tall red ticks failed, short green ticks passed. The top lane is a retest-all job in alphabetical order, the bottom lane the order BlastRadius ran, at-risk files first.</Empty>;
  if (done?.reason && !n) return <Empty title="The suite was not run.">{String(done.reason)}. The graph and the impact ranking are still real.</Empty>;
  return (
    <>
      {fail && <div className="mb-3"><StageError what="The test stage failed." reason={String(fail.data.reason ?? (fail.data.timed_out ? "the suite exceeded its timeout" : "see the log"))} next={NEXT.tests} /></div>}
      <p className="ui m-0 mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
        <span><span className="num text-ink">{n}</span>{total ? <>/<span className="num">{total}</span></> : null} test cases {done ? "ran" : "so far"}{done ? <> in <span className="num">{fmtMs(done.wall_s * 1000)}</span></> : null}</span>
        <StatusIcon tone="passed" text className="text-xs" /><span className="num -ml-2 text-ink">{n - failedN}</span>
        <StatusIcon tone="failed" text className="text-xs" /><span className="num -ml-2 text-ink">{failedN}</span>
        {race && !race.order_respected && <span className="text-amber">{race.order_note}.</span>}
      </p>
      {race ? (
        <>
          <LaneRow lane={race.lanes[1]} total={n} failed={failedN} />
          <LaneRow lane={race.lanes[0]} total={n} failed={failedN} />
          <p className="cap m-0 text-xs">
            The risk-first lane is the order pytest actually ran, enforced by a plugin that sorts collected tests by their file&apos;s rank. The retest-all lane is{" "}
            <strong>computed</strong> from this run&apos;s measured per-test durations in alphabetical id order; it was not run separately. {race.unit}.
            {race.lanes[0].measured_wall_to_first_failure_ms !== undefined && <> Measured wall time from suite start to the first failure in the real run, including pytest start-up: <span className="num">{fmtMs(race.lanes[0].measured_wall_to_first_failure_ms)}</span>.</>}
          </p>
        </>
      ) : (
        <div className="flex h-7 w-full items-end gap-px overflow-hidden rounded-sm bg-page" role="img" aria-label={`${n} tests so far, ${failedN} failed`}>
          {s.tests.results.map((t) => <span key={t.index} className={`min-w-px flex-1 ${OUTCOME_COLOR[t.outcome] ?? "bg-muted"} ${t.outcome === "failed" || t.outcome === "error" ? "h-full" : "h-1/2"}`} />)}
        </div>
      )}
    </>
  );
}

const COLS = [
  { k: "mine" as const, title: "Mine", what: "passed on the base, fails on the head: this change broke it", icon: "bolt" as const, tone: "text-accent" },
  { k: "inherited" as const, title: "Inherited", what: "already failing on the base commit: not this change", icon: "minus" as const, tone: "text-blue" },
  { k: "flaky" as const, title: "Flaky", what: "the triage model says it fails without a code reason", icon: "warn" as const, tone: "text-amber" },
];

/** Triage board: mine, inherited, flaky. */
export function TriagePanel({ s }: { s: LabState }) {
  const t = s.triage;
  const [open, setOpen] = useState<string | null>(null);
  if (!t) return <Empty title="Failing tests are sorted into mine, inherited and flaky once the suite finishes.">Each failing test is re-run on the base commit: a test that also fails there is inherited, not this change&apos;s fault.</Empty>;
  if (t.skipped) return <Empty title="Nothing to triage.">{t.skipped}.</Empty>;
  return (
    <>
      <p className="ui m-0 mb-3 text-sm text-muted">
        Each failing test was re-run on the base commit. Unit: {t.unit ?? "unique test ids"}; <span className="num">{t.rows.length}</span> failing ids from <span className="num">{t.failing_cases ?? "?"}</span> failing cases. Model: <span className="mono">{t.model}</span>.
      </p>
      <div className="grid gap-3 md:grid-cols-3">
        {COLS.map((c) => {
          const rows = t.rows.filter((r) => r.class === c.k);
          return (
            <div key={c.k} className="rounded-md border border-rule bg-page p-2">
              <div className="ui mb-1 flex items-baseline justify-between"><span className={`flex items-center gap-1.5 text-sm font-semibold ${c.tone}`}><Icon name={c.icon} />{c.title}</span><span className="num mono text-sm">{rows.length}</span></div>
              <p className="ui m-0 mb-2 text-xs text-muted">{c.what}</p>
              <div className="max-h-72 space-y-1.5 overflow-y-auto pr-1">
                {rows.length === 0 && <p className="ui m-0 text-xs text-muted">none</p>}
                {rows.slice(0, 60).map((r) => (
                  <button key={r.test} type="button" onClick={() => setOpen(open === r.test ? null : r.test)} aria-expanded={open === r.test}
                    className="block w-full rounded border border-rule bg-panel px-2 py-1.5 text-left hover:border-muted">
                    <Id id={r.test} n={44} className="block text-xs" />
                    <span className="ui mt-0.5 flex flex-wrap items-center gap-x-2 text-xs text-muted">
                      <span className="flex items-center gap-1">base <StatusIcon tone={(r.base_outcome === "passed" || r.base_outcome === "absent" ? "passed" : "failed") as Tone} text /></span>
                      <span className="flex items-center gap-1">head <StatusIcon tone="failed" text /></span>
                      <span>confidence <span className="num mono text-ink">{r.confidence.toFixed(2)}</span></span>
                    </span>
                    {open === r.test && <span className="ui mt-1 block text-xs text-muted">{r.reason}{r.message ? ` · ${midEllipsis(r.message, 140)}` : ""}</span>}
                  </button>
                ))}
                {rows.length > 60 && <p className="ui m-0 text-xs text-muted">{rows.length - 60} more not shown</p>}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

export const CHECKS: { name: string; label: string }[] = [
  { name: "applies", label: "The patch applies cleanly" },
  { name: "syntax", label: "Python syntax compiles" },
  { name: "targeted", label: "The previously failing tests pass" },
  { name: "full", label: "The full suite passes" },
  { name: "scope", label: "No edits outside the changed or allowed files" },
];

export function checkTone(x: Check | undefined): Tone {
  return !x ? "pending" : x.status === "running" ? "running" : x.status === "skipped" ? "skipped" : x.ok ? "ok" : "failed";
}

export function CheckList({ checks, attempt, large = false }: { checks: Check[]; attempt: number; large?: boolean }) {
  return (
    <ol className="m-0 list-none space-y-1.5 p-0">
      {CHECKS.map((c) => {
        const x = checks.find((k) => k.attempt === attempt && k.name === c.name);
        const st = checkTone(x);
        return (
          <li key={c.name} className="flex gap-2">
            <span className={large ? "mt-0.5 text-2xl leading-none" : "mt-[3px]"}><StatusIcon tone={st} /></span>
            <span className={`ui min-w-0 ${large ? "text-xl" : "text-sm"}`}><span className={st === "pending" ? "text-muted" : ""}>{c.label}</span>
              {x && !large && <span className="mono block text-xs text-muted [overflow-wrap:anywhere]">{x.evidence}</span>}
            </span>
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
    <>
      <p className="ui m-0 mb-3 text-sm text-muted"><span className="num mono text-ink">{s.tokens.total.toLocaleString()}</span> tokens{s.tokens.cached ? <> (<span className="num">{s.tokens.cached.toLocaleString()}</span> answered from the cache)</> : ""}.</p>
      {r.unavailable && (
        <div className="mb-3"><StageError what={`The model is unavailable (${r.unavailable.kind}).`} reason={r.unavailable.reason} next={NEXT.repair} /></div>
      )}
      {r.skipped && !r.requests.length && <Empty title="Repair did not run.">{r.skipped}.</Empty>}
      {!r.skipped && !r.chunks.length && !r.unavailable && <Empty title="A patch is generated here when a failure is triaged mine.">The model sees at most three functions, chosen from the diff and the failure output; a patch counts only after the five checks below pass, the full suite among them.</Empty>}
      {r.chunks.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="min-w-0">
            <h4 className="ui m-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted">Context shown to the model</h4>
            <ul className="m-0 list-none space-y-1 p-0">
              {r.chunks.map((c) => (
                <li key={`${c.file}:${c.qualname}`} className="rounded border border-rule bg-page px-2 py-1">
                  <Id id={`${c.file}::${c.qualname}`} n={52} className="text-xs" />
                  <span className="num mono text-xs text-muted"> L{c.start}-{c.end}</span>
                  <span className="ui block text-xs text-muted">{c.why}</span>
                </li>
              ))}
            </ul>
            {r.requests.map((q) => {
              const rep = r.replies.find((x) => x.attempt === q.attempt);
              return (
                <p key={q.attempt} className="ui m-0 mt-2 text-sm text-muted">
                  Attempt {q.attempt}: <span className="mono text-ink">{q.model}</span>, about <span className="num mono text-ink">{q.prompt_tokens_estimate}</span> prompt tokens (estimate), temperature {q.params?.temperature ?? 0}{q.cached ? ", answered from the lab cache" : ""}.
                  {rep?.usage && <> Used <span className="num mono text-ink">{rep.usage.total_tokens}</span> tokens.</>}
                </p>
              );
            })}
            {r.replies.length > 0 && (
              <div className="mt-2">
                <button type="button" onClick={() => setShowReply(!showReply)} className="ui text-sm text-blue underline" aria-expanded={showReply}>{showReply ? "Hide" : "Show"} the model&apos;s reply</button>
                {showReply && r.replies.map((x) => <pre key={x.attempt} className="mono mt-1 max-h-64 overflow-auto whitespace-pre-wrap rounded bg-page p-2 text-xs">{x.text}</pre>)}
              </div>
            )}
          </div>
          <div className="min-w-0">
            <h4 className="ui m-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted">Validation{attempts.length > 1 ? ` (attempt ${lastAttempt} of ${attempts.length})` : ""}</h4>
            <CheckList checks={s.validate.checks} attempt={lastAttempt} />
            <div className={`ui mt-3 flex items-center gap-2 rounded border px-3 py-2 text-sm font-semibold ${accepted ? "border-green text-green" : v ? "border-red text-red" : "border-rule text-muted"}`} role="status">
              {accepted ? <><Icon name="check" />Accepted: the full suite passed with this patch.</> : v ? (v.status === "skipped" ? `Not validated: ${v.reason}` : <><Icon name="cross" />Rejected: {v.note}</>) : s.running ? "Not accepted yet. A patch is accepted only after the full suite passes." : "No patch was accepted."}
            </div>
          </div>
        </div>
      )}
      {r.patch && r.patch.files?.length > 0 && (
        <div className="mt-4">
          <div className="mb-2 flex items-center gap-2">
            <h4 className="ui m-0 text-xs font-semibold uppercase tracking-wide text-muted">The patch</h4>
            <button type="button" onClick={() => setView("side")} aria-pressed={view === "side"} className={SEG(view === "side")}>side by side</button>
            <button type="button" onClick={() => setView("unified")} aria-pressed={view === "unified"} className={SEG(view === "unified")}>unified</button>
            {!accepted && <span className="ui text-xs text-amber">not accepted</span>}
          </div>
          {view === "unified" ? <UnifiedDiff diff={r.patch.diff} /> : (r.patch.files as { path: string; before: string; after: string }[]).map((f) => <SideBySide key={f.path} path={f.path} before={f.before} after={f.after} />)}
        </div>
      )}
    </>
  );
}
