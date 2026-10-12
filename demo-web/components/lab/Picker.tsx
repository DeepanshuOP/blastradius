"use client";

import { useEffect, useMemo, useState } from "react";
import { Empty, Icon } from "./common";
import { Explain, Info } from "./Info";
import { SideBySide, changedLines } from "./Diff";

export interface RepoInfo {
  name: string; url: string; commit: string; language: string; n_files: number; test_files: number; n_tests: number | null; runnable: boolean;
  tasks: { task_id: string; repo: string; operator: string; variant: "standard" | "hard"; gt_file: string; gt_function: string; n_decoys: number }[];
}
export interface RunInfo { name: string; date?: string; model?: string | null; git_sha?: string; title?: string; description?: string }
export type Mutation = { operator: string; line: number; col: number; old: string; new: string };
export type FnMut = { function: string; mutations: Mutation[]; start?: number; end?: number; def_line?: number };

export type Scenario = { kind: "repo"; name: string } | { kind: "github"; url: string } | { kind: "pr"; url: string } | { kind: "replay"; name: string } | null;
export type Change =
  | { kind: "inject"; file: string; function: string; operator: string; line: number | null }
  | { kind: "edit"; file: string; text: string }
  | { kind: "task"; id: string; variant: "standard" | "hard" }
  | null;

export const PR_RE = /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/pull\/\d+\/?$/;
export const TESTED_PRS: { url: string; note: string }[] = [
  { url: "https://github.com/tkem/cachetools/pull/424", note: "merged 2026-09-27; verified here 2026-10-12: 353 tests, about 28 s end to end" },
];

export const TESTED_EXAMPLES = [
  { url: "https://github.com/tkem/cachetools", note: "338 tests, installs in about 1 s" },
  { url: "https://github.com/pytoolz/toolz", note: "193 tests, installs in about 1 s" },
];

const SKIP = /(^|\/)(tests?|docs?|examples?|benchmarks?)\//;

export function applyMutation(text: string, m: Mutation): string {
  const lines = text.split("\n");
  const l = lines[m.line - 1] ?? "";
  lines[m.line - 1] = l.slice(0, m.col) + m.new + l.slice(m.col + m.old.length);
  return lines.join("\n");
}

/** A text view with changed lines highlighted that the reader can edit (textarea over a mirrored, highlighted <pre>). */
export function EditableCode({ original, value, onChange }: { original: string; value: string; onChange: (v: string) => void }) {
  const changed = useMemo(() => changedLines(original, value), [original, value]);
  const lines = value.split("\n");
  return (
    <div className="relative h-72 overflow-hidden rounded border border-rule bg-page">
      <pre aria-hidden="true" id="edit-mirror" className="mono pointer-events-none absolute inset-0 m-0 overflow-hidden py-2 text-xs leading-[1.55]">
        {lines.map((l, i) => (
          <div key={i} className={`flex ${changed.has(i + 1) ? "bg-accent/20" : ""}`}>
            <span className="w-10 shrink-0 select-none pr-2 text-right text-muted">{i + 1}</span>
            <span className="whitespace-pre text-transparent">{l || " "}</span>
          </div>
        ))}
      </pre>
      <textarea value={value} onChange={(e) => onChange(e.target.value)} spellCheck={false} wrap="off" aria-label="Edit the file"
        onScroll={(e) => { const m = document.getElementById("edit-mirror"); if (m) { m.scrollTop = e.currentTarget.scrollTop; m.scrollLeft = e.currentTarget.scrollLeft; } }}
        className="mono absolute inset-0 h-full w-full resize-none border-0 bg-transparent py-2 pl-12 pr-2 text-xs leading-[1.55] outline-none" style={{ whiteSpace: "pre", overflow: "auto" }} />
    </div>
  );
}

/** A two-letter mark for a repository card; the colour comes from the name, so a card keeps its look. */
export function monogram(name: string): { text: string; tone: string } {
  const tones = ["bg-blue/20 text-blue", "bg-accent/20 text-accent", "bg-green/20 text-green", "bg-amber/20 text-amber"];
  const h = Array.from(name).reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);
  return { text: name.replace(/[^A-Za-z0-9]/g, "").slice(0, 2).toUpperCase() || "?", tone: tones[h % tones.length] };
}

const LANG: Record<string, string> = { python: "Python", java: "Java" };

