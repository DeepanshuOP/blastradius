"use client";

import { useEffect, useMemo, useState } from "react";
import { Empty, Panel, Prov } from "./common";
import { SideBySide, changedLines } from "./Diff";

export interface RepoInfo {
  name: string; url: string; commit: string; language: string; n_files: number; test_files: number; n_tests: number | null; runnable: boolean;
  tasks: { task_id: string; repo: string; operator: string; variant: "standard" | "hard"; gt_file: string; gt_function: string; n_decoys: number }[];
}
export interface RunInfo { name: string; date?: string; model?: string | null; git_sha?: string; title?: string; description?: string }
export type Mutation = { operator: string; line: number; col: number; old: string; new: string };
export type FnMut = { function: string; mutations: Mutation[] };

export type Scenario = { kind: "repo"; name: string } | { kind: "github"; url: string } | { kind: "replay"; name: string } | null;
export type Change =
  | { kind: "inject"; file: string; function: string; operator: string; line: number | null }
  | { kind: "edit"; file: string; text: string }
  | { kind: "task"; id: string; variant: "standard" | "hard" }
  | null;

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

export function Picker({ repos, runs, live, reason, scenario, setScenario, change, setChange, disabled }: {
  repos: RepoInfo[] | null; runs: RunInfo[]; live: boolean; reason: string; scenario: Scenario; setScenario: (s: Scenario) => void;
  change: Change; setChange: (c: Change) => void; disabled: boolean;
}) {
  const [url, setUrl] = useState("");
  const repo = scenario?.kind === "repo" ? repos?.find((r) => r.name === scenario.name) ?? null : null;
  return (
    <Panel id="panel-picker" title="Scenario" right={<Prov mode="idle" />}>
      {!live && <p className="ui m-0 mb-3 rounded border border-amber px-3 py-2 text-sm text-amber" role="status">Live runs are unavailable: {reason} Recorded runs replay in the browser.</p>}
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        {(repos ?? []).map((r) => (
          <button key={r.name} type="button" disabled={disabled || !live} onClick={() => { setScenario({ kind: "repo", name: r.name }); setChange(null); }}
            aria-pressed={scenario?.kind === "repo" && scenario.name === r.name}
            className={`rounded border px-3 py-2 text-left disabled:opacity-40 ${scenario?.kind === "repo" && scenario.name === r.name ? "border-accent bg-accent/10" : "border-rule bg-page hover:border-muted"}`}>
            <span className="ui block text-base font-semibold">{r.name}</span>
            <span className="mono block text-xs text-muted">{r.n_files} files · {r.n_tests ?? "?"} tests · {r.commit.slice(0, 7)}</span>
            <span className="ui block text-xs text-muted">prepared · {r.runnable ? "tests runnable" : "no interpreter"}</span>
          </button>
        ))}
        {repos === null && live && <Empty>Loading repositories.</Empty>}
      </div>
      <div className="mt-3 grid gap-3 lg:grid-cols-2">
        <div className={`rounded border px-3 py-2 ${scenario?.kind === "github" ? "border-accent bg-accent/10" : "border-rule bg-page"}`}>
          <label className="ui block text-sm font-semibold" htmlFor="gh-url">Any public GitHub repo</label>
          <div className="mt-1 flex gap-2">
            <input id="gh-url" type="url" value={url} placeholder="https://github.com/owner/repo" disabled={disabled || !live}
              onChange={(e) => { setUrl(e.target.value); setScenario(e.target.value.trim() ? { kind: "github", url: e.target.value.trim() } : null); setChange(null); }}
              className="mono min-w-0 flex-1 px-2 py-1 text-sm disabled:opacity-40" />
          </div>
          <p className="ui m-0 mt-1 text-xs text-muted">Shallow clone, then <span className="mono">uv pip install -e .</span> (180 s cap). If it cannot be installed the run still ranks and graphs it, and says why tests did not run.</p>
          <p className="ui m-0 mt-1 text-xs text-muted">Tested here:{" "}
            {TESTED_EXAMPLES.map((x, i) => (
              <span key={x.url}>{i ? " · " : ""}<button type="button" disabled={disabled || !live} className="mono text-blue underline disabled:opacity-40" title={x.note}
                onClick={() => { setUrl(x.url); setScenario({ kind: "github", url: x.url }); setChange(null); }}>{x.url.replace("https://github.com/", "")}</button></span>
            ))}
          </p>
        </div>
        <div className="rounded border border-rule bg-page px-3 py-2">
          <span className="ui block text-sm font-semibold">Recorded scenarios (replay)</span>
          <div className="mt-1 flex flex-wrap gap-2">
            {runs.length === 0 && <span className="ui text-xs text-muted">None recorded yet.</span>}
            {runs.map((r) => (
              <button key={r.name} type="button" disabled={disabled} title={r.description} onClick={() => { setScenario({ kind: "replay", name: r.name }); setChange(null); }}
                aria-pressed={scenario?.kind === "replay" && scenario.name === r.name}
                className={`ui rounded border px-2 py-1 text-left text-xs ${scenario?.kind === "replay" && scenario.name === r.name ? "border-amber bg-amber/10" : "border-rule hover:border-muted"}`}>
                <span className="block font-medium">{r.title ?? r.name}</span>
                <span className="mono block text-2xs text-muted">{(r.date ?? "").slice(0, 10)} · {r.model ?? "no model"}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      {(scenario?.kind === "repo" || scenario?.kind === "github") && (
        <ChangePicker scenario={scenario} repo={repo} change={change} setChange={setChange} disabled={disabled} />
      )}
      {scenario?.kind === "replay" && (
        <p className="ui m-0 mt-3 text-sm text-muted">This replays a recording of a real run, event by event, with its original timing. Nothing is computed in this session.</p>
      )}
    </Panel>
  );
}

function ChangePicker({ scenario, repo, change, setChange, disabled }: {
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
              <p className="ui m-0 mt-1 text-xs text-muted">Highlighted lines differ from the file at the base commit. The whole new file is sent to the lab, committed in a scratch worktree, and every later stage runs on it.</p>
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
      <p className="ui m-0 text-xs text-muted sm:col-span-4">For a repository that is not prepared the lab applies the operator to that function after cloning, and fails with the list of what is available if there is none.{change?.kind === "inject" ? "" : ""}</p>
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
