# Hand-Labelled Held-Out Fixture Corpus (Holdout v5 Ground Truth)

This document contains hand-labelled ground truth test outcome expectations for the 40 held-out raw job logs in `tests/fixtures/holdout_v5/`.
Labels were transcribed directly from the blind operator-filled worksheet `docs/phase/024-holdout-v5-worksheet.md` under approved mapping rules.

---

## 1. apache__beam__088751256715.txt
- **Source Repo:** `apache/beam`
- **Fixture Filename:** `apache__beam__088751256715.txt`
- **Build Tool:** Pytest (invoked via Gradle)
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failure count only, no test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 2. fla-org__flash-linear-attention__082350718781.txt
- **Source Repo:** `fla-org/flash-linear-attention`
- **Fixture Filename:** `fla-org__flash-linear-attention__082350718781.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 3. apache__beam__082969168132.txt
- **Source Repo:** `apache/beam`
- **Fixture Filename:** `apache__beam__082969168132.txt`
- **Build Tool:** Pytest (invoked via Gradle)
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failure count only, no test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 4. fla-org__flash-linear-attention__082477100071.txt
- **Source Repo:** `fla-org/flash-linear-attention`
- **Fixture Filename:** `fla-org__flash-linear-attention__082477100071.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `tests/models/test_modeling_nsa.py::test_modeling`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 5. floci-io__floci__091421214772.txt
- **Source Repo:** `floci-io/floci`
- **Fixture Filename:** `floci-io__floci__091421214772.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `tests/test_sagemaker.py::test_sagemaker_control_plane_and_training`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 6. dask__distributed__084757050312.txt
- **Source Repo:** `dask/distributed`
- **Fixture Filename:** `dask__distributed__084757050312.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `distributed/tests/test_nanny.py::test_failure_during_worker_initialization`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 7. floci-io__floci__089834122110.txt
- **Source Repo:** `floci-io/floci`
- **Fixture Filename:** `floci-io__floci__089834122110.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `tests/test_sagemaker.py::test_sagemaker_control_plane_and_training`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 8. apache__flink__080107589164.txt
- **Source Repo:** `apache/flink`
- **Fixture Filename:** `apache__flink__080107589164.txt`
- **Build Tool:** Pytest (invoked via Maven)
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `pyflink/datastream/tests/test_stream_execution_environment.py::test_generate_stream_graph_with_dependencies`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 9. farama-foundation__highwayenv__082832194425.txt
- **Source Repo:** `farama-foundation/highwayenv`
- **Fixture Filename:** `farama-foundation__highwayenv__082832194425.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no failed test identified)
- **Expected Class:** TEST_RAN_CLEAN
- **Confidence:** CERTAIN

---

## 10. agno-agi__agno__096352887725.txt
- **Source Repo:** `agno-agi/agno`
- **Fixture Filename:** `agno-agi__agno__096352887725.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no failed test identified)
- **Expected Class:** TEST_RAN_CLEAN
- **Confidence:** CERTAIN

---

## 11. diffplug__spotless__095081359640.txt
- **Source Repo:** `diffplug/spotless`
- **Fixture Filename:** `diffplug__spotless__095081359640.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `com.diffplug.spotless.maven.FormatterStepFactoryTest#eclipseUsesDefaultCacheDirectory`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 12. Stirling-Tools__Stirling-PDF__089792061823.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__089792061823.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `JarPathUtilTest#restartHelperJar_notFound_returnsNull`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 13. baomidou__mybatis-plus__083974450312.txt
- **Source Repo:** `baomidou/mybatis-plus`
- **Fixture Filename:** `baomidou__mybatis-plus__083974450312.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `MybatisConfigurationTest#testReload`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 14. sirixdb__sirix__092355497985.txt
- **Source Repo:** `sirixdb/sirix`
- **Fixture Filename:** `sirixdb__sirix__092355497985.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `io.sirix.query.scan.RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable`
  - Canonical `normalize_test_id()`: `io.sirix.query.scan.RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass`
  - Canonical `normalize_test_id()`: `io.sirix.query.scan.RegionOnlyPredicateCountTest#multiFieldConjunctionsAreAnsweredFromColumns`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 15. openremote__openremote__086930896418.txt
