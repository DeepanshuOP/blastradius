/** GET /api/lab/repos: the prepared repositories (files, test files, seeded tasks), recorded runs, whether a model key exists. */
import { PREPARED, fail, isLocal, labJson, recordedRuns } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

let cache: { at: number; body: unknown } | null = null;

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  if (cache && Date.now() - cache.at < 60_000) return Response.json(cache.body);
  const r = await labJson(["repos"], 120_000, true);
  if (r.code !== 0) return fail(500, "The repository listing failed.", r.err.slice(-1500));
  const j = JSON.parse(r.out) as { repos: { name: string }[]; runs: unknown[]; llm: boolean };
  const body = { ok: true, live: true, llm: j.llm, repos: j.repos.filter((x) => PREPARED.includes(x.name)), runs: recordedRuns() };
  cache = { at: Date.now(), body };
  return Response.json(body);
}
