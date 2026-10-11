/**
 * POST /api/ask: run `python -m src.agents ask` on one of the seeded repositories (exploratory RAG assistant).
 * Local use only: requests whose Host is not localhost are refused, and the npm scripts bind the server to
 * 127.0.0.1. The repository must be one of data/seeded/repos (a whitelist, never a path from the browser).
 * Needs GROQ_API_KEY in the server's environment and network access; without them GET reports
 * `live: false` and the page shows the recorded answers instead. At most one question runs at a time.
 */
import { execFile } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import path from "node:path";
import { promisify } from "node:util";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const run = promisify(execFile);
const REPO_ROOT = path.resolve(process.cwd(), "..");
const SEEDED = path.join(REPO_ROOT, "data", "seeded", "repos");
const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);
let busy = false;

function isLocal(req: Request): boolean {
  const host = (req.headers.get("host") ?? "").replace(/:\d+$/, "");
  const fwd = (req.headers.get("x-forwarded-for") ?? "").split(",").map((x) => x.trim()).filter(Boolean);
  return LOCAL_HOSTS.has(host) && fwd.every((ip) => ["127.0.0.1", "::1", "::ffff:127.0.0.1"].includes(ip));
}

const fail = (status: number, error: string, detail?: string) => Response.json({ ok: false, error, detail }, { status });

function repos(): string[] {
  return existsSync(SEEDED) ? readdirSync(SEEDED).filter((d) => existsSync(path.join(SEEDED, d, ".git"))).sort() : [];
}

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The assistant only serves localhost.");
  return Response.json({ ok: true, live: Boolean(process.env.GROQ_API_KEY) && repos().length > 0, repos: repos() });
}

export async function POST(req: Request) {
  if (!isLocal(req)) return fail(403, "The assistant only serves localhost.");
  if (!process.env.GROQ_API_KEY) return fail(503, "GROQ_API_KEY is not set on the server: showing recorded answers only.");
  let body: { question?: string; repo?: string };
  try { body = await req.json(); } catch { return fail(400, "Body must be JSON."); }
  const question = (body.question ?? "").trim();
  const repo = (body.repo ?? "").trim();
  if (question.length < 8 || question.length > 600) return fail(400, "The question must be 8 to 600 characters.");
  if (!repos().includes(repo)) return fail(400, `repo must be one of: ${repos().join(", ")}`);
  if (busy) return fail(429, "Another question is running; try again in a moment.");
  busy = true;
  try {
    const r = await run("uv", ["run", "--extra", "graph", "--extra", "ml", "--extra", "rag", "python", "-m", "src.agents",
      "ask", "--repo", path.join(SEEDED, repo), "--question", question, "--provider", "groq",
      "--state-dir", path.join(REPO_ROOT, ".blastradius-ask", repo)],
      { cwd: REPO_ROOT, timeout: 240_000, maxBuffer: 16 << 20, env: process.env });
    return Response.json({ ok: true, repo, result: JSON.parse(r.stdout) });
  } catch (e) {
    const err = e as { stderr?: string; message: string; killed?: boolean };
    return fail(500, err.killed ? "The question timed out after 240 s." : "The assistant failed.",
      (err.stderr || err.message).slice(-1500));
  } finally {
    busy = false;
  }
}
