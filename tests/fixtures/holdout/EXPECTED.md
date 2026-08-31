# Hand-Labelled Held-Out Fixture Corpus (T1.1c-v2 Failure-Stratified Ground Truth)

This document contains hand-labelled ground truth test outcome expectations for the 20 held-out raw job logs in `tests/fixtures/holdout/`.
All labels were identified **by eye directly from raw log text** without consulting or running any BlastRadius extractor or classifier.
Per ROADMAP §25.3, §26.1 and AGENTS.md, this held-out set is set aside untouched and is **NEVER** scored during parser development.

---

## 1. apache__beam__078088881219.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `078088881219`
- **Parent Run ID:** `26514824726`
- **Fixture Filename:** `apache__beam__078088881219.txt`
- **Build Tool:** Pytest (invoked in Python PreCommit 3.10)
- **Expected Outcomes:**
  - RAW: `FAILED apache_beam/yaml/examples/testing/examples_test.py::MLTest::test_ml_preprocessing_yaml`
  - Canonical `normalize_test_id()`: `apache_beam/yaml/examples/testing/examples_test.py::MLTest::test_ml_preprocessing_yaml`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 2. apache__beam__077874374405.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `077874374405`
- **Parent Run ID:** `26286811087`
- **Fixture Filename:** `apache__beam__077874374405.txt`
- **Build Tool:** Pytest (invoked via Gradle Yaml_Xlang_Direct PreCommit)
- **Expected Outcomes:**
  - RAW: `FAILED apache_beam/yaml/integration_tests.py::Validate_With_SchemaTest::test_only`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::Validate_With_SchemaTest::test_only`
  - RAW: `FAILED apache_beam/yaml/integration_tests.py::Assign_TimestampsTest::test_only`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::Assign_TimestampsTest::test_only`
  - RAW: `FAILED apache_beam/yaml/integration_tests.py::Ml_TransformTest::test_only`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::Ml_TransformTest::test_only`
  - RAW: `FAILED apache_beam/yaml/integration_tests.py::CreateTest::test_only`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::CreateTest::test_only`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 3. floci-io__floci__084186316975.txt
- **Source Repo:** `floci-io/floci`
- **Job ID:** `084186316975`
- **Parent Run ID:** `28319865219`
- **Fixture Filename:** `floci-io__floci__084186316975.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Summary: `[ERROR]   Ec2ContainerManagerTest.launchInstanceUserDataStreamToCloudWatch:205`
  - Canonical `normalize_test_id()`: `io.github.hectorvent.floci.services.ec2.Ec2ContainerManagerTest#launchInstanceUserDataStreamToCloudWatch`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 4. unicode-org__cldr__083663566205.txt
- **Source Repo:** `unicode-org/cldr`
- **Job ID:** `083663566205`
- **Parent Run ID:** `28238948592`
- **Fixture Filename:** `unicode-org__cldr__083663566205.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Summary: `[ERROR]   AppTest.shouldDrive:10`
  - Canonical `normalize_test_id()`: `org.unicode.cldr.surveydriver.AppTest#shouldDrive`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 5. unicode-org__cldr__086892997256.txt
- **Source Repo:** `unicode-org/cldr`
- **Job ID:** `086892997256`
- **Parent Run ID:** `29173537567`
- **Fixture Filename:** `unicode-org__cldr__086892997256.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Summary: `[ERROR]   AppTest.shouldDrive:10`
  - Canonical `normalize_test_id()`: `org.unicode.cldr.surveydriver.AppTest#shouldDrive`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 6. apache__hugegraph__086448298201.txt
