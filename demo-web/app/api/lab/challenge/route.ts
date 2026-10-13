/**
 * GET /api/lab/challenge?repo=&seed=  -> the function and mutation operator a seed chooses in a prepared repository
 * (`python -m src.lab challenge`): a pure function of (repository text, seed). No repository code runs and no model is
 * called. Without `seed` the route draws one and returns it, so the reviewer sees which seed made the choice.
 */
import { randomInt } from "node:crypto";
import { PREPARED, fail, isLocal, labJson, labParse } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const SEED_MAX = 2 ** 31 - 1;

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  const q = new URL(req.url).searchParams;
  const repo = q.get("repo") ?? "";
  if (!PREPARED.includes(repo)) return fail(400, `repo must be one of: ${PREPARED.join(", ")}`);
  const raw = q.get("seed");
  let seed: number;
  if (raw === null || raw === "") seed = randomInt(0, SEED_MAX);
  else {
    seed = Number(raw);
    if (!Number.isInteger(seed) || seed < 0 || seed > SEED_MAX) return fail(400, `seed must be an integer from 0 to ${SEED_MAX}`);
  }
  const r = await labJson(["challenge", "--repo", repo, "--seed", String(seed)], 60_000);
  if (r.code !== 0) return fail(500, "Choosing the bug failed.", (r.err || r.out).slice(-600));
  return Response.json({ ok: true, ...labParse(r, "challenge") });
}
