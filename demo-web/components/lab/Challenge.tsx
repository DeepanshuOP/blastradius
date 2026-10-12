"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { TestGapPanel, gapOf } from "./BreakIt";
import { BTN, BTN_PRIMARY, Icon } from "./common";
import { Counter } from "./Info";
import type { LabState } from "./types";

/** What `python -m src.lab challenge` returns for a seed. */
export interface Pick { seed: number; file: string; function: string; operator: string; line: number; old: string; new: string; n_functions: number; n_operators: number }
export interface GuessTally { answered: number; correct: number }
type Phase = "ask" | "running" | "revealed";

const KEY = "br-lab-challenge-v1";
const readTally = (): GuessTally => {
  try { const j = JSON.parse(sessionStorage.getItem(KEY) ?? "{}") as Partial<GuessTally>; return { answered: Number(j.answered) || 0, correct: Number(j.correct) || 0 }; } catch { return { answered: 0, correct: 0 }; }
};
const writeTally = (t: GuessTally) => { try { sessionStorage.setItem(KEY, JSON.stringify(t)); } catch { /* storage blocked */ } };

/** Whether the suite caught the change, and where each ordering reached its first failure; all read from the run's events. */
export function outcomeOf(s: LabState): { ran: boolean; caught: boolean; ours: number | null; base: number | null; failed: number; total: number | null } {
  const c = s.tests.done?.counts as Record<string, number> | undefined;
  const failed = c ? Number(c.failed ?? 0) + Number(c.error ?? 0) : 0;
  const lanes = s.tests.race?.lanes ?? [];
  return {
    ran: Boolean(c) && Number(c?.total ?? 0) > 0,
    caught: failed > 0,
    ours: lanes.find((l) => l.name === "risk-first")?.first_failure_position ?? null,
    base: lanes.find((l) => l.name === "alphabetical")?.first_failure_position ?? null,
    failed, total: c ? Number(c.total ?? 0) : null,
  };
}

/**
 * The reviewer challenge: a seeded random bug, a yes/no guess, a live run, the reveal and a session tally of correct
 * guesses. No model is called unless the reviewer presses "Fix it".
 */