- **Source Repo:** `apache/hugegraph`
- **Job ID:** `086448298201`
- **Parent Run ID:** `29116143412`
- **Fixture Filename:** `apache__hugegraph__086448298201.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] testLogin(org.apache.hugegraph.core.AuthTest)  Time elapsed: 0.397 s  <<< ERROR!`
    - Canonical `normalize_test_id()`: `org.apache.hugegraph.core.AuthTest#testLogin`
  - RAW: `[ERROR] testLogout(org.apache.hugegraph.core.AuthTest)  Time elapsed: 0.48 s  <<< ERROR!`
    - Canonical `normalize_test_id()`: `org.apache.hugegraph.core.AuthTest#testLogout`
  - RAW: `[ERROR] testValidateUserByToken(org.apache.hugegraph.core.AuthTest)  Time elapsed: 0.929 s  <<< ERROR!`
    - Canonical `normalize_test_id()`: `org.apache.hugegraph.core.AuthTest#testValidateUserByToken`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 7. apache__hugegraph__085379131609.txt
- **Source Repo:** `apache/hugegraph`
- **Job ID:** `085379131609`
- **Parent Run ID:** `28791463328`
- **Fixture Filename:** `apache__hugegraph__085379131609.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] testTask(org.apache.hugegraph.core.TaskCoreTest)  Time elapsed: 19.582 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.apache.hugegraph.core.TaskCoreTest#testTask`
  - RAW: `[ERROR] testTaskWithoutResult(org.apache.hugegraph.core.TaskCoreTest)  Time elapsed: 1.77 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.apache.hugegraph.core.TaskCoreTest#testTaskWithoutResult`
  - RAW: `[ERROR] testDistributedDeleteKeepsTaskResultRecoverable(org.apache.hugegraph.task.TaskAndResultSchedulerTest)  Time elapsed: 0.321 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.apache.hugegraph.task.TaskAndResultSchedulerTest#testDistributedDeleteKeepsTaskResultRecoverable`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 8. airlift__airlift__084082609225.txt
- **Source Repo:** `airlift/airlift`
- **Job ID:** `084082609225`
- **Parent Run ID:** `28380815882`
- **Fixture Filename:** `airlift__airlift__084082609225.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] io.airlift.api.maven.tests.OpenApiGenerationTest.testApiIdSupportsLookupSucceeds()[1] -- Time elapsed: 0.364 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `io.airlift.api.maven.tests.OpenApiGenerationTest#testApiIdSupportsLookupSucceeds`
  - RAW: `[ERROR] io.airlift.api.maven.tests.OpenApiGenerationTest.testApiIdSupportsLookupSucceeds()[2] -- Time elapsed: 0.369 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `io.airlift.api.maven.tests.OpenApiGenerationTest#testApiIdSupportsLookupSucceeds`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 9. apache__fineract__081211032591.txt
- **Source Repo:** `apache/fineract`
- **Job ID:** `081211032591`
- **Parent Run ID:** `27472784365`
- **Fixture Filename:** `apache__fineract__081211032591.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `Test payCharge_shouldReturnTransactionIdInResult() FAILED`
    - Canonical `normalize_test_id()`: `org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#payCharge_shouldReturnTransactionIdInResult`
  - RAW: `Test holdAmount_shouldUpdateTransactionExternalId() FAILED`
    - Canonical `normalize_test_id()`: `org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#holdAmount_shouldUpdateTransactionExternalId`
  - RAW: `Test postInterest_shouldValidateRequestAndUpdateManualInterestPostingExternalId() FAILED`
    - Canonical `normalize_test_id()`: `org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#postInterest_shouldValidateRequestAndUpdateManualInterestPostingExternalId`
  - RAW: `Test releaseAmount_shouldUpdateTransactionExternalId() FAILED`
    - Canonical `normalize_test_id()`: `org.apache.fineract.portfolio.savings.service.SavingsAccountWritePlatformServiceJpaRepositoryImplTest#releaseAmount_shouldUpdateTransactionExternalId`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 10. diffplug__spotless__079141262640.txt
