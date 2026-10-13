"use client";

import { Empty, Icon, Id, Prov, StatusIcon, fmtMs, short, type Tone } from "./common";
import type { AuditRecord, LabState, TestResult } from "./types";

/** Every value below is read from this run's events; nothing is typed in. */
export function ciView(s: LabState) {
  const lanes = s.tests.race?.lanes ?? [];
  const alpha = lanes.find((l) => l.name === "alphabetical") ?? null;
  const risk = lanes.find((l) => l.name === "risk-first") ?? null;
  const counts = (s.tests.done?.counts ?? {}) as Record<string, number>;
  const failed = Number(counts.failed ?? 0) + Number(counts.error ?? 0);
  const firstFail: TestResult | undefined = alpha?.first_failure_id
    ? s.tests.results.find((r) => r.id === alpha.first_failure_id && (r.outcome === "failed" || r.outcome === "error"))
    : undefined;
  const loc = s.events.filter((e) => e.type === "localize.result" && e.status === "ok").pop()?.data ?? null;
  const chunk = s.repair.chunks[0] ?? null;
  const paths = (s.impact.paths?.paths ?? []) as { test_file: string; path: string[]; length: number | null }[];
  const failingFiles = new Set(s.tests.results.filter((r) => r.outcome === "failed" || r.outcome === "error").map((r) => r.id.split("::")[0]));
  const path = paths.filter((p) => p.length !== null && failingFiles.has(p.test_file)).sort((a, b) => (a.length ?? 99) - (b.length ?? 99))[0] ?? null;
  const prRec = [...s.audit.records].reverse().find((r) => r.artifacts?.pr_url);
  const verdict = s.validate.verdict;
  return { alpha, risk, counts, failed, firstFail, loc, chunk, path, prRec, verdict };
}

function Stage({ name, tone, detail }: { name: string; tone: Tone; detail: string }) {
  const bg = tone === "ok" ? "border-green/60 bg-green/10" : tone === "failed" ? "border-red/70 bg-red/10" : "border-rule bg-panel2";
  return (
    <div className={`flex min-w-0 flex-1 flex-col items-center gap-1 rounded border px-2 py-2 text-center ${bg}`} data-ci-stage={name} data-tone={tone}>
      <span className="ui flex items-center gap-1.5 text-sm font-semibold"><StatusIcon tone={tone} />{name}</span>
      <span className="ui text-2xs text-muted">{detail}</span>
    </div>
  );
}

function Row({ k, children }: { k: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[9.5rem_1fr] gap-2 border-t border-rule py-1.5 first:border-t-0">
      <span className="ui text-xs text-muted">{k}</span><span className="ui min-w-0 text-sm">{children}</span>
    </div>
  );
}

