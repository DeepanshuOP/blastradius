"use client";

import { BarFigure } from "./Figures";
import { parsePrimary } from "./lib";
import type { ResultsDoc } from "./types";
import { MoreResults, type PanelsDoc } from "./Panels";
import { Mono, NumTable, TD, TH, methodName } from "./ui";

export type Tbl = { columns: string[]; rows: string[][] };
export type E1Doc = { source: string; verdict: string; gate3_met: boolean; main: Tbl } | null;
export type E2Doc = { source: string; classes: Tbl; pooled: Tbl | null; chronological: Tbl | null; dangerous_error: string } | null;
export type E3Doc = {
  status: string; note?: string; source?: string; primary?: string; secondary?: Tbl | null; models?: Record<string, Tbl>;
  progress?: { model: string; variant: string; n: number; total: number; interim: boolean; text: string }[];
  detection?: Tbl | null; pilot?: Record<string, Tbl>; exploratory?: Record<string, Tbl>;
} | null;
type E1Row = { id: string; method: string; n: number; recall10: string; map: string; ci: [number, number]; p_adj: number | null; p_adj_text: string | null; delta: string | null; magnitude: string | null };
export type CompareLite = {
  e1: { source: string; n: number; split: string; test: string; verdict: string; rows: E1Row[] } | null;
  localization: { source: string; variants: Record<string, { mode: string; k: number; n: number; cell: string; mrr: string; wilson: [number, number] }[]>;
    paired: Tbl | null } | null;
};
export type RagDoc = { ask: { model: string; questions: { faithful: boolean | null; cited: number[]; answer: string | null; tokens: number; qtype: string }[] } | null } | null;

const ci = (w: [number, number]) => `[${w[0].toFixed(3)}, ${w[1].toFixed(3)}]`;

/** One results subsection: question, method, evidence, what it shows, source. */
function Sub({ id, title, question, method, children, shows, source }: {
  id: string; title: string; question: string; method: string; children: React.ReactNode; shows: React.ReactNode; source: string;
}) {
  return (
    <section id={id} aria-labelledby={`h-${id}`} className="scroll-mt-20 border-t border-rule pt-2">
      <h3 id={`h-${id}`}>{title}</h3>
      <div className="prose-col">
        <p className="mt-0"><span className="font-semibold">Question.</span> {question}</p>
        <p><span className="font-semibold">Method.</span> {method}</p>
      </div>
      {children}
      <div className="prose-col">
        <p><span className="font-semibold">What this shows.</span> {shows}</p>
        <p className="cap">Source: <Mono>{source}</Mono></p>
      </div>
    </section>
  );
}

function Rq1({ r }: { r: ResultsDoc }) {
  const rows = r.rq1_k10.methods;
  const co = rows.find((m) => m.method === "co-change, all partner files");
  const hist = rows.find((m) => m.method === "historical-frequency baseline");
  const n = rows[0]?.n;
  return (
    <Sub id="rq1" title="RQ1: co-change against failure history"
      question="Does what changed together in the past, or what failed in the past, name the tests that fail now?"
      method={`Each predictor names its top ${r.rq1_k10.k} files per instance using only data from before the run; the names are scored against the strict labels of the same ${n} instances.`}
      shows={co && hist
        ? <>Past failure frequency recovers {hist.micro_recall.text} of the failing test files and co-change recovers {co.micro_recall.text}; both miss most of what fails.</>
        : "Not exported."}
      source={r.rq1_k10.source}>
      <NumTable caption={<>RQ1 at k = {r.rq1_k10.k}, all methods on the same {n} instances. No significance test is applied here; E1 adds paired tests.</>}>
        <table className="w-full min-w-[640px] border-collapse">
          <thead><tr><th className={TH}>method</th><th className={`${TH} text-right`}>n</th><th className={`${TH} text-right`}>mean precision</th>
            <th className={`${TH} text-right`}>mean recall</th><th className={`${TH} text-right`}>micro recall (hits/actual)</th><th className={`${TH} text-right`}>median names</th></tr></thead>
          <tbody>
            {rows.map((m) => (
              <tr key={m.method}><td className={TD}>{methodName(m.method)}</td><td className={`${TD} text-right`}>{m.n}</td>
                <td className={`${TD} text-right`}>{m.mean_precision.toFixed(3)}</td><td className={`${TD} text-right`}>{m.mean_recall.toFixed(3)}</td>
                <td className={`${TD} text-right`}>{m.micro_recall.text}</td><td className={`${TD} text-right`}>{m.median_size}</td></tr>
            ))}
          </tbody>
        </table>
      </NumTable>
    </Sub>
  );
}