/** Step 1: one card per prepared repository (monogram, language chip, file and test counts) and a GitHub URL card. */
export function RepoCards({ repos, live, disabled, scenario, setScenario, setChange }: {
  repos: RepoInfo[] | null; live: boolean; disabled: boolean; scenario: Scenario; setScenario: (s: Scenario) => void; setChange: (c: Change) => void;
}) {
  const [url, setUrl] = useState("");
  const pick = (sc: Scenario, u = "") => { setUrl(u); setScenario(sc); setChange(null); };
  const gh = scenario?.kind === "github" || scenario?.kind === "pr";
  return (
    <div className="space-y-2">
      <ul className="m-0 grid list-none gap-2 p-0 sm:grid-cols-2 lg:grid-cols-1">
        {(repos ?? []).map((r) => {
          const on = scenario?.kind === "repo" && scenario.name === r.name;
          const m = monogram(r.name);
          return (
            <li key={r.name}>
              <button type="button" disabled={disabled || !live} onClick={() => pick({ kind: "repo", name: r.name })} aria-pressed={on}
                className={`flex w-full items-center gap-2.5 rounded-md border p-2 text-left disabled:opacity-40 ${on ? "border-accent bg-accent/10" : "border-rule bg-page hover:border-muted"}`}>
                <span className={`ui grid h-10 w-10 shrink-0 place-items-center rounded-md text-md font-bold ${m.tone}`} aria-hidden="true">{m.text}</span>
                <span className="min-w-0 flex-1">
                  <span className="ui flex flex-wrap items-center gap-x-1.5 text-base font-semibold">{r.name}<span className="ui rounded bg-panel2 px-1.5 text-2xs font-medium text-muted">{LANG[r.language] ?? r.language}</span></span>
                  <span className="num mono block truncate text-xs text-muted">{r.n_files} files · {r.n_tests ?? "?"} tests</span>
                </span>
              </button>
            </li>
          );
        })}
        {repos === null && live && <li className="ui text-sm text-muted">Loading…</li>}
      </ul>
      <div className={`rounded-md border p-2 ${gh ? "border-accent bg-accent/10" : "border-rule bg-page"}`}>
        <div className="flex items-center gap-2">
          <span className="ui grid h-10 w-10 shrink-0 place-items-center rounded-md bg-panel2 text-xs font-bold text-muted" aria-hidden="true">GH</span>
          <div className="min-w-0 flex-1">
            <label className="ui flex items-center gap-1.5 text-sm font-semibold" htmlFor="gh-url">GitHub URL
              <Info label="About GitHub URLs">
                <span className="block">Any public repository, or a pull request URL.</span>
                <span className="mt-1 block">Shallow clone, then <span className="mono">uv pip install -e .</span> with a 180 s cap. If it cannot be installed the run still graphs and ranks it, and says why tests did not run.</span>
              </Info>
            </label>
            <input id="gh-url" type="url" value={url} placeholder="github.com/owner/repo or …/pull/1" disabled={disabled || !live}
              onChange={(e) => { const v = e.target.value.trim(); pick(!v ? null : PR_RE.test(v) ? { kind: "pr", url: v } : { kind: "github", url: v }, e.target.value); }}
              className="mono mt-0.5 w-full min-w-0 px-2 py-1 text-xs disabled:opacity-40" />
          </div>
        </div>
        <div className="mt-1.5 flex flex-wrap gap-1.5" aria-label="Tested examples">
          {TESTED_EXAMPLES.map((x) => (
            <button key={x.url} type="button" disabled={disabled || !live} title={x.note} onClick={() => pick({ kind: "github", url: x.url }, x.url)}
              className="mono rounded-full border border-rule px-2 py-0.5 text-2xs text-muted hover:text-ink disabled:opacity-40">{x.url.replace("https://github.com/", "")}</button>
          ))}
          {TESTED_PRS.map((x) => (
            <button key={x.url} type="button" disabled={disabled || !live} title={x.note} onClick={() => pick({ kind: "pr", url: x.url }, x.url)}
              className="mono rounded-full border border-rule px-2 py-0.5 text-2xs text-muted hover:text-ink disabled:opacity-40">{x.url.replace("https://github.com/", "").replace("/pull/", " #")}</button>
          ))}
        </div>
      </div>
    </div>
  );
}

