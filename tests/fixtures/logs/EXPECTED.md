# Hand-Labelled Log Fixture Corpus (T1.1a Ground Truth)

This document contains hand-labelled ground truth test outcome expectations for the 40 raw job logs in `tests/fixtures/logs/`.
All labels were identified **by eye directly from raw log text** before writing any parser.

---

## 1. apache__beam__077621011187.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `077621011187`
- **Parent Run ID:** `26370233040`
- **Fixture Filename:** `apache__beam__077621011187.txt`
- **Build Tool:** GitHub Actions / Gradle
- **Expected Outcomes:** NO_TEST_OUTCOMES (Runner failed to set up Gradle action `gradle/actions/setup-gradle@4d9f0ba0025fe599b4ebab9`; aborted before task execution)
- **Confidence:** CERTAIN

---

## 2. apache__beam__077630056646.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `077630056646`
- **Parent Run ID:** `26373643475`
- **Fixture Filename:** `apache__beam__077630056646.txt`
- **Build Tool:** Gradle (Java harness test)
- **Expected Outcomes:**
  - RAW: `MemoryMonitorTest > detectGCThrashing FAILED`
  - Canonical `normalize_test_id()`: `MemoryMonitorTest#detectGCThrashing`
- **Confidence:** CERTAIN

---

## 3. apache__beam__082575659629.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `082575659629`
- **Parent Run ID:** `27906377477`
- **Fixture Filename:** `apache__beam__082575659629.txt`
- **Build Tool:** Gradle / Python sdist
- **Expected Outcomes:** NO_TEST_OUTCOMES (`> Task :sdks:python:sdist FAILED` due to `yaml.parser.ParserError` in `sdks/standard_external_transforms.yaml`; no test suite executed)
- **Confidence:** CERTAIN

---

## 4. apache__beam__082592431584.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `082592431584`
- **Parent Run ID:** `27912685795`
- **Fixture Filename:** `apache__beam__082592431584.txt`
- **Build Tool:** pytest (invoked via Gradle `:sdks:python:yamlIntegrationTests`)
- **Expected Outcomes:**
  - RAW: `apache_beam/yaml/integration_tests.py::FlattenTest::test_Flatten_ExternalJavaProvider_2 FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::FlattenTest::test_Flatten_ExternalJavaProvider_2`
  - RAW: `apache_beam/yaml/integration_tests.py::DatadogTest::test_only FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::DatadogTest::test_only`
  - RAW: `apache_beam/yaml/integration_tests.py::Iceberg_Add_FilesTest::test_WriteToJson_ExternalJavaProvider_1 FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::Iceberg_Add_FilesTest::test_WriteToJson_ExternalJavaProvider_1`
  - RAW: `apache_beam/yaml/integration_tests.py::Iceberg_Add_FilesTest::test_WriteToJson_InlineProvider_0 FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::Iceberg_Add_FilesTest::test_WriteToJson_InlineProvider_0`
  - RAW: `apache_beam/yaml/integration_tests.py::DeltaTest::test_only FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::DeltaTest::test_only`
  - RAW: `apache_beam/yaml/integration_tests.py::IcebergTest::test_only FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::IcebergTest::test_only`
  - RAW: `apache_beam/yaml/integration_tests.py::MongodbTest::test_WriteToMongoDB_ExternalJavaProvider_1 FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::MongodbTest::test_WriteToMongoDB_ExternalJavaProvider_1`
  - RAW: `apache_beam/yaml/integration_tests.py::Iceberg_Add_Files_BatchTest::test_only FAILED`
    - Canonical `normalize_test_id()`: `apache_beam/yaml/integration_tests.py::Iceberg_Add_Files_BatchTest::test_only`
- **Confidence:** CERTAIN

---

## 5. apache__beam__086455350919.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `086455350919`
- **Parent Run ID:** `29120851420`
- **Fixture Filename:** `apache__beam__086455350919.txt`
- **Build Tool:** Gradle (Groovy test runner `:beam-test-infra-metrics:checkProber`)
- **Expected Outcomes:**
  - RAW: `ProberTests > CheckGrafanaStalenessAlerts FAILED`
    - Canonical `normalize_test_id()`: `ProberTests#CheckGrafanaStalenessAlerts`
  - RAW: `ProberTests > PingGrafanaHttpApi FAILED`
    - Canonical `normalize_test_id()`: `ProberTests#PingGrafanaHttpApi`
