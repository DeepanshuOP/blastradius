"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Icon, Id, StatusIcon, fmtMs, midEllipsis } from "./common";
import { parseDiff } from "./CodePanel";
import { useEvidence } from "./EvidenceStrip";
import { GraphView } from "./GraphView";
import { CheckList } from "./Panels";
import { MarkdownLite } from "./Report";
import { ArenaTable, arenaOf } from "./Arena";
import { TestGapPanel, gapOf } from "./BreakIt";
import type { GEdge, GNode, LabState, Lane } from "./types";

type G = { nodes: GNode[]; edges: GEdge[]; changed: string[]; paths: string[][]; atRisk: string[]; outcomes: Record<string, "passed" | "failed"> };

interface Screen {
  id: string;
  title: string;
  /** The stage events this screen needs have arrived. */
  ready: (s: LabState) => boolean;
  /** Everything this screen shows has arrived (autoplay may move on). */
  done: (s: LabState) => boolean;
  /** Why the screen has nothing to show once the run is over. */
  absent?: (s: LabState) => string | null;
  caption: (s: LabState) => string;
  real: (s: LabState) => string;
  render: (s: LabState, g: G, enterKey: number) => ReactNode;
}

const mode = (s: LabState) => (s.mode === "replay" ? `REPLAY of a run recorded ${String(s.header?.date ?? "").slice(0, 10)}` : "LIVE in this session");
const failedN = (s: LabState) => s.tests.results.filter((t) => t.outcome === "failed" || t.outcome === "error").length;
const liveTests = (s: LabState) => {
  const total = (s.tests.results[s.tests.results.length - 1] as { of?: number } | undefined)?.of;
  return `tests ${s.tests.results.length}${total ? `/${total}` : ""} · ${failedN(s)} failed`;
};

/** Lines with their common leading indentation removed (a projector has no room for it). */
function dedent<T extends { text: string }>(rows: T[]): T[] {
  const ind = Math.min(...rows.filter((r) => r.text.trim()).map((r) => r.text.length - r.text.trimStart().length));
  return Number.isFinite(ind) && ind > 0 ? rows.map((r) => ({ ...r, text: r.text.slice(ind) })) : rows;
}

/** The changed function's hunks, large. */
function BigDiff({ s }: { s: LabState }) {
  const files = parseDiff(String(s.change?.diff ?? ""));
  const fns = (s.change?.changed_functions ?? []) as { file: string; function: string }[];
  const f = files.find((x) => fns.some((c) => c.file === x.path && c.function !== "<module>")) ?? files[0];
  if (!f) return <p className="ui text-xl text-muted">The change produced no diff.</p>;
  const rows = f.lines.filter((l) => l.kind !== "hunk");
  const firstChange = Math.max(0, rows.findIndex((l) => l.kind !== "ctx"));
  const view = dedent(rows.slice(Math.max(0, firstChange - 4), firstChange + 10));
  return (
    <div className="min-w-0">
      <p className="mono m-0 mb-3 text-lg text-muted">{f.path}{files.length > 1 ? `  (+${files.length - 1} more file${files.length > 2 ? "s" : ""})` : ""}</p>
      <div className="mono overflow-hidden rounded-md border border-rule bg-page py-2 text-md leading-[28px]">
        {view.map((l, i) => (
          <div key={i} className={`flex whitespace-pre ${l.kind === "add" ? "bg-green/20" : l.kind === "del" ? "bg-red/20" : ""}`}>
            <span className="num w-14 shrink-0 pr-3 text-right text-muted">{l.new ?? l.old}</span>
            <span className={`w-6 shrink-0 text-center ${l.kind === "add" ? "text-green" : l.kind === "del" ? "text-red" : ""}`}>{l.kind === "add" ? "+" : l.kind === "del" ? "−" : ""}</span>
            <span className="overflow-hidden text-ellipsis whitespace-pre pr-4">{l.text || " "}</span>
          </div>
        ))}
      </div>
      {fns.length > 0 && <p className="ui m-0 mt-4 text-xl">Changed: <span className="mono text-accent">{fns.filter((x) => x.function !== "<module>").map((x) => x.function).join(", ") || "module-level code"}</span></p>}
    </div>
  );
}