export function CiVsBrPanel({ s, onDecisions }: { s: LabState; onDecisions?: () => void }) {
  if (!s.tests.done || !s.tests.race) return <Empty title="The comparison appears when the suite has finished." />;
  const v = ciView(s);
  const total = Number(v.counts.total ?? 0);
  const repoTone: Tone = s.stage.repo?.status === "ok" ? "ok" : s.stage.repo?.status === "failed" ? "failed" : "pending";
  const buildTone: Tone = s.repo?.tests_runnable ? "ok" : "failed";
  const testTone: Tone = v.failed > 0 ? "failed" : "ok";
  const tri = s.triage?.counts ?? {};
  const accepted = v.verdict?.accepted === true && v.verdict?.status === "ok";
  const runName = String(s.header?.run_id ?? "");
  const logHref = s.mode === "replay" && runName ? `/lab/runs/audit/${runName}.jsonl` : null;
  const verified = s.audit.verify?.ok === true;
  const excerpt = v.firstFail ? `FAILED ${v.firstFail.id}\n${v.firstFail.message || "(no message)"}` : "";
  return (
    <div className="space-y-3" data-testid="ci-vs-br">
      <div className="flex items-center gap-2"><Prov mode={s.mode} /><span className="ui text-xs text-muted">the same run, two readers: a CI server that runs everything and reports at the end, and BlastRadius</span></div>
      <div className="grid gap-3 lg:grid-cols-2">
        <section aria-label="CI server" className="rounded-md border border-rule bg-panel p-3" data-testid="ci-side">
          <h3 className="ui m-0 mb-2 flex items-center gap-2 text-sm font-semibold"><Icon name="dot" />CI server (Jenkins-style stage view)</h3>
          <div className="flex items-stretch gap-1.5">
            <Stage name="Checkout" tone={repoTone} detail={s.repo?.commit ? `@${String(s.repo.commit).slice(0, 7)}` : "n/a"} />
            <Stage name="Build" tone={buildTone} detail={s.repo?.tests_runnable ? "environment ready" : short(String(s.repo?.reason ?? "not runnable"), 30)} />
            <Stage name="Test" tone={testTone} detail={`${v.failed} of ${total} failed`} />
          </div>
          <div className="mt-3">
            <Row k="First failure">{v.alpha?.first_failure_position != null ? <>case <span className="num mono">{v.alpha.first_failure_position}</span> of <span className="num mono">{total}</span> (retest-all, alphabetical)</> : "none"}</Row>
            <Row k="Elapsed to verdict"><span className="num mono">{fmtMs(v.alpha?.total_ms ?? null)}</span> <span className="text-muted">the job reports when the whole suite has run</span></Row>
            <Row k="Raw log excerpt">{excerpt ? <pre className="mono m-0 max-h-40 overflow-auto whitespace-pre-wrap rounded bg-panel2 p-2 text-2xs" data-testid="ci-log">{short(excerpt, 700)}</pre> : <span className="text-muted">no failure</span>}</Row>
            <Row k="Next"><span className="font-semibold">developer reads the log</span></Row>
          </div>
          <p className="ui m-0 mt-2 text-2xs text-muted">{v.alpha?.basis}</p>
        </section>
        <section aria-label="BlastRadius" className="rounded-md border border-accent/60 bg-panel p-3" data-testid="br-side">
          <h3 className="ui m-0 mb-2 flex items-center gap-2 text-sm font-semibold"><Icon name="ring" />BlastRadius</h3>
          <Row k="First failure">{v.risk?.first_failure_position != null ? <>case <span className="num mono">{v.risk.first_failure_position}</span> of <span className="num mono">{total}</span> after <span className="num mono">{fmtMs(v.risk.elapsed_to_first_failure_ms)}</span> (risk-first)</> : "none"}</Row>
          <Row k="Triage">{s.triage && !s.triage.skipped ? <><span className="num mono">{tri.mine ?? 0}</span> mine · <span className="num mono">{tri.inherited ?? 0}</span> inherited · <span className="num mono">{tri.flaky ?? 0}</span> flaky</> : <span className="text-muted">{s.triage?.skipped || "not run"}</span>}</Row>
          <Row k="Localised line">
            {v.loc?.ranked?.[0] ? (
              <span data-testid="br-loc"><Id id={`${v.loc.ranked[0].file}:${v.loc.ranked[0].line ?? "?"}`} n={60} /> <span className="text-muted">({v.loc.ranked[0].node}, {v.loc.ranked[0].hops ?? "?"} hop(s))</span>
                {v.loc.paths?.[0]?.path?.length ? <span className="mono block text-2xs text-muted">{short(v.loc.paths[0].path.join(" → "), 160)}</span> : null}</span>
            ) : v.chunk ? (
              <span data-testid="br-loc"><Id id={`${v.chunk.file}:${v.chunk.focus}`} n={60} /> <span className="text-muted">({v.chunk.qualname})</span>
                {v.path ? <span className="mono block text-2xs text-muted">graph path: {short(v.path.path.join(" → "), 160)} ({v.path.length} hops)</span> : null}</span>
            ) : <span className="text-muted">no function localised</span>}
          </Row>
          <Row k="Fix">
            {v.prRec?.artifacts?.pr_url ? <a className="text-accent underline" href={v.prRec.artifacts.pr_url} target="_blank" rel="noreferrer" data-testid="br-pr">{v.prRec.artifacts.pr_url}</a>
              : accepted ? <span data-testid="br-fix">validated suggestion in the PR comment (all checks passed, {String(v.verdict?.attempts ?? "?")} attempt(s))</span>
              : <span className="text-muted">{s.repair.unavailable ? `no fix: model unavailable (${s.repair.unavailable.kind})` : s.repair.skipped ? `no fix: ${s.repair.skipped}` : "no validated fix"}</span>}
          </Row>
          <Row k="Decision log">
            {s.audit.records.length ? <span data-testid="br-log">
              <span className="num mono">{s.audit.records.length}</span> records · {verified ? <span className="text-green">chain verified</span> : s.audit.verify ? <span className="text-red">chain broken</span> : "not verified yet"}
              {onDecisions && <button type="button" onClick={onDecisions} className="ml-2 text-accent underline">open Decisions</button>}
              {logHref && <a href={logHref} className="ml-2 text-accent underline" target="_blank" rel="noreferrer">raw log</a>}
            </span> : <span className="text-muted">this recording has no decision log</span>}
          </Row>
          <Row k="Next"><span className="font-semibold">{v.prRec ? "review the fix PR" : accepted ? "review the suggestion" : "read the triage and the localised line"}</span></Row>
        </section>
      </div>
    </div>
  );
}

/** Decision records whose stage is one of `stages`. */
export const recordsOf = (recs: AuditRecord[], stages: string[]) => recs.filter((r) => stages.includes(r.stage));
