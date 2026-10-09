"use client";

import { useEffect, useState } from "react";
import Markdown from "./Markdown";
import { Badge, Card, KV, Mono, short } from "./ui";

type FileRow = { path: string; role: string; score: number; reasons: string[] };
type TestRow = { test_id: string; file: string; distance: number; score: number; reasons: string[] };
type Impact = {
  title: string; story: string; repo: string; base_branch: string; base_sha: string; provider: string;
  files: FileRow[]; tests: TestRow[]; unaffected_tests: string[]; risk: string; risk_reasons: string[];
  gaps: string[]; cochange_hints: { file: string; partner: string; count: number }[];
  graph_stats: { nodes: number; edges: number; files_parsed: number; parse_failures: number; graphify_commit: string };
};
type Reply = { ok: true; url: string; branch: string | null; clone_dir: string; impact: Impact; markdown: string }
  | { ok: false; error: string; detail?: string };

/** One-click examples; each was run end to end through this route before it was listed. */
const EXAMPLES: { url: string; story: string; lang: string }[] = [
  { url: "https://github.com/pallets/itsdangerous", lang: "Python",
    story: "Add support for a max_age grace period when validating timestamped signatures so slightly expired tokens can be accepted" },
  { url: "https://github.com/pallets/markupsafe", lang: "Python",
    story: "Make escape() also escape the backtick character so escaped strings are safe inside backtick-quoted HTML attributes" },
  { url: "https://github.com/apache/commons-cli", lang: "Java",
    story: "Allow the DefaultParser to accept long option values separated by a colon, such as --file:path, in addition to = and a space" },
];

const riskTone = (r: string) => (r === "high" ? "red" : r === "medium" ? "amber" : "green") as "red" | "amber" | "green";

