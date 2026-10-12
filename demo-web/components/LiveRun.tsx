"use client";

import { useEffect, useRef, useState } from "react";
import { STAGE_TITLES, StageCard } from "./Stages";
import type { IndexDoc, InstanceDoc } from "./types";
import { Mono, short } from "./ui";

const STEP_MS = 800;

async function getJson<T>(path: string): Promise<T> {
  const r = await fetch(path, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return (await r.json()) as T;
}

/** Replays one recorded pipeline run stage by stage. Nothing here is computed in the browser. */
export default function LiveRun({ index }: { index: IndexDoc }) {
  const [id, setId] = useState(index.default);
  const [doc, setDoc] = useState<InstanceDoc | null>(null);
  const [shown, setShown] = useState(0);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => () => { if (timer.current) clearInterval(timer.current); }, []);
  const stop = () => { if (timer.current) clearInterval(timer.current); timer.current = null; };

  const run = async () => {
    stop(); setShown(0); setErr(null); setRunning(true);
    try {
      const d = doc && doc.id === id ? doc : await getJson<InstanceDoc>(`/data/instances/${id}.json`);
      setDoc(d);
      let n = 0;
      timer.current = setInterval(() => {
        n += 1; setShown(n);
        if (n >= STAGE_TITLES.length) { stop(); setRunning(false); }
      }, STEP_MS);
    } catch (e) { setErr(String(e)); setRunning(false); }
  };

  const total = STAGE_TITLES.length;
  return (
    <div className="space-y-4">
      <p className="ui m-0 border border-rule bg-panel px-4 py-3 text-[15px]">
        Replaying a recorded run computed by <Mono>analysis/export_demo_data.py</Mono> at <Mono>{short(index.generated_at_git_sha)}</Mono>.
        The same pipeline runs live with <Mono>make demo</Mono>.
      </p>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="ui flex-1 text-[15px]">
          <span className="mb-1 block text-[13px] font-medium text-muted">Instance</span>
          <select value={id} disabled={running}
            onChange={(e) => { stop(); setId(e.target.value); setShown(0); setDoc(null); }}
            className="w-full border border-rule bg-panel px-3 py-2 text-[15px]">
            {index.instances.map((x) => (
              <option key={x.id} value={x.id}>
                {x.repo}, PR {x.pr_number}, run {x.run_id}, {x.failure_class}, {x.test_count} fault-revealing test{x.test_count === 1 ? "" : "s"}
              </option>
            ))}
          </select>
        </label>
        <button onClick={run} disabled={running}
          className="ui bg-accent px-5 py-2 text-[15px] font-semibold text-white hover:bg-sky-800 disabled:cursor-not-allowed disabled:bg-muted">
          {running ? "Replaying" : shown >= total ? "Replay again" : "Replay run"}
        </button>
      </div>
      {index.instances.length === 1 && (
        <p className="cap m-0">
          One instance qualified: it must clear every gate (strict label, bound test, no holdout job, raw log on disk) and have a graph buildable offline from local git objects.
        </p>
      )}
      {err && <p className="text-fail">{err}</p>}
      {(running || shown > 0) && (
        <div>
          <p className="ui m-0 mb-1 text-[14px] text-muted">
            {shown < total ? `Stage ${Math.min(shown + 1, total)} of ${total}: ${STAGE_TITLES[Math.min(shown, total - 1)]}` : "All stages complete"}
          </p>
          <div className="h-1.5 w-full bg-rule" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={shown}>
            <div className="h-full bg-accent" style={{ width: `${(shown / total) * 100}%` }} />
          </div>
        </div>
      )}
      <div className="space-y-6">
        {doc && Array.from({ length: shown }, (_, i) => <StageCard key={`${doc.id}-${i}`} i={i} doc={doc} />)}
      </div>
    </div>
  );
}
