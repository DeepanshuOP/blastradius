"use client";

import { useMemo, useState } from "react";
import { Counter, Explain, Info } from "./Info";
import { Drawer, Empty, Icon, Id, OUTCOME_COLOR, SEG, StageError, StatusIcon, fmtMs, midEllipsis, uniqueSuffixes, type Tone } from "./common";
import { SideBySide, UnifiedDiff } from "./Diff";
import type { Check, LabEvent, LabState, Lane } from "./types";

/** The failure event of a stage, if it failed (its reason, from the event itself). */
export function stageFailure(s: LabState, stage: string): LabEvent | undefined {
  return s.stage[stage]?.status === "failed" ? [...s.events].reverse().find((e) => e.stage === stage && e.status === "failed") : undefined;
}

export const NEXT: Record<string, string> = {
  graph: "the impact ranking still runs from the diff; check that the repository parses (the reason above names the file) or pick a prepared repository.",
  impact: "the suite still runs in collection order; read the reason, then retry or pick a prepared repository.",
  tests: "check the reason (a timeout or a missing interpreter); prepared repositories run with their own virtualenv.",
  repair: "switch to a recorded run for this step, or retry after the quota window named above.",
  validate: "open the Repair tab: the check that failed names the evidence.",
};

const Chip = ({ children, title, tone = "" }: { children: React.ReactNode; title?: string; tone?: string }) => (
  <span title={title} className={`ui inline-flex items-center gap-1 rounded-full border border-rule px-2 py-0.5 text-xs ${tone || "text-muted"}`}>{children}</span>
);

