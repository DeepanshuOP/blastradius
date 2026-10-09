/**
 * POST /api/analyze: shallow-clone a public GitHub repository and run the offline
 * Impact Analysis Agent (`python -m src.agents impact --provider offline`) on it.
 * Local use only: requests whose Host is not localhost are refused, and the
 * npm scripts bind the server to 127.0.0.1. No LLM, no token, no write outside
 * os.tmpdir()/br-analyze.
 */
import { execFile } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const run = promisify(execFile);
const URL_RE = /^https:\/\/github\.com\/([\w.-]+)\/([\w.-]+?)(\.git)?$/;
const BRANCH_RE = /^[\w][\w./-]{0,99}$/;
const REPO_ROOT = path.resolve(process.cwd(), "..");
const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);

function isLocal(req: Request): boolean {
  const host = (req.headers.get("host") ?? "").replace(/:\d+$/, "");
  const fwd = (req.headers.get("x-forwarded-for") ?? "").split(",").map((x) => x.trim()).filter(Boolean);
  return LOCAL_HOSTS.has(host) && fwd.every((ip) => ["127.0.0.1", "::1", "::ffff:127.0.0.1"].includes(ip));
}

const fail = (status: number, error: string, detail?: string) => Response.json({ ok: false, error, detail }, { status });

/** Count .py and .java files (skipping hidden and build directories), stopping early at 1 of each. */
function languages(dir: string): { python: number; java: number } {
  const n = { python: 0, java: 0 };
  const walk = (d: string, depth: number) => {
    if (depth > 8 || (n.python > 0 && n.java > 0)) return;
    for (const e of readdirSync(d, { withFileTypes: true })) {
      if (e.name.startsWith(".") || ["node_modules", "build", "target", "dist"].includes(e.name)) continue;
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p, depth + 1);
      else if (e.name.endsWith(".py")) n.python++;
      else if (e.name.endsWith(".java")) n.java++;
    }
  };
  walk(dir, 0);
  return n;
}

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The analyzer only serves localhost.");
  return Response.json({ ok: true, live: true });
}

export async function POST(req: Request) {
  if (!isLocal(req)) return fail(403, "The analyzer only serves localhost.");
  let body: { url?: string; story?: string; branch?: string };
  try { body = await req.json(); } catch { return fail(400, "Body must be JSON."); }
  const url = (body.url ?? "").trim();
  const story = (body.story ?? "").trim();
  const branch = (body.branch ?? "").trim();
  const m = URL_RE.exec(url);
  if (!m) return fail(400, "Only https://github.com/<owner>/<repo> URLs are accepted.");
  if (story.length < 10 || story.length > 2000) return fail(400, "The user story must be 10 to 2,000 characters.");
  if (branch && !BRANCH_RE.test(branch)) return fail(400, "Invalid branch name.");

  const slug = `${m[1]}__${m[2]}${branch ? `__${branch.replace(/[^\w.-]/g, "_")}` : ""}`;
  const dir = path.join(os.tmpdir(), "br-analyze", slug);
  const env = { ...process.env, GIT_TERMINAL_PROMPT: "0" };
  try {
    if (!existsSync(path.join(dir, ".git"))) {
      await run("git", ["clone", "--quiet", "--depth", "50", ...(branch ? ["--branch", branch] : []), url, dir],
        { timeout: 120_000, env });
    }
  } catch (e) {
    return fail(502, "git clone failed (repository missing, private, or branch not found).", String((e as Error).message).slice(0, 500));
  }

  const lang = languages(dir);
  if (lang.python === 0 && lang.java === 0) {
    return fail(422, "BlastRadius analyses Python and Java repositories only; no .py or .java file was found.");
  }

  let stdout = "";
  try {
    const r = await run("uv", ["run", "--extra", "graph", "python", "-m", "src.agents", "impact", "--repo", dir,
      "--story", story, "--provider", "offline"], { cwd: REPO_ROOT, timeout: 180_000, maxBuffer: 32 << 20, env });
    stdout = r.stdout;
  } catch (e) {
    const err = e as { stderr?: string; message: string; killed?: boolean };
    return fail(500, err.killed ? "The impact analysis timed out after 180 s." : "The impact analysis failed.",
      (err.stderr || err.message).slice(-1500));
  }

  const { stdout: head } = await run("git", ["-C", dir, "rev-parse", "HEAD"], { env });
  let out = path.join(dir, ".blastradius", "impact", head.trim().slice(0, 12));
  if (!existsSync(path.join(out, "impact.json"))) {  // fall back to the newest impact run
    const root = path.join(dir, ".blastradius", "impact");
    const dirs = existsSync(root) ? readdirSync(root).map((d) => path.join(root, d)).filter((d) => existsSync(path.join(d, "impact.json"))) : [];
    dirs.sort((a, b) => statSync(b).mtimeMs - statSync(a).mtimeMs);
    if (!dirs.length) return fail(500, "The analysis ran but wrote no impact.json.", stdout.slice(-1500));
    out = dirs[0];
  }
  return Response.json({
    ok: true, url, branch: branch || null, clone_dir: dir, languages: lang,
    impact: JSON.parse(readFileSync(path.join(out, "impact.json"), "utf-8")),
    markdown: readFileSync(path.join(out, "impact.md"), "utf-8"),
  });
}