- **Confidence:** CERTAIN

---

## 6. apache__dolphinscheduler__083801509824.txt
- **Source Repo:** `apache/dolphinscheduler`
- **Job ID:** `083801509824`
- **Parent Run ID:** `28215841642`
- **Fixture Filename:** `apache__dolphinscheduler__083801509824.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `testEmrServerlessSuccessWorkflowInstance  Time elapsed: 0.345 s  <<< FAILURE!` (in `org.apache.dolphinscheduler.api.test.cases.tasks.EmrServerlessTaskAPITest`)
  - RAW Summary: `[ERROR]   EmrServerlessTaskAPITest.testEmrServerlessSuccessWorkflowInstance:115 expected: <true> but was: <false>`
  - Canonical `normalize_test_id()`: `org.apache.dolphinscheduler.api.test.cases.tasks.EmrServerlessTaskAPITest#testEmrServerlessSuccessWorkflowInstance`
- **Confidence:** CERTAIN

---

## 7. apache__fineract__080132127199.txt
- **Source Repo:** `apache/fineract`
- **Job ID:** `080132127199`
- **Parent Run ID:** `27146509365`
- **Fixture Filename:** `apache__fineract__080132127199.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:** NO_TEST_OUTCOMES (Docker container build task failed: `> Task :fineract-provider:jibDockerBuild FAILED`; no test tasks executed)
- **Confidence:** CERTAIN

---

## 8. apache__fineract__083161294301.txt
- **Source Repo:** `apache/fineract`
- **Job ID:** `083161294301`
- **Parent Run ID:** `28061249770`
- **Fixture Filename:** `apache__fineract__083161294301.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `  Test testLoanCOBPartitioningQuery() FAILED (3.1s)`
  - Enclosing Class (preceding line 12906): `org.apache.fineract.integrationtests.cob.CobPartitioningTest`
  - Canonical `normalize_test_id()`: `org.apache.fineract.integrationtests.cob.CobPartitioningTest#testLoanCOBPartitioningQuery` (if multiline context tracked) or unresolvable bare method name if parsed line-by-line.
- **Confidence:** AMBIGUOUS (Gradle outputs class names on separate lines above individual test methods; the failure line itself contains only the method name, making single-line regex extractors lose class scoping).

---

## 9. apache__flink__079221420559.txt
- **Source Repo:** `apache/flink`
- **Job ID:** `079221420559`
- **Parent Run ID:** `26861051716`
- **Fixture Filename:** `apache__flink__079221420559.txt`
- **Build Tool:** Maven / Docker CI
- **Expected Outcomes:** NO_TEST_OUTCOMES (CI infrastructure failure: `##[error]Docker pull failed with exit code 1`; job aborted before build/test step)
- **Confidence:** CERTAIN

---

## 10. apache__flink__079848838447.txt
- **Source Repo:** `apache/flink`
- **Job ID:** `079848838447`
- **Parent Run ID:** `27050719257`
- **Fixture Filename:** `apache__flink__079848838447.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `Jun 06 04:05:43 04:05:43.382 [ERROR] org.apache.flink.test.checkpointing.SavepointITCase.testStopWithSavepointFailsOverToSavepoint`
  - RAW Summary: `Jun 06 04:33:52 04:33:52.032 [ERROR]   SavepointITCase.testStopWithSavepointFailsOverToSavepoint:326`
  - Canonical `normalize_test_id()`: `org.apache.flink.test.checkpointing.SavepointITCase#testStopWithSavepointFailsOverToSavepoint`
  - RAW: `[ERROR] org.apache.flink.test.runtime.IPv6HostnamesITCase.testClusterWithIPv6host -- Time elapsed: 0.381 s <<< ERROR!`
  - RAW Summary: `Jun 06 04:33:52 04:33:52.032 [ERROR]   IPv6HostnamesITCase.testClusterWithIPv6host:123 » Runtime Failed to fetch next result`
  - Canonical `normalize_test_id()`: `org.apache.flink.test.runtime.IPv6HostnamesITCase#testClusterWithIPv6host`
  - Note: Ground-truth omission identified by harness-count audit on 2026-08-26 (lines 7291, 7292, 7784, 7786), not by initial hand-labelling pass.
