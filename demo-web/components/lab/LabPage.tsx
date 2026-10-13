"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ArenaPanel } from "./Arena";
import { ChallengeCard } from "./Challenge";
import { InjectMenu, ProbePanel, TestGapPanel, useProbe } from "./BreakIt";
import { CodePanel } from "./CodePanel";
import { BTN, BTN_PRIMARY, Drawer, Icon, Panel, Prov, StatusIcon, type Tone } from "./common";
import { GraphView, type GraphHandle } from "./GraphView";
import { ExplainContext, Info } from "./Info";
import { EventLog, Ticker } from "./Log";
import { NodeCard } from "./NodeDetails";
import { GUIDED_IDLE, GUIDED_RECORDING, GUIDED_REPO, GUIDED_SEED, GUIDED_STEPS, GuidedStepper, liveFailure, stepMs, stepTone, type Guided, type StepRecord } from "./GuidedDemo";
import { ImpactPanel, RacePanel, RepairPanel, TriagePanel, VerdictPanel, stageFailure, type RecordedRepair } from "./Panels";
import { ChangePicker, RepoCards, type Change, type RepoInfo, type RunInfo, type Scenario } from "./Picker";
import { Presenter } from "./Presenter";
import { PipelineRail } from "./Rail";
import { IntegrityPanel, ReportPanel } from "./Report";
import { GlanceCard, MetaCard } from "./ReviewCards";
import { importantNodes, reachCounts, sizeByReach } from "./reach";
import { useSessionTally } from "./Scoreboard";
import { RunPanel, Steps } from "./Start";
import { TopBar } from "./TopBar";
import type { GEdge, GNode, GraphDoc, LabState, Stage } from "./types";
import { useLab } from "./useLab";

const MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"];

export type TabId = "impact" | "race" | "arena" | "triage" | "repair" | "verdict" | "comment" | "integrity";
export const RESULT_TABS: { id: TabId; label: string; stages: Stage[] }[] = [
  { id: "impact", label: "Impact", stages: ["repo", "graph", "change", "impact"] },
  { id: "race", label: "Test race", stages: ["tests"] },
  { id: "arena", label: "Strategy arena", stages: ["arena"] },
  { id: "triage", label: "Triage", stages: ["triage"] },
  { id: "repair", label: "Repair", stages: ["repair", "validate"] },
  { id: "verdict", label: "Verdict", stages: ["report"] },
  { id: "comment", label: "PR comment", stages: [] },
  { id: "integrity", label: "Integrity", stages: [] },
];
export const tabOf = (st: Stage): TabId => RESULT_TABS.find((t) => t.stages.includes(st))?.id ?? "impact";

function tabTone(s: LabState, t: { id: TabId; stages: Stage[] }): Tone | null {
  if (t.id === "comment") return s.report.comment ? "ok" : "pending";
  if (t.stages.length === 0) return null;
  const xs = t.stages.map((k) => s.stage[k]?.status).filter(Boolean);
  if (!xs.length) return "pending";
  return xs.includes("failed") ? "failed" : xs.includes("running") ? "running" : xs.every((x) => x === "skipped") ? "skipped" : "ok";
}

/** Maps a result's canonical id onto graph test nodes (file + function name, parameters stripped). */
export function outcomeMap(nodes: GNode[], results: { id: string; outcome: string }[]): Record<string, "passed" | "failed"> {
  const byKey = new Map<string, string[]>();
  nodes.forEach((n) => {
    if (n.type === "test") {
      const k = `${n.file}::${n.label.replace(/^\./, "").replace(/\(\)$/, "")}`;
      (byKey.get(k) ?? byKey.set(k, []).get(k)!).push(n.id);
    }
  });
  const fileNode = new Map(nodes.filter((n) => n.type === "file").map((n) => [n.file, n.id]));
  const out: Record<string, "passed" | "failed"> = {};
  const mark = (id: string, failed: boolean) => { if (failed || out[id] === undefined) out[id] = failed ? "failed" : "passed"; };
  results.forEach((r) => {
    const parts = r.id.split("::");
    const failed = r.outcome === "failed" || r.outcome === "error";
    const name = parts[parts.length - 1].replace(/\[.*$/, "");
    byKey.get(`${parts[0]}::${name}`)?.forEach((id) => mark(id, failed));
    const f = fileNode.get(parts[0]);
    if (f) mark(f, failed);
  });
  return out;
}

export function useGraphDoc(url: string | null): { doc: GraphDoc | null; error: string | null } {
  const [doc, setDoc] = useState<GraphDoc | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    setDoc(null); setError(null);
    if (!url) return;
    let alive = true;
    fetch(url).then(async (r) => (r.ok ? r.json() : Promise.reject(new Error((await r.json().catch(() => ({}))).error ?? `HTTP ${r.status}`))))
      .then((j: GraphDoc) => alive && setDoc(j)).catch((e) => alive && setError(String(e.message ?? e)));
    return () => { alive = false; };
  }, [url]);
  return { doc, error };
}

