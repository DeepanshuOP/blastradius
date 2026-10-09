"use client";

import { useEffect, useState } from "react";
import { inline } from "./Markdown";
import { Badge, Card, Mono, Source } from "./ui";

type Table = { heading: string; columns: string[]; rows: string[][] };
type Panel = { id: string; title: string; source: string; source_generated_at_git_sha: string | null; tables: Table[] };
export type PanelsDoc = {
  generated_at_git_sha: string;
  panels: Panel[];
  release: {
    sources: string[]; dois: { what: string; doi: string }[]; tables: { table: string; rows: number }[];
    validator: { verdict: string; violations: string[] }; datasheet_rows: { item: string; status: string }[];
  };
  decisions: { source: string; rows: { id: string; title: string }[] };
};
type ReachRow = { method: string; mean_p: number; mean_r: number; mean_j: number; micro_hits: number; micro_actual: number; median_size: number };
type ReachDoc = {
  source: string; generated_at_git_sha: string; funnel: { step: string; n: number }[]; n: number;
  unbound: { n: number; d: number } | null;
  test_id_level: { scope: string; n: number; rows: ReachRow[] }[]; file_level: { scope: string; n: number; rows: ReachRow[] }[];
};

function MdTable({ t }: { t: Table }) {
  return (
    <div className="mb-4 last:mb-0">
      <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">{t.heading}</h4>
      <div className="max-h-96 overflow-auto">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-white"><tr>{t.columns.map((c, i) => <th key={i} className="border-b border-slate-200 px-2 py-1.5 font-semibold text-slate-600">{inline(c)}</th>)}</tr></thead>
          <tbody>{t.rows.map((r, i) => (
            <tr key={i} className="odd:bg-slate-50">{r.map((c, j) => <td key={j} className={`px-2 py-1.5 align-top ${j > 0 ? "tabular-nums" : ""}`}>{inline(c)}</td>)}</tr>))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PanelCard({ p, open = false }: { p: Panel; open?: boolean }) {
  return (
    <Card title={p.title}>
      <details open={open}>
        <summary className="cursor-pointer text-xs font-semibold text-slate-600">{p.tables.length} table{p.tables.length === 1 ? "" : "s"}</summary>
        <div className="mt-3">{p.tables.map((t, i) => <MdTable key={i} t={t} />)}</div>
      </details>
      <Source file={`${p.source}${p.source_generated_at_git_sha ? ` (generated at ${p.source_generated_at_git_sha.slice(0, 10)})` : ""}`} />
    </Card>
  );
}

function ReachTable({ title, rows }: { title: string; rows: ReachRow[] }) {
  return (
    <div className="mb-4 overflow-x-auto">
      <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h4>
      <table className="w-full min-w-[560px] text-left text-xs">
        <thead><tr className="text-slate-500"><th className="py-1">method</th><th className="text-right">mean P</th><th className="text-right">mean R</th>
          <th className="text-right">mean J</th><th className="text-right">micro recall</th><th className="text-right">median size</th></tr></thead>
        <tbody>{rows.map((r) => (
          <tr key={r.method} className="border-t border-slate-100 tabular-nums"><td className="py-1">{r.method}</td>
            <td className="text-right">{r.mean_p.toFixed(3)}</td><td className="text-right">{r.mean_r.toFixed(3)}</td><td className="text-right">{r.mean_j.toFixed(3)}</td>
            <td className="text-right">{r.micro_actual ? `${((100 * r.micro_hits) / r.micro_actual).toFixed(2)}% (${r.micro_hits}/${r.micro_actual})` : "n/a"}</td>
            <td className="text-right">{r.median_size}</td></tr>))}
        </tbody>
      </table>
    </div>
  );
}

function Reachability() {
  const [d, setD] = useState<ReachDoc | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    fetch("/data/reachability.json", { cache: "no-store" }).then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setD).catch((e) => setErr(String(e)));
  }, []);
  return (
    <Card title="Graph reachability vs real failures (mini-corpus, course result, D-48)">
      {err && <p className="text-red-700">Could not load /data/reachability.json ({err}).</p>}
      {d && (
        <>
          <table className="mb-3 w-full text-left text-xs"><tbody>{d.funnel.map((f) => (
            <tr key={f.step} className="border-t border-slate-100"><td className="py-1 pr-2">{f.step}</td><td className="text-right tabular-nums font-semibold">{f.n}</td></tr>))}
          </tbody></table>
          {d.n === 0 ? (
            <p className="rounded border border-amber-200 bg-amber-50 p-3 text-amber-900">
              <span className="font-semibold">n = 0: no result.</span> None of the resolved base SHAs has a graph, and none can be built offline:
              the commits are absent from the local clone or its blobs were never fetched (partial clone). Nothing is estimated or filled in.
              See <Mono>docs/phase/031-reachability-mini-corpus.md</Mono>.
            </p>
          ) : (
            <>
              {d.unbound && <p className="mb-2 text-xs">Ground-truth test_ids with no graph node: {d.unbound.n}/{d.unbound.d}</p>}
              {d.test_id_level.map((s) => <ReachTable key={`t${s.scope}`} title={`test-id level: ${s.scope} (n=${s.n})`} rows={s.rows} />)}
              {d.file_level.map((s) => <ReachTable key={`f${s.scope}`} title={`file level: ${s.scope} (n=${s.n})`} rows={s.rows} />)}
            </>
          )}
        </>
      )}
      <Source file={d ? `${d.source} → demo-web/public/data/reachability.json (at ${d.generated_at_git_sha})` : "analysis/reachability_mini.py"} />
    </Card>
  );
}