export default function Analyze() {
  const [live, setLive] = useState<boolean | null>(null);
  const [url, setUrl] = useState(EXAMPLES[0].url);
  const [story, setStory] = useState(EXAMPLES[0].story);
  const [branch, setBranch] = useState("");
  const [busy, setBusy] = useState(false);
  const [reply, setReply] = useState<Reply | null>(null);
  const [secs, setSecs] = useState(0);

  useEffect(() => {
    fetch("/api/analyze", { cache: "no-store" }).then((r) => r.json()).then((j) => setLive(!!j.ok)).catch(() => setLive(false));
  }, []);
  useEffect(() => {
    if (!busy) return;
    const t = setInterval(() => setSecs((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [busy]);

  const analyze = async (u = url, s = story, b = branch) => {
    setBusy(true); setSecs(0); setReply(null);
    try {
      const r = await fetch("/api/analyze", { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ url: u, story: s, branch: b }) });
      setReply(await r.json());
    } catch (e) {
      setReply({ ok: false, error: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const im = reply && reply.ok ? reply.impact : null;
  const change = im?.files.filter((f) => f.role === "change") ?? [];
  const deps = im?.files.filter((f) => f.role !== "change") ?? [];

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Analyze a repository</h2>
        <p className="mt-1 max-w-3xl text-sm text-slate-600">
          Give a public GitHub repository (Python or Java) and a user story. BlastRadius clones it, builds the code graph at
          HEAD and runs the offline Impact Analysis Agent: which files the story touches, what depends on them, and which tests
          are at risk, ranked by graph distance. No language model and no token are used.
        </p>
      </div>

      {live === false && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          This is the static build, so there is no analysis server. Run <Mono>make demo-web</Mono> locally to analyse live,
          or use the command line twin: <Mono>make analyze REPO=https://github.com/owner/repo STORY=&quot;...&quot;</Mono>.
        </div>
      )}

      <Card title="Repository and user story">
        <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); analyze(); }}>
          <div className="grid gap-3 sm:grid-cols-[1fr_12rem]">
            <label className="text-sm">
              <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500">GitHub URL</span>
              <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://github.com/owner/repo"
                className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-[13px] shadow-sm focus:border-slate-500 focus:outline-none" />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500">Branch (optional)</span>
              <input value={branch} onChange={(e) => setBranch(e.target.value)} placeholder="default branch"
                className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-[13px] shadow-sm focus:border-slate-500 focus:outline-none" />
            </label>
          </div>
          <label className="block text-sm">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500">User story</span>
            <textarea value={story} onChange={(e) => setStory(e.target.value)} rows={3}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none" />
          </label>
          <div className="flex flex-wrap items-center gap-3">
            <button type="submit" disabled={busy || live === false}
              className="rounded-md bg-slate-900 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400">
              {busy ? `Analysing… ${secs}s` : "Analyze"}
            </button>
            <span className="text-xs text-slate-500">Clone ≤ 120 s (depth 50, reused), analysis ≤ 180 s. Localhost only.</span>
          </div>
        </form>
        <div className="mt-4 border-t border-slate-100 pt-3">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Examples</p>
          <div className="grid gap-2 md:grid-cols-3">
            {EXAMPLES.map((x) => (
              <button key={x.url} disabled={busy || live === false}
                onClick={() => { setUrl(x.url); setStory(x.story); setBranch(""); analyze(x.url, x.story, ""); }}
                className="rounded-lg border border-slate-200 bg-white p-3 text-left text-xs transition hover:border-slate-400 disabled:opacity-60">
                <span className="flex items-center justify-between gap-2">
                  <span className="font-mono font-semibold text-slate-900">{x.url.replace("https://github.com/", "")}</span>
                  <Badge tone="slate">{x.lang}</Badge>
                </span>
                <span className="mt-1 block text-slate-600">{x.story}</span>
              </button>
            ))}
          </div>
        </div>
      </Card>

      {reply && !reply.ok && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <p className="font-semibold">{reply.error}</p>
          {reply.detail && <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap font-mono text-[11px]">{reply.detail}</pre>}
        </div>
      )}

      {im && reply?.ok && (
        <>
          <div className="grid gap-3 sm:grid-cols-4">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <Badge tone={riskTone(im.risk)}>{im.risk.toUpperCase()} RISK</Badge>
              <p className="mt-2 text-xs text-slate-600">{im.risk_reasons.join("; ")}</p>
            </div>
            {[["tests at risk", im.tests.length], ["files to change", change.length], ["dependent files", deps.length]].map(([k, v]) => (
              <div key={k} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="text-2xl font-bold tabular-nums text-slate-900">{v}</div>
                <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">{k}</div>
              </div>
            ))}
          </div>

          <Card title={`Tests at risk, ranked (${im.tests.length} of ${im.tests.length + im.unaffected_tests.length})`}>
            {im.tests.length === 0 ? <p className="text-slate-500">No test reaches a file to change in the code graph.</p> : (
              <div className="max-h-[28rem] overflow-auto">
                <table className="w-full min-w-[640px] text-left text-xs">
                  <thead className="sticky top-0 bg-white text-slate-500"><tr>
                    <th className="py-1.5 pr-2">#</th><th className="py-1.5 pr-2">test</th>
                    <th className="py-1.5 pr-2 text-right">hops</th><th className="py-1.5 pr-2 text-right">score</th><th className="py-1.5">why</th>
                  </tr></thead>
                  <tbody>{im.tests.map((t, i) => (
                    <tr key={t.test_id} className="border-t border-slate-100 align-top">
                      <td className="py-1.5 pr-2 tabular-nums text-slate-500">{i + 1}</td>
                      <td className="py-1.5 pr-2"><Mono>{t.test_id}</Mono></td>
                      <td className="py-1.5 pr-2 text-right tabular-nums">{t.distance}</td>
                      <td className="py-1.5 pr-2 text-right tabular-nums">{t.score.toFixed(2)}</td>
                      <td className="py-1.5 text-slate-600">{t.reasons.join("; ")}</td>
                    </tr>))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          <div className="grid gap-5 md:grid-cols-2">
            <Card title="Files to change">
              <ul className="space-y-1.5">{change.map((f) => (
                <li key={f.path}><Mono>{f.path}</Mono> <span className="text-xs text-slate-500">{f.score.toFixed(2)} · {f.reasons.join("; ")}</span></li>))}
                {change.length === 0 && <li className="text-slate-500">No file matched the story.</li>}
              </ul>
              <h4 className="mb-1 mt-4 text-xs font-semibold uppercase text-slate-500">Dependents</h4>
              <ul className="space-y-1.5">{deps.map((f) => (
                <li key={f.path}><Mono>{f.path}</Mono> <span className="text-xs text-slate-500">{f.reasons.join("; ")}</span></li>))}
                {deps.length === 0 && <li className="text-slate-500">None.</li>}
              </ul>
            </Card>
            <Card title="Code graph and co-change hints">
              <dl>
                <KV k="repository"><Mono>{reply.url}</Mono></KV>
                <KV k="base"><Mono>{im.base_branch} @ {short(im.base_sha)}</Mono></KV>
                <KV k="graph"><span className="tabular-nums">{im.graph_stats.nodes.toLocaleString()} nodes · {im.graph_stats.edges.toLocaleString()} edges · {im.graph_stats.files_parsed} files parsed · {im.graph_stats.parse_failures} parse failures</span></KV>
                <KV k="graphify"><Mono>{short(im.graph_stats.graphify_commit)}</Mono></KV>
              </dl>
              <h4 className="mb-1 mt-3 text-xs font-semibold uppercase text-slate-500">Co-change hints (weak signal)</h4>
              <ul className="space-y-1">{im.cochange_hints.filter((h) => h.partner).map((h, i) => (
                <li key={i} className="text-xs"><Mono>{h.file}</Mono> ↔ <Mono>{h.partner}</Mono> <span className="text-slate-500">{h.count} commits</span></li>))}
                {im.cochange_hints.filter((h) => h.partner).length === 0 && <li className="text-xs text-slate-500">None in the cloned history.</li>}
              </ul>
            </Card>
          </div>

          <Card title="Impact analysis document (impact.md)">
            <div className="max-h-[40rem] overflow-y-auto"><Markdown text={reply.markdown} /></div>
            <p className="mt-3 text-xs text-slate-500">written to <Mono>{reply.clone_dir}/.blastradius/impact/</Mono></p>
          </Card>
        </>
      )}
    </div>
  );
}
