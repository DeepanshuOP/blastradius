"use client";

import { Icon, Prov, StatusIcon, fmtMs, type Tone } from "./common";
import { Term } from "./Glossary";
import type { LabState, Stage } from "./types";

/** The recording the guided demo falls back to: itsdangerous, reviewer-challenge seed 7, end to end. */
export const GUIDED_RECORDING = "guided-demo";
export const GUIDED_REPO = "itsdangerous";
export const GUIDED_SEED = 7;

export type StepId = "change" | "impact" | "tests" | "triage" | "repair";
export const GUIDED_STEPS: { id: StepId; label: string; stages: Stage[]; caption: React.ReactNode }[] = [
  { id: "change", label: "Change", stages: ["repo", "graph", "change"], caption: <>One seeded bug goes into itsdangerous and the code graph is rebuilt to show its <Term k="blast radius" />.</> },
  { id: "impact", label: "Impact", stages: ["impact"], caption: <>The <Term k="LambdaRank" /> ranker scores every test file by how likely this change breaks it.</> },
  { id: "tests", label: "Tests", stages: ["tests", "arena"], caption: <>The whole suite runs, riskiest tests first, so the failures show up early.</> },
  { id: "triage", label: "Triage", stages: ["triage"], caption: <>Each failure is checked on the <Term k="base commit" />: mine, <Term k="inherited" /> or <Term k="flaky" />?</> },
  { id: "repair", label: "Repair", stages: ["repair", "validate", "report"], caption: <>The model writes a patch; it counts only if the full suite then passes.</> },
];

/** Index of the step that ran a stage. */
export const stepOf = (st: Stage): number => GUIDED_STEPS.findIndex((x) => x.stages.includes(st));

export function stepTone(s: LabState, i: number): Tone {
  const xs = GUIDED_STEPS[i].stages.map((k) => s.stage[k]?.status).filter(Boolean);
  if (!xs.length) return "pending";
  if (xs.includes("failed")) return "failed";
  if (xs.includes("running") && s.running) return "running";
  if (GUIDED_STEPS[i].id === "repair" && (s.repair.skipped || s.repair.unavailable)) return "skipped";
  return xs.every((x) => x === "skipped") ? "skipped" : s.running && i === currentStep(s) ? "running" : "ok";
}

/** Wall time of a step: from its first event to its last, read from the events' own timestamps. */
export function stepMs(s: LabState, i: number): number | null {
  const evs = s.events.filter((e) => GUIDED_STEPS[i].stages.includes(e.stage));
  if (!evs.length) return null;
  const prev = s.events.filter((e) => e.seq < evs[0].seq && e.stage !== "meta").pop();
  const t0 = Date.parse((prev ?? evs[0]).ts);
  return Math.max(0, Date.parse(evs[evs.length - 1].ts) - t0);
}

export function currentStep(s: LabState): number {
  const last = [...s.events].reverse().find((e) => e.stage !== "meta");
  return last ? Math.max(0, stepOf(last.stage)) : 0;
}

/** The first step a live run could not complete (a failed stage, or a repair that did not run), else null. */
export function liveFailure(s: LabState): number | null {
  for (let i = 0; i < GUIDED_STEPS.length; i++) if (stepTone(s, i) === "failed") return i;
  if (s.repair.skipped || s.repair.unavailable) return stepOf("repair");
  if (s.error) return currentStep(s);
  return null;
}

export type StepRecord = { ms: number | null; tone: Tone; source: "live" | "replay" };
export type Guided = { phase: "idle" | "running" | "done"; live: StepRecord[]; fellBackAt: number | null; reason: string | null; pick: string | null };
export const GUIDED_IDLE: Guided = { phase: "idle", live: [], fellBackAt: null, reason: null, pick: null };

/** The five-step stepper of the guided demo: per-step status, timing and source label, one caption for the current step. */
export function GuidedStepper({ s, g, onStop }: { s: LabState; g: Guided; onStop: () => void }) {
  const cur = g.phase === "done" ? GUIDED_STEPS.length - 1 : currentStep(s);
  const rows = GUIDED_STEPS.map((step, i) => {
    const kept = g.fellBackAt !== null && i < g.fellBackAt ? g.live[i] : null;
    return kept ?? { ms: stepMs(s, i), tone: stepTone(s, i), source: s.mode === "replay" ? "replay" as const : "live" as const };
  });
  const done = g.phase === "done";
  return (
    <section aria-label="Guided demo" data-testid="guided-stepper" className="rounded-md border border-accent/60 bg-panel px-3 py-2">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <span className="ui text-sm font-semibold">Full demo{g.pick ? <span className="mono ml-1.5 hidden text-xs font-normal text-muted wide:inline">{g.pick}</span> : null}</span>
        <ol className="m-0 flex min-w-0 flex-1 list-none flex-wrap items-center gap-1.5 p-0">
          {GUIDED_STEPS.map((step, i) => {
            const r = rows[i];
            const on = !done && i === cur;
            return (
              <li key={step.id} className="flex items-center gap-1.5" aria-current={on ? "step" : undefined} data-step={step.id} data-tone={r.tone} data-source={r.source}>
                {i > 0 && <Icon name="chevron" className="text-muted" />}
                <span className={`ui inline-flex items-center gap-1.5 rounded-full border px-2 py-1 text-sm ${on ? "border-accent font-semibold text-ink" : "border-rule"}`}>
                  <StatusIcon tone={r.tone} />{step.label}
                  {r.ms !== null && r.tone !== "pending" && r.tone !== "running" && <span className="num mono text-xs text-muted">{fmtMs(r.ms)}</span>}
                  {r.tone !== "pending" && <Prov mode={r.source} />}
                </span>
              </li>
            );
          })}
        </ol>
        {!done && g.phase === "running" && <button type="button" onClick={onStop} className="ui text-xs text-muted underline">stop</button>}
      </div>
      <p className="ui m-0 mt-1.5 text-sm text-ink" data-testid="guided-caption">
        {done ? (g.fellBackAt !== null ? <>Finished. Steps from {GUIDED_STEPS[g.fellBackAt].label} on are the recorded run{g.reason ? <span className="text-muted"> (live: {g.reason})</span> : null}.</> : <>Finished: all five steps ran live.</>)
          : GUIDED_STEPS[cur].caption}
      </p>
    </section>
  );
}
