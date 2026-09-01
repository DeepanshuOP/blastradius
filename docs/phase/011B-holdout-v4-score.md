# Phase 011-B: Holdout v4 Scorecard

> [!CAUTION]
> **STATUS: VOID — no valid measurement occurred.**
>
> The ground truth (formerly `tests/fixtures/holdout_v4/EXPECTED.md`) was produced by
> automated extraction — `normalize_test_id()` was applied to raw log lines, which
> is exactly the extractor under evaluation. This violates D-27 (only harness-reported
> counts or human reading of raw log text may be used) and Phase 3 of 011-B
> ("hand-label strictly from log contents without BlastRadius execution").
>
> Concrete evidence: entry #8 (apache__dolphinscheduler__092883042571.txt) shows
> `Canonical normalize_test_id(): testCreateDolphinDBDataSource  Time elapsed: 1::254 s  <<< ERROR!`
> — the separator rule in `normalize_test_id()` converted the decimal point in
> `1.254 s` to `1::254 s`. No human labeller would produce this string. It is the
> parser's own output presented as ground truth.
>
> The 58.33% precision figure is **VOID**, not superseded. This is distinct from a
> superseded score under D-37 (where a valid measurement was taken and later
> invalidated). Here, no measurement occurred at all. See D-38 in `docs/DECISIONS.md`.
>
> The voided labels have been moved to `docs/phase/011B-VOIDED-machine-labels.md`.
> A hand-labelling worksheet is at `docs/phase/012B-holdout-v4-worksheet.md`.
> This file is preserved as evidence. Do not delete it.

## Overall Metrics
- **Precision**: 28 / 48 (58.33%)
- **Recall**: 28 / 47 (59.57%)
- **F1 Score**: 0.5895
- **Classification Accuracy**: 27 / 32 (84.38%)

## Per-Harness Breakdown
- **pytest**: Precision 36.36%, Recall 36.36%, F1 0.3636, Class Acc 100.00%
- **Maven**: Precision 33.33%, Recall 35.71%, F1 0.3448, Class Acc 66.67%
- **Gradle**: Precision 86.36%, Recall 86.36%, F1 0.8636, Class Acc 100.00%
- **Cross-Firing Count**: 0/32

## Three-Column Comparison for Paper Section III
| Corpus & Stage | Precision | Held Out Status |
|---|---|---|
| `holdout_v3` first scoring | 83.87% | Held Out (Pre-Fix) |
| `holdout_v3` second scoring | 95.74% | NOT Held Out (Post-Fix) |
| `holdout_v4` (this scoring) | 58.33% | Held Out (Post-Fix) |

The holdout_v4 precision of 58.33% belongs in the paper as it is the only rigorously held-out measurement of the current parser logic, exposing genuine parameterisation and extraction flaws (such as the pytest parser's violation of D-32) that were inadvertently fitted out of previous sets.

## Disagreements
- `apache__dolphinscheduler__092883042571.txt`:
  FP: `org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest::testCreateDolphinDBDataSource`
  FN: `testCreateDolphinDBDataSource  Time elapsed: 1::254 s  <<< ERROR!`
- `apache__flink__078003756269.txt`:
  FP: `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase::testRuntimeRestApiDocsUpToDate`
  FN: `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase::testRuntimeRestApiDocsUpToDate(Path)`
- `apache__flink__079445374425.txt`:
  FP: `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase::testRuntimeRestApiDocsUpToDate`
  FN: `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase::testRuntimeRestApiDocsUpToDate(Path)`
- `apache__hugegraph__084221602296.txt`:
  FP: `org.apache.hugegraph.core.CoreTestSuite::init`, `org.apache.hugegraph.core::CoreTestSuite`
  FN: `org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2::946 s  <<< ERROR!`
- `apache__hugegraph__086386091934.txt`:
  FP: 5 instances of `org.apache.hugegraph.api.GraphsApiStandaloneTest::test...`
  FN: 5 instances of `test...(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: ...  <<< FAILURE!`
- `dask__distributed__084645769341.txt`:
  FP: `distributed/tests/test_nanny.py::test_failure_during_worker_initialization[45-100]`
  FN: `distributed/tests/test_nanny.py::test_failure_during_worker_initialization`
- `dask__distributed__084757793457.txt`:
  FP: `distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100]`
  FN: `distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress`
- `fla-org__flash-linear-attention__082566635619.txt`:
  FP: `tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16]`
  FN: `tests/models/test_modeling_forgetting_transformer.py::test_modeling`
- `fla-org__flash-linear-attention__086098926451.txt`:
  FP: `tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16]`
  FN: `tests/models/test_modeling_comba.py::test_generation`
- `linkedin__brooklin__077863844421.txt`:
  FP: `Gradle suite::com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation`
  FN: `com.linkedin.datastream.server.TestCoordinator::testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation`
- `sirixdb__sirix__092352347826.txt`:
  FP: `RegionOnlyPredicateCountTest::negationConjoinedWithAnAnchoringLeafIsRepresentable`, `RegionOnlyPredicateCountTest::numericAndBooleanFuseIntoOnePass`
  FN: `org.sirix.index.path.summary.RegionOnlyPredicateCountTest::negationConjoinedWithAnAnchoringLeafIsRepresentable`, `org.sirix.index.path.summary.RegionOnlyPredicateCountTest::numericAndBooleanFuseIntoOnePass`