export function ChallengeCard({ s, repo, live, running, llmOk, onRun, onPickMyself, onClose }: {
  s: LabState; repo: string | null; live: boolean; running: boolean; llmOk: boolean;
  onRun: (c: { file: string; function: string; operator: string; line: number }, opts: { noLlm: boolean }) => void;
  onPickMyself: () => void; onClose: () => void;
}) {
  const [seed, setSeed] = useState<number | null>(null);
  const [seedText, setSeedText] = useState("");
  const [pick, setPick] = useState<Pick | null>(null);
  const [err, setErr] = useState("");
  const [phase, setPhase] = useState<Phase>("ask");
  const [guess, setGuess] = useState<boolean | null>(null);
  const [fixed, setFixed] = useState(false);
  const [tally, setTally] = useState<GuessTally>({ answered: 0, correct: 0 });
  const runKey = useRef<number | null>(null);
  useEffect(() => { setTally(readTally()); }, []);

  const choose = useCallback(async (sd: number | null) => {
    if (!repo) return;
    setErr(""); setPick(null); setPhase("ask"); setGuess(null); setFixed(false);
    try {
      const r = await fetch(`/api/lab/challenge?repo=${repo}${sd === null ? "" : `&seed=${sd}`}`);
      const j = await r.json();
      if (!r.ok) throw new Error(j.error ?? `HTTP ${r.status}`);
      setPick(j as Pick); setSeed(j.seed); setSeedText(String(j.seed));
    } catch (e) { setErr(String((e as Error).message ?? e)); }
  }, [repo]);
  useEffect(() => { if (live && repo) void choose(null); }, [repo, live]); // eslint-disable-line react-hooks/exhaustive-deps

  const answer = (yes: boolean) => {
    if (!pick || running) return;
    setGuess(yes); setPhase("running"); runKey.current = null;
    onRun({ file: pick.file, function: pick.function, operator: pick.operator, line: pick.line }, { noLlm: true });
  };

  // the reveal: once, when this challenge's run has finished
  const out = outcomeOf(s);
  const done = phase === "running" && !s.running && s.mode === "live" && s.events.some((e) => e.type === "run.end");
  useEffect(() => {
    if (!done || guess === null || runKey.current === s.startedAt) return;
    runKey.current = s.startedAt;
    setPhase("revealed");
    if (out.ran && !fixed) {                     // the "Fix it" re-run reveals again but never counts a second guess
      const t = { answered: tally.answered + 1, correct: tally.correct + (guess === out.caught ? 1 : 0) };
      setTally(t); writeTally(t);
    }
  }); // eslint-disable-line react-hooks/exhaustive-deps

  const fix = () => {
    if (!pick) return;
    setFixed(true); setPhase("running"); runKey.current = null;
    onRun({ file: pick.file, function: pick.function, operator: pick.operator, line: pick.line }, { noLlm: false });
  };
  const verdict = s.validate.verdict;
  const right = guess !== null && out.ran && guess === out.caught;

  return (
    <section aria-label="Reviewer challenge" className="rounded-md border border-accent/60 bg-panel">
      <header className="flex flex-wrap items-center gap-3 border-b border-rule px-4 py-2">
        <h2 className="ui m-0 flex items-center gap-2 text-md font-semibold"><Icon name="bug" className="text-accent" />Challenge</h2>
        <span className="ui text-sm text-muted" title="Correct guesses in this browser session">
          your guesses: <Counter value={tally.correct} className="text-ink" /> of <Counter value={tally.answered} className="text-ink" /> correct
        </span>
        <button type="button" onClick={onClose} className={`${BTN} ml-auto`} aria-label="Close the challenge">Close</button>
      </header>
      <div className="p-4">
        {!live ? <p className="ui m-0 text-sm text-muted">The challenge runs live and needs the local server.</p>
          : !repo ? <p className="ui m-0 text-sm text-muted">Pick one of the four prepared repositories first.</p>
          : err ? <p className="ui m-0 text-sm text-red" role="alert">{err}</p>
          : !pick ? <p className="ui m-0 text-sm text-muted">Choosing a bug…</p>
          : (
            <div className="grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
              <div className="min-w-0">
                <p className="ui m-0 text-2xl font-semibold">Will the tests catch this bug?</p>
                <p className="mono m-0 mt-2 truncate text-sm text-muted" title={`${pick.file}:${pick.line} ${pick.function}`}>{pick.file}:{pick.line} · {pick.function}</p>
                <div className="mono mt-2 overflow-hidden rounded border border-rule bg-page text-sm leading-[26px]">
                  <div className="flex bg-red/15"><span className="w-5 text-center text-red">−</span><span className="whitespace-pre pr-2">{pick.old}</span></div>
                  <div className="flex bg-green/15"><span className="w-5 text-center text-green">+</span><span className="whitespace-pre pr-2">{pick.new}</span></div>
                </div>
                <p className="ui m-0 mt-1 text-xs text-muted">{pick.operator}, one of {pick.n_operators} operator{pick.n_operators === 1 ? "" : "s"} that apply to this function</p>
                {phase === "ask" && (
                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    <button type="button" onClick={() => answer(true)} disabled={running} className={`${BTN_PRIMARY} min-h-[48px] px-8 text-lg`}>Yes, caught</button>
                    <button type="button" onClick={() => answer(false)} disabled={running} className={`${BTN} min-h-[48px] px-8 text-lg font-semibold`}>No, it survives</button>
                  </div>
                )}
                {phase !== "ask" && guess !== null && <p className="ui m-0 mt-4 text-sm">Your guess: <span className="font-semibold">{guess ? "caught" : "survives"}</span></p>}
              </div>
              <div className="min-w-0 space-y-3">
                <div className="flex flex-wrap items-end gap-2">
                  <label className="ui block text-xs text-muted" htmlFor="ch-seed">Seed
                    <input id="ch-seed" inputMode="numeric" value={seedText} disabled={phase !== "ask"} onChange={(e) => setSeedText(e.target.value.replace(/\D/g, ""))}
                      onKeyDown={(e) => { if (e.key === "Enter" && seedText) void choose(Number(seedText)); }}
                      className="mono mt-0.5 block w-36 px-2 py-1 text-sm disabled:opacity-50" />
                  </label>
                  <button type="button" className={BTN} disabled={phase !== "ask" || !seedText} onClick={() => void choose(Number(seedText))}>Use seed</button>
                  <button type="button" className={BTN} disabled={phase !== "ask"} onClick={() => void choose(null)}>New random bug</button>
                </div>
                <p className="ui m-0 text-xs text-muted">The same seed on the same repository names the same bug. Seed <span className="num mono text-ink">{seed}</span>.</p>
                <button type="button" className={BTN} disabled={phase !== "ask"} onClick={onPickMyself}>Pick the function myself</button>
              </div>
            </div>
          )}

        {phase === "running" && <p className="ui m-0 mt-4 flex items-center gap-2 text-sm text-blue" role="status"><span className="br-pulse inline-block h-2 w-2 rounded-full bg-blue" />{fixed ? "Asking the model for a fix and checking it…" : "Running the whole suite on this change…"}</p>}

        {phase === "revealed" && pick && (
          <div className="mt-5 space-y-4 border-t border-rule pt-4" role="status" aria-live="polite">
            {!out.ran ? (
              <p className="ui m-0 text-lg text-amber"><Icon name="warn" /> The tests could not run for this repository, so there is nothing to reveal.</p>
            ) : (
              <>
                <p className={`ui m-0 flex flex-wrap items-center gap-3 text-3xl font-bold ${out.caught ? "text-green" : "text-amber"}`}>
                  <Icon name={out.caught ? "check" : "warn"} />{out.caught ? `Caught: ${out.failed} test${out.failed === 1 ? "" : "s"} failed` : "Survived: every test passed"}
                  <span className={`ui rounded px-2 py-0.5 text-sm font-semibold ${right ? "bg-green/20 text-green" : "bg-red/20 text-red"}`}>{right ? "you were right" : "you were wrong"}</span>
                </p>
                {out.caught && (
                  <p className="ui m-0 text-lg">
                    BlastRadius reached its first failure at test <span className="num mono font-semibold">{out.ours ?? "–"}</span>;
                    retest-all at test <span className="num mono font-semibold">{out.base ?? "–"}</span>{out.total ? <span className="text-muted"> of {out.total}</span> : null}.
                  </p>
                )}
                {!out.caught && gapOf(s) && <TestGapPanel s={s} />}
                {out.caught && (
                  <div className="flex flex-wrap items-center gap-3">
                    {!fixed ? (
                      <button type="button" onClick={fix} disabled={!llmOk || running} className={BTN_PRIMARY}
                        title={llmOk ? "One model call, then the five checks, the full suite among them" : "The model is not available (no key, or the daily quota is used up)"}>
                        <Icon name="bolt" />Fix it
                      </button>
                    ) : verdict ? (
                      <p className={`ui m-0 text-base font-semibold ${verdict.accepted ? "text-green" : "text-ink"}`}>{verdict.accepted ? "The model's fix passed all five checks." : "The model's fix was not accepted."}</p>
                    ) : s.repair.unavailable ? (
                      <p className="ui m-0 text-sm text-amber">The model was unavailable: {s.repair.unavailable.reason}</p>
                    ) : null}
                    {!fixed && <span className="ui text-xs text-muted">No model has been called so far in this challenge.</span>}
                  </div>
                )}
              </>
            )}
            <button type="button" className={BTN} onClick={() => void choose(null)} disabled={running}>Next bug</button>
          </div>
        )}
      </div>
    </section>
  );
}