function BigLane({ lane, total, enterKey }: { lane: Lane; total: number; enterKey: number }) {
  const ff = lane.first_failure_position;
  const pos = ff ? ((ff - 0.5) / Math.max(total, 1)) * 100 : 0;
  return (
    <div>
      <div className="ui mb-2 flex items-baseline justify-between gap-4">
        <span className="text-2xl font-semibold">{lane.name === "alphabetical" ? "Retest-all" : "BlastRadius, risk-first"}</span>
        <span className="text-xl text-muted">{ff ? <>first failure at test <span className="num mono text-ink">{ff}</span> of <span className="num">{total}</span></> : "no failure"}</span>
      </div>
      <div key={enterKey} className="br-reveal relative flex h-16 w-full items-end gap-px overflow-hidden rounded bg-page" role="img" aria-label={`${lane.label}: first failure at ${ff ?? "none"} of ${total}`}>
        {lane.ticks.map((t) => {
          const bad = t.outcome === "failed" || t.outcome === "error";
          return <span key={t.i} className={`min-w-px flex-1 ${bad ? "h-full bg-red" : "h-1/2 bg-green/80"}`} />;
        })}
        {ff && <span className="absolute inset-y-0 w-1 bg-ink" style={{ left: `${pos}%` }} />}
      </div>
      {ff && <div className="relative h-8"><span className="ui absolute flex -translate-x-1/2 items-center gap-1.5 whitespace-nowrap text-lg" style={{ left: `${Math.min(Math.max(pos, 8), 92)}%` }}><Icon name="target" />first failure · {fmtMs(lane.elapsed_to_first_failure_ms)}</span></div>}
    </div>
  );
}

function Running({ s, what }: { s: LabState; what: string }) {
  return (
    <div className="grid h-full place-items-center">
      <div className="text-center">
        <p className="ui m-0 flex items-center justify-center gap-3 text-2xl text-blue"><span className="br-pulse inline-block h-3 w-3 rounded-full bg-blue" />running…</p>
        <p className="ui m-0 mt-3 text-xl text-muted">{what}</p>
        {s.tests.started && <p className="num mono m-0 mt-2 text-xl">{liveTests(s)}</p>}
      </div>
    </div>
  );
}

