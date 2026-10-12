"use client";

import { useEffect, useMemo, useState } from "react";
import Markdown from "./Markdown";
import { Badge, Card, Mono } from "./ui";

type Citation = { id: string; source: string; ref: string; title: string };
type Item = { id: string; source: string; ref: string; text: string };
type Answer = {
  id?: string; type?: string; question: string; qtype: string; answer: string | null; citations: Citation[];
  context: Item[]; cited: number[]; faithful: boolean | null; model: string; tokens: number; notes: string[];
};
type RagDoc = {
  generated_at_git_sha: string;
  ask: { model: string; questions: Answer[] } | null;
  retrieval_md: string | null;
  bot_comment_md: string | null;
};

const SOURCE_TONE: Record<string, "slate" | "green" | "amber" | "red"> = { code: "slate", failure: "red", doc: "green", e1: "amber" };

/** Split an answer at [Sk] markers so each becomes a clickable chip. */
function Chips({ text, onPick, valid }: { text: string; onPick: (id: string) => void; valid: Set<string> }) {
  const parts = text.split(/(\[S\d+\])/g);
  return (
    <p className="whitespace-pre-wrap leading-relaxed">
      {parts.map((p, i) => {
        const m = /^\[(S\d+)\]$/.exec(p);
        if (!m) return <span key={i}>{p}</span>;
        const ok = valid.has(m[1]);
        return (
          <button key={i} onClick={() => ok && onPick(m[1])} title={ok ? "show the cited item" : "not a retrieved item"}
            className={`mx-0.5 rounded px-1.5 py-0.5 align-baseline text-[12.5px] font-semibold ring-1 ${ok ? "bg-sky-50 text-sky-800 ring-sky-200 hover:bg-sky-100" : "bg-red-50 text-red-700 ring-red-200"}`}>
            {m[1]}
          </button>
        );
      })}
    </p>
  );
}

