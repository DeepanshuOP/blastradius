import BlastRadius from "./BlastRadius";
import GraphPaths from "./GraphPaths";
import type { InstanceDoc } from "./types";
import { Badge, Card, KV, Mono, pct, short } from "./ui";

type S = InstanceDoc["stages"];

export const STAGE_TITLES = [
  "The change",
  "The raw CI log",
  "The parsed outcome",
  "Head run vs base run",
  "The fault-revealing verdict",
  "The bound test file",
  "Graph context at the base commit",
  "Predictors vs what actually failed",
];

function Change({ s }: { s: S["change"] }) {
  const files = s.changed_files;
  return (
    <>
      <dl>
        <KV k="repository"><Mono>{s.repo}</Mono></KV>
        <KV k="pull request">#{s.pr_number} · workflow “{s.workflow_name}” · run <Mono>{s.run_id}</Mono></KV>
        <KV k="head commit"><Mono>{s.head_sha}</Mono></KV>
        <KV k="base commit"><Mono>{s.base_sha}</Mono> <Badge tone="slate">{s.base_status}</Badge></KV>
      </dl>
      <p className="mt-3 text-xs font-medium text-slate-600">{files.length} changed file{files.length === 1 ? "" : "s"}</p>
      <ul className="mt-1 max-h-48 overflow-y-auto rounded border border-slate-100 bg-slate-50 p-2">
        {files.map((f) => (
          <li key={f.path} className="flex justify-between gap-3 py-0.5">
            <Mono>{f.path}</Mono>
            <span className="shrink-0 font-mono text-xs"><span className="text-emerald-700">+{f.additions}</span> <span className="text-red-700">−{f.deletions}</span></span>
          </li>
        ))}
      </ul>
    </>
  );
}

function RawLog({ s }: { s: S["raw_log"] }) {
  return (
    <>
      <p className="mb-2">Job <Mono>{s.job_id}</Mono>: lines naming <Mono>{s.test_name_token}</Mono>; failure lines highlighted.</p>
      <pre className="overflow-x-auto rounded bg-slate-900 p-3 font-mono text-[11.5px] leading-5 text-slate-300">
        {s.lines.map((l, i) => (
          <div key={i} className={l.failing ? "-mx-3 border-l-2 border-red-400 bg-red-500/15 px-3 text-red-200" : ""}>{l.text}</div>
        ))}
      </pre>
    </>
  );
}

function Parsed({ s }: { s: S["parsed_outcome"] }) {
  return (
    <>
      <div className="mb-3 rounded border border-slate-200 bg-slate-50 p-3">
        <p className="text-xs text-slate-500">raw log line</p>
        <Mono className="text-[11.5px]">{s.raw_log_line}</Mono>
        <p className="my-2 text-center text-slate-400">↓ parser ({s.harness}) + canonicaliser</p>
        <p className="text-xs text-slate-500">canonical test_id</p>
        <Mono className="font-semibold">{s.test_id}</Mono>
      </div>
      <dl>
        <KV k="status"><Badge tone="red">{s.status}</Badge></KV>
        <KV k="harness">{s.harness} · parser confidence {s.parser_confidence.toFixed(2)}</KV>
        {s.params && <KV k="params (stripped)"><Mono>{s.params}</Mono></KV>}
        <KV k="failure message"><Mono>{s.failure_message || "(none recorded)"}</Mono></KV>
        <KV k="failure class"><Badge tone={s.failure_class === "code-level" ? "green" : "amber"}>{s.failure_class}</Badge> rule “{s.failure_rule}”</KV>
      </dl>
    </>
  );
}

