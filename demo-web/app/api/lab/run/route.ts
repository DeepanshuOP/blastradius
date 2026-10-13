/**
 * GET  /api/lab/run   -> { live, llm, busy }
 * POST /api/lab/run   -> Server-Sent Events: one lab event per `data:` line, from `python -m src.lab run ...`.
 * 409 while another run is active; the child process group is killed when the client disconnects, and after 15 min.
 */
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { MODELS, OPERATORS, PREPARED, REPO_ROOT, SSE_HEADERS, fail, isLocal, killGroup, labCommand, labJson, labParse, lock, safeName, safePath, sse } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const URL_RE = /^https:\/\/github\.com\/([\w.-]+)\/([\w.-]+?)(\.git)?$/;
const PR_RE = /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/pull\/\d+\/?$/;
const MAX_RUN_MS = 15 * 60_000;

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  const st = lock();
  const s = await labJson(["status"], 60_000, true);
  const j = s.code === 0 ? labParse(s, "status") : {};
  return Response.json({ ok: true, live: true, llm: Boolean(j.llm), quota: j.quota ?? null, providers: j.providers ?? null, fix_mode: j.fix_mode ?? "suggest", busy: st.busy, since: st.busy ? st.since : null, what: st.what });
}

type Body = {
  repo?: string; url?: string; pr?: string; task?: string; variant?: "standard" | "hard";
  probe?: { file: string; function: string };
  inject?: { file: string; function: string; operator: string; line?: number };
  edit?: { file: string; text: string }; model?: string; noLlm?: boolean; repairArena?: boolean;
};

export async function POST(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  let b: Body;
  try { b = await req.json(); } catch { return fail(400, "Body must be JSON."); }
  let args: string[] = ["run", "--mode", "live"];
  if (b.probe) {                          // suite strength: up to five mutants of one function, no model
    if (!b.repo || !PREPARED.includes(b.repo)) return fail(400, `repo must be one of: ${PREPARED.join(", ")}`);
    if (!safePath(b.probe.file) || !b.probe.file.endsWith(".py")) return fail(400, "probe.file must be a repository-relative .py path");
    if (!/^[\w.<>]{1,120}$/.test(b.probe.function)) return fail(400, "Invalid function name.");
    args = ["probe", "--repo", b.repo, "--file", b.probe.file, "--function", b.probe.function];
  } else if (b.pr) {
    if (!PR_RE.test(b.pr.trim())) return fail(400, "Only https://github.com/<owner>/<repo>/pull/<n> URLs are accepted.");
    args.push("--pr", b.pr.trim());
  } else if (b.repo) {
    if (!PREPARED.includes(b.repo)) return fail(400, `repo must be one of: ${PREPARED.join(", ")}`);
    args.push("--repo", b.repo);
  } else if (b.url) {
    if (!URL_RE.test(b.url.trim())) return fail(400, "Only https://github.com/<owner>/<repo> URLs are accepted.");
    args.push("--url", b.url.trim());
  } else return fail(400, "Give repo, url or pr.");
  if (b.model && !b.probe) {
    if (!MODELS.includes(b.model)) return fail(400, `model must be one of: ${MODELS.join(", ")}`);
    args.push("--model", b.model);
  }
  if (b.probe) { /* no model, no flags */ }
  else if (b.noLlm) args.push("--no-llm");
  else if (b.repairArena) args.push("--repair-arena");
  let tmp: string | null = null;
  if (b.probe || b.pr) {
    /* the change is the pull request itself, or the probe's own mutants */
  } else if (b.task) {
    if (!safeName(b.task)) return fail(400, "Invalid task id.");
    args.push("--task", b.task, "--variant", b.variant === "hard" ? "hard" : "standard");
  } else if (b.inject) {
    const i = b.inject;
    if (!safePath(i.file) || !i.file.endsWith(".py")) return fail(400, "inject.file must be a repository-relative .py path");
    if (!/^[\w.<>]{1,120}$/.test(i.function)) return fail(400, "Invalid function name.");
    if (!OPERATORS.includes(i.operator)) return fail(400, `operator must be one of: ${OPERATORS.join(", ")}`);
    args.push("--inject", `${i.file}::${i.function}::${i.operator}${Number.isInteger(i.line) ? `::${i.line}` : ""}`);
  } else if (b.edit) {
    if (!safePath(b.edit.file)) return fail(400, "edit.file must be a repository-relative path");
    if (typeof b.edit.text !== "string" || b.edit.text.length > 300_000) return fail(400, "edit.text must be a string up to 300 kB.");
    tmp = mkdtempSync(path.join(os.tmpdir(), "br-lab-edit-"));
    const f = path.join(tmp, "new_text");
    writeFileSync(f, b.edit.text, "utf-8");
    args.push("--edit", `${b.edit.file}=@${f}`);
  } else return fail(400, "Choose a change: task, inject or edit.");

  const st = lock();
  if (st.busy) { if (tmp) rmSync(tmp, { recursive: true, force: true }); return fail(409, "A lab run is already active.", st.what); }
  st.busy = true; st.since = Date.now(); st.what = b.probe ? `probe ${b.repo}: ${b.probe.function}` : b.pr ? `pull request ${b.pr}` : `${b.repo ?? b.url}: ${b.task ?? (b.inject ? "inject" : "edit")}`;

  const { cmd, argv } = labCommand(args, !b.noLlm || Boolean(b.pr));
  const child = spawn(cmd, argv, { cwd: REPO_ROOT, env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" }, detached: true });
  const enc = new TextEncoder();
  let done = false;
  const release = () => {
    if (done) return;
    done = true; st.busy = false;
    if (tmp) rmSync(tmp, { recursive: true, force: true });
  };
  const stream = new ReadableStream<Uint8Array>({
    start(ctrl) {
      let buf = "";
      let errTail = "";
      let sawEnd = false;
      const timer = setTimeout(() => killGroup(child), MAX_RUN_MS);
      child.stdout.on("data", (d: Buffer) => {
        buf += d.toString("utf-8");
        let i: number;
        while ((i = buf.indexOf("\n")) >= 0) {
          const line = buf.slice(0, i).trim();
          buf = buf.slice(i + 1);
          if (!line) continue;
          if (line.includes('"type":"run.end"')) sawEnd = true;
          try { ctrl.enqueue(enc.encode(`data: ${line}\n\n`)); } catch { /* client gone */ }
        }
      });
      child.stderr.on("data", (d: Buffer) => { errTail = (errTail + d.toString("utf-8")).slice(-3000); });
      child.on("close", (code) => {
        clearTimeout(timer);
        if (!sawEnd) {                      // the process ended without its own run.end: say so, with its stderr
          try {
            ctrl.enqueue(enc.encode(sse({ seq: -1, ts: new Date().toISOString(), stage: "meta", type: "run.end", status: "failed",
              dur_ms: 0, data: { reason: `the lab process exited with code ${code}`, stderr: errTail.slice(-1500), transport: true } })));
          } catch { /* closed */ }
        }
        try { ctrl.close(); } catch { /* closed */ }
        release();
      });
      child.on("error", (e) => { try { ctrl.error(e); } catch { /* closed */ } release(); });
    },
    cancel() { killGroup(child); },
  });
  req.signal.addEventListener("abort", () => killGroup(child));
  return new Response(stream, { headers: SSE_HEADERS });
}