/** The run's graph, the derived highlights (paths, at-risk files, outcomes) and the selection. */
export function useRunGraph(s: LabState, preview: GraphDoc | null) {
  const [full, setFull] = useState<GraphDoc | null>(null);
  useEffect(() => { setFull(null); }, [s.startedAt]);
  const runGraph: GraphDoc | null = full ?? (s.graph && s.graph.nodes.length ? (s.graph as GraphDoc) : preview);
  const nodes = useMemo(() => runGraph?.nodes ?? [], [runGraph]);
  const edges: GEdge[] = useMemo(() => runGraph?.edges ?? [], [runGraph]);
  const outcomes = useMemo(() => outcomeMap(nodes, s.tests.results), [nodes, s.tests.results.length]); // eslint-disable-line react-hooks/exhaustive-deps
  const paths = useMemo(() => ((s.impact.paths?.paths ?? []) as { path: string[] }[]).map((p) => p.path).filter((p) => p.length > 1), [s.impact.paths]);
  const atRisk = useMemo(() => {
    const files = new Set<string>((s.impact.ranking?.at_risk_files ?? []) as string[]);
    return nodes.filter((n) => n.type === "file" && files.has(n.file)).map((n) => n.id);
  }, [nodes, s.impact.ranking]);
  const changed = useMemo(() => (s.change?.changed_nodes as string[] | undefined) ?? [], [s.change]);
  const loadFull = async () => {
    const id = s.graph?.graph_id;
    if (!id) return;
    for (const u of [`/api/lab/graph?run=${id}`, `/lab/runs/${id}.graph.json`]) {
      try { const r = await fetch(u); if (r.ok) { setFull((await r.json()) as GraphDoc); return; } } catch { /* try next */ }
    }
  };
  return { runGraph, nodes, edges, outcomes, paths, atRisk, changed, full, loadFull };
}

type Filter = "file" | "class" | "function" | "test" | "passed" | "failed";
const LEGEND: { k: Filter; label: string; swatch: React.ReactNode }[] = [
  { k: "file", label: "file", swatch: <span className="inline-block h-2.5 w-3 rounded-sm bg-blue" /> },
  { k: "class", label: "class", swatch: <span className="inline-block h-2.5 w-2.5 rotate-45 bg-amber" /> },
  { k: "function", label: "function", swatch: <span className="inline-block h-2.5 w-2.5 rounded-full bg-muted" /> },
  { k: "test", label: "test", swatch: <span className="inline-block h-2.5 w-2.5 rounded-full border-2 border-green" /> },
  { k: "passed", label: "passed", swatch: <StatusIcon tone="passed" /> },
  { k: "failed", label: "failed", swatch: <StatusIcon tone="failed" /> },
];

/** Legend chips that are also the filters: a chip that is off hides that kind of node. */
export function GraphFilters({ hidden, toggle, counts }: { hidden: Filter[]; toggle: (k: Filter) => void; counts: Partial<Record<Filter, number>> }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label="Graph filters">
      {LEGEND.map((x) => {
        const off = hidden.includes(x.k);
        return (
          <button key={x.k} type="button" onClick={() => toggle(x.k)} aria-pressed={!off}
            className={`ui inline-flex min-h-[26px] items-center gap-1.5 rounded-full border px-2 text-xs ${off ? "border-rule text-muted line-through opacity-60" : "border-rule text-ink hover:border-muted"}`}>
            {x.swatch}{x.label}{counts[x.k] !== undefined && <span className="num text-muted">{counts[x.k]}</span>}
          </button>
        );
      })}
      <span className="ui inline-flex items-center gap-1 text-xs text-accent"><Icon name="bolt" />changed</span>
    </div>
  );
}

/** The recorded run whose repair stands in for this run's: the same change when one was recorded (its description
 * names the task, or the function and operator), otherwise a recording of the same repository whose repair ran
 * (for itsdangerous, the guided demo's validated repair). */
export function recordedRepairFor(s: LabState, runs: RunInfo[]): RecordedRepair | null {
  const cands = runs.filter((r) => r.model);
  if (!cands.length) return null;
  const src = (s.change?.source ?? {}) as Record<string, unknown>;
  const text = (r: RunInfo) => `${r.name} ${r.title ?? ""} ${r.description ?? ""}`;
  const exact = cands.find((r) => (src.task_id && text(r).includes(String(src.task_id)))
    || (src.function && src.operator && text(r).includes(String(src.function)) && text(r).includes(String(src.operator))));
  const repo = String(s.repo?.name ?? "");
  const repaired = cands.filter((r) => !/no model call/i.test(text(r)));   // recordings whose repair actually ran
  const pick = exact ?? (repo === GUIDED_REPO ? repaired.find((r) => r.name === GUIDED_RECORDING) : undefined)
    ?? repaired.find((r) => repo && text(r).includes(repo)) ?? repaired[0] ?? cands[0];
  return { name: pick.name, title: pick.title ?? pick.name, date: pick.date ?? "", exact: Boolean(exact) };
}