function HeadBase({ s }: { s: S["head_vs_base"] }) {
  return (
    <>
      <p className="mb-2">
        Base run {s.base_run_id !== null ? <Mono>{s.base_run_id}</Mono> : "not recorded"}
        {s.base_run_distance !== null && <>, {s.base_run_distance} commit(s) from the PR base</>}
        {s.base_run_conclusion && <>, conclusion {s.base_run_conclusion}</>}.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr><th className="py-1 pr-3">test</th><th className="py-1 pr-3">head</th><th className="py-1">base</th></tr>
          </thead>
          <tbody>
            {s.tests.map((t) => (
              <tr key={t.test_id} className="border-t border-slate-100">
                <td className="py-1.5 pr-3"><Mono>{t.test_id}</Mono></td>
                <td className="py-1.5 pr-3"><Badge tone="red">{t.head}</Badge></td>
                <td className="py-1.5"><Badge tone={t.base === "fail" ? "red" : "green"}>{t.base}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function SetBox({ name, items }: { name: string; items: string[] }) {
  return (
    <span className="inline-flex flex-col rounded border border-slate-200 bg-slate-50 px-2 py-1 align-top">
      <span className="text-[11px] font-semibold text-slate-600">{name} = {items.length}</span>
      <span className="font-mono text-[11px] text-slate-500">{items.length ? `{${items.map((x) => x.split(/::|#/).pop()).join(", ")}}` : "∅"}</span>
    </span>
  );
}

function Verdict({ s }: { s: S["verdict"] }) {
  return (
    <>
      <div className="mb-3 flex flex-wrap items-center gap-3">
        {s.selected_is_fault_revealing ? (
          <span className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-bold tracking-wide text-white">FAULT-REVEALING</span>
        ) : (
          <span className="rounded-md bg-slate-500 px-3 py-1.5 text-sm font-bold text-white">NOT FAULT-REVEALING</span>
        )}
        <Mono>{s.selected_test}</Mono>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <SetBox name="T_reveal" items={s.t_reveal} />
        <span>=</span>
        <SetBox name="T_head_fail" items={s.t_head_fail} />
        <span>−</span>
        <SetBox name="T_base_fail" items={s.t_base_fail} />
        <span>−</span>
        <SetBox name="flaky" items={s.flaky} />
      </div>
      <p className="mt-3 text-xs text-slate-500">
        flaky = fails in some but not all of the {s.sibling_runs} run(s) of this workflow on this head commit.
        Agrees with <Mono>outcomes.parquet</Mono> (strict split, {s.recorded_strict} recorded): {s.agrees_with_outcomes_parquet ? "yes" : "no"}.
      </p>
    </>
  );
}

function Binding({ s }: { s: S["binding"] }) {
  return (
    <>
      <p className="mb-2">Each fault-revealing test is bound to a test file at the pinned clone commit (<Mono>{s.pins_file}</Mono>).</p>
      <ul className="space-y-1.5">
        {s.all.map((b) => (
          <li key={b.test_id} className={`rounded border p-2 ${b.test_id === s.selected.test_id ? "border-slate-400" : "border-slate-100"}`}>
            <Mono>{b.test_id}</Mono>
            <div className="mt-0.5 text-slate-600">→ <Mono>{b.resolved_path ?? "(unbound)"}</Mono>{" "}
              <Badge tone={b.status === "exact" ? "green" : "amber"}>{b.status}</Badge>{" "}
              <span className="text-xs text-slate-500">{b.candidates_considered} candidate file(s)</span></div>
          </li>
        ))}
      </ul>
    </>
  );
}

function Graph({ s }: { s: S["graph"] }) {
  const unreachable = s.changed_distances.filter((d) => d.in_graph && d.hops === null).length;
  const absent = s.changed_distances.filter((d) => !d.in_graph).length;
  return (
    <>
      <p className="mb-3">
        Code graph at <Mono>{short(s.graph_commit)}</Mono>: {s.n_nodes.toLocaleString()} nodes, {s.n_edges.toLocaleString()} edges
        {s.built_offline_from_local_git ? " (built offline from local git objects)" : ""}.
      </p>
      {s.blast && (
        <div className="mb-5 rounded-lg border border-slate-100 bg-slate-50/60 p-3">
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Blast radius: the neighbourhood of the change</h4>
          <BlastRadius b={s.blast} />
        </div>
      )}
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Shortest paths: failing test to the {s.paths.length} nearest changed files</h4>
      <GraphPaths paths={s.paths} testLabel={s.test_node?.label ?? "test"} />
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <span className="rounded bg-slate-800 px-3 py-1 font-mono text-sm text-white">
          min_distance_to_any_changed = {s.min_distance_to_any_changed ?? "unreachable"}
        </span>
        <span className="text-xs text-slate-500">
          {s.distance_note}. {unreachable} changed file(s) unreachable, {absent} not in the base graph.
        </span>
      </div>
    </>
  );
}

function Mark({ ok }: { ok: boolean }) {
  return <span aria-label={ok ? "hit" : "miss"} className="shrink-0">{ok ? "✅" : "❌"}</span>;
}

const SHOW = 10;

function Predictions({ s }: { s: S["predictions"] }) {
  const m = s.metrics;
  const n = m.n_actual;
  return (
    <>
      <p className="mb-3 rounded bg-slate-100 px-3 py-2 font-medium text-slate-800">
        History caught {m.history.hits}/{n} failing test file{n === 1 ? "" : "s"}; co-change caught {m.cochange.hits}/{n}.
      </p>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="min-w-0 rounded border border-slate-200 p-3">
          <h4 className="text-xs font-semibold uppercase text-slate-600">Co-change (top {s.k} per changed file)</h4>
          <p className="mb-2 text-xs text-slate-500">P {pct(m.cochange.precision)} · R {pct(m.cochange.recall)} · {m.cochange.predicted} predicted</p>
          <ul className="space-y-1">
            {s.cochange.slice(0, SHOW).map((x) => (
              <li key={x.path} className="flex gap-2"><Mark ok={x.hit} /><Mono className="text-[11px]">{x.path}</Mono></li>
            ))}
            {s.cochange.length > SHOW && <li className="text-xs text-slate-500">… {s.cochange.length - SHOW} more ({s.cochange.slice(SHOW).filter((x) => x.hit).length} hit(s) among them)</li>}
            {!s.cochange.length && <li className="text-xs text-slate-500">silent: no partner before the run started</li>}
          </ul>
        </div>
        <div className="min-w-0 rounded border border-slate-200 p-3">
          <h4 className="text-xs font-semibold uppercase text-slate-600">Historical frequency (top {s.k})</h4>
          <p className="mb-2 text-xs text-slate-500">P {pct(m.history.precision)} · R {pct(m.history.recall)} · {m.history.predicted} predicted</p>
          <ul className="space-y-1">
            {s.history.map((x) => (
              <li key={x.path} className="flex gap-2"><Mark ok={x.hit} /><Mono className="text-[11px]">{x.path}</Mono><span className="ml-auto shrink-0 text-[11px] text-slate-400">×{x.past_failures}</span></li>
            ))}
            {!s.history.length && <li className="text-xs text-slate-500">no earlier failures in this repo</li>}
          </ul>
        </div>
        <div className="min-w-0 rounded border border-red-200 bg-red-50/40 p-3">
          <h4 className="text-xs font-semibold uppercase text-red-700">Actually failed ({n})</h4>
          <p className="mb-2 text-xs text-slate-500">bound test files of the strict labels</p>
          <ul className="space-y-1.5">
            {s.actual.map((x) => (
              <li key={x.path}>
                <Mono className="text-[11px]">{x.path}</Mono>
                <div className="text-[11px] text-slate-500">co-change <Mark ok={x.caught_by_cochange} /> · history <Mark ok={x.caught_by_history} /></div>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <p className="mt-3 text-xs text-slate-500">
        Leakage-free: co-change uses only commits before the run started ({s.run_started_at}); history uses only strict labels of earlier runs. Same logic as <Mono>analysis/rq1_divergence.py</Mono>.
      </p>
    </>
  );
}

export function StageCard({ i, doc }: { i: number; doc: InstanceDoc }) {
  const s = doc.stages;
  const body = [
    <Change key={0} s={s.change} />,
    <RawLog key={1} s={s.raw_log} />,
    <Parsed key={2} s={s.parsed_outcome} />,
    <HeadBase key={3} s={s.head_vs_base} />,
    <Verdict key={4} s={s.verdict} />,
    <Binding key={5} s={s.binding} />,
    <Graph key={6} s={s.graph} />,
    <Predictions key={7} s={s.predictions} />,
  ][i];
  return <Card step={i + 1} title={STAGE_TITLES[i]} className="animate-[fadein_.35s_ease-out]">{body}</Card>;
}
