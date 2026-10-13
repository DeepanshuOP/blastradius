# Style notes for the final BR-Bench paper

Model: papers by T. Radzik and co-authors (King's College London).

## Rules, restated

1. Open every section and the abstract with the object and what it is ("BR-Bench is a dataset of ...", "We define ..."). No scene-setting about CI.
2. "We", present tense ("we collect", "the data show"). Past tense only for one-off events (the harvest of August 2026, the pre-registration).
3. Plain verbs, few adjectives. Banned: novel, robust, comprehensive, crucial, leverage, seamless, state-of-the-art, delve, notably, furthermore, moreover, additionally, underscore, showcase, pivotal. No em dashes (`---`, `—`): use commas, brackets or a full stop. (The track name contains "Showcase", so the body never names the track.)
4. Gloss a term in brackets at first use, then keep that one name: "a same-SHA flip (a test that fails in some, but not all, runs of one workflow on one commit)". Use "that is," / "i.e.," to restate exactly, "say," for a concrete case.
5. Mix one long defining sentence with short flat ones. A semicolon may split a two-part explanation.
6. Notation before use: "Let H be ...", "We write T_reveal for ...". One name per object (strict split, fault-revealing test, base run, the harvester, the labelling engine).
7. Italic run-in paragraph heads (*Base-run resolution.*). The introduction ends with an itemised *Summary of results* pointing to sections and tables.
8. "a/an" at first mention, "the" after; "the" for our artefacts; no article before general plurals.
9. Modest, exact claims: "we observe", "the data suggest", "an upper bound". Negative results stated flatly ("The ranker does not beat the strongest baseline.").
10. Occasional honest hedges ("it seems", "this may").
11. Citations inside the sentence ("as in STARTS [6]", "see Machalica et al. [1]").
12. British spelling (labelling, behaviour, analyse, modelled, licence as noun). Close on open questions, not a grand conclusion.
13. Every sentence written fresh; prior work described in our own structure, never paraphrasing abstracts or the old related-work lines.

## Three draft sentences, rewritten

Old: "Continuous Integration (CI) services execute automated test suites to detect regressions introduced by pull requests."
New: "BR-Bench is a dataset of pull-request runs from GitHub Actions, each linked to the individual tests that the change caused to fail."

Old: "Flaky tests flip their status non-deterministically without code changes~\cite{bell2018deflaker}. We detect same-SHA flips across repeated workflow executions on the exact same commit hash."
New: "A test is flaky if its verdict changes while the code does not, see Bell et al. [7]. We remove every same-SHA flip (a test that fails in some, but not all, runs of one workflow on one commit) from the strict split. Flips are rare."

Old: "Thus, historical failure frequency markedly outperforms version-control co-change heuristics at identifying true regressions."
New: "At k = 10 failure history recalls 519 of the 1,316 fault-revealing test files, and co-change recalls 61. Co-change is a poor label for the tests a change breaks."
