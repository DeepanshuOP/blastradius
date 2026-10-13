"use client";

import { useCallback, useEffect, useReducer, useRef, useState } from "react";
import type { Check, LabEvent, LabState, Stage, TestResult, TriageRow } from "./types";

export const initialState: LabState = {
  mode: "idle", running: false, error: null, events: [], header: null, stage: {}, repo: null, graph: null, change: null,
  impact: { ranking: null, paths: null },
  tests: { started: false, results: [], done: null, race: null },
  triage: null,
  repair: { chunks: [], requests: [], replies: [], blocks: [], patch: null, skipped: null, unavailable: null },
  validate: { checks: [], verdict: null }, report: { comment: null, summary: null },
  tokens: { prompt: 0, completion: 0, total: 0, cached: 0, calls: 0 }, startedAt: null, elapsedMs: 0,
};

type Action = { t: "reset" } | { t: "start"; mode: "live" | "replay" } | { t: "events"; evs: LabEvent[] } | { t: "end"; error?: string } | { t: "tick" };

export function applyEvent(s: LabState, ev: LabEvent): LabState {
  const d = ev.data;
  const stage = ev.stage === "meta" ? s.stage : {
    ...s.stage,
    [ev.stage]: ev.type === "test.result"
      ? { status: s.stage[ev.stage]?.status ?? "running", dur_ms: s.stage[ev.stage]?.dur_ms ?? 0 }
      : { status: ev.status, dur_ms: ev.dur_ms },
  };
  const n: LabState = { ...s, events: [...s.events, ev], stage };
  switch (ev.type) {
    case "run.header": n.header = d; break;
    case "run.end": if (ev.status === "failed") n.error = String(d.reason ?? "the run failed"); break;
    case "repo.info": n.repo = { ...(s.repo ?? {}), ...d }; break;
    case "graph.built": if (ev.status !== "running") n.graph = { ...(d as object), nodes: d.nodes ?? [], edges: d.edges ?? [] } as LabState["graph"]; break;
    case "change.applied": n.change = d; break;
    case "impact.ranking": n.impact = { ...s.impact, ranking: d }; break;
    case "impact.paths": n.impact = { ...s.impact, paths: d }; break;
    case "tests.start": n.tests = { ...s.tests, started: true }; break;
    case "test.result": n.tests = { ...s.tests, results: [...s.tests.results, d as TestResult] }; break;
    case "tests.done": n.tests = { ...s.tests, done: d }; break;
    case "tests.race": n.tests = { ...s.tests, race: d as never }; break;
    case "triage.result": n.triage = { rows: (d.rows ?? []) as TriageRow[], counts: d.counts ?? {}, model: d.model, failing_cases: d.failing_cases, unit: d.unit, skipped: ev.status === "skipped" ? String(d.reason ?? "") : undefined }; break;
    case "repair.chunks": n.repair = { ...s.repair, chunks: d.chunks ?? [] }; break;
    case "repair.request": n.repair = { ...s.repair, requests: [...s.repair.requests, d] }; break;
    case "repair.reply": {
      n.repair = { ...s.repair, replies: [...s.repair.replies, d] };
      if (d.tokens_so_far) n.tokens = d.tokens_so_far;
      break;
    }
    case "repair.blocks": n.repair = { ...s.repair, blocks: [...s.repair.blocks, d] }; break;
    case "repair.patch": n.repair = { ...s.repair, patch: d }; break;
    case "repair.skipped": n.repair = { ...s.repair, skipped: String(d.reason ?? "skipped") }; break;
    case "repair.unavailable": n.repair = { ...s.repair, unavailable: { kind: String(d.kind), reason: String(d.reason) } }; break;
    case "validate.check": {
      const c: Check = { attempt: d.attempt, name: d.name, status: ev.status, ok: d.ok, evidence: d.evidence };
      const rest = s.validate.checks.filter((x) => !(x.attempt === c.attempt && x.name === c.name));
      n.validate = { ...s.validate, checks: [...rest, c] };
      break;
    }
    case "validate.verdict": n.validate = { ...s.validate, verdict: { ...d, status: ev.status } }; break;
    case "report.comment": n.report = { ...s.report, comment: d.comment }; break;
    case "report.summary": n.report = { ...s.report, summary: d }; break;
  }
  return n;
}

function reducer(s: LabState, a: Action): LabState {
  switch (a.t) {
    case "reset": return initialState;
    case "start": return { ...initialState, mode: a.mode, running: true, startedAt: Date.now() };
    case "events": return a.evs.reduce(applyEvent, s);
    case "end": return { ...s, running: false, error: a.error ?? s.error };
    case "tick": return s.running && s.startedAt ? { ...s, elapsedMs: Date.now() - s.startedAt } : s;
  }
}

