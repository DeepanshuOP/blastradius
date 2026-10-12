"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { ArenaDoc, Strategy } from "./Arena";
import { Icon, fmtMs } from "./common";
import { Info, reducedMotion } from "./Info";

/** Wall time the shared clock takes to run through the longest lane (seconds). */
const PLAY_S = 6;

/** The shared race clock: measured milliseconds from 0 to `total`, played over PLAY_S seconds; the end state at once
 * under reduced motion. `run` restarts it. */
function useClock(total: number, run: number) {
  const [t, setT] = useState(0);
  const [done, setDone] = useState(false);
  useEffect(() => {
    if (total <= 0 || reducedMotion()) { setT(total); setDone(true); return; }
    setT(0); setDone(false);
    const t0 = performance.now();
    let raf = 0;
    const step = (now: number) => {
      const k = Math.min(1, (now - t0) / (PLAY_S * 1000));
      setT(total * k);
      if (k < 1) raf = requestAnimationFrame(step); else setDone(true);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [total, run]);
  return { t, done };
}

const laneEnd = (x: Strategy) => (x.status === "unavailable" ? 0 : x.ci_ms);

/** One lane per strategy on a shared clock. A flag stands where the lane reaches its first failure. */
export function ArenaRace({ a }: { a: ArenaDoc }) {
  const [run, setRun] = useState(0);
  const total = useMemo(() => Math.max(1, ...a.strategies.map(laneEnd)), [a]);
  const { t, done } = useClock(total, run);
  const lanes = a.strategies;
  return (
    <section aria-label="Strategy race" className="rounded-md border border-rule bg-page p-3">
      <header className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <h4 className="ui m-0 text-sm font-semibold">Race: first failure</h4>
        <span className="ui rounded bg-blue/15 px-1.5 py-0.5 text-2xs font-semibold tracking-wider text-blue">COMPUTED FROM THIS RUN</span>
        <Info label="How the race is computed">
          <span className="block">Every lane plays this run&apos;s measured per-test durations, in that strategy&apos;s order, on one clock. Nothing was run separately.</span>
          <span className="mt-1 block">Playback is {Math.round(total / PLAY_S)} ms of measured time per second.</span>
        </Info>
        <span className="num mono ml-auto text-xs text-muted">clock {fmtMs(t)}</span>
        <button type="button" onClick={() => setRun(run + 1)} className="ui inline-flex items-center gap-1 rounded border border-rule px-2 py-0.5 text-xs hover:border-muted" aria-label="Replay the race"><Icon name="restart" />replay</button>
      </header>
      <ol className="m-0 list-none space-y-2 p-0">
        {lanes.map((x) => {
          const end = laneEnd(x);
          const fill = x.status === "unavailable" ? 0 : Math.min(t, end) / total * 100;
          const ff = x.first_failure_ms;
          const flagAt = ff !== null && ff !== undefined ? (ff / total) * 100 : null;
          const reached = ff !== null && ff !== undefined && t >= ff;
          return (
            <li key={x.id} className="grid grid-cols-[9rem_minmax(0,1fr)_7.5rem] items-center gap-3">
              <span className={`ui truncate text-sm ${x.ours ? "font-semibold" : "text-muted"}`} title={x.name}>{x.name}</span>
              <div className="relative h-5 rounded-sm bg-panel2" role="img"
                aria-label={x.status === "unavailable" ? `${x.name}: unavailable` : flagAt === null ? `${x.name}: ${a.n_failing ? "no failure reached" : "no failure to reach"}` : `${x.name}: first failure at test ${x.first_failure_position}, ${fmtMs(ff)}`}>
                {x.status !== "unavailable" && <div className={`absolute inset-y-0 left-0 rounded-sm ${x.ours ? "bg-accent/70" : "bg-muted/50"}`} style={{ width: `${fill}%` }} />}
                {flagAt !== null && (
                  <span className={`absolute -top-1 bottom-[-4px] w-0.5 ${reached ? "bg-ink" : "bg-transparent"}`} style={{ left: `${flagAt}%` }}>
                    {reached && <span className="ui absolute -top-[2px] left-0.5 flex items-center gap-0.5 whitespace-nowrap rounded-sm bg-ink px-1 text-2xs font-semibold text-page"><Icon name="target" />#{x.first_failure_position}</span>}
                  </span>
                )}
                {x.status === "unavailable" && <span className="ui absolute inset-0 grid place-items-center text-2xs text-muted">unavailable</span>}
              </div>
              <span className="num mono text-right text-xs text-muted">
                {x.status === "unavailable" ? "–" : reached || done ? (ff !== null && ff !== undefined ? fmtMs(ff) : a.n_failing ? "missed" : "no failure") : "…"}
              </span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

const MEDAL = ["bg-amber/80 text-page", "bg-muted/70 text-page", "bg-[#a0673a] text-page"];

/** The podium: strategies ranked by time to the first failure, with what each costs. */
export function Podium({ a }: { a: ArenaDoc }) {
  const ranked = a.strategies.filter((x) => x.status !== "unavailable" && x.first_failure_ms !== null && x.first_failure_ms !== undefined)
    .sort((p, q) => (p.first_failure_ms as number) - (q.first_failure_ms as number) || p.name.localeCompare(q.name));
  if (a.n_failing === 0) {
    return <p className="ui m-0 text-sm text-muted">No test failed, so there is nothing to rank: every strategy would have passed.</p>;
  }
  const top = ranked.slice(0, 3);
  const order = top.length === 3 ? [top[1], top[0], top[2]] : top;           // 2nd, 1st, 3rd
  const height = (x: Strategy) => `${40 + 30 * (3 - ranked.indexOf(x))}px`;
  return (
    <section aria-label="Podium" className="rounded-md border border-rule bg-page p-3">
      <h4 className="ui m-0 mb-3 flex items-center gap-2 text-sm font-semibold">Podium <span className="text-xs font-normal text-muted">by time to first failure</span></h4>
      <ol className="m-0 flex list-none items-end justify-center gap-3 p-0">
        {order.map((x) => {
          const place = ranked.indexOf(x);
          return (
            <li key={x.id} className="flex w-44 flex-col items-center text-center">
              <span className={`ui text-sm ${x.ours ? "font-semibold" : ""}`}>{x.name}</span>
              <span className="num mono text-lg font-semibold">{fmtMs(x.first_failure_ms)}</span>
              <span className="ui text-xs text-muted">test #{x.first_failure_position} · runs {x.selected}</span>
              <span className="ui text-xs text-muted">caught {x.caught}/{a.n_failing}</span>
              <span className="ui mb-1 text-2xs text-muted" title={x.needs}>cost {fmtMs(x.ci_ms)} CI</span>
              <span className={`grid w-full place-items-center rounded-t text-xl font-bold ${MEDAL[place]}`} style={{ height: height(x) }} aria-label={`place ${place + 1}`}>{place + 1}</span>
            </li>
          );
        })}
      </ol>
      {ranked.length > 3 && (
        <p className="ui m-0 mt-3 text-xs text-muted">
          {ranked.slice(3).map((x, i) => <span key={x.id}>{i ? " · " : ""}{i + 4}. {x.name} <span className="num mono">{fmtMs(x.first_failure_ms)}</span></span>)}
        </p>
      )}
    </section>
  );
}