function E1({ e1, c }: { e1: E1Doc; c: CompareLite | null }) {
  const rows = c?.e1?.rows ?? [];
  const ours = rows.find((r) => r.id === "ours");
  return (
    <Sub id="e1" title="E1: predict which test files a change breaks"
      question="Does a learned ranker over change, history, co-change and path features place the failing test files earlier than simpler orderings?"
      method={`LightGBM ranker with pre-registered baselines B0 to B7, chronological 60/20/20 split by run start, ${c?.e1 ? `n = ${c.e1.n} test instances` : "test split"}; Wilcoxon signed-rank with Holm correction, Cliff's delta as effect size.`}
      shows={e1 ? <>{e1.verdict}</> : "Not exported."}
      source={e1?.source ?? "paper/generated/rq2_predictor.md"}>
      {rows.length > 0 && (
        <>
          <BarFigure
            max={0.7}
            bars={rows.map((r) => ({ label: r.method.replace(/ \(.*\)$/, ""), value: parseFloat(r.recall10), text: r.recall10, lo: r.ci[0], hi: r.ci[1], strong: r.id === "ours" }))}
            summary={`Recall at 10 per method on ${c?.e1?.n} test instances: ${rows.map((r) => `${r.method} ${r.recall10}`).join("; ")}.`}
            caption={<>Recall@10 on the chronological test split (n = {c?.e1?.n}); whiskers are 95% bootstrap intervals. The ranker is the highlighted bar.</>}
          />
          <NumTable caption={<>E1 test-split results against the ranker. p is Holm-adjusted over all comparisons; δ is Cliff&apos;s delta. {c?.e1?.test}</>} source={c?.e1?.source}>
            <table className="w-full min-w-[720px] border-collapse">
              <thead><tr><th className={TH}>method</th><th className={`${TH} text-right`}>n</th><th className={`${TH} text-right`}>Recall@10</th><th className={`${TH} text-right`}>95% CI</th>
                <th className={`${TH} text-right`}>MAP</th><th className={`${TH} text-right`}>adjusted p vs ranker</th><th className={`${TH} text-right`}>δ</th><th className={TH}>magnitude</th></tr></thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className={r.id === "ours" ? "bg-panel" : ""}><td className={TD}>{r.method}</td><td className={`${TD} text-right`}>{r.n}</td>
                    <td className={`${TD} text-right`}>{r.recall10}</td><td className={`${TD} text-right`}>{ci(r.ci)}</td><td className={`${TD} text-right`}>{r.map}</td>
                    <td className={`${TD} text-right`}>{r.p_adj_text ?? "n/a"}</td><td className={`${TD} text-right`}>{r.delta ?? "n/a"}</td><td className={TD}>{r.magnitude ?? "n/a"}</td></tr>
                ))}
              </tbody>
            </table>
          </NumTable>
        </>
      )}
      {!ours && <p className="prose-col">E1 results are not exported.</p>}
    </Sub>
  );
}