- **Confidence:** CERTAIN

---

## 11. apache__hbase__078892029185.txt
- **Source Repo:** `apache/hbase`
- **Job ID:** `078892029185`
- **Parent Run ID:** `26765891466`
- **Fixture Filename:** `apache__hbase__078892029185.txt`
- **Build Tool:** Apache Yetus (Dockerized Maven container)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Yetus summary table reports `| -1 | unit | 66m 7s | hbase-server in the patch failed.` and points to artifact `/yetus-jdk17-hadoop3-unit-check/output/patch-unit-hbase-server.txt`. No individual test class or method names appear anywhere in the job log.)
- **Confidence:** CERTAIN

---

## 12. apache__hbase__082907939305.txt
- **Source Repo:** `apache/hbase`
- **Job ID:** `082907939305`
- **Parent Run ID:** `28012242226`
- **Fixture Filename:** `apache__hbase__082907939305.txt`
- **Build Tool:** Apache Yetus (Dockerized Maven container)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Yetus summary table reports `| -1 | mvninstall | 3m 26s | root in the patch failed.` and `| -1 | unit | 0m 21s | hbase-it in the patch failed.`. Result files are saved to `patch-mvninstall-root.txt` and `patch-unit-hbase-it.txt`. No test names appear in the job log.)
- **Confidence:** CERTAIN

---

## 13. apache__hbase__083382132597.txt
- **Source Repo:** `apache/hbase`
- **Job ID:** `083382132597`
- **Parent Run ID:** `28155253251`
- **Fixture Filename:** `apache__hbase__083382132597.txt`
- **Build Tool:** Apache Yetus (Dockerized Maven container)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Workflow cancelled / aborted early during Yetus container initialization; no test execution occurred.)
- **Confidence:** CERTAIN

---

## 14. apache__hbase__084057821217.txt
- **Source Repo:** `apache/hbase`
- **Job ID:** `084057821217`
- **Parent Run ID:** `28373719766`
- **Fixture Filename:** `apache__hbase__084057821217.txt`
- **Build Tool:** Apache Yetus (Dockerized Maven container)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Yetus summary table reports `| -1 | unit | 74m 55s | hbase-server in the patch failed.` with artifact path `output/patch-unit-hbase-server.txt`. No individual test class or method names appear in the job log.)
- **Confidence:** CERTAIN

---

## 15. apache__zeppelin__079328560137.txt
- **Source Repo:** `apache/zeppelin`
- **Job ID:** `079328560137`
- **Parent Run ID:** `26894242937`
- **Fixture Filename:** `apache__zeppelin__079328560137.txt`
- **Build Tool:** Maven
- **Expected Outcomes:** NO_TEST_OUTCOMES (GitHub Actions runner cancelled / failed during environment setup before test execution)
- **Confidence:** CERTAIN

---

## 16. apache__zeppelin__084837475646.txt
- **Source Repo:** `apache/zeppelin`
- **Job ID:** `084837475646`
- **Parent Run ID:** `28609331283`
- **Fixture Filename:** `apache__zeppelin__084837475646.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] org.apache.zeppelin.integration.AuthenticationIT.testSimpleAuthentication -- Time elapsed: 46.44 s <<< ERROR!`
  - RAW Summary: `[ERROR]   AuthenticationIT.testSimpleAuthentication:96->AbstractZeppelinIT.authenticationUser:60->AbstractZeppelinIT.clickableWait:181 » Timeout Expected condition failed...`
  - Canonical `normalize_test_id()`: `org.apache.zeppelin.integration.AuthenticationIT#testSimpleAuthentication`
- **Confidence:** CERTAIN

---

## 17. airlift__airlift__081878478589.txt
- **Source Repo:** `airlift/airlift`
- **Job ID:** `081878478589`
- **Parent Run ID:** `27684091241`
- **Fixture Filename:** `airlift__airlift__081878478589.txt`
- **Build Tool:** Maven
- **Expected Outcomes:** NO_TEST_OUTCOMES (Maven dependency resolution/network error during compilation; build aborted before testing phase)
- **Confidence:** CERTAIN

