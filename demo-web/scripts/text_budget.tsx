/**
 * `make demo-check`: the text budget of the Live Lab main screen, counted in server-rendered HTML (react-dom/server, no
 * browser): no visible paragraph runs past 2 lines and no caption past 14 words.
 *
 *   node <compiled>/scripts/text_budget.js <runs dir>
 *
 * What is counted: every <p> and <figcaption> of (a) the idle lab page and (b) each result panel, rendered from every
 * recording through the lab's own reducer. Not counted, because the reader does not see it without asking: the content
 * of a closed <details>, anything with class sr-only, and the Explain sentences (the Explain switch is off by default,
 * so they are not in the markup). The pull-request comment card renders the bot's own text verbatim and is exempt.
 * A line is CPL = 80 characters (a 14 px sans-serif line of the narrowest text column, 560 px). A caption is a
 * paragraph whose class list has the token `cap`, or a <figcaption>.
 */
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { ArenaPanel } from "../components/lab/Arena";
import { TestGapPanel } from "../components/lab/BreakIt";
import LabPage from "../components/lab/LabPage";
import { ImpactPanel, RacePanel, RepairPanel, TriagePanel, VerdictPanel } from "../components/lab/Panels";
import { PipelineRail } from "../components/lab/Rail";
import { IntegrityPanel, ReportPanel } from "../components/lab/Report";
import type { LabEvent, LabState } from "../components/lab/types";
import { applyEvent, initialState } from "../components/lab/useLab";

const CPL = 80;
const MAX_LINES = 2;
const MAX_CAPTION_WORDS = 14;

const strip = (html: string): string => {
  let h = html.replace(/<script[\s\S]*?<\/script>/g, "");
  let prev = "";
  while (prev !== h) {                                  // innermost closed <details> first
    prev = h;
    h = h.replace(/<details(?![^>]*\sopen(?:=|\s|>))[^>]*>(?:(?!<details)[\s\S])*?<\/details>/g, "");
  }
  h = h.replace(/<article[^>]*aria-label="Pull request comment"[\s\S]*?<\/article>/g, "");
  return h;
};

type Over = { lines: number; words: number; caption: boolean; text: string };
function over(html: string): { n: number; over: Over[] } {
  const out: Over[] = [];
  let n = 0;
  const re = /<(p|figcaption)\b([^>]*)>([\s\S]*?)<\/\1>/g;
  for (const m of strip(html).matchAll(re)) {
    const cls = /class="([^"]*)"/.exec(m[2])?.[1] ?? "";
    if (/\bsr-only\b/.test(cls)) continue;
    const text = m[3].replace(/<[^>]+>/g, " ").replace(/&[a-z#0-9]+;/g, "x").replace(/\s+/g, " ").trim();
    if (!text) continue;
    n++;
    const words = text.split(" ").length;
    const lines = Math.ceil(text.length / CPL);
    const caption = m[1] === "figcaption" || cls.split(/\s+/).includes("cap");
    if (lines > MAX_LINES || (caption && words > MAX_CAPTION_WORDS)) out.push({ lines, words, caption, text: text.slice(0, 90) });
  }
  return { n, over: out };
}

const dir = process.argv[2];
let failed = 0;

// The check must be able to fail: a three-line paragraph and a 15-word caption are both flagged, a short one is not.
const control = [
  over(`<p class="ui">${"word ".repeat(50)}</p>`).over.length === 1,
  over(`<p class="cap">${"word ".repeat(15)}</p>`).over.length === 1,
  over(`<p class="cap">${"word ".repeat(14)}</p>`).over.length === 0,
  over(`<details><p>${"word ".repeat(80)}</p></details>`).over.length === 0,
].every(Boolean);
console.log(JSON.stringify({ screen: "negative control", ok: control }));
if (!control) failed++;
const report = (screen: string, html: string) => {
  const r = over(html);
  if (r.over.length) failed++;
  console.log(JSON.stringify({ screen, paragraphs: r.n, over: r.over }));
};

try { report("idle", renderToStaticMarkup(<LabPage />)); } catch (e) { failed++; console.log(JSON.stringify({ screen: "idle", error: String(e).slice(0, 200) })); }

for (const f of readdirSync(dir).filter((x) => x.endsWith(".jsonl")).sort()) {
  const name = f.replace(/\.jsonl$/, "");
  const evs = readFileSync(path.join(dir, f), "utf-8").split("\n").filter((l) => l.trim()).map((l) => ({ ...(JSON.parse(l) as LabEvent), replay: true }));
  const s: LabState = evs.reduce(applyEvent, { ...initialState, mode: "replay", running: false, startedAt: 1 });
  const panels: [string, React.ReactElement][] = [
    ["impact", <ImpactPanel s={s} />], ["race", <RacePanel s={s} />], ["arena", <ArenaPanel s={s} />], ["triage", <TriagePanel s={s} />],
    ["repair", <RepairPanel s={s} />], ["verdict", <VerdictPanel s={s} />], ["comment", <ReportPanel s={s} />],
    ["integrity", <IntegrityPanel s={s} />], ["gap", <TestGapPanel s={s} />], ["rail", <PipelineRail s={s} active={null} onPick={() => undefined} />],
  ];
  for (const [id, el] of panels) {
    try { report(`${name}/${id}`, renderToStaticMarkup(el)); } catch (e) { failed++; console.log(JSON.stringify({ screen: `${name}/${id}`, error: String(e).slice(0, 200) })); }
  }
}
process.exit(failed ? 1 : 0);
