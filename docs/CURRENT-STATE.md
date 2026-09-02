# BlastRadius — Current State
Derived from docs/ on 2026-09-02. This document is rank 6 and loses to ROADMAP.md, SCHEMAS.md, DECISIONS.md and TASKS.md. Every figure names its source file.

## 1. What the Project Is
BlastRadius is a GitHub Actions harvest and empirical evaluation pipeline building BR-Bench, an execution-grounded dataset for test-impact analysis.
It captures raw workflow runs, job logs, and test outcomes across Java and Python to ground test failure sets against real CI execution.
The project evaluates how far standard proxies (co-change, reachability) diverge from execution reality.
Pipeline core operates under zero-LLM and strict reproducibility constraints; the target venue is MSR 2027 Data & Tool Showcase.

## 2. Decision Ledger
| # | Summary | Status |
|---|---|---|
| D-01 | Target track: MSR 2027 Data & Tool Showcase | IN FORCE |
| D-02 | Claimed contribution: Dataset + honest evaluation, not novel SOTA predictor | IN FORCE |
| D-03 | Language scope: Java + Python; TypeScript cut | IN FORCE |
| D-04 | Parser strategy: tree-sitter spine everywhere + optional Java SCIP tier | IN FORCE |
| D-05 | Graph formalism: Multi-layer typed property graph; no data-flow/PDG/CPG | IN FORCE |
| D-06 | Storage: NetworkX in-process + DuckDB/Parquet; no graph database | IN FORCE |
| D-07 | Diff extraction: Tier 1 tree-sitter symbol diff; Tier 2 GumTree on gold | IN FORCE |
| D-08 | Naming: Project BlastRadius; dataset named BR-Bench separately | IN FORCE |
| D-09 | Test-ID normalizer: Extend graphify ids.py | AMENDED (by D-25/D-31/D-46) |
| D-10 | Test-node typing: Registered LanguageResolver plugin in graphify | IN FORCE |
| D-11 | Graphify baseline: Two baselines: GRAPHIFY-COMMUNITY and GRAPHIFY-DIRECT | IN FORCE |
| D-12 | Matrix builds: Union failures across legs, record n_matrix_legs | IN FORCE |
| D-13 | Monorepos: Excluded from v1 frame | IN FORCE |
| D-14 | Graph versioning: Snapshot every 50 commits + deltas at base SHAs | IN FORCE |
| D-15 | Visualisation: vis.js internal/CLI; Cytoscape.js public demo | IN FORCE |
| D-16 | Dual submission: No; single submission to Data & Tool Showcase | IN FORCE |
| D-17 | LLM in pipeline: Zero LLM calls in reproducible core | IN FORCE |
| D-18 | Placement collision: Blackout window declared Week 1 | IN FORCE |
| D-19 | Raw-capture path keying: rawstore derives scope from KIND_SCOPE table | IN FORCE |
| D-20 | Cursor completion: capture_unit replaces run_capture; repo_cursor tracks PRs | IN FORCE |
| D-21 | [GAP] RESERVED and empty; held for parent_run_id from details_url | RESERVED |
| D-22 | Transient handling: TransientGovernor 60/300/900s ladder; 401 evicts token | IN FORCE |
| D-23 | Capture order: Build log (T0.3e) & artifact (T0.3d) capture before stage 3 scale | IN FORCE |
| D-24 | Check-run annotations demoted to fallback; logs/XML become primary | IN FORCE |
| D-25 | Test identity two-key model: Canonical test_id vs lossy graph_node_id | IN FORCE |
| D-26 | Per-repo log retention: Configured per-repo (1-90d), not uniform 90d | IN FORCE |
| D-27 | EXPECTED.md amended only via independent harness/log evidence | IN FORCE |
| D-28 | Artifact retention: 1-7d per-repo window; forward-only capture window | IN FORCE |
| D-29 | Ground-truth labelling discipline: Expectations derive strictly from raw logs | IN FORCE |
| D-30 | Language sweep filter: --lang filter before --limit slice; early Python pivot | IN FORCE |
| D-31 | Gradle FQCN suffix join: Gradle chevron binds FQCN via at frame suffix | IN FORCE |
| D-32 | Parameterisation: test_id is selectable method; iteration in params | IN FORCE |
| D-33 | [GAP] PyDriller -> blobless clone deviation from ROADMAP §9.4; missing from DECISIONS.md | MISSING |
| D-34 | Base resolution: Walk commit graph from blobless clone; exact_green status | IN FORCE |
| D-35 | run_attempt semantics: Label refers to attempt captured in raw API | IN FORCE |
| D-36 | Transfer deadline: 29,704s deadline, 15MB ceiling, 707 B/s floor | IN FORCE |
| D-37 | Holdout lifecycle: Scored once; parser inspection converts to dev set | IN FORCE |
| D-38 | Void vs superseded: Machine-extracted GT is VOID; corpus re-labellable | IN FORCE |
| D-39 | Java test convention: FQCN::method + fqcn_incomplete (contradicted by Phase 020) | AMENDED / CONTRADICTED |
| D-40 | Language-ordered sweep: Sweeps Python first via --lang due to 90d expiry | IN FORCE |
| D-41 | Retention cadence: data/raw 4.6 GB permanent, cursor.db permanent | IN FORCE |
| D-42 | Schema conformance: SCHEMAS.md frozen; absent columns categorized | IN FORCE |
| D-43 | Derivable negatives: Negatives derived from candidates.parquet | IN FORCE |
| D-44 | Gate 1 reads against label count (positives), not instance count | IN FORCE |
| D-45 | Secret-scan severity tiering: BLOCKER (tokens) vs REVIEW (email/hosts) | IN FORCE |
| D-46 | Class-level failures counted, not emitted as test_ids | IN FORCE |
| D-47 | Binding rate reported as split: combined (93.93%) & full-confidence (63.81%) | IN FORCE |

