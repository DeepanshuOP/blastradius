"use client";

import type { ReactNode } from "react";
import type { LabState, Stage } from "./types";

export const fmtMs = (ms: number | null | undefined) =>
  ms === null || ms === undefined ? "n/a" : ms < 1000 ? `${ms.toFixed(ms < 10 ? 1 : 0)} ms` : `${(ms / 1000).toFixed(ms < 10000 ? 2 : 1)} s`;
export const short = (s: string, n = 64) => (s.length <= n ? s : `${s.slice(0, n - 1)}…`);
export const sha = (s: string | undefined | null) => (s ? s.slice(0, 10) : "n/a");

/** Shortens the middle of a long id so its file and its test name both stay visible: `tests/te…::test_alt_salt`. */
export function midEllipsis(s: string, n = 56): string {
  if (s.length <= n) return s;
  const keepEnd = Math.ceil((n - 1) * 0.6);
  return `${s.slice(0, n - 1 - keepEnd)}…${s.slice(s.length - keepEnd)}`;
}

/** An id shortened in the middle, with the full id in a tooltip (and for screen readers). */
export function Id({ id, n = 56, className = "" }: { id: string; n?: number; className?: string }) {
  const s = midEllipsis(id, n);
  return <span className={`mono whitespace-nowrap ${className}`} title={s === id ? undefined : id} aria-label={s === id ? undefined : id}>{s}</span>;
}

/** Where a number on screen comes from: this run (LIVE), a recorded run (REPLAY), or the paper's dataset. */
export function Prov({ mode, className = "" }: { mode: LabState["mode"] | "bench"; className?: string }) {
  const m = { live: ["LIVE", "bg-green/15 text-green"], replay: ["REPLAY", "bg-amber/15 text-amber"], idle: ["", ""], bench: ["FROM BR-BENCH", "bg-blue/15 text-blue"] }[mode];
  if (!m[0]) return null;
  return <span className={`ui inline-block rounded px-1.5 py-0.5 text-2xs font-semibold tracking-wider ${m[1]} ${className}`}>{m[0]}</span>;
}

// ---- icons: one stroke family (1.75 px, round caps), drawn on a 16 px grid ----------------------------------------
const PATHS = {
  check: "M3.5 8.5l3 3 6-7",
  cross: "M4.5 4.5l7 7M11.5 4.5l-7 7",
  dot: "M8 8m-2.5 0a2.5 2.5 0 1 0 5 0a2.5 2.5 0 1 0 -5 0",
  ring: "M8 8m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0",
  minus: "M4.5 8h7",
  bolt: "M9 2.5L4 9h4l-1 4.5L12 7H8z",
  warn: "M8 3l5.5 10h-11zM8 7v2.5M8 11.5v.01",
  play: "M5.5 3.5v9l7-4.5z",
  pause: "M5.5 3.5v9M10.5 3.5v9",
  restart: "M3.5 8a4.5 4.5 0 1 0 1.4-3.3M3.5 3v2.5H6",
  close: "M4.5 4.5l7 7M11.5 4.5l-7 7",
  chevron: "M6 3.5l4.5 4.5L6 12.5",
  present: "M2.5 3.5h11v7h-11zM8 10.5v2.5M5.5 13h5",
  menu: "M3 4.5h10M3 8h10M3 11.5h10",
  target: "M8 8m-5.5 0a5.5 5.5 0 1 0 11 0a5.5 5.5 0 1 0 -11 0M8 8m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0",
  bug: "M5.5 6.5h5v4a2.5 2.5 0 0 1-5 0zM8 6.5v6.5M3 8.5h2.5M10.5 8.5H13M6 4.5l-1-1.5M10 4.5l1-1.5M3.5 12l2-1M12.5 12l-2-1",
} as const;
export type IconName = keyof typeof PATHS;

export function Icon({ name, className = "", title }: { name: IconName; className?: string; title?: string }) {
  return (
    <svg viewBox="0 0 16 16" width="1em" height="1em" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round"
      className={`inline-block shrink-0 ${className}`} role={title ? "img" : undefined} aria-hidden={title ? undefined : true} aria-label={title}>
      {title && <title>{title}</title>}
      <path d={PATHS[name]} fill={name === "dot" || name === "play" || name === "bolt" ? "currentColor" : "none"} />
    </svg>
  );
}

