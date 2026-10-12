"use client";

import { useState } from "react";
import { useDoc } from "./lib";
import { Caption, Mono, NumTable, TD, TH } from "./ui";

type Cell = { value: "yes" | "no" | "partial" | "not_reported" | "not_documented"; source: string; note?: string; proof?: string[] };
type Matrix = {
  columns: { id: string; label: string }[];
  rows: { id: string; label: string; cells: Record<string, Cell> }[];
  safety: { claim: string; tests: string[] }[];
  products?: { title: string; checked: string; note: string; columns: { id: string; label: string }[]; rows: { id: string; label: string; cells: Record<string, Cell> }[] };
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
    lab_ledger?: { paid_usd: number; by_model: Record<string, { calls: number; tokens: number }> }; lab?: Run[];
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


const WORD: Record<Cell["value"], string> = { yes: "yes", no: "no", partial: "partial", not_reported: "not reported", not_documented: "not documented" };
const urls = (src: string) => src.split(/\s+and\s+|[\s,]+/).filter((x) => /^https:\/\//.test(x));

function Table({ children, min = 640 }: { children: React.ReactNode; min?: number }) {
  return <div className="overflow-x-auto" tabIndex={0} role="region" aria-label="Table, scrolls horizontally"><table className="border-collapse" style={{ minWidth: min, width: "100%" }}>{children}</table></div>;
}
function Interim({ text }: { text: string }) {
  return <p className="ui m-0 mb-2 border border-rule bg-panel px-3 py-2 text-[14px]">Interim: {text}. These numbers move when the run is synced.</p>;
}
function TblView({ t }: { t: Tbl }) {
  return (
    <Table min={480}>
      <thead><tr>{t.columns.map((c, i) => <th key={c} className={`${TH} ${i > 0 ? "text-right" : ""}`}>{c}</th>)}</tr></thead>
      <tbody>{t.rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j} className={`${TD} ${j > 0 ? "text-right" : ""}`}>{c}</td>)}</tr>)}</tbody>
    </Table>
  );
}
function Take({ children }: { children: React.ReactNode }) {
  return <p className="prose-col"><span className="font-semibold">What this shows.</span> {children}</p>;
}
function Panel({ id, title, intro, children }: { id: string; title: string; intro?: React.ReactNode; children: React.ReactNode }) {
  return (
    <section id={id} aria-labelledby={`h-${id}`} className="scroll-mt-20 border-t border-rule pt-2">
      <h3 id={`h-${id}`}>{title}</h3>
      {intro && <div className="prose-col">{intro}</div>}
      {children}
    </section>
  );
}

