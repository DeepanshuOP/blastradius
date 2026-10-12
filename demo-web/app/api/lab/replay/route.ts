/** GET /api/lab/replay?name=&speed=: a recorded run re-emitted as Server-Sent Events with its original relative timing. */
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { RUNS_DIR, SSE_HEADERS, fail, isLocal, lock, safeName } from "../_lib";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const MAX_GAP_S = 4;

export async function GET(req: Request) {
  if (!isLocal(req)) return fail(403, "The lab only serves localhost.");
  const q = new URL(req.url).searchParams;
  const name = q.get("name") ?? "";
  const speed = Math.min(Math.max(Number(q.get("speed") ?? "1") || 1, 0.25), 50);
  if (!safeName(name)) return fail(400, "Invalid run name.");
  const file = path.join(RUNS_DIR, `${name}.jsonl`);
  if (!existsSync(file)) return fail(404, "No such recorded run.");
  const st = lock();
  if (st.busy) return fail(409, "A lab run is already active.", st.what);
  st.busy = true; st.since = Date.now(); st.what = `replay ${name}`;
  const events = readFileSync(file, "utf-8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l) as { ts: string });
  const enc = new TextEncoder();
  let cancelled = false;
  const stream = new ReadableStream<Uint8Array>({
    async start(ctrl) {
      try {
        let prev: number | null = null;
        for (const ev of events) {
          if (cancelled) return;
          const t = Date.parse(ev.ts);
          if (prev !== null) await new Promise((r) => setTimeout(r, Math.min(Math.max(t - prev!, 0) / speed, (MAX_GAP_S * 1000) / speed)));
          prev = t;
          ctrl.enqueue(enc.encode(`data: ${JSON.stringify({ ...ev, replay: true })}\n\n`));
        }
        ctrl.close();
      } catch { /* client gone */ } finally { st.busy = false; }
    },
    cancel() { cancelled = true; st.busy = false; },
  });
  return new Response(stream, { headers: SSE_HEADERS });
}