export type Tone = "pending" | "running" | "ok" | "failed" | "skipped" | "passed" | "changed" | "error";
const TONE: Record<Tone, { icon: IconName; color: string; label: string }> = {
  pending: { icon: "ring", color: "text-muted", label: "pending" },
  running: { icon: "dot", color: "text-blue br-pulse", label: "running" },
  ok: { icon: "check", color: "text-green", label: "done" },
  passed: { icon: "check", color: "text-green", label: "passed" },
  failed: { icon: "cross", color: "text-red", label: "failed" },
  error: { icon: "cross", color: "text-red", label: "error" },
  skipped: { icon: "minus", color: "text-muted", label: "skipped" },
  changed: { icon: "bolt", color: "text-accent", label: "changed" },
};

/** A state shown by icon AND colour AND (for screen readers, or with `text`) a word: colour is never the only signal. */
export function StatusIcon({ tone, text = false, className = "" }: { tone: Tone; text?: boolean; className?: string }) {
  const t = TONE[tone];
  return (
    <span className={`inline-flex items-center gap-1 ${t.color} ${className}`}>
      <Icon name={t.icon} />
      {text ? <span className="ui">{t.label}</span> : <span className="sr-only">{t.label}</span>}
    </span>
  );
}

export function Panel({ id, title, right, children, className = "", bodyClass = "p-3" }: { id?: string; title: ReactNode; right?: ReactNode; children: ReactNode; className?: string; bodyClass?: string }) {
  return (
    <section id={id} className={`min-w-0 rounded-md border border-rule bg-panel ${className}`} aria-label={typeof title === "string" ? title : undefined}>
      <header className="flex min-h-[40px] items-center justify-between gap-3 border-b border-rule px-3 py-2">
        <h3 className="ui m-0 text-sm font-semibold text-ink">{title}</h3>
        <div className="flex items-center gap-2">{right}</div>
      </header>
      <div className={bodyClass}>{children}</div>
    </section>
  );
}

/** An empty state that says what will appear here and when. */
export function Empty({ title, children }: { title?: ReactNode; children?: ReactNode }) {
  return (
    <div className="ui py-2">
      {title && <p className="m-0 text-sm font-medium text-ink">{title}</p>}
      {children && <p className="m-0 mt-0.5 text-sm text-muted">{children}</p>}
    </div>
  );
}

/** A failed stage: the error itself and what to do next. Never a blank panel. */
export function StageError({ what, reason, next }: { what: string; reason: ReactNode; next: ReactNode }) {
  return (
    <div className="ui rounded border border-red/60 bg-red/10 px-3 py-2" role="alert">
      <p className="m-0 flex items-center gap-1.5 text-sm font-semibold text-red"><Icon name="warn" />{what}</p>
      <p className="mono m-0 mt-1 text-xs text-ink">{reason}</p>
      <p className="m-0 mt-1 text-xs text-muted">Next: {next}</p>
    </div>
  );
}

/** Button vocabulary shared by every control on the lab. */
export const BTN = "ui inline-flex min-h-[30px] items-center gap-1.5 rounded border border-rule px-2.5 text-sm text-ink hover:border-muted disabled:cursor-not-allowed disabled:opacity-40";
export const BTN_PRIMARY = "ui inline-flex min-h-[30px] items-center gap-1.5 rounded bg-accent px-4 text-sm font-semibold text-white hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40";
export const SEG = (on: boolean) => `ui rounded px-2 py-0.5 text-xs ${on ? "bg-ink text-page" : "text-muted hover:text-ink"}`;

export const OUTCOME_COLOR: Record<string, string> = { passed: "bg-green", failed: "bg-red", error: "bg-red", skipped: "bg-muted" };

export const STAGE_LABEL: Record<Stage, string> = {
  meta: "run", repo: "Repo", graph: "Graph", change: "Change", impact: "Impact", tests: "Tests", arena: "Arena", triage: "Triage",
  repair: "Repair", validate: "Validate", report: "Report",
};