const SCREENS: Screen[] = [
  {
    id: "change", title: "The change",
    ready: (s) => Boolean(s.change), done: (s) => Boolean(s.change) && Boolean(s.graph),
    caption: () => "Someone changed one line of code. Left: the exact edit. Right: where that function sits among all the code, at the centre.",
    real: (s) => `${mode(s)}: the edit was committed in a scratch copy of the repository; the graph was built from the base commit by our own builder (measured, not drawn by hand).`,
    render: (s, g) => (
      <div className="grid h-full grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-8">
        <BigDiff s={s} />
        <div className="relative min-h-0 overflow-hidden rounded-md border border-rule bg-page">
          <GraphView className="absolute inset-0" nodes={g.nodes} edges={g.edges} layout="rings" changed={g.changed} ariaLabel="The change at the centre of the code graph" />
        </div>
      </div>
    ),
  },
  {
    id: "radius", title: "Blast radius",
    ready: (s) => Boolean(s.impact.ranking), done: (s) => Boolean(s.impact.paths),
    caption: () => "The change ripples outward, one ring per step through the code. These are the test files most likely to break, and the three strongest reasons for each.",
    real: (s) => `${mode(s)}: the rings are hop distances in the real graph; the ranking and its reasons are the E1 model's output for this diff (computed).`,
    render: (s, g, k) => {
      const rows = ((s.impact.ranking?.rows ?? []) as { test: string; score: number; reasons: string[] }[]).slice(0, 4);
      return (
        <div className="grid h-full grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)] gap-8">
          <div className="relative min-h-0 overflow-hidden rounded-md border border-rule bg-page">
            <GraphView className="absolute inset-0" nodes={g.nodes} edges={g.edges} layout="rings" changed={g.changed} waveKey={k} paths={g.paths} atRisk={g.atRisk} ariaLabel="Blast radius" />
          </div>
          <ol className="m-0 list-none space-y-5 overflow-hidden p-0">
            {rows.map((r, i) => (
              <li key={r.test}>
                <p className="ui m-0 flex items-baseline gap-3 text-xl"><span className="num text-muted">{i + 1}</span><Id id={r.test.split("/").slice(-1)[0]} n={34} className="font-semibold" /><span className="num mono ml-auto text-lg text-muted">{r.score.toFixed(2)}</span></p>
                <ul className="m-0 mt-1 list-none space-y-0.5 pl-8">
                  {r.reasons.slice(0, 3).map((x) => <li key={x} className="mono truncate text-sm text-muted" title={x}>{x}</li>)}
                </ul>
              </li>
            ))}
          </ol>
        </div>
      );
    },
  },
  {
    id: "race", title: "Test race",
    ready: (s) => Boolean(s.tests.race), done: (s) => Boolean(s.tests.race),
    absent: (s) => (s.tests.done?.reason ? `The suite was not run: ${s.tests.done.reason}` : null),
    caption: () => "Both lanes are the same tests. Retest-all runs them alphabetically; BlastRadius runs the risky ones first, so a broken change is caught sooner.",
    real: (s) => `${mode(s)}: the risk-first lane is the order pytest actually ran, with measured durations. The retest-all lane and the time saved are computed from those durations, not a second run.`,
    render: (s, _g, k) => {
      const race = s.tests.race!;
      const n = s.tests.results.length;
      const [risk, alpha] = race.lanes;
      const saved = alpha.elapsed_to_first_failure_ms !== null && risk.elapsed_to_first_failure_ms !== null ? alpha.elapsed_to_first_failure_ms - risk.elapsed_to_first_failure_ms : null;
      return (
        <div className="flex h-full flex-col justify-center gap-6">
          <BigLane lane={alpha} total={n} enterKey={k} />
          <BigLane lane={risk} total={n} enterKey={k} />
          <div className="ui grid grid-cols-3 gap-6 border-t border-rule pt-5">
            <div><p className="m-0 text-lg text-muted">first failure</p><p className="num mono m-0 text-3xl">{risk.first_failure_position ?? "–"} <span className="text-xl text-muted">vs {alpha.first_failure_position ?? "–"}</span></p></div>
            <div><p className="m-0 text-lg text-muted">time to first failure</p><p className="num mono m-0 text-3xl">{fmtMs(risk.elapsed_to_first_failure_ms)} <span className="text-xl text-muted">vs {fmtMs(alpha.elapsed_to_first_failure_ms)}</span></p></div>
            <div><p className="m-0 text-lg text-muted">time saved (computed)</p><p className="num mono m-0 text-3xl">{saved === null ? "–" : saved > 0 ? fmtMs(saved) : "none"}</p>{saved !== null && saved <= 0 && <p className="m-0 text-base text-muted">on this run the alphabetical order reached a failure as early</p>}</div>
          </div>
        </div>
      );
    },
  },
  {
    id: "arena", title: "Strategy arena",
    ready: (s) => Boolean(arenaOf(s)), done: (s) => Boolean(arenaOf(s)),
    absent: () => "This run has no strategy arena (it was recorded before the arena existed, or its tests did not run).",
    caption: (s) => arenaOf(s)?.takeaway ?? "How other tools would have chosen tests on this same change, against how we choose.",
    real: (s) => `${mode(s)}: every row is computed from this run's full-suite results; no strategy was run separately. Each is an approach re-implemented here, not the vendor's product.`,
    render: (s) => <ArenaTable a={arenaOf(s)!} large />,
  },
  {
    id: "triage", title: "Triage",
    ready: (s) => Boolean(s.triage), done: (s) => Boolean(s.triage),
    caption: () => "Not every red test is this change's fault. Each failure is re-run on the code before the change: if it failed there too, it was inherited.",
    real: (s) => `${mode(s)}: base and head outcomes are measured by re-running the failing tests on the base commit; the flaky call is the E2 model's (computed).`,
    render: (s) => {
      const t = s.triage!;
      if (t.skipped) return <div className="grid h-full place-items-center"><p className="ui m-0 text-2xl text-muted">{t.skipped}: nothing to triage.</p></div>;
      const cols = [["mine", "Mine", "this change broke it", "text-accent"], ["inherited", "Inherited", "already failing before", "text-blue"], ["flaky", "Flaky", "fails without a code reason", "text-amber"]] as const;
      return (
        <div className="grid h-full grid-cols-3 gap-6">
          {cols.map(([k, title, what, tone]) => {
            const rows = t.rows.filter((r) => r.class === k);
            return (
              <div key={k} className="flex min-h-0 flex-col rounded-md border border-rule bg-page p-5">
                <p className={`ui m-0 text-2xl font-semibold ${tone}`}>{title}</p>
                <p className="num mono m-0 text-3xl">{rows.length}</p>
                <p className="ui m-0 mb-4 text-lg text-muted">{what}</p>
                <ul className="m-0 min-h-0 list-none space-y-3 overflow-hidden p-0">
                  {rows.slice(0, 4).map((r) => (
                    <li key={r.test} className="ui text-base">
                      <Id id={r.test.split("::").slice(-1)[0]} n={30} className="block text-base" />
                      <span className="flex items-center gap-3 text-sm text-muted">base <StatusIcon tone={r.base_outcome === "passed" || r.base_outcome === "absent" ? "passed" : "failed"} text /> head <StatusIcon tone="failed" text /></span>
                    </li>
                  ))}
                  {rows.length > 4 && <li className="ui text-base text-muted">and {rows.length - 4} more</li>}
                </ul>
              </div>
            );
          })}
        </div>
      );
    },
  },
  {
    id: "repair", title: "Repair",
    ready: (s) => s.repair.chunks.length > 0, done: (s) => Boolean(s.validate.verdict) || Boolean(s.repair.unavailable),
    absent: (s) => s.repair.unavailable ? `The model was unavailable (${s.repair.unavailable.kind}): ${s.repair.unavailable.reason}` : s.repair.skipped ? `Repair did not run: ${s.repair.skipped}` : null,
    caption: () => "The model sees only the few functions the change touched, writes a patch, and the patch counts only if all five checks pass, the full test suite among them.",
    real: (s) => s.repair.unavailable
      ? `${mode(s)}: the context was chosen in this run; the model was not called (${s.repair.unavailable.kind}), so no patch and no checks exist for this run.`
      : `${mode(s)}: the context, the model's reply and its token count are from this run${s.repair.replies.some((r) => r.from_cache) ? " (the reply was answered from the lab cache)" : ""}; the five checks were executed, not simulated.`,
    render: (s) => {
      const attempt = Math.max(1, ...s.validate.checks.map((c) => c.attempt));
      const un = s.repair.unavailable;
      const pf = parseDiff(String(s.repair.patch?.diff ?? ""))[0];
      const lines = pf ? dedent(pf.lines.filter((l) => l.kind === "add" || l.kind === "del")).slice(0, 10) : [];
      return (
        <div className="grid h-full grid-cols-3 gap-6">
          <div className="min-w-0"><p className="ui m-0 mb-3 text-xl font-semibold">1 · Context</p>
            <ul className="m-0 list-none space-y-3 p-0">{s.repair.chunks.map((c) => <li key={`${c.file}${c.qualname}`} className="rounded border border-rule bg-page p-3"><Id id={c.qualname} n={28} className="text-lg" /><span className="ui block text-base text-muted">{midEllipsis(String(c.why), 70)}</span></li>)}</ul>
            {!un && <p className="ui m-0 mt-3 text-lg text-muted"><span className="num mono text-ink">{s.tokens.total.toLocaleString()}</span> tokens</p>}
          </div>
          <div className="min-w-0"><p className="ui m-0 mb-3 text-xl font-semibold">2 · Patch</p>
            {un ? <p className="ui text-lg text-muted">no patch: the model was not called</p> : pf ? <div className="mono overflow-hidden rounded border border-rule bg-page py-3 text-base leading-[28px]"><p className="m-0 mb-2 px-3 text-sm text-muted">{pf.path}</p>{lines.map((l, k) => <div key={k} className={`flex ${l.kind === "add" ? "bg-green/20" : "bg-red/20"}`}><span className="num w-12 shrink-0 pr-2 text-right text-muted">{l.new ?? l.old}</span><span className={`w-5 shrink-0 text-center ${l.kind === "add" ? "text-green" : "text-red"}`}>{l.kind === "add" ? "+" : "−"}</span><span className="overflow-hidden text-ellipsis whitespace-pre pr-3">{l.text}</span></div>)}</div>
              : <p className="ui text-lg text-muted">{s.running ? "waiting for the model…" : "no applicable patch"}</p>}
          </div>
          <div className="min-w-0"><p className="ui m-0 mb-3 text-xl font-semibold">3 · Five checks</p>
            {un ? (
              <div className="rounded-md border border-amber p-4" role="status">
                <p className="ui m-0 flex items-center gap-2 text-xl font-semibold text-amber"><Icon name="warn" />The model is unavailable</p>
                <p className="ui m-0 mt-2 text-lg">{un.reason}.</p>
                <p className="ui m-0 mt-2 text-base text-muted">Nothing was retried. The recorded run &quot;Seeded task: one swapped operator&quot; shows this step end to end.</p>
              </div>
            ) : <CheckList checks={s.validate.checks} attempt={attempt} large />}
          </div>
        </div>
      );
    },
  },
  {
    id: "verdict", title: "Verdict and PR comment",
    ready: (s) => Boolean(s.report.comment), done: (s) => Boolean(s.report.comment),
    caption: (s) => gapOf(s) ? "A known bug went straight through: every test passed. That is a gap in the tests, found here before a user finds it." : s.repair.unavailable ? "No fix this time: the model could not be called. The bot still reports the risk, the results and the triage." : s.validate.verdict?.accepted ? "The fix passed every test, so the bot would suggest it on the pull request, with all the evidence attached." : "No fix was accepted, so the bot reports the risk and the triage, and suggests nothing it could not prove.",
    real: (s) => gapOf(s)
      ? `${mode(s)}: the mutation was committed in a scratch copy and the full suite ran against it; the tests named were measured by per-test coverage at the base commit and by the code graph.`
      : `${mode(s)}: this is the exact comment text the PR bot rendered in this run. Nothing was posted anywhere.`,
    render: (s) => {
      if (gapOf(s)) return <div className="flex h-full flex-col justify-center"><TestGapPanel s={s} large /></div>;
      const v = s.validate.verdict;
      const ok = v?.accepted === true && v.status === "ok";
      const un = s.repair.unavailable;
      const failed = Number(s.tests.done?.counts?.failed ?? 0) + Number(s.tests.done?.counts?.error ?? 0);
      return (
        <div className="grid h-full grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] gap-8">
          <div className="flex flex-col justify-center">
            <p className={`ui m-0 flex items-center gap-3 text-2xl font-semibold ${ok ? "text-green" : un ? "text-amber" : "text-ink"}`}><Icon name={ok ? "check" : un ? "warn" : "minus"} />{ok ? "Accepted" : un ? "Not repaired" : failed === 0 ? "Nothing to repair" : "Not accepted"}</p>
            <p className="ui m-0 mt-3 text-xl text-muted">{ok ? "The full suite passed with the patch." : un ? `The model was unavailable (${un.kind}); no patch was attempted.` : failed === 0 ? "No test failed." : v?.note ?? v?.reason ?? "No patch was proposed."}</p>
            {s.tests.done?.counts && <p className="num mono m-0 mt-6 text-xl">{s.tests.done.counts.total} tests · {failed} failed{ok ? " before the fix" : ""}</p>}
          </div>
          <div className="relative min-h-0 overflow-hidden">
            <MarkdownLite text={s.report.comment ?? ""} className="h-full overflow-hidden text-base" />
            <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-page to-transparent" />
          </div>
        </div>
      );
    },
  },
  {
    id: "evidence", title: "Evidence",
    ready: () => true, done: () => true,
    caption: () => "What one run shows, the benchmark measures at scale. These four results come from BR-Bench, each read from the file that generates it.",
    real: () => "FROM BR-BENCH: read from paper/generated at build time, not from this run.",
    render: () => <EvidenceSlide />,
  },
];

