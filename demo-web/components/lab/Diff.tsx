"use client";

import { useMemo } from "react";

export type Row = { l: number | null; r: number | null; a: string | null; b: string | null; kind: "same" | "del" | "add" | "chg" };

/** Line diff by longest common subsequence (prefix and suffix trimmed first); rows pair removed with added lines. */
export function lineDiff(before: string, after: string): Row[] {
  const A = before.split("\n");
  const B = after.split("\n");
  let p = 0;
  while (p < A.length && p < B.length && A[p] === B[p]) p++;
  let sa = A.length, sb = B.length;
  while (sa > p && sb > p && A[sa - 1] === B[sb - 1]) { sa--; sb--; }
  const mid: Row[] = [];
  const a = A.slice(p, sa), b = B.slice(p, sb);
  if (a.length * b.length > 4_000_000) {
    a.forEach((x, i) => mid.push({ l: p + i + 1, r: null, a: x, b: null, kind: "del" }));
    b.forEach((x, i) => mid.push({ l: null, r: p + i + 1, a: null, b: x, kind: "add" }));
  } else {
    const dp: number[][] = Array.from({ length: a.length + 1 }, () => new Array<number>(b.length + 1).fill(0));
    for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--) dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    let i = 0, j = 0;
    const dels: Row[] = [], adds: Row[] = [];
    const flush = () => {
      const n = Math.max(dels.length, adds.length);
      for (let k = 0; k < n; k++) {
        const d = dels[k], ad = adds[k];
        mid.push({ l: d?.l ?? null, r: ad?.r ?? null, a: d?.a ?? null, b: ad?.b ?? null, kind: d && ad ? "chg" : d ? "del" : "add" });
      }
      dels.length = 0; adds.length = 0;
    };
    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) { flush(); mid.push({ l: p + i + 1, r: p + j + 1, a: a[i], b: b[j], kind: "same" }); i++; j++; }
      else if (dp[i + 1][j] >= dp[i][j + 1]) { dels.push({ l: p + i + 1, r: null, a: a[i], b: null, kind: "del" }); i++; }
      else { adds.push({ l: null, r: p + j + 1, a: null, b: b[j], kind: "add" }); j++; }
    }
    while (i < a.length) { dels.push({ l: p + i + 1, r: null, a: a[i], b: null, kind: "del" }); i++; }
    while (j < b.length) { adds.push({ l: null, r: p + j + 1, a: null, b: b[j], kind: "add" }); j++; }
    flush();
  }
  const head: Row[] = A.slice(0, p).map((x, i) => ({ l: i + 1, r: i + 1, a: x, b: x, kind: "same" as const }));
  const tail: Row[] = A.slice(sa).map((x, i) => ({ l: sa + i + 1, r: sb + i + 1, a: x, b: x, kind: "same" as const }));
  return [...head, ...mid, ...tail];
}

/** The line numbers (1-based, in `after`) that differ from `before`. */
export function changedLines(before: string, after: string): Set<number> {
  const out = new Set<number>();
  lineDiff(before, after).forEach((r) => { if ((r.kind === "add" || r.kind === "chg") && r.r) out.add(r.r); });
  return out;
}

export function SideBySide({ path, before, after, context = 3 }: { path: string; before: string; after: string; context?: number }) {
  const rows = useMemo(() => lineDiff(before, after), [before, after]);
  const keep = useMemo(() => {
    const k = new Array(rows.length).fill(false);
    rows.forEach((r, i) => { if (r.kind !== "same") for (let d = -context; d <= context; d++) if (rows[i + d]) k[i + d] = true; });
    return k;
  }, [rows, context]);
  const view: (Row | null)[] = [];
  rows.forEach((r, i) => { if (keep[i]) view.push(r); else if (view[view.length - 1] !== null) view.push(null); });
  const bg = { del: "bg-red/20", add: "bg-green/20", chg: "", same: "" };
  return (
    <div className="mb-3 overflow-hidden rounded border border-rule">
      <div className="mono border-b border-rule bg-page px-2 py-1 text-xs">{path}</div>
      <div className="max-h-96 overflow-auto">
        <table className="mono w-full table-fixed border-collapse text-xs leading-[1.5]">
          <colgroup><col className="w-10" /><col /><col className="w-10" /><col /></colgroup>
          <tbody>
            {view.map((r, i) => r === null ? (
              <tr key={`g${i}`}><td colSpan={4} className="bg-page px-2 text-center text-muted">…</td></tr>
            ) : (
              <tr key={i}>
                <td className="select-none px-1 text-right text-muted">{r.l ?? ""}</td>
                <td className={`whitespace-pre-wrap break-all px-1 ${r.kind === "del" || r.kind === "chg" ? "bg-red/20" : bg[r.kind]}`}>{r.a ?? ""}</td>
                <td className="select-none px-1 text-right text-muted">{r.r ?? ""}</td>
                <td className={`whitespace-pre-wrap break-all px-1 ${r.kind === "add" || r.kind === "chg" ? "bg-green/20" : ""}`}>{r.b ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function UnifiedDiff({ diff }: { diff: string }) {
  return (
    <pre className="mono m-0 max-h-96 overflow-auto rounded border border-rule bg-page p-2 text-xs leading-[1.5]">
      {diff.split("\n").map((ln, i) => (
        <div key={i} className={ln.startsWith("+") && !ln.startsWith("+++") ? "bg-green/20" : ln.startsWith("-") && !ln.startsWith("---") ? "bg-red/20" : ln.startsWith("@@") ? "text-blue" : ln.startsWith("diff") || ln.startsWith("index") || ln.startsWith("---") || ln.startsWith("+++") ? "text-muted" : ""}>{ln || " "}</div>
      ))}
    </pre>
  );
}
