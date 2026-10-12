"use client";

import { useEffect, useRef, useState } from "react";
import { Counter, Info } from "./Info";
import type { LabState } from "./types";

/** What one run adds to the session scoreboard. Every field is read from that run's events, nothing else. */
export interface Tally { bugs: number; caught: number; earlier: number; gaps: number; fixed: number; tokens: number }
export const EMPTY: Tally = { bugs: 0, caught: 0, earlier: 0, gaps: 0, fixed: 0, tokens: 0 };

const sum = (a: Tally, b: Tally): Tally => ({ bugs: a.bugs + b.bugs, caught: a.caught + b.caught, earlier: a.earlier + b.earlier, gaps: a.gaps + b.gaps, fixed: a.fixed + b.fixed, tokens: a.tokens + b.tokens });

/**
 * The contribution of the run in `s`, from the events that have arrived so far:
 *   bugs     a change.applied event whose source is an injected bug, a seeded task or an edit
 *   caught   tests.done reports at least one failing case
 *   earlier  tests.race: BlastRadius reached its first failure at a lower test number than retest-all
 *   gaps     an arena.gap event
 *   fixed    a validate.verdict that was accepted
 *   tokens   tokens spent by model calls (answers served from the lab cache cost nothing)
 */
export function contribution(s: LabState): Tally {
  const t = { ...EMPTY };
  const kind = String(s.change?.source?.kind ?? "");
  if (["inject", "seeded-task", "edit"].includes(kind)) t.bugs = 1;
  const c = s.tests.done?.counts as Record<string, number> | undefined;
  if (c && Number(c.failed ?? 0) + Number(c.error ?? 0) > 0) t.caught = 1;
  const lanes = s.tests.race?.lanes;
  if (lanes) {
    const ours = lanes.find((l) => l.name === "risk-first")?.first_failure_position;
    const base = lanes.find((l) => l.name === "alphabetical")?.first_failure_position;
    if (ours && base && ours < base) t.earlier = 1;
  }
  if (s.events.some((e) => e.type === "arena.gap")) t.gaps = 1;
  if (s.validate.verdict?.accepted === true && s.validate.verdict.status === "ok") t.fixed = 1;
  t.tokens = Math.max(0, s.tokens.total - s.tokens.cached);
  return t;
}

const KEY = "br-lab-session-v1";
const read = (): Tally => {
  try { return { ...EMPTY, ...(JSON.parse(sessionStorage.getItem(KEY) ?? "{}") as Partial<Tally>) }; } catch { return EMPTY; }
};
const write = (t: Tally) => { try { sessionStorage.setItem(KEY, JSON.stringify(t)); } catch { /* storage blocked */ } };

/**
 * The session tally: finished live runs (kept in sessionStorage) plus the run in progress. A replay adds nothing: the
 * scoreboard counts what this browser session ran, not what was recorded earlier.
 */
export function useSessionTally(s: LabState): Tally {
  const [base, setBase] = useState<Tally>(EMPTY);
  const last = useRef<{ key: string | null; c: Tally }>({ key: null, c: EMPTY });
  useEffect(() => { setBase(read()); }, []);
  useEffect(() => () => { if (last.current.key) write(sum(read(), last.current.c)); }, []);   // leaving the page banks the run
  const key = s.mode === "live" && s.startedAt ? String(s.startedAt) : null;
  const cur = key ? contribution(s) : EMPTY;
  useEffect(() => {
    if (last.current.key !== key) {                         // a run ended, was reset, or a new one started: bank it
      if (last.current.key) {
        const banked = sum(read(), last.current.c);
        write(banked);
        setBase(banked);
      }
      last.current = { key, c: cur };
    } else {
      last.current = { key, c: cur };
    }
  });
  return sum(base, cur);
}

const ITEMS: { k: keyof Tally; label: string; what: string }[] = [
  { k: "bugs", label: "bugs injected", what: "Changes this session put into code: an injected bug, a seeded task or an edit." },
  { k: "caught", label: "caught by the suite", what: "Runs where at least one test failed on the change." },
  { k: "earlier", label: "caught earlier", what: "Runs where BlastRadius reached its first failure at a lower test number than retest-all." },
  { k: "gaps", label: "test gaps", what: "Bugs that every test let through: the suite has a gap there." },
  { k: "fixed", label: "fixes validated", what: "Patches whose five checks passed, the full suite included." },
];

/** The session scoreboard of the top bar. Counters move only when a run event arrives. */
export function Scoreboard({ t }: { t: Tally }) {
  return (
    <ul className="m-0 flex list-none flex-wrap items-center gap-x-4 gap-y-1 p-0" aria-label="Session scoreboard">
      {ITEMS.map((x) => (
        <li key={x.k} className="ui flex items-baseline gap-1.5 text-sm" title={x.what}>
          <Counter value={t[x.k]} className="text-md font-semibold" />
          <span className="text-xs text-muted">{x.label}</span>
        </li>
      ))}
      <li className="ui flex items-baseline gap-1.5 text-sm" title="Tokens the model calls of this session spent. The model is on the free tier: $0.">
        <Counter value={t.tokens} className="text-md font-semibold" />
        <span className="text-xs text-muted">tokens · <span className="num mono text-ink">$0</span></span>
      </li>
      <li><Info label="About the scoreboard" align="right">
        <span className="block font-semibold">This browser session</span>
        <span className="mt-1 block">Counted from live run events only; replays add nothing. Tokens are model calls that went to the provider, which is on the free tier, so the cost is $0.</span>
      </Info></li>
    </ul>
  );
}
