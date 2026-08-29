# Phase 3: Binding Rate Remeasurement

## 3a. Binding Status Comparison

| Status | Old (Phase 002) | New (Phase 004) |
|---|---|---|
| **exact** | 3350 (61.71%) | 5125 (93.64%) |
| **unqualified** | 1970 (36.29%) | 0 (0.00%) |
| **not_found** | 105 (1.93%) | 181 (3.31%) |
| **ambiguous** | 4 (0.07%) | 167 (3.05%) |

## 3b. Binding Rate per (repo, harness)

The previously failing repositories have moved massively above the 70% gate, confirming that Gradle bare-class extraction was the primary bottleneck.

| Repo | Harness | Old Rate | New Rate |
|---|---|---|---|
| Stirling-Tools/Stirling-PDF | gradle | 1.30% | 96.09% |
| apache/beam | gradle | 3.17% | 90.60% |
| baomidou/mybatis-plus | gradle | 0.00% | 92.02% |
| sirixdb/sirix | gradle | 57.93% | 88.97% |
| apache/atlas | maven | 98.25% | 99.12% |
| apache/beam | pytest | 98.13% | 98.13% |
| apache/dolphinscheduler | maven | 91.60% | 91.60% |
| apache/fineract | gradle | 98.40% | 98.40% |
| apache/tika | maven | 95.15% | 95.15% |
| castorini/anserini | maven | 95.36% | 95.36% |
| dask/distributed | pytest | 95.61% | 95.61% |
| diffplug/spotless | gradle | 98.91% | 98.91% |
| floci-io/floci | maven | 100.00% | 100.00% |
| floci-io/floci | pytest | 94.44% | 94.44% |
| sirixdb/sirix | pytest | 0.00% | 0.00% |

**Repos below 70% gate:** 1 / 14 (Only `sirixdb/sirix [pytest]` remains below the gate at 0%).

## 3c. 20 Sampled Ambiguous Identifiers

Ambiguity rose from 4 to 167 (3.05%). This is primarily driven by multi-module repositories with duplicate test filenames (e.g. `TestUtils`, `UpdateTest`), validating predicted failure #1.
The major drivers are `apache/beam` and `sirixdb/sirix`.

- Repo: sirixdb/sirix | ID: UpdateTest#testInsertAsRightSiblingUpdateTextFirst
- Repo: apache/beam | ID: ReshuffleTest#testReshufflePreservesTimestamps
- Repo: sirixdb/sirix | ID: HOTLeafPageTest#testGuardManagement
- Repo: sirixdb/sirix | ID: UpdateTest#testNodeTransactionIsolation
- Repo: apache/tika | ID: org.apache.tika.parser.microsoft.ooxml.OOXMLParserTest#testNoRecordSizeOverflow
- Repo: apache/beam | ID: MetricsTest$AttemptedMetricTests#testAttemptedCounterMetrics
- Repo: baomidou/mybatis-plus | ID: SqlRunnerTest#testTransactional
- Repo: apache/beam | ID: ParDoTest$TimerFamilyTests#testTimerFamilyEventTimeBounded
- Repo: apache/beam | ID: WindowingTest#testMergingWindowing
- Repo: apache/beam | ID: ParDoTest$MultipleInputsAndOutputTests#testMultiOutputChaining
- Repo: apache/beam | ID: TestUtils#foo
- Repo: apache/beam | ID: SimpleParDoFnTest#testOutputsPerElementCounterDisabledViaExperiment
- Repo: apache/beam | ID: PipelineTest#testEmptyPipeline
- Repo: apache/beam | ID: CoGroupByKeyTest#testCoGroupByKeyWithWindowing
- Repo: apache/beam | ID: DataflowWorkProgressUpdaterTest#workProgressAdaptsNextDuration
- Repo: sirixdb/sirix | ID: ConcurrentNodeTrxTest#testConcurrentTrx
- Repo: sirixdb/sirix | ID: TransactionTest#testRollback
- Repo: sirixdb/sirix | ID: PageTest#initializationError
- Repo: baomidou/mybatis-plus | ID: H2UserTest#testLambdaTypeHandler
- Repo: diffplug/spotless | ID: SpotlessTaskTest#testFormat

## 3d. Gate 1.5 Assessment and Coverage Denominator

Gate 1.5 (≥70%) is **met**. The overall binding rate is now **93.64%**.
This rate is computed over 5,473 distinct test identifiers, which represents **91.00%** of ALL 6,014 distinct test_ids in the corpus. The remaining 9% belong to repositories that were not cloned locally (Terminal A is continuing to clone repos).