export type Quota = Record<string, { used: number; cap: number; ok: boolean; resume_after: string | null }>;
export type Availability = { checked: boolean; live: boolean; llm: boolean; reason: string; quota?: Quota | null };

/** The lab's state, the stream readers (live over SSE, replay from a recorded file) and the server's availability. */
export function useLab() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [avail, setAvail] = useState<Availability>({ checked: false, live: false, llm: false, reason: "" });
  const abort = useRef<AbortController | null>(null);
  const queue = useRef<LabEvent[]>([]);
  const raf = useRef<number | null>(null);

  const flush = useCallback(() => {
    raf.current = null;
    if (queue.current.length) {
      const evs = queue.current;
      queue.current = [];
      dispatch({ t: "events", evs });
    }
  }, []);
  const push = useCallback((ev: LabEvent) => {
    queue.current.push(ev);
    if (raf.current === null) raf.current = requestAnimationFrame(flush);
  }, [flush]);

  useEffect(() => {
    let alive = true;
    fetch("/api/lab/run", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((j: { live: boolean; llm: boolean; busy: boolean; quota: Quota | null }) => {
        if (alive) setAvail({ checked: true, live: j.live, llm: j.llm, quota: j.quota, reason: j.llm ? "" : "GROQ_API_KEY is not set on the server: runs go through triage and stop before repair." });
      })
      .catch(() => {
        if (alive) setAvail({ checked: true, live: false, llm: false, reason: "This is a static build with no Python server behind it, so live runs are unavailable. Recorded runs replay in the browser." });
      });
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    if (!state.running) return;
    const id = setInterval(() => dispatch({ t: "tick" }), 250);
    return () => clearInterval(id);
  }, [state.running]);

  const reset = useCallback(() => {
    abort.current?.abort();
    queue.current = [];
    dispatch({ t: "reset" });
  }, []);

  const startLive = useCallback(async (body: Record<string, unknown>) => {
    abort.current?.abort();
    const ac = new AbortController();
    abort.current = ac;
    queue.current = [];
    dispatch({ t: "start", mode: "live" });
    try {
      const r = await fetch("/api/lab/run", { method: "POST", body: JSON.stringify(body), signal: ac.signal, headers: { "Content-Type": "application/json" } });
      if (!r.ok || !r.body) {
        const j = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
        dispatch({ t: "end", error: `${j.error ?? "request failed"}${j.detail ? `: ${String(j.detail).slice(0, 300)}` : ""}` });
        return;
      }
      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i: number;
        while ((i = buf.indexOf("\n\n")) >= 0) {
          const chunk = buf.slice(0, i);
          buf = buf.slice(i + 2);
          if (chunk.startsWith("data: ")) {
            try { push(JSON.parse(chunk.slice(6)) as LabEvent); } catch { /* partial line */ }
          }
        }
      }
      flush();
      dispatch({ t: "end" });
    } catch (e) {
      flush();
      dispatch({ t: "end", error: ac.signal.aborted ? undefined : `connection lost: ${String(e)}` });
    }
  }, [push, flush]);

  /** Replay a recorded run in the browser from `/lab/runs/<name>.jsonl`, with its original relative timing. With
   * `fastUntil`, the events before that stage's first event arrive without waiting (the guided demo's fallback). */
  const startReplay = useCallback(async (name: string, speed = 1, fastUntil?: Stage) => {
    abort.current?.abort();
    const ac = new AbortController();
    abort.current = ac;
    queue.current = [];
    dispatch({ t: "start", mode: "replay" });
    try {
      const r = await fetch(`/lab/runs/${name}.jsonl`, { cache: "no-store", signal: ac.signal });
      if (!r.ok) throw new Error(`recorded run ${name}: HTTP ${r.status}`);
      const evs = (await r.text()).split("\n").filter((l) => l.trim()).map((l) => ({ ...(JSON.parse(l) as LabEvent), replay: true }));
      let prev: number | null = null;
      let fast = Boolean(fastUntil && evs.some((e) => e.stage === fastUntil));
      for (const ev of evs) {
        if (ac.signal.aborted) return;
        if (fast && ev.stage === fastUntil) fast = false;
        const t = Date.parse(ev.ts);
        if (prev !== null && !fast) {
          const wait = Math.min(Math.max(t - prev, 0) / speed, 4000 / speed);
          if (wait > 8) await new Promise((res) => setTimeout(res, wait));
        }
        prev = t;
        push(ev);
      }
      flush();
      dispatch({ t: "end" });
    } catch (e) {
      if (!ac.signal.aborted) dispatch({ t: "end", error: String(e) });
    }
  }, [push, flush]);

  useEffect(() => () => { abort.current?.abort(); if (raf.current) cancelAnimationFrame(raf.current); }, []);

  return { state, avail, startLive, startReplay, reset };
}