function EvidenceSlide() {
  const cards = useEvidence();
  return (
    <div className="grid h-full grid-cols-2 grid-rows-2 gap-6">
      {cards.map((c) => (
        <div key={c.title} className="flex min-h-0 flex-col rounded-md border border-rule bg-panel p-5">
          <p className="ui m-0 text-lg font-semibold text-muted">{c.title}</p>
          <p className="num mono m-0 mt-1 text-2xl font-semibold">{c.big}</p>
          <p className="ui m-0 mt-2 line-clamp-4 text-lg leading-snug">{c.body}</p>
          <p className="mono m-0 mt-auto pt-2 text-sm text-muted">Source: {c.source}</p>
        </div>
      ))}
    </div>
  );
}

const DWELL = 7000;

/** Why a screen shows nothing once the run is over (null while it can still arrive, or when it is ready). */
export function absentReason(sc: Screen, s: LabState): string | null {
  return !sc.ready(s) && !s.running ? (sc.absent?.(s) ?? "This stage produced nothing in this run.") : null;
}

/** One screen's body: the screen when its events have arrived, why it is empty after the run, or "running…". */
export function ScreenBody({ s, g, i, enterKey = 1 }: { s: LabState; g: G; i: number; enterKey?: number }) {
  const sc = SCREENS[i];
  const absent = absentReason(sc, s);
  if (sc.ready(s)) return <>{sc.render(s, g, enterKey)}</>;
  if (absent) return <div className="grid h-full place-items-center"><p className="ui m-0 max-w-3xl text-center text-2xl text-muted">{absent}</p></div>;
  return <Running s={s} what={s.running ? `waiting for the ${sc.title.toLowerCase()} stage` : "waiting for a run to start"} />;
}

