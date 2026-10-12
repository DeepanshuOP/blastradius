import type { ReactNode } from "react";

/** A titled block of a section: a rule, a heading, the body. No box, no shadow. */
export function Card({ title, step, children, className = "" }: {
  title: string;
  step?: number;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`min-w-0 border-t border-rule pt-4 ${className}`}>
      <h4 className="mb-3 font-serif">{step !== undefined ? `${step}. ` : ""}{title}</h4>
      <div className="text-[15px] text-ink">{children}</div>
    </section>
  );
}

export function Source({ file }: { file: string }) {
  return <p className="cap mt-3">Source: <Mono>{file}</Mono></p>;
}

export function Mono({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <code className={`break-all font-mono text-[13px] text-ink ${className}`}>{children}</code>;
}

export function KV({ k, children }: { k: string; children: ReactNode }) {
  return (
    <div className="ui grid grid-cols-1 gap-0.5 py-1 text-[14px] sm:grid-cols-[10rem_1fr] sm:gap-3">
      <dt className="text-muted">{k}</dt>
      <dd className="min-w-0">{children}</dd>
    </div>
  );
}

/** A plain text status. Colour is carried only by test outcome (pass, fail) and the fix / no-fix words. */
export function Badge({ tone, children }: { tone: "red" | "green" | "slate" | "amber"; children: ReactNode }) {
  const c = { red: "text-fail", green: "text-pass", slate: "text-muted", amber: "text-ink" }[tone];
  return <span className={`ui text-[13px] font-medium ${c}`}>{children}</span>;
}

/** Figure or table caption: "Table 3." is filled in by the page in order of appearance. */
export function Caption({ kind, children }: { kind: "Figure" | "Table"; children: ReactNode }) {
  return (
    <p className="cap mt-2" data-cap={kind}>
      <span className="cap-label font-semibold text-ink">{kind} <span className="cap-num" /></span>. {children}
    </p>
  );
}

/** A numbered table with its caption below. `children` is the <table>; wraps for horizontal scroll at 375px. */
export function NumTable({ caption, children, source }: { caption: ReactNode; children: ReactNode; source?: string }) {
  return (
    <figure className="wide-col my-6">
      <div className="overflow-x-auto" tabIndex={0} role="region" aria-label="Table, scrolls horizontally">{children}</div>
      <Caption kind="Table">{caption}</Caption>
      {source && <p className="cap">Source: <Mono>{source}</Mono></p>}
    </figure>
  );
}

export const TH = "ui border-b border-rule px-2 py-1.5 text-left text-[13px] font-semibold text-muted align-bottom";
export const TD = "ui border-b border-rule px-2 py-1.5 align-top text-[14px] tabular-nums";

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
