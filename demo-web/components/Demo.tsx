"use client";

import { useEffect, useRef, useState } from "react";
import Overview from "./Overview";
import Results from "./Results";
import { STAGE_TITLES, StageCard } from "./Stages";
import type { IndexDoc, InstanceDoc, OverviewDoc, ResultsDoc } from "./types";
import { Card, Mono, short } from "./ui";

const TABS = ["Overview", "How it works", "Live run", "Results", "Corpus"] as const;
type Tab = (typeof TABS)[number];
const STEP_MS = 800;

async function getJson<T>(path: string): Promise<T> {
  const r = await fetch(path, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return (await r.json()) as T;
}

const PIPELINE: [string, string][] = [
  ["GitHub Actions", "Open-source projects run their test suites on every pull request."],
  ["Harvester", "We download PR, run and job metadata through a rate-limited, resumable API client."],
  ["CI logs", "The raw job logs of failed runs are stored locally; success-run logs are pruned."],
  ["Parsers", "Harness-specific parsers (JUnit/Maven/Gradle, pytest) extract each failing test from the log."],
  ["Canonical test_id", "Every raw test name is normalised to one join key, so the same test matches across runs."],
  ["Base-run resolution", "We find the CI run of the commit the PR branched from, to see what was already broken."],
  ["Fault-revealing labels", "A test is labelled when it fails at head, did not fail at base, and is not flaky."],
  ["Binding", "Each labelled test is bound to its test file at a pinned commit of the repository."],
  ["Code graph", "A static graph of files, functions and imports is built at the base commit."],
  ["Predictors vs reality", "Co-change and historical-frequency predictions are scored against the tests that actually failed."],
];

function HowItWorks() {
  return (
    <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {PIPELINE.map(([t, d], i) => (
        <li key={t} className="relative flex">
          <div className="flex w-full flex-col rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <span className="text-xs font-semibold text-slate-400">STEP {i + 1}</span>
            <span className="mt-1 font-semibold text-slate-900">{t}</span>
            <span className="mt-1 text-sm text-slate-600">{d}</span>
          </div>
          {i < PIPELINE.length - 1 && (
            <span aria-hidden className="absolute -bottom-3 left-1/2 z-10 -translate-x-1/2 text-slate-400 sm:hidden">↓</span>
          )}
          {i < PIPELINE.length - 1 && (
            <span aria-hidden className="absolute -right-2.5 top-1/2 z-10 hidden -translate-y-1/2 text-slate-400 sm:block">→</span>
          )}
        </li>
      ))}
    </ol>
  );
}

function LiveRun({ index }: { index: IndexDoc }) {
  const [id, setId] = useState(index.default);
  const [doc, setDoc] = useState<InstanceDoc | null>(null);
  const [shown, setShown] = useState(0);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => () => { if (timer.current) clearInterval(timer.current); }, []);

  const stop = () => { if (timer.current) clearInterval(timer.current); timer.current = null; };

  const run = async () => {
    stop();
    setShown(0);
    setErr(null);
    setRunning(true);
    try {
      const d = doc && doc.id === id ? doc : await getJson<InstanceDoc>(`/data/instances/${id}.json`);
      setDoc(d);
      let n = 0;
      timer.current = setInterval(() => {
        n += 1;
        setShown(n);
        if (n >= STAGE_TITLES.length) { stop(); setRunning(false); }
      }, STEP_MS);
    } catch (e) {
      setErr(String(e));
      setRunning(false);
    }
  };

  const total = STAGE_TITLES.length;
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-900">
        Replaying a recorded run computed by <Mono>analysis/export_demo_data.py</Mono> at{" "}
        <Mono>{short(index.generated_at_git_sha)}</Mono>. The same pipeline runs live with <Mono>make demo</Mono>.
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="flex-1 text-sm">
          <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500">Instance</span>
          <select value={id} disabled={running}
            onChange={(e) => { stop(); setId(e.target.value); setShown(0); setDoc(null); }}
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none">
            {index.instances.map((x) => (
              <option key={x.id} value={x.id}>
                {x.repo} · PR #{x.pr_number} · run {x.run_id} · {x.failure_class} · {x.test_count} fault-revealing test{x.test_count === 1 ? "" : "s"}
              </option>
            ))}
          </select>
        </label>
        <button onClick={run} disabled={running}
          className="rounded-md bg-slate-900 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400">
          {running ? "Running…" : shown >= total ? "Run again" : "Run pipeline"}
        </button>
      </div>
      {index.instances.length === 1 && (
        <p className="text-xs text-slate-500">
          One instance qualified: it must clear every gate (strict label, bound test, no holdout job, raw log on disk) and have a graph buildable offline from local git objects.
        </p>
      )}
      {err && <p className="text-sm text-red-700">{err}</p>}
      {(running || shown > 0) && (
        <div>
          <div className="mb-1 flex justify-between text-xs text-slate-500">
            <span>{shown < total ? `Stage ${Math.min(shown + 1, total)} of ${total}: ${STAGE_TITLES[Math.min(shown, total - 1)]}` : "All stages complete"}</span>
            <span>{Math.round((shown / total) * 100)}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
            <div className="h-full rounded-full bg-slate-800 transition-all duration-500" style={{ width: `${(shown / total) * 100}%` }} />
          </div>
        </div>
      )}
      <div className="space-y-4">
        {doc && Array.from({ length: shown }, (_, i) => <StageCard key={`${doc.id}-${i}`} i={i} doc={doc} />)}
      </div>
    </div>
  );
}

