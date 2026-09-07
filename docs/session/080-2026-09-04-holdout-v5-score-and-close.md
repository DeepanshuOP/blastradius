# Session Report 080: Holdout v5 Score and Corpus Closure

**Date**: 2026-09-04  
**Task ID**: Phase 028 / `holdout-v5`  
**Slug**: `holdout-v5-score-and-close`  
**Agent**: Antigravity (Gemini 3.8 Flash High)  
**Commit**: `4ba2d6485a2944416c0c5eeb66b2eba5a9be831d`

---

## 1. Task Statement
Score Holdout v5 under D-37 exactly once and close the corpus permanently. Transcribe the operator-filled worksheet (`docs/phase/024-holdout-v5-worksheet.md`) using approved mechanical mappings A, B, C into `tests/fixtures/holdout_v5/EXPECTED.md`. Add a path CLI argument to `analysis/holdout_eval.py` without modifying constants or scoring logic. Run the evaluator ONCE against `tests/fixtures/holdout_v5/`. Analyze all disagreements against raw log bytes. Fix zero parsers. Write `docs/phase/028-holdout-v5-score.md` (<=60 lines), stage explicit paths, commit with message `data: score holdout v5 and close the corpus`, push, and verify SHAs match.

---

## 2. Guard Commands Run & Raw Output

### 2.1 System & Python Guard
Command:
```bash
uname -s && pwd && uv run python --version
```
Output:
```text
Linux
/home/shree/blastradius
Python 3.11.15
```

### 2.2 Git Config Guard
Command:
```bash
git config user.name && git config user.email
```
Output:
```text
DeepanshuOP
99538840+DeepanshuOP@users.noreply.github.com
```

### 2.3 Pytest Guard
Predicted: 463 passed, 1 skipped, 0 failed.
Auto-backgrounded as `task-359` due to tool timeout (>10s).
Output:
```text
463 passed, 1 skipped in 62.45s (0:01:02)
```
Actual matched prediction exactly.

---

## 3. Step 1 — Transcription Audit Trail

### 3.1 Format Required by `parse_holdout_expected()`
- Fixture header: `## {index}. {filename}` (unquoted)
- Build tool: `- **Build Tool:** {build_tool}`
- Outcomes: `- **Expected Outcomes:**` with `Canonical \`normalize_test_id()\`: \`{id}\`` (or `NO_TEST_OUTCOMES`)
- Expected class: `- **Expected Class:** {TEST_FAILURE|NO_TEST_OUTPUT|TEST_RAN_CLEAN}`
- Confidence: `- **Confidence:** CERTAIN`

### 3.2 Transcribed Counts & Split
- Transcribed: 40 / 40 (100%)
- Expected Class Split:
  - `TEST_FAILURE`: 19 / 40 (47.5%)
  - `NO_TEST_OUTPUT`: 19 / 40 (47.5%)
  - `TEST_RAN_CLEAN`: 2 / 40 (5.0%)
  - Total: 40 / 40 (100%)
- Total Expected Identifiers: 22

### 3.3 Derived Expected Class Audit Trail (All 40 Sections)
 1. apache__beam__088751256715.txt -> NO_TEST_OUTPUT (0 IDs)
 2. fla-org__flash-linear-attention__082350718781.txt -> TEST_FAILURE (1 IDs: tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx)
 3. apache__beam__082969168132.txt -> NO_TEST_OUTPUT (0 IDs)
 4. fla-org__flash-linear-attention__082477100071.txt -> TEST_FAILURE (1 IDs: tests/models/test_modeling_nsa.py::test_modeling)
 5. floci-io__floci__091421214772.txt -> TEST_FAILURE (1 IDs: tests/test_sagemaker.py::test_sagemaker_control_plane_and_training)
 6. dask__distributed__084757050312.txt -> TEST_FAILURE (1 IDs: distributed/tests/test_nanny.py::test_failure_during_worker_initialization)
 7. floci-io__floci__089834122110.txt -> TEST_FAILURE (1 IDs: tests/test_sagemaker.py::test_sagemaker_control_plane_and_training)
 8. apache__flink__080107589164.txt -> TEST_FAILURE (1 IDs: pyflink/datastream/tests/test_stream_execution_environment.py::test_generate_stream_graph_with_dependencies)
 9. farama-foundation__highwayenv__082832194425.txt -> TEST_RAN_CLEAN (0 IDs)
