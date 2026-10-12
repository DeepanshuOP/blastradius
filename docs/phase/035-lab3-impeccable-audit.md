# Impeccable audits of the Live Lab main screen, before and after Part 2 (2026-10-12)

## Before

Target: demo-web/components/lab/*, demo-web/components/LabApp.tsx, demo-web/app/globals.css (Live Lab main screen).
Context: no PRODUCT.md / DESIGN.md in the repository (scoped audit of existing code, proceeded as the skill directs).
Detector (`impeccable detect --json`): 0 findings.

| # | Dimension | Score | Key finding |
|---|---|---|---|
| 1 | Accessibility | 3 | global 1 ms reduced-motion kill (state changes still land); controls 30 px tall; 22 uses of 11 px text; no h1 on the lab screen |
| 2 | Performance | 3 | full graph rendered by Cytoscape (<=600 nodes streamed), per-test results re-render the panels on every event; no layout thrash found |
| 3 | Theming | 3 | token system in globals.css with a light theme; five hard-coded shadow rgba values in components |
| 4 | Responsive | 3 | drawers replace side panels below the lab breakpoint; controls under 44 px; graph card fixed 340 px |
| 5 | Implementation integrity | 3 | detector clean, one coherent token/type scale; but the main screen is paragraph-heavy (the Part 2 target): every panel carries a multi-line explanation |
| | Total | 15/20 | Good: address weak dimensions |

P2 text density: Empty states, panel captions and the picker carry paragraphs of 2-4 lines (Picker, Panels, Arena, Report, Rail).
P2 reduced motion: `*{animation-duration:1ms}` also removes the ring wave and lane reveal instead of giving a static end state alternative.
P2 touch targets: BTN `min-h-[30px]`.
P3 heading structure: no h1 on the lab surface; panel titles are h3 under a header with no h2.

## After

Target: demo-web/components/lab/*, demo-web/components/LabApp.tsx, demo-web/app/globals.css (Live Lab main screen).
Detector (`impeccable detect --json`): 0 findings (before: 0).
Evidence: production build served on 127.0.0.1:3000, headless Chromium 1440x900 / 1280x800 / 820 / 390 (emulated viewport and
emulated coarse pointer; no physical touch device, no synthesized drag gestures).

| # | Dimension | Before | After | What changed / what is left |
|---|---|---|---|---|
| 1 | Accessibility | 3 | 3 | h1 added, panel titles are h2; the global 1 ms reduced-motion kill is replaced by targeted rules (reveal/pop/wave/ring dropped, end state shown at once, colour changes kept); popovers are buttons with aria-expanded and Esc. Left: 11 px (`text-2xs`) text still used for secondary labels; contrast not re-measured. |
| 2 | Performance | 3 | 3 | unchanged; per-test results still re-render the panels on every event |
| 3 | Theming | 3 | 3 | token system intact; the popover/pill shadows are hard-coded rgba values (now 7) |
| 4 | Responsive | 3 | 3 | FOUND AND FIXED: the document was 826 px wide at a 390 px viewport (absolutely positioned sr-only labels escaped the pipeline rail's overflow container; four containers fixed). Coarse pointers now get 44 px controls and 44 px hit areas on the "i" buttons. Not exercised: real touch gestures. |
| 5 | Implementation integrity | 3 | 4 | text budget met: no visible paragraph over 2 lines and no caption over 14 words, measured in the browser on the idle screen and on every result tab of a replayed run (before: paragraphs of 2-4 lines in Picker, Panels, Arena, Report, Rail); explanations live behind Explain / "i"; presenter captions are one line and generated from the run's numbers |
| | Total | 15/20 | 16/20 | Good |

Defects this pass found in its own work (all fixed before the commit):
- the race caption said "risk-first reaches the first failure sooner" on a recording where it does not (test 8 at 19 ms against test 9 at 4.4 ms); the caption now states both positions;
- the bottom ticker was translucent over the pipeline rail;
- the repo cards truncated the file and test counts at the 340 px panel width.
