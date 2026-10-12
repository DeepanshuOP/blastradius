"use client";

import { useDoc, parsePrimary } from "../lib";
import { Prov } from "./common";

type Compare = {
  e1: { verdict: string; rows: { id: string; recall10: string; p_adj_text: string | null; delta: string | null; method: string }[]; source: string } | null;
  e3: { primary: string } | null;
  localization: { takeaway: string; source: string } | null;
};
type Results = { rq1_k10: { k: number; methods: { method: string; micro_recall: { n: number; d: number; text: string }; n: number }[]; source?: string } };

function Card({ title, big, body, source }: { title: string; big: string; body: string; source: string }) {
  return (
    <div className="min-w-0 rounded-md border border-rule bg-panel p-3">
      <div className="mb-1 flex items-center justify-between gap-2"><span className="ui text-xs font-semibold uppercase tracking-wide text-muted">{title}</span><Prov mode="bench" /></div>
      <div className="mono text-lg font-semibold leading-tight">{big}</div>
      <p className="ui m-0 mt-1 text-sm leading-snug">{body}</p>
      <p className="cap m-0 mt-1.5 text-2xs">Source: <span className="mono text-2xs">{source}</span></p>
    </div>
  );
}

export type EvidenceCard = { title: string; big: string; body: string; source: string };

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
      source: r.doc?.rq1_k10.source ?? "paper/generated/rq1.md" },
    { title: "E1 · ranker, Gate 3", big: gate ? `Gate 3: ${gate}` : "…",
      body: ours && best ? `Recall@10 ${ours.recall10} against ${best.recall10} for ${best.method}; Holm-adjusted p = ${best.p_adj_text}, Cliff's delta ${best.delta}.` : "Loading.",
      source: c.doc?.e1?.source ?? "paper/generated/rq2_predictor.md" },
    { title: "E3 · repair, R2 vs R1", big: e3 ? `p = ${e3.p}` : "…",
      body: e3 ? `${e3.model}, n = ${e3.n}: R2 fixes ${e3.r2[0]}/${e3.r2[1]}, R1 ${e3.r1[0]}/${e3.r1[1]} (R2 only ${e3.r2Only}, R1 only ${e3.r1Only}); exact McNemar, one-sided.` : "Loading.",
      source: "paper/generated/rq4_repair.md" },
    { title: "Retrieval · change-aware", big: c.doc?.localization ? (c.doc.localization.takeaway.match(/(\d+)\/70/)?.[0] ?? "…") : "…",
      body: c.doc?.localization?.takeaway ?? "Loading.", source: c.doc?.localization?.source ?? "paper/generated/rq5_retrieval.md" },
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
