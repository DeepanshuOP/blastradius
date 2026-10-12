"use client";

import { useState } from "react";
import { Empty, Panel, Prov, fmtMs, sha } from "./common";
import type { LabState } from "./types";

function download(name: string, text: string, type: string) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

/** The PR comment as the bot would post it, and the downloadable run. */
export function ReportPanel({ s }: { s: LabState }) {
  const c = s.report.comment;
  const [raw, setRaw] = useState(false);
  const html = c ?? "";
  return (
    <Panel id="panel-report" title="PR comment preview" right={<>
      <Prov mode={s.mode} />
      <button type="button" disabled={!c} onClick={() => c && download("blastradius-run.md", c, "text/markdown")} className="ui rounded border border-rule px-2 py-0.5 text-[12px] disabled:opacity-40">Download .md</button>
      <button type="button" disabled={!s.events.length} onClick={() => download("blastradius-run.json", JSON.stringify({ header: s.header, summary: s.report.summary, comment: c, events: s.events }, null, 1), "application/json")} className="ui rounded border border-rule px-2 py-0.5 text-[12px] disabled:opacity-40">Download .json</button>
    </>}>
      {!c ? <Empty>The comment is rendered at the end of the run.</Empty> : (
        <>
          <label className="ui mb-2 flex items-center gap-1 text-[12px] text-muted"><input type="checkbox" checked={raw} onChange={(e) => setRaw(e.target.checked)} /> show raw Markdown</label>
          {raw ? <pre className="mono m-0 max-h-[28rem] overflow-auto whitespace-pre-wrap rounded bg-page p-3 text-[12px]">{html}</pre> : <MarkdownLite text={html} />}
          <p className="cap m-0 mt-2 text-[12px]">This is the text <span className="mono">src.agents.bot.render_comment</span> produced in this run. Nothing was posted anywhere.</p>
        </>
      )}
    </Panel>
  );
}

/** A small Markdown renderer for the bot's own output: headings, tables, code fences, details, lists, inline code. */
function MarkdownLite({ text }: { text: string }) {
  const lines = text.split("\n").filter((l) => !l.startsWith("<!--"));
  const out: JSX.Element[] = [];
  let i = 0;
  const inline = (t: string) => t.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((p, k) =>
    p.startsWith("`") ? <code key={k} className="mono rounded bg-page px-1 text-[12px]">{p.slice(1, -1)}</code>
      : p.startsWith("**") ? <strong key={k}>{p.slice(2, -2)}</strong> : p);
  while (i < lines.length) {
    const l = lines[i];
    if (l.startsWith("```")) {
      const buf: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) buf.push(lines[i++]);
      i++;
      out.push(<pre key={i} className="mono m-0 mb-2 max-h-72 overflow-auto rounded bg-page p-2 text-[11.5px]">{buf.join("\n")}</pre>);
    } else if (l.startsWith("|")) {
      const rows: string[][] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        if (!/^\|[-: |]+\|$/.test(lines[i])) rows.push(lines[i].split(/(?<!\\)\|/).slice(1, -1).map((c) => c.trim().replace(/\\\|/g, "|")));
        i++;
      }
      out.push(
        <div key={i} className="mb-2 overflow-x-auto"><table className="w-full text-[12px]"><thead><tr>{rows[0].map((h, k) => <th key={k} className="ui border-b border-rule px-1.5 py-1 text-left text-muted">{inline(h)}</th>)}</tr></thead>
          <tbody>{rows.slice(1).map((r, k) => <tr key={k}>{r.map((c, j) => <td key={j} className="border-b border-rule px-1.5 py-1 align-top">{inline(c)}</td>)}</tr>)}</tbody></table></div>);
    } else if (l.startsWith("### ")) { out.push(<h4 key={i} className="ui m-0 mb-1 mt-3 text-[14px]">{inline(l.slice(4))}</h4>); i++; }
    else if (l.startsWith("## ")) { out.push(<h3 key={i} className="ui m-0 mb-1 text-[16px]">{inline(l.slice(3))}</h3>); i++; }
    else if (l.startsWith("<")) { i++; }
    else if (l.trim() === "" || l.startsWith("---")) { i++; }
    else { const t = l.replace(/<\/?sub>/g, ""); out.push(<p key={i} className={`ui m-0 mb-1.5 text-[13px] ${/^_.*_$/.test(t) ? "italic text-muted" : ""}`}>{inline(/^_.*_$/.test(t) ? t.slice(1, -1) : t)}</p>); i++; }
  }
  return <div className="max-h-[32rem] overflow-y-auto rounded border border-rule bg-panel p-3">{out}</div>;
}

/** Everything needed to audit the run: commands, SHAs, model and sampling, cache, durations, mode, live vs recorded. */
export function IntegrityDrawer({ s, onClose }: { s: LabState; onClose: () => void }) {
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
    ["Test command", s.triage ? "pytest, one process, at-risk files first (plugin sort), junit xml" : "n/a"],
    ["Stage durations", Object.entries(s.stage).map(([k, v]) => `${k} ${fmtMs(v.dur_ms)}`).join(" · ") || "n/a"],
    ["Unit of counts", String(sum?.unit ?? s.triage?.unit ?? "test cases for the suite, unique canonical test ids for triage")],
  ];
  if (h.scenario_note || s.repo?.scenario_note) rows.splice(2, 0, ["Scenario", String(h.scenario_note ?? s.repo?.scenario_note)]);
  return (
    <aside className="fixed inset-y-0 right-0 z-40 flex w-full max-w-md flex-col border-l border-rule bg-panel shadow-2xl" aria-label="Integrity">
      <header className="flex items-center justify-between border-b border-rule px-4 py-3">
        <h3 className="ui m-0 text-[14px] font-semibold">Integrity</h3>
        <button type="button" onClick={onClose} className="ui rounded border border-rule px-2 py-0.5 text-[12px]">Close</button>
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <dl className="m-0">
          {rows.map(([k, v]) => (
            <div key={k} className="mb-3"><dt className="ui text-[11px] uppercase tracking-wide text-muted">{k}</dt><dd className="mono m-0 break-words text-[12px]">{v}</dd></div>
          ))}
        </dl>
        <h4 className="ui m-0 mb-1 mt-4 text-[12px] font-semibold uppercase text-muted">Live and recorded</h4>
        <ul className="ui m-0 list-disc pl-5 text-[12.5px]">
          <li>{rep ? "Every event on screen is read from a recorded run; none was computed in this session." : "Graph, ranking, test results, triage, patch checks and counts were computed in this session."}</li>
          <li>{h.model ? (rep ? "The model reply was recorded at the time of the run." : live > 0 ? `${live} model call(s) went to the provider in this run${cached ? `; ${cached} came from the lab cache` : ""}.` : "The model reply came from the lab cache; no tokens were spent in this session.") : "No model was called."}</li>
          <li>The alphabetical lane of the test race is computed from measured durations, not a second run.</li>
          <li>Numbers labelled FROM BR-BENCH are read from <span className="mono">paper/generated</span>, not from this run.</li>
        </ul>
      </div>
    </aside>
  );
}
