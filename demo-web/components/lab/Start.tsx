"use client";

import type { ReactNode } from "react";
import { Icon } from "./common";
import { Info } from "./Info";
import { ReplayChips, type Change, type RunInfo, type Scenario } from "./Picker";

/** A short phrase for what will run: the repository and the change. */
export function runSummary(scenario: Scenario, change: Change): string {
  if (!scenario) return "";
  const where = scenario.kind === "repo" ? scenario.name : scenario.kind === "replay" ? scenario.name
    : scenario.url.replace("https://github.com/", "").replace("/pull/", " #");
  if (scenario.kind === "pr") return `${where} · its own diff`;
  if (!change) return where;
  const what = change.kind === "inject" ? `${change.operator} in ${change.function.split(".").slice(-1)[0]}`
    : change.kind === "edit" ? `edit of ${change.file.split("/").slice(-1)[0]}` : change.id;
  return `${where} · ${what}`;
}

/** The three steps as a header strip: pick, break, run. The current one is lit, the finished ones are ticked. */
export function Steps({ stage }: { stage: 1 | 2 | 3 | 4 }) {
  const items = ["Pick a repo", "Break it", "Run"];
  return (
    <ol className="m-0 flex list-none items-center gap-2 p-0" aria-label="Steps">
      {items.map((t, k) => {
        const done = stage > k + 1, cur = stage === k + 1;
        return (
          <li key={t} className="flex items-center gap-2" aria-current={cur ? "step" : undefined}>
            {k > 0 && <span className="h-px w-6 bg-rule" aria-hidden="true" />}
            <span className={`ui grid h-7 w-7 place-items-center rounded-full text-sm font-bold ${done ? "bg-green text-white" : cur ? "bg-accent text-white" : "border border-rule text-muted"}`}>
              {done ? <Icon name="check" /> : k + 1}
            </span>
            <span className={`ui text-md font-semibold ${cur ? "text-ink" : done ? "text-ink" : "text-muted"}`}>{t}</span>
          </li>
        );
      })}
    </ol>
  );
}

/** Step 3: one large button, what it will run, the options and the recorded scenarios as Replay chips. */
export function RunPanel({ scenario, change, running, canRun, why, onRun, runs, onReplay, children, extra, stageLabel }: {
  scenario: Scenario; change: Change; running: boolean; canRun: boolean; why: string; onRun: () => void;
  runs: RunInfo[]; onReplay: (name: string) => void; children?: ReactNode; extra?: ReactNode; stageLabel?: string;
}) {
  const summary = runSummary(scenario, change);
  return (
    <div className="flex flex-col gap-3">
      <button type="button" onClick={onRun} disabled={!canRun || running}
        className="ui flex min-h-[72px] w-full items-center justify-center gap-3 rounded-lg bg-accent px-4 text-2xl font-bold text-white shadow-[0_6px_20px_rgb(var(--accent-rgb)/0.35)] hover:brightness-110 disabled:cursor-not-allowed disabled:bg-panel2 disabled:text-muted disabled:shadow-none">
        <Icon name="play" className="text-2xl" />{running ? (stageLabel ?? "Running") : "Run"}
      </button>
      <p className="ui m-0 min-h-[20px] truncate text-center text-sm" title={summary || why}>
        {canRun && summary ? <span className="mono">{summary}</span> : <span className="text-muted">{why}</span>}
      </p>
      {extra}
      {children}
      <div>
        <p className="ui m-0 mb-1 flex items-center gap-1.5 text-xs text-muted">Recorded runs
          <Info label="About recorded runs"><span className="block">A recorded run replays event by event with its original timing. Nothing is computed in this session, and it adds nothing to the scoreboard.</span></Info>
        </p>
        <ReplayChips runs={runs} disabled={running} onReplay={onReplay} />
      </div>
    </div>
  );
}
