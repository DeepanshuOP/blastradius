/**
 * GET  /api/lab/history?repo=   -> how many earlier runs the arena's failure-history store holds for a repository.
 * POST /api/lab/history {repo}  -> forgets them (the "Reset history" button). Refused while a run is active.
 * The store is the lab's own scratch file under the OS temp directory; nothing under data/ is touched.
 */
import { PREPARED, fail, isLocal, labJson, lock } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const KEY = /^[\w.-]{1,80}(__[\w.-]{1,80})?$/;
const known = (r: string) => PREPARED.includes(r) || (KEY.test(r) && r.includes("__"));

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  const repo = new URL(req.url).searchParams.get("repo") ?? "";
  if (!known(repo)) return fail(400, "repo must be a prepared repository or owner__repo");
  const r = await labJson(["history", "--repo", repo], 30_000);
  if (r.code !== 0) return fail(500, "Reading the history failed.", r.err.slice(-500));
  return Response.json({ ok: true, ...JSON.parse(r.out) });
}

export async function POST(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  let b: { repo?: string };
  try { b = await req.json(); } catch { return fail(400, "Body must be JSON."); }
  const repo = b.repo ?? "";
  if (!known(repo)) return fail(400, "repo must be a prepared repository or owner__repo");
  if (lock().busy) return fail(409, "A lab run is active; reset the history when it ends.");
  const r = await labJson(["history", "--repo", repo, "--reset"], 30_000);
  if (r.code !== 0) return fail(500, "Resetting the history failed.", r.err.slice(-500));
  return Response.json({ ok: true, ...JSON.parse(r.out) });
}