function Corpus() {
  return (
    <Card title="Corpus dashboard">
      <p>The live harvest state (repositories, runs, jobs, logs on disk) is shown by the existing read-only Streamlit dashboard, not rebuilt here. From the repository root, in WSL2:</p>
      <pre className="mt-3 overflow-x-auto rounded bg-slate-900 p-3 font-mono text-xs text-slate-200">uv run --extra dashboard streamlit run dashboard.py</pre>
      <p className="mt-3">It opens on <Mono>http://localhost:8501</Mono> and reads <Mono>data/state/cursor.db</Mono> in read-only mode, plus <Mono>data/frame/frame_v1.csv</Mono> and the raw-store directory.</p>
    </Card>
  );
}

export default function Demo() {
  const [tab, setTab] = useState<Tab>("Overview");
  const [index, setIndex] = useState<IndexDoc | null>(null);
  const [results, setResults] = useState<ResultsDoc | null>(null);
  const [overview, setOverview] = useState<OverviewDoc | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getJson<IndexDoc>("/data/index.json"), getJson<ResultsDoc>("/data/results.json"),
      getJson<OverviewDoc>("/data/overview.json")])
      .then(([i, r, o]) => { setIndex(i); setResults(r); setOverview(o); })
      .catch((e) => setErr(String(e)));
  }, []);

  const loading = !err && <p className="text-sm text-slate-500">Loading…</p>;
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 pt-3 sm:flex-row sm:items-end sm:justify-between sm:px-6">
          <div className="pb-1 sm:pb-3">
            <h1 className="text-lg font-bold tracking-tight text-slate-900 sm:text-xl">BlastRadius</h1>
            <p className="text-xs text-slate-500">Which tests did a pull request actually break, and can a predictor tell in advance?</p>
          </div>
          <nav className="-mb-px flex gap-1 overflow-x-auto" role="tablist">
            {TABS.map((t) => (
              <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)}
                className={`whitespace-nowrap border-b-2 px-3 py-2.5 text-sm font-medium transition-colors ${tab === t ? "border-slate-900 text-slate-900" : "border-transparent text-slate-500 hover:text-slate-800"}`}>
                {t}
              </button>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
        {err && <p className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">Could not load /data: {err}. Run <Mono>make demo-data</Mono>.</p>}
        {tab === "Overview" && (overview ? <Overview o={overview} /> : loading)}
        {tab === "How it works" && <HowItWorks />}
        {tab === "Live run" && (index ? <LiveRun index={index} /> : loading)}
        {tab === "Results" && (results ? <Results r={results} /> : loading)}
        {tab === "Corpus" && <Corpus />}
      </main>
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-slate-500 sm:px-6">
          data at <Mono className="text-slate-600">{index ? short(index.generated_at_git_sha) : "…"}</Mono> · static replay · <Mono className="text-slate-600">make demo</Mono> runs it live
        </div>
      </footer>
    </div>
  );
}
