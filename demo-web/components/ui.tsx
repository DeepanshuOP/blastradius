import type { ReactNode } from "react";

export function Card({ title, step, children, className = "" }: {
  title: string;
  step?: number;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 ${className}`}>
      <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-slate-800">
        {step !== undefined && (
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-800 text-xs text-white">
            {step}
          </span>
        )}
        {title}
      </h3>
      <div className="text-sm text-slate-700">{children}</div>
    </section>
  );
}

export function Source({ file }: { file: string }) {
  return <p className="mt-3 text-xs text-slate-500">source: {file}</p>;
}

export function Mono({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <code className={`break-all font-mono text-[12px] text-slate-800 ${className}`}>{children}</code>;
}

export function KV({ k, children }: { k: string; children: ReactNode }) {
  return (
    <div className="grid grid-cols-1 gap-0.5 py-1 sm:grid-cols-[10rem_1fr] sm:gap-3">
      <dt className="text-xs uppercase tracking-wide text-slate-500">{k}</dt>
      <dd className="min-w-0">{children}</dd>
    </div>
  );
}

export function Badge({ tone, children }: { tone: "red" | "green" | "slate" | "amber"; children: ReactNode }) {
  const c = {
    red: "bg-red-50 text-red-700 ring-red-200",
    green: "bg-emerald-50 text-emerald-700 ring-emerald-200",
    slate: "bg-slate-100 text-slate-700 ring-slate-200",
    amber: "bg-amber-50 text-amber-800 ring-amber-200",
  }[tone];
  return <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ring-1 ${c}`}>{children}</span>;
}

export const short = (sha: string) => sha.slice(0, 10);
export const pct = (x: number) => `${(x * 100).toFixed(1)}%`;

/** Short display names for the RQ1 method rows of paper/generated/rq1.md. */
export const METHOD_SHORT: Record<string, string> = {
  "co-change, all partner files": "Co-change (all)",
  "co-change, restricted to conventional test files": "Co-change (test files)",
  'co-change, restricted to files with "test" in the path (sensitivity)': "Co-change (\"test\" in path)",
  "changeset baseline": "Changeset",
  "historical-frequency baseline": "Historical frequency",
};
export const methodName = (m: string) => METHOD_SHORT[m] ?? m;
export const ratePct = (r: { n: number; d: number }) => `${((100 * r.n) / r.d).toFixed(2)}%`;