---

## 18. airlift__airlift__084082609180.txt
- **Source Repo:** `airlift/airlift`
- **Job ID:** `084082609180`
- **Parent Run ID:** `28380815882`
- **Fixture Filename:** `airlift__airlift__084082609180.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] io.airlift.api.maven.tests.OpenApiGenerationTest.testApiIdSupportsLookupSucceeds()[1] -- Time elapsed: 0.250 s <<< FAILURE!`
  - RAW: `[ERROR] io.airlift.api.maven.tests.OpenApiGenerationTest.testApiIdSupportsLookupSucceeds()[2] -- Time elapsed: 0.259 s <<< FAILURE!`
  - Canonical `normalize_test_id()`: `io.airlift.api.maven.tests.OpenApiGenerationTest#testApiIdSupportsLookupSucceeds`
- **Confidence:** CERTAIN

---

## 19. apple__servicetalk__085939947321.txt
- **Source Repo:** `apple/servicetalk`
- **Job ID:** `085939947321`
- **Parent Run ID:** `28958227558`
- **Fixture Filename:** `apple__servicetalk__085939947321.txt`
- **Build Tool:** Gradle (`:servicetalk-concurrent-api:test`)
- **Expected Outcomes:**
  - RAW: `PublisherBufferConcurrencyTest > largeRun() FAILED`
  - Canonical `normalize_test_id()`: `PublisherBufferConcurrencyTest#largeRun`
- **Confidence:** CERTAIN

---

## 20. baomidou__mybatis-plus__085831964676.txt
- **Source Repo:** `baomidou/mybatis-plus`
- **Job ID:** `085831964676`
- **Parent Run ID:** `28931648316`
- **Fixture Filename:** `baomidou__mybatis-plus__085831964676.txt`
- **Build Tool:** Gradle (`:mybatis-plus-core:test`)
- **Expected Outcomes:**
  - RAW: `GeneratePomTest > test() FAILED`
  - Canonical `normalize_test_id()`: `GeneratePomTest#test`
- **Confidence:** CERTAIN

---

## 21. crimera__piko__083277376521.txt
- **Source Repo:** `crimera/piko`
- **Job ID:** `083277376521`
- **Parent Run ID:** `28122338908`
- **Fixture Filename:** `crimera__piko__083277376521.txt`
- **Build Tool:** GitHub Actions
- **Expected Outcomes:** NO_TEST_OUTCOMES (Workflow setup failure: `##[error]Unable to resolve action actions/setup-java@v6, unable to find version v6`. This is the smallest log in the corpus: 1.16 KB compressed.)
- **Confidence:** CERTAIN

---

## 22. diffplug__spotless__077697425370.txt
- **Source Repo:** `diffplug/spotless`
- **Job ID:** `077697425370`
- **Parent Run ID:** `26396209318`
- **Fixture Filename:** `diffplug__spotless__077697425370.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:** NO_TEST_OUTCOMES (Code formatting check failure: `> Task :plugin-maven:spotlessJavaCheck FAILED`; no test tasks executed)
- **Confidence:** CERTAIN

---

## 23. diffplug__spotless__086063491051.txt
- **Source Repo:** `diffplug/spotless`
- **Job ID:** `086063491051`
- **Parent Run ID:** `29001522633`
- **Fixture Filename:** `diffplug__spotless__086063491051.txt`
- **Build Tool:** Gradle (`:testlib:test`)
- **Expected Outcomes:**
  - RAW: `com.diffplug.spotless.rdf.RdfFormatterTest testCoolRdfFormatter_2_0_0_DefaultStyle() FAILED (7.1s)`
    - Canonical `normalize_test_id()`: `com.diffplug.spotless.rdf.RdfFormatterTest#testCoolRdfFormatter_2_0_0_DefaultStyle`
  - RAW: `com.diffplug.spotless.rdf.RdfFormatterTest blankNodeOrderingIsNotStableInCoolRdfFormatter_2_0_0() FAILED`
    - Canonical `normalize_test_id()`: `com.diffplug.spotless.rdf.RdfFormatterTest#blankNodeOrderingIsNotStableInCoolRdfFormatter_2_0_0`
  - RAW: `com.diffplug.spotless.rdf.RdfFormatterTest testCoolRdfFormatter_2_0_0_style01() FAILED`
    - Canonical `normalize_test_id()`: `com.diffplug.spotless.rdf.RdfFormatterTest#testCoolRdfFormatter_2_0_0_style01`
