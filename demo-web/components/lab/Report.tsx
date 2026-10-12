"use client";

import { useMemo, useState } from "react";
import { Info } from "./Info";
import { BTN, Empty, Icon, fmtMs, sha } from "./common";
import type { LabState } from "./types";

function download(name: string, text: string, type: string) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

/** The comment split into its summary (everything before the first "###") and its titled sections. */
export function splitComment(md: string): { title: string; summary: string; sections: { title: string; body: string }[] } {
  const lines = md.split("\n").filter((l) => !l.startsWith("<!--"));
  const title = (lines.find((l) => l.startsWith("## ")) ?? "## BlastRadius").slice(3);
  const sections: { title: string; body: string }[] = [];
  const head: string[] = [];
  let cur: { title: string; body: string[] } | null = null;
  const flush = () => { if (cur) sections.push({ title: cur.title, body: cur.body.join("\n") }); };
  for (const l of lines) {
    if (l.startsWith("### ")) { flush(); cur = { title: l.slice(4), body: [] }; }
    else if (cur) cur.body.push(l);
    else if (!l.startsWith("## ")) head.push(l);
  }
  flush();
  return { title, summary: head.join("\n"), sections };
}

/** The PR comment as a GitHub-style card: the summary open, every other section collapsed. Nothing is posted. */
export function ReportPanel({ s }: { s: LabState }) {
  const c = s.report.comment;
  const [raw, setRaw] = useState(false);
  const parts = useMemo(() => (c ? splitComment(c) : null), [c]);
  const rederived = Boolean(s.header?.rederived);
  return (
    <>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="ui rounded bg-panel2 px-1.5 py-0.5 text-2xs font-semibold tracking-wider text-muted">NOT POSTED ANYWHERE</span>
        {rederived && <Info label="About this comment"><span className="block">This is the comment as the bot rendered it when the run was recorded. The race and arena were re-derived afterwards; their numbers can differ from the first-failure position written here.</span></Info>}
        <span className="flex-1" />
        <label className="ui flex items-center gap-1 text-xs text-muted"><input type="checkbox" checked={raw} disabled={!c} onChange={(e) => setRaw(e.target.checked)} /> raw Markdown</label>
        <button type="button" disabled={!c} onClick={() => c && download("blastradius-run.md", c, "text/markdown")} className={BTN}>Download .md</button>
        <button type="button" disabled={!s.events.length} onClick={() => download("blastradius-run.json", JSON.stringify({ header: s.header, summary: s.report.summary, comment: c, events: s.events }, null, 1), "application/json")} className={BTN}>Download .json</button>
      </div>
      {!c || !parts ? <Empty title="The pull-request comment is rendered here at the end of the run." /> : raw ? (
        <pre className="mono m-0 max-h-[28rem] overflow-auto whitespace-pre-wrap rounded bg-page p-3 text-xs">{c}</pre>
      ) : (
        <article className="max-w-3xl overflow-hidden rounded-md border border-rule bg-panel" aria-label="Pull request comment">
          <header className="flex items-center gap-2.5 border-b border-rule bg-panel2 px-3 py-2">
            <span className="ui grid h-8 w-8 shrink-0 place-items-center rounded-full bg-accent text-xs font-bold text-white" aria-hidden="true">BR</span>
            <span className="ui text-sm"><span className="font-semibold">blastradius-bot</span> <span className="text-muted">commented on PR #1</span></span>
            <span className="ui ml-auto rounded-full border border-rule px-2 text-2xs text-muted">bot</span>
          </header>
          <div className="px-4 py-3">
            <h3 className="ui m-0 mb-1 text-md font-semibold">{parts.title}</h3>
            <MarkdownLite text={parts.summary} bare className="" />
            <div className="mt-3 divide-y divide-rule rounded border border-rule">
              {parts.sections.map((x) => (
                <details key={x.title} className="group">
                  <summary className="ui flex cursor-pointer items-center gap-2 px-3 py-2 text-sm font-medium hover:bg-panel2"><Icon name="chevron" className="text-xs transition-transform group-open:rotate-90" />{x.title.replace(/^\d+\.\s*/, "")}</summary>
                  <div className="px-3 pb-3"><MarkdownLite text={x.body} bare className="" /></div>
                </details>
              ))}
            </div>
          </div>
        </article>
      )}
    </>
  );
}