function Release({ r }: { r: PanelsDoc["release"] }) {
  return (
    <Card title="Release v0.2 and datasheet">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">DOIs</h4>
          <ul className="space-y-1">{r.dois.map((x) => <li key={x.doi}>{x.what}: <a className="text-sky-700 hover:underline" href={`https://doi.org/${x.doi}`}>{x.doi}</a></li>)}</ul>
          <h4 className="mb-1 mt-3 text-xs font-semibold uppercase text-slate-500">{r.tables.length} released tables</h4>
          <ul className="space-y-1">{r.tables.map((t) => <li key={t.table} className="flex justify-between"><Mono>{t.table}.parquet</Mono><span className="tabular-nums">{t.rows.toLocaleString()} rows</span></li>)}</ul>
        </div>
        <div>
          <h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">Checks</h4>
          <ul className="space-y-2">
            <li><Badge tone={r.validator.verdict === "PASS" ? "green" : "amber"}>{r.validator.verdict}</Badge> schema v0.2 validator (T1.6a, D-54){r.validator.violations.length ? `: ${r.validator.violations.length} violations` : ""}</li>
            {r.datasheet_rows.map((x) => <li key={x.item}><span className="font-medium">{inline(x.item)}</span>: <span className="text-slate-600">{inline(x.status)}</span></li>)}
          </ul>
        </div>
      </div>
      <Source file={r.sources.join(", ")} />
    </Card>
  );
}

/** Every remaining result of paper/generated, the reachability result and the release facts. */
export function MoreResults({ d }: { d: PanelsDoc }) {
  const by = (id: string) => d.panels.find((p) => p.id === id);
  const order = ["gates", "funnel", "binding", "classes", "rq1_k5", "rq1_k10", "rq1_k20", "rq1_size", "sensitivity", "leakage", "flakiness", "expiry", "expiry_d23", "parser"];
  return (
    <div className="space-y-5">
      <h2 className="pt-4 text-lg font-bold text-slate-900">All results, table by table</h2>
      <p className="-mt-3 text-sm text-slate-600">Copied cell for cell from the generated files by <Mono>analysis/export_demo_data.py</Mono>; nothing here is typed in by hand.</p>
      <Reachability />
      <div className="grid gap-5 lg:grid-cols-2">
        {order.map((id) => by(id)).filter((p): p is Panel => !!p).map((p) => <PanelCard key={p.id} p={p} open={["gates", "flakiness", "expiry", "parser"].includes(p.id)} />)}
      </div>
      <Release r={d.release} />
    </div>
  );
}

export function Decisions({ d }: { d: PanelsDoc["decisions"] }) {
  const nums = d.rows.map((r) => Number(r.id.slice(2)));
  const missing = Array.from({ length: Math.max(...nums) }, (_, i) => i + 1).filter((n) => !nums.includes(n)).map((n) => `D-${String(n).padStart(2, "0")}`);
  return (
    <Card title={`Decision log (${d.rows.length} decisions)`}>
      <ul className="divide-y divide-slate-100">{d.rows.map((r) => (
        <li key={r.id} className="grid grid-cols-[4rem_1fr] gap-3 py-1.5"><Mono className="font-semibold">{r.id}</Mono><span>{inline(r.title)}</span></li>))}
      </ul>
      <p className="mt-3 text-xs text-slate-500">{missing.length ? `Not present as an entry in the log: ${missing.join(", ")} (the log states D-51 was never assigned). ` : ""}Full rationale and revisit triggers are in the source file.</p>
      <Source file={d.source} />
    </Card>
  );
}
