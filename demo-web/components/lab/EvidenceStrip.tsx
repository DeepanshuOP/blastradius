"use client";

import { useDoc, parsePrimary } from "../lib";
import { Prov } from "./common";

type Compare = {
  e1: { verdict: string; rows: { id: string; recall10: string; p_adj_text: string | null; delta: string | null; method: string }[]; source: string } | null;
  e3: { primary: string } | null;
  localization: { takeaway: string; source: string } | null;
};
type Results = { rq1_k10: { k: number; methods: { method: string; micro_recall: { n: number; d: number; text: string }; n: number }[]; source?: string } };

/** A small horizontal bar chart: each bar is a share between 0 and 1, printed at its end (no legend needed). */
export function MiniBars({ bars, label }: { bars: EvidenceBar[]; label: string }) {
  if (!bars.length) return null;
  return (
    <svg viewBox={`0 0 240 ${bars.length * 22 + 4}`} role="img" aria-label={label} className="ui mt-2 h-auto w-full max-w-[320px]">
      {bars.map((b, i) => (
        <g key={b.label} transform={`translate(0 ${i * 22 + 2})`}>
          <text x={0} y={13} fontSize={11} fill="var(--muted)">{b.label}</text>
          <rect x={92} y={2} width={Math.max(1, 90 * Math.min(1, Math.max(0, b.share)))} height={14} fill={b.strong ? "rgb(var(--blue-text-rgb))" : "var(--muted)"} />
          <text x={92 + Math.max(1, 90 * Math.min(1, Math.max(0, b.share))) + 5} y={13} fontSize={11} fill="var(--ink)">{b.text}</text>
        </g>
      ))}
    </svg>
  );
}

function Card({ title, big, body, source, bars, barsLabel }: EvidenceCard) {
  return (
    <div className="min-w-0 rounded-md border border-rule bg-panel p-3">
      <div className="mb-1.5"><Prov mode="bench" /></div>
      <p className="ui m-0 text-xs font-semibold uppercase tracking-wide text-muted">{title}</p>
      <div className="mono text-lg font-semibold leading-tight">{big}</div>
      <MiniBars bars={bars} label={barsLabel} />
      <p className="ui m-0 mt-2 text-sm leading-snug">{body}</p>
      <p className="cap m-0 mt-1.5 text-2xs">Source: <span className="mono text-2xs">{source}</span></p>
    </div>
  );
}

export type EvidenceBar = { label: string; share: number; text: string; strong?: boolean };
export type EvidenceCard = { title: string; big: string; body: string; source: string; bars: EvidenceBar[]; barsLabel: string };

/** The four headline results of the paper's evaluation, each read from a generated file and carried with that file. */
export function useEvidence(): EvidenceCard[] {
  const c = useDoc<Compare>("compare");
  const r = useDoc<Results>("results");
  const methods = r.doc?.rq1_k10.methods ?? [];
  const cochange = methods.find((m) => m.method === "co-change, all partner files");
  const history = methods.find((m) => m.method === "historical-frequency baseline");
  const pct = (m: { micro_recall: { n: number; d: number } }) => `${((100 * m.micro_recall.n) / m.micro_recall.d).toFixed(2)}%`;
  const ours = c.doc?.e1?.rows.find((x) => x.id === "ours");
  const best = c.doc?.e1?.rows.find((x) => x.id === "B7");
  const gate = c.doc?.e1?.verdict.match(/Gate 3 \([^)]*\) is (NOT MET|MET)/)?.[1];
  const e3 = c.doc?.e3 ? parsePrimary(c.doc.e3.primary) : null;
  return [
    { title: "RQ1 · co-change vs failure history", big: cochange && history ? `${pct(cochange)} vs ${pct(history)}` : "…",
      body: cochange && history ? `Micro recall at k = ${r.doc?.rq1_k10.k} over ${cochange.n} instances: co-change (all partner files) recovers ${cochange.micro_recall.n} of ${cochange.micro_recall.d.toLocaleString("en-US")} failing test files; failure history (historical frequency) ${history.micro_recall.n} of ${history.micro_recall.d.toLocaleString("en-US")}.` : "Loading.",
      source: r.doc?.rq1_k10.source ?? "paper/generated/rq1.md",
      bars: cochange && history ? [{ label: "co-change", share: cochange.micro_recall.n / cochange.micro_recall.d, text: pct(cochange), strong: true },
        { label: "failure history", share: history.micro_recall.n / history.micro_recall.d, text: pct(history) }] : [],
      barsLabel: "Micro recall at k = 10: co-change against failure history" },
    { title: "E1 · ranker, Gate 3", big: gate ? `Gate 3: ${gate}` : "…",
      body: ours && best ? `Recall@10 ${ours.recall10} against ${best.recall10} for ${best.method}; Holm-adjusted p = ${best.p_adj_text}, Cliff's delta ${best.delta}.` : "Loading.",
      source: c.doc?.e1?.source ?? "paper/generated/rq2_predictor.md",
      bars: ours && best ? [{ label: "ranker", share: parseFloat(ours.recall10), text: ours.recall10, strong: true },
        { label: best.method.replace(/ \(.*\)$/, "").slice(0, 16), share: parseFloat(best.recall10), text: best.recall10 }] : [],
      barsLabel: "Recall at 10: the ranker against the strongest baseline" },
    { title: "E3 · repair, R2 vs R1", big: e3 ? `p = ${e3.p}` : "…",
      body: e3 ? `${e3.model}, n = ${e3.n}: R2 fixes ${e3.r2[0]}/${e3.r2[1]}, R1 ${e3.r1[0]}/${e3.r1[1]} (R2 only ${e3.r2Only}, R1 only ${e3.r1Only}); exact McNemar, one-sided.` : "Loading.",
      source: "paper/generated/rq4_repair.md",
      bars: e3 ? [{ label: "R2 (ours)", share: e3.r2[0] / Math.max(1, e3.r2[1]), text: `${e3.r2[0]}/${e3.r2[1]}`, strong: true },
        { label: "R1", share: e3.r1[0] / Math.max(1, e3.r1[1]), text: `${e3.r1[0]}/${e3.r1[1]}` }] : [],
      barsLabel: "Plausible fixes by arm" },
    { title: "Retrieval · change-aware", big: c.doc?.localization ? (c.doc.localization.takeaway.match(/(\d+)\/70/)?.[0] ?? "…") : "…",
      body: c.doc?.localization?.takeaway ?? "Loading.", source: c.doc?.localization?.source ?? "paper/generated/rq5_retrieval.md",
      bars: (() => { const m = c.doc?.localization?.takeaway.match(/(\d+)\/70/); return m ? [{ label: "hit@3", share: Number(m[1]) / 70, text: `${m[1]}/70`, strong: true }] : []; })(),
      barsLabel: "Seeded function among the top three retrieved chunks" },
  ];
}

/** Four headline results of the paper's evaluation, each shown with the file it was read from. */
export function EvidenceStrip() {
  const cards = useEvidence();
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Key results">
      {cards.map((c) => <Card key={c.title} {...c} />)}
    </div>
  );
}
