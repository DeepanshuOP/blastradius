"use client";

import { useEffect, useState } from "react";
import Markdown from "./Markdown";
import { Card, Mono } from "./ui";

type UseItDoc = {
  generated_at_git_sha: string; pinned_ref: string; live_pr_url: string;
  setup_steps: { n: number; title: string; body: string }[];
  workflow_yaml: string; bot_comment_md: string | null; bot_comment_source: string;
  jenkinsfile: string; cli: { cmd: string; help: string; line: string }[];
};
type CompareLite = {
  time: { e1: { rows: { id: string; recall_first_10pct: string }[] } | null };
  cost: { ledger: { paid_usd: number } } | null;
};

function Copy({ text, label = "Copy" }: { text: string; label?: string }) {
  const [done, setDone] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); } catch { /* clipboard unavailable; the text stays selectable */ }
      document.body.removeChild(ta);
    }
    setDone(true);
    setTimeout(() => setDone(false), 1500);
  };
  return (
    <button onClick={copy} className="rounded border border-slate-300 bg-panel px-2 py-0.5 text-[13px] font-medium text-slate-700 hover:bg-slate-100">
      {done ? "Copied" : label}
    </button>
  );
}

function CodeBlock({ title, text, max = "max-h-80" }: { title: string; text: string; max?: string }) {
  return (
    <div className="rounded-md border border-slate-200">
      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-3 py-1.5">
        <span className="text-[13px] font-semibold text-slate-700">{title}</span>
        <Copy text={text} />
      </div>
      <pre className={`${max} overflow-auto p-3 text-[12.5px] leading-relaxed text-slate-800`}>{text}</pre>
    </div>
  );
}

const EVIDENCE: Record<number, [string, string]> = {
  1: ["#compare-papers", "Compare, capabilities"], 4: ["#compare-cost", "Compare, cost"],
  5: ["#compare-time", "Compare, time"], 6: ["#compare-safety", "Compare, safety"],
};

export default function UseIt() {
  const [d, setD] = useState<UseItDoc | null>(null);
  const [c, setC] = useState<CompareLite | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    fetch("/data/use_it.json", { cache: "no-store" })
      .then((r) => { if (!r.ok) throw new Error(`use_it.json: HTTP ${r.status}`); return r.json() as Promise<UseItDoc>; })
      .then(setD).catch((e) => setErr(String(e)));
    fetch("/data/compare.json", { cache: "no-store" }).then((r) => r.json() as Promise<CompareLite>).then(setC).catch(() => setC(null));
  }, []);
  if (err) return <p className="rounded border border-red-200 bg-red-50 p-3 text-[15px] text-red-700">Could not load /data/use_it.json ({err}). Run <Mono>make demo-data</Mono>.</p>;
  if (!d) return <p className="text-[15px] text-slate-500">Loading…</p>;

  const first10 = (id: string) => c?.time?.e1?.rows.find((r) => r.id === id)?.recall_first_10pct;
  const ours = first10("ours");
  const retest = first10("B0");
  const why: { text: string; panel: number }[] = [
    { text: `Finds the failing tests sooner on projects with history${ours && retest ? ` (BR-Bench test split: share of failing test files found in the first 10% of the suite, ${ours} against ${retest} for retest-all)` : ""}.`, panel: 5 },
    { text: "Tells you which failures are yours: a failure that also fails on the base commit is marked inherited (E2 triage is a small-sample result).", panel: 1 },
    { text: "Proposes a fix only when the whole suite passes; otherwise the patch is shown as not validated.", panel: 6 },
    { text: `Costs $${c?.cost ? c.cost.ledger.paid_usd.toFixed(2) : "0.00"} on the free tier.`, panel: 4 },
  ];

  return (
    <div className="space-y-6">
      <Card title="Why use it">
        <ul className="space-y-2">
          {why.map((w) => (
            <li key={w.text} className="flex flex-wrap items-baseline gap-2">
              <span className="text-slate-900">{w.text}</span>
              <a href={EVIDENCE[w.panel][0]} className="ui text-[14px]">Evidence: {EVIDENCE[w.panel][1]}</a>
            </li>
          ))}
        </ul>
      </Card>

      <Card title="1, GitHub Action: a comment on every pull request" step={1}>
        <ol className="mb-4 space-y-3">
          {d.setup_steps.map((s) => (
            <li key={s.n}>
              <p className="font-semibold text-slate-900">Step {s.n}: {s.title}</p>
              <div className="mt-1 text-[13px] text-slate-700"><Markdown text={s.body} /></div>
            </li>
          ))}
        </ol>
        <CodeBlock title={`.github/workflows/blastradius-bot.yml (tool pinned to ${d.pinned_ref.slice(0, 10)})`} text={d.workflow_yaml} />
        <p className="mt-3 text-[15px]">
          Live example: <a className="break-all" href={d.live_pr_url} target="_blank" rel="noreferrer">{d.live_pr_url}</a>. The comment below is
          the bot&apos;s latest comment on that pull request ({d.bot_comment_source}).
        </p>
        {d.bot_comment_md && (
          <div className="mt-3 rounded-md border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-3 py-1.5">
              <span className="text-[13px] font-semibold text-slate-700">Recorded bot comment</span>
              <Copy text={d.bot_comment_md} />
            </div>
            <div className="max-h-[32rem] overflow-auto p-3 text-[15px]"><Markdown text={d.bot_comment_md.replace("<!-- blastradius-bot -->", "")} /></div>
          </div>
        )}
      </Card>

      <Card title="2, Jenkins: Jenkins runs, BlastRadius decides" step={2}>
        <ul className="mb-3 list-disc space-y-1 pl-5 text-[15px]">
          <li>Jenkins stays the executor: it checks out, runs and reports, as it does today.</li>
          <li>BlastRadius decides the order (riskiest tests first) and, for each failure, whether it is yours, inherited or flaky.</li>
          <li>For a failure that is yours it suggests a fix, accepted only if the full suite passes; nothing is merged or pushed.</li>
        </ul>
        <CodeBlock title="integrations/jenkins/Jenkinsfile (an example; not deployed on a Jenkins server by this project)" text={d.jenkinsfile} />
      </Card>

      <Card title="3, Command line" step={3}>
        <div className="space-y-3">
          {d.cli.map((x) => (
            <div key={x.cmd}>
              <p className="mb-1 text-[15px]"><Mono>{x.cmd}</Mono>: {x.help}</p>
              <CodeBlock title="shell" text={x.line} max="max-h-24" />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