export { SCREENS };
export type { G as PresenterGraph };

/** Full-screen, projector-sized walkthrough of the current or replayed run: one stage per screen. */
export function Presenter({ s, g, onClose, onRestart }: { s: LabState; g: G; onClose: () => void; onRestart: () => void }) {
  const root = useRef<HTMLDivElement>(null);
  const [i, setI] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [enterKey, setEnterKey] = useState(1);
  const sc = SCREENS[i];
  const go = useCallback((k: number) => { setI(Math.max(0, Math.min(SCREENS.length - 1, k))); setEnterKey((x) => x + 1); }, []);

  useEffect(() => {
    const el = root.current;
    el?.focus();
    el?.requestFullscreen?.().catch(() => undefined);
    const off = () => { if (!document.fullscreenElement) onClose(); };
    document.addEventListener("fullscreenchange", off);
    return () => { document.removeEventListener("fullscreenchange", off); if (document.fullscreenElement) document.exitFullscreen().catch(() => undefined); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // autoplay: a screen moves on once everything it shows has arrived and the reader had time to read it
  const ready = sc.ready(s), done = sc.done(s);
  const absent = absentReason(sc, s);
  useEffect(() => {
    if (!playing || i >= SCREENS.length - 1 || !(done || absent)) return;
    const t = window.setTimeout(() => go(i + 1), absent ? 2500 : DWELL);
    return () => clearTimeout(t);
  }, [playing, i, done, absent, go]);
  useEffect(() => { if (ready) setEnterKey((x) => x + 1); }, [ready]);

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight" || e.key === "PageDown") { e.preventDefault(); go(i + 1); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); go(i - 1); }
    else if (e.key === " ") { e.preventDefault(); setPlaying((p) => !p); }
    else if (e.key === "r" || e.key === "R") { e.preventDefault(); go(0); onRestart(); }
    else if (e.key === "Escape") { e.preventDefault(); onClose(); }
    else if (/^[1-8]$/.test(e.key)) go(Number(e.key) - 1);
  };
  const doneFlags = useMemo(() => SCREENS.map((x) => x.ready(s)), [s]);

  return (
    <div ref={root} tabIndex={-1} onKeyDown={onKey} role="dialog" aria-modal="true" aria-label={`Presenter: step ${i + 1} of ${SCREENS.length}, ${sc.title}`}
      className="fixed inset-0 z-50 flex flex-col bg-page text-ink outline-none">
      <header className="flex h-16 shrink-0 items-center gap-6 border-b border-rule px-8">
        <span className="ui text-lg font-semibold"><span className="text-accent">●</span> BlastRadius</span>
        <span className={`ui rounded border px-2.5 py-0.5 text-base font-semibold ${s.mode === "replay" ? "border-amber text-amber" : "border-green text-green"}`}>{s.mode === "replay" ? "REPLAY" : "LIVE"}</span>
        <h2 className="ui m-0 text-xl font-semibold"><span className="num text-muted">{i + 1}/{SCREENS.length}</span> · {sc.title}</h2>
        <nav className="ml-auto flex items-center gap-1.5" aria-label="Steps">
          {SCREENS.map((x, k) => (
            <button key={x.id} type="button" onClick={() => go(k)} aria-label={`Step ${k + 1}: ${x.title}`} aria-current={k === i ? "step" : undefined}
              className={`h-2.5 rounded-full transition-all ${k === i ? "w-8 bg-accent" : doneFlags[k] ? "w-2.5 bg-ink/70" : "w-2.5 bg-rule"}`} />
          ))}
        </nav>
        <div className="flex items-center gap-1">
          <button type="button" onClick={() => go(i - 1)} className="rounded p-2 text-lg text-muted hover:text-ink" aria-label="Previous step"><Icon name="chevron" className="rotate-180" /></button>
          <button type="button" onClick={() => setPlaying((p) => !p)} className="rounded p-2 text-lg text-muted hover:text-ink" aria-label={playing ? "Pause" : "Play"}><Icon name={playing ? "pause" : "play"} /></button>
          <button type="button" onClick={() => go(i + 1)} className="rounded p-2 text-lg text-muted hover:text-ink" aria-label="Next step"><Icon name="chevron" /></button>
          <button type="button" onClick={() => { go(0); onRestart(); }} className="rounded p-2 text-lg text-muted hover:text-ink" aria-label="Restart"><Icon name="restart" /></button>
          <button type="button" onClick={onClose} className="rounded p-2 text-lg text-muted hover:text-ink" aria-label="Close the presenter"><Icon name="close" /></button>
        </div>
      </header>
      <main className="min-h-0 flex-1 px-10 pb-4 pt-8">
        <ScreenBody s={s} g={g} i={i} enterKey={enterKey} />
      </main>
      <footer className="shrink-0 border-t border-rule px-10 py-4">
        <p className="ui m-0 text-xl leading-snug">{sc.caption(s)}</p>
        <p className="ui m-0 mt-1.5 text-sm text-muted"><span className="font-semibold">What is real here:</span> {sc.real(s)}</p>
        <p className="ui m-0 mt-1 text-xs text-muted">← → step · space {playing ? "pause" : "play"} · R restart · Esc close</p>
      </footer>
    </div>
  );
}

