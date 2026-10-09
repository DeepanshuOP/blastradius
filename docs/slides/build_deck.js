const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require("/root/.claude/skills/synced/bf4a3ab2-07de-40ae-ae7d-d5c22a7291b5_f8cba1ca-c905-48f0-938d-5d043e817455/pptx/scripts/apply_theme.js");

const THEME = {
  name: "BlastRadius",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1F2A", lt1: "FFFFFF", dk2: "131722", lt2: "F2F3F5",
    accent1: "E8572A", accent2: "F2A93B", accent3: "2F7FB0",
    accent4: "2E9E6A", accent5: "5E6678", accent6: "C23B30",
    hlink: "2F7FB0", folHlink: "5E6678",
  },
};
const H = THEME.colors; // hex, only for hex-only options

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "BlastRadius — Final Review";
pres.author = "Deepanshu, Sanskriti Singh, Prisha Vadhavkar";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

const W = 13.333;
const FOOT = "BlastRadius · BITE497J Project I · Final Review";

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.55, w: 7.6, h: 1.2, fontSize: 54, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 2.95, w: 7.4, h: 1.3, fontSize: 20, color: C.accent2, fontFace: THEME.bodyFontFace, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  margin: [0.4, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.13, h: 0.9, fontSize: 32, bold: true, color: C.text1, fontFace: THEME.headFontFace, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 12.23, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5, align: "right", margin: 0 },
});

// ---------- helpers ----------
async function icon(Comp, hex, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + hex, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
const ICONS = {};
async function loadIcons() {
  const list = {
    clock: fa.FaClock, flask: fa.FaFlask, hourglass: fa.FaHourglassHalf, code: fa.FaCodeBranch,
    play: fa.FaPlay, github: fa.FaGithub, gauge: fa.FaTachometerAlt, db: fa.FaDatabase,
    file: fa.FaFileAlt, list: fa.FaListUl, finger: fa.FaFingerprint, project: fa.FaProjectDiagram,
    shield: fa.FaShieldAlt, check: fa.FaCheckCircle, times: fa.FaTimesCircle, lock: fa.FaLock,
    redo: fa.FaRedo, search: fa.FaSearch, bug: fa.FaBug, cut: fa.FaCut, sitemap: fa.FaSitemap,
    bolt: fa.FaBolt, wifi: fa.FaWifi, key: fa.FaKey, clone: fa.FaClone, history: fa.FaHistory,
    archive: fa.FaArchive, user: fa.FaUserSecret, tag: fa.FaTag, robot: fa.FaRobot, seed: fa.FaRandom,
    target: fa.FaBullseye, rocket: fa.FaRocket, clip: fa.FaClipboardCheck, eye: fa.FaEye, layer: fa.FaLayerGroup, chart: fa.FaChartBar, road: fa.FaRoad, exclam: fa.FaExclamationTriangle,
  };
  for (const [k, comp] of Object.entries(list)) ICONS[k] = await icon(comp, "FFFFFF");
}
function title(slide, t) { slide.addText(t, { placeholder: "title" }); }
function text(slide, t, o) { slide.addText(t, Object.assign({ isTextBox: true, margin: 0, fontSize: 15, color: C.text1, valign: "top" }, o)); }
function card(slide, x, y, w, h, fill, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill || C.background2 }, line: { type: "none" }, objectName: name || "card" });
}
function iconCircle(slide, key, x, y, d, fill) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill || C.accent1 }, line: { type: "none" }, objectName: "icon circle" });
  const p = d * 0.24;
  slide.addImage({ data: ICONS[key], x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, altText: key + " icon" });
}
function pill(slide, t, x, y, w, fill) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.34, rectRadius: 0.17, fill: { color: fill }, line: { type: "none" }, objectName: "status pill" });
  text(slide, t, { x, y, w, h: 0.34, fontSize: 11, bold: true, color: C.background1, align: "center", valign: "middle" });
}
function numCircle(slide, n, x, y, d, fill) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill || C.accent1 }, line: { type: "none" }, objectName: "number badge" });
  text(slide, String(n), { x, y, w: d, h: d, fontSize: Math.round(d * 30), bold: true, color: C.background1, align: "center", valign: "middle" });
}
function arrow(slide, x1, y1, x2, y2, color) {
  const o = { line: { color: color || C.accent5, width: 1.75, endArrowType: "triangle" } };
  const x = Math.min(x1, x2), y = Math.min(y1, y2), w = Math.abs(x2 - x1), h = Math.abs(y2 - y1);
  if (x2 < x1) o.flipH = true;
  if (y2 < y1) o.flipV = true;
  slide.addShape(pres.shapes.LINE, Object.assign({ x, y, w, h, objectName: "arrow" }, o));
}
function content(section) { return pres.addSlide({ masterName: "CONTENT", sectionTitle: section }); }
const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  catAxisLabelColor: H.dk1, valAxisLabelColor: H.accent5, dataLabelColor: H.dk1, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontSize: 12 };

