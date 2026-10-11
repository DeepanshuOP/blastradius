"use client";

import { useEffect, useState } from "react";
import { Badge, Card, Mono } from "./ui";

type Cell = { value: "yes" | "no" | "not_reported"; source: string; note?: string; proof?: string[] };
type Matrix = {
  columns: { id: string; label: string }[];
  rows: { id: string; label: string; cells: Record<string, Cell> }[];
  safety: { claim: string; tests: string[] }[];
};
type Tbl = { columns: string[]; rows: string[][] };
type E1Row = { id: string; method: string; n: number; recall10: string; map: string; ci: [number, number]; p_adj: number | null; p_adj_text: string | null; delta: string | null; magnitude: string | null };
type Arm = { arm: string; label: string; k: number; n: number; wilson: [number, number] };
type LocRow = { mode: string; k: number; n: number; wilson: [number, number]; cell: string; mrr: string };
type CostRow = {
  model: string; arm: string; n: number; accepted: number; calls: number; prompt_tokens: number; completion_tokens: number;
  in_per_task: number | null; out_per_task: number | null; in_per_fix: number | null; out_per_fix: number | null;
  usd_list_total: number | null; usd_list_per_task: number | null; usd_list_per_fix: number | null;
};
type Run = { model: string; calls: number; prompt_tokens: number; completion_tokens: number; tokens_per_call: number; usd_list_per_call: number | null; file: string };
type CompareDoc = {
  generated_at_git_sha: string;
  matrix: Matrix;
  e1: { source: string; n: number; split: string; test: string; verdict: string; rows: E1Row[]; takeaway: string } | null;
  e3: {
    source: string; models: { model: string; n: number; arms: Arm[] }[]; primary: string; secondary: Tbl | null; interim: boolean;
    interim_text: string; takeaway: string; applier_note: string;
  } | null;
  localization: {
    source: string; variants: Record<string, LocRow[]>; paired: Tbl | null; takeaway?: string;
    l4_vs_l1: { variant: string; r2_only: number; r1_only: number; p: string; n: number }[];
  } | null;
  table2: { source: string; rows: { work: string; result: string; data: string; lit_number: number | null; title?: string; url?: string }[] };
  cost: {
    prices: { date: string; url: string; usd_per_million_in_out: Record<string, [number, number]> };
    ledger: { paid_usd: number; by_model: Record<string, { calls: number; tokens: number }> };
    e3: CostRow[]; bot: Run[]; bot_live: { model: string; tokens: number; file: string } | null; ask: Run[]; context: string;
  } | null;
  time: {
    e1: { source: string; n: number; candidates_median: string; history_drop_recall10?: number;
          rows: { id: string; method: string; first_fail_pos: string; recall_first_10pct: string; apfd: string; suite_frac_full_recall: string }[] } | null;
    e3_detection: { source: string; rows: Record<string, string>[]; takeaway: string } | null;
  };
  figures: string[];
};

const fmt = (x: number | null, d = 0) => (x === null ? "n/a" : x.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }));
const ci = (w: [number, number]) => `[${w[0].toFixed(3)}, ${w[1].toFixed(3)}]`;

function Th({ children }: { children: React.ReactNode }) {
  return <th className="whitespace-nowrap px-2 py-1.5 text-left font-semibold">{children}</th>;
}
function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`whitespace-nowrap px-2 py-1 tabular-nums text-slate-800 ${className}`}>{children}</td>;
}
function Take({ children }: { children: React.ReactNode }) {
  return <p className="mt-3 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-800"><span className="font-semibold">In plain words: </span>{children}</p>;
}
function Scroll({ children }: { children: React.ReactNode }) {
  return <div className="overflow-x-auto"><table className="min-w-full text-xs">{children}</table></div>;
}
function Interim({ text }: { text: string }) {
  return <p className="mb-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">Interim: {text}. These numbers move when the run is synced.</p>;
}
function TblView({ t }: { t: Tbl }) {
  return (
    <Scroll>
      <thead><tr className="border-b border-slate-200 text-slate-500">{t.columns.map((c) => <Th key={c}>{c}</Th>)}</tr></thead>
      <tbody>{t.rows.map((r, i) => <tr key={i} className="border-b border-slate-100 last:border-0">{r.map((c, j) => <Td key={j}>{c}</Td>)}</tr>)}</tbody>
    </Scroll>
  );
}