function E2({ e2 }: { e2: E2Doc }) {
  const t = e2?.pooled;
  const col = (name: string) => t?.columns.findIndex((c) => c.toLowerCase() === name.toLowerCase()) ?? -1;
  const lgb = t?.rows.find((r) => r[0].toLowerCase().startsWith("lightgbm"));
  const wrong = t ? col("mine WRONGLY CLEARED") : -1;
  const test = e2?.classes.rows.find((r) => r[0] === "test");
  return (
    <Sub id="e2" title="E2: is a failure mine, inherited or flaky?"
      question="Can a model tell which failing tests the change caused, and which were already failing or are flaky?"
      method="Leave-one-repository-out over all known-base runs, against rule baselines (failed on the branch before, same message seen before); positive class is not-mine, and the cost that matters is a mine failure wrongly cleared."
      shows={lgb && wrong >= 0
        ? <>LightGBM wrongly clears {lgb[wrong].replace(/\*\*/g, "")} mine failures pooled over held-out repositories, and the chronological test split holds only {test ? Number(test[2]) + Number(test[3]) : "few"} not-mine pairs, so this is a small-sample result.</>
        : "Not exported."}
      source={e2?.source ?? "paper/generated/rq3_triage.md"}>
      {t && (
        <NumTable caption={<>Pooled leave-one-repository-out triage. Not-mine is inherited plus flaky; the last column is the harmful error. Intervals are in the source file.</>} source={e2?.source}>
          <table className="w-full min-w-[720px] border-collapse">
            <thead><tr>{t.columns.map((c, i) => <th key={c} className={`${TH} ${i > 0 ? "text-right" : ""}`}>{c}</th>)}</tr></thead>
            <tbody>
              {t.rows.map((r) => (
                <tr key={r[0]}>{r.map((c, i) => <td key={i} className={`${TD} ${i > 0 ? "text-right" : ""}`}>{c.replace(/\*\*/g, "")}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </NumTable>
      )}
    </Sub>
  );
}

/** Columns of an E3 arm table that are shown: arm, n, plausible fix, CI, edited function, exact restore, overfit, tokens. */
const SHOW = [0, 1, 2, 3, 5, 6, 7, 9];
const MODEL_KEY = /^(.*), (standard|hard) variant \(n = (\d+) tasks\)$/;

function E3({ e3, c }: { e3: E3Doc; c: CompareLite | null }) {
  void c;
  const primary = e3?.primary ? parsePrimary(e3.primary) : null;
  const entries = Object.entries(e3?.models ?? {}).map(([k, t]) => {
    const m = MODEL_KEY.exec(k);
    return { key: k, model: m?.[1] ?? k, variant: m?.[2] ?? "", n: Number(m?.[3] ?? 0), t };
  });
  const confirmatory = (x: (typeof entries)[number]) => x.variant === "standard" && x.n === 70 && x.model.startsWith("openai/");
  const label = (x: (typeof entries)[number]) => confirmatory(x) ? "pre-registered (docs/phase/033)" : `interim, run continuing (${x.n} of 70)`;
  // Exploratory third model and the 20-task pilot, from the same generated file.
  for (const [k, t] of Object.entries(e3?.exploratory ?? {})) {
    const m = /^Third model ([\w./-]+), (standard|hard) variant \(n = (\d+) of 70 tasks/.exec(k);
    entries.push({ key: k, model: m?.[1] ?? k, variant: m?.[2] ?? "standard", n: Number(m?.[3] ?? 0), t });
  }
  const pilots = Object.entries(e3?.pilot ?? {}).map(([k, t]) => ({ key: k, model: k.replace(/ \(pilot.*$/, ""), variant: "standard", n: 20, t }));
  const sig = primary?.supported;
  return (
    <Sub id="e3" title="E3: change-aware repair"
      question="Does telling the repair agent which functions the change touched raise the share of tasks fixed with the full suite green?"
      method="Seeded single-line bugs in six repositories; arms R0 (notify only), R1 (failure log only), R2 (functions the diff touches) and R3 (R2 plus up to two retries); a fix counts only if the full suite passes. Primary test: R2 above R1, exact one-sided McNemar, gpt-oss-120b, standard variant."
      shows={primary ? (
        <>{sig ? "R2 fixes more tasks than R1 and the pre-registered test (docs/phase/033) supports it" : "The pre-registered test does not support R2 above R1"}: {primary.r2[0]}/{primary.r2[1]} against {primary.r1[0]}/{primary.r1[1]} (R2 only {primary.r2Only}, R1 only {primary.r1Only}, p = {primary.p}, n = {primary.n}). Seeded bugs are simpler than real ones, so these rates do not transfer to real failures.</>
      ) : "Not exported."}
      source={e3?.source ?? "paper/generated/rq4_repair.md"}>
      {primary && !sig && (
        <p className="prose-col font-semibold">The primary pre-registered test is not significant.</p>
      )}
      {entries.map((x) => (
        <NumTable key={x.key}
          caption={<>{x.model}, {x.variant} variant, n = {x.n} tasks: {label(x)}. Plausible fix means the full suite is green; intervals are bootstrap 95%.</>}
          source={e3?.source}>
          <table className="w-full min-w-[720px] border-collapse">
            <thead><tr>{SHOW.map((i) => x.t.columns[i]).map((c) => <th key={c} className={`${TH} ${c === "arm" ? "" : "text-right"}`}>{c}</th>)}</tr></thead>
            <tbody>
              {x.t.rows.map((r) => (
                <tr key={r[0]}>{SHOW.map((i) => r[i]).map((cell, i) => <td key={i} className={`${TD} ${i > 0 ? "text-right" : ""}`}>{cell}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </NumTable>
      ))}
      {pilots.map((x) => (
        <NumTable key={x.key} caption={<>{x.model}, standard variant, n = {x.n} tasks: pilot. Run before the pre-registration was written; the 20 tasks are part of the 70 and are not an independent sample.</>} source={e3?.source}>
          <table className="w-full min-w-[720px] border-collapse">
            <thead><tr>{SHOW.map((i) => x.t.columns[i]).map((c) => <th key={c} className={`${TH} ${c === "arm" ? "" : "text-right"}`}>{c}</th>)}</tr></thead>
            <tbody>{x.t.rows.map((r) => <tr key={r[0]}>{SHOW.map((i) => r[i]).map((cell, i) => <td key={i} className={`${TD} ${i > 0 ? "text-right" : ""}`}>{cell}</td>)}</tr>)}</tbody>
          </table>
        </NumTable>
      ))}
      {e3?.secondary && (
        <NumTable caption={<>Secondary pre-registered tests, one-sided exact McNemar, Holm-adjusted over the pre-registered family of 7 (hard-variant rows are interim). &quot;First only&quot; counts tasks fixed by the first-named arm and not the second.</>} source={e3.source}>
          <table className="w-full min-w-[560px] border-collapse">
            <thead><tr>{e3.secondary.columns.map((c, i) => <th key={c} className={`${TH} ${i > 0 ? "text-right" : ""}`}>{c}</th>)}</tr></thead>
            <tbody>{e3.secondary.rows.map((r) => <tr key={r[0]}>{r.map((c, i) => <td key={i} className={`${TD} ${i > 0 ? "text-right" : ""}`}>{c}</td>)}</tr>)}</tbody>
          </table>
        </NumTable>
      )}
      <div className="prose-col">
        <p>
          Arm R4 (R2 plus retrieved history and documentation) is built, not run. The evaluation uses a strict patch applier;
          the PR bot uses a whitespace-tolerant one, so these rates are conservative relative to the bot.
        </p>
      </div>
    </Sub>
  );
}

function Retrieval({ c }: { c: CompareLite | null }) {
  const l = c?.localization;
  const std = l?.variants.standard ?? [];
  const hard = l?.variants.hard ?? [];
  const l4 = std.find((x) => x.mode.startsWith("L4"));
  const l1 = std.find((x) => x.mode.startsWith("L1"));
  const l3 = std.find((x) => x.mode.startsWith("L3"));
  const l5h = hard.find((x) => x.mode.startsWith("L5"));
  const l4h = hard.find((x) => x.mode.startsWith("L4"));
  return (
    <Sub id="retrieval" title="Retrieval (RAG), exploratory"
      question="Is the seeded function among the three chunks a retriever shows, and does smarter retrieval replace knowing the change?"
      method="Five retrieval modes over the seeded repositories with no language model: BM25, dense, hybrid, and BM25 or hybrid restricted to the functions the diff touches; exact McNemar on hit@3 with Holm correction. Not pre-registered."
      shows={l1 && l3 && l4
        ? <>Restricting the search to the functions the change touched (L4, {l4.cell}) finds the seeded function far more often than whole-repository hybrid retrieval (L3, {l3.cell}) or BM25 (L1, {l1.cell}); adding dense vectors to L4 does not help on the hard variant ({l5h?.cell} against {l4h?.cell}).</>
        : "Not exported."}
      source={l?.source ?? "paper/generated/rq5_retrieval.md"}>
      {l && (
        <>
          <NumTable caption={<>Seeded function among the top 3 chunks, 70 tasks per variant; intervals are 95% Wilson. L1 and L4 are the retrieval of arms R1 and R2.</>} source={l.source}>
            <table className="w-full min-w-[720px] border-collapse">
              <thead><tr><th className={TH}>mode</th><th className={`${TH} text-right`}>standard hit@3</th><th className={`${TH} text-right`}>95% CI</th>
                <th className={`${TH} text-right`}>hard hit@3</th><th className={`${TH} text-right`}>95% CI</th></tr></thead>
              <tbody>
                {std.map((s, i) => (
                  <tr key={s.mode}><td className={TD}>{s.mode}</td><td className={`${TD} text-right`}>{s.cell}</td><td className={`${TD} text-right`}>{ci(s.wilson)}</td>
                    <td className={`${TD} text-right`}>{hard[i]?.cell ?? "n/a"}</td><td className={`${TD} text-right`}>{hard[i] ? ci(hard[i].wilson) : "n/a"}</td></tr>
                ))}
              </tbody>
            </table>
          </NumTable>
          {l.paired && (
            <NumTable caption={<>Paired exact McNemar tests on hit@3, two-sided, Holm-adjusted over a family of 4.</>} source={l.source}>
              <table className="w-full min-w-[560px] border-collapse">
                <thead><tr>{l.paired.columns.map((h, i) => <th key={h} className={`${TH} ${i > 1 ? "text-right" : ""}`}>{h}</th>)}</tr></thead>
                <tbody>{l.paired.rows.map((r, j) => <tr key={j}>{r.map((x, i) => <td key={i} className={`${TD} ${i > 1 ? "text-right" : ""}`}>{x}</td>)}</tr>)}</tbody>
              </table>
            </NumTable>
          )}
        </>
      )}
    </Sub>
  );
}

function Ask({ rag }: { rag: RagDoc }) {
  const qs = rag?.ask?.questions ?? [];
  const n = qs.length;
  const faithful = qs.filter((q) => q.faithful === true).length;
  const cited = qs.filter((q) => q.cited.length > 0).length;
  const tokens = qs.reduce((a, q) => a + q.tokens, 0);
  const byType = new Map<string, { n: number; cited: number }>();
  qs.forEach((q) => { const v = byType.get(q.qtype) ?? { n: 0, cited: 0 }; v.n += 1; v.cited += q.cited.length > 0 ? 1 : 0; byType.set(q.qtype, v); });
  return (
    <Sub id="ask" title="Ask: answers with citations, exploratory"
      question="When a language model answers from retrieved code, failure history and documents, do its citations point at items it was actually shown?"
      method="Fifteen fixed questions, answered once with retrieval over eight items and told to answer only from them and cite each claim; the replay of the recording is checked offline."
      shows={n > 0 ? <>No citation points outside the retrieved items in {faithful} of {n} answers and {cited} of {n} cite at least one item; this scores citation hygiene only, not whether the answers are correct.</> : "Not recorded."}
      source="paper/generated/rq5_retrieval.md">
      {n > 0 && (
        <NumTable caption={<>Citation check of the recorded answers ({rag?.ask?.model}, {tokens.toLocaleString()} tokens in total). Correctness was not scored.</>} source="paper/generated/rq5_retrieval.md">
          <table className="w-full min-w-[480px] border-collapse">
            <thead><tr><th className={TH}>question type</th><th className={`${TH} text-right`}>questions</th><th className={`${TH} text-right`}>citing at least one item</th></tr></thead>
            <tbody>
              {Array.from(byType.entries()).map(([k, v]) => <tr key={k}><td className={TD}>{k}</td><td className={`${TD} text-right`}>{v.n}</td><td className={`${TD} text-right`}>{v.cited}/{v.n}</td></tr>)}
              <tr><td className={`${TD} font-semibold`}>all</td><td className={`${TD} text-right`}>{n}</td><td className={`${TD} text-right`}>{cited}/{n}</td></tr>
            </tbody>
          </table>
        </NumTable>
      )}
    </Sub>
  );
}

export default function ResultsSection({ r, e1, e2, e3, c, rag, panels }: {
  r: ResultsDoc | null; e1: E1Doc; e2: E2Doc; e3: E3Doc; c: CompareLite | null; rag: RagDoc; panels: PanelsDoc | null;
}) {
  return (
    <section id="results" aria-labelledby="h-results" className="scroll-mt-20">
      <h2 id="h-results" className="m-0 mb-3">Results</h2>
      <div className="prose-col">
        <p className="mt-0">
          Each subsection states its question and method, shows one numbered table or figure with its sample size and test, and
          names the generated file the numbers were read from. Negative results are reported with the same prominence as positive ones.
        </p>
      </div>
      {r && <Rq1 r={r} />}
      <E1 e1={e1} c={c} />
      <E2 e2={e2} />
      <E3 e3={e3} c={c} />
      <Retrieval c={c} />
      <Ask rag={rag} />
      {panels && (
        <details className="mt-6 border-t border-rule pt-3">
          <summary className="ui text-[15px] font-medium">Every remaining result table, the reachability result and the release facts</summary>
          <div className="mt-4"><MoreResults d={panels} /></div>
        </details>
      )}
    </section>
  );
}
