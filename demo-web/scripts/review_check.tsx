/**
 * `make demo-check`: the review-ready Live Lab, rendered with react-dom/server (no browser, no network).
 *
 *   node <compiled>/scripts/review_check.js <runs dir>
 *
 * Prints one JSON line per check ({check, ok, detail}); exit 1 if any fails. Checks:
 *   - the model chip says "ready (<model> via Groq|Bedrock)" or "offline — <reason>" for each server state, and the idle page has it;
 *   - the guided demo completes on its recording: every one of the five steps ends ok, no step falls back, and the
 *     stepper renders five REPLAY steps with timings and the "Finished" caption;
 *   - a skipped repair shows its reason and the "Play recorded repair" button labelled REPLAY with its date;
 *   - the "top x %" slider renders on a recording and its counts agree with the recording's own verdicts.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { GUIDED_RECORDING, GUIDED_STEPS, GuidedStepper, liveFailure, stepTone, type Guided } from "../components/lab/GuidedDemo";
import LabPage, { recordedRepairFor } from "../components/lab/LabPage";
import { RacePanel, RepairPanel, topShare } from "../components/lab/Panels";
import { ModelChip, modelStatus } from "../components/lab/TopBar";
import type { LabEvent, LabState } from "../components/lab/types";
import { applyEvent, initialState, type Availability } from "../components/lab/useLab";

const dir = process.argv[2];
let failed = 0;
const report = (check: string, ok: boolean, detail: string) => { if (!ok) failed++; console.log(JSON.stringify({ check, ok, detail })); };
const load = (name: string): LabState => readFileSync(path.join(dir, `${name}.jsonl`), "utf-8").split("\n").filter((l) => l.trim())
  .map((l) => ({ ...(JSON.parse(l) as LabEvent), replay: true }))
  .reduce(applyEvent, { ...initialState, mode: "replay", running: false, startedAt: 1 });

// ---- the model chip ----
const M = "openai/gpt-oss-120b";
const base: Availability = { checked: true, live: true, llm: true, reason: "", quota: { [M]: { used: 5175, cap: 200000, ok: true, resume_after: null } } };
const idle = initialState;
const cases: [string, LabState, Availability, string][] = [
  ["ready", idle, base, "Model: ready (gpt-oss-120b via Groq)"],
  // D-69: Groq's quota used up, the Bedrock fallback configured and under budget -> the chip names Bedrock
  ["bedrock fallback", idle, { ...base, quota: { [M]: { used: 200000, cap: 200000, ok: false, resume_after: null } },
    providers: { [M]: { provider: "bedrock", why: "Groq unavailable", bedrock: { configured: true, model_id: "openai.gpt-oss-120b-1:0", spent_usd: 0, budget_usd: 5, ok: true } } } },
    "Model: ready (gpt-oss-120b via Bedrock)"],
  ["forced bedrock", idle, { ...base, providers: { [M]: { provider: "bedrock", why: "BR_LLM_PROVIDER=bedrock", bedrock: { configured: true, model_id: "openai.gpt-oss-120b-1:0", spent_usd: 0, budget_usd: 5, ok: true } } } },
    "Model: ready (gpt-oss-120b via Bedrock)"],
  ["no key", idle, { ...base, llm: false }, "Model: offline — no key"],
  ["quota", idle, { ...base, quota: { [M]: { used: 200000, cap: 200000, ok: false, resume_after: "2026-10-14T08:00:00" } } }, "Model: offline — quota"],
  ["static", idle, { ...base, live: false, llm: false, reason: "static build" }, "Model: offline — no server (static build)"],
  ["disabled by option", { ...idle, mode: "live", header: { llm: "disabled by --no-llm" } }, base, "Model: offline — disabled by option"],
];
const chipBad = cases.filter(([, s, a, want]) => modelStatus(s, a, M).text !== want || !renderToStaticMarkup(<ModelChip s={s} avail={a} model={M} />).includes(want));
let idleHtml = "";
try { idleHtml = renderToStaticMarkup(<LabPage />); } catch (e) { idleHtml = `ERROR ${String(e)}`; }
report("model chip", chipBad.length === 0 && idleHtml.includes('data-testid="model-chip"'),
  chipBad.length ? `wrong text for: ${chipBad.map((c) => c[0]).join(", ")}` : `${cases.length} states render the expected text; idle page has the chip`);
report("idle page: Run full demo button", idleHtml.includes('data-testid="run-full-demo"'), idleHtml.startsWith("ERROR") ? idleHtml.slice(0, 160) : "present");

// ---- the guided demo on its recording ----
try {
  const s = load(GUIDED_RECORDING);
  const tones = GUIDED_STEPS.map((_, i) => stepTone(s, i));
  const g: Guided = { phase: "done", live: [], fellBackAt: 0, reason: "no local server", pick: null };
  const html = renderToStaticMarkup(<GuidedStepper s={s} g={g} onStop={() => undefined} />);
  const okSteps = (html.match(/data-tone="ok"/g) ?? []).length;
  const replaySteps = (html.match(/data-source="replay"/g) ?? []).length;
  const ok = tones.every((t) => t === "ok") && liveFailure(s) === null && okSteps === 5 && replaySteps === 5 && html.includes("Finished") && s.validate.verdict?.accepted === true;
  report("guided demo completes on the recorded run", ok,
    `steps ${tones.join("/")}; fallback ${liveFailure(s)}; accepted ${String(s.validate.verdict?.accepted)}; ${okSteps} ok, ${replaySteps} REPLAY in the stepper`);
} catch (e) { report("guided demo completes on the recorded run", false, String(e).slice(0, 200)); }

// ---- a skipped repair offers the recorded one ----
{
  const s: LabState = { ...initialState, mode: "live", repair: { ...initialState.repair, skipped: "no GROQ_API_KEY" } };
  const html = renderToStaticMarkup(<RepairPanel s={s} recorded={{ name: GUIDED_RECORDING, title: "Guided demo", date: "2026-10-13T10:00:00", exact: true }} onPlayRecorded={() => undefined} />);
  const ok = html.includes("no GROQ_API_KEY") && html.includes('data-testid="play-recorded-repair"') && html.includes("REPLAY") && html.includes("2026-10-13");
  report("repair skipped: reason and Play recorded repair (REPLAY, dated)", ok, ok ? "reason, button, REPLAY label and date rendered" : html.slice(0, 200));
}

// ---- which recording stands in for a skipped repair ----
{
  const runs = JSON.parse(readFileSync(path.join(dir, "index.json"), "utf-8"));
  const other: LabState = { ...initialState, mode: "live", repo: { name: "itsdangerous" }, change: { source: { kind: "inject", function: "Signer.sign", operator: "CMP_FLIP" } } };
  const same: LabState = { ...other, change: { source: { kind: "inject", function: "HMACAlgorithm.__init__", operator: "NEGATE_COND" } } };
  const a = recordedRepairFor(other, runs), b = recordedRepairFor(same, runs);
  const ok = a?.name === GUIDED_RECORDING && a.exact === false && b?.name === GUIDED_RECORDING && b.exact === true;
  report("recorded repair: same change when recorded, else a recording whose repair ran", ok, `other change -> ${a?.name} (exact ${a?.exact}); seed-7 change -> ${b?.name} (exact ${b?.exact})`);
}

// ---- the slider on a recording ----
try {
  const s = load("itsdangerous-pr1");
  const lane = s.tests.race!.lanes.find((l) => l.name === "risk-first")!;
  const all = topShare(lane, 100);
  const html = renderToStaticMarkup(<RacePanel s={s} />);
  const failing = s.tests.results.filter((t) => t.outcome === "failed" || t.outcome === "error").length;
  const ok = html.includes('data-testid="top-slider"') && html.includes("REPLAY") && all.k === all.n && all.caught === all.failing && all.failing === failing && all.savedMs === 0;
  report("top-x% slider on a recording", ok, `n ${all.n}, failing ${all.failing} (recording: ${failing}); at 100% nothing saved: ${all.savedMs === 0}`);
} catch (e) { report("top-x% slider on a recording", false, String(e).slice(0, 200)); }

process.exit(failed ? 1 : 0);