const MARK: Record<Cell["value"], { text: string; cls: string }> = {
  yes: { text: "✓", cls: "text-emerald-700 font-bold" },
  no: { text: "✗", cls: "text-red-700 font-bold" },
  not_reported: { text: "not reported", cls: "text-slate-400 text-[11px]" },
};

function MatrixPanel({ m }: { m: Matrix }) {
  const [sel, setSel] = useState<{ row: string; col: string } | null>(null);
  const cell = sel ? m.rows.find((r) => r.id === sel.row)?.cells[sel.col] : undefined;
  const rowLabel = sel ? m.rows.find((r) => r.id === sel.row)?.label : "";
  const colLabel = sel ? m.columns.find((c) => c.id === sel.col)?.label : "";
  return (
    <Card title="1 · What BlastRadius does that others don't" step={1}>
      <p className="mb-3 text-xs text-slate-600">
        A mark for another work is shown only where its summary in <Mono>docs/LITERATURE.md</Mono> (written from titles and abstracts) or this
        project's own results establish it; otherwise the cell says <em>not reported</em>, which is not a claim that the capability is absent.
        Hover a cell for its source; click it for the evidence (for BlastRadius, the test that proves it).
      </p>
      <Scroll>
        <thead>
          <tr className="border-b border-slate-200 align-bottom text-slate-500">
            <Th>capability</Th>
            {m.columns.map((c) => <th key={c.id} className={`px-2 py-1.5 text-left font-semibold ${c.id === "br" ? "text-slate-900" : ""}`}>{c.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {m.rows.map((r) => (
            <tr key={r.id} className="border-b border-slate-100 last:border-0">
              <td className="px-2 py-1.5 text-slate-800">{r.label}</td>
              {m.columns.map((c) => {
                const x = r.cells[c.id];
                const mk = MARK[x.value];
                return (
                  <td key={c.id} className={`px-2 py-1.5 ${c.id === "br" ? "bg-sky-50" : ""}`}>
                    <button title={`${x.source}${x.note ? ` — ${x.note}` : ""}`} onClick={() => setSel({ row: r.id, col: c.id })}
                      className={`${mk.cls} rounded px-1 hover:bg-slate-100`}>{mk.text}</button>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </Scroll>
      {cell && (
        <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 p-3 text-xs">
          <p className="font-semibold text-slate-800">{rowLabel} · {colLabel} · {MARK[cell.value].text === "not reported" ? "not reported" : cell.value}</p>
          <p className="mt-1">source: <Mono>{cell.source}</Mono></p>
          {cell.note && <p className="mt-1 text-slate-600">{cell.note}</p>}
          {cell.proof && cell.proof.length > 0 && (
            <div className="mt-1">proved by: {cell.proof.map((p) => <div key={p}><Mono>{p}</Mono></div>)}</div>
          )}
        </div>
      )}
    </Card>
  );
}

function E1Table({ e1 }: { e1: NonNullable<CompareDoc["e1"]> }) {
  return (
    <div>
      <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">(a) E1: predict which test files a change breaks</h4>
      <p className="mb-2 text-xs text-slate-600">n = {e1.n} test instances ({e1.split}). Test: {e1.test}</p>
      <Scroll>
        <thead><tr className="border-b border-slate-200 text-slate-500">
          <Th>method</Th><Th>n</Th><Th>Recall@10 (mean ± sd over seeds)</Th><Th>95% CI (bootstrap)</Th><Th>MAP</Th><Th>vs ours: Holm-adj. p</Th><Th>Cliff&apos;s δ</Th><Th>magnitude</Th>
        </tr></thead>
        <tbody>
          {e1.rows.map((r) => (
            <tr key={r.id} className={`border-b border-slate-100 last:border-0 ${r.id === "ours" ? "bg-sky-50" : ""}`}>
              <Td className="whitespace-normal">{r.method}</Td><Td>{r.n}</Td><Td>{r.recall10}</Td><Td>[{r.ci[0].toFixed(3)}, {r.ci[1].toFixed(3)}]</Td>
              <Td>{r.map}</Td><Td>{r.p_adj_text ?? "n/a"}</Td><Td>{r.delta ?? "n/a"}</Td><Td>{r.magnitude ?? "n/a"}</Td>
            </tr>
          ))}
        </tbody>
      </Scroll>
      <p className="mt-2 text-xs text-slate-700"><span className="font-semibold">Gate 3 verdict (as generated): </span>{e1.verdict}</p>
      <Take>{e1.takeaway}</Take>
    </div>
  );
}

function E3Table({ e3 }: { e3: NonNullable<CompareDoc["e3"]> }) {
  return (
    <div>
      <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">(b) E3: repair arms on BR-Seeded, standard variant</h4>
      {e3.interim && <Interim text={e3.interim_text} />}
      <Scroll>
        <thead><tr className="border-b border-slate-200 text-slate-500"><Th>model</Th><Th>arm</Th><Th>n</Th><Th>plausible fix (full suite green)</Th><Th>95% Wilson CI</Th></tr></thead>
        <tbody>
          {e3.models.flatMap((m) => m.arms.map((a) => (
            <tr key={m.model + a.arm} className="border-b border-slate-100 last:border-0">
              <Td>{m.model}</Td><Td className="whitespace-normal">{a.label}</Td><Td>{a.n}</Td><Td>{a.k}/{a.n}</Td><Td>{ci(a.wilson)}</Td>
            </tr>
          )))}
        </tbody>
      </Scroll>
      <p className="mt-2 text-xs text-slate-700"><span className="font-semibold">Primary pre-registered test: </span>{e3.primary}</p>
      {e3.secondary && <div className="mt-2"><TblView t={e3.secondary} /></div>}
      <p className="mt-2 text-xs text-slate-500">{e3.applier_note} Strict: <Mono>apply_blocks</Mono> (<Mono>tests/test_agents_repair.py::test_search_must_match_exactly_once</Mono>);
        tolerant: <Mono>apply_blocks_tolerant</Mono> (<Mono>tests/test_bot.py::test_strict_apply_rejects_the_real_replies_and_tolerant_apply_fixes_them</Mono>).</p>
      <Take>{e3.takeaway}</Take>
    </div>
  );
}

function LocTable({ l }: { l: NonNullable<CompareDoc["localization"]> }) {
  const std = l.variants.standard ?? [];
  const hard = l.variants.hard ?? [];
  return (
    <div>
      <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">(c) Localization: is the seeded function among the top 3 chunks?</h4>
      <Scroll>
        <thead><tr className="border-b border-slate-200 text-slate-500"><Th>mode</Th><Th>n</Th><Th>standard hit@3</Th><Th>95% Wilson CI</Th><Th>hard hit@3</Th><Th>95% Wilson CI</Th></tr></thead>
        <tbody>
          {std.map((s, i) => (
            <tr key={s.mode} className="border-b border-slate-100 last:border-0">
              <Td className="whitespace-normal">{s.mode}</Td><Td>{s.n}</Td><Td>{s.cell}</Td><Td>{ci(s.wilson)}</Td>
              <Td>{hard[i]?.cell ?? "n/a"}</Td><Td>{hard[i] ? ci(hard[i].wilson) : "n/a"}</Td>
            </tr>
          ))}
        </tbody>
      </Scroll>
      <p className="mt-2 text-xs text-slate-700">
        <span className="font-semibold">Tests: </span>exact McNemar, two-sided.{" "}
        {l.l4_vs_l1.map((x) => `L4 vs L1, ${x.variant}: ${x.r2_only} only L4, ${x.r1_only} only L1, p = ${x.p} (n = ${x.n}).`).join(" ")}
      </p>
      {l.paired && <div className="mt-2"><TblView t={l.paired} /></div>}
      {l.takeaway && <Take>{l.takeaway}</Take>}
    </div>
  );
}

function SameData({ d }: { d: CompareDoc }) {
  return (
    <Card title="2 · Same data, same split (fair comparisons only)" step={2}>
      <div className="grid gap-6 lg:grid-cols-[3fr_2fr]">
        <div className="space-y-8">
          {d.e1 ? <E1Table e1={d.e1} /> : <p>E1 results not generated.</p>}
          {d.e3 ? <E3Table e3={d.e3} /> : <p>E3 results not generated.</p>}
          {d.localization ? <LocTable l={d.localization} /> : <p>Retrieval results not generated.</p>}
        </div>
        <div className="space-y-4">
          {d.figures.map((f) => (
            <figure key={f} className="rounded-lg border border-slate-200 p-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={f} alt={f.includes("fig6") ? "E3 plausible-fix rate per arm" : "Localization hit@3 per retrieval mode"} className="w-full" />
              <figcaption className="mt-1 text-xs text-slate-500">{f.includes("fig6") ? "fig6: E3 arms, standard variant, 95% Wilson" : "fig7: retrieval modes, hit@3"}</figcaption>
            </figure>
          ))}
        </div>
      </div>
    </Card>
  );
}

function OtherData({ t }: { t: CompareDoc["table2"] }) {
  return (
    <Card title="3 · Published numbers on other data (not comparable)" step={3}>
      <p className="mb-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-900">
        Different datasets and bug types. Shown for context only; we do not claim to beat these numbers.
      </p>
      <Scroll>
        <thead><tr className="border-b border-slate-200 text-slate-500"><Th>work</Th><Th>reported result</Th><Th>their data</Th><Th>source</Th></tr></thead>
        <tbody>
          {t.rows.map((r) => (
            <tr key={r.work} className="border-b border-slate-100 last:border-0">
              <Td className="whitespace-normal">{r.work}</Td><Td className="whitespace-normal">{r.result}</Td><Td className="whitespace-normal">{r.data}</Td>
              <Td className="whitespace-normal">{r.url ? <a className="text-sky-700 underline" href={r.url} target="_blank" rel="noreferrer">#{r.lit_number} {r.title}</a> : "n/a"}</Td>
            </tr>
          ))}
        </tbody>
      </Scroll>
      <p className="mt-2 text-xs text-slate-500">source: {t.source}</p>
    </Card>
  );
}

function CostPanel({ c }: { c: CompareDoc["cost"] }) {
  if (!c) return <Card title="4 · Cost" step={4}><p>Not generated: run <Mono>make cost-report</Mono>.</p></Card>;
  const prices = Object.entries(c.prices.usd_per_million_in_out).map(([m, p]) => `${m} $${p[0]} in / $${p[1]} out`).join("; ");
  return (
    <Card title="4 · Cost" step={4}>
      <p className="text-base font-semibold text-slate-900">USD actually paid: ${c.ledger.paid_usd.toFixed(2)} <span className="text-xs font-normal text-slate-500">(Groq free tier)</span></p>
      <p className="mt-1 text-xs text-slate-600">
        At Groq&apos;s paid list prices ({c.prices.date}, <a className="text-sky-700 underline" href={c.prices.url}>{c.prices.url}</a>; per million tokens: {prices}) the recorded tokens
        would cost the amounts in the right-hand columns. That is what it would cost, not money spent.
      </p>
      <h4 className="mb-1 mt-4 text-xs font-semibold uppercase tracking-wide text-slate-500">E3 repair, standard variant (tokens per task and per plausible fix)</h4>
      <Scroll>
        <thead><tr className="border-b border-slate-200 text-slate-500">
          <Th>model</Th><Th>arm</Th><Th>tasks</Th><Th>fixes</Th><Th>in tok / task</Th><Th>out tok / task</Th><Th>in tok / fix</Th><Th>out tok / fix</Th><Th>USD at list / task</Th><Th>USD at list / fix</Th>
        </tr></thead>
        <tbody>
          {c.e3.map((r) => (
            <tr key={r.model + r.arm} className="border-b border-slate-100 last:border-0">
              <Td>{r.model}</Td><Td>{r.arm}</Td><Td>{r.n}</Td><Td>{r.accepted}</Td><Td>{fmt(r.in_per_task)}</Td><Td>{fmt(r.out_per_task)}</Td>
              <Td>{fmt(r.in_per_fix)}</Td><Td>{fmt(r.out_per_fix)}</Td><Td>{fmt(r.usd_list_per_task, 5)}</Td><Td>{fmt(r.usd_list_per_fix, 5)}</Td>
            </tr>
          ))}
        </tbody>
      </Scroll>
      <h4 className="mb-1 mt-4 text-xs font-semibold uppercase tracking-wide text-slate-500">PR bot, recorded run(s)</h4>
      <Scroll>
        <thead><tr className="border-b border-slate-200 text-slate-500"><Th>model</Th><Th>model calls</Th><Th>input tokens</Th><Th>output tokens</Th><Th>tokens / call</Th><Th>USD at list / call</Th></tr></thead>
        <tbody>
          {c.bot.map((r) => (
            <tr key={r.file} className="border-b border-slate-100 last:border-0">
              <Td>{r.model}</Td><Td>{r.calls}</Td><Td>{fmt(r.prompt_tokens)}</Td><Td>{fmt(r.completion_tokens)}</Td><Td>{fmt(r.tokens_per_call)}</Td><Td>{fmt(r.usd_list_per_call, 5)}</Td>
            </tr>
          ))}
        </tbody>
      </Scroll>
      {c.bot_live && (
        <p className="mt-2 text-xs text-slate-600">
          Live PR #1 run: <Mono>{c.bot_live.model}</Mono>, {fmt(c.bot_live.tokens)} tokens in one run (the comment records no input/output split, so no dollar figure is computed).
        </p>
      )}
      <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
        <span className="font-semibold">Context, not a comparison. </span>{c.context}
      </div>
    </Card>
  );
}

function TimePanel({ t }: { t: CompareDoc["time"] }) {
  return (
    <Card title="5 · Time" step={5}>
      {t.e1 && (
        <div>
          <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">BR-Bench, chronological test split (n = {t.e1.n})</h4>
          <Scroll>
            <thead><tr className="border-b border-slate-200 text-slate-500">
              <Th>order</Th><Th>mean position of the first failing test file</Th><Th>failing files found in the first 10% of the suite (Recall@10%)</Th><Th>suite fraction needed for full recall</Th><Th>APFD</Th>
            </tr></thead>
            <tbody>
              {t.e1.rows.map((r) => (
                <tr key={r.id} className={`border-b border-slate-100 last:border-0 ${r.id === "ours" ? "bg-sky-50" : ""}`}>
                  <Td className="whitespace-normal">{r.method}</Td><Td>{r.first_fail_pos}</Td><Td>{r.recall_first_10pct}</Td><Td>{r.suite_frac_full_recall}</Td><Td>{r.apfd}</Td>
                </tr>
              ))}
            </tbody>
          </Scroll>
          <p className="mt-2 text-xs text-slate-500">Candidate test files per instance: {t.e1.candidates_median} Source: {t.e1.source}.
            The share of the suite run before the first failure is not a generated BR-Bench number; position, Recall@10% and the suite fraction are.</p>
        </div>
      )}
      {t.e3_detection && (
        <div className="mt-6">
          <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">The honest negative: fresh repositories with no failure history (E3 detection, BR-Seeded)</h4>
          <TblView t={{ columns: Object.keys(t.e3_detection.rows[0]), rows: t.e3_detection.rows.map((r) => Object.values(r)) }} />
          <Take>{t.e3_detection.takeaway}</Take>
          {t.e1?.history_drop_recall10 !== undefined && (
            <p className="mt-2 text-xs text-slate-600">Why: removing the failure-history features costs {t.e1.history_drop_recall10.toFixed(3)} Recall@10 on BR-Bench (ablation), and a fresh repository has none.</p>
          )}
        </div>
      )}
    </Card>
  );
}

function SafetyPanel({ m }: { m: Matrix }) {
  return (
    <Card title="6 · Safety" step={6}>
      <p className="mb-2 text-xs text-slate-600">Each line is backed by a named test; <Mono>make demo-check</Mono> runs them.</p>
      <ul className="space-y-2">
        {m.safety.map((s) => (
          <li key={s.claim} className="flex gap-2">
            <span className="mt-0.5 text-emerald-700">✓</span>
            <div>
              <span className="text-slate-900">{s.claim}</span>
              {s.tests.map((t) => <div key={t}><Mono className="text-slate-600">{t}</Mono></div>)}
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}

export default function Compare() {
  const [d, setD] = useState<CompareDoc | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    fetch("/data/compare.json", { cache: "no-store" })
      .then((r) => { if (!r.ok) throw new Error(`compare.json: HTTP ${r.status}`); return r.json() as Promise<CompareDoc>; })
      .then(setD).catch((e) => setErr(String(e)));
  }, []);
  if (err) return <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">Could not load /data/compare.json ({err}). Run <Mono>make demo-data</Mono>.</p>;
  if (!d) return <p className="text-sm text-slate-500">Loading…</p>;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <Badge tone="slate">every number is read from paper/generated, the usage ledger or a script</Badge>
        <span>data at <Mono>{d.generated_at_git_sha.slice(0, 10)}</Mono></span>
      </div>
      <div id="compare-panel-1"><MatrixPanel m={d.matrix} /></div>
      <div id="compare-panel-2"><SameData d={d} /></div>
      <div id="compare-panel-3"><OtherData t={d.table2} /></div>
      <div id="compare-panel-4"><CostPanel c={d.cost} /></div>
      <div id="compare-panel-5"><TimePanel t={d.time} /></div>
      <div id="compare-panel-6"><SafetyPanel m={d.matrix} /></div>
    </div>
  );
}