// ---------- slides ----------
async function build() {
  await loadIcons();

  // 1. Title
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Introduction" });
  s.addText("BlastRadius", { placeholder: "title" });
  s.addText("Graph-Based Change Impact Prediction and Dependency Analysis for Software Repositories", { placeholder: "body" });
  text(s, [
    { text: "Deepanshu (23BIT0264)  ·  Sanskriti Singh (23BIT0256)  ·  Prisha Vadhavkar (23BIT0010)", options: { breakLine: true } },
    { text: "Guide: Dr. Yoga Raja C A", options: { breakLine: true } },
  ], { x: 0.8, y: 4.75, w: 8.2, h: 0.75, fontSize: 15, color: C.background1, paraSpaceAfter: 4 });
  text(s, "BITE497J Project I  ·  Final Review  ·  21 October 2026  ·  SCORE, VIT Vellore", { x: 0.8, y: 5.75, w: 8.2, h: 0.35, fontSize: 13, color: C.background2 });
  // blast-radius rings motif
  const cx = 10.75, cy = 3.75;
  [2.3, 1.65, 1.0].forEach((r, i) => s.addShape(pres.shapes.OVAL, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { color: C.accent1, transparency: 88 - i * 4 }, line: { color: C.accent1, width: 1, transparency: 40 }, objectName: "ring" }));
  s.addShape(pres.shapes.OVAL, { x: cx - 0.38, y: cy - 0.38, w: 0.76, h: 0.76, fill: { color: C.accent1 }, line: { type: "none" }, objectName: "change dot" });
  const dots = [[1.0, 20, 1], [1.65, 75, 0], [1.65, 160, 1], [2.3, 230, 0], [1.0, 200, 0], [2.3, 310, 0], [1.65, 285, 0], [2.3, 120, 0], [1.0, 330, 0], [2.3, 30, 0]];
  dots.forEach(([r, a, f]) => {
    const t = a * Math.PI / 180, d = 0.26;
    s.addShape(pres.shapes.OVAL, { x: cx + r * Math.cos(t) - d / 2, y: cy + r * Math.sin(t) - d / 2, w: d, h: d, fill: { color: f ? C.accent2 : C.background2 }, line: { type: "none" }, objectName: "test dot" });
  });
  s.addNotes("Introduce the team and the guide. One-line pitch: BlastRadius asks which tests a code change actually broke in CI, and builds a public dataset (BR-Bench) that answers it from real GitHub Actions runs. The rings motif: the change sits at the centre; the dots are tests; the highlighted ones are the tests it broke.");

  // 2. The question
  s = content("Introduction");
  title(s, "Which tests will this change actually break?");
  const rows2 = [
    ["clock", "Running every test on every change is slow and costly", "Teams want to run only the tests a change can break."],
    ["flask", "Research is scored against the wrong labels", "Impact-analysis methods are evaluated on labels that never record a real test failure."],
    ["hourglass", "The evidence disappears", "GitHub Actions logs expire after 90 days. Data not captured now is lost for good."],
  ];
  rows2.forEach(([ic, h, b], i) => {
    const y = 1.65 + i * 1.6;
    iconCircle(s, ic, 0.6, y, 0.8);
    text(s, h, { x: 1.65, y: y - 0.02, w: 5.6, h: 0.45, fontSize: 18, bold: true });
    text(s, b, { x: 1.65, y: y + 0.45, w: 5.6, h: 0.8, fontSize: 15, color: C.accent5 });
  });
  // diagram
  const dx = 10.05, dy = 3.85;
  [2.15, 1.45].forEach((r) => s.addShape(pres.shapes.OVAL, { x: dx - r, y: dy - r, w: 2 * r, h: 2 * r, fill: { color: C.background2 }, line: { color: C.accent5, width: 0.75, dashType: "dash" }, objectName: "ring" }));
  s.addShape(pres.shapes.OVAL, { x: dx - 0.62, y: dy - 0.62, w: 1.24, h: 1.24, fill: { color: C.text2 }, line: { type: "none" }, objectName: "change" });
  text(s, "code change", { x: dx - 0.62, y: dy - 0.62, w: 1.24, h: 1.24, fontSize: 12, bold: true, color: C.background1, align: "center", valign: "middle" });
  const t2 = [[1.45, 40, 1], [1.45, 140, 0], [1.45, 250, 0], [1.45, 320, 0], [2.15, 10, 0], [2.15, 80, 0], [2.15, 190, 1], [2.15, 215, 0], [2.15, 285, 0]];
  t2.forEach(([r, a, f]) => {
    const t = a * Math.PI / 180, d = 0.36;
    s.addShape(pres.shapes.OVAL, { x: dx + r * Math.cos(t) - d / 2, y: dy + r * Math.sin(t) - d / 2, w: d, h: d, fill: { color: f ? C.accent1 : C.accent5 }, line: { color: C.background1, width: 1.5 }, objectName: "test" });
  });
  s.addShape(pres.shapes.OVAL, { x: 8.3, y: 6.38, w: 0.2, h: 0.2, fill: { color: C.accent1 }, line: { type: "none" }, objectName: "legend failed" });
  text(s, "test failed in CI because of the change", { x: 8.6, y: 6.32, w: 3.6, h: 0.32, fontSize: 12, color: C.accent5 });
  s.addShape(pres.shapes.OVAL, { x: 8.3, y: 6.68, w: 0.2, h: 0.2, fill: { color: C.accent5 }, line: { type: "none" }, objectName: "legend passed" });
  text(s, "test unaffected", { x: 8.6, y: 6.62, w: 3.6, h: 0.32, fontSize: 12, color: C.accent5 });
  s.addNotes("Every developer asks this before merging. The 'blast radius' of a change is the set of tests it actually breaks. Three motivations: cost of running full suites; the field's labels don't record failures; and GitHub Actions logs expire after 90 days, which made the harvester the most time-critical part of the project.");

  // 3. Three camps
  s = content("Introduction");
  title(s, "Three research camps, three different labels");
  const camps = [
    ["code", "Change impact analysis", "Co-change mining", "Files edited together in Git history", "Public", "Wrong label: records developer habits, not failures", C.accent6],
    ["sitemap", "Regression test selection", "Ekstazi, STARTS", "Tests that can reach the changed code", "Public tools", "Safe over-approximation, not an observation", C.accent2],
    ["bolt", "Predictive test selection", "Meta, Google", "Tests that actually failed in CI", "Proprietary", "Right label, but no one else can use the data", C.accent6],
  ];
  camps.forEach(([ic, h, ex, label, data, verdict, vc], i) => {
    const x = 0.6 + i * 4.18, y = 1.55, w = 3.85, h2 = 4.0;
    card(s, x, y, w, h2);
    iconCircle(s, ic, x + 0.3, y + 0.3, 0.7, C.text2);
    text(s, h, { x: x + 1.15, y: y + 0.3, w: w - 1.35, h: 0.7, fontSize: 18, bold: true, valign: "middle" });
    text(s, ex, { x: x + 0.3, y: y + 1.15, w: w - 0.6, h: 0.35, fontSize: 13, italic: true, color: C.accent5 });
    text(s, [
      { text: "Label", options: { bold: true, breakLine: true, fontSize: 12, color: C.accent5 } },
      { text: label, options: { breakLine: true } },
      { text: "Data", options: { bold: true, breakLine: true, fontSize: 12, color: C.accent5 } },
      { text: data },
    ], { x: x + 0.3, y: y + 1.6, w: w - 0.6, h: 1.55, fontSize: 15, paraSpaceAfter: 3 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.3, y: y + 3.2, w: w - 0.6, h: 0.6, rectRadius: 0.08, fill: { color: vc }, line: { type: "none" }, objectName: "verdict" });
    text(s, verdict, { x: x + 0.4, y: y + 3.2, w: w - 0.8, h: 0.6, fontSize: 12, bold: true, color: C.background1, valign: "middle" });
  });
  card(s, 0.6, 5.85, 12.13, 0.8, C.text2, "takeaway");
  text(s, [{ text: "BlastRadius: ", options: { bold: true, color: C.accent2 } }, { text: "the right label (tests that actually failed in CI) on public, open-source data.", options: { color: C.background1 } }],
    { x: 0.9, y: 5.85, w: 11.6, h: 0.8, fontSize: 17, valign: "middle" });
  s.addNotes("CIA has public data with the wrong label. RTS tools give principled but over-approximate labels. PTS at Meta and Google uses the right label, but on private monorepos. BlastRadius closes the triangle.");

  // 4. Objectives
  s = content("Introduction");
  title(s, "Objectives and contribution");
  const objs = [
    ["Build BR-Bench", "An execution-grounded dataset linking code changes to the individual tests that failed in GitHub Actions."],
    ["Measure the proxies", "Quantify how far co-change predictions diverge from the tests that actually failed."],
    ["Commit-pinned code graph", "Files, classes, methods and tests with their dependencies, as a substrate for dependency analysis."],
    ["Reproducible by construction", "Deterministic pipeline: every number regenerates from raw logs with one command."],
  ];
  objs.forEach(([h, b], i) => {
    const y = 1.55 + i * 1.28;
    numCircle(s, i + 1, 0.6, y, 0.62);
    text(s, h, { x: 1.45, y: y - 0.02, w: 5.9, h: 0.4, fontSize: 18, bold: true });
    text(s, b, { x: 1.45, y: y + 0.4, w: 5.9, h: 0.75, fontSize: 14, color: C.accent5 });
  });
  card(s, 7.85, 1.55, 4.88, 4.9, C.text2, "claim card");
  iconCircle(s, "target", 8.2, 1.9, 0.7);
  text(s, "What we claim", { x: 9.05, y: 1.9, w: 3.5, h: 0.7, fontSize: 20, bold: true, color: C.background1, valign: "middle" });
  text(s, [
    { text: "The contribution is the dataset and the measurement, not a new prediction model (decision D-02).", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "A predictor that loses to a simple baseline is still a publishable finding.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "Target venue: MSR 2027 Data & Tool Showcase.", options: { color: C.accent2, bold: true } },
  ], { x: 8.2, y: 2.85, w: 4.2, h: 3.3, fontSize: 15, color: C.background1 });
  s.addNotes("Four objectives. Emphasise the claim discipline: we claim the dataset and the measurement, not state-of-the-art prediction. That keeps every claim fully supported by the data.");

  // 5. Literature survey
  pres.addSection({ title: "Background" });
  s = content("Background");
  title(s, "Literature survey: the seven approved papers");
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
  const lit = [
    ["Borg et al., IEEE TSE 2017", "Recommendation-based impact analysis in one industrial, safety-critical system", "Proprietary single system; ground truth from change requests, not CI"],
    ["Huang et al., IEEE TSE 2022", "Change-pattern mining (co-change labels)", "Predicts what changes together, not which tests fail"],
    ["Dai et al., Computer Comm. 2022", "Improved static impact analysis for C programs", "Static only; no validation against execution"],
    ["Zhao et al., JSME 2002", "Architectural slicing; component-level impact", "Architecture-level and analytical"],
    ["Angerer et al., ICSME 2016", "Modular impact analysis for configurable software", "Configuration space; an orthogonal problem"],
    ["Zhang et al., ICSM 2008", "Atomic-change impact analysis for AspectJ", "Taxonomy only; not validated against execution"],
    ["Gupta & Gupta, IJSSOE 2015", "Computes and ranks impacted functions", "Small examples; ranks functions, not tests"],
  ];
  const litRows = [[hdr("Paper"), hdr("What it does"), hdr("Gap BlastRadius addresses")]].concat(
    lit.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: j === 0, fill: { color: i % 2 ? C.background1 : C.background2 } } }))));
  s.addTable(litRows, { x: 0.6, y: 1.45, w: 12.13, colW: [3.0, 4.6, 4.53], fontSize: 13, color: C.text1, rowH: 0.52, valign: "middle", margin: [0.04, 0.12, 0.04, 0.12], border: { type: "none" } });
  card(s, 0.6, 5.9, 12.13, 0.7, C.background2, "synthesis");
  iconCircle(s, "search", 0.78, 5.98, 0.54);
  text(s, "None of the seven validates its impact set against the tests that actually failed in a real CI pipeline, because no public dataset made that possible.", { x: 1.5, y: 5.9, w: 11.0, h: 0.7, fontSize: 15, bold: true, valign: "middle" });
  s.addNotes("These are the seven references approved at the Zeroth Review. The common gap: none is validated against observed CI test failures. Huang et al.'s co-change label is exactly the kind of proxy our RQ1 measures.");

  // 6. Closest work matrix
  s = content("Background");
  title(s, "Closest work, and what BR-Bench adds");
  const Y = { text: "✓", options: { color: C.accent4, bold: true, align: "center", fontSize: 18 } };
  const N = { text: "✗", options: { color: C.accent6, bold: true, align: "center", fontSize: 18 } };
  const P = (t) => ({ text: t, options: { color: C.accent5, align: "center", fontSize: 12, italic: true } });
  const mh = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: "center", fontSize: 13 } });
  const mat = [
    ["Co-change impact analysis", N, Y, N, Y],
    ["RTS tools (Ekstazi, STARTS)", P("reachability"), Y, Y, Y],
    ["Predictive test selection (Meta 2019, Google 2017)", Y, N, Y, Y],
    ["RTPTorrent (MSR 2020)", Y, Y, Y, P("Travis build jobs, no PR diff")],
    ["GHALogs (MSR 2025)", P("raw logs only"), Y, N, N],
  ];
  const matRows = [[{ text: "Work", options: { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 13 } }, mh("Label = observed CI failure"), mh("Public data"), mh("Per-test verdicts"), mh("Linked to the PR diff")]]
    .concat(mat.map((r, i) => r.map((c, j) => j === 0 ? { text: c, options: { fill: { color: i % 2 ? C.background1 : C.background2 } } } : { text: c.text, options: Object.assign({}, c.options, { fill: { color: i % 2 ? C.background1 : C.background2 } }) })))
    .concat([[{ text: "BR-Bench (ours)", options: { bold: true, color: C.background1, fill: { color: C.accent1 } } }].concat([0, 1, 2, 3].map(() => ({ text: "✓", options: { bold: true, color: C.background1, fill: { color: C.accent1 }, align: "center", fontSize: 18 } })))]);
  s.addTable(matRows, { x: 0.6, y: 1.45, w: 12.13, colW: [4.33, 2.0, 1.8, 1.8, 2.2], fontSize: 14, color: C.text1, rowH: 0.56, valign: "middle", margin: [0.04, 0.12, 0.04, 0.12], border: { type: "none" } });
  card(s, 0.6, 5.65, 12.13, 0.95, C.background2, "advantage");
  iconCircle(s, "shield", 0.8, 5.83, 0.6);
  text(s, [{ text: "What only BR-Bench does: ", options: { bold: true } }, { text: "it resolves a base run for every change and removes pre-existing and flaky failures, so a label means \"this change broke this test\"." }],
    { x: 1.6, y: 5.65, w: 10.9, h: 0.95, fontSize: 15, valign: "middle" });
  s.addNotes("This is the 'advantage over others' slide. RTPTorrent has test outcomes but on Travis CI, organised by build job rather than PR with a diff. GHALogs is a large raw-log corpus but stops at the log: no per-test verdicts, no diff link, no de-flaking. Meta and Google have the right label on private data.");

  // 7. RQs and scope
  s = content("Background");
  title(s, "Research questions and scope");
  const rqs = [
    ["RQ1", "How far do co-change predictions diverge from the tests that actually failed?", "Answered", C.accent4],
    ["RQ4", "What does the dataset contain, and how reliably was it labelled?", "Answered", C.accent4],
    ["RQ2", "Which change characteristics predict that divergence?", "Future work", C.accent5],
    ["RQ3", "Can a model trained on execution outcomes beat the proxies?", "Future work", C.accent5],
  ];
  rqs.forEach(([k, q, st, col], i) => {
    const x = 0.6 + (i % 2) * 6.17, y = 1.55 + Math.floor(i / 2) * 1.95, w = 5.96;
    card(s, x, y, w, 1.75);
    text(s, k, { x: x + 0.3, y: y + 0.25, w: 1.2, h: 0.5, fontSize: 24, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
    pill(s, st, x + w - 1.75, y + 0.3, 1.45, col);
    text(s, q, { x: x + 0.3, y: y + 0.8, w: w - 0.6, h: 0.8, fontSize: 16 });
  });
  const chips = ["Java + Python only (D-03)", "No LLM anywhere in the pipeline (D-17)", "Graph layer is a course deliverable, outside the paper (D-48)"];
  let cxp = 0.6; const chipW = [2.6, 3.7, 5.33];
  chips.forEach((c, ci) => {
    const w = chipW[ci];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cxp, y: 5.6, w, h: 0.5, rectRadius: 0.25, fill: { color: C.background1 }, line: { color: C.text2, width: 1 }, objectName: "scope chip" });
    text(s, c, { x: cxp, y: 5.6, w, h: 0.5, fontSize: 13, align: "center", valign: "middle" });
    cxp += w + 0.25;
  });
  s.addNotes("RQ1 and RQ4 are answered in this project and in the paper. RQ2 and RQ3 are future work: the learned predictor was deliberately cut. In the paper RQ1 compares co-change with fault-revelation; static reachability depends on the graph layer, which stays outside the paper (D-48).");

  // 8. Architecture
  pres.addSection({ title: "Design" });
  s = content("Design");
  title(s, "System architecture");
  const boxes = [
    ["SEART frame", "300 candidate repositories"], ["Harvester", "rate-limited, resumable"], ["Raw store", "immutable CI logs"], ["Parsers", "Gradle · Maven · pytest"],
    ["test_id normaliser", "one canonical join key"], ["Labelling engine", "base run · T_reveal · flakiness"], ["Binding", "test → file at pinned commit"], ["make tables + release", "BR-Bench on Zenodo"],
  ];
  const bx = [0.6, 3.75, 6.9, 10.05], bw = 2.68, bh = 1.1, ry = [1.5, 3.2];
  boxes.forEach(([h, b], i) => {
    const row = i < 4 ? 0 : 1, col = row === 0 ? i : 7 - i;
    const x = bx[col], y = ry[row];
    const dark = i === 5 || i === 7;
    card(s, x, y, bw, bh, dark ? C.text2 : C.background2, "stage " + (i + 1));
    numCircle(s, i + 1, x + 0.15, y + 0.15, 0.42, C.accent1);
    text(s, h, { x: x + 0.68, y: y + 0.12, w: bw - 0.8, h: 0.45, fontSize: 15, bold: true, valign: "middle", color: dark ? C.background1 : C.text1 });
    text(s, b, { x: x + 0.2, y: y + 0.62, w: bw - 0.35, h: 0.4, fontSize: 12, color: dark ? C.background2 : C.accent5 });
  });
  for (let c = 0; c < 3; c++) arrow(s, bx[c] + bw + 0.05, ry[0] + bh / 2, bx[c + 1] - 0.05, ry[0] + bh / 2);
  arrow(s, bx[3] + bw / 2, ry[0] + bh + 0.05, bx[3] + bw / 2, ry[1] - 0.05);
  for (let c = 3; c > 0; c--) arrow(s, bx[c] - 0.05, ry[1] + bh / 2, bx[c - 1] + bw + 0.05, ry[1] + bh / 2);
  // graph layer branch from binding (col 1 row 2)
  arrow(s, bx[1] + bw / 2, ry[1] + bh + 0.05, bx[1] + bw / 2, 4.85 - 0.05, C.accent3);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx[1], y: 4.85, w: 9.0, h: 0.9, rectRadius: 0.1, fill: { color: C.background1 }, line: { color: C.accent3, width: 1.5, dashType: "dash" }, objectName: "graph layer outline" });
  text(s, [{ text: "Graph layer  ", options: { bold: true, color: C.accent3 } }, { text: "commit-pinned code graphs · test nodes bound to test_id · 5-primitive query API" }],
    { x: bx[1] + 0.25, y: 4.85, w: 8.6, h: 0.9, fontSize: 14, valign: "middle" });
  text(s, "Python 3.11 · uv · DuckDB + Parquet · tree-sitter · NetworkX · pytest · Streamlit · Next.js", { x: 0.6, y: 6.2, w: 12.13, h: 0.4, fontSize: 13, color: C.accent5, align: "center" });
  s.addNotes("Follow the numbers: frame, harvest, raw store, parse, normalise test IDs, label, bind, then regenerate tables and build the release. The graph layer branches off binding and runs on the three-repository mini-corpus. Storage is DuckDB + Parquet with no server (D-06).");

  // 9. Harvester
  s = content("Design");
  title(s, "Harvester: racing the 90-day log expiry");
  const hv = [
    ["github", "Sampling frame from SEART: 300 repositories, 150 Java and 150 Python."],
    ["gauge", "3 tokens × 5,000 requests/hour. Every request goes through one function, get_with_backoff(): quota, Retry-After, backoff, resumable cursors."],
    ["hourglass", "Logs expire after 90 days, so capture ran continuously for about 61 days, until 29 Aug 2026."],
    ["db", "77 repositories captured (71 Java, 6 Python) into an immutable raw store."],
  ];
  hv.forEach(([ic, t], i) => {
    const y = 1.55 + i * 1.22;
    iconCircle(s, ic, 0.6, y, 0.62);
    text(s, t, { x: 1.4, y: y - 0.03, w: 4.75, h: 1.1, fontSize: 15 });
  });
  const iw = 6.35, ih = iw * 892 / 1917;
  s.addImage({ path: "dash.png", x: 6.38, y: 1.7, w: iw, h: ih, altText: "Streamlit corpus dashboard showing 77 of 300 repositories touched", shadow: { type: "outer", blur: 6, offset: 2, angle: 90, color: "000000", opacity: 0.25 } });
  text(s, "Live corpus dashboard (Streamlit): 300,565 of 302,245 capture units complete (99.4%), 0 join mismatches.", { x: 6.38, y: 1.8 + ih + 0.1, w: iw, h: 0.6, fontSize: 12, color: C.accent5, italic: true });
  s.addNotes("The only immovable deadline in the project was log expiry. The harvester stores raw API responses immutably so everything downstream can be rebuilt. The dashboard shows frame coverage: 77 of 300 repositories, 71 Java and 6 Python, which is why the corpus is Java-heavy (a stated limitation).");

  // 10. Parsing & test_id
  s = content("Design");
  title(s, "From raw CI logs to per-test outcomes");
  const steps10 = [
    ["file", "Raw job log", "Strip ANSI codes and timestamps, handle ::group:: blocks and interleaved parallel output."],
    ["list", "Parsed outcome", "One record per test: name, verdict, failure message. Parsers for Gradle, Maven and pytest."],
    ["finger", "Canonical test_id", "One normaliser (NFKC + casefold, Class#method). The project-wide join key, contract-tested on every merge."],
  ];
  steps10.forEach(([ic, h, b], i) => {
    const x = 0.6 + i * 4.18, w = 3.77;
    card(s, x, 1.55, w, 2.9);
    iconCircle(s, ic, x + 0.3, 1.8, 0.7, C.text2);
    text(s, h, { x: x + 1.15, y: 1.8, w: w - 1.3, h: 0.7, fontSize: 18, bold: true, valign: "middle" });
    text(s, b, { x: x + 0.3, y: 2.7, w: w - 0.6, h: 1.6, fontSize: 14, color: C.accent5 });
    if (i < 2) arrow(s, x + w + 0.05, 3.0, x + 4.18 - 0.05, 3.0, C.accent1);
  });
  text(s, "Parser precision (development sets)", { x: 0.6, y: 4.8, w: 6, h: 0.4, fontSize: 16, bold: true });
  [["46/46", "fixture corpus"], ["30/30", "holdout v1"]].forEach(([v, l], i) => {
    const x = 0.6 + i * 3.1;
    text(s, v, { x, y: 5.25, w: 2.8, h: 0.75, fontSize: 36, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
    text(s, l, { x, y: 6.0, w: 2.8, h: 0.35, fontSize: 13, color: C.accent5 });
  });
  card(s, 6.85, 4.85, 5.88, 1.6, C.background2, "precision caveat");
  iconCircle(s, "exclam", 7.05, 5.05, 0.55, C.accent2);
  text(s, "Both sets were used during development. The blind holdout (v5, 40 logs) is not yet scored, so independent precision is not claimed (D-53).", { x: 7.8, y: 4.95, w: 4.75, h: 1.4, fontSize: 14, valign: "middle" });
  s.addNotes("Parsing turns messy CI text into per-test verdicts. The normaliser is the single source of test identity: if two parsers spelled the same test differently, every join downstream would silently break. Be precise about precision: 46/46 and 30/30 are on development data; we do not claim independent precision until the blind holdout is scored.");

  // 11. Labelling
  s = content("Design");
  title(s, "Fault-revealing labels: base-run resolution");
  card(s, 0.6, 1.5, 12.13, 1.05, C.text2, "equation");
  text(s, [
    { text: "T", options: { bold: true } }, { text: "reveal", options: { subscript: true } },
    { text: "  =  T" }, { text: "head_fail", options: { subscript: true } },
    { text: "  −  T" }, { text: "base_fail", options: { subscript: true } },
    { text: "  −  T" }, { text: "flaky", options: { subscript: true } },
  ], { x: 0.9, y: 1.5, w: 7.5, h: 1.05, fontSize: 26, color: C.background1, fontFace: THEME.headFontFace, valign: "middle" });
  text(s, "failed at head, not at base, and never flipped on the same commit", { x: 8.0, y: 1.5, w: 4.5, h: 1.05, fontSize: 14, color: C.accent2, valign: "middle", italic: true });
  const steps11 = [
    "Find the tests failing at the head commit",
    "Base run = latest run of the same workflow at the base commit; else walk back up to 10 ancestors",
    "No base found → status no_base, emit no labels",
    "Subtract base failures, then remove same-commit flips",
  ];
  steps11.forEach((t, i) => {
    const x = 0.6 + i * 3.08, w = 2.85;
    card(s, x, 2.95, w, 1.9);
    numCircle(s, i + 1, x + 0.2, 3.12, 0.5, i === 2 ? C.accent6 : C.accent1);
    text(s, t, { x: x + 0.2, y: 3.75, w: w - 0.4, h: 1.05, fontSize: 14 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.2, w: 12.13, h: 1.3, rectRadius: 0.1, fill: { color: C.background1 }, line: { color: C.accent6, width: 1.5 }, objectName: "invariant outline" });
  iconCircle(s, "exclam", 0.85, 5.48, 0.72, C.accent6);
  text(s, [{ text: "Critical invariant: ", options: { bold: true, color: C.accent6 } }, { text: "an empty base failure set is never read as \"the base was green\". Otherwise every failure at head would become a fault-revealing label, manufacturing false positives at scale." }],
    { x: 1.8, y: 5.2, w: 10.7, h: 1.3, fontSize: 15, valign: "middle" });
  s.addNotes("This is the hardest correctness problem in the project. A failure at head only counts if the same test did not already fail at base. If we cannot find a base run, we emit nothing: 5,520 of 12,581 failed runs (43.88%) are no_base and contribute no labels. Edge cases if asked: a cancelled or timed-out head run is excluded; a test that exists at head but not at base is a new test, never fault-revealing; a test at base but not at head is excluded; matrix builds take the union of failures across legs (D-12); a base found by walking back ancestors is kept with base_run_distance recorded. Splits: all 897, relaxed 770, strict 762 instances.");

  // 13. Binding
  s = content("Design");
  title(s, "Binding each test to its file");
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Binding", labels: ["Full confidence (qualified class)", "Basename only (0.5 confidence)", "Ambiguous", "Not found"], values: [3820, 1823, 164, 178] }], Object.assign({
    x: 0.5, y: 1.4, w: 6.0, h: 5.2, holeSize: 55, chartColors: [H.accent4, H.accent2, H.accent5, H.accent6],
    showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: H.dk1, showPercent: true, showValue: false, dataLabelColor: H.lt1, dataLabelFontSize: 12,
    showTitle: true, title: "5,985 bound test IDs", titleFontSize: 14, titleColor: H.dk1,
  }, chartText, { dataLabelColor: H.lt1 }));
  const bind = [["94.29%", "combined (5,643 / 5,985)", "MET", C.accent4], ["63.83%", "full confidence (3,820 / 5,985)", "NOT MET", C.accent6]];
  bind.forEach(([v, l, st, col], i) => {
    const y = 1.6 + i * 1.6;
    text(s, v, { x: 7.0, y, w: 3.0, h: 0.85, fontSize: 40, bold: true, color: col, fontFace: THEME.headFontFace });
    pill(s, st, 10.3, y + 0.25, 1.4, col);
    text(s, l + " · Gate 1.5 needs ≥ 70%", { x: 7.0, y: y + 0.85, w: 5.7, h: 0.4, fontSize: 14, color: C.accent5 });
  });
  card(s, 7.0, 4.95, 5.73, 1.55, C.background2, "binding notes");
  text(s, [
    { text: "Clones are pinned to a fixed commit per repository (D-50), so figures no longer drift as upstream code changes.", options: { breakLine: true } },
    { text: "Both numbers are always reported together (D-47).", options: { bold: true } },
  ], { x: 7.25, y: 5.05, w: 5.3, h: 1.35, fontSize: 14, valign: "middle", paraSpaceAfter: 4 });
  s.addNotes("Binding connects a test ID from a log to a test file in the repository. Full confidence means the fully qualified class name matched; basename-only matches carry 0.5 confidence. Gate 1.5 is met on the combined figure and not met at full confidence; we report both, never just the flattering one.");

  // 14. Graph layer design
  s = content("Design");
  title(s, "Graph layer design");
  const g = [
    ["cut", "Fork & strip", "Graphify vendored at a fixed commit; 12 modules removed (−20,158 / +253 lines), including its LLM pass. 0 test regressions."],
    ["code", "Commit-pinned builder", "Git worktree at a given commit → tree-sitter on .java and .py → compressed node-link JSON keyed by (repo, sha)."],
    ["project", "Test nodes & edges", "Tests bound to test_id. Edges: direct calls, naming convention, mirrored layout. MultiDiGraph keyed by edge type."],
    ["search", "Query API", "5 primitives: shortest path, distance to any changed node, k-hop neighbourhood, same community, PageRank delta."],
  ];
  g.forEach(([ic, h, b], i) => {
    const x = 0.6 + i * 3.08, w = 2.85;
    card(s, x, 1.55, w, 4.2);
    iconCircle(s, ic, x + 0.25, 1.8, 0.75, C.accent3);
    text(s, h, { x: x + 0.25, y: 2.75, w: w - 0.5, h: 0.75, fontSize: 18, bold: true });
    text(s, b, { x: x + 0.25, y: 3.55, w: w - 0.5, h: 2.1, fontSize: 14, color: C.accent5 });
    if (i < 3) arrow(s, x + w + 0.03, 2.17, x + 3.08 - 0.03, 2.17, C.accent3);
  });
  text(s, "Incremental builds reuse a SHA-256 content cache; a blocking test checks the incremental graph equals a cold build exactly.", { x: 0.6, y: 6.0, w: 12.13, h: 0.5, fontSize: 14, italic: true, color: C.accent5 });
  s.addNotes("The graph layer is Prisha's module. We forked an open-source extractor and removed everything non-deterministic, including its LLM pass, so graphs are exactly reproducible. A MultiDiGraph keyed by edge type stops a derived 'tests' edge from overwriting the 'calls' edge it was derived from — a defect the tests caught.");

  // 15. Graph results
  s = content("Design");
  title(s, "Graph layer results (3-repository mini-corpus)");
  text(s, "427 / 427", { x: 0.6, y: 1.5, w: 4.2, h: 1.0, fontSize: 48, bold: true, color: C.accent3, fontFace: THEME.headFontFace });
  text(s, "commit-pinned graphs built, 0 failures", { x: 0.6, y: 2.5, w: 4.2, h: 0.4, fontSize: 15, color: C.accent5 });
  const gr = [["fla-org/flash-linear-attention", "pytest", "107", "47.7"], ["Stirling-Tools/Stirling-PDF", "Gradle", "140", "99.7"], ["spiculedata/saiku", "Maven", "180", "43.5"]];
  const grRows = [[hdr("Repository"), hdr("Build"), hdr("Graphs"), hdr("Query (ms)")]].concat(gr.map((r, i) => r.map((c, j) => ({ text: c, options: { align: j > 1 ? "right" : "left", fill: { color: i % 2 ? C.background1 : C.background2 } } }))));
  s.addTable(grRows, { x: 5.2, y: 1.5, w: 7.53, colW: [3.43, 1.2, 1.2, 1.7], fontSize: 14, color: C.text1, rowH: 0.5, valign: "middle", margin: [0.04, 0.12, 0.04, 0.12], border: { type: "none" } });
  const bud = [["Query latency ≤ 100 ms", "47.7 / 99.7 / 43.5 ms", "MET", C.accent4], ["Incremental build ≤ 10 s", "25–29 s", "NOT MET", C.accent6], ["Cold build ≤ 10 min", "mini-corpus only", "PARTIAL", C.accent2]];
  bud.forEach(([k, v, st, col], i) => {
    const x = 0.6 + i * 4.18, w = 3.85;
    card(s, x, 3.75, w, 1.55);
    text(s, k, { x: x + 0.25, y: 3.9, w: w - 0.5, h: 0.4, fontSize: 15, bold: true });
    text(s, v, { x: x + 0.25, y: 4.4, w: w - 1.9, h: 0.7, fontSize: 15, color: C.accent5, valign: "middle" });
    pill(s, st, x + w - 1.6, 4.58, 1.35, col);
  });
  card(s, 0.6, 5.55, 12.13, 1.0, C.background2, "defect");
  iconCircle(s, "bug", 0.8, 5.72, 0.62, C.accent6);
  text(s, "Caught by the equivalence test: splicing a re-extracted subgraph diverged on 4/4 commit transitions (Java import resolution saw only the re-extracted files). Fix: pass the full file list; take incrementality from the cache.",
    { x: 1.6, y: 5.55, w: 10.95, h: 1.0, fontSize: 14, valign: "middle" });
  s.addNotes("Results are on the three-repository mini-corpus and are a course deliverable, not part of the paper (D-48). Be honest about the budgets: query latency is met (99.7 ms is right at the limit), incremental build is not met, cold build is only shown on the mini-corpus.");

  // 16. Reproducibility & guards
  pres.addSection({ title: "Implementation quality" });
  s = content("Implementation quality");
  title(s, "Reproducible by construction");
  text(s, "make tables", { x: 0.6, y: 1.5, w: 4.4, h: 0.5, fontSize: 18, bold: true, fontFace: "Courier New", color: C.accent1 });
  text(s, "Regenerates every reported number offline from raw logs in about 8 minutes. Each output file is stamped with the script and git commit that produced it.", { x: 0.6, y: 2.05, w: 4.4, h: 1.4, fontSize: 15 });
  text(s, "821", { x: 0.6, y: 3.6, w: 2.0, h: 0.9, fontSize: 44, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
  text(s, "tests passing (3 skipped), against real checked-in fixtures, no mocks", { x: 2.4, y: 3.7, w: 2.6, h: 0.9, fontSize: 13, color: C.accent5, valign: "middle" });
  const guards = [
    ["robot", "No LLM in the pipeline", "Harvest, parse, label and every number come from deterministic code (D-17)."],
    ["wifi", "Offline guard", "BR_OFFLINE=1: any network call during make tables raises an error."],
    ["history", "Freshness guard", "make tables refuses to run if a derived file is older than its inputs."],
    ["clone", "Complete-clone guard", "Rejects partial clones before binding runs."],
    ["tag", "Pinned commits", "Binding runs against a fixed commit per repository."],
    ["key", "Release-key check", "The release build refuses to run without the pseudonymisation key."],
  ];
  guards.forEach(([ic, h, b], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 5.45 + col * 3.7, y = 1.5 + row * 1.55, w = 3.48;
    card(s, x, y, w, 1.38);
    iconCircle(s, ic, x + 0.18, y + 0.2, 0.55, C.text2);
    text(s, h, { x: x + 0.88, y: y + 0.18, w: w - 1.0, h: 0.55, fontSize: 15, bold: true, valign: "middle" });
    text(s, b, { x: x + 0.18, y: y + 0.8, w: w - 0.3, h: 0.55, fontSize: 12, color: C.accent5 });
  });
  text(s, "Development method: an architect → operator → agent loop; every change was scoped, tested and verified by the team before it was committed.", { x: 0.6, y: 6.25, w: 12.13, h: 0.5, fontSize: 12, italic: true, color: C.accent5 });
  s.addNotes("If a number cannot be regenerated by a script, it does not go in the report or the paper. The guards exist because each one corresponds to a real silent failure we hit (next slides). Be open about the development method if asked: an AI coding assistant was used for implementation, with no AI anywhere in the data pipeline, and every change was verified by us.");

  // 17. Funnel
  pres.addSection({ title: "Results" });
  s = content("Results");
  title(s, "From 165,349 CI runs to 762 benchmark instances");
  const fl = ["Runs discovered", "Failed runs", "Failed-job log on disk", "Parsed head test failure", "Resolved base run", "Known base failure set", "≥ 1 strict label"];
  const fv = [165349, 12581, 6586, 1774, 1348, 897, 762];
  s.addChart(pres.charts.BAR, [{ name: "Runs", labels: fl.slice().reverse(), values: fv.slice().reverse() }], Object.assign({
    x: 0.6, y: 1.4, w: 12.13, h: 4.9, barDir: "bar", chartColors: [H.accent1], valAxisLogScaleBase: 10, valAxisMinVal: 100,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", valAxisLabelFormatCode: "#,##0", valGridLine: { color: "E3E5EA", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: false, barGapWidthPct: 45, valAxisHidden: true,
  }, chartText, { catAxisLabelFontSize: 13 }));
  text(s, "Each stage is the intersection with the previous one. Log scale. Source: paper/generated/attrition_funnel.md", { x: 0.6, y: 6.35, w: 12.13, h: 0.35, fontSize: 12, italic: true, color: C.accent5 });
  s.addNotes("Read top to bottom. The biggest losses: only 12,581 runs failed; logs for many failed jobs were not on disk; parsing a head test failure; and base resolution. 762 instances survive with at least one strict label. Every number here comes from attrition_funnel.md.");

  // 18. Dataset & gates
  s = content("Results");
  title(s, "The dataset, and the gates we set ourselves");
  [["762", "instances"], ["4,168", "fault-revealing labels"], ["2,466", "distinct tests"]].forEach(([v, l], i) => {
    const x = 0.6 + i * 4.18, w = 3.85;
    card(s, x, 1.5, w, 1.75);
    text(s, v, { x: x + 0.3, y: 1.62, w: w - 0.6, h: 1.0, fontSize: 48, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
    text(s, l + " (strict split)", { x: x + 0.3, y: 2.62, w: w - 0.6, h: 0.45, fontSize: 15, color: C.accent5 });
  });
  const gates = [
    ["Gate 1 · strict labels ≥ 5,000", "4,168 / 5,000 (83.36%)", "NOT MET", C.accent6],
    ["Gate 1 · strict instances ≥ 5,000", "762 / 5,000 (15.24%)", "NOT MET", C.accent6],
    ["Gate 1.5 · combined binding ≥ 70%", "5,643 / 5,985 (94.29%)", "MET", C.accent4],
    ["Gate 1.5 · full-confidence binding ≥ 70%", "3,820 / 5,985 (63.83%)", "NOT MET", C.accent6],
    ["Gate 3 · model beats best baseline", "model not built (RQ3 is future work)", "N/A", C.accent5],
  ];
  gates.forEach(([k, v, st, col], i) => {
    const y = 3.55 + i * 0.6;
    if (i % 2 === 0) s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 12.13, h: 0.56, fill: { color: C.background2 }, line: { type: "none" }, objectName: "row band" });
    text(s, k, { x: 0.8, y, w: 5.6, h: 0.56, fontSize: 15, bold: true, valign: "middle" });
    text(s, v, { x: 6.4, y, w: 4.3, h: 0.56, fontSize: 15, valign: "middle" });
    pill(s, st, 11.1, y + 0.11, 1.45, col);
  });
  s.addNotes("Gates were set in the roadmap before results existed. We missed Gate 1 and say so; the dataset is still the first of its kind. Gate 2 (a solid RQ1 result) is the next slide.");

  // 19. RQ1
  s = content("Results");
  title(s, "RQ1: predictors versus the tests that actually failed");
  s.addChart(pres.charts.BAR, [{ name: "Mean recall at k = 10", labels: ["Co-change (all partner files)", "Co-change (test files only)", "Changeset baseline", "Historical failure frequency"], values: [0.051, 0.087, 0.245, 0.517] }], Object.assign({
    x: 0.5, y: 1.4, w: 6.6, h: 4.6, barDir: "col", chartColors: [H.accent3, H.accent3, H.accent5, H.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000", valAxisMinVal: 0, valAxisMaxVal: 0.6, valAxisLabelFormatCode: "0.0",
    valGridLine: { color: "E3E5EA", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 60,
    showTitle: true, title: "Mean recall at k = 10 (n = 576 instances)", titleFontSize: 14, titleColor: H.dk1,
  }, chartText));
  card(s, 7.4, 1.5, 5.33, 2.25, C.text2, "finding");
  text(s, [
    { text: "Of 1,316 tests that actually failed:", options: { breakLine: true, color: C.background2 } },
    { text: "co-change predicted 61 (4.64%)", options: { breakLine: true, bold: true, color: C.background1 } },
    { text: "historical frequency predicted 519 (39.44%)", options: { bold: true, color: C.accent2 } },
  ], { x: 7.7, y: 1.6, w: 4.85, h: 2.05, fontSize: 17, valign: "middle", paraSpaceAfter: 6 });
  const pr = [["Method", "P", "R", "J"], ["Co-change, all", ".011", ".051", ".010"], ["Co-change, test files", ".054", ".087", ".038"], ["Changeset", ".039", ".245", ".037"], ["Historical frequency", ".185", ".517", ".178"]];
  s.addTable(pr.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 }, align: j ? "right" : "left" } : { align: j ? "right" : "left", bold: i === 4, fill: { color: i % 2 ? C.background2 : C.background1 } } }))),
    { x: 7.4, y: 3.95, w: 5.33, colW: [2.63, 0.9, 0.9, 0.9], fontSize: 13, color: C.text1, rowH: 0.38, valign: "middle", margin: [0.03, 0.12, 0.03, 0.12], border: { type: "none" } });
  text(s, "Co-change is trailing and symmetric; the leakage audit went from 640/713 leaking instances to 0/713.", { x: 0.6, y: 6.2, w: 12.13, h: 0.4, fontSize: 13, italic: true, color: C.accent5 });
  s.addNotes("This is the headline finding. The co-change proxy the field uses recovered under 5% of the tests that actually failed; simply ranking tests by how often they failed before recovered about 39%. P, R, J are mean precision, recall and Jaccard at k = 10 on the same 576 instances. We fixed a leakage bug before trusting these numbers: the old co-change table used future commits for 640 of 713 instances.");

  // 20. Data quality
  s = content("Results");
  title(s, "What the labels look like");
  s.addChart(pres.charts.BAR, [{ name: "Strict labels", labels: ["Unknown", "Code-level", "Timeout", "Environment"], values: [3238, 729, 112, 89] }], Object.assign({
    x: 0.5, y: 1.4, w: 6.6, h: 4.6, barDir: "bar", chartColors: [H.accent5, H.accent1, H.accent2, H.accent3],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", valAxisMinVal: 0, valAxisMaxVal: 4000, valAxisHidden: true,
    valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 45,
    showTitle: true, title: "Failure class of the 4,168 strict labels", titleFontSize: 14, titleColor: H.dk1,
  }, chartText, { catAxisLabelFontSize: 13 }));
  const dq = [
    ["43.88%", "of failed runs had no resolvable base (5,520 / 12,581) and emit no labels"],
    ["0.54%", "same-commit test flips (62 / 11,557), removed from labels as flaky"],
    ["77.69%", "of labels are unclassified: the regex classifier is a lower bound, and nothing is removed"],
  ];
  dq.forEach(([v, l], i) => {
    const y = 1.5 + i * 1.65;
    card(s, 7.4, y, 5.33, 1.45);
    text(s, v, { x: 7.65, y: y + 0.12, w: 4.9, h: 0.65, fontSize: 30, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
    text(s, l, { x: 7.65, y: y + 0.78, w: 4.9, h: 0.6, fontSize: 13, color: C.accent5 });
  });
  s.addNotes("Class counts are from a regex on the failure message, so environment and timeout are lower bounds; 729 labels are clearly code-level. Environment and timeout labels stay in the strict set and are reported, not silently dropped. Base distance is usually zero: most bases are the exact base commit.");

  // 21. Silent failures
  s = content("Results");
  title(s, "Silent failures we caught, and the guard each one left");
  const sf = [
    ["history", "Stale labels", "Labels were never regenerated after a re-parse. Everything was rebuilt from raw logs (D-49); a freshness guard now blocks it."],
    ["bug", "Parameter types read as classes", "JUnit 5 parameterised tests mis-parsed: 21 test IDs (60 rows) corrected one-to-one."],
    ["history", "Co-change leakage", "Future commits leaked into 640/713 instances. Now trailing and per-instance: 0/713."],
    ["user", "Live logins in a bundle", "A first local release kept real usernames. It was never published; the build now requires the key."],
    ["clone", "Partial clone", "An interrupted clone resolved to our own repository. A complete-clone guard rejects it."],
    ["wifi", "Network inside make tables", "A table script called the API. Offline mode now raises on any request."],
  ];
  sf.forEach(([ic, h, b], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.6 + col * 4.18, y = 1.5 + row * 2.55, w = 3.85;
    card(s, x, y, w, 2.35);
    iconCircle(s, ic, x + 0.25, y + 0.25, 0.6, C.accent6);
    text(s, h, { x: x + 1.0, y: y + 0.25, w: w - 1.15, h: 0.6, fontSize: 16, bold: true, valign: "middle" });
    text(s, b, { x: x + 0.25, y: y + 1.0, w: w - 0.5, h: 1.25, fontSize: 13, color: C.accent5 });
  });
  s.addNotes("None of these raised an exception. Each was found by an explicit check, and each now has a permanent guard. This is the project's core engineering lesson: no crash is not proof that a run worked.");

  // NEW. Agentic workflow
  s = content("Results");
  title(s, "Agentic workflow: from user story to deployment");
  const ag = [
    ["search", "Impact Analysis", "user story + codebase", "impact analysis document"],
    ["code", "Coding", "impact analysis + codebase", "changed files + pull request"],
    ["eye", "PR Reviewer", "PR + impact analysis", "review, merge, commit id"],
    ["rocket", "Build & Deploy", "commit id + branch", "build, deploy, or notify on failure"],
    ["clip", "Regression Suite", "impact analysis + suite", "test report"],
  ];
  ag.forEach(([ic, h, i1, o1], i) => {
    const x = 0.6 + i * 2.47, w = 2.22;
    card(s, x, 1.45, w, 2.55);
    iconCircle(s, ic, x + 0.2, 1.62, 0.6, C.accent1);
    text(s, h, { x: x + 0.2, y: 2.3, w: w - 0.3, h: 0.45, fontSize: 15, bold: true });
    text(s, [{ text: "in: ", options: { bold: true, color: C.accent5 } }, { text: i1, options: { breakLine: true } }, { text: "out: ", options: { bold: true, color: C.accent5 } }, { text: o1 }],
      { x: x + 0.2, y: 2.78, w: w - 0.3, h: 1.15, fontSize: 12, paraSpaceAfter: 3 });
    if (i < 4) arrow(s, x + w + 0.03, 2.72, x + 2.47 - 0.03, 2.72, C.accent1);
  });
  text(s, "Demo story: \"As a shopper, I want to apply the discount code FESTIVE20 at checkout to get 20% off my cart total, capped at Rs 500\" on a 15-test sample library", { x: 0.6, y: 4.15, w: 12.13, h: 0.4, fontSize: 13, italic: true, color: C.accent5 });
  const scen = [
    ["Clean change", "7 of 15 tests at risk; reviewer approves and merges; build passes and deploys; regression 18/18 pass", "DEPLOYED", C.accent4],
    ["Out-of-scope change", "The change also rewrites receipts; the scope check fails, so the reviewer requests changes", "BLOCKED", C.accent2],
    ["Reviewer in warn mode", "It merges; the build fails on 2 receipt tests; notification sent; impact recall 0/2", "NOTIFIED", C.accent6],
  ];
  scen.forEach(([h, b, st, col], i) => {
    const x = 0.6 + i * 4.18, w = 3.85;
    card(s, x, 4.7, w, 1.85);
    text(s, h, { x: x + 0.25, y: 4.85, w: w - 1.9, h: 0.45, fontSize: 15, bold: true, valign: "middle" });
    pill(s, st, x + w - 1.6, 4.9, 1.35, col);
    text(s, b, { x: x + 0.25, y: 5.4, w: w - 0.5, h: 1.05, fontSize: 13, color: C.accent5 });
  });
  text(s, "Impact analysis runs on the BlastRadius code graph, on the sample repo or any public GitHub repo (Analyze-a-repo tab). Separate demo path (D-55).", { x: 0.6, y: 6.62, w: 12.13, h: 0.32, fontSize: 11, italic: true, color: C.accent5 });
  s.addNotes("New since the pre-final review: five agents take a user story to a deployed, regression-tested change. The Impact Analysis Agent builds the BlastRadius code graph of the target repository, matches the story to source files, and finds the tests that depend on them by reverse reachability; failure history from earlier regression runs raises a test's risk, because in BR-Bench failure history was the strongest predictor. The Coding Agent writes the change and opens a PR; the Reviewer checks scope, compile and the tests at risk, then merges and returns the commit id; the Build and Deploy Agent builds at that commit and deploys, or sends a notification on failure; the Regression Suite Agent runs the selected scope and the full suite and reports impact recall. Live demo: make agents-demo, then the Agents tab. Offline it uses keyword matching and recorded change sets; with an API key the model writes the code.");

  // 22. Demo
  pres.addSection({ title: "Demonstration and release" });
  s = content("Demonstration and release");
  title(s, "Demonstration");
  const dw = 6.6, dh = dw * 892 / 1917;
  s.addImage({ path: "demo.png", x: 0.6, y: 1.55, w: dw, h: dh, altText: "Next.js demo site replaying one real instance stage by stage", shadow: { type: "outer", blur: 6, offset: 2, angle: 90, color: "000000", opacity: 0.25 } });
  text(s, "Demo site, Live run tab: fla-org/flash-linear-attention PR #935, a code-level failure with 2 fault-revealing tests, replayed stage by stage.", { x: 0.6, y: 1.55 + dh + 0.1, w: 7.6, h: 0.55, fontSize: 12, italic: true, color: C.accent5 });
  const stages = ["The change", "Harvest", "CI log", "Parse", "test_id", "Base run", "Labels", "Binding", "Code graph", "Prediction"];
  text(s, "What the Live run tab walks through, stage by stage", { x: 0.6, y: 5.35, w: 7.6, h: 0.4, fontSize: 15, bold: true });
  stages.forEach((st, i) => {
    const col = i % 5, row = Math.floor(i / 5), cw = 1.42, x = 0.6 + col * (cw + 0.12), y = 5.82 + row * 0.55;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: 0.45, rectRadius: 0.22, fill: { color: C.background2 }, line: { type: "none" }, objectName: "stage chip" });
    text(s, (i + 1) + "  " + st, { x: x + 0.05, y, w: cw - 0.1, h: 0.45, fontSize: 11, align: "center", valign: "middle" });
  });
  const demo = [
    ["make demo-web", "Next.js site on localhost:3000: Live run · Results · Agents · Corpus"],
    ["make agents-demo", "the five agents on a sample repo, three scenarios"],
    ["make demo", "the data pipeline as a terminal walkthrough"],
    ["make tables", "regenerate every number, offline"],
    ["make analyze", "Analyze-a-repo tab: run the impact agent on any public GitHub repo"],
  ];
  demo.forEach(([c, d], i) => {
    const y = 1.5 + i * 1.03;
    numCircle(s, i + 1, 8.6, y + 0.05, 0.5, C.accent1);
    text(s, c, { x: 9.3, y, w: 3.45, h: 0.42, fontSize: 15, bold: true, fontFace: "Courier New" });
    text(s, d, { x: 9.3, y: y + 0.42, w: 3.45, h: 0.7, fontSize: 13, color: C.accent5 });
  });
  s.addNotes("Live demo order: (1) How it works tab, the 10-step pipeline; (2) Live run: walk the instance from the change, through the log line, parsed outcome, test_id, base run, label, binding and graph; (3) Results tab charts; (4) optionally the Streamlit dashboard. The site replays a recorded run, so it works without network; make demo runs the same pipeline live in the terminal.");

  // 23. Release
  s = content("Demonstration and release");
  title(s, "Release: open, archived and citable");
  card(s, 0.6, 1.5, 6.0, 3.15);
  iconCircle(s, "archive", 0.85, 1.72, 0.65, C.text2);
  text(s, "BR-Bench dataset", { x: 1.7, y: 1.72, w: 4.7, h: 0.65, fontSize: 19, bold: true, valign: "middle" });
  text(s, "doi.org/10.5281/zenodo.23250262 · CC BY 4.0", { x: 0.85, y: 2.5, w: 5.6, h: 0.4, fontSize: 14, color: C.accent3, bold: true });
  const rel = [["instances", "165,349"], ["outcomes", "12,766"], ["cochange", "175,204"], ["failure_messages", "3,490"]];
  rel.forEach(([k, v], i) => {
    const y = 3.0 + i * 0.38;
    text(s, k, { x: 0.85, y, w: 3.0, h: 0.36, fontSize: 14, fontFace: "Courier New" });
    text(s, v + " rows", { x: 3.6, y, w: 2.7, h: 0.36, fontSize: 14, align: "right" });
  });
  card(s, 6.85, 1.5, 5.88, 3.15);
  iconCircle(s, "github", 7.1, 1.72, 0.65, C.text2);
  text(s, "Source code", { x: 7.95, y: 1.72, w: 4.6, h: 0.65, fontSize: 19, bold: true, valign: "middle" });
  text(s, "doi.org/10.5281/zenodo.23250690 · MIT", { x: 7.1, y: 2.5, w: 5.4, h: 0.4, fontSize: 14, color: C.accent3, bold: true });
  text(s, [
    { text: "github.com/DeepanshuOP/blastradius", options: { breakLine: true } },
    { text: "release v1.0.0 · CITATION.cff · datasheet", options: { breakLine: true } },
    { text: "v0.2 built and validated (base runs, changeset columns, schema validator); Zenodo deposit pending", options: { color: C.accent5, fontSize: 12 } },
  ], { x: 7.1, y: 3.0, w: 5.4, h: 1.4, fontSize: 14, paraSpaceAfter: 4 });
  const priv = [["user", "Logins pseudonymised (keyed HMAC-SHA256)"], ["shield", "Secret scan and canary string"], ["lock", "SHA-256 checksum manifest"]];
  priv.forEach(([ic, t], i) => {
    const x = 0.6 + i * 4.18;
    iconCircle(s, ic, x, 5.0, 0.55, C.accent4);
    text(s, t, { x: x + 0.7, y: 5.0, w: 3.3, h: 0.55, fontSize: 14, valign: "middle" });
  });
  card(s, 0.6, 5.85, 12.13, 0.75, C.background2, "venue");
  text(s, [{ text: "Next: ", options: { bold: true } }, { text: "MSR 2027 Data & Tool Showcase. Abstract due 5 Nov 2026, paper due 10 Nov 2026." }], { x: 0.85, y: 5.85, w: 11.7, h: 0.75, fontSize: 15, valign: "middle" });
  s.addNotes("Both the dataset and the code are archived on Zenodo with DOIs, which the MSR track requires. The release holds the four tables, not the raw log store. Author logins are pseudonymised with a keyed hash; the key is never committed.");

  // 24. Limitations & future work
  pres.addSection({ title: "Conclusion" });
  s = content("Conclusion");
  title(s, "Limitations and future work");
  const lim = [
    "Gate 1 not met: 4,168 strict labels against a 5,000 target",
    "Full-confidence binding 63.83%, below the 70% gate",
    "Parser precision measured on development sets only",
    "Labels are observational; no re-executed gold subset",
    "Corpus skewed to Java (71 of 77 repositories)",
    "Graph reachability not yet scored against real failures (base commits missing locally)",
  ];
  const fut = [
    "Score the blind holdout (v5) before camera-ready",
    "Learned predictor and GNN to answer RQ3",
    "Fetch base commits and score graph reachability vs real failures",
    "Docker re-execution subset for causal labels",
    "More Python repositories; base runs for non-failing runs",
  ];
  [["Limitations", lim, C.accent6, "exclam"], ["Future work", fut, C.accent4, "road"]].forEach(([h, items, col, ic], k) => {
    const x = 0.6 + k * 6.17, w = 5.96;
    card(s, x, 1.5, w, 5.05);
    iconCircle(s, ic, x + 0.3, 1.75, 0.6, col);
    text(s, h, { x: x + 1.1, y: 1.75, w: w - 1.4, h: 0.6, fontSize: 20, bold: true, valign: "middle" });
    text(s, items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })), { x: x + 0.3, y: 2.65, w: w - 0.6, h: 3.8, fontSize: 16, paraSpaceAfter: 16 });
  });
  s.addNotes("State limitations before the panel asks. Every one of these is also written in the report and the paper. The next concrete step is scoring the blind holdout, which turns parser precision into an independent number.");

  // 25. Conclusion
  s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Conclusion" });
  s.addText("Thank you", { placeholder: "title" });
  s.addText("Questions?", { placeholder: "body" });
  const take = [
    ["BR-Bench is the first public, execution-grounded dataset of which tests a change broke: 762 instances and 4,168 labels on the strict split."],
    ["The proxy the field uses misses most real failures: co-change found 4.64% of failing tests; failure history found 39.44%."],
    ["Every number regenerates offline from raw logs with one command, and data and code are archived with DOIs."],
  ];
  take.forEach(([t], i) => {
    const y = 4.45 + i * 0.72;
    numCircle(s, i + 1, 0.8, y + 0.04, 0.45, C.accent1);
    text(s, t, { x: 1.45, y, w: 11.2, h: 0.62, fontSize: 15, color: C.background1, valign: "middle" });
  });
  text(s, "github.com/DeepanshuOP/blastradius  ·  doi.org/10.5281/zenodo.23250262", { x: 0.8, y: 6.75, w: 11.5, h: 0.35, fontSize: 12, color: C.background2 });
  const cx2 = 11.0, cy2 = 2.1;
  [1.3, 0.85].forEach((r, i) => s.addShape(pres.shapes.OVAL, { x: cx2 - r, y: cy2 - r, w: 2 * r, h: 2 * r, fill: { color: C.accent1, transparency: 85 - i * 5 }, line: { color: C.accent1, width: 1, transparency: 40 }, objectName: "ring" }));
  s.addShape(pres.shapes.OVAL, { x: cx2 - 0.3, y: cy2 - 0.3, w: 0.6, h: 0.6, fill: { color: C.accent1 }, line: { type: "none" }, objectName: "change dot" });
  s.addNotes("Close on the three takeaways: a new public dataset, a clear measurement, and full reproducibility. Then take questions.");

  await pres.writeFile({ fileName: "BlastRadius_Final_Review.pptx" });
  await applyTheme("BlastRadius_Final_Review.pptx", THEME);
  console.log("written");
}
build().catch((e) => { console.error(e); process.exit(1); });
