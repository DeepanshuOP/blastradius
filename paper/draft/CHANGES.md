# Summary of Changes to Submission Draft

1. Recompacted author affiliation block in `main.tex` to preserve all 4 authors and VIT Vellore affiliations within a single row.
2. Tightened introductory text in Section I comparing RTS, CIA, and industrial continuous testing without removing citations or technical distinctions.
3. Restructured Table I to document Release Schema v0.2 (D-54) across instances, outcomes, cochange, and failure_messages in a two-column format.
4. Rewrote Section III (Storage and Schema) with exact v0.2 release metrics (7,061 resolved base runs, base_status distribution, base_run_distance, UTC TIMESTAMP run_started_at, changeset diff attributes, and outcomes long grain).
5. Corrected Java and Python instance breakdowns in Table III (`all` split to 767/130; `relaxed` split to 646/124) per `paper/generated/composition.md`.
6. Calibrated LaTeX float separation distances and table array stretches (0.80) to eliminate white-space gaps across pages 1–4.
7. Proportionally scaled Fig. 2 (RQ1 micro recall chart) to 0.65\columnwidth to preserve visual readability while reclaiming vertical space.
8. Condensed Section V-A and V-B text describing the 4 test selection heuristics, leakage audit (D-52), and evaluation metrics without omitting any number.
9. Converted Section VI (Originality) and Section VII (Limitations) from vertical list environments into compact inline paragraphs.
10. Explicitly stated non-attainment of Roadmap Gates 1 and 1.5 (full-confidence binding) and absence of blind holdout v5 scoring (D-53) in Section VII.
11. Updated Section IX to reference published v0.1 Zenodo DOIs (dataset 10.5281/zenodo.23250262, code 10.5281/zenodo.23250690) and noted pending v0.2 deposit.
12. Updated test suite verification in Section IX to 806 tests (804 passed, 2 skipped) matching fresh execution of `make test`.
13. Refined Section X Conclusion to fit the entire paper body within the 4-page ceiling.
14. Enforced strict 5-page ceiling with `\clearpage` and balanced two-column bibliography layout using `\balance` from `balance.sty`.
15. Verified and completed bibliographic metadata (DOIs, pages, conference proceedings) across all 12 literature entries in `refs.bib`.
16. Added formal `@misc` bibliography entries for published Zenodo dataset (`brbench_data`) and code repository (`brbench_code`).