/** A small Markdown renderer for the bot's own output: headings, tables, code fences, details, lists, inline code. */
export function MarkdownLite({ text, className = "max-h-[32rem] overflow-y-auto", bare = false }: { text: string; className?: string; bare?: boolean }) {
  const lines = text.split("\n").filter((l) => !l.startsWith("<!--"));
  const out: JSX.Element[] = [];
  let i = 0;
  const inline = (t: string) => t.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((p, k) =>
    p.startsWith("`") ? <code key={k} className="mono rounded bg-page px-1 text-xs">{p.slice(1, -1)}</code>
      : p.startsWith("**") ? <strong key={k}>{p.slice(2, -2)}</strong> : p);
  while (i < lines.length) {
    const l = lines[i];
    if (l.startsWith("```")) {
      const buf: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) buf.push(lines[i++]);
      i++;
      out.push(<pre key={i} className="mono m-0 mb-2 max-h-72 overflow-auto rounded bg-page p-2 text-xs">{buf.join("\n")}</pre>);
    } else if (l.startsWith("|")) {
      const rows: string[][] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        if (!/^\|[-: |]+\|$/.test(lines[i])) rows.push(lines[i].split(/(?<!\\)\|/).slice(1, -1).map((c) => c.trim().replace(/\\\|/g, "|")));
        i++;
      }
      out.push(
        <div key={i} className="relative mb-2 overflow-x-auto"><table className="w-full text-xs"><thead><tr>{rows[0].map((h, k) => <th key={k} className="ui border-b border-rule px-1.5 py-1 text-left text-muted">{inline(h)}</th>)}</tr></thead>
          <tbody>{rows.slice(1).map((r, k) => <tr key={k}>{r.map((c, j) => <td key={j} className="border-b border-rule px-1.5 py-1 align-top">{inline(c)}</td>)}</tr>)}</tbody></table></div>);
    } else if (l.startsWith("### ")) { out.push(<h4 key={i} className="ui m-0 mb-1 mt-3 text-base">{inline(l.slice(4))}</h4>); i++; }
    else if (l.startsWith("## ")) { out.push(<h3 key={i} className="ui m-0 mb-1 text-md">{inline(l.slice(3))}</h3>); i++; }
    else if (l.startsWith("<")) { i++; }
    else if (l.trim() === "" || l.startsWith("---")) { i++; }
    else { const t = l.replace(/<\/?sub>/g, ""); out.push(<p key={i} className={`ui m-0 mb-1.5 text-sm ${/^_.*_$/.test(t) ? "italic text-muted" : ""}`}>{inline(/^_.*_$/.test(t) ? t.slice(1, -1) : t)}</p>); i++; }
  }
  return <div className={`${bare ? "" : "rounded border border-rule bg-panel p-3"} ${className}`}>{out}</div>;
}

/** Everything needed to audit the run: commands, SHAs, model and sampling, cache, durations, mode, live vs recorded. */
export function IntegrityPanel({ s }: { s: LabState }) {
  const h = s.header ?? {};
  const rep = s.mode === "replay";
  const sum = s.report.summary;
  const cached = s.repair.replies.filter((r) => r.from_cache).length;
  const live = s.repair.replies.length - cached;
  const rows: [string, string][] = [
    ["Mode", rep ? `REPLAY of a recording made ${h.date ?? "?"} at BlastRadius ${h.git_sha ?? "?"}` : "LIVE: every stage executed in this session"],
    ["Command", (h.command ?? []).join(" ") || "n/a"],
    ["Repository", `${s.repo?.name ?? "?"} @ ${sha(s.repo?.commit)} (${s.repo?.url ?? ""})`],
    ["Head commit", sha(s.change?.head)],
    ["Interpreter", s.repo?.interpreter ?? "n/a"],
    ["Model", h.model ? `${h.model} · temperature ${h.temperature}, seed ${h.seed}` : `none (${h.llm ?? "n/a"})`],
    ["LLM cache", h.cache ?? "n/a"],
    ["Token ledger", h.ledger ? `${h.ledger} (the lab's own; E3's usage.jsonl is never written)` : "n/a"],
    ["Model calls", s.repair.replies.length ? `${s.repair.replies.length}: ${live} live, ${cached} from cache` : "0"],
    ["Tokens", `${s.tokens.total.toLocaleString()} total (${s.tokens.prompt.toLocaleString()} prompt, ${s.tokens.completion.toLocaleString()} completion)`],
    ["Test command", s.triage ? "pytest, one process, BlastRadius test-case order (plugin sort), junit xml" : "n/a"],
    ...(s.tests.race?.order_rule ? [["Order rule", `${s.tests.race.order_rule.id}, fixed ${s.tests.race.order_rule.fixed}, ${s.tests.race.order_rule.source}`] as [string, string]] : []),
    ...(h.rederived ? [["Re-derived", `${String((h.rederived as { date?: string }).date ?? "").slice(0, 10)}: ${(h.rederived as { events?: string[] }).events?.join(", ")}`] as [string, string]] : []),
    ["Stage durations", Object.entries(s.stage).map(([k, v]) => `${k} ${fmtMs(v.dur_ms)}`).join(" · ") || "n/a"],
    ["Unit of counts", String(sum?.unit ?? s.triage?.unit ?? "test cases for the suite, unique canonical test ids for triage")],
  ];
  if (h.scenario_note || s.repo?.scenario_note) rows.splice(2, 0, ["Scenario", String(h.scenario_note ?? s.repo?.scenario_note)]);
  if (!s.events.length) return <Empty title="The audit trail of the run appears here as soon as it starts." />;
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
      <dl className="m-0 grid grid-cols-1 gap-x-6 sm:grid-cols-2">
        {rows.map(([k, v]) => (
          <div key={k} className="mb-3 min-w-0"><dt className="ui text-2xs uppercase tracking-wide text-muted">{k}</dt><dd className="mono m-0 text-xs [overflow-wrap:anywhere]">{v}</dd></div>
        ))}
      </dl>
      <div>
        <h4 className="ui m-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted">Live and recorded</h4>
        <ul className="ui m-0 list-disc space-y-1 pl-5 text-sm">
          <li>{rep ? "Read from a recorded run; none computed in this session." : "Computed in this session."}</li>
          <li>{h.model ? (rep ? "Model reply: recorded at the time of the run." : live > 0 ? `${live} model call(s) went to the provider${cached ? `; ${cached} from the lab cache` : ""}.` : "Model reply: lab cache; no tokens spent.") : "No model was called."}</li>
          <li>The retest-all lane is computed from measured durations.</li>
          <li>FROM BR-BENCH numbers are read from <span className="mono">paper/generated</span>.</li>
        </ul>
      </div>
    </div>
  );
}
