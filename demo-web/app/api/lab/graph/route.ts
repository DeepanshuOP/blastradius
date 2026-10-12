/** GET /api/lab/graph?run=<id>  (the full stored graph of a run)  or  ?repo=<slug>  (a prepared repo's whole graph). */
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { LAB_TMP, PREPARED, RUNS_DIR, fail, isLocal, labJson, safeName } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  const q = new URL(req.url).searchParams;
  const run = q.get("run");
  const repo = q.get("repo");
  if (run) {
    if (!safeName(run)) return fail(400, "Invalid run id.");
    for (const p of [path.join(LAB_TMP, "graphs", `${run}.json`), path.join(RUNS_DIR, `${run}.graph.json`)]) {
      if (existsSync(p)) return new Response(readFileSync(p), { headers: { "Content-Type": "application/json" } });
    }
    return fail(404, "No stored graph for this run.");
  }
  if (repo) {
    if (!PREPARED.includes(repo)) return fail(400, `repo must be one of: ${PREPARED.join(", ")}`);
    const r = await labJson(["graph", "--repo", repo], 180_000);
    if (r.code !== 0) return fail(500, "The graph build failed.", r.err.slice(-1000));
    return new Response(r.out, { headers: { "Content-Type": "application/json" } });
  }
  return fail(400, "Pass run= or repo=.");
}