/** Recorded scenarios as small chips; pressing one replays it. */
export function ReplayChips({ runs, disabled, onReplay }: { runs: RunInfo[]; disabled: boolean; onReplay: (name: string) => void }) {
  if (runs.length === 0) return null;
  return (
    <ul className="m-0 flex list-none flex-wrap gap-1.5 p-0" aria-label="Recorded scenarios">
      {runs.map((r) => (
        <li key={r.name}>
          <button type="button" disabled={disabled} onClick={() => onReplay(r.name)} title={`${r.title ?? r.name}${r.description ? `: ${r.description}` : ""}`}
            className="ui inline-flex items-center gap-1 rounded-full border border-amber/60 px-2 py-0.5 text-2xs text-amber hover:bg-amber/10 disabled:opacity-40">
            <Icon name="play" className="text-2xs" />Replay<span className="text-muted">·</span><span className="max-w-[9rem] truncate text-ink">{(r.title ?? r.name).replace(/:.*$/, "")}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}

export function ChangePicker({ scenario, repo, change, setChange, disabled }: {
  scenario: NonNullable<Scenario>; repo: RepoInfo | null; change: Change; setChange: (c: Change) => void; disabled: boolean;
}) {
  const prepared = scenario.kind === "repo" && repo;
  const [tab, setTab] = useState<"inject" | "edit" | "task">(prepared ? "inject" : "inject");
  const [files, setFiles] = useState<string[]>([]);
  const [file, setFile] = useState("");
  const [text, setText] = useState<string | null>(null);
  const [fns, setFns] = useState<FnMut[]>([]);
  const [edited, setEdited] = useState("");
  const [loadErr, setLoadErr] = useState("");
  const name = scenario.kind === "repo" ? scenario.name : "";

  useEffect(() => {
    setFiles([]); setFile(""); setText(null); setFns([]);
    if (!prepared) return;
    let alive = true;
    fetch(`/api/lab/file?repo=${name}&tree=1`).then((r) => r.json()).then((j: { files: string[] }) => {
      if (!alive) return;
      const src = j.files.filter((f) => !SKIP.test(f) && !/(^|\/)(conftest|setup)\.py$/.test(f) && !/test_[^/]*\.py$/.test(f));
      setFiles(src.length ? src : j.files);
    }).catch(() => alive && setLoadErr("could not list files"));
    return () => { alive = false; };
  }, [name, prepared]);

  useEffect(() => {
    setText(null); setFns([]); setLoadErr("");
    if (!file || !prepared) return;
    let alive = true;
    fetch(`/api/lab/file?repo=${name}&path=${encodeURIComponent(file)}`).then((r) => r.json()).then((j: { text: string }) => { if (alive) { setText(j.text); setEdited(j.text); } });
    fetch(`/api/lab/mutations?repo=${name}&file=${encodeURIComponent(file)}`).then((r) => r.json()).then((j: { functions: FnMut[] }) => { if (alive) setFns(j.functions ?? []); }).catch(() => alive && setLoadErr("could not list mutations"));
    return () => { alive = false; };
  }, [file, name, prepared]);

  const sel = change?.kind === "inject" ? change : null;
  const mutation = sel ? fns.find((f) => f.function === sel.function)?.mutations.find((m) => m.operator === sel.operator && m.line === sel.line) : undefined;
  const mutated = text !== null && mutation ? applyMutation(text, mutation) : null;

  return (
    <div className="mt-4 border-t border-rule pt-3">
      <div className="mb-2 flex items-center gap-2">
        <h4 className="ui m-0 text-sm font-semibold">The change</h4>
        {(["inject", "edit", ...(prepared ? ["task"] : [])] as ("inject" | "edit" | "task")[]).map((t) => (
          <button key={t} type="button" disabled={disabled} onClick={() => { setTab(t); setChange(null); }} aria-pressed={tab === t}
            className={`ui rounded px-2 py-0.5 text-sm ${tab === t ? "bg-ink text-page" : "border border-rule text-muted hover:text-ink"}`}>
            {t === "inject" ? "Inject a bug" : t === "edit" ? "Edit code yourself" : "Use a seeded task"}
          </button>
        ))}
      </div>
      {loadErr && <p className="ui m-0 text-xs text-red">{loadErr}</p>}

      {tab === "inject" && prepared && (
        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
          <div>
            <label className="ui block text-xs text-muted" htmlFor="inj-file">File</label>
            <select id="inj-file" value={file} onChange={(e) => { setFile(e.target.value); setChange(null); }} className="mono w-full px-2 py-1 text-xs">
              <option value="">choose a source file</option>
              {files.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
            <div className="mt-2 max-h-56 overflow-y-auto rounded border border-rule bg-page">
              {file && fns.length === 0 && text !== null && <p className="ui m-0 p-2 text-xs text-muted">No mutation applies in this file.</p>}
              {fns.map((f) => (
                <div key={f.function} className="border-b border-rule px-2 py-1 last:border-0">
                  <div className="mono text-xs">{f.function}</div>
                  <div className="mt-0.5 flex flex-wrap gap-1">
                    {f.mutations.map((m) => {
                      const on = sel?.function === f.function && sel.operator === m.operator && sel.line === m.line;
                      return (
                        <button key={`${m.operator}${m.line}${m.col}`} type="button" disabled={disabled} onClick={() => setChange({ kind: "inject", file, function: f.function, operator: m.operator, line: m.line })}
                          className={`mono rounded border px-1.5 py-0.5 text-2xs ${on ? "border-accent bg-accent/15" : "border-rule text-muted hover:text-ink"}`}
                          title={`line ${m.line}: ${m.old} → ${m.new}`}>{m.operator} L{m.line}</button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <span className="ui block text-xs text-muted">Preview of the diff</span>
            {text !== null && mutated !== null ? <SideBySide path={file} before={text} after={mutated} /> : <Empty>Choose a function and an operator to preview the change.</Empty>}
          </div>
        </div>
      )}

      {tab === "inject" && !prepared && <GithubInject change={change} setChange={setChange} disabled={disabled} />}

      {tab === "edit" && (
        <div>
          {prepared ? (
            <>
              <label className="ui block text-xs text-muted" htmlFor="edit-file">File</label>
              <select id="edit-file" value={file} onChange={(e) => { setFile(e.target.value); setChange(null); }} className="mono mb-2 w-full px-2 py-1 text-xs sm:w-96">
                <option value="">choose a source file</option>
                {files.map((f) => <option key={f} value={f}>{f}</option>)}
              </select>
            </>
          ) : (
            <GithubEdit setChange={setChange} disabled={disabled} />
          )}
          {prepared && text !== null && (
            <>
              <EditableCode original={text} value={edited} onChange={(v) => { setEdited(v); setChange(v === text ? null : { kind: "edit", file, text: v }); }} />
              <Explain>Highlighted lines differ from the file at the base commit. The whole new file is sent to the lab, committed in a scratch worktree, and every later stage runs on it.</Explain>
            </>
          )}
        </div>
      )}

      {tab === "task" && prepared && repo && (
        <div className="max-h-56 overflow-y-auto rounded border border-rule bg-page">
          {repo.tasks.map((t) => {
            const on = change?.kind === "task" && change.id === t.task_id && change.variant === t.variant;
            return (
              <button key={`${t.variant}-${t.task_id}`} type="button" disabled={disabled} onClick={() => setChange({ kind: "task", id: t.task_id, variant: t.variant })}
                className={`flex w-full items-baseline gap-3 border-b border-rule px-2 py-1 text-left last:border-0 ${on ? "bg-accent/15" : "hover:bg-panel2"}`}>
                <span className="mono text-xs">{t.task_id}</span>
                <span className="ui text-xs text-muted">{t.variant} · {t.operator} in {t.gt_function} · {t.n_decoys} {t.variant === "hard" ? "decoy edits" : "harmless edits"}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function GithubInject({ change, setChange, disabled }: { change: Change; setChange: (c: Change) => void; disabled: boolean }) {
  const [f, setF] = useState(""); const [fn, setFn] = useState(""); const [op, setOp] = useState("CMP_FLIP"); const [ln, setLn] = useState("");
  const push = (a = f, b = fn, c = op, d = ln) => setChange(a && b ? { kind: "inject", file: a, function: b, operator: c, line: d ? Number(d) : null } : null);
  return (
    <div className="grid gap-2 sm:grid-cols-4">
      <input type="text" value={f} disabled={disabled} placeholder="src/pkg/module.py" aria-label="File" onChange={(e) => { setF(e.target.value); push(e.target.value); }} className="mono px-2 py-1 text-xs" />
      <input type="text" value={fn} disabled={disabled} placeholder="Class.method" aria-label="Function" onChange={(e) => { setFn(e.target.value); push(f, e.target.value); }} className="mono px-2 py-1 text-xs" />
      <select value={op} disabled={disabled} aria-label="Operator" onChange={(e) => { setOp(e.target.value); push(f, fn, e.target.value); }} className="mono px-2 py-1 text-xs">
        {["CMP_FLIP", "ARITH_SWAP", "NEGATE_COND", "OFF_BY_ONE", "BOOL_RETURN"].map((o) => <option key={o}>{o}</option>)}
      </select>
      <input type="text" value={ln} disabled={disabled} placeholder="line (optional)" aria-label="Line" onChange={(e) => { setLn(e.target.value); push(f, fn, op, e.target.value); }} className="mono px-2 py-1 text-xs" />
      <Explain className="sm:col-span-4">For a repository that is not prepared the lab applies the operator to that function after cloning, and fails with the list of what is available if there is none.</Explain>
    </div>
  );
}

function GithubEdit({ setChange, disabled }: { setChange: (c: Change) => void; disabled: boolean }) {
  const [f, setF] = useState(""); const [t, setT] = useState("");
  return (
    <div className="grid gap-2">
      <input type="text" value={f} disabled={disabled} placeholder="path/in/repo.py" aria-label="File" onChange={(e) => { setF(e.target.value); setChange(e.target.value && t ? { kind: "edit", file: e.target.value, text: t } : null); }} className="mono px-2 py-1 text-xs sm:w-96" />
      <textarea value={t} disabled={disabled} rows={8} placeholder="The complete new text of that file" aria-label="New file text" onChange={(e) => { setT(e.target.value); setChange(f && e.target.value ? { kind: "edit", file: f, text: e.target.value } : null); }} className="mono px-2 py-1 text-xs" />
    </div>
  );
}