- **Confidence:** CERTAIN

---

## 24. floci-io__floci__081814559712.txt
- **Source Repo:** `floci-io/floci`
- **Job ID:** `081814559712`
- **Parent Run ID:** `27303796031`
- **Fixture Filename:** `floci-io__floci__081814559712.txt`
- **Build Tool:** GitHub Actions
- **Expected Outcomes:** NO_TEST_OUTCOMES (Artifact download failure: `##[error]Unable to download artifact(s): Artifact not found for name: floci-dist`)
- **Confidence:** CERTAIN

---

## 25. floci-io__floci__082492942956.txt
- **Source Repo:** `floci-io/floci`
- **Job ID:** `082492942956`
- **Parent Run ID:** `27809413832`
- **Fixture Filename:** `floci-io__floci__082492942956.txt`
- **Build Tool:** Bash / Git hook
- **Expected Outcomes:** NO_TEST_OUTCOMES (Conventional commits check script failed on non-conforming commit title; no test suite run)
- **Confidence:** CERTAIN

---

## 26. floci-io__floci__084479785666.txt
- **Source Repo:** `floci-io/floci`
- **Job ID:** `084479785666`
- **Parent Run ID:** `28501544001`
- **Fixture Filename:** `floci-io__floci__084479785666.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] io.github.hectorvent.floci.services.ec2.Ec2ContainerManagerTest.launchInstanceUserDataStreamToCloudWatch -- Time elapsed: 2.755 s <<< FAILURE!`
  - RAW Summary: `[ERROR]   Ec2ContainerManagerTest.launchInstanceUserDataStreamToCloudWatch:205`
  - Canonical `normalize_test_id()`: `io.github.hectorvent.floci.services.ec2.Ec2ContainerManagerTest#launchInstanceUserDataStreamToCloudWatch`
- **Confidence:** CERTAIN

---

## 27. grobidOrg__grobid__085264981989.txt
- **Source Repo:** `grobidOrg/grobid`
- **Job ID:** `085264981989`
- **Parent Run ID:** `28756729612`
- **Fixture Filename:** `grobidOrg__grobid__085264981989.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:** NO_TEST_OUTCOMES (Code formatting check failure: `> Task :grobid-core:spotlessJavaCheck FAILED`; no test tasks executed)
- **Confidence:** CERTAIN

---

## 28. jhipster__prettier-java__084966237571.txt
- **Source Repo:** `jhipster/prettier-java`
- **Job ID:** `084966237571`
- **Parent Run ID:** `28650234828`
- **Fixture Filename:** `jhipster__prettier-java__084966237571.txt`
- **Build Tool:** npm / Prettier
- **Expected Outcomes:** NO_TEST_OUTCOMES (JavaScript prettier formatting check failure; no test suite run)
- **Confidence:** CERTAIN

---

## 29. openremote__openremote__082946004526.txt
- **Source Repo:** `openremote/openremote`
- **Job ID:** `082946004526`
- **Parent Run ID:** `28023333667`
- **Fixture Filename:** `openremote__openremote__082946004526.txt`
- **Build Tool:** GitHub Actions
- **Expected Outcomes:** NO_TEST_OUTCOMES (Repository checkout / auth error before build start)
- **Confidence:** CERTAIN

---

## 30. openremote__openremote__084103046129.txt
- **Source Repo:** `openremote/openremote`
- **Job ID:** `084103046129`
- **Parent Run ID:** `28386638456`
- **Fixture Filename:** `openremote__openremote__084103046129.txt`
- **Build Tool:** Gradle / Spock
- **Expected Outcomes:**
  - RAW: `  Test Does not emit attribute events after asset deletion FAILED (22.2s)`
  - Preceding Context: `org.openremote.test.assets.ApplyPredictedDataPointsServiceTest > Does not emit attribute events after asset deletion took: 22262ms`
  - Canonical `normalize_test_id()`: `org.openremote.test.assets.ApplyPredictedDataPointsServiceTest#Does not emit attribute events after asset deletion`