- **Source Repo:** `diffplug/spotless`
- **Job ID:** `079141262640`
- **Parent Run ID:** `26827354100`
- **Fixture Filename:** `diffplug__spotless__079141262640.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `com.diffplug.gradle.spotless.AsciidocExtensionTest spotlessCheckFailsOnUnformattedThenPassesAfterApply() FAILED (1s)`
    - Canonical `normalize_test_id()`: `com.diffplug.gradle.spotless.AsciidocExtensionTest#spotlessCheckFailsOnUnformattedThenPassesAfterApply`
  - RAW: `com.diffplug.gradle.spotless.AsciidocExtensionTest spotlessCheckFailsOnUnformattedThenPassesAfterApply() FAILED (9.1s)`
    - Canonical `normalize_test_id()`: `com.diffplug.gradle.spotless.AsciidocExtensionTest#spotlessCheckFailsOnUnformattedThenPassesAfterApply`
  - RAW: `com.diffplug.gradle.spotless.AsciidocExtensionTest spotlessCheckFailsOnUnformattedThenPassesAfterApply() FAILED (9.9s)`
    - Canonical `normalize_test_id()`: `com.diffplug.gradle.spotless.AsciidocExtensionTest#spotlessCheckFailsOnUnformattedThenPassesAfterApply`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 11. apache__fineract__081669730637.txt
- **Source Repo:** `apache/fineract`
- **Job ID:** `081669730637`
- **Parent Run ID:** `27620301526`
- **Fixture Filename:** `apache__fineract__081669730637.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `Test testOriginatorExternalIdsPersistedViaAggregationJobAppearInSnapshotPath() FAILED (2.6s)`
  - Canonical `normalize_test_id()`: `org.apache.fineract.integrationtests.client.feign.tests.FeignTrialBalanceSummaryReportTest#testOriginatorExternalIdsPersistedViaAggregationJobAppearInSnapshotPath`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 12. nats-io__nats.java__086852684070.txt
- **Source Repo:** `nats-io/nats.java`
- **Job ID:** `086852684070`
- **Parent Run ID:** `29260554335`
- **Fixture Filename:** `nats-io__nats.java__086852684070.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `KeyValueConfigurationTests > testInstanceMirrorAndSources() FAILED`
    - Canonical `normalize_test_id()`: `io.nats.client.api.KeyValueConfigurationTests#testInstanceMirrorAndSources`
  - RAW: `KeyValueConfigurationTests > testInstanceMirrorAndSources() FAILED`
    - Canonical `normalize_test_id()`: `io.nats.client.api.KeyValueConfigurationTests#testInstanceMirrorAndSources`
  - RAW: `KeyValueConfigurationTests > testInstanceMirrorAndSources() FAILED`
    - Canonical `normalize_test_id()`: `io.nats.client.api.KeyValueConfigurationTests#testInstanceMirrorAndSources`
  - RAW: `KeyValueConfigurationTests > testInstanceMirrorAndSources() FAILED`
    - Canonical `normalize_test_id()`: `io.nats.client.api.KeyValueConfigurationTests#testInstanceMirrorAndSources`
  - RAW: `KeyValueConfigurationTests > testInstanceMirrorAndSources() FAILED`
    - Canonical `normalize_test_id()`: `io.nats.client.api.KeyValueConfigurationTests#testInstanceMirrorAndSources`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 13. grobidOrg__grobid__082786616906.txt
- **Source Repo:** `grobidOrg/grobid`
- **Job ID:** `082786616906`
- **Parent Run ID:** `27973893779`
- **Fixture Filename:** `grobidOrg__grobid__082786616906.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `BiblioItemTest > setNormalizedPublicationDate_populatesYearMonthDay_issue15 FAILED`
    - Canonical `normalize_test_id()`: `org.grobid.core.data.BiblioItemTest#setNormalizedPublicationDate_populatesYearMonthDay_issue15`
  - RAW: `BiblioItemTest > setNormalizedPublicationDate_partialDateLeavesMissingFieldsNull_issue15 FAILED`
    - Canonical `normalize_test_id()`: `org.grobid.core.data.BiblioItemTest#setNormalizedPublicationDate_partialDateLeavesMissingFieldsNull_issue15`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 14. gurkenlabs__litiengine__079032771640.txt