## 3. Current Figures Table
| Figure | Current Value | Source File & Section |
|---|---|---|
| Distinct test ids | 5,985 | docs/phase/023-binding-rate.md §Corpus Scope & Outcomes |
| Distinct Java ids | 5,115 | docs/phase/023-binding-rate.md §Corpus Scope & Outcomes |
| Distinct Python ids | 870 | docs/phase/023-binding-rate.md §Corpus Scope & Outcomes |
| Outcome rows | 20,451 | docs/phase/023-binding-rate.md §Corpus Scope & Outcomes |
| Binding rate | 93.93% combined (63.81% full / 30.13% 0.5-conf) | docs/phase/023-binding-rate.md §Quality Breakdown |
| Bare-class Java ids | 2,043 / 5,115 (39.94%) | docs/phase/023-binding-rate.md §Residual Bare-Class Fragmentation |
| Strict instances | 122 (INVARIANT-6) / 725 (EVIDENCE-ONLY) | docs/phase/017-REPORT.md §Phase 4 |
| Strict labels | 423 (INVARIANT-6) / 4,100 (EVIDENCE-ONLY) | docs/phase/017-REPORT.md §Phase 4 |
| no_base rate | 75.94% (INVARIANT-6) / 48.26% (EVIDENCE-ONLY) | docs/phase/017-REPORT.md §Phase 4 |
| exact_green count | 210 (INVARIANT-6) / 3,693 (EVIDENCE-ONLY) | docs/phase/017-REPORT.md §Phase 4 |
| Verified base runs | 275 / 1,732 (108 Java, 167 Python) | docs/HANDOFF-019.md §2 |
| Verified instances | 878 / 4,245 | docs/HANDOFF-019.md §2 |
| data/raw size | 4.9 GB / 2,734,020,926 B (304,534 logs) | docs/phase/025-transfer-manifest.md §Data Inventory |
| Fixture count | Dev: 40 logs (46 IDs); Holdout v5: 40 logs | docs/phase/013B-holdout-v5-protocol.md §Scope |
| Holdout precision | Dev-fitted: 100%; v4 voided: 58.33%; v5: unscored | docs/DECISIONS.md §D-31, docs/phase/012B-REPORT.md §Phase 1 |
| Quarantined verdicts | 375 base runs / 558 verdicts discarded | docs/HANDOFF-019.md §3 |

