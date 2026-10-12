"use client";

import type { ReactNode } from "react";
import type { LabState, Stage } from "./types";

export const fmtMs = (ms: number | null | undefined) =>
  ms === null || ms === undefined ? "n/a" : ms < 1000 ? `${ms.toFixed(ms < 10 ? 1 : 0)} ms` : `${(ms / 1000).toFixed(ms < 10000 ? 2 : 1)} s`;
export const short = (s: string, n = 64) => (s.length <= n ? s : `${s.slice(0, n - 1)}…`);
export const sha = (s: string | undefined | null) => (s ? s.slice(0, 10) : "n/a");

/** Where a number on screen comes from: this run (LIVE), a recorded run (REPLAY), or the paper's dataset. */
export function Prov({ mode, className = "" }: { mode: LabState["mode"] | "bench"; className?: string }) {
  const m = { live: ["LIVE", "bg-green/15 text-green"], replay: ["REPLAY", "bg-amber/15 text-amber"], idle: ["", ""], bench: ["FROM BR-BENCH", "bg-blue/15 text-blue"] }[mode];
  if (!m[0]) return null;
  return <span className={`ui inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold tracking-wider ${m[1]} ${className}`}>{m[0]}</span>;
}

export function Panel({ id, title, right, children, className = "" }: { id?: string; title: ReactNode; right?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section id={id} className={`min-w-0 rounded-md border border-rule bg-panel ${className}`}>
      <header className="flex items-center justify-between gap-3 border-b border-rule px-3 py-2">
        <h3 className="ui m-0 text-[13px] font-semibold uppercase tracking-wide text-muted">{title}</h3>
        <div className="flex items-center gap-2">{right}</div>
      </header>
      <div className="p-3">{children}</div>
    </section>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <p className="ui m-0 text-[13px] text-muted">{children}</p>;
}

export const OUTCOME_COLOR: Record<string, string> = { passed: "bg-green", failed: "bg-red", error: "bg-red", skipped: "bg-muted" };

export const STAGE_LABEL: Record<Stage, string> = {
  meta: "run", repo: "Repo", graph: "Graph", change: "Change", impact: "Impact", tests: "Tests", triage: "Triage",
  repair: "Repair", validate: "Validate", report: "Report",
};

/** One-line summary of an event for the log. */
export function summarize(type: string, d: Record<string, unknown>, status: string): string {
  const g = (k: string) => d[k] as never;
  switch (type) {
    case "run.header": return `${g("mode")} run ${g("run_id")} · model ${g("model") ?? "none"} · ${g("llm")}`;
    case "run.end": return status === "ok" ? "run complete" : `run ended: ${g("reason")}`;
    case "repo.info": return status === "running" ? `preparing ${g("name")}` : `${g("name")} @ ${sha(g("commit"))} · ${g("language")} · ${g("n_files")} files · tests ${g("tests_runnable") ? "runnable" : `not runnable: ${g("reason")}`}`;
    case "graph.built": return status === "running" ? "building the code graph" : status === "failed" ? `graph failed: ${g("reason")}` : `${g("n_nodes")} nodes · ${g("n_edges")} edges · ${g("parse_failures")} parse failures${g("truncated") ? " · stream is a subset" : ""}`;
    case "change.applied": return `${(g("changed_files") as string[]).length} file(s) · ${(g("changed_nodes") as string[]).length} graph node(s) changed · head ${sha(g("head"))}`;
    case "impact.ranking": return `${g("ranker")} ranked ${g("n_test_files")} test files; top: ${((g("at_risk_files") as string[]) ?? [])[0] ?? "none"}`;
    case "impact.paths": return `${((g("paths") as unknown[]) ?? []).length} paths · ${(g("reachability") as { n_reachable: number }).n_reachable} nodes reachable`;
    case "tests.start": return "running the suite, at-risk files first";
    case "test.result": return `${String(g("outcome")).toUpperCase()} ${short(String(g("id")), 70)} ${fmtMs(Number(g("duration_s")) * 1000)}`;
    case "tests.done": return status === "skipped" ? `not run: ${g("reason")}` : `${(g("counts") as { passed: number; failed: number; total: number }).passed} passed · ${(g("counts") as { failed: number }).failed} failed of ${(g("counts") as { total: number }).total} cases`;
    case "tests.race": return "race: risk-first vs alphabetical";
    case "triage.result": return status === "skipped" ? `no triage: ${g("reason")}` : `mine ${(g("counts") as Record<string, number>).mine} · inherited ${(g("counts") as Record<string, number>).inherited} · flaky ${(g("counts") as Record<string, number>).flaky}`;
    case "repair.chunks": return `${(g("chunks") as unknown[]).length} context chunk(s) chosen`;
    case "repair.request": return `attempt ${g("attempt")} → ${g("model")} · ~${g("prompt_tokens_estimate")} prompt tokens${g("cached") ? " · cached" : ""}`;
    case "repair.reply": return `reply · ${(g("usage") as { total_tokens?: number } | null)?.total_tokens ?? "?"} tokens · ${g("from_cache") ? "from cache" : "live call"}`;
    case "repair.blocks": return status === "ok" ? `${(g("blocks") as unknown[]).length} search/replace block(s) applied` : `blocks rejected: ${short(String(g("error")), 90)}`;
    case "repair.patch": return `patch for ${(g("files") as unknown[]).length} file(s)`;
    case "repair.skipped": return `repair skipped: ${g("reason")}`;
    case "repair.unavailable": return `repair unavailable (${g("kind")}): ${g("reason")}`;
    case "validate.check": return `${g("name")}: ${status === "running" ? "running" : g("ok") ? "ok" : status === "skipped" ? "skipped" : "FAILED"} · ${short(String(g("evidence")), 90)}`;
    case "validate.verdict": return status === "skipped" ? `not validated: ${g("reason")}` : g("accepted") ? "ACCEPTED: the full suite passed with the patch" : `REJECTED: ${g("note")}`;
    case "report.comment": return "PR comment rendered";
    case "report.summary": return "run summary";
    default: return type;
  }
}