export default function LabPage() {
  const { state: s, avail, startLive, startReplay, reset } = useLab();
  const [repos, setRepos] = useState<RepoInfo[] | null>(null);
  const [runs, setRuns] = useState<RunInfo[]>([]);
  const [scenario, setScenario] = useState<Scenario>(null);
  const [change, setChange] = useState<Change>(null);
  const [model, setModel] = useState(MODELS[0]);
  const [repairArena, setRepairArena] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [logOpen, setLogOpen] = useState(false);
  const [otherOpen, setOtherOpen] = useState(false);
  const [waveKey, setWaveKey] = useState(0);
  const [tab, setTab] = useState<TabId>("impact");
  const [presenting, setPresenting] = useState(false);
  const [explain, setExplain] = useState(false);
  const [challenge, setChallenge] = useState(false);
  const [hidden, setHidden] = useState<Filter[]>([]);
  const [ctx, setCtx] = useState<{ id: string; x: number; y: number } | null>(null);
  const { probe, startProbe, clearProbe } = useProbe();
  const fixRuns = useRef<Set<number>>(new Set());          // runs started by the challenge's "Fix it": their bug is already counted
  const fixPending = useRef(false);
  useEffect(() => { if (fixPending.current && s.startedAt) { fixRuns.current.add(s.startedAt); fixPending.current = false; } }, [s.startedAt]);
  const tally = useSessionTally(s, fixRuns.current);
  const lastReplay = useRef<{ name: string; speed: number } | null>(null);
  const pinnedAt = useRef<Stage | null>(null);
  const graphRef = useRef<GraphHandle>(null);
  const results = useRef<HTMLDivElement>(null);
  const holdTab = useRef<TabId | null>(null);           // a tab the reader asked for that the running stage must not move
  const [guided, setGuided] = useState<Guided>(GUIDED_IDLE);

  useEffect(() => {
    let alive = true;
    fetch("/lab/runs/index.json", { cache: "no-store" }).then((r) => (r.ok ? r.json() : [])).then((j: RunInfo[]) => alive && setRuns(j)).catch(() => undefined);
    if (avail.live) {
      fetch("/api/lab/repos").then((r) => r.json()).then((j: { repos: RepoInfo[]; runs: RunInfo[] }) => {
        if (!alive) return;
        setRepos(j.repos);
        if (j.runs.length) setRuns(j.runs);
      }).catch(() => alive && setRepos([]));
    }
    return () => { alive = false; };
  }, [avail.live]);

  const idle = s.mode === "idle";
  const previewUrl = !idle ? null : scenario?.kind === "repo" ? `/api/lab/graph?repo=${scenario.name}` : scenario?.kind === "replay" ? `/lab/runs/${scenario.name}.graph.json` : null;
  const preview = useGraphDoc(previewUrl);
  const g = useRunGraph(s, preview.doc);
  useEffect(() => { setSelected(null); setTab(holdTab.current ?? "impact"); pinnedAt.current = null; }, [s.startedAt]);

  const changeEv = useMemo(() => s.events.find((e) => e.type === "change.applied"), [s.events]);
  useEffect(() => { if (changeEv) setWaveKey(changeEv.seq); }, [changeEv]);

  // the active tab follows the running stage, unless the reader picked a tab while that stage was running
  const runningStage = useMemo(() => [...s.events].reverse().find((e) => e.stage !== "meta")?.stage ?? null, [s.events]);
  useEffect(() => {
    if (!runningStage || holdTab.current) return;
    if (pinnedAt.current && pinnedAt.current === runningStage) return;
    pinnedAt.current = null;
    setTab(tabOf(runningStage));
  }, [runningStage]);
  const pick = (t: TabId) => { setTab(t); pinnedAt.current = runningStage; holdTab.current = null; };
  const pickStage = (st: Stage) => { pick(tabOf(st)); results.current?.scrollIntoView({ behavior: "smooth", block: "start" }); };

  const reach = useMemo(() => reachCounts(g.nodes, g.edges), [g.nodes, g.edges]);
  const sizeBy = useMemo(() => sizeByReach(reach, g.nodes), [reach, g.nodes]);
  const important = useMemo(() => importantNodes(g.nodes, reach), [g.nodes, reach]);
  const hiddenTypes = hidden.filter((k) => ["file", "class", "function", "test"].includes(k));
  const hiddenIds = useMemo(() => {
    const out: string[] = [];
    if (hidden.includes("passed")) Object.entries(g.outcomes).forEach(([id, o]) => { if (o === "passed") out.push(id); });
    if (hidden.includes("failed")) Object.entries(g.outcomes).forEach(([id, o]) => { if (o === "failed") out.push(id); });
    return out;
  }, [hidden, g.outcomes]);
  const typeCounts = useMemo(() => {
    const c: Partial<Record<Filter, number>> = {};
    g.nodes.forEach((n) => { c[n.type as Filter] = (c[n.type as Filter] ?? 0) + 1; });
    const o = Object.values(g.outcomes);
    if (o.length) { c.passed = o.filter((x) => x === "passed").length; c.failed = o.filter((x) => x === "failed").length; }
    return c;
  }, [g.nodes, g.outcomes]);
  const hops = (s.impact.paths?.reachability?.hops ?? {}) as Record<string, number>;
  const tooltipOf = useCallback((id: string) => {
    const n = g.nodes.find((x) => x.id === id);
    if (!n) return [];
    const r = reach.count[id] ?? 0;
    return [n.label.replace(/^\./, ""), `${n.type} · ${n.file}${n.line ? `:${n.line}` : ""}`,
      n.type === "test" ? "a test" : `reached by ${r} test${r === 1 ? "" : "s"}`,
      ...(hops[id] !== undefined ? [hops[id] === 0 ? "the changed code" : `${hops[id]} hop${hops[id] === 1 ? "" : "s"} from the change`] : [])];
  }, [g.nodes, reach, hops]);

  const sel = g.nodes.find((n) => n.id === selected) ?? null;
  const repoName = (s.repo?.prepared ? s.repo.name : null) ?? (scenario?.kind === "repo" ? scenario.name : null);
  const q = avail.quota?.[model];
  const quotaReason = q && !q.ok ? `the daily token quota of ${model} is used up (${q.used.toLocaleString()} of ${q.cap.toLocaleString()} tokens in the last 24 h, E3 and lab ledgers together)${q.resume_after ? `; the next call is possible after ${q.resume_after.replace("T", " ")} UTC` : ""}` : "";
  const modelOk = avail.llm && !quotaReason;
  const canRun = scenario !== null && (scenario.kind === "replay" || scenario.kind === "pr" || change !== null) && !s.running && (scenario.kind === "replay" || avail.live);
  const breakable = (n: GNode | undefined | null) => Boolean(n && n.type === "function" && repoName && avail.live && !s.running && !n.is_test_file);
  const why = s.running ? "Running…" : !scenario ? "Pick a repo first" : !avail.live && scenario.kind !== "replay" ? "Live runs need the local server" : scenario.kind !== "replay" && scenario.kind !== "pr" && !change ? "Click a function to break it" : "";
  const stage: 1 | 2 | 3 | 4 = s.events.length ? 4 : !scenario ? 1 : scenario.kind === "pr" || scenario.kind === "replay" || change ? 3 : 2;

  /** Start a live run of `ch` on `sc`. */
  const launch = useCallback((sc: NonNullable<Scenario>, ch: Change, opts?: { noLlm?: boolean }) => {
    if (sc.kind === "replay") return;
    lastReplay.current = null;
    holdTab.current = null;
    const body: Record<string, unknown> = { model, ...(sc.kind === "repo" ? { repo: sc.name } : sc.kind === "pr" ? { pr: sc.url } : { url: sc.url }) };
    if (ch?.kind === "task") Object.assign(body, { task: ch.id, variant: ch.variant });
    if (ch?.kind === "inject") body.inject = { file: ch.file, function: ch.function, operator: ch.operator, ...(ch.line ? { line: ch.line } : {}) };
    if (ch?.kind === "edit") body.edit = { file: ch.file, text: ch.text };
    if (!avail.llm || opts?.noLlm) body.noLlm = true;
    if (repairArena && modelOk && !opts?.noLlm) body.repairArena = true;
    startLive(body);
  }, [model, avail.llm, repairArena, modelOk, startLive]);

  const run = useCallback(() => {
    if (!scenario) return;
    setGuided(GUIDED_IDLE); holdTab.current = null;
    if (scenario.kind === "replay") {
      lastReplay.current = { name: scenario.name, speed: Number(new URLSearchParams(window.location.search).get("speed")) || 1 };
      startReplay(lastReplay.current.name, lastReplay.current.speed);
      return;
    }
    if (scenario.kind !== "pr" && !change) return;
    launch(scenario, change);
  }, [scenario, change, launch, startReplay]);

  const replay = useCallback((name: string) => {
    setGuided(GUIDED_IDLE); holdTab.current = null;
    setScenario({ kind: "replay", name });
    setChange(null);
    lastReplay.current = { name, speed: Number(new URLSearchParams(window.location.search).get("speed")) || 1 };
    startReplay(name, lastReplay.current.speed);
  }, [startReplay]);

  /** Play a recorded run from its repair stage on, labelled REPLAY, and keep the Repair tab in front. */
  const playRecorded = useCallback((name: string) => {
    setGuided(GUIDED_IDLE);
    setScenario({ kind: "replay", name }); setChange(null);
    lastReplay.current = { name, speed: 1 };
    holdTab.current = "repair"; setTab("repair");
    startReplay(name, 1, "repair");
  }, [startReplay]);
  const recorded = useMemo(() => (s.mode === "live" ? recordedRepairFor(s, runs) : null), [s.mode, s.change, s.repo, runs]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---- guided demo: itsdangerous, seed 7, end to end; a live step that fails hands over to the recording ----
  const fallBack = useCallback((at: number, reason: string, live: StepRecord[]) => {
    setGuided((g) => ({ ...g, phase: "running", fellBackAt: at, reason: reason.slice(0, 70), live }));
    setScenario({ kind: "replay", name: GUIDED_RECORDING }); setChange(null);
    lastReplay.current = { name: GUIDED_RECORDING, speed: 1 };
    holdTab.current = null;
    startReplay(GUIDED_RECORDING, 1, at > 0 ? GUIDED_STEPS[at].stages[0] : undefined);
  }, [startReplay]);
  const runFullDemo = useCallback(async () => {
    holdTab.current = null;
    setChallenge(false);
    setGuided({ ...GUIDED_IDLE, phase: "running" });
    if (!avail.live) { fallBack(0, "no local server", []); return; }
    let c: { file: string; function: string; operator: string; line: number } | null = null;
    try {
      const r = await fetch(`/api/lab/challenge?repo=${GUIDED_REPO}&seed=${GUIDED_SEED}`);
      if (r.ok) c = await r.json();
    } catch { /* falls back below */ }
    if (!c) { fallBack(0, `seed ${GUIDED_SEED} could not be resolved`, []); return; }
    setGuided((g) => ({ ...g, pick: `seed ${GUIDED_SEED}: ${c!.operator} in ${c!.function}` }));
    const sc = { kind: "repo", name: GUIDED_REPO } as NonNullable<Scenario>;
    const ch: Change = { kind: "inject", file: c.file, function: c.function, operator: c.operator, line: c.line };
    setScenario(sc); setChange(ch);
    launch(sc, ch, { noLlm: !modelOk });
  }, [avail.live, fallBack, launch, modelOk]);
  useEffect(() => {
    if (guided.phase !== "running" || s.running || !s.startedAt) return;
    if (guided.fellBackAt === null && s.mode === "live" && (s.events.length || s.error)) {
      const f = liveFailure(s);
      if (f === null) { setGuided((g) => ({ ...g, phase: "done" })); return; }
      const why = s.repair.unavailable?.reason ?? s.repair.skipped ?? s.error ?? stageFailure(s, GUIDED_STEPS[f].stages.find((k) => stageFailure(s, k)) ?? "")?.data.reason ?? "the step failed";
      fallBack(f, String(why), GUIDED_STEPS.slice(0, f).map((_, i) => ({ ms: stepMs(s, i), tone: stepTone(s, i), source: "live" as const })));
    } else if (guided.fellBackAt !== null && s.mode === "replay" && s.events.length) {
      setGuided((g) => ({ ...g, phase: "done" }));
    }
  }, [s.running, s.startedAt, s.mode, s.events.length, s.error, guided.phase, guided.fellBackAt]); // eslint-disable-line react-hooks/exhaustive-deps

  const graphFail = stageFailure(s, "graph");
  const counts = s.graph?.counts ?? g.runGraph?.counts;
  const graphEmpty = s.running ? "Building the code graph." : graphFail ? "" : preview.error ? `The graph could not be loaded: ${preview.error}` : scenario ? "Loading the graph…" : "Pick a repo to see its code graph.";
  const prepared = scenario?.kind === "repo" ? repos?.find((r) => r.name === scenario.name) ?? null : null;
  const changePreviewNode = change?.kind === "inject" ? g.nodes.find((n) => n.type === "function" && n.file === change.file && n.label.replace(/^\./, "").replace(/\(\)$/, "") === change.function.split(".").slice(-1)[0]) : undefined;

  return (
    <ExplainContext.Provider value={explain}>
      <div className="mx-auto max-w-[1760px] space-y-3 px-3 py-3 pb-14">
        <h1 className="sr-only">Live Lab</h1>
        <TopBar s={s} avail={avail} model={model} tally={tally} explain={explain} setExplain={setExplain}
          onReset={() => { reset(); setScenario(null); setChange(null); setHidden([]); setChallenge(false); setGuided(GUIDED_IDLE); holdTab.current = null; }}
          onIntegrity={() => { pick("integrity"); results.current?.scrollIntoView({ behavior: "smooth", block: "start" }); }} onPresent={() => setPresenting(true)} />
        {presenting && (
          <Presenter s={s} g={{ nodes: g.nodes, edges: g.edges, changed: g.changed, paths: g.paths, atRisk: g.atRisk, outcomes: g.outcomes }} onClose={() => setPresenting(false)}
            onRestart={() => { if (s.mode === "replay" && lastReplay.current) startReplay(lastReplay.current.name, lastReplay.current.speed); }} />
        )}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Steps stage={stage} />
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" onClick={runFullDemo} disabled={s.running} data-testid="run-full-demo"
              className={`${BTN_PRIMARY} min-h-[36px]`} title={`itsdangerous, seed ${GUIDED_SEED}, from the change to the repair`}><Icon name="play" />Run full demo</button>
            <button type="button" onClick={() => setChallenge((v) => !v)} aria-pressed={challenge} aria-expanded={challenge}
              className={`${BTN} min-h-[36px] font-semibold ${challenge ? "border-accent text-accent" : ""}`}><Icon name="bug" />Challenge</button>
          </div>
        </div>
        {guided.phase !== "idle" && <GuidedStepper s={s} g={guided} onStop={() => { reset(); setGuided(GUIDED_IDLE); }} />}
        {challenge && (
          <ChallengeCard s={s} live={avail.live} running={s.running} llmOk={modelOk}
            repo={scenario?.kind === "repo" ? scenario.name : s.repo?.prepared ? String(s.repo.name) : null}
            onRun={(c, opts) => {
              const name = scenario?.kind === "repo" ? scenario.name : String(s.repo?.name ?? "");
              const sc = { kind: "repo", name } as NonNullable<Scenario>;
              const ch: Change = { kind: "inject", ...c };
              fixPending.current = !opts.noLlm;
              setGuided(GUIDED_IDLE);
              setScenario(sc); setChange(ch); launch(sc, ch, opts);
            }}
            onPickMyself={() => { setChallenge(false); document.getElementById("panel-graph")?.scrollIntoView({ behavior: "smooth", block: "center" }); }}
            onClose={() => setChallenge(false)} />
        )}
        {s.error && <p className="ui m-0 flex items-center gap-2 rounded border border-red px-3 py-2 text-sm text-red" role="alert"><Icon name="warn" />{s.error}</p>}
        {s.repo && s.repo.tests_runnable === false && s.repo.reason && (
          <p className="ui m-0 rounded border border-amber px-3 py-2 text-sm text-amber" role="status">Tests were not run: {s.repo.reason}</p>
        )}
        {!avail.live && avail.checked && idle && (
          <p className="ui m-0 rounded border border-amber px-3 py-2 text-sm text-amber" role="status">Live runs are off: {avail.reason}</p>
        )}

        <div className="grid gap-3 lg:grid-cols-[minmax(300px,340px)_minmax(0,1fr)_minmax(260px,300px)]">
          {idle ? (
            <Panel id="panel-pick" title={<span className="flex items-center gap-2"><span className="num text-accent">1</span>Pick a repo</span>} bodyClass="p-3">
              <RepoCards repos={repos} live={avail.live} disabled={s.running} scenario={scenario} setScenario={setScenario} setChange={setChange} />
            </Panel>
          ) : (
            <Panel id="panel-code" title="The change" className="hidden min-h-0 flex-col lg:flex" bodyClass="flex min-h-0 flex-1 flex-col" right={<Prov mode={s.change ? s.mode : "idle"} />}>
              <CodePanel change={s.change} className="h-[clamp(420px,calc(100vh-300px),640px)]" />
            </Panel>
          )}

          <Panel id="panel-graph" title={idle ? <span className="flex items-center gap-2"><span className="num text-accent">2</span>Break it</span> : "Blast radius"} bodyClass="p-0" right={
            <>
              <Prov mode={s.graph ? s.mode : "idle"} />
              <button type="button" onClick={() => graphRef.current?.fit()} className={BTN} aria-label="Fit the graph">fit</button>
              <button type="button" onClick={() => graphRef.current?.zoomIn()} className={BTN} aria-label="Zoom in">+</button>
              <button type="button" onClick={() => graphRef.current?.zoomOut()} className={BTN} aria-label="Zoom out">−</button>
            </>}>
            <div className="relative h-[clamp(420px,calc(100vh-300px),640px)] overflow-hidden bg-page">
              {g.nodes.length === 0 && (
                <div className="absolute inset-0 grid place-items-center px-8 text-center">
                  {graphFail ? <div className="max-w-md text-left"><p className="ui m-0 text-sm font-semibold text-red">The graph could not be built.</p><p className="mono m-0 mt-1 text-xs">{String(graphFail.data.reason)}</p></div>
                    : <p className="ui m-0 max-w-md text-md text-muted">{graphEmpty}</p>}
                </div>
              )}
              {idle && prepared && !change && g.nodes.length > 0 && (
                <span className="ui pointer-events-none absolute left-1/2 top-3 z-10 -translate-x-1/2 rounded-full border border-accent bg-panel px-3 py-1 text-sm font-semibold text-accent shadow-[0_4px_16px_rgb(0_0_0/0.4)]">Click a function to break it</span>
              )}
              <GraphView ref={graphRef} className="absolute inset-0" nodes={g.nodes} edges={g.edges} layout="rings"
                changed={g.changed} waveKey={waveKey} paths={g.paths} atRisk={g.atRisk} outcomes={g.outcomes}
                selected={changePreviewNode && idle ? changePreviewNode.id : selected} focusSelected={!idle}
                hiddenNodeTypes={hiddenTypes} hiddenIds={hiddenIds} sizeBy={sizeBy} important={important} tooltipOf={tooltipOf}
                onSelect={(id) => { const n = g.nodes.find((k) => k.id === id); if (idle && breakable(n)) return; setSelected(id); setCtx(null); }}
                onTap={(id, x, y) => { const n = g.nodes.find((k) => k.id === id); if (idle && breakable(n)) { setSelected(null); setCtx({ id, x, y }); } }}
                onContext={(id, x, y) => { const n = g.nodes.find((k) => k.id === id); if (breakable(n)) { setSelected(null); setCtx({ id, x, y }); } }}
                ariaLabel="Blast-radius graph. Click, long-press or press Enter on a function to break it"
                renderCard={(id, info) => sel && sel.id === id ? (
                  <NodeCard node={sel} nodes={g.nodes} edges={g.edges} repo={repoName} s={s} info={info} onClose={() => setSelected(null)} onSelect={(x) => { setSelected(x); graphRef.current?.center(x); }}
                    actions={breakable(sel) ? (<>
                      <button type="button" className={BTN} onClick={() => { setCtx({ id: sel.id, x: 40, y: 40 }); setSelected(null); }}><Icon name="bug" />Break it</button>
                      <button type="button" className={BTN} disabled={probe?.running} onClick={async () => {
                        const r = await fetch(`/api/lab/mutations?repo=${repoName}&file=${encodeURIComponent(sel.file)}`).then((x) => x.json()).catch(() => null);
                        const { matchFunction } = await import("./BreakIt");
                        const fn = r ? matchFunction(sel, r.functions ?? []) : null;
                        if (repoName && fn) startProbe(repoName, sel.file, fn.function);
                      }}>Probe suite strength</button>
                    </>) : undefined} />
                ) : null} />
              {ctx && repoName && g.nodes.find((n) => n.id === ctx.id) && (
                <InjectMenu node={g.nodes.find((n) => n.id === ctx.id)!} repo={repoName} x={ctx.x} y={ctx.y} disabled={s.running}
                  onClose={() => setCtx(null)}
                  onRun={(c) => { setScenario({ kind: "repo", name: repoName }); setChange({ kind: "inject", ...c }); setCtx(null); }} />
              )}
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-rule px-3 py-2">
              <GraphFilters hidden={hidden} counts={typeCounts} toggle={(k) => setHidden((h) => (h.includes(k) ? h.filter((x) => x !== k) : [...h, k]))} />
              {g.runGraph && <span className="num mono ml-auto text-xs text-muted">{s.graph?.n_nodes ?? g.nodes.length} nodes · {s.graph?.n_edges ?? g.edges.length} edges{counts ? ` · ${counts.nodes.test ?? 0} tests` : ""}</span>}
              <Info label="About the graph" align="right">
                <span className="block">Node size is the number of tests that reach it along calls and imports. Click a node to focus it; click empty space to clear.</span>
                <span className="mt-1 block">{s.graph?.parse_failures ?? g.runGraph?.parse_failures ?? 0} parse failures in this graph.</span>
              </Info>
            </div>
            {s.graph?.truncated && !g.full && (
              <p className="ui m-0 border-t border-rule px-3 py-1.5 text-xs text-amber">Showing files and the 2-hop neighbourhood of the change. <button type="button" className="underline" onClick={g.loadFull}>Load the full graph</button></p>
            )}
          </Panel>

          <Panel id="panel-run" title={<span className="flex items-center gap-2"><span className="num text-accent">3</span>Run</span>} bodyClass="p-3">
            <RunPanel scenario={scenario} change={change} running={s.running} canRun={canRun} why={why} onRun={run} runs={runs} onReplay={replay}
              stageLabel={runningStage ? `Running · ${runningStage}` : "Running"}
              extra={(scenario?.kind === "repo" || scenario?.kind === "github") && idle ? (
                <button type="button" onClick={() => setOtherOpen(true)} className={`${BTN} justify-center`} aria-haspopup="dialog">Other ways to change code</button>
              ) : undefined}>
              <details className="rounded border border-rule bg-page">
                <summary className="ui cursor-pointer px-2 py-1.5 text-sm">Options</summary>
                <div className="space-y-2 border-t border-rule p-2">
                  <label className="ui block text-xs text-muted" htmlFor="model">Model for the repair step</label>
                  <select id="model" value={model} onChange={(e) => setModel(e.target.value)} className="mono w-full px-2 py-1 text-xs">{MODELS.map((m) => <option key={m}>{m}</option>)}</select>
                  <label className={`ui flex items-center gap-1.5 text-xs ${modelOk ? "text-ink" : "text-muted"}`} title={modelOk ? "One extra model call: R1 (log-only) on the same failure" : quotaReason || avail.reason}>
                    <input type="checkbox" checked={repairArena && modelOk} disabled={!modelOk} onChange={(e) => setRepairArena(e.target.checked)} />
                    Repair arena (one extra call)
                  </label>
                  {avail.checked && !modelOk && <p className="ui m-0 text-xs text-amber" role="status">{quotaReason ? "Repair is off: quota used up." : avail.live ? "Repair is off: no model key." : "Static build: replays only."}</p>}
                </div>
              </details>
            </RunPanel>
          </Panel>
        </div>

        <PipelineRail s={s} active={null} onPick={pickStage} />

        <TestGapPanel s={s} />
        {probe && <ProbePanel p={probe} onClose={clearProbe} />}
        <section ref={results} id="results" className="scroll-mt-16 rounded-md border border-rule bg-panel" aria-label="Results">
          <div className="flex flex-wrap items-center gap-1 border-b border-rule px-2 pt-2" role="tablist" aria-label="Result views">
            {RESULT_TABS.map((t) => {
              const tone = tabTone(s, t);
              return (
                <button key={t.id} type="button" role="tab" id={`tab-${t.id}`} aria-selected={tab === t.id} aria-controls={`tabpanel-${t.id}`} onClick={() => pick(t.id)}
                  className={`ui -mb-px flex min-h-[34px] items-center gap-1.5 rounded-t border border-b-0 px-3 py-1.5 text-sm ${tab === t.id ? "border-rule bg-panel font-semibold text-ink" : "border-transparent text-muted hover:text-ink"}`}>
                  {tone && <StatusIcon tone={tone} className="text-xs" />}{t.label}
                </button>
              );
            })}
            <span className="ml-auto pb-1.5 pr-1"><Prov mode={s.mode} /></span>
          </div>
          <div role="tabpanel" id={`tabpanel-${tab}`} aria-labelledby={`tab-${tab}`} className="p-4">
            {tab === "impact" && <ImpactPanel s={s} />}
            {tab === "race" && <RacePanel s={s} />}
            {tab === "arena" && <ArenaPanel s={s} />}
            {tab === "triage" && <TriagePanel s={s} />}
            {tab === "repair" && <RepairPanel s={s} recorded={recorded} onPlayRecorded={playRecorded} />}
            {tab === "verdict" && <VerdictPanel s={s} />}
            {tab === "comment" && <ReportPanel s={s} />}
            {tab === "integrity" && <IntegrityPanel s={s} />}
          </div>
        </section>

        <div className="grid gap-3 pt-2" aria-label="Paper results">
          <MetaCard />
          <GlanceCard />
        </div>
      </div>

      {otherOpen && (scenario?.kind === "repo" || scenario?.kind === "github") && (
        <Drawer side="left" title="Other ways to change code" onClose={() => setOtherOpen(false)}>
          <div className="min-h-0 flex-1 overflow-y-auto p-3">
            <ChangePicker scenario={scenario} repo={prepared} change={change} setChange={(c) => { setChange(c); if (c) setOtherOpen(false); }} disabled={s.running} />
          </div>
        </Drawer>
      )}
      {logOpen && (
        <Drawer side="right" title="Event log" onClose={() => setLogOpen(false)}>
          <EventLog events={s.events} className="min-h-0 flex-1" />
        </Drawer>
      )}
      <Ticker events={s.events} onOpen={() => setLogOpen(true)} />
    </ExplainContext.Provider>
  );
}
