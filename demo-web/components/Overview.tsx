"use client";

import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { OverviewDoc } from "./types";
import { Card, Source, methodName, ratePct } from "./ui";

const WHY: [string, string][] = [
  ["Real CI ground truth, not proxies",
    "Labels come from tests that actually failed in GitHub Actions runs, not from co-change, coverage or mutation proxies."],
  ["Per PR, per test, filtered",
    "Each label is one test on one pull-request run that failed at head, did not fail at the base run, and is not flaky across sibling runs."],
  ["Public and reproducible",
    "Every number regenerates from the checked-in pipeline with one command, and both predictors are leakage-audited per instance."],
];

function colour(method: string): string {
  if (method.startsWith("historical")) return "#2563eb";
  if (method.startsWith("co-change, all")) return "#ea580c";
  if (method.startsWith("co-change")) return "#fdba74";
  return "#94a3b8";
}

export default function Overview({ o }: { o: OverviewDoc }) {
  const h = o.headline;
  const data = h.methods.map((m) => ({
    name: methodName(m.method), method: m.method, recall: (100 * m.micro_recall.n) / m.micro_recall.d, text: m.micro_recall.text,
  }));
  const co = h.methods.find((m) => m.method === "co-change, all partner files");
  const hist = h.methods.find((m) => m.method === "historical-frequency baseline");
  const n = h.methods[0]?.n;
  const b = o.binding;

  return (
    <div className="space-y-6">
      <section className="rounded-xl bg-gradient-to-br from-slate-900 to-slate-700 px-6 py-8 text-white shadow-md">
        <p className="text-xs font-semibold uppercase tracking-widest text-slate-300">Execution-grounded change impact</p>
        <h2 className="mt-2 max-w-3xl text-2xl font-bold leading-snug sm:text-3xl">
          BlastRadius mines real GitHub Actions runs to record which tests each pull request actually broke, then measures how well predictors could have told in advance.
        </h2>
      </section>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {o.kpis.map((k) => (
          <div key={k.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm" title={`source: ${k.source}`}>
            <div className="text-2xl font-bold tabular-nums text-slate-900">{k.value.toLocaleString()}</div>
            <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">{k.label}</div>
          </div>
        ))}
        <div className="col-span-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm" title={`source: ${b.source}`}>
          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
            <span className="text-2xl font-bold tabular-nums text-slate-900">{ratePct(b.combined)}</span>
            <span className="text-lg font-semibold tabular-nums text-slate-600">{ratePct(b.full_confidence)}</span>
          </div>
          <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
            test-to-file binding: combined ({b.combined.n.toLocaleString()}/{b.combined.d.toLocaleString()}) · full confidence ({b.full_confidence.n.toLocaleString()}/{b.full_confidence.d.toLocaleString()})
          </div>
        </div>
      </div>

      <Card title={`Headline: of the tests that actually failed, how many did each predictor name? (micro recall at k = ${h.k})`}>
        <div className="h-72 w-full">
          <ResponsiveContainer>
            <BarChart data={data} layout="vertical" margin={{ left: 8, right: 130, top: 4, bottom: 4 }}>
              <CartesianGrid horizontal={false} stroke="#e2e8f0" />
              <XAxis type="number" domain={[0, (max: number) => Math.ceil(max / 10) * 10]} tickFormatter={(v: number) => `${v}%`} tick={{ fontSize: 12, fill: "#64748b" }} />
              <YAxis type="category" dataKey="name" width={170} tick={{ fontSize: 13, fill: "#334155" }} />
              <Tooltip formatter={(_v: number, _n: string, p: { payload?: { text: string } }) => p.payload?.text ?? ""} />
              <Bar dataKey="recall" radius={[0, 4, 4, 0]} isAnimationActive={false} barSize={28}>
                {data.map((d) => <Cell key={d.method} fill={colour(d.method)} />)}
                <LabelList dataKey="text" position="right" style={{ fontSize: 12, fill: "#334155" }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        {co && hist && (
          <p className="mt-2 text-base font-medium text-slate-800">
            Of the tests that actually failed, co-change predicted {ratePct(co.micro_recall)}; historical failure frequency {ratePct(hist.micro_recall)} (n={n}).
          </p>
        )}
        <Source file={h.source} />
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {WHY.map(([t, d]) => (
          <div key={t} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="font-semibold text-slate-900">{t}</h3>
            <p className="mt-2 text-sm text-slate-600">{d}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
