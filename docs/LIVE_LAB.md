# Live Lab, in one page

A demonstration path (D-65): pick a repository, break it, run it, and watch prediction, risk-first execution, triage and
repair happen. Nothing here enters `make tables` or the paper. Every number on screen is **LIVE** (this session), **REPLAY**
(a recording, with its date) or **from BR-Bench** (read from `paper/generated`). Screenshots: `docs/screenshots/lab3/`, 1440×900.

| Feature | What it does | Screenshot |
|---|---|---|
| Start | Three steps: pick a repo (cards with language and file and test counts, plus a GitHub URL card), break it, run. Recordings are small Replay chips. | `01-start` |
| Break it | The code graph is the main element. Click a function, the mutation menu opens with a diff preview. Legend chips filter the graph; node size is the number of tests that reach it. | `02-break-it-graph`, `03-inject-menu-diff-preview`, `12-graph-filters-and-ticker` |
| Challenge | A seeded random function and operator ("Will the tests catch this bug?", the seed is shown). Yes or No, then a live run, then caught or survived, BlastRadius against retest-all, a test-gap card if it survived, and a session tally of correct guesses. No model call unless **Fix it** is pressed. | `16a-challenge-ask`, `16-challenge-caught`, `17-challenge-survived-test-gap`, `18-challenge-fix-it` |
| Scoreboard | Top bar counters for this browser session: bugs injected, caught, caught earlier, test gaps, fixes validated, tokens and $0. They move only when a live run event arrives. | every screen |
| Test race | Two lanes over the same measured durations: retest-all and the BlastRadius order (E1 file rank, then graph hops to the change, then id; D-66). | `05-race` |
| Arena race | One lane per strategy on a shared clock, a flag at each first failure, a podium by time to first failure with cost; the table is behind Details. Orderers and selectors are separate; **Needs** says what each requires. Labelled "computed from this run". | `06-arena-race-podium` |
| History row | Failure history excludes earlier runs of the same diff by default (D-67); the toggle shows both rows, the label says how many earlier runs it used, **Reset history** forgets them. | `06-…` and `07-arena-history-same-diff-included` |
| Triage, Repair, Verdict | Three counters with chips (list in a drawer); context → patch → five checks ticking in as events arrive; a before/after bar. | `08-triage`, `09-repair-flow`, `10-verdict` |
| PR comment | A GitHub-style card, summary open, other sections collapsed. Never posted anywhere. | `11-pr-comment-card` |
| Explain | Top-bar switch, off by default. Every explanation lives behind it or behind an **i** popover. | `13-explain-on` |
| Presenter | One stage per screen, one caption line, "what is real here" in a popover. | `14-presenter-caption-and-popover` |
| Evidence | The four BR-Bench results as cards with a small chart; tables behind "Show table", source line kept. | `15-evidence-cards` |

Event log: a slim ticker at the bottom with a drawer for the full log. Motion plays only when an event arrives and is dropped
under `prefers-reduced-motion`. Checks: `make demo-check` (the tie-break order, the arena columns, the challenge seed and the
text budget of the main screen are among them). Honest limits: recordings made before D-67 hold one history row; the arena
unit is a test case; per-test coverage and co-change are re-implementations, not vendor products.
