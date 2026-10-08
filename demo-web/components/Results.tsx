"use client";

import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ResultsDoc } from "./types";
import { Badge, Card, Source, METHOD_SHORT as SHORT } from "./ui";


export default function Results({ r }: { r: ResultsDoc }) {
  const rq = r.rq1_k10;
  const recall = rq.methods.map((m) => ({ name: SHORT[m.method] ?? m.method, recall: m.mean_recall }));
  const funnel = r.runs_funnel.stages.map((s) => ({ name: s.stage, count: s.count }));
  const lk = r.leakage;

  return (
    <div className="space-y-5">
      <Card title={`RQ1: predictors at k = ${rq.k} (scored on the same instances)`}>
        <div className="overflow-x-auto">
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
        <h4 className="mb-1 mt-5 text-xs font-semibold uppercase text-slate-500">Mean recall per method</h4>
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

      <Card title="Runs funnel: from every discovered run to strict benchmark instances">
        <div className="h-80 w-full">
          <ResponsiveContainer>
            <BarChart data={funnel} layout="vertical" margin={{ left: 8, right: 72, top: 4, bottom: 4 }}>
              <CartesianGrid horizontal={false} stroke="#e2e8f0" />
              <XAxis type="number" scale="log" domain={[100, "auto"]} allowDataOverflow tick={{ fontSize: 12, fill: "#64748b" }}
                tickFormatter={(v: number) => v.toLocaleString()} />
              <YAxis type="category" dataKey="name" width={190} tick={{ fontSize: 11, fill: "#334155" }} />
              <Tooltip formatter={(v: number) => v.toLocaleString()} />
              <Bar dataKey="count" fill="#64748b" radius={[0, 3, 3, 0]} isAnimationActive={false}>
                <LabelList dataKey="count" position="right" formatter={(v: number) => v.toLocaleString()} style={{ fontSize: 12, fill: "#334155" }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-slate-500">Log scale. Each stage is the intersection with the previous one.</p>
        <Source file={r.runs_funnel.source} />
      </Card>

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
