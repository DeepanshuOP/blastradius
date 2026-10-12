/**
 * Shared helpers of the Live Lab routes (D-65). Local use only: every route calls `isLocal`; the npm scripts bind the
 * server to 127.0.0.1. Repository code never runs here: the Python CLI (`python -m src.lab`) runs it inside scratch
 * git worktrees under the OS temp directory.
 */
import { spawn, type ChildProcess } from "node:child_process";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import os from "node:os";
import path from "node:path";

export const REPO_ROOT = path.resolve(process.cwd(), "..");
export const SEEDED = path.join(REPO_ROOT, "data", "seeded", "repos");
export const RUNS_DIR = path.join(REPO_ROOT, "demo-web", "public", "lab", "runs");
export const LAB_TMP = path.join(os.tmpdir(), "br-lab");
export const PREPARED = ["click", "itsdangerous", "markupsafe", "shopcart"];
export const MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"];
export const OPERATORS = ["CMP_FLIP", "ARITH_SWAP", "NEGATE_COND", "OFF_BY_ONE", "BOOL_RETURN"];
const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);

export function isLocal(req: Request): boolean {
  const host = (req.headers.get("host") ?? "").replace(/:\d+$/, "");
  const fwd = (req.headers.get("x-forwarded-for") ?? "").split(",").map((x) => x.trim()).filter(Boolean);
  return LOCAL_HOSTS.has(host) && fwd.every((ip) => ["127.0.0.1", "::1", "::ffff:127.0.0.1"].includes(ip));
}

export const fail = (status: number, error: string, detail?: string) =>
  Response.json({ ok: false, error, detail }, { status });

/** One lab run at a time, across all route modules (Next bundles routes separately, so the state lives on globalThis). */
type LabState = { busy: boolean; since: number; what: string };
const g = globalThis as unknown as { __brLab?: LabState };
export const lock = (): LabState => (g.__brLab ??= { busy: false, since: 0, what: "" });

export const safeName = (s: string) => /^[A-Za-z0-9_-]{1,60}$/.test(s);
export const safePath = (s: string) => /^[\w./+-]{1,200}$/.test(s) && !s.split("/").includes("..") && !s.startsWith("/");

/** `uv run` arguments for the lab CLI; the `.env` file is passed to uv, never read or printed here. */
export function labCommand(args: string[], withKey: boolean): { cmd: string; argv: string[] } {
  const env = withKey && existsSync(path.join(REPO_ROOT, ".env")) ? ["--env-file", ".env"] : [];
  return { cmd: "uv", argv: ["run", ...env, "--extra", "graph", "--extra", "ml", "--extra", "rag", "python", "-m", "src.lab", ...args] };
}

/** Run a short lab CLI command and return its stdout (JSON), with a timeout. */
export function labJson(args: string[], timeoutMs = 120_000, withKey = false): Promise<{ code: number; out: string; err: string }> {
  const { cmd, argv } = labCommand(args, withKey);
  return new Promise((resolve) => {
    const child = spawn(cmd, argv, { cwd: REPO_ROOT, env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" }, detached: true });
    let out = "";
    let err = "";
    const timer = setTimeout(() => killGroup(child), timeoutMs);
    child.stdout.on("data", (d) => (out += d));
    child.stderr.on("data", (d) => (err = (err + d).slice(-4000)));
    child.on("close", (code) => { clearTimeout(timer); resolve({ code: code ?? -1, out, err }); });
    child.on("error", (e) => { clearTimeout(timer); resolve({ code: -1, out, err: String(e) }); });
  });
}

/** SIGTERM the whole process group (uv, python, and the pytest children), then SIGKILL after 3 s. */
export function killGroup(child: ChildProcess): void {
  if (!child.pid || child.exitCode !== null) return;
  try { process.kill(-child.pid, "SIGTERM"); } catch { /* already gone */ }
  setTimeout(() => { try { if (child.pid) process.kill(-child.pid, "SIGKILL"); } catch { /* gone */ } }, 3000).unref();
}

/** Recorded runs: file name, header data. */
export function recordedRuns(): { name: string; date?: string; model?: string | null; git_sha?: string; title?: string; description?: string }[] {
  if (!existsSync(RUNS_DIR)) return [];
  return readdirSync(RUNS_DIR).filter((f) => f.endsWith(".jsonl")).sort().map((f) => {
    let hdr: Record<string, unknown> = {};
    try {
      const first = readFileSync(path.join(RUNS_DIR, f), "utf-8").split("\n", 1)[0];
      hdr = (JSON.parse(first) as { data: Record<string, unknown> }).data ?? {};
    } catch { /* unreadable header */ }
    return { name: f.replace(/\.jsonl$/, ""), date: hdr.date as string, model: (hdr.model ?? null) as string | null,
      git_sha: hdr.git_sha as string, title: hdr.title as string, description: hdr.description as string };
  });
}

export const sse = (obj: unknown) => `data: ${JSON.stringify(obj)}\n\n`;
export const SSE_HEADERS = { "Content-Type": "text/event-stream; charset=utf-8", "Cache-Control": "no-store", Connection: "keep-alive" };
