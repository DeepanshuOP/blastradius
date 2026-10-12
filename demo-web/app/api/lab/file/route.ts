/** GET /api/lab/file?repo=&path=  (source text)  or  ?repo=&tree=1  (tracked .py files), for the code viewer. */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { PREPARED, SEEDED, fail, isLocal, safePath } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const SKIP = new Set([".git", "__pycache__", "node_modules", ".pytest_cache", "build", "dist"]);

function tree(dir: string, rel = "", depth = 0, out: string[] = []): string[] {
  if (depth > 6 || out.length > 800) return out;
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(e.name) || e.name.startsWith(".") || e.name.endsWith(".egg-info")) continue;
    const p = path.join(dir, e.name);
    const r = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) tree(p, r, depth + 1, out);
    else if (e.name.endsWith(".py")) out.push(r);
  }
  return out;
}

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  const q = new URL(req.url).searchParams;
  const repo = q.get("repo") ?? "";
  if (!PREPARED.includes(repo)) return fail(400, `repo must be one of: ${PREPARED.join(", ")}`);
  const root = path.join(SEEDED, repo);
  if (!existsSync(root)) return fail(404, "The repository is not prepared on this machine (make seeded).");
  if (q.get("tree")) return Response.json({ ok: true, repo, files: tree(root).sort() });
  const rel = q.get("path") ?? "";
  if (!safePath(rel)) return fail(400, "Invalid path.");
  const p = path.join(root, rel);
  if (!p.startsWith(root + path.sep) || !existsSync(p) || !statSync(p).isFile()) return fail(404, "No such file.");
  if (statSync(p).size > 400_000) return fail(413, "File too large for the viewer.");
  return Response.json({ ok: true, repo, path: rel, text: readFileSync(p, "utf-8") });
}