- **Source Repo:** `gurkenlabs/litiengine`
- **Job ID:** `079032771640`
- **Parent Run ID:** `26808716542`
- **Fixture Filename:** `gurkenlabs__litiengine__079032771640.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `AlignTests > getClampedLocation_InPoint() FAILED`
    - Canonical `normalize_test_id()`: `AlignTests#getClampedLocation_InPoint`
  - RAW: `AlignTests > getClampedLocation_OffPoint() FAILED`
    - Canonical `normalize_test_id()`: `AlignTests#getClampedLocation_OffPoint`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 15. mcreator__mcreator__081715271356.txt
- **Source Repo:** `mcreator/mcreator`
- **Job ID:** `081715271356`
- **Parent Run ID:** `27633735945`
- **Fixture Filename:** `mcreator__mcreator__081715271356.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `ReferencesFinderTest > testModElementUsagesSearch() FAILED`
    - Canonical `normalize_test_id()`: `ReferencesFinderTest#testModElementUsagesSearch`
  - RAW: `ReferencesFinderTest > testTextureUsagesSearch() FAILED`
    - Canonical `normalize_test_id()`: `ReferencesFinderTest#testTextureUsagesSearch`
  - RAW: `ReferencesFinderTest > testStructureUsagesSearch() FAILED`
    - Canonical `normalize_test_id()`: `ReferencesFinderTest#testStructureUsagesSearch`
  - RAW: `ReferencesFinderTest > testModelUsagesSearch() FAILED`
    - Canonical `normalize_test_id()`: `ReferencesFinderTest#testModelUsagesSearch`
- **Expected Class:** TEST_FAILURE
- **Confidence:** CERTAIN

---

## 16. floci-io__floci__079239274562.txt
- **Source Repo:** `floci-io/floci`
- **Job ID:** `079239274562`
- **Parent Run ID:** `26868978269`
- **Fixture Filename:** `floci-io__floci__079239274562.txt`
- **Build Tool:** Maven (`maven-compiler-plugin:3.15.0:testCompile`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Test compilation failure during `maven-compiler-plugin:3.15.0:testCompile` in `CustomResourceProvisionerTest.java`; aborted before test execution)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 17. apache__dolphinscheduler__082710858610.txt
- **Source Repo:** `apache/dolphinscheduler`
- **Job ID:** `082710858610`
- **Parent Run ID:** `27951676693`
- **Fixture Filename:** `apache__dolphinscheduler__082710858610.txt`
- **Build Tool:** GitHub Actions / Bash
- **Expected Outcomes:** NO_TEST_OUTCOMES (Aggregator job check `E2E-K8S-Result` failed due to upstream `cancelled` status; no test runner executed)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 18. Stirling-Tools__Stirling-PDF__086823631877.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `086823631877`
- **Parent Run ID:** `29251382303`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__086823631877.txt`
- **Build Tool:** GitHub Actions / Bash
- **Expected Outcomes:** NO_TEST_OUTCOMES (Aggregator job check `All checks passed` failed due to upstream `frontend-validation` job failure; no test runner executed)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 19. Stirling-Tools__Stirling-PDF__077856960467.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `077856960467`
- **Parent Run ID:** `26446751991`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__077856960467.txt`
- **Build Tool:** GitHub Actions / Bash
- **Expected Outcomes:** NO_TEST_OUTCOMES (Aggregator job check `All checks passed` failed due to upstream `docker-compose-tests` cancellation; no test runner executed)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN

---

## 20. apache__hbase__081801116210.txt
- **Source Repo:** `apache/hbase`
- **Job ID:** `081801116210`
- **Parent Run ID:** `27629549783`
- **Fixture Filename:** `apache__hbase__081801116210.txt`
- **Build Tool:** Apache Yetus (Dockerized container)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Docker-encapsulated Yetus build; test results uploaded to artifact `yetus-jdk11-hadoop3-unit-check-medium` (ID 7685365255); no individual test traces or test summary lines in runner job log)
- **Expected Class:** NO_TEST_OUTPUT
- **Confidence:** CERTAIN
