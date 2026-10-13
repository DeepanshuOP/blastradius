/**
 * POST /api/lab/approve {run}: the Live Lab "Approve fix" button (D-70, ask mode). Records the operator's approval in
 * the run's decision log and lets the gate open the fix PR (`python -m src.agents.fixpr approve`). The gate still
 * refuses a repository outside BR_FIX_ALLOWLIST, a failed check, or a default-branch target. Returns the log's records.
 */
import { spawn, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { REPO_ROOT, fail, isLocal, killGroup } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const RUN_RE = /^[\w.-]{1,120}$/;

export async function POST(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  let b: { run?: string };
  try { b = await req.json(); } catch { return fail(400, "Body must be JSON."); }
  if (!b.run || !RUN_RE.test(b.run)) return fail(400, "run must be a decision-log run id");
  const logFile = path.join(REPO_ROOT, "logs", "agent", `${b.run}.jsonl`);
  if (!existsSync(logFile)) return fail(404, "No decision log for this run on this machine.");
  const by = spawnSync("git", ["config", "user.name"], { cwd: REPO_ROOT, encoding: "utf-8" }).stdout.trim() || "operator";
  const env = existsSync(path.join(REPO_ROOT, ".env")) ? ["--env-file", ".env"] : [];
  const argv = ["run", ...env, "python", "-m", "src.agents.fixpr", "approve", "--run", b.run, "--by", by, "--source", "Live Lab button"];
  const res = await new Promise<{ code: number; out: string; err: string }>((resolve) => {
    const child = spawn("uv", argv, { cwd: REPO_ROOT, env: { ...process.env }, detached: true });
    let out = "", err = "";
    const timer = setTimeout(() => killGroup(child), 10 * 60_000);
    child.stdout.on("data", (d) => (out += d));
    child.stderr.on("data", (d) => (err = (err + d).slice(-2000)));
    child.on("close", (code) => { clearTimeout(timer); resolve({ code: code ?? -1, out, err }); });
    child.on("error", (e) => { clearTimeout(timer); resolve({ code: -1, out, err: String(e) }); });
  });
  const records = readFileSync(logFile, "utf-8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
  let result: Record<string, unknown> = {};
  try { result = JSON.parse(res.out.trim().split("\n").pop() ?? "{}"); } catch { /* the records say what happened */ }
  return Response.json({ ok: result.status === "opened", result, records, error: result.status === "opened" ? undefined : String(result.reason ?? res.err.slice(-300)) });
}