/** Impact: the E1 ranking with each file's score, its top reasons and its graph path. */
export function ImpactPanel({ s }: { s: LabState }) {
  const r = s.impact.ranking;
  const paths = s.impact.paths;
  const fail = stageFailure(s, "impact");
  if (fail) return <StageError what="The impact ranking failed." reason={String(fail.data.reason ?? "no reason recorded")} next={NEXT.impact} />;
  if (!r) return <Empty title="Ranked test files appear once the change is committed." />;
  const pathOf = (f: string) => (paths?.paths as { test_file: string; path: string[]; length: number | null }[] | undefined)?.find((x) => x.test_file === f);
  const rows = (r.rows as { test: string; score: number; reasons: string[] }[]).slice(0, 8);
  const max = Math.max(...rows.map((x) => x.score)), min = Math.min(...rows.map((x) => x.score));
  const span = Math.max(max - min, 1e-6);
  return (
    <>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <Chip tone="text-ink"><span className="mono">{r.ranker}</span></Chip>
        <Chip><span className="num">{r.n_test_files}</span> test files</Chip>
        <Chip><span className="num">{r.changed_files.length}</span> changed file(s) · <span className="num">{r.changed_lines}</span> lines</Chip>
        {paths && <Chip><span className="num">{paths.reachability.n_reachable}</span> of <span className="num">{paths.reachability.n_nodes}</span> nodes within {paths.reachability.limit} hops</Chip>}
        <Info label="About the ranking">
          <span className="block">The E1 ranker scores every test file against the diff. Each row shows the score, the strongest reasons and the shortest graph path from the change.</span>
        </Info>
      </div>
      <div className="relative overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="ui text-left text-2xs uppercase tracking-wide text-muted"><th className="py-1 pr-3 font-medium">#</th><th className="pr-3 font-medium">Test file</th><th className="pr-3 font-medium">Score</th><th className="pr-3 font-medium">Top reasons</th><th className="font-medium">Graph path</th></tr></thead>
          <tbody>
            {rows.map((row, i) => {
              const p = pathOf(row.test);
              const atRisk = (r.at_risk_files as string[] | undefined)?.includes(row.test);
              return (
                <tr key={row.test} className="border-t border-rule align-top">
                  <td className="num py-1.5 pr-3 text-muted">{i + 1}</td>
                  <td className="pr-3"><Id id={row.test} n={44} />{atRisk && <span className="ui ml-1.5 rounded bg-accent/15 px-1 text-2xs font-semibold text-accent">at risk</span>}</td>
                  <td className="pr-3">
                    <span className="flex items-center gap-2"><span className="inline-block h-1.5 rounded-r bg-accent" style={{ width: `${12 + 60 * ((row.score - min) / span)}px` }} /><span className="num mono text-xs">{row.score.toFixed(2)}</span></span>
                  </td>
                  <td className="pr-3">{row.reasons.slice(0, 2).map((x) => <div key={x} className="mono text-xs text-muted">{x}</div>)}</td>
                  <td className="ui text-xs text-muted">{p ? (p.length === null ? "no path" : `${p.length} hop${p.length === 1 ? "" : "s"}`) : "–"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}

const OUTCOME_TICK = (o: string) => (o === "failed" || o === "error" ? "h-full" : "h-1/2 opacity-80");

function LaneRow({ lane, total, failed }: { lane: Lane; total: number; failed: number }) {
  const ff = lane.first_failure_position;
  const pos = ff ? Math.min(Math.max(((ff - 0.5) / Math.max(total, 1)) * 100, 0), 100) : 0;
  return (
    <div className="mb-4">
      <div className="ui mb-1 flex flex-wrap items-baseline justify-between gap-2 text-sm">
        <span className="flex items-center gap-1.5 font-semibold">{lane.label}<Info label={`About ${lane.label}`}><span className="block">{lane.basis}.</span></Info></span>
        <span className="text-muted">
          {ff ? <>first failure at <span className="num mono text-ink">{ff}</span> of <span className="num">{total}</span> · <span className="num mono text-ink">{fmtMs(lane.elapsed_to_first_failure_ms)}</span></> : "no failure"}
        </span>
      </div>
      <div className="relative flex h-7 w-full items-end gap-px overflow-hidden rounded-sm bg-page" role="img" aria-label={`${lane.label}: ${total} tests, ${failed} failed${ff ? `, first failure at position ${ff}` : ""}`}>
        {lane.ticks.map((t, k) => (
          <span key={`${t.i}-${k}`} title={`${k + 1}. ${t.id} ${t.outcome} ${fmtMs(t.ms)}`} className={`min-w-px flex-1 ${OUTCOME_COLOR[t.outcome] ?? "bg-muted"} ${OUTCOME_TICK(t.outcome)}`} />
        ))}
        {ff && <span className="absolute inset-y-0 w-0.5 bg-ink" style={{ left: `${pos}%` }} />}
      </div>
      {ff && <div className="relative h-5"><span className="ui absolute flex -translate-x-1/2 items-center gap-1 whitespace-nowrap text-2xs text-ink" style={{ left: `${Math.min(Math.max(pos, 7), 93)}%` }}><Icon name="target" />first failure</span></div>}
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
  if (!s.tests.started && !done) return <Empty title="Two lanes race here once the suite starts." />;
  if (done?.reason && !n) return <Empty title="The suite was not run.">{String(done.reason)}</Empty>;
  const rule = race?.order_rule;
  return (
    <>
      {fail && <div className="mb-3"><StageError what="The test stage failed." reason={String(fail.data.reason ?? (fail.data.timed_out ? "the suite exceeded its timeout" : "see the log"))} next={NEXT.tests} /></div>}
      <p className="ui m-0 mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
        <span><Counter value={n} className="text-ink" />{total ? <>/<span className="num">{total}</span></> : null} test cases {done ? "ran" : "so far"}{done ? <> in <span className="num">{fmtMs(done.wall_s * 1000)}</span></> : null}</span>
        <StatusIcon tone="passed" text className="text-xs" /><span className="num -ml-2 text-ink">{n - failedN}</span>
        <StatusIcon tone="failed" text className="text-xs" /><span className="num -ml-2 text-ink">{failedN}</span>
        {race && race.order_respected === false && <span className="text-amber">{race.order_note}.</span>}
        {rule?.before && <Chip title={rule.before.basis}>before the tie-break rule: first failure at <span className="num mono text-ink">{rule.before.first_failure_position ?? "–"}</span>{rule.before.first_failure_ms != null && <> · <span className="num mono text-ink">{fmtMs(rule.before.first_failure_ms)}</span></>}</Chip>}
        {rule && <Info label="About the order rule">
          <span className="block">{rule.text}</span>
          <span className="mt-1 block">{rule.source === "derived" ? "This recording ran before the rule existed: the top lane is computed from its stored results." : "Pytest ran the cases in this order."}</span>
        </Info>}
      </p>
      {race ? (
        <>
          <LaneRow lane={race.lanes[1]} total={n} failed={failedN} />
          <LaneRow lane={race.lanes[0]} total={n} failed={failedN} />
          <Explain>
            Retest-all is <strong>computed</strong> from this run&apos;s measured per-test durations in alphabetical id order; it was not run separately. {race.unit}.
            {race.lanes[0].measured_wall_to_first_failure_ms !== undefined && <> Measured wall time to the first failure in the real run, pytest start-up included: <span className="num">{fmtMs(race.lanes[0].measured_wall_to_first_failure_ms)}</span>.</>}
          </Explain>
        </>
      ) : (
        <div className="flex h-7 w-full items-end gap-px overflow-hidden rounded-sm bg-page" role="img" aria-label={`${n} tests so far, ${failedN} failed`}>
          {s.tests.results.map((t) => <span key={t.index} className={`min-w-px flex-1 ${OUTCOME_COLOR[t.outcome] ?? "bg-muted"} ${OUTCOME_TICK(t.outcome)}`} />)}
        </div>
      )}
    </>
  );
}

const COLS = [
  { k: "mine" as const, title: "Mine", what: "this change broke it", icon: "bolt" as const, tone: "text-accent", ring: "border-accent/60" },
  { k: "inherited" as const, title: "Inherited", what: "already failing before", icon: "minus" as const, tone: "text-blue", ring: "border-blue/50" },
  { k: "flaky" as const, title: "Flaky", what: "no code reason", icon: "warn" as const, tone: "text-amber", ring: "border-amber/50" },
];

/** Triage: three large counters with compact chips; the whole list is in a drawer. */
export function TriagePanel({ s }: { s: LabState }) {
  const t = s.triage;
  const [drawer, setDrawer] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  if (!t) return <Empty title="Failures are sorted into mine, inherited and flaky once the suite ends." />;
  if (t.skipped) return <Empty title="Nothing to triage.">{t.skipped}</Empty>;
  const names = uniqueSuffixes(t.rows.map((r) => r.test));
  return (
    <>
      <div className="grid gap-3 md:grid-cols-3">
        {COLS.map((c) => {
          const rows = t.rows.filter((r) => r.class === c.k);
          return (
            <div key={c.k} className={`rounded-md border bg-page p-3 ${rows.length ? c.ring : "border-rule"}`}>
              <div className={`ui flex items-center gap-1.5 text-sm font-semibold ${c.tone}`}><Icon name={c.icon} />{c.title}</div>
              <Counter value={rows.length} className="block text-3xl font-semibold leading-tight text-ink" />
              <p className="ui m-0 text-xs text-muted">{c.what}</p>
              <ul className="m-0 mt-2 flex list-none flex-wrap gap-1 p-0">
                {rows.slice(0, 4).map((r) => <li key={r.test}><span className="mono block max-w-[15rem] truncate rounded border border-rule bg-panel px-1.5 py-0.5 text-2xs" title={r.test}>{names.get(r.test)}</span></li>)}
                {rows.length > 4 && <li><span className="ui block rounded px-1 py-0.5 text-2xs text-muted">+{rows.length - 4}</span></li>}
                {rows.length === 0 && <li className="ui text-2xs text-muted">none</li>}
              </ul>
            </div>
          );
        })}
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button type="button" onClick={() => setDrawer(true)} disabled={t.rows.length === 0} className="ui rounded border border-rule px-2.5 py-1 text-sm hover:border-muted disabled:opacity-40" aria-haspopup="dialog">Full list ({t.rows.length})</button>
        <span className="ui text-xs text-muted"><span className="num">{t.failing_cases ?? "?"}</span> failing cases · {t.unit ?? "unique test ids"}</span>
        <Info label="About triage"><span className="block">Each failing test was re-run on the base commit; a test that also fails there is inherited, not this change&apos;s fault. Model: <span className="mono">{t.model ?? "n/a"}</span>.</span></Info>
      </div>
      {drawer && (
        <Drawer side="right" title="Triage: every failing test" onClose={() => setDrawer(false)}>
          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-3">
            {COLS.map((c) => {
              const rows = t.rows.filter((r) => r.class === c.k);
              if (!rows.length) return null;
              return (
                <section key={c.k}>
                  <h4 className={`ui m-0 mb-1 flex items-center gap-1.5 text-sm font-semibold ${c.tone}`}><Icon name={c.icon} />{c.title} <span className="num text-muted">{rows.length}</span></h4>
                  <ul className="m-0 list-none space-y-1.5 p-0">
                    {rows.map((r) => (
                      <li key={r.test}>
                        <button type="button" onClick={() => setOpen(open === r.test ? null : r.test)} aria-expanded={open === r.test} className="block w-full rounded border border-rule bg-page px-2 py-1.5 text-left hover:border-muted">
                          <Id id={r.test} label={names.get(r.test)} className="block text-xs" />
                          <span className="ui mt-0.5 flex flex-wrap items-center gap-x-2 text-xs text-muted">
                            <span className="flex items-center gap-1">base <StatusIcon tone={(r.base_outcome === "passed" || r.base_outcome === "absent" ? "passed" : "failed") as Tone} text /></span>
                            <span className="flex items-center gap-1">head <StatusIcon tone="failed" text /></span>
                            <span>confidence <span className="num mono text-ink">{r.confidence.toFixed(2)}</span></span>
                          </span>
                          {open === r.test && <span className="ui mt-1 block text-xs text-muted">{r.reason}{r.message ? ` · ${midEllipsis(r.message, 140)}` : ""}</span>}
                        </button>
                      </li>
                    ))}
                  </ul>
                </section>
              );
            })}
          </div>
        </Drawer>
      )}
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
const CHECK_SHORT: Record<string, string> = { applies: "applies", syntax: "compiles", targeted: "failing tests pass", full: "full suite", scope: "scope" };

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

/** A check that ticks in when its event arrives: the chip is keyed by its state, so the pop plays once per change. */
export function CheckChip({ check, name }: { check: Check | undefined; name: string }) {
  const st = checkTone(check);
  const ring = st === "ok" ? "border-green text-green" : st === "failed" ? "border-red text-red" : st === "running" ? "border-blue text-blue" : "border-rule text-muted";
  return (
    <li key={`${name}-${st}`} className={`ui flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm ${ring} ${st === "ok" || st === "failed" ? "br-pop" : ""}`} title={check?.evidence}>
      <StatusIcon tone={st} />{CHECK_SHORT[name]}
    </li>
  );
}

const Step = ({ n, title, state, children }: { n: number; title: string; state: Tone; children: React.ReactNode }) => (
  <li className="min-w-0 rounded-md border border-rule bg-page p-3">
    <p className="ui m-0 mb-2 flex items-center gap-2 text-sm font-semibold"><span className="num grid h-5 w-5 place-items-center rounded-full bg-panel2 text-2xs">{n}</span>{title}<span className="ml-auto"><StatusIcon tone={state} /></span></p>
    {children}
  </li>
);

/** Repair: a horizontal flow of context, patch and the five checks. The model's reply sits behind a toggle. */
export function RepairPanel({ s }: { s: LabState }) {
  const r = s.repair;
  const [view, setView] = useState<"side" | "unified">("side");
  const [showReply, setShowReply] = useState(false);
  const attempts = useMemo(() => Array.from(new Set([...r.requests.map((x) => x.attempt as number), ...s.validate.checks.map((c) => c.attempt)])).sort(), [r.requests, s.validate.checks]);
  const lastAttempt = attempts[attempts.length - 1] ?? 1;
  const v = s.validate.verdict;
  const accepted = v?.accepted === true && v.status === "ok";
  if (r.unavailable) return <StageError what={`The model is unavailable (${r.unavailable.kind}).`} reason={r.unavailable.reason} next={NEXT.repair} />;
  if (r.skipped && !r.requests.length) return <Empty title="Repair did not run.">{r.skipped}</Empty>;
  if (!r.chunks.length) return <Empty title="A patch is generated here when a failure is triaged mine." />;
  const files = (r.patch?.files ?? []) as { path: string; before: string; after: string }[];
  const checks = s.validate.checks.filter((c) => c.attempt === lastAttempt);
  const done = checks.filter((c) => c.status !== "running").length;
  return (
    <>
      <ol className="m-0 grid list-none gap-3 p-0 lg:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)_auto_minmax(0,1.1fr)]">
        <Step n={1} title="Context" state={r.chunks.length ? "ok" : "pending"}>
          <ul className="m-0 flex list-none flex-wrap gap-1 p-0">
            {r.chunks.map((c) => <li key={`${c.file}:${c.qualname}`} title={`${c.file}::${c.qualname} L${c.start}-${c.end}: ${c.why}`}><span className="mono block max-w-[12rem] truncate rounded border border-rule bg-panel px-1.5 py-0.5 text-xs">{c.qualname}</span></li>)}
          </ul>
          <p className="ui m-0 mt-2 text-xs text-muted"><Counter value={s.tokens.total} className="text-ink" /> tokens{s.tokens.cached ? ` · ${s.tokens.cached.toLocaleString()} cached` : ""}</p>
        </Step>
        <li className="hidden items-center text-muted lg:flex" aria-hidden="true"><Icon name="chevron" className="text-xl" /></li>
        <Step n={2} title="Patch" state={r.patch ? "ok" : s.running ? "running" : "pending"}>
          {files.length ? <p className="ui m-0 text-sm">{files.map((f) => <span key={f.path} className="mono block truncate" title={f.path}>{f.path.split("/").slice(-1)[0]}</span>)}</p> : <p className="ui m-0 text-xs text-muted">{s.running ? "waiting for the model" : "no applicable patch"}</p>}
          {r.replies.length > 0 && (
            <button type="button" onClick={() => setShowReply(!showReply)} className="ui mt-2 text-xs text-blue underline" aria-expanded={showReply}>{showReply ? "Hide" : "Show"} the model&apos;s reply</button>
          )}
        </Step>
        <li className="hidden items-center text-muted lg:flex" aria-hidden="true"><Icon name="chevron" className="text-xl" /></li>
        <Step n={3} title="Five checks" state={accepted ? "ok" : v ? "failed" : done ? "running" : "pending"}>
          <ul className="m-0 flex list-none flex-wrap gap-1.5 p-0">
            {CHECKS.map((c) => <CheckChip key={c.name} name={c.name} check={checks.find((k) => k.name === c.name)} />)}
          </ul>
          <p className={`ui m-0 mt-2 flex items-center gap-1.5 text-sm font-semibold ${accepted ? "text-green" : v ? "text-red" : "text-muted"}`} role="status">
            {accepted ? <><Icon name="check" />Accepted</> : v ? (v.status === "skipped" ? "Not validated" : <><Icon name="cross" />Rejected</>) : s.running ? "Checking…" : "Not accepted"}
          </p>
        </Step>
      </ol>
      {showReply && r.replies.map((x) => <pre key={x.attempt} className="mono mt-3 max-h-64 overflow-auto whitespace-pre-wrap rounded bg-page p-2 text-xs">{x.text}</pre>)}
      {files.length > 0 && (
        <div className="mt-4">
          <div className="mb-2 flex items-center gap-2">
            <button type="button" onClick={() => setView("side")} aria-pressed={view === "side"} className={SEG(view === "side")}>side by side</button>
            <button type="button" onClick={() => setView("unified")} aria-pressed={view === "unified"} className={SEG(view === "unified")}>unified</button>
            {!accepted && <span className="ui text-xs text-amber">not accepted</span>}
          </div>
          {view === "unified" ? <UnifiedDiff diff={r.patch!.diff} /> : files.map((f) => <SideBySide key={f.path} path={f.path} before={f.before} after={f.after} />)}
        </div>
      )}
      <Explain>
        {r.requests.map((q) => {
          const rep = r.replies.find((x) => x.attempt === q.attempt);
          return <span key={q.attempt} className="block">Attempt {q.attempt}: <span className="mono">{q.model}</span>, about <span className="num">{q.prompt_tokens_estimate}</span> prompt tokens, temperature {q.params?.temperature ?? 0}{q.cached ? ", answered from the lab cache" : ""}{rep?.usage ? `; used ${rep.usage.total_tokens} tokens` : ""}.</span>;
        })}
      </Explain>
    </>
  );
}

/** The verdict: failing tests before the fix against after it, as two bars on one scale. */
export function VerdictPanel({ s }: { s: LabState }) {
  const c = s.tests.done?.counts as Record<string, number> | undefined;
  if (!c) return <Empty title="The verdict appears when the suite and the checks have finished." />;
  const total = Number(c.total ?? 0);
  const failed = Number(c.failed ?? 0) + Number(c.error ?? 0);
  const v = s.validate.verdict;
  const accepted = v?.accepted === true && v.status === "ok";
  const un = s.repair.unavailable;
  const Bar = ({ red, label, sub }: { red: number; label: string; sub: string }) => (
    <div>
      <div className="ui mb-1 flex items-baseline justify-between text-sm"><span className="font-semibold">{label}</span><span className="text-muted">{sub}</span></div>
      <div className="flex h-9 w-full overflow-hidden rounded bg-panel2" role="img" aria-label={`${label}: ${red} failing, ${total - red} passing of ${total}`}>
        {red > 0 && <span className="grid min-w-[2.5rem] place-items-center bg-red text-sm font-bold text-white" style={{ width: `${Math.max((red / Math.max(total, 1)) * 100, 3)}%` }}><span className="num">{red}</span></span>}
        <span className="grid flex-1 place-items-center bg-green text-sm font-bold text-white"><span className="num">{total - red}</span></span>
      </div>
    </div>
  );
  if (failed === 0) {
    return <div className="space-y-2"><Bar red={0} label="No failing tests" sub={`${total} passing`} /><p className="ui m-0 text-sm text-muted">Nothing to repair.</p></div>;
  }
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-baseline gap-x-3">
        <span className="num mono text-3xl font-semibold text-red">{failed} red</span>
        {accepted ? <><Icon name="chevron" className="text-xl text-muted" /><span className="num mono text-3xl font-semibold text-green">{total} green</span></> : <span className="ui text-sm text-muted">{un ? `no fix: model unavailable (${un.kind})` : v ? "fix not accepted" : s.running ? "checking the fix…" : "no fix accepted"}</span>}
      </div>
      <Bar red={failed} label="Before the fix" sub={`${failed} failing of ${total}`} />
      {accepted ? <Bar red={0} label="After the fix" sub={`full suite: ${total} of ${total} pass`} />
        : <div className="ui rounded border border-dashed border-rule px-3 py-2 text-sm text-muted">After the fix: {un ? "not attempted" : v ? "not accepted, so nothing is claimed" : "not decided yet"}</div>}
    </div>
  );
}
