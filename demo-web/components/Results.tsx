"use client";

import {
  Bar, BarChart, CartesianGrid, Cell, LabelList, Legend, Pie, PieChart, ResponsiveContainer, Scatter, ScatterChart,
  Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import type { MethodRow, ResultsDoc } from "./types";
import { Badge, CHART_METHODS, Card, METHOD_COLOR, Source, METHOD_SHORT as SHORT } from "./ui";

const CLASS_COLOR: Record<string, string> = {
  "code-level": "#2563eb", "environment-strict": "#dc2626", timeout: "#f59e0b", unknown: "#94a3b8",
};

/** One row per group (language or size stratum), one bar per charted method, value = mean recall. */
function groupedRecall(groups: { name: string; methods: MethodRow[] }[]) {
  return groups.map((g) => ({
    name: g.name,
    ...Object.fromEntries(CHART_METHODS.map((m) => [m, g.methods.find((x) => x.method === m)?.mean_recall ?? 0])),
  }));
}

function GroupedBars({ data }: { data: ReturnType<typeof groupedRecall> }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 4 }}>
          <CartesianGrid vertical={false} stroke="#e2e8f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#334155" }} />
          <YAxis domain={[0, 1]} tickFormatter={(v: number) => v.toFixed(1)} tick={{ fontSize: 12, fill: "#64748b" }} />
          <Tooltip formatter={(v: number, k: string) => [v.toFixed(3), SHORT[k] ?? k]} />
          <Legend formatter={(k: string) => SHORT[k] ?? k} wrapperStyle={{ fontSize: 12 }} />
          {CHART_METHODS.map((m) => (
            <Bar key={m} dataKey={m} fill={METHOD_COLOR[m]} isAnimationActive={false} radius={[3, 3, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}


export default function Results({ r }: { r: ResultsDoc }) {
  const rq = r.rq1_k10;
  const recall = rq.methods.map((m) => ({ name: SHORT[m.method] ?? m.method, recall: m.mean_recall }));
  const lk = r.leakage;
  const bd = r.rq1_breakdowns;
  const byLang = groupedRecall(Object.entries(bd.by_language).map(([k, v]) => ({ name: `${k} (n=${v[0].n})`, methods: v })));
  const bySize = groupedRecall(bd.by_size.map((g) => ({ name: `${g.stratum} file${g.stratum === "1" ? "" : "s"} (n=${g.n})`, methods: g.methods })));
  const curves = CHART_METHODS.map((m) => ({
    method: m,
    points: Object.keys(bd.curves).map(Number).sort((a, b) => a - b).map((k) => {
      const row = bd.curves[String(k)].find((x) => x.method === m);
      return { k: `k=${k}`, recall: row?.mean_recall ?? 0, precision: row?.mean_precision ?? 0 };
    }),
  }));
  const classes = r.environment_audit.labels_by_class.map((c) => ({ name: c.class, value: c.labels.n, text: c.labels.text }));

  return (
    <div className="space-y-5">
      <Card title={`RQ1: predictors at k = ${rq.k} (scored on the same instances)`}>
        <details className="group mb-4 rounded border border-slate-200 bg-slate-50/50 px-3 py-2">
          <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-slate-600">Details: full k = 10 table</summary>
        <div className="mt-2 overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="text-xs uppercase text-slate-500">
              <tr>
                <th className="py-1.5 pr-3">method</th><th className="py-1.5 pr-3 text-right">n</th>
                <th className="py-1.5 pr-3 text-right">mean P</th><th className="py-1.5 pr-3 text-right">mean R</th>
                <th className="py-1.5 pr-3 text-right">mean J</th><th className="py-1.5 pr-3">micro R (hits/actual)</th>
                <th className="py-1.5 text-right">median size</th>
              </tr>
            </thead>
            <tbody>
              {rq.methods.map((m) => (
                <tr key={m.method} className="border-t border-slate-100">
                  <td className="py-1.5 pr-3">{m.method}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums">{m.n}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums">{m.mean_precision.toFixed(3)}</td>
                  <td className="py-1.5 pr-3 text-right font-semibold tabular-nums">{m.mean_recall.toFixed(3)}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums">{m.mean_jaccard.toFixed(3)}</td>
                  <td className="py-1.5 pr-3 tabular-nums text-slate-600">{m.micro_recall.text}</td>
                  <td className="py-1.5 text-right tabular-nums">{m.median_size}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </details>
        <h4 className="mb-1 mt-2 text-xs font-semibold uppercase text-slate-500">Mean recall per method</h4>
        <div className="h-72 w-full">
          <ResponsiveContainer>
            <BarChart data={recall} layout="vertical" margin={{ left: 8, right: 48, top: 4, bottom: 4 }}>
              <CartesianGrid horizontal={false} stroke="#e2e8f0" />
              <XAxis type="number" domain={[0, 1]} tickFormatter={(v: number) => v.toFixed(1)} tick={{ fontSize: 12, fill: "#64748b" }} />
              <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 12, fill: "#334155" }} />
              <Tooltip formatter={(v: number) => v.toFixed(3)} />
              <Bar dataKey="recall" fill="#334155" radius={[0, 3, 3, 0]} isAnimationActive={false}>
                <LabelList dataKey="recall" position="right" formatter={(v: number) => v.toFixed(3)} style={{ fontSize: 12, fill: "#334155" }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <Source file={rq.source} />
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card title="Mean recall at k = 10 by language">
          <GroupedBars data={byLang} />
          <Source file={bd.source} />
        </Card>
        <Card title="Mean recall at k = 10 by change size (files changed in the PR)">
          <GroupedBars data={bySize} />
          <Source file={bd.source} />
        </Card>
        <Card title="Precision vs recall as k grows (k = 5, 10, 20)">
          <div className="h-72 w-full">
            <ResponsiveContainer>
              <ScatterChart margin={{ left: 0, right: 24, top: 8, bottom: 24 }}>
                <CartesianGrid stroke="#e2e8f0" />
                <XAxis type="number" dataKey="recall" name="mean recall" domain={[0, 0.7]} tick={{ fontSize: 12, fill: "#64748b" }}
                  label={{ value: "mean recall", position: "insideBottom", offset: -8, fontSize: 12, fill: "#64748b" }} />
                <YAxis type="number" dataKey="precision" name="mean precision" domain={[0, 0.25]} ticks={[0, 0.05, 0.1, 0.15, 0.2, 0.25]} tick={{ fontSize: 12, fill: "#64748b" }}
                  label={{ value: "mean precision", angle: -90, position: "insideLeft", fontSize: 12, fill: "#64748b" }} />
                <ZAxis range={[60, 60]} />
                <Tooltip cursor={{ strokeDasharray: "3 3" }} formatter={(v: number) => v.toFixed(3)} />
                <Legend verticalAlign="top" wrapperStyle={{ fontSize: 12 }} />
                {curves.map((c) => (
                  <Scatter key={c.method} name={SHORT[c.method] ?? c.method} data={c.points} fill={METHOD_COLOR[c.method]}
                    line={{ stroke: METHOD_COLOR[c.method], strokeWidth: 1.5 }} isAnimationActive={false}>
                    {c.method === "historical-frequency baseline" && (
                      <LabelList dataKey="k" position="top" style={{ fontSize: 10, fill: "#64748b" }} />
                    )}
                  </Scatter>
                ))}
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <Source file={bd.source} />
        </Card>
        <Card title={`What the ${classes.reduce((a, c) => a + c.value, 0).toLocaleString()} strict labels failed with (message-based class)`}>
          <div className="h-72 w-full">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={classes} dataKey="value" nameKey="name" innerRadius={55} outerRadius={95} paddingAngle={2} isAnimationActive={false}
                  label={(e: { name: string; value: number }) => `${e.name} ${e.value.toLocaleString()}`}>
                  {classes.map((c) => <Cell key={c.name} fill={CLASS_COLOR[c.name] ?? "#94a3b8"} />)}
                </Pie>
                <Tooltip formatter={(v: number, _n: string, p: { payload?: { text: string } }) => p.payload?.text ?? v} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">A regular expression on the recorded failure message; a lower bound where no message was recorded (unknown).</p>
          <Source file={r.environment_audit.source} />
        </Card>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <Card title="Gates">
          <ul className="space-y-2">
            {r.gates.rows.map((g) => (
              <li key={g.gate} className="flex flex-wrap items-baseline justify-between gap-2 border-b border-slate-100 pb-2 last:border-0">
                <span className="min-w-0 flex-1">{g.gate}</span>
                <span className="tabular-nums text-slate-600">{g.measured.text}</span>
                <Badge tone={g.verdict === "MET" ? "green" : "amber"}>{g.verdict} ({g.threshold})</Badge>
              </li>
            ))}
          </ul>
          <Source file={r.gates.source} />
        </Card>

        <Card title="Test-to-file binding (both figures)">
          <ul className="space-y-2">
            {r.binding.rows.map((b) => (
              <li key={b.measure} className="flex flex-wrap justify-between gap-2 border-b border-slate-100 pb-2 last:border-0">
                <span className="min-w-0 flex-1">{b.measure}</span>
                <span className="tabular-nums text-slate-600">{b.value.text}</span>
              </li>
            ))}
          </ul>
          <Source file={r.binding.source} />
        </Card>

        <Card title="Leakage audit: co-change">
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="rounded border border-red-200 bg-red-50 p-3">
              <div className="text-2xl font-bold tabular-nums text-red-700">{lk.legacy_violations.n}/{lk.legacy_violations.d}</div>
              <div className="mt-1 text-xs text-red-800">leaking instances found (legacy static table)</div>
            </div>
            <div className="rounded border border-emerald-200 bg-emerald-50 p-3">
              <div className="text-2xl font-bold tabular-nums text-emerald-700">{lk.current_violations.n}/{lk.current_violations.d}</div>
              <div className="mt-1 text-xs text-emerald-800">now (per-instance trailing history)</div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-600">Legacy check: {lk.legacy_check}.</p>
          <p className="mt-1 text-xs text-slate-600">Current check: {lk.current_check}.</p>
          <Source file={lk.source} />
        </Card>

        <Card title="Environment / timeout audit of strict labels">
          <ul className="space-y-1.5">
            {r.environment_audit.labels_by_class.map((c) => (
              <li key={c.class} className="flex justify-between gap-2"><span>{c.class}</span><span className="tabular-nums text-slate-600">{c.labels.text}</span></li>
            ))}
          </ul>
          <h4 className="mb-1 mt-3 text-xs font-semibold uppercase text-slate-500">Strict instances</h4>
          <ul className="space-y-1.5">
            {r.environment_audit.instances.map((c) => (
              <li key={c.measure} className="flex justify-between gap-2"><span className="min-w-0">{c.measure}</span><span className="shrink-0 tabular-nums text-slate-600">{c.value.text}</span></li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-500">Measurement only: no label is removed.</p>
          <Source file={r.environment_audit.source} />
        </Card>
      </div>
    </div>
  );
}