function MatrixTable({ columns, rows, highlight, caption, source }: {
  columns: { id: string; label: string }[]; rows: { id: string; label: string; cells: Record<string, Cell> }[];
  highlight: string; caption: React.ReactNode; source?: string;
}) {
  const [sel, setSel] = useState<{ row: string; col: string } | null>(null);
  const cell = sel ? rows.find((r) => r.id === sel.row)?.cells[sel.col] : undefined;
  const rowLabel = sel ? rows.find((r) => r.id === sel.row)?.label : "";
  const colLabel = sel ? columns.find((c) => c.id === sel.col)?.label : "";
  return (
    <>
      <NumTable caption={caption} source={source}>
        <table className="border-collapse" style={{ minWidth: 560 + columns.length * 90, width: "100%" }}>
          <thead>
            <tr><th className={TH}>capability</th>{columns.map((c) => <th key={c.id} className={`${TH} ${c.id === highlight ? "text-ink" : ""}`}>{c.label}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className={TD}>{r.label}</td>
                {columns.map((c) => {
                  const x = r.cells[c.id];
                  const quiet = x.value === "not_reported" || x.value === "not_documented";
                  return (
                    <td key={c.id} className={`${TD} ${c.id === highlight ? "bg-panel" : ""}`}>
                      <button className={`ui text-left text-[14px] underline decoration-rule underline-offset-2 ${quiet ? "text-muted" : "font-medium text-ink"}`}
                        aria-label={`${r.label}, ${c.label}: ${WORD[x.value]}. Show the source.`}
                        onClick={() => setSel({ row: r.id, col: c.id })}>{WORD[x.value]}</button>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </NumTable>
      <div aria-live="polite" className="prose-col">
        {cell ? (
          <div className="ui border border-rule bg-panel p-3 text-[14px]">
            <p className="m-0 font-medium">{rowLabel}, {colLabel}: {WORD[cell.value]}</p>
            <p className="mb-0 mt-1">
              Source: {urls(cell.source).length
                ? urls(cell.source).map((u, i) => <span key={u}>{i > 0 ? "; " : ""}<a href={u} target="_blank" rel="noreferrer">{u}</a></span>)
                : <Mono>{cell.source}</Mono>}
            </p>
            {cell.note && <p className="mb-0 mt-1 text-muted">{cell.note}</p>}
            {cell.proof && cell.proof.length > 0 && <div className="mt-1">Proved by: {cell.proof.map((p) => <div key={p}><Mono>{p}</Mono></div>)}</div>}
          </div>
        ) : <p className="cap">Select a cell to see its source, note and, for BlastRadius, the test that proves it.</p>}
      </div>
    </>
  );
}

function PapersMatrix({ m }: { m: Matrix }) {
  return (
    <Panel id="compare-papers" title="Capabilities against published work"
      intro={<p className="mt-0">A mark for another work appears only where its summary in <Mono>docs/LITERATURE.md</Mono> (written from titles and abstracts) or this project&apos;s own results establish it. &quot;Not reported&quot; means the sources do not establish it, not that the capability is absent.</p>}>
      <MatrixTable columns={m.columns} rows={m.rows} highlight="br"
        caption={<>What BlastRadius does that the compared published work and the retest-all practice do not report. Each BlastRadius &quot;yes&quot; names the test that proves it.</>}
        source="docs/compare_matrix.yaml" />
    </Panel>
  );
}

function ProductsMatrix({ m }: { m: Matrix }) {
  const p = m.products;
  if (!p) return null;
  return (
    <Panel id="compare-products" title={p.title}
      intro={<p className="mt-0">{p.note}</p>}>
      <MatrixTable columns={p.columns} rows={p.rows} highlight="br"
        caption={<>Commercial tools as their own documentation describes them, checked {p.checked}. Select a cell for the vendor page it was read from.</>}
        source="docs/compare_matrix.yaml" />
    </Panel>
  );
}

function SameData({ d }: { d: CompareDoc }) {
  const std = d.localization?.variants.standard ?? [];
  const hard = d.localization?.variants.hard ?? [];
  return (
    <Panel id="compare-same-data" title="Same data, same split"
      intro={<p className="mt-0">Only comparisons made on identical data appear here. BR-Bench for E1, BR-Seeded for E3 and retrieval.</p>}>
      {d.e1 && (
        <NumTable caption={<>E1 on the chronological test split ({d.e1.split}, n = {d.e1.n}). {d.e1.test}</>} source={d.e1.source}>
          <table className="w-full min-w-[720px] border-collapse">
            <thead><tr><th className={TH}>method</th><th className={`${TH} text-right`}>n</th><th className={`${TH} text-right`}>Recall@10</th><th className={`${TH} text-right`}>95% CI</th>
              <th className={`${TH} text-right`}>MAP</th><th className={`${TH} text-right`}>adjusted p vs ranker</th><th className={`${TH} text-right`}>δ</th><th className={TH}>magnitude</th></tr></thead>
            <tbody>
              {d.e1.rows.map((r) => (
                <tr key={r.id} className={r.id === "ours" ? "bg-panel" : ""}><td className={TD}>{r.method}</td><td className={`${TD} text-right`}>{r.n}</td><td className={`${TD} text-right`}>{r.recall10}</td>
                  <td className={`${TD} text-right`}>{ci(r.ci)}</td><td className={`${TD} text-right`}>{r.map}</td><td className={`${TD} text-right`}>{r.p_adj_text ?? "n/a"}</td>
                  <td className={`${TD} text-right`}>{r.delta ?? "n/a"}</td><td className={TD}>{r.magnitude ?? "n/a"}</td></tr>
              ))}
            </tbody>
          </table>
        </NumTable>
      )}
      {d.e1 && <Take>{d.e1.takeaway} Gate 3, as generated: {d.e1.verdict}</Take>}
      {d.e3 && (
        <>
          {d.e3.interim && <div className="prose-col"><Interim text={d.e3.interim_text} /></div>}
          <NumTable caption={<>E3 repair arms on BR-Seeded, standard variant. Plausible fix means the full suite is green; intervals are 95% Wilson.</>} source={d.e3.source}>
            <table className="w-full min-w-[640px] border-collapse">
              <thead><tr><th className={TH}>model</th><th className={TH}>arm</th><th className={`${TH} text-right`}>n</th><th className={`${TH} text-right`}>plausible fix</th><th className={`${TH} text-right`}>95% CI</th></tr></thead>
              <tbody>
                {d.e3.models.flatMap((m) => m.arms.map((a) => (
                  <tr key={m.model + a.arm}><td className={TD}>{m.model}</td><td className={TD}>{a.label}</td><td className={`${TD} text-right`}>{a.n}</td>
                    <td className={`${TD} text-right`}>{a.k}/{a.n}</td><td className={`${TD} text-right`}>{ci(a.wilson)}</td></tr>
                )))}
              </tbody>
            </table>
          </NumTable>
          <div className="prose-col">
            <p><span className="font-semibold">Primary pre-registered test.</span> {d.e3.primary}</p>
            {d.e3.secondary && <TblView t={d.e3.secondary} />}
            <p className="cap">{d.e3.applier_note} Strict applier: <Mono>apply_blocks</Mono> (<Mono>tests/test_agents_repair.py::test_search_must_match_exactly_once</Mono>); tolerant: <Mono>apply_blocks_tolerant</Mono> (<Mono>tests/test_bot.py::test_strict_apply_rejects_the_real_replies_and_tolerant_apply_fixes_them</Mono>).</p>
          </div>
          <Take>{d.e3.takeaway}</Take>
        </>
      )}
      {d.localization && (
        <>
          <NumTable caption={<>Retrieval: seeded function among the top 3 chunks, 70 tasks per variant; intervals are 95% Wilson.</>} source={d.localization.source}>
            <table className="w-full min-w-[640px] border-collapse">
              <thead><tr><th className={TH}>mode</th><th className={`${TH} text-right`}>n</th><th className={`${TH} text-right`}>standard hit@3</th><th className={`${TH} text-right`}>95% CI</th>
                <th className={`${TH} text-right`}>hard hit@3</th><th className={`${TH} text-right`}>95% CI</th></tr></thead>
              <tbody>
                {std.map((s, i) => (
                  <tr key={s.mode}><td className={TD}>{s.mode}</td><td className={`${TD} text-right`}>{s.n}</td><td className={`${TD} text-right`}>{s.cell}</td><td className={`${TD} text-right`}>{ci(s.wilson)}</td>
                    <td className={`${TD} text-right`}>{hard[i]?.cell ?? "n/a"}</td><td className={`${TD} text-right`}>{hard[i] ? ci(hard[i].wilson) : "n/a"}</td></tr>
                ))}
              </tbody>
            </table>
          </NumTable>
          <div className="prose-col">
            <p><span className="font-semibold">Tests.</span> Exact McNemar, two-sided. {d.localization.l4_vs_l1.map((x) => `L4 against L1, ${x.variant}: ${x.r2_only} only L4, ${x.r1_only} only L1, p = ${x.p} (n = ${x.n}).`).join(" ")}</p>
          </div>
          {d.localization.takeaway && <Take>{d.localization.takeaway}</Take>}
        </>
      )}
      {d.figures.length > 0 && (
        <div className="wide-col my-6 grid gap-6 md:grid-cols-2">
          {d.figures.map((f) => (
            <figure key={f} className="m-0">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={f} alt={f.includes("fig6") ? "Plausible-fix rate per repair arm with 95% Wilson intervals; the values are in the E3 table above" : "Hit at 3 per retrieval mode; the values are in the retrieval table above"} className="w-full border border-rule" />
              <Caption kind="Figure">{f.includes("fig6") ? "E3 arms, standard variant, 95% Wilson intervals." : "Retrieval modes, hit@3 on both variants."}</Caption>
            </figure>
          ))}
        </div>
      )}
    </Panel>
  );
}

function OtherData({ t }: { t: CompareDoc["table2"] }) {
  return (
    <Panel id="compare-other-data" title="Published numbers on other data">
      <div className="prose-col">
        <p className="mt-0 ui border border-rule bg-panel px-3 py-2 text-[15px] font-semibold">
          Different datasets and bug types. Shown for context only; they are not comparable to the tables above, and we make no claim about them.
        </p>
      </div>
      <NumTable caption={<>Results as reported by each work on its own data.</>} source={t.source}>
        <table className="w-full min-w-[640px] border-collapse">
          <thead><tr><th className={TH}>work</th><th className={TH}>reported result</th><th className={TH}>their data</th><th className={TH}>paper</th></tr></thead>
          <tbody>
            {t.rows.map((r) => (
              <tr key={r.work}><td className={TD}>{r.work}</td><td className={TD}>{r.result}</td><td className={TD}>{r.data}</td>
                <td className={TD}>{r.url ? <a href={r.url} target="_blank" rel="noreferrer">#{r.lit_number} {r.title}</a> : "n/a"}</td></tr>
            ))}
          </tbody>
        </table>
      </NumTable>
    </Panel>
  );
}

function CostPanel({ c }: { c: CompareDoc["cost"] }) {
  if (!c) return <Panel id="compare-cost" title="Cost"><p className="prose-col">Not generated: run <Mono>make cost-report</Mono>.</p></Panel>;
  const prices = Object.entries(c.prices.usd_per_million_in_out).map(([m, p]) => `${m} $${p[0]} in, $${p[1]} out`).join("; ");
  return (
    <Panel id="compare-cost" title="Cost"
      intro={<>
        <p className="mt-0 font-semibold">USD actually paid: ${c.ledger.paid_usd.toFixed(2)} (Groq free tier).</p>
        <p>At Groq&apos;s paid list prices ({c.prices.date}; <a href={c.prices.url}>{c.prices.url}</a>; per million tokens: {prices}) the recorded tokens would cost the amounts in the right-hand columns. That is what it would cost, not money spent.</p>
      </>}>
      <NumTable caption={<>E3 repair, standard variant: tokens per task and per plausible fix, and the cost of those tokens at list price.</>} source="paper/generated/cost_report.md">
        <table className="w-full min-w-[820px] border-collapse">
          <thead><tr><th className={TH}>model</th><th className={TH}>arm</th><th className={`${TH} text-right`}>tasks</th><th className={`${TH} text-right`}>fixes</th><th className={`${TH} text-right`}>in tokens per task</th>
            <th className={`${TH} text-right`}>out tokens per task</th><th className={`${TH} text-right`}>in tokens per fix</th><th className={`${TH} text-right`}>out tokens per fix</th>
            <th className={`${TH} text-right`}>USD at list per task</th><th className={`${TH} text-right`}>USD at list per fix</th></tr></thead>
          <tbody>
            {c.e3.map((r) => (
              <tr key={r.model + r.arm}><td className={TD}>{r.model}</td><td className={TD}>{r.arm}</td><td className={`${TD} text-right`}>{r.n}</td><td className={`${TD} text-right`}>{r.accepted}</td>
                <td className={`${TD} text-right`}>{fmt(r.in_per_task)}</td><td className={`${TD} text-right`}>{fmt(r.out_per_task)}</td><td className={`${TD} text-right`}>{fmt(r.in_per_fix)}</td>
                <td className={`${TD} text-right`}>{fmt(r.out_per_fix)}</td><td className={`${TD} text-right`}>{fmt(r.usd_list_per_task, 5)}</td><td className={`${TD} text-right`}>{fmt(r.usd_list_per_fix, 5)}</td></tr>
            ))}
          </tbody>
        </table>
      </NumTable>
      <NumTable caption={<>PR bot, recorded runs.{c.bot_live ? ` The live PR 1 run used ${c.bot_live.model} and ${fmt(c.bot_live.tokens)} tokens in one run; the comment records no input and output split, so no dollar figure is computed.` : ""}</>} source="paper/generated/cost_report.md">
        <table className="w-full min-w-[560px] border-collapse">
          <thead><tr><th className={TH}>model</th><th className={`${TH} text-right`}>model calls</th><th className={`${TH} text-right`}>input tokens</th><th className={`${TH} text-right`}>output tokens</th>
            <th className={`${TH} text-right`}>tokens per call</th><th className={`${TH} text-right`}>USD at list per call</th></tr></thead>
          <tbody>
            {c.bot.map((r) => (
              <tr key={r.file}><td className={TD}>{r.model}</td><td className={`${TD} text-right`}>{r.calls}</td><td className={`${TD} text-right`}>{fmt(r.prompt_tokens)}</td><td className={`${TD} text-right`}>{fmt(r.completion_tokens)}</td>
                <td className={`${TD} text-right`}>{fmt(r.tokens_per_call)}</td><td className={`${TD} text-right`}>{fmt(r.usd_list_per_call, 5)}</td></tr>
            ))}
          </tbody>
        </table>
      </NumTable>
      <NumTable caption={<>Token ledgers, kept apart: <Mono>usage.jsonl</Mono> holds every live call of E3, the PR bot and Ask; <Mono>lab_usage.jsonl</Mono> holds the Live Lab&apos;s demonstration calls (D-65), which are not E3 and never enter <Mono>make tables</Mono>. Both count against the same daily quota.</>} source="eval/llm_cache/usage.jsonl, eval/llm_cache/lab_usage.jsonl">
        <table className="w-full min-w-[480px] border-collapse">
          <thead><tr><th className={TH}>ledger</th><th className={TH}>model</th><th className={`${TH} text-right`}>calls</th><th className={`${TH} text-right`}>tokens</th></tr></thead>
          <tbody>
            {([["E3, bot and Ask", c.ledger], ["Live Lab", c.lab_ledger ?? { paid_usd: 0, by_model: {} }]] as const).flatMap(([name, l]) => {
              const rows = Object.entries(l.by_model).sort(([a], [b]) => a.localeCompare(b));
              return rows.length ? rows.map(([m, v]) => (
                <tr key={name + m}><td className={TD}>{name}</td><td className={TD}>{m}</td><td className={`${TD} text-right`}>{fmt(v.calls)}</td><td className={`${TD} text-right`}>{fmt(v.tokens)}</td></tr>
              )) : [<tr key={name}><td className={TD}>{name}</td><td className={TD} colSpan={3}>no calls recorded</td></tr>];
            })}
          </tbody>
        </table>
      </NumTable>
      <div className="prose-col"><p className="cap"><span className="font-semibold text-ink">Context, not a comparison.</span> {c.context}</p></div>
    </Panel>
  );
}

function TimePanel({ t }: { t: CompareDoc["time"] }) {
  return (
    <Panel id="compare-time" title="Time">
      {t.e1 && (
        <NumTable caption={<>BR-Bench, chronological test split (n = {t.e1.n}). Candidate test files per instance: {t.e1.candidates_median} Position, Recall@10% and the suite fraction are generated; the share of the suite run before the first failure is not a generated BR-Bench number.</>} source={t.e1.source}>
          <table className="w-full min-w-[720px] border-collapse">
            <thead><tr><th className={TH}>order</th><th className={`${TH} text-right`}>mean position of the first failing test file</th><th className={`${TH} text-right`}>failing files found in the first 10% of the suite</th>
              <th className={`${TH} text-right`}>suite fraction for full recall</th><th className={`${TH} text-right`}>APFD</th></tr></thead>
            <tbody>
              {t.e1.rows.map((r) => (
                <tr key={r.id} className={r.id === "ours" ? "bg-panel" : ""}><td className={TD}>{r.method}</td><td className={`${TD} text-right`}>{r.first_fail_pos}</td><td className={`${TD} text-right`}>{r.recall_first_10pct}</td>
                  <td className={`${TD} text-right`}>{r.suite_frac_full_recall}</td><td className={`${TD} text-right`}>{r.apfd}</td></tr>
              ))}
            </tbody>
          </table>
        </NumTable>
      )}
      {t.e3_detection && (
        <>
          <NumTable caption={<>The negative result: fresh repositories with no failure history (E3 detection on BR-Seeded).</>} source={t.e3_detection.source}>
            <TblView t={{ columns: Object.keys(t.e3_detection.rows[0]), rows: t.e3_detection.rows.map((r) => Object.values(r)) }} />
          </NumTable>
          <Take>{t.e3_detection.takeaway}{t.e1?.history_drop_recall10 !== undefined && ` Removing the failure-history features costs ${t.e1.history_drop_recall10.toFixed(3)} Recall@10 on BR-Bench, and a fresh repository has none.`}</Take>
        </>
      )}
    </Panel>
  );
}

function SafetyPanel({ m }: { m: Matrix }) {
  return (
    <Panel id="compare-safety" title="Safety"
      intro={<p className="mt-0">Each statement is backed by a named test; <Mono>make demo-check</Mono> runs them.</p>}>
      <ul className="prose-col list-none pl-0">
        {m.safety.map((s) => (
          <li key={s.claim} className="mb-3">
            <span>{s.claim}</span>
            {s.tests.map((t) => <div key={t}><Mono className="text-muted">{t}</Mono></div>)}
          </li>
        ))}
      </ul>
    </Panel>
  );
}

export default function Compare() {
  const { doc: d, error } = useDoc<CompareDoc>("compare");
  return (
    <section id="compare" aria-labelledby="h-compare" className="scroll-mt-20">
      <h2 id="h-compare" className="m-0 mb-3">Compare</h2>
      <div className="prose-col">
        <p className="mt-0">
          Every number on this page is read from <Mono>paper/generated</Mono>, the usage ledger or a script
          {d ? <>; data at <Mono>{d.generated_at_git_sha.slice(0, 10)}</Mono></> : ""}. Same-data results and other-data numbers are never shown in one table.
        </p>
      </div>
      {error && <p className="text-fail">Could not load /data/compare.json ({error}). Run <Mono>make demo-data</Mono>.</p>}
      {!d && !error && <p className="text-muted">Loading.</p>}
      {d && (
        <>
          <PapersMatrix m={d.matrix} />
          <ProductsMatrix m={d.matrix} />
          <SameData d={d} />
          <OtherData t={d.table2} />
          <CostPanel c={d.cost} />
          <TimePanel t={d.time} />
          <SafetyPanel m={d.matrix} />
        </>
      )}
    </section>
  );
}
