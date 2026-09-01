# 011B VOIDED MACHINE LABELS — EVIDENCE ONLY

> [!CAUTION]
> **This file is EVIDENCE, not ground truth.**
>
> These labels were produced by automated extraction: `normalize_test_id()` from
> `src/parse/test_ids.py` was applied to raw log lines. That function is the
> extractor under evaluation. Using its output as ground truth is circular.
>
> Proof: entry #8 records `normalize_test_id(): testCreateDolphinDBDataSource  Time elapsed: 1::254 s  <<< ERROR!`
> — the `::` separator rule transformed `1.254 s` to `1::254 s`. This string
> can only come from the parser; no human reader would write it.
>
> Ground truth for this corpus must be produced by a human reading the raw logs.
> See `docs/phase/012B-holdout-v4-worksheet.md` for the labelling worksheet.
> See `docs/DECISIONS.md` D-38 for the void-versus-superseded distinction.
>
> Do NOT use any identifier in this file as an EXPECTED value in any test.

---

## Holdout v4 Expected Outcomes

<!-- Format matching spec 008-B Expected Class -->
## 1. Stirling-Tools__Stirling-PDF__081016081705.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `081016081705`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__081016081705.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 908: `2026-06-12T11:17:50.6211639Z UIDataControllerTest > getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical() FAILED`
    - Canonical `normalize_test_id()`: `UIDataControllerTest::getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 2. Stirling-Tools__Stirling-PDF__081185748047.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `081185748047`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__081185748047.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 576: `2026-06-13T11:09:29.5109777Z [[33mbackend:build:ci[0m] JobQueueTest > shouldCheckIfJobIsQueued() FAILED`
    - Canonical `normalize_test_id()`: `JobQueueTest::shouldCheckIfJobIsQueued`
  - RAW Line 579: `2026-06-13T11:09:29.5110981Z [[33mbackend:build:ci[0m] JobQueueTest > shouldCancelJob() FAILED`
    - Canonical `normalize_test_id()`: `JobQueueTest::shouldCancelJob`
  - RAW Line 582: `2026-06-13T11:09:29.5112069Z [[33mbackend:build:ci[0m] JobQueueTest > shouldGetQueueStats() FAILED`
    - Canonical `normalize_test_id()`: `JobQueueTest::shouldGetQueueStats`
  - RAW Line 585: `2026-06-13T11:09:29.5112976Z [[33mbackend:build:ci[0m] JobQueueTest > shouldQueueJob() FAILED`
    - Canonical `normalize_test_id()`: `JobQueueTest::shouldQueueJob`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 4

## 3. agno-agi__agno__079305370965.txt
- **Source Repo:** `agno-agi/agno`
- **Job ID:** `079305370965`
- **Fixture Filename:** `agno-agi__agno__079305370965.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 10206: `2026-06-03T13:39:13.1733817Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'gpt2' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/openai-community/gpt2/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/gpt2/resolve/main/tokenizer.json: status code 429'}`
    - Canonical `normalize_test_id()`: `libs.agno.tests.unit.knowledge.chunking.test_code_chunking::test_code_chunking_gpt2_tokenizer`
  - RAW Line 10207: `2026-06-03T13:39:13.1736939Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'cl100k_base' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/Xenova/gpt-4/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/cl100k_base/resolve/main/tokenizer.json: status code 429'}`
    - Canonical `normalize_test_id()`: `libs.agno.tests.unit.knowledge.chunking.test_code_chunking::test_code_chunking_cl100k_tokenizer`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 2

## 4. agno-agi__agno__092042274925.txt
- **Source Repo:** `agno-agi/agno`
- **Job ID:** `092042274925`
- **Fixture Filename:** `agno-agi__agno__092042274925.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 1250: `2026-08-04T15:29:41.6265273Z FAILED tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields - AttributeError: 'str' object has no attribute 'rating'`
    - Canonical `normalize_test_id()`: `tests.integration.models.deepinfra.test_structured_response::test_structured_response_with_enum_fields`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 5. apache__atlas__085339439869.txt
- **Source Repo:** `apache/atlas`
- **Job ID:** `085339439869`
- **Fixture Filename:** `apache__atlas__085339439869.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 1362: `2026-07-06T09:38:44.7360321Z [ERROR] org.apache.atlas.kafka.KafkaNotificationTest.setup -- Time elapsed: 17.90 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.apache.atlas.kafka.KafkaNotificationTest::setup`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 6. apache__beam__086101982024.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `086101982024`
- **Fixture Filename:** `apache__beam__086101982024.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 1090: `2026-07-09T11:09:03.8535306Z HadoopFormatIOCassandraTest > classMethod FAILED`
    - Canonical `normalize_test_id()`: `HadoopFormatIOCassandraTest::classMethod`
  - RAW Line 1096: `2026-07-09T11:10:15.1523730Z HadoopFormatIOElasticTest > testHifIOWithElastic FAILED`
    - Canonical `normalize_test_id()`: `HadoopFormatIOElasticTest::testHifIOWithElastic`
  - RAW Line 1100: `2026-07-09T11:10:15.6517616Z HadoopFormatIOElasticTest > testHifIOWithElasticQuery FAILED`
    - Canonical `normalize_test_id()`: `HadoopFormatIOElasticTest::testHifIOWithElasticQuery`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 3

## 7. apache__beam__093527298308.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `093527298308`
- **Fixture Filename:** `apache__beam__093527298308.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 4633: `2026-08-10T17:18:38.4314148Z BigQueryMetastoreCatalogIT > testWrite FAILED`
    - Canonical `normalize_test_id()`: `BigQueryMetastoreCatalogIT::testWrite`
  - RAW Line 8479: `2026-08-10T17:31:48.9284336Z BigQueryMetastoreCatalogIT > testWriteRead FAILED`
    - Canonical `normalize_test_id()`: `BigQueryMetastoreCatalogIT::testWriteRead`
  - RAW Line 8788: `2026-08-10T17:40:41.8287404Z BigQueryMetastoreCatalogIT > testReadWriteStreaming FAILED`
    - Canonical `normalize_test_id()`: `BigQueryMetastoreCatalogIT::testReadWriteStreaming`
  - RAW Line 8972: `2026-08-10T17:48:56.7296640Z BigQueryMetastoreCatalogIT > testStreamToPartitionedDynamicDestinations FAILED`
    - Canonical `normalize_test_id()`: `BigQueryMetastoreCatalogIT::testStreamToPartitionedDynamicDestinations`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 4

## 8. apache__dolphinscheduler__092883042571.txt
- **Source Repo:** `apache/dolphinscheduler`
- **Job ID:** `092883042571`
- **Fixture Filename:** `apache__dolphinscheduler__092883042571.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 2439: `2026-08-07T13:46:49.6026738Z [ERROR] testCreateDolphinDBDataSource  Time elapsed: 1.254 s  <<< ERROR!`
    - Canonical `normalize_test_id()`: `testCreateDolphinDBDataSource  Time elapsed: 1::254 s  <<< ERROR!`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 9. apache__flink__078003756269.txt
- **Source Repo:** `apache/flink`
- **Job ID:** `078003756269`
- **Fixture Filename:** `apache__flink__078003756269.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 26441: `2026-05-27T04:04:44.4971975Z May 27 04:04:44 04:04:44.495 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 2.485 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase::testRuntimeRestApiDocsUpToDate(Path)`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 10. apache__flink__079445374425.txt
- **Source Repo:** `apache/flink`
- **Job ID:** `079445374425`
- **Fixture Filename:** `apache__flink__079445374425.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 26465: `2026-06-04T04:09:23.4243464Z Jun 04 04:09:23 04:09:23.422 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 1.690 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase::testRuntimeRestApiDocsUpToDate(Path)`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 11. apache__hugegraph__084221602296.txt
- **Source Repo:** `apache/hugegraph`
- **Job ID:** `084221602296`
- **Fixture Filename:** `apache__hugegraph__084221602296.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 14455: `2026-06-30T06:02:25.8950390Z [ERROR] org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2.946 s  <<< ERROR!`
    - Canonical `normalize_test_id()`: `org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2::946 s  <<< ERROR!`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 12. apache__hugegraph__086386091934.txt
- **Source Repo:** `apache/hugegraph`
- **Job ID:** `086386091934`
- **Fixture Filename:** `apache__hugegraph__086386091934.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 20801: `2026-07-10T14:56:51.4090752Z [ERROR] testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.249 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0::249 s  <<< FAILURE!`
  - RAW Line 20805: `2026-07-10T14:56:51.4099617Z [ERROR] testUnsetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.22 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `testUnsetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0::22 s  <<< FAILURE!`
  - RAW Line 20809: `2026-07-10T14:56:51.4105732Z [ERROR] testSetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.227 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `testSetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0::227 s  <<< FAILURE!`
  - RAW Line 20813: `2026-07-10T14:56:51.4111044Z [ERROR] testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.224 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0::224 s  <<< FAILURE!`
  - RAW Line 20817: `2026-07-10T14:56:51.4116484Z [ERROR] testGetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.027 s  <<< FAILURE!`
    - Canonical `normalize_test_id()`: `testGetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0::027 s  <<< FAILURE!`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 5

## 13. apache__tika__090757115090.txt
- **Source Repo:** `apache/tika`
- **Job ID:** `090757115090`
- **Fixture Filename:** `apache__tika__090757115090.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  NO_TEST_OUTCOMES
- **Expected Class:** NO_TEST_OUTPUT
- **Expected Identifier Count:** 0

## 14. apache__zeppelin__077616025677.txt
- **Source Repo:** `apache/zeppelin`
- **Job ID:** `077616025677`
- **Fixture Filename:** `apache__zeppelin__077616025677.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 35269: `2026-05-24T18:24:22.9212470Z [ERROR] org.apache.zeppelin.rest.InterpreterRestApiTest.testCreatedInterpreterDependencies -- Time elapsed: 0.017 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.apache.zeppelin.rest.InterpreterRestApiTest::testCreatedInterpreterDependencies`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 15. dask__distributed__084645769341.txt
- **Source Repo:** `dask/distributed`
- **Job ID:** `084645769341`
- **Fixture Filename:** `dask__distributed__084645769341.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 2334: `2026-07-01T22:02:54.1287396Z FAILED distributed/tests/test_nanny.py::test_failure_during_worker_initialization[45-100]`
    - Canonical `normalize_test_id()`: `distributed/tests/test_nanny.py::test_failure_during_worker_initialization`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 16. dask__distributed__084757793457.txt
- **Source Repo:** `dask/distributed`
- **Job ID:** `084757793457`
- **Fixture Filename:** `dask__distributed__084757793457.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 1932: `2026-07-02T16:11:51.6888636Z FAILED distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100]`
    - Canonical `normalize_test_id()`: `distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 17. fla-org__flash-linear-attention__082566635619.txt
- **Source Repo:** `fla-org/flash-linear-attention`
- **Job ID:** `082566635619`
- **Fixture Filename:** `fla-org__flash-linear-attention__082566635619.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 709: `2026-06-21T11:35:36.7152616Z FAILED tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] - RuntimeError: No CUDA GPUs are available`
    - Canonical `normalize_test_id()`: `tests/models/test_modeling_forgetting_transformer.py::test_modeling`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 18. fla-org__flash-linear-attention__086098926451.txt
- **Source Repo:** `fla-org/flash-linear-attention`
- **Job ID:** `086098926451`
- **Fixture Filename:** `fla-org__flash-linear-attention__086098926451.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 779: `2026-07-09T10:42:18.0446013Z FAILED tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16] - TypeError: Can't instantiate abstract class FLALayer without an implementation for abstract method 'get_max_length'`
    - Canonical `normalize_test_id()`: `tests/models/test_modeling_comba.py::test_generation`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 19. floci-io__floci__078678232449.txt
- **Source Repo:** `floci-io/floci`
- **Job ID:** `078678232449`
- **Fixture Filename:** `floci-io__floci__078678232449.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 2128: `2026-05-30T21:20:12.8280399Z [ERROR] com.floci.test.CodeBuildTest.batchGetBuilds_eventuallySucceeds -- Time elapsed: 2.019 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `com.floci.test.CodeBuildTest::batchGetBuilds_eventuallySucceeds`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 20. floci-io__floci__085018489189.txt
- **Source Repo:** `floci-io/floci`
- **Job ID:** `085018489189`
- **Fixture Filename:** `floci-io__floci__085018489189.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 9808: `2026-07-03T14:22:14.0339511Z [ERROR] io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest.describeDefaultVpc -- Time elapsed: 0.025 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest::describeDefaultVpc`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 21. gurkenlabs__litiengine__079152380933.txt
- **Source Repo:** `gurkenlabs/litiengine`
- **Job ID:** `079152380933`
- **Fixture Filename:** `gurkenlabs__litiengine__079152380933.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 554: `2026-06-02T19:15:25.8858314Z AlignTests > getClampedLocation_InPoint() FAILED`
    - Canonical `normalize_test_id()`: `AlignTests::getClampedLocation_InPoint`
  - RAW Line 557: `2026-06-02T19:15:25.8860406Z AlignTests > getClampedLocation_OffPoint() FAILED`
    - Canonical `normalize_test_id()`: `AlignTests::getClampedLocation_OffPoint`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 2

## 22. linkedin__brooklin__077863844421.txt
- **Source Repo:** `linkedin/brooklin`
- **Job ID:** `077863844421`
- **Fixture Filename:** `linkedin__brooklin__077863844421.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 3577: `2026-05-26T13:05:09.6365165Z Gradle suite > Gradle test > com.linkedin.datastream.server.TestCoordinator::testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation FAILED`
    - Canonical `normalize_test_id()`: `com.linkedin.datastream.server.TestCoordinator::testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 23. nats-io__nats.java__080900237539.txt
- **Source Repo:** `nats-io/nats.java`
- **Job ID:** `080900237539`
- **Fixture Filename:** `nats-io__nats.java__080900237539.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 3033: `2026-06-11T20:42:58.2319604Z ConsumerConfigurationTests > testBuilder() FAILED`
    - Canonical `normalize_test_id()`: `io.nats.client.api.ConsumerConfigurationTests::testBuilder`
  - RAW Line 5704: `2026-06-11T20:44:54.8318517Z SimplificationTests > testReconnectOverOrdered() FAILED`
    - Canonical `normalize_test_id()`: `io.nats.client.impl.SimplificationTests::testReconnectOverOrdered`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 2

## 24. opentripplanner__opentripplanner__081988213338.txt
- **Source Repo:** `opentripplanner/opentripplanner`
- **Job ID:** `081988213338`
- **Fixture Filename:** `opentripplanner__opentripplanner__081988213338.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  NO_TEST_OUTCOMES
- **Expected Class:** NO_TEST_OUTPUT
- **Expected Identifier Count:** 0

## 25. opentripplanner__opentripplanner__092404918995.txt
- **Source Repo:** `opentripplanner/opentripplanner`
- **Job ID:** `092404918995`
- **Fixture Filename:** `opentripplanner__opentripplanner__092404918995.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  NO_TEST_OUTCOMES
- **Expected Class:** NO_TEST_OUTPUT
- **Expected Identifier Count:** 0

## 26. robo-code__robocode__084332182805.txt
- **Source Repo:** `robo-code/robocode`
- **Job ID:** `084332182805`
- **Fixture Filename:** `robo-code__robocode__084332182805.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 500: `2026-06-30T15:36:20.9720512Z TestFairPlay > run FAILED`
    - Canonical `normalize_test_id()`: `TestFairPlay::run`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 27. sirixdb__sirix__080642754882.txt
- **Source Repo:** `sirixdb/sirix`
- **Job ID:** `080642754882`
- **Fixture Filename:** `sirixdb__sirix__080642754882.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 1319: `2026-06-10T19:16:20.6268645Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'`
    - Canonical `normalize_test_id()`: `sirix-python-client/tests/test_sirix_async.py::test_database_create`
  - RAW Line 1322: `2026-06-10T19:16:20.6271210Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'`
    - Canonical `normalize_test_id()`: `sirix-python-client/tests/test_sirix_async.py::test_database_delete`
  - RAW Line 1325: `2026-06-10T19:16:20.6274000Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'`
    - Canonical `normalize_test_id()`: `sirix-python-client/tests/test_sirix_sync.py::test_create`
  - RAW Line 1328: `2026-06-10T19:16:20.6276807Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'`
    - Canonical `normalize_test_id()`: `sirix-python-client/tests/test_sirix_sync.py::test_delete`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 4

## 28. sirixdb__sirix__092352347826.txt
- **Source Repo:** `sirixdb/sirix`
- **Job ID:** `092352347826`
- **Fixture Filename:** `sirixdb__sirix__092352347826.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 384: `2026-08-05T15:30:56.2947870Z RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable() FAILED`
    - Canonical `normalize_test_id()`: `org.sirix.index.path.summary.RegionOnlyPredicateCountTest::negationConjoinedWithAnAnchoringLeafIsRepresentable`
  - RAW Line 387: `2026-08-05T15:30:57.7205480Z RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass() FAILED`
    - Canonical `normalize_test_id()`: `org.sirix.index.path.summary.RegionOnlyPredicateCountTest::numericAndBooleanFuseIntoOnePass`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 2

## 29. spiculedata__saiku__086592116219.txt
- **Source Repo:** `spiculedata/saiku`
- **Job ID:** `086592116219`
- **Fixture Filename:** `spiculedata__saiku__086592116219.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  NO_TEST_OUTCOMES
- **Expected Class:** NO_TEST_OUTPUT
- **Expected Identifier Count:** 0

## 30. thealgorithms__java__095336925353.txt
- **Source Repo:** `thealgorithms/java`
- **Job ID:** `095336925353`
- **Fixture Filename:** `thealgorithms__java__095336925353.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  NO_TEST_OUTCOMES
- **Expected Class:** NO_TEST_OUTPUT
- **Expected Identifier Count:** 0

## 31. unicode-org__cldr__090672967305.txt
- **Source Repo:** `unicode-org/cldr`
- **Job ID:** `090672967305`
- **Fixture Filename:** `unicode-org__cldr__090672967305.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 6090: `2026-07-29T19:01:50.5670322Z [ERROR] org.unicode.cldr.unittest.TestShim.TestAll -- Time elapsed: 1484 s <<< FAILURE!`
    - Canonical `normalize_test_id()`: `org.unicode.cldr.unittest.TestShim::TestAll`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 1

## 32. webauthn4j__webauthn4j__080348707704.txt
- **Source Repo:** `webauthn4j/webauthn4j`
- **Job ID:** `080348707704`
- **Fixture Filename:** `webauthn4j__webauthn4j__080348707704.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 1832: `2026-06-09T14:35:50.7781357Z EC2COSEKeyTest > json_serialize_deserialize_test() FAILED`
    - Canonical `normalize_test_id()`: `com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest::json_serialize_deserialize_test`
  - RAW Line 1917: `2026-06-09T14:35:52.1721696Z RSACOSEKeyTest > json_serialize_deserialize_test() FAILED`
    - Canonical `normalize_test_id()`: `com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest::json_serialize_deserialize_test`
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 2
