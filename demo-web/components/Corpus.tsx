"use client";

import { Bar, BarChart, CartesianGrid, Cell, LabelList, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CorpusDoc } from "./types";
import { Card, Mono, Source } from "./ui";

const LANG_COLOR: Record<string, string> = { Java: "#2563eb", Python: "#f59e0b" };

function Donut({ data, total }: { data: { name: string; value: number; text?: string }[]; total: string }) {
  return (
    <div className="relative h-56 w-full">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={52} outerRadius={82} paddingAngle={2} isAnimationActive={false}
            label={(e: { name: string; value: number }) => `${e.name} ${e.value.toLocaleString()}`}>
            {data.map((d) => <Cell key={d.name} fill={LANG_COLOR[d.name] ?? "#94a3b8"} />)}
          </Pie>
          <Tooltip formatter={(v: number, _n: string, p: { payload?: { text?: string } }) => p.payload?.text ?? v.toLocaleString()} />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center text-center text-xs text-slate-500">{total}</div>
    </div>
  );
}

function Funnel({ stages, height, log = true, left = 200 }: { stages: { stage: string; count: number }[]; height: string; log?: boolean; left?: number }) {
  const min = Math.min(...stages.map((s) => s.count));
  return (
    <div className={`${height} w-full`}>
      <ResponsiveContainer>
        <BarChart data={stages.map((s) => ({ name: s.stage, count: s.count }))} layout="vertical" margin={{ left: 8, right: 64, top: 4, bottom: 4 }}>
          <CartesianGrid horizontal={false} stroke="#e2e8f0" />
          <XAxis type="number" scale={log ? "log" : "auto"} domain={log ? [Math.max(1, Math.floor(min / 2)), "auto"] : [0, "auto"]} allowDataOverflow
            tick={{ fontSize: 12, fill: "#64748b" }} tickFormatter={(v: number) => v.toLocaleString()} />
          <YAxis type="category" dataKey="name" width={left} tick={{ fontSize: 11, fill: "#334155" }} />
          <Tooltip formatter={(v: number) => v.toLocaleString()} />
          <Bar dataKey="count" fill="#64748b" radius={[0, 3, 3, 0]} isAnimationActive={false}>
            <LabelList dataKey="count" position="right" formatter={(v: number) => v.toLocaleString()} style={{ fontSize: 12, fill: "#334155" }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function Corpus({ c }: { c: CorpusDoc }) {
  const harvested = ["Java", "Python"].map((k) => ({ name: k, value: c.harvested_repos_by_language[k as "Java" | "Python"] }));
  const strict = c.strict_by_language.rows.map((r) => ({ name: r.language, value: r.instances.n, text: r.instances.text }));
  const strictTotal = strict.reduce((a, x) => a + x.value, 0);
  const top = c.top_repos?.rows.map((r) => ({ name: r.repo, instances: r.instances, labels: r.labels }));
  return (
    <div className="space-y-5">
      <div className="grid gap-5 md:grid-cols-2">
        <Card title="Harvested repositories by language">
          <Donut data={harvested} total={`${harvested.reduce((a, x) => a + x.value, 0)} repos`} />
          <Source file={c.harvested_repos_by_language.source} />
        </Card>
        <Card title="Strict instances by language">
          <Donut data={strict} total={`${strictTotal.toLocaleString()} instances`} />
          <Source file={c.strict_by_language.source} />
        </Card>
      </div>

      <Card title="Top repositories by strict instances">
        {top ? (
          <>
            <div style={{ height: 28 * top.length + 40 }} className="w-full">
              <ResponsiveContainer>
                <BarChart data={top} layout="vertical" margin={{ left: 8, right: 48, top: 4, bottom: 4 }}>
                  <CartesianGrid horizontal={false} stroke="#e2e8f0" />
                  <XAxis type="number" tick={{ fontSize: 12, fill: "#64748b" }} />
                  <YAxis type="category" dataKey="name" width={230} tick={{ fontSize: 11, fill: "#334155" }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="instances" name="strict instances" fill="#334155" radius={[0, 3, 3, 0]} isAnimationActive={false}>
                    <LabelList dataKey="instances" position="right" style={{ fontSize: 12, fill: "#334155" }} />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <Source file={c.top_repos!.source} />
          </>
        ) : (
          <p className="text-slate-600">
            Not exported in this build: it needs <Mono>data/interim/outcomes.parquet</Mono> and <Mono>instances_raw.parquet</Mono>. Run <Mono>make demo-data</Mono>{" "}
            on a machine that has the data, and this chart fills in.
          </p>
        )}
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card title="Repositories funnel">
          <Funnel stages={c.repos_funnel.stages} height="h-72" left={190} />
          <p className="text-xs text-slate-500">Log scale. Each stage is the intersection with the previous one.</p>
          <Source file={c.repos_funnel.source} />
        </Card>
        <Card title="Runs funnel: from every discovered run to strict benchmark instances">
          <Funnel stages={c.runs_funnel.stages} height="h-72" left={190} />
          <p className="text-xs text-slate-500">Log scale. Each stage is the intersection with the previous one.</p>
          <Source file={c.runs_funnel.source} />
        </Card>
      </div>

      <Card title="Live harvest dashboard">
        <p>The live harvest state (repositories, runs, jobs, logs on disk) is shown by the existing read-only Streamlit dashboard, not rebuilt here. From the repository root, in WSL2:</p>
        <pre className="mt-3 overflow-x-auto rounded bg-slate-900 p-3 font-mono text-xs text-slate-200">uv run --extra dashboard streamlit run dashboard.py</pre>
        <p className="mt-3">It opens on <Mono>http://localhost:8501</Mono> and reads <Mono>data/state/cursor.db</Mono> in read-only mode, plus <Mono>data/frame/frame_v1.csv</Mono> and the raw-store directory.</p>
      </Card>
    </div>
  );
}
