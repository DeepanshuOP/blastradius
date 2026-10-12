/**
 * `make demo-check`: every presenter screen rendered from every recorded run, offline (react-dom/server, no browser).
 *
 *   node <compiled>/scripts/presenter_check.js <runs dir>
 *
 * For each recording the events are folded through the lab's own reducer, then each of the eight screens is rendered.
 * A screen passes when it renders without throwing, shows either its content or a stated reason (never a blank), and
 * prints no "undefined" or "NaN". Prints one JSON line per recording and exits 1 on any failure.
 */
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { SCREENS, ScreenBody, absentReason, type PresenterGraph } from "../components/lab/Presenter";
import type { GraphDoc, LabEvent, LabState } from "../components/lab/types";
import { applyEvent, initialState } from "../components/lab/useLab";

const dir = process.argv[2];
let failed = 0;
for (const f of readdirSync(dir).filter((x) => x.endsWith(".jsonl")).sort()) {
  const name = f.replace(/\.jsonl$/, "");
  const evs = readFileSync(path.join(dir, f), "utf-8").split("\n").filter((l) => l.trim()).map((l) => ({ ...(JSON.parse(l) as LabEvent), replay: true }));
  const s: LabState = evs.reduce(applyEvent, { ...initialState, mode: "replay", running: false, startedAt: 1 });
  const doc = JSON.parse(readFileSync(path.join(dir, `${name}.graph.json`), "utf-8")) as GraphDoc;
  const g: PresenterGraph = { nodes: doc.nodes, edges: doc.edges, changed: (s.change?.changed_nodes as string[]) ?? [], paths: [], atRisk: [], outcomes: {} };
  const screens = SCREENS.map((sc, i) => {
    try {
      const html = renderToStaticMarkup(<ScreenBody s={s} g={g} i={i} />);
      const text = html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
      const bad = /\bundefined\b|\bNaN\b/.test(text) ? "prints undefined or NaN" : text.length < 20 ? "blank" : null;
      if (bad) failed++;
      return { id: sc.id, state: sc.ready(s) ? "shown" : absentReason(sc, s) ? "absent, reason stated" : "waiting", ok: !bad, problem: bad, chars: text.length };
    } catch (e) {
      failed++;
      return { id: sc.id, state: "error", ok: false, problem: String(e).slice(0, 200), chars: 0 };
    }
  });
  console.log(JSON.stringify({ recording: name, screens }));
}
process.exit(failed ? 1 : 0);