- **Source Repo:** `openremote/openremote`
- **Fixture Filename:** `openremote__openremote__086930896418.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failure count only, no test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 16. baomidou__mybatis-plus__084235124274.txt
- **Source Repo:** `baomidou/mybatis-plus`
- **Fixture Filename:** `baomidou__mybatis-plus__084235124274.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failure count only, no test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 17. openremote__openremote__086149354006.txt
- **Source Repo:** `openremote/openremote`
- **Fixture Filename:** `openremote__openremote__086149354006.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failure count only, no test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 18. sirixdb__sirix__088196470656.txt
- **Source Repo:** `sirixdb/sirix`
- **Fixture Filename:** `sirixdb__sirix__088196470656.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `io.sirix.query.ProjectionIndexStressTest#tombstoneRebuildCyclesKeepServingExactly`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 19. diffplug__spotless__080436519238.txt
- **Source Repo:** `diffplug/spotless`
- **Fixture Filename:** `diffplug__spotless__080436519238.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - build error, no test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 20. grobidOrg__grobid__082786414435.txt
- **Source Repo:** `grobidOrg/grobid`
- **Fixture Filename:** `grobidOrg__grobid__082786414435.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failed count but no failed test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 21. Stirling-Tools__Stirling-PDF__092039331010.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__092039331010.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no tests ran)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 22. apple__servicetalk__094207332011.txt
- **Source Repo:** `apple/servicetalk`
- **Fixture Filename:** `apple__servicetalk__094207332011.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no tests identified)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 23. webauthn4j__webauthn4j__085896676258.txt
- **Source Repo:** `webauthn4j/webauthn4j`
- **Fixture Filename:** `webauthn4j__webauthn4j__085896676258.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no tests ran)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 24. apple__servicetalk__093415674647.txt
- **Source Repo:** `apple/servicetalk`
- **Fixture Filename:** `apple__servicetalk__093415674647.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no tests identified)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 25. webauthn4j__webauthn4j__084798963375.txt
- **Source Repo:** `webauthn4j/webauthn4j`
- **Fixture Filename:** `webauthn4j__webauthn4j__084798963375.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no tests ran)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 26. unicode-org__cldr__077741081038.txt
- **Source Repo:** `unicode-org/cldr`
- **Fixture Filename:** `unicode-org__cldr__077741081038.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `TestShim#TestAll`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 27. apache__zeppelin__093702538653.txt
- **Source Repo:** `apache/zeppelin`
- **Fixture Filename:** `apache__zeppelin__093702538653.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `AuthenticationIT#testAnyOfRolesUser`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 28. unicode-org__cldr__088667882207.txt
- **Source Repo:** `unicode-org/cldr`
- **Fixture Filename:** `unicode-org__cldr__088667882207.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `TestShim#TestAll`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 29. apache__atlas__092533695478.txt
- **Source Repo:** `apache/atlas`
- **Fixture Filename:** `apache__atlas__092533695478.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failure count and stack frame only)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 30. apache__flink__080018153058.txt
- **Source Repo:** `apache/flink`
- **Fixture Filename:** `apache__flink__080018153058.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `AbstractAsyncRunnableStreamOperatorTest#testCheckpointDrain`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 31. apache__hugegraph__088106696924.txt
- **Source Repo:** `apache/hugegraph`
- **Fixture Filename:** `apache__hugegraph__088106696924.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `org.apache.hugegraph.core.VertexCoreTest#testQueryByNonEqLabelAndIndexedProperty`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 32. apache__zeppelin__087393956477.txt
- **Source Repo:** `apache/zeppelin`
- **Fixture Filename:** `apache__zeppelin__087393956477.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `AuthenticationIT#testSimpleAuthentication`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 33. apache__hertzbeat__091878341153.txt
- **Source Repo:** `apache/hertzbeat`
- **Fixture Filename:** `apache__hertzbeat__091878341153.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `LogRealTimeAlertE2eTest#testRealTimeLogAlertWithGroupAlert`
  - Canonical `normalize_test_id()`: `LogRealTimeAlertE2eTest#testRealTimeLogAlertWithIndividualAlert`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 34. apache__hugegraph__085380370363.txt
- **Source Repo:** `apache/hugegraph`
- **Fixture Filename:** `apache__hugegraph__085380370363.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  - Canonical `normalize_test_id()`: `org.apache.hugegraph.task.TaskAndResultSchedulerTest#testDistributedDeleteKeepsTaskResultRecoverable`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 35. apache__tika__093653111110.txt
- **Source Repo:** `apache/tika`
- **Fixture Filename:** `apache__tika__093653111110.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - failure count only, no test named)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 36. jline__jline3__086920871447.txt
- **Source Repo:** `jline/jline3`
- **Fixture Filename:** `jline__jline3__086920871447.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no failed test identified)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 37. nitrite__nitrite-java__090043799546.txt
- **Source Repo:** `nitrite/nitrite-java`
- **Fixture Filename:** `nitrite__nitrite-java__090043799546.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no failed test identified)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 38. thealgorithms__java__079347942021.txt
- **Source Repo:** `thealgorithms/java`
- **Fixture Filename:** `thealgorithms__java__079347942021.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no failed test identified)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 39. spiculedata__saiku__079996412627.txt
- **Source Repo:** `spiculedata/saiku`
- **Fixture Filename:** `spiculedata__saiku__079996412627.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no failed test identified)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 40. apache__tika__087468230709.txt
- **Source Repo:** `apache/tika`
- **Fixture Filename:** `apache__tika__087468230709.txt`
- **Build Tool:** Maven
- **Expected Outcomes:**
  NO_TEST_OUTCOMES (NO_TEST - no failed test identified)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---