- **Confidence:** AMBIGUOUS (Spock narrative feature method names with spaces do not match standard Java identifier token rules and require special unquoted handling).

---

## 31. opentripplanner__opentripplanner__077860984374.txt
- **Source Repo:** `opentripplanner/opentripplanner`
- **Job ID:** `077860984374`
- **Parent Run ID:** `26447963629`
- **Fixture Filename:** `opentripplanner__opentripplanner__077860984374.txt`
- **Build Tool:** GitHub Actions
- **Expected Outcomes:** NO_TEST_OUTCOMES (GitHub Action download failure: `##[error]Failed to download archive 'https://codeload.github.com/actions/setup-java/zip/...'`)
- **Confidence:** CERTAIN

---

## 32. opentripplanner__opentripplanner__077865124037.txt
- **Source Repo:** `opentripplanner/opentripplanner`
- **Job ID:** `077865124037`
- **Parent Run ID:** `26449266376`
- **Fixture Filename:** `opentripplanner__opentripplanner__077865124037.txt`
- **Build Tool:** Maven/Surefire 3.x
- **Expected Outcomes:**
  - RAW: `[ERROR]   ScooterRentalGeofencingTest.arriveByAdjacentNoDropOffZonesDropsOutsideBothZones:398 » IllegalArgument Unexpected non-empty arriveByDestinationZones when arriveBy is false`
    - Canonical `normalize_test_id()`: `ScooterRentalGeofencingTest#arriveByAdjacentNoDropOffZonesDropsOutsideBothZones`
  - RAW: `[ERROR]   ScooterRentalGeofencingTest.arriveBySearchBlocksRidingIntoNoTraversalZone:205 » IllegalArgument Unexpected non-empty arriveByDestinationZones when arriveBy is false`
    - Canonical `normalize_test_id()`: `ScooterRentalGeofencingTest#arriveBySearchBlocksRidingIntoNoTraversalZone`
  - RAW: `[ERROR]   ScooterRentalGeofencingTest.arriveBySearchDropsOffOutsideNoDropOffZone:104->runSearch:639 » IllegalArgument Unexpected non-empty arriveByDestinationZones when arriveBy is false`
    - Canonical `normalize_test_id()`: `ScooterRentalGeofencingTest#arriveBySearchDropsOffOutsideNoDropOffZone`
  - RAW: `[ERROR]   ScooterRentalGeofencingTest.forwardAndArriveByBothFindPath:112->runSearch:639 » IllegalArgument Unexpected non-empty arriveByDestinationZones when arriveBy is false`
    - Canonical `normalize_test_id()`: `ScooterRentalGeofencingTest#forwardAndArriveByBothFindPath`
- **Confidence:** CERTAIN

---

## 33. sirixdb__sirix__079909436297.txt
- **Source Repo:** `sirixdb/sirix`
- **Job ID:** `079909436297`
- **Parent Run ID:** `27074498882`
- **Fixture Filename:** `sirixdb__sirix__079909436297.txt`
- **Build Tool:** Gradle (Kotlin Native Image Smoke Test `:sirix-kotlin-cli:nativeSmokeTest`)
- **Expected Outcomes:**
  - RAW: `io.sirix.cli.NativeImageSmokeTest > FLWOR expression FAILED`
    - Canonical `normalize_test_id()`: `io.sirix.cli.NativeImageSmokeTest#FLWOR expression`
  - RAW: `io.sirix.cli.NativeImageSmokeTest > Let expression with computation FAILED`
    - Canonical `normalize_test_id()`: `io.sirix.cli.NativeImageSmokeTest#Let expression with computation`
  - RAW: `io.sirix.cli.NativeImageSmokeTest > String manipulation query FAILED`
    - Canonical `normalize_test_id()`: `io.sirix.cli.NativeImageSmokeTest#String manipulation query`
  - RAW: `io.sirix.cli.NativeImageSmokeTest > Conditional expression FAILED`
    - Canonical `normalize_test_id()`: `io.sirix.cli.NativeImageSmokeTest#Conditional expression`
  - RAW: `io.sirix.cli.NativeImageSmokeTest > Sequence operations FAILED`
    - Canonical `normalize_test_id()`: `io.sirix.cli.NativeImageSmokeTest#Sequence operations`
  - RAW: `io.sirix.cli.NativeImageSmokeTest > Basic arithmetic query FAILED`
    - Canonical `normalize_test_id()`: `io.sirix.cli.NativeImageSmokeTest#Basic arithmetic query`
