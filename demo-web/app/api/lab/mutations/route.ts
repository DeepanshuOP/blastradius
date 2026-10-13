/** GET /api/lab/mutations?repo=&file=: functions of a file and the mutation operators that apply to each. */
import { PREPARED, fail, isLocal, labJson, labParse, safePath } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  const q = new URL(req.url).searchParams;
  const repo = q.get("repo") ?? "";
  const file = q.get("file") ?? "";
  if (!PREPARED.includes(repo)) return fail(400, `repo must be one of: ${PREPARED.join(", ")}`);
  if (!safePath(file) || !file.endsWith(".py")) return fail(400, "file must be a repository-relative .py path");
  const r = await labJson(["mutations", "--repo", repo, "--file", file], 60_000);
  if (r.code !== 0) return fail(500, "Listing mutations failed.", r.err.slice(-1000));
  return Response.json({ ok: true, repo, ...labParse(r, "mutations") });
}