## 4. Conflicts Requiring a Ruling
- **Strict instances & labels**: 778 / 4,194 (docs/phase/014A-REPORT.md §Executive Summary, docs/HANDOFF-019.md §6) vs 122 / 423 (INVARIANT-6 in docs/phase/017-REPORT.md §Phase 4, docs/phase/018-REPORT.md §Phase 4, docs/HANDOFF.md §Header banner).
- **exact_green count & no_base rate**: 4,245 / 43.88% (docs/phase/014A-REPORT.md §Executive Summary, docs/HANDOFF-019.md §6) vs 210 / 75.94% (INVARIANT-6 in docs/phase/017-REPORT.md §Phase 4).
- **data/raw size**: 4.6 GB (docs/DECISIONS.md §D-41, docs/HANDOFF.md §3.1) vs 4.9 GB / 2,734,020,926 B (docs/DATA_DEPENDENCIES.md §Data Retention, docs/phase/025-transfer-manifest.md §Data Inventory).
- **D-39 Java format**: D-39 specifies `FQCN::method` and `fqcn_incomplete`; contradicted by docs/phase/020-parser-survey-REPORT.md §d (`FQCN#method` in code/tests) & docs/phase/020-parser-survey-REPORT.md §8 (`fqcn_incomplete` undeclared in docs/SCHEMAS.md).
- **Holdout precision**: 100% held-out claim (docs/HANDOVER-PRISHA.md §6) vs dev-set fitted metric (docs/DECISIONS.md §D-31) and voided v4 (docs/phase/012B-REPORT.md §Phase 1).

## 5. Stale Claims Needing Correction
- **6,014 tests & 20,535 outcomes** (docs/HANDOFF.md §3.1, docs/phase/020-parser-survey-REPORT.md) -> 5,985 & 20,451 (docs/phase/023-binding-rate.md §Corpus Scope & Outcomes).
- **5,144 Java & 2,067 bare-class IDs** (docs/phase/020-parser-survey-REPORT.md) -> 5,115 & 2,043 (docs/phase/023-binding-rate.md §Residual Bare-Class Fragmentation).
- **151 Python test IDs** (docs/HANDOFF.md §V Limitations) -> 870 (docs/phase/020-parser-survey-REPORT.md §c, docs/phase/023-binding-rate.md §Corpus Scope & Outcomes).
- **93.60% single binding rate** (docs/HANDOFF.md §3.1) -> 93.93% combined / 63.81% full-confidence (docs/phase/023-binding-rate.md §Quality Breakdown, docs/DECISIONS.md §D-47).
- **524 strict instances / 2,912 labels** (docs/HANDOFF.md §3.1) -> 122 / 423 (INVARIANT-6 in docs/phase/017-REPORT.md §Phase 4, docs/phase/018-REPORT.md §Phase 4).
- **4.6 GB data/raw size** (docs/DECISIONS.md §D-41, docs/HANDOFF.md §3.1) -> 4.9 GB / 2,734,020,926 B (docs/DATA_DEPENDENCIES.md §Data Retention, docs/phase/025-transfer-manifest.md §Data Inventory).

## 6. Open Threads
- **Base run verification sweep**: Incomplete; 275/1,732 runs verified; Java needs 92 sampled runs (docs/HANDOFF-019.md §2).
- **Live parser defects**: D1 (pytest params), D2 (Gradle suite), D3 (Gradle FQCN suffix), D4/D-46 (classMethod) live in src/parse/ (docs/phase/020-parser-survey-REPORT.md §Summary, docs/phase/022-REPORT.md §Non-goals honoured).
- **D-46 event counter**: Mandated count of synthetic classMethod events is not implemented in src/parse/ (docs/phase/022-REPORT.md §Open questions).
- **D-39 schema escalation**: `fqcn_incomplete` undeclared in frozen docs/SCHEMAS.md; separator is `#`, not `::` (docs/phase/020-parser-survey-REPORT.md §8 & §d).
- **Holdout v5**: 40-log worksheet unpopulated; awaiting operator hand-labelling (docs/phase/024-holdout-v5-worksheet.md).
- **11 CodeQL instances**: Executed real tests; awaiting operator ruling on retention vs test-free purge (docs/phase/018-REPORT.md §Rulings applied, docs/HANDOFF-019.md §4).
- **Release v0.1 withdrawn**: Staged v0.1 withdrawn; v0.2 blocked on DEFECT columns in analysis/ and src/label/ (docs/phase/014B-REPORT.md, docs/HANDOFF.md §31 Aug entry).
- **TASKS.md divergence**: Stale board; T1.1h, T1.1i, T1.4a, T1.6b, T5.6c marked undone despite completion; Gate 1 misstated vs docs/DECISIONS.md §D-44.