/** One-line summary of an event for the log. Ids are shortened in the middle; the full text is the line's tooltip. */
export function summarize(type: string, d: Record<string, unknown>, status: string): string {
  const g = (k: string) => d[k] as never;
  const counts = g("counts") as Record<string, number> | undefined;
  switch (type) {
    case "run.header": return `${g("mode")} run ${g("run_id")} · model ${g("model") ?? "none"} · ${g("llm")}`;
    case "run.end": return status === "ok" ? "run complete" : `run ended: ${g("reason")}`;
    case "repo.info": return status === "running" ? `preparing ${g("name")}` : `${g("name")} @ ${sha(g("commit"))} · ${g("language")} · ${g("n_files")} files · tests ${g("tests_runnable") ? "runnable" : `not runnable: ${g("reason")}`}`;
    case "graph.built": return status === "running" ? "building the code graph" : status === "failed" ? `graph failed: ${g("reason")}` : `${g("n_nodes")} nodes · ${g("n_edges")} edges · ${g("parse_failures")} parse failures${g("truncated") ? " · stream is a subset" : ""}`;
    case "change.applied": return `${(g("changed_files") as string[]).length} file(s) · ${(g("changed_nodes") as string[]).length} graph node(s) changed · head ${sha(g("head"))}`;
    case "impact.ranking": return `${g("ranker")} ranked ${g("n_test_files")} test files; top ${midEllipsis(((g("at_risk_files") as string[]) ?? [])[0] ?? "none", 44)}`;
    case "impact.paths": return `${((g("paths") as unknown[]) ?? []).length} paths · ${(g("reachability") as { n_reachable: number }).n_reachable} nodes reachable`;
    case "tests.start": return "running the suite, at-risk files first";
    case "test.result": return `${String(g("outcome"))} ${midEllipsis(String(g("id")), 52)} ${fmtMs(Number(g("duration_s")) * 1000)}`;
    case "tests.done": return status === "skipped" ? `not run: ${g("reason")}` : `${counts?.passed} passed · ${counts?.failed} failed of ${counts?.total} cases`;
    case "tests.race": return "race: risk-first against alphabetical";
    case "arena.coverage": return status === "running" ? "recording per-test coverage at the base commit" : status === "skipped" ? `coverage skipped: ${g("reason")}` : `coverage: ${g("n_tests")} tests · ${fmtMs(Number(g("wall_s")) * 1000)}${g("cached") ? " (cached)" : ""}`;
    case "arena.result": return `${((g("strategies") as unknown[]) ?? []).length} strategies compared on this run's results`;
    case "arena.repair": return status === "running" ? "repair arena: R1 log-only call" : status === "skipped" ? `repair arena skipped: ${g("reason")}` : "repair arena: R1, R2 and the unvalidated push compared";
    case "arena.probe": return status === "running" ? `suite strength: mutant ${g("i")}/${g("n")}` : `suite strength: ${g("caught")} caught, ${g("survived")} survived`;
    case "triage.result": return status === "skipped" ? `no triage: ${g("reason")}` : `mine ${counts?.mine} · inherited ${counts?.inherited} · flaky ${counts?.flaky}`;
    case "repair.chunks": return `${(g("chunks") as unknown[]).length} context chunk(s) chosen`;
    case "repair.request": return `attempt ${g("attempt")} to ${g("model")} · about ${g("prompt_tokens_estimate")} prompt tokens${g("cached") ? " · cached" : ""}`;
    case "repair.reply": return `reply · ${(g("usage") as { total_tokens?: number } | null)?.total_tokens ?? "?"} tokens · ${g("from_cache") ? "from cache" : "live call"}`;
    case "repair.blocks": return status === "ok" ? `${(g("blocks") as unknown[]).length} search/replace block(s) applied` : `blocks rejected: ${short(String(g("error")), 90)}`;
    case "repair.patch": return `patch for ${(g("files") as unknown[]).length} file(s)`;
    case "repair.skipped": return `repair skipped: ${g("reason")}`;
    case "repair.unavailable": return `repair unavailable (${g("kind")}): ${g("reason")}`;
    case "validate.check": return `${g("name")}: ${status === "running" ? "running" : g("ok") ? "ok" : status === "skipped" ? "skipped" : "failed"} · ${short(String(g("evidence")), 90)}`;
    case "validate.verdict": return status === "skipped" ? `not validated: ${g("reason")}` : g("accepted") ? "accepted: the full suite passed with the patch" : `rejected: ${g("note")}`;
    case "report.comment": return "PR comment rendered";
    case "report.summary": return "run summary";
    default: return type;
  }
}