- **Confidence:** AMBIGUOUS (Test method names are Kotlin backticked descriptive strings containing spaces).

---

## 34. sirixdb__sirix__086198357085.txt
- **Source Repo:** `sirixdb/sirix`
- **Job ID:** `086198357085`
- **Parent Run ID:** `29041053794`
- **Fixture Filename:** `sirixdb__sirix__086198357085.txt`
- **Build Tool:** Gradle (`:sirix-core:test`)
- **Expected Outcomes:**
  - RAW: `LinuxMemorySegmentAllocatorTest > testAllocateMaximumSize() FAILED`
  - Canonical `normalize_test_id()`: `LinuxMemorySegmentAllocatorTest#testAllocateMaximumSize`
- **Confidence:** CERTAIN

---

## 35. spiculedata__saiku__080014373865.txt
- **Source Repo:** `spiculedata/saiku`
- **Job ID:** `080014373865`
- **Parent Run ID:** `27112995819`
- **Fixture Filename:** `spiculedata__saiku__080014373865.txt`
- **Build Tool:** Maven
- **Expected Outcomes:** NO_TEST_OUTCOMES (Maven build failed during packaging/assembly phase with `[INFO] BUILD FAILURE`; all unit tests executed in earlier modules passed clean with 0 failures)
- **Confidence:** CERTAIN

---

## 36. spiculedata__saiku__082534301666.txt
- **Source Repo:** `spiculedata/saiku`
- **Job ID:** `082534301666`
- **Parent Run ID:** `27890993514`
- **Fixture Filename:** `spiculedata__saiku__082534301666.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.AiAskServiceTest.degradesWhenProviderEmitsInvalidJson -- Time elapsed: 0.031 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.AiAskServiceTest#degradesWhenProviderEmitsInvalidJson`
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest.requestAlwaysCarriesRefusalToolAndForcesToolChoice -- Time elapsed: 0.022 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest#requestAlwaysCarriesRefusalToolAndForcesToolChoice`
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest.requestBodyBindsSchemaAsToolInputSchema -- Time elapsed: 0.003 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest#requestBodyBindsSchemaAsToolInputSchema`
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest.systemPromptKeepsGuardrailWordingVerbatim -- Time elapsed: 0.003 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.AnthropicNlAskProviderTest#systemPromptKeepsGuardrailWordingVerbatim`
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest.requestBodyBindsFunctionParametersAndForcesToolChoice -- Time elapsed: 0.004 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#requestBodyBindsFunctionParametersAndForcesToolChoice`
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest.requestAlwaysCarriesRefusalFunctionAndForcesToolChoice -- Time elapsed: 0.004 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#requestAlwaysCarriesRefusalFunctionAndForcesToolChoice`
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest.systemPromptKeepsGuardrailWordingVerbatim -- Time elapsed: 0.001 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#systemPromptKeepsGuardrailWordingVerbatim`
  - RAW: `[ERROR] org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest.parseToolResponseDegradesWhenToolCallsExcludeEmitQuery -- Time elapsed: 0 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.saiku.service.olap.ai.ask.OpenAINlAskProviderTest#parseToolResponseDegradesWhenToolCallsExcludeEmitQuery`
- **Confidence:** CERTAIN

---

## 37. Stirling-Tools__Stirling-PDF__077860967858.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `077860967858`
- **Parent Run ID:** `26447957683`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__077860967858.txt`
- **Build Tool:** GitHub Actions
- **Expected Outcomes:** NO_TEST_OUTCOMES (GitHub Action download failure: `##[error]Failed to download archive 'https://codeload.github.com/step-security/harden-runner/zip/...'`)
- **Confidence:** CERTAIN

---

