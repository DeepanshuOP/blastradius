"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge, Card, Mono, Source } from "./ui";

type Tbl = { columns: string[]; rows: string[][] };
type E1 = {
  source: string; verdict: string; gate3_met: boolean; main: Tbl; ci: Tbl; stats: Tbl | null; loro: Tbl | null;
  ablation: Tbl | null; alone: Tbl | null; learning_curve: Tbl | null; strata: Tbl | null; shap_family: Tbl | null;
  recall_vs_suite: Record<string, number[]> | null; curve_fracs: number[] | null;
} | null;
type E2 = {
  source: string; classes: Tbl; chronological: Tbl | null; pooled: Tbl | null; dangerous_error: string; application: Tbl | null;
} | null;
type E3 = {
  status: string; note?: string; source?: string; detection?: Tbl | null; retrieval?: Tbl | null; models?: Record<string, Tbl>;
} | null;

async function load<T>(name: string, key: string): Promise<T | null> {
  const r = await fetch(`/data/${name}.json`, { cache: "no-store" });
  if (!r.ok) throw new Error(`${name}.json: HTTP ${r.status}`);
  return ((await r.json()) as Record<string, T>)[key] ?? null;
}

function Table({ t, pick, max }: { t: Tbl; pick?: string[]; max?: number }) {
  const idx = pick ? pick.map((p) => t.columns.findIndex((c) => c === p || c.startsWith(p))).filter((i) => i >= 0) : t.columns.map((_, i) => i);
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-xs">
        <thead><tr className="border-b border-slate-200 text-slate-500">
          {idx.map((i) => <th key={i} className="whitespace-nowrap px-2 py-1.5 font-semibold">{t.columns[i]}</th>)}
        </tr></thead>
        <tbody>
          {t.rows.slice(0, max).map((r, ri) => (
            <tr key={ri} className="border-b border-slate-100 last:border-0">
              {idx.map((i) => <td key={i} className="whitespace-nowrap px-2 py-1 tabular-nums text-slate-800">{r[i]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** The four stages. The CI server stays the executor; BR-Bench trains the two models and scores all three. */
function Architecture() {
  const box = (x: number, title: string, sub: string, tag: string) => (
    <g key={title}>
      <rect x={x} y={30} width={170} height={84} rx={10} className="fill-white stroke-slate-300" />
      <text x={x + 85} y={56} textAnchor="middle" className="fill-slate-900 text-[13px] font-semibold">{title}</text>
      <text x={x + 85} y={76} textAnchor="middle" className="fill-slate-600 text-[10.5px]">{sub}</text>
      <text x={x + 85} y={98} textAnchor="middle" className="fill-orange-700 text-[10.5px] font-semibold">{tag}</text>
    </g>
  );
  return (
    <svg viewBox="0 0 800 190" role="img" aria-label="Predict, run, triage, repair, fed by BR-Bench" className="w-full">
      {box(10, "1 Predict", "rank the tests a change breaks", "E1 LightGBM ranker")}
      {box(215, "2 Run", "risky tests first (CI executes)", "Jenkins / Actions")}
      {box(420, "3 Triage", "mine · inherited · flaky", "E2 classifier")}
      {box(625, "4 Repair", "patch only what is mine", "E3 LLM agent, full-suite gate")}
      {[180, 385, 590].map((x) => <path key={x} d={`M${x} 72 h35`} className="stroke-slate-400" strokeWidth={2} markerEnd="url(#a)" />)}
      <defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" className="fill-slate-400" /></marker></defs>
      <rect x={10} y={140} width={785} height={36} rx={8} className="fill-slate-100 stroke-slate-300" />
      <text x={402} y={163} textAnchor="middle" className="fill-slate-700 text-[11.5px]">
        BR-Bench: tests that really failed in GitHub Actions. It trains stages 1 and 3 and scores all four.
      </text>
      <path d="M95 140 V114 M505 140 V114" className="stroke-slate-300" strokeDasharray="4 3" />
    </svg>
  );
}

const COLORS: Record<string, string> = {
  B0: "#94a3b8", B1: "#cbd5e1", B2: "#64748b", B3: "#f59e0b", B4: "#2563eb", B5: "#a855f7", B6: "#0ea5e9", B7: "#14b8a6", ours: "#ea580c",
};

function Verdict({ ok, text }: { ok: boolean | null; text: string }) {
  return (
    <p className={`rounded-lg border px-4 py-3 text-sm ${ok === null ? "border-slate-200 bg-slate-50 text-slate-800" : ok ? "border-emerald-200 bg-emerald-50 text-emerald-900" : "border-amber-200 bg-amber-50 text-amber-950"}`}>
      {text}
    </p>
  );
}

export default function Intelligence() {
  const [e1, setE1] = useState<E1>(null);
  const [e2, setE2] = useState<E2>(null);
  const [e3, setE3] = useState<E3>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    Promise.all([load<NonNullable<E1>>("e1", "e1"), load<NonNullable<E2>>("e2", "e2"), load<NonNullable<E3>>("e3", "e3")])
      .then(([a, b, c]) => { setE1(a); setE2(b); setE3(c); }).catch((e) => setErr(String(e)));
  }, []);
  if (err) return <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">Could not load /data/e1.json ({err}). Run <Mono>make demo-data</Mono>.</p>;

  const curve = e1?.recall_vs_suite && e1.curve_fracs
    ? e1.curve_fracs.map((f, i) => ({ pct: `${(f * 100).toFixed(f < 0.1 ? 0 : 0)}%`, ...Object.fromEntries(Object.keys(e1.recall_vs_suite!).map((m) => [m, e1.recall_vs_suite![m][i]])) }))
    : [];
  const fam = e1?.shap_family?.rows.map((r) => ({ family: r[0], share: parseFloat(r[2]) })) ?? [];
  const abl = e1?.ablation?.rows.map((r) => ({ family: r[0].replace("without ", ""), delta: parseFloat(r[3]) })) ?? [];
  const e2one = e2?.dangerous_error?.split(". ").slice(0, 2).join(". ");

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-slate-900">From a dataset to a change-aware CI assistant</h2>
        <p className="mt-1 max-w-3xl text-sm text-slate-600">
          Predict which tests a change will break, run those first, say which failures are the change's own, and propose a fix that is accepted only if the whole suite passes.
          Each stage is one experiment on BR-Bench and each is allowed to come out negative. Verdicts below are the generated sentences, not hand-written ones.
        </p>
      </div>
      <Architecture />

      <Card title="E1 · Predict: rank the test files a change will break" step={1}>
        {!e1 ? <p>Loading…</p> : (
          <div className="space-y-4">
            <Verdict ok={e1.gate3_met} text={e1.verdict} />
            <Table t={e1.main} pick={["method", "n", "Recall@1", "Recall@5", "Recall@10", "Recall@20%", "MAP", "APFD"]} />
            <div className="grid gap-6 lg:grid-cols-2">
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Recall vs share of the suite run (test split)</p>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={curve} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="pct" fontSize={11} />
                      <YAxis domain={[0, 1]} fontSize={11} />
                      <Tooltip formatter={(v: number) => v.toFixed(3)} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      {Object.keys(COLORS).map((m) => <Line key={m} dataKey={m} stroke={COLORS[m]} dot={false} strokeWidth={m === "ours" ? 3 : 1.4} />)}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Change in Recall@10 when a family is removed</p>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={abl} layout="vertical" margin={{ left: 16, right: 16 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" fontSize={11} />
                      <YAxis type="category" dataKey="family" width={80} fontSize={11} />
                      <Tooltip formatter={(v: number) => v.toFixed(3)} />
                      <Bar dataKey="delta" fill="#ea580c" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
            <div>
              <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Mean |SHAP| share by feature family (how much the model uses it)</p>
              <div className="h-40">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={fam} layout="vertical" margin={{ left: 16, right: 16 }}>
                    <XAxis type="number" unit="%" fontSize={11} />
                    <YAxis type="category" dataKey="family" width={80} fontSize={11} />
                    <Tooltip />
                    <Bar dataKey="share" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <Source file={e1.source} />
          </div>
        )}
      </Card>

      <Card title="E2 · Triage: is this failure mine, inherited or flaky?" step={2}>
        {!e2 ? <p>Not generated.</p> : (
          <div className="space-y-4">
            <Verdict ok={null} text={e2one ?? ""} />
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Class counts per split (pairs)</p>
            <Table t={e2.classes} />
            {e2.pooled && <>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Pooled leave-one-repo-out (small sample)</p>
              <Table t={e2.pooled} pick={["method", "not-mine P", "not-mine R", "not-mine F1", "PR-AUC", "mine WRONGLY CLEARED"]} />
            </>}
            <Source file={e2.source} />
          </div>
        )}
      </Card>

      <Card title="E3 · Repair: patch the failures that are the change's own" step={3}>
        {!e3 || e3.status !== "run" ? (
          <Verdict ok={null} text={`Not run: ${e3?.note ?? "no results file"}. Run make repair-run, then make repair-eval.`} />
        ) : (
          <div className="space-y-4">
            {e3.retrieval && <><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Retrieval hit rate (no model, all tasks)</p><Table t={e3.retrieval} /></>}
            {e3.detection && <><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Detection</p><Table t={e3.detection} /></>}
            {Object.entries(e3.models ?? {}).map(([m, t]) => (
              <div key={m}><p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">{m}</p>
                <Table t={t} pick={["arm", "n", "plausible fix", "bootstrap", "edited seeded function", "tokens"]} /></div>
            ))}
            {e3.source && <Source file={e3.source} />}
          </div>
        )}
      </Card>
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <Badge tone="slate">seeded bugs are easier than real ones</Badge>
        <Badge tone="slate">test split is Java-only</Badge>
        <span>See <Mono>docs/RESULTS_2.md</Mono> for the two result tables: same-data comparisons, and context from other papers' data.</span>
      </div>
    </div>
  );
}