10. agno-agi__agno__096352887725.txt -> TEST_RAN_CLEAN (0 IDs)
11. diffplug__spotless__095081359640.txt -> TEST_FAILURE (1 IDs: com.diffplug.spotless.maven.FormatterStepFactoryTest#eclipseUsesDefaultCacheDirectory)
12. Stirling-Tools__Stirling-PDF__089792061823.txt -> TEST_FAILURE (1 IDs: JarPathUtilTest#restartHelperJar_notFound_returnsNull)
13. baomidou__mybatis-plus__083974450312.txt -> TEST_FAILURE (1 IDs: MybatisConfigurationTest#testReload)
14. sirixdb__sirix__092355497985.txt -> TEST_FAILURE (3 IDs: multiFieldConjunctionsAreAnsweredFromColumns, negationConjoinedWithAnAnchoringLeafIsRepresentable, numericAndBooleanFuseIntoOnePass)
15. openremote__openremote__086930896418.txt -> NO_TEST_OUTPUT (0 IDs)
16. baomidou__mybatis-plus__084235124274.txt -> NO_TEST_OUTPUT (0 IDs)
17. openremote__openremote__086149354006.txt -> NO_TEST_OUTPUT (0 IDs)
18. sirixdb__sirix__088196470656.txt -> TEST_FAILURE (1 IDs: io.sirix.query.ProjectionIndexStressTest#tombstoneRebuildCyclesKeepServingExactly)
19. diffplug__spotless__080436519238.txt -> NO_TEST_OUTPUT (0 IDs)
20. grobidOrg__grobid__082786414435.txt -> NO_TEST_OUTPUT (0 IDs)
21. Stirling-Tools__Stirling-PDF__092039331010.txt -> NO_TEST_OUTPUT (0 IDs)
22. apple__servicetalk__094207332011.txt -> NO_TEST_OUTPUT (0 IDs)
23. webauthn4j__webauthn4j__085896676258.txt -> NO_TEST_OUTPUT (0 IDs)
24. apple__servicetalk__093415674647.txt -> NO_TEST_OUTPUT (0 IDs)
25. webauthn4j__webauthn4j__084798963375.txt -> NO_TEST_OUTPUT (0 IDs)
26. unicode-org__cldr__077741081038.txt -> TEST_FAILURE (1 IDs: TestShim#TestAll)
27. apache__zeppelin__093702538653.txt -> TEST_FAILURE (1 IDs: AuthenticationIT#testAnyOfRolesUser)
28. unicode-org__cldr__088667882207.txt -> TEST_FAILURE (1 IDs: TestShim#TestAll)
29. apache__atlas__092533695478.txt -> NO_TEST_OUTPUT (0 IDs)
30. apache__flink__080018153058.txt -> TEST_FAILURE (1 IDs: AbstractAsyncRunnableStreamOperatorTest#testCheckpointDrain)
31. apache__hugegraph__088106696924.txt -> TEST_FAILURE (1 IDs: org.apache.hugegraph.core.VertexCoreTest#testQueryByNonEqLabelAndIndexedProperty)
32. apache__zeppelin__087393956477.txt -> TEST_FAILURE (1 IDs: AuthenticationIT#testSimpleAuthentication)
33. apache__hertzbeat__091878341153.txt -> TEST_FAILURE (2 IDs: LogRealTimeAlertE2eTest#testRealTimeLogAlertWithGroupAlert, LogRealTimeAlertE2eTest#testRealTimeLogAlertWithIndividualAlert)
34. apache__hugegraph__085380370363.txt -> TEST_FAILURE (1 IDs: org.apache.hugegraph.task.TaskAndResultSchedulerTest#testDistributedDeleteKeepsTaskResultRecoverable)
35. apache__tika__093653111110.txt -> NO_TEST_OUTPUT (0 IDs)
36. jline__jline3__086920871447.txt -> NO_TEST_OUTPUT (0 IDs)
37. nitrite__nitrite-java__090043799546.txt -> NO_TEST_OUTPUT (0 IDs)
38. thealgorithms__java__079347942021.txt -> NO_TEST_OUTPUT (0 IDs)
39. spiculedata__saiku__079996412627.txt -> NO_TEST_OUTPUT (0 IDs)
40. apache__tika__087468230709.txt -> NO_TEST_OUTPUT (0 IDs)

---

## 4. Step 2 — Single Scoring Run Output
Command:
```bash
uv run python analysis/holdout_eval.py tests/fixtures/holdout_v5 --show-errors
```
Auto-backgrounded as `task-425` due to tool timeout (>10s).
Raw Output Summary:
- True Positives (TP): 10 / 41
- False Positives (FP): 31 / 41
- False Negatives (FN): 12 / 22
- Precision: 10 / 41 = 0.2439 (24.39%)
- Recall: 10 / 22 = 0.4545 (45.45%)
- F1 Score: 20 / 63 = 0.3175
- Classification Accuracy: 25 / 40 = 0.6250 (62.50%)
- Cross-Firing Fixtures: 0 / 40 (zero cross-contamination)

---

## 5. Step 3 — Disagreement Analysis (26 Fixtures)
- **PARSER WRONG (2)**:
  - Fixture 8 (`apache__flink__080107589164.txt`): Pytest parser missed `FAILED` line because of syslog timestamp prefix `Jun 08 13:56:54`.
  - Fixture 18 (`sirixdb__sirix__088196470656.txt`): Gradle parser extracted bare class from `> Task` line, missing FQCN present in raw log `FAILED-TEST:` line.
- **OPERATOR WRONG (24)**:
  - 9 missed failures entirely (blind worksheet excerpts truncated before test failures): #1, #3, #15, #16, #17, #19, #20, #29, #35.
  - 2 missed additional failing methods: #11 (missed 1 of 2), #33 (missed 1 of 3).
  - 3 omitted pytest parameterization `[...]`: #2, #4, #6.
  - 6 omitted Java package prefix present in log: #26, #27, #28, #30, #32, #33.
  - 5 clean test runs labelled NO_TEST: #36, #37, #38, #39, #40.
- **AMBIGUOUS (0)**.

---

## 6. Non-Goals Honoured
- Zero parser code touched or modified.
- Zero test expectations modified.
- Exactly one scoring run executed against Holdout v5.
- Explicit git staging used (never `git add -A`).
- No trailers in commit message.
