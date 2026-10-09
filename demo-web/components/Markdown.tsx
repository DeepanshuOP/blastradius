import type { ReactNode } from "react";

/** Inline markdown: `code` and **bold**. */
export function inline(text: string): ReactNode[] {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("`") && part.endsWith("`") ? <code key={i} className="rounded bg-slate-100 px-1 font-mono text-[11.5px]">{part.slice(1, -1)}</code>
      : part.startsWith("**") && part.endsWith("**") ? <strong key={i}>{part.slice(2, -2)}</strong> : <span key={i}>{part}</span>);
}

/** Just enough markdown for the agents' documents: headings, tables, lists, quotes, code fences. */
export default function Markdown({ text }: { text: string }) {
  const lines = text.split("\n");
  const out: ReactNode[] = [];
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (l.startsWith("```")) {
      const body: string[] = [];
      for (i++; i < lines.length && !lines[i].startsWith("```"); i++) body.push(lines[i]);
      out.push(<pre key={i} className="overflow-x-auto rounded bg-slate-900 p-3 font-mono text-[11.5px] leading-relaxed text-slate-100">{body.join("\n")}</pre>);
    } else if (l.startsWith("|")) {
      const rows: string[][] = [];
      for (; i < lines.length && lines[i].startsWith("|"); i++) {
        if (/^\|[\s|:-]+\|$/.test(lines[i])) continue;
        rows.push(lines[i].slice(1, -1).split("|").map((c) => c.trim()));
      }
      i--;
      const [head, ...body] = rows;
      out.push(
        <div key={i} className="overflow-x-auto"><table className="my-2 w-full text-left text-xs">
          <thead><tr>{head.map((c, j) => <th key={j} className="border-b border-slate-200 px-2 py-1.5 font-semibold text-slate-600">{inline(c)}</th>)}</tr></thead>
          <tbody>{body.map((r, k) => <tr key={k} className="odd:bg-slate-50">{r.map((c, j) => <td key={j} className="px-2 py-1.5 align-top">{inline(c)}</td>)}</tr>)}</tbody>
        </table></div>);
    } else if (l.startsWith("# ")) out.push(<h4 key={i} className="mt-1 text-base font-bold text-slate-900">{inline(l.slice(2))}</h4>);
    else if (l.startsWith("## ")) out.push(<h5 key={i} className="mt-3 text-sm font-semibold text-slate-800">{inline(l.slice(3))}</h5>);
    else if (l.startsWith("> ")) out.push(<blockquote key={i} className="border-l-2 border-orange-400 pl-3 italic text-slate-700">{inline(l.slice(2))}</blockquote>);
    else if (/^\s*- /.test(l)) out.push(<li key={i} className={`ml-5 list-disc ${l.startsWith("  ") ? "ml-10" : ""}`}>{inline(l.replace(/^\s*- /, ""))}</li>);
    else if (l.trim()) out.push(<p key={i} className="my-1">{inline(l)}</p>);
  }
  return <div className="space-y-0.5 text-[13px] text-slate-700">{out}</div>;
}