function AnswerView({ a }: { a: Answer }) {
  const [open, setOpen] = useState<string | null>(null);
  const valid = useMemo(() => new Set(a.context.map((c) => c.id)), [a]);
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 text-[13px]">
        <Badge tone="slate">{a.qtype}</Badge>
        {a.faithful === true && a.cited.length > 0 && <Badge tone="green">every citation points to a retrieved item</Badge>}
        {a.faithful === false && <Badge tone="red">cites an item that was not retrieved</Badge>}
        {a.answer === null && <Badge tone="amber">retrieval only (no model)</Badge>}
        {a.model && <span className="text-slate-500">{a.model}, {a.tokens.toLocaleString()} tokens</span>}
      </div>
      {a.answer !== null && <div className="rounded border border-slate-200 bg-slate-50 p-4 text-[15px] text-slate-800"><Chips text={a.answer} onPick={setOpen} valid={valid} /></div>}
      {a.notes.length > 0 && <ul className="list-disc pl-5 text-[13px] text-slate-500">{a.notes.map((n) => <li key={n}>{n}</li>)}</ul>}
      <div>
        <h4 className="mb-2 text-[13px] font-semibold text-slate-500">Retrieved context ({a.context.length})</h4>
        <ul className="space-y-2">
          {a.context.map((c) => (
            <li key={c.id} className={`rounded border bg-white p-3 text-[13px] ${open === c.id ? "border-sky-400 ring-1 ring-sky-200" : "border-slate-200"}`}>
              <button className="flex w-full flex-wrap items-center gap-2 text-left" onClick={() => setOpen(open === c.id ? null : c.id)}>
                <span className="font-semibold text-slate-900">{c.id}</span>
                <Badge tone={SOURCE_TONE[c.source] ?? "slate"}>{c.source}</Badge>
                <Mono>{c.ref}</Mono>
              </button>
              {open === c.id && <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap border border-rule bg-panel p-3 font-mono text-[12.5px] text-ink">{c.text}</pre>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default function Ask() {
  const [doc, setDoc] = useState<RagDoc | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [sel, setSel] = useState(0);
  const [live, setLive] = useState<{ live: boolean; repos: string[] } | null>(null);
  const [question, setQuestion] = useState("");
  const [repo, setRepo] = useState("");
  const [busy, setBusy] = useState(false);
  const [liveAnswer, setLiveAnswer] = useState<Answer | null>(null);
  const [liveErr, setLiveErr] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/rag.json", { cache: "no-store" }).then((r) => (r.ok ? r.json() : Promise.reject(`HTTP ${r.status}`)))
      .then(setDoc).catch((e) => setErr(String(e)));
    fetch("/api/ask", { cache: "no-store" }).then((r) => (r.ok ? r.json() : null))
      .then((j) => { if (j?.ok) { setLive({ live: j.live, repos: j.repos }); setRepo(j.repos[0] ?? ""); } }).catch(() => setLive(null));
  }, []);

  const ask = async () => {
    setBusy(true); setLiveErr(null); setLiveAnswer(null);
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ question, repo }) });
      const j = await r.json();
      if (!j.ok) setLiveErr(`${j.error}${j.detail ? `: ${j.detail}` : ""}`);
      else setLiveAnswer(j.result as Answer);
    } catch (e) { setLiveErr(String(e)); } finally { setBusy(false); }
  };

  const qs = doc?.ask?.questions ?? [];
  const cur = qs[sel];
  return (
    <div className="space-y-6">
      <p className="ui m-0 border border-rule bg-panel px-4 py-3 text-[15px]" role="status">
        <span className="font-semibold">Mode: {live?.live ? "live (a key and the network are present)" : "recorded answers (no live key or network here)"}.</span>{" "}
        Exploratory, not pre-registered. Answers come from retrieval over code, BR-Bench failure history and docs; the model is told to
        answer only from that context and to cite every claim. The checks below say whether citations point at retrieved items, not
        whether an answer is correct.
      </p>
      {err && <p className="text-[15px] text-red-700">Could not load /data/rag.json: {err}. Run <Mono>make demo-data</Mono>.</p>}

      <Card title="Ask a question (live)">
        {live?.live ? (
          <div className="space-y-3">
            <div className="flex flex-col gap-2 sm:flex-row">
              <select value={repo} onChange={(e) => setRepo(e.target.value)} className="rounded-md border border-slate-300 bg-white px-3 py-2 text-[15px]">
                {live.repos.map((r) => <option key={r}>{r}</option>)}
              </select>
              <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="What is at risk if I change src/click/parser.py?"
                className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-[15px]" />
              <button onClick={ask} disabled={busy || question.trim().length < 8}
                className="bg-accent px-5 py-2 text-[15px] font-semibold text-white disabled:bg-muted">{busy ? "Asking…" : "Ask"}</button>
            </div>
            {liveErr && <p className="text-[15px] text-red-700">{liveErr}</p>}
            {liveAnswer && <AnswerView a={liveAnswer} />}
          </div>
        ) : (
          <p className="text-slate-600">
            Live asking needs <Mono>GROQ_API_KEY</Mono> in the server's environment and the network (run
            <Mono> make demo-web</Mono> locally). Showing the recorded answers below instead.
          </p>
        )}
      </Card>

      <Card title={`Recorded answers (${qs.length} fixed questions${doc?.ask ? `, ${doc.ask.model}` : ""})`}>
        {!doc?.ask && <p className="text-slate-600">No answers have been recorded yet (<Mono>python -m analysis.ask_eval record</Mono>).</p>}
        {qs.length > 0 && (
          <div className="space-y-4">
            <select value={sel} onChange={(e) => setSel(Number(e.target.value))} className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-[15px]">
              {qs.map((q, i) => <option key={i} value={i}>{q.id}, {q.type}, {q.question.slice(0, 110)}</option>)}
            </select>
            {cur && <><p className="text-[15px] font-medium text-slate-900">{cur.question}</p><AnswerView a={cur} /></>}
          </div>
        )}
      </Card>

      {doc?.retrieval_md && <Card title="Retrieval study (make rag-eval)"><Markdown text={doc.retrieval_md} /></Card>}
      {doc?.bot_comment_md && <Card title="PR bot comment (recording run)"><Markdown text={doc.bot_comment_md} /></Card>}
    </div>
  );
}