## 38. Stirling-Tools__Stirling-PDF__081016086095.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `081016086095`
- **Parent Run ID:** `27412209407`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__081016086095.txt`
- **Build Tool:** Gradle (`:***-pdf:test` / `backend:build:ci`)
- **Expected Outcomes:**
  - RAW: `UIDataControllerTest > getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical() FAILED`
  - Canonical `normalize_test_id()`: `UIDataControllerTest#getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical`
- **Confidence:** CERTAIN

---

## 39. Stirling-Tools__Stirling-PDF__085817860968.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `085817860968`
- **Parent Run ID:** `28927244680`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__085817860968.txt`
- **Build Tool:** Gradle (`:***-pdf:test` / `backend:build:ci`)
- **Expected Outcomes:**
  - RAW: `WebMvcConfig > addResourceHandlers > registers all five resource handler groups FAILED`
  - Canonical `normalize_test_id()`: `WebMvcConfig#registers all five resource handler groups`
- **Confidence:** AMBIGUOUS (Hierarchical 3-segment Gradle test name `Class > Context > Method` with space-delimited narrative assertion text).

---

## 40. thealgorithms__java__080494921200.txt
- **Source Repo:** `thealgorithms/java`
- **Job ID:** `080494921200`
- **Parent Run ID:** `27257466355`
- **Fixture Filename:** `thealgorithms__java__080494921200.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `[ERROR] com.thealgorithms.dynamicprogramming.LongestPalindromicSubsequenceTest.testLpsKnownCases(String, String)[1] -- Time elapsed: 0.009 s <<< FAILURE!`
  - RAW: `[ERROR] com.thealgorithms.dynamicprogramming.LongestPalindromicSubsequenceTest.testLpsKnownCases(String, String)[5] -- Time elapsed: 0.001 s <<< FAILURE!`
  - RAW Summary: `[ERROR]   LongestPalindromicSubsequenceTest.testLpsKnownCases:21 expected: <BABCBAB> but was: <BACBCAB>`
  - Canonical `normalize_test_id()`: `com.thealgorithms.dynamicprogramming.LongestPalindromicSubsequenceTest#testLpsKnownCases`
- **Confidence:** CERTAIN

---

## Analysis of the Four Anomalous Repositories

### 1. apache/hbase (CONFIRMED GENUINE NO_TEST_OUTCOMES)
All 4 sampled logs (`078892029185`, `082907939305`, `083382132597`, `084057821217`) independently confirm Terminal B's diagnosis. HBase executes tests inside Docker via Apache Yetus, streaming output to container log files. The GitHub Actions job log contains only setup, Docker build commands, and a high-level Yetus vote table (e.g. `| -1 | unit | hbase-server in the patch failed.`). Individual failing test names are saved to `output/patch-unit-*.txt` and uploaded as build artifacts. **No individual test identifiers exist in the job log text itself.**

### 2. opentripplanner/opentripplanner (CONFIRMED SUREFIRE 3.x)
Log `077865124037` confirms that OpenTripPlanner uses Maven Surefire 3.x, formatting test failures as `[ERROR]   ClassName.methodName:LINE » ExceptionType message`. The extractor previously missed these due to expecting Maven 2.x `<<< FAILURE!` blocks or Surefire 2.x summary headings.

### 3. apache/fineract (CONFIRMED MULTILINE GRADLE SPLIT)
Log `083161294301` confirms that Gradle outputs class headers on separate lines (e.g. line 12906 `org.apache.fineract.integrationtests.cob.CobPartitioningTest`) while test outcomes appear on subsequent lines (line 12908 `  Test testLoanCOBPartitioningQuery() FAILED (3.1s)`). A single-line regex extractor sees only the bare method name, creating ambiguity unless class context is retained across lines.

### 4. sirixdb/sirix (CONFIRMED KOTLIN / GRADLE CASCADE & NARRATIVE NAMES)
Logs `086198357085` and `079909436297` confirm standard Gradle test outputs (`ClassName > methodName() FAILED`) as well as Kotlin/JUnit 5 test names with whitespace and backticks (`io.sirix.cli.NativeImageSmokeTest > FLWOR expression FAILED`). Selecting small runs avoids 1,200-failure cascades while capturing the exact syntactic variations.
