# Phase 021B — Blind Ground-Truth Worksheet (re-keyed)

Fill `HAND_EXPECTED` for each row below by reading ONLY the `RAW_LINE` evidence shown in that
row. Do not consult `docs/phase/021-expectation-table.md`, `parsed_outcomes.parquet`, any
parser source under `src/parse/`, or any prior HAND_EXPECTED value while filling this sheet.
Rows join to `docs/phase/021-expectation-table.md` by `row_key` — the first 12 hex characters
of `sha256(fixture_filename + "\n" + raw_evidence_lines_joined_by_"\n")`, computed over the
RAW bytes of the fixture name and evidence lines, not any display transform of them. `row_key`
is recomputed independently by `analysis/expectation_diff.py`; nothing here is a trusted
stored value.

## KNOWN LIMITATION

The parser's output for all 47 rows was displayed to the operator before this worksheet
was filled. Rows are re-keyed and shuffled to reduce anchoring, but this corpus is FITTED,
not blind. It is a regression fixture. No precision figure may be derived from it.

This worksheet was filled by the coding agent, not by the operator. The agent generated
the underlying table and had all 47 parser outputs in context while filling. Agreement rows
are therefore self-agreement and carry no evidential weight. Only disagreement rows are
evidence. This corpus is a regression fixture and yields no precision figure.

`RAW_LINE` text is shown as a Python `repr()` of the exact source line, fenced. This is a
display transform only: control bytes (ANSI colour escapes, etc.) are shown as literal
escape-sequence text instead of corrupting rendering, and the fence means no character in the
line needs piecemeal escaping. No byte of the underlying line is added, removed, or reordered
by this transform — but `row_key` above is computed from the raw bytes, before this
transform, not from the displayed repr() text.

## Answering convention

- Java canonical form is `<fully.qualified.ClassName>#<methodName>`, no trailing parentheses.
- Python canonical form is `<path/to/file.py>::<test_name>`, with any parameter set omitted.
- Write the package ONLY if it appears somewhere in the raw evidence shown. Never infer or
  guess a package (D-39).
- If the evidence does not identify a test, write `NO_TEST` and a short reason.

Some rows show two evidence lines, labelled "evidence line 1" / "evidence line 2" in the order
they appear in the source log. The label carries no meaning beyond that order — it does not
indicate which line (if either) supplies the class, the package, or the method.

Row order below is shuffled (seed 20260902) and headed by `row_key`, not by any sequential
number — no sequential row number from any prior version of this worksheet appears anywhere
below.

---

## Row 5ce7156d4c23 — apache__atlas__085339439869.txt

RAW_LINE:
```
'2026-07-06T09:38:44.7360321Z [ERROR] org.apache.atlas.kafka.KafkaNotificationTest.setup -- Time elapsed: 17.90 s <<< FAILURE!'
```

HAND_EXPECTED: org.apache.atlas.kafka.KafkaNotificationTest#setup

---

## Row f74f48f3de5e — apache__hugegraph__086386091934.txt

RAW_LINE:
```
'2026-07-10T14:56:51.4116484Z [ERROR] testGetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.027 s  <<< FAILURE!'
```

HAND_EXPECTED: org.apache.hugegraph.api.GraphsApiStandaloneTest#testGetDefaultGraphReturnsFriendlyError

---

## Row 51208f55ec56 — apache__beam__086101982024.txt

RAW_LINE:
```
'2026-07-09T11:10:15.6517616Z HadoopFormatIOElasticTest > testHifIOWithElasticQuery FAILED'
```

HAND_EXPECTED: HadoopFormatIOElasticTest#testHifIOWithElasticQuery

---

## Row 9be730822015 — gurkenlabs__litiengine__079152380933.txt

RAW_LINE:
```
'2026-06-02T19:15:25.8860406Z AlignTests > getClampedLocation_OffPoint() FAILED'
```

HAND_EXPECTED: AlignTests#getClampedLocation_OffPoint

---

## Row 6d271ffe6080 — Stirling-Tools__Stirling-PDF__081016081705.txt

RAW_LINE:
```
'2026-06-12T11:17:50.6211639Z UIDataControllerTest > getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical() FAILED'
```

HAND_EXPECTED: UIDataControllerTest#getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical

---

## Row 6a5fd9d35a1f — apache__beam__086101982024.txt

RAW_LINE:
```
'2026-07-09T11:09:03.8539833Z HadoopFormatIOCassandraTest > classMethod FAILED'
```

HAND_EXPECTED: NO_TEST - JUnit4 synthetic classMethod descriptor for a class-level @BeforeClass / @AfterClass failure; names no source method (D-46)

---

## Row 068f9bb711d8 — unicode-org__cldr__090672967305.txt

RAW_LINE:
```
'2026-07-29T19:01:50.5670322Z [ERROR] org.unicode.cldr.unittest.TestShim.TestAll -- Time elapsed: 1484 s <<< FAILURE!'
```

HAND_EXPECTED: org.unicode.cldr.unittest.TestShim#TestAll

---

## Row 0e5d3a59b174 — robo-code__robocode__084332182805.txt

RAW_LINE:
```
'2026-06-30T15:36:20.9720512Z TestFairPlay > run FAILED'
```

HAND_EXPECTED: TestFairPlay#run

---

## Row 80b12bf4ef69 — apache__beam__093527298308.txt

RAW_LINE:
```
'2026-08-10T17:31:48.9284336Z BigQueryMetastoreCatalogIT > testWriteRead FAILED'
```

HAND_EXPECTED: BigQueryMetastoreCatalogIT#testWriteRead

---

## Row ff36ea9d0dbe — apache__beam__093527298308.txt

RAW_LINE:
```
'2026-08-10T17:40:41.8287404Z BigQueryMetastoreCatalogIT > testReadWriteStreaming FAILED'
```

HAND_EXPECTED: BigQueryMetastoreCatalogIT#testReadWriteStreaming

---

## Row 3f74c8efd8d5 — apache__hugegraph__086386091934.txt

RAW_LINE:
```
'2026-07-10T14:56:51.4111044Z [ERROR] testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.224 s  <<< FAILURE!'
```

HAND_EXPECTED: org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError

---

## Row 1b4f2d40df89 — Stirling-Tools__Stirling-PDF__081185748047.txt

RAW_LINE:
```
'2026-06-13T11:09:29.5112976Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldQueueJob() FAILED'
```

HAND_EXPECTED: JobQueueTest#shouldQueueJob

---

## Row 7a18936bd0b6 — webauthn4j__webauthn4j__080348707704.txt

RAW_LINE (evidence line 1):
```
'2026-06-09T14:35:52.1721696Z RSACOSEKeyTest > json_serialize_deserialize_test() FAILED'
```

RAW_LINE (evidence line 2):
```
'2026-06-09T14:35:52.1741411Z         at app//com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest.json_serialize_deserialize_test(RSACOSEKeyTest.java:116)'
```

HAND_EXPECTED: com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest#json_serialize_deserialize_test

---

## Row 561a20998890 — apache__hugegraph__086386091934.txt

RAW_LINE:
```
'2026-07-10T14:56:51.4090752Z [ERROR] testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.249 s  <<< FAILURE!'
```

HAND_EXPECTED: org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError

---

## Row 3269f76d726f — sirixdb__sirix__080642754882.txt

RAW_LINE:
```
"2026-06-10T19:16:20.6274000Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'"
```

HAND_EXPECTED: sirix-python-client/tests/test_sirix_sync.py::test_create

---

## Row bc6fb538ad06 — agno-agi__agno__092042274925.txt

RAW_LINE:
```
"2026-08-04T15:29:41.6265273Z FAILED tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields - AttributeError: 'str' object has no attribute 'rating'"
```

HAND_EXPECTED: tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields

---

## Row d2acfc050586 — apache__beam__093527298308.txt

RAW_LINE:
```
'2026-08-10T17:48:56.7296640Z BigQueryMetastoreCatalogIT > testStreamToPartitionedDynamicDestinations FAILED'
```

HAND_EXPECTED: BigQueryMetastoreCatalogIT#testStreamToPartitionedDynamicDestinations

---

## Row 4d25554936d1 — dask__distributed__084645769341.txt

RAW_LINE (evidence line 1):
```
'2026-07-01T22:02:10.3797799Z distributed/tests/test_nanny.py::test_failure_during_worker_initialization[45-100] \x1b[31mFAILED\x1b[0m\x1b[31m [ 45%]\x1b[0m'
```

RAW_LINE (evidence line 2):
```
'2026-07-01T22:02:54.1287396Z \x1b[31mFAILED\x1b[0m distributed/tests/test_nanny.py::\x1b[1mtest_failure_during_worker_initialization[45-100]\x1b[0m - TimeoutError: Test timeout (30) hit after 30.000552999999968s.'
```

HAND_EXPECTED: distributed/tests/test_nanny.py::test_failure_during_worker_initialization

---

## Row 906fd9b5040d — floci-io__floci__085018489189.txt

RAW_LINE:
```
'2026-07-03T14:22:14.0339511Z [ERROR] io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest.describeDefaultVpc -- Time elapsed: 0.025 s <<< FAILURE!'
```

HAND_EXPECTED: io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest#describeDefaultVpc

---

## Row 9e4d4bd8e591 — apache__beam__086101982024.txt

RAW_LINE:
```
'2026-07-09T11:10:15.1523730Z HadoopFormatIOElasticTest > testHifIOWithElastic FAILED'
```

HAND_EXPECTED: HadoopFormatIOElasticTest#testHifIOWithElastic

---

## Row 4ca072d0ebcf — gurkenlabs__litiengine__079152380933.txt

RAW_LINE:
```
'2026-06-02T19:15:25.8858314Z AlignTests > getClampedLocation_InPoint() FAILED'
```

HAND_EXPECTED: AlignTests#getClampedLocation_InPoint

---

## Row e2d48d930cf9 — agno-agi__agno__079305370965.txt

RAW_LINE (evidence line 1):
```
'2026-06-03T13:34:59.9163951Z libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer FAILED [ 12%]'
```

RAW_LINE (evidence line 2):
```
"2026-06-03T13:39:13.1736939Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'cl100k_base' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/Xenova/gpt-4/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/cl100k_base/resolve/main/tokenizer.json: status code 429'}"
```

HAND_EXPECTED: libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer

---

## Row d6556fd08827 — sirixdb__sirix__080642754882.txt

RAW_LINE:
```
"2026-06-10T19:16:20.6268645Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'"
```

HAND_EXPECTED: sirix-python-client/tests/test_sirix_async.py::test_database_create

---

## Row bee7e94431f6 — Stirling-Tools__Stirling-PDF__081185748047.txt

RAW_LINE:
```
'2026-06-13T11:09:29.5110981Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldCancelJob() FAILED'
```

HAND_EXPECTED: JobQueueTest#shouldCancelJob

---

## Row 83a64a4e66bd — Stirling-Tools__Stirling-PDF__081185748047.txt

RAW_LINE:
```
'2026-06-13T11:09:29.5112069Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldGetQueueStats() FAILED'
```

HAND_EXPECTED: JobQueueTest#shouldGetQueueStats

---

## Row 0b1dcde22361 — apache__dolphinscheduler__092883042571.txt

RAW_LINE (evidence line 1):
```
'2026-08-07T13:46:49.9368742Z [ERROR]   DolphinDBDataSourceE2ETest.testCreateDolphinDBDataSource:79 » NoSuchElement no...'
```

RAW_LINE (evidence line 2):
```
'2026-08-07T13:46:49.6025516Z [ERROR] Tests run: 2, Failures: 0, Errors: 1, Skipped: 1, Time elapsed: 97.179 s <<< FAILURE! - in org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest'
```

HAND_EXPECTED: org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest#testCreateDolphinDBDataSource

---

## Row dd21bdcdf521 — sirixdb__sirix__080642754882.txt

RAW_LINE:
```
"2026-06-10T19:16:20.6276807Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'"
```

HAND_EXPECTED: sirix-python-client/tests/test_sirix_sync.py::test_delete

---

## Row 36ea4df7a8e6 — apache__flink__079445374425.txt

RAW_LINE:
```
'2026-06-04T04:09:23.4243464Z Jun 04 04:09:23 04:09:23.422 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 1.690 s <<< FAILURE!'
```

HAND_EXPECTED: org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate

---

## Row 819c2f5d708c — webauthn4j__webauthn4j__080348707704.txt

RAW_LINE (evidence line 1):
```
'2026-06-09T14:35:50.7781357Z EC2COSEKeyTest > json_serialize_deserialize_test() FAILED'
```

RAW_LINE (evidence line 2):
```
'2026-06-09T14:35:50.7805802Z         at app//com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest.json_serialize_deserialize_test(EC2COSEKeyTest.java:130)'
```

HAND_EXPECTED: com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest#json_serialize_deserialize_test

---

## Row 185149df8b18 — apache__zeppelin__077616025677.txt

RAW_LINE:
```
'2026-05-24T18:24:22.9212470Z [ERROR] org.apache.zeppelin.rest.InterpreterRestApiTest.testCreatedInterpreterDependencies -- Time elapsed: 0.017 s <<< FAILURE!'
```

HAND_EXPECTED: org.apache.zeppelin.rest.InterpreterRestApiTest#testCreatedInterpreterDependencies

---

## Row 2bec1480577b — apache__hugegraph__084221602296.txt

RAW_LINE (evidence line 1):
```
"2026-06-30T06:02:26.2679783Z [ERROR]   CoreTestSuite.init:98 » Huge Failed to listen 'HUGEGRAPH/hg/EVENT/GRAPH/SCHEMA..."
```

RAW_LINE (evidence line 2):
```
'2026-06-30T06:02:25.8930403Z [ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 2.946 s <<< FAILURE! - in org.apache.hugegraph.core.CoreTestSuite'
```

HAND_EXPECTED: org.apache.hugegraph.core.CoreTestSuite#init

---

## Row 2598cf91f544 — sirixdb__sirix__092352347826.txt

RAW_LINE:
```
'2026-08-05T15:30:56.2947870Z RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable() FAILED'
```

HAND_EXPECTED: RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable

---

## Row 8aabd9035ed4 — apache__beam__093527298308.txt

RAW_LINE:
```
'2026-08-10T17:18:38.4314148Z BigQueryMetastoreCatalogIT > testWrite FAILED'
```

HAND_EXPECTED: BigQueryMetastoreCatalogIT#testWrite

---

## Row 57e11a35966e — apache__hugegraph__084221602296.txt

RAW_LINE:
```
'2026-06-30T06:02:25.8950390Z [ERROR] org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2.946 s  <<< ERROR!'
```

HAND_EXPECTED: NO_TEST - class-level suite error; the line names only the class org.apache.hugegraph.core.CoreTestSuite and no test method

---

## Row 2724bcfc3dff — nats-io__nats.java__080900237539.txt

RAW_LINE (evidence line 1):
```
'2026-06-11T20:42:58.2319604Z ConsumerConfigurationTests > testBuilder() FAILED'
```

RAW_LINE (evidence line 2):
```
'2026-06-11T20:42:58.2327031Z         at io.nats.client.api.ConsumerConfigurationTests.testBuilder(ConsumerConfigurationTests.java:172)'
```

HAND_EXPECTED: io.nats.client.api.ConsumerConfigurationTests#testBuilder

---

## Row b0980797f104 — fla-org__flash-linear-attention__082566635619.txt

RAW_LINE (evidence line 1):
```
'2026-06-21T11:35:36.7113481Z tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] FAILED'
```

RAW_LINE (evidence line 2):
```
'2026-06-21T11:35:36.7152616Z FAILED tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] - RuntimeError: No CUDA GPUs are available'
```

HAND_EXPECTED: tests/models/test_modeling_forgetting_transformer.py::test_modeling

---

## Row f433234b4233 — fla-org__flash-linear-attention__086098926451.txt

RAW_LINE (evidence line 1):
```
'2026-07-09T10:42:18.0395527Z tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16] FAILED'
```

RAW_LINE (evidence line 2):
```
"2026-07-09T10:42:18.0446013Z FAILED tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16] - TypeError: Can't instantiate abstract class FLALayer without an implementation for abstract method 'get_max_length'"
```

HAND_EXPECTED: tests/models/test_modeling_comba.py::test_generation

---

## Row 015d3b2416a0 — dask__distributed__084757793457.txt

RAW_LINE (evidence line 1):
```
'2026-07-02T11:27:28.6182458Z distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100] \x1b[31mFAILED\x1b[0m\x1b[31m [  8%]\x1b[0m'
```

RAW_LINE (evidence line 2):
```
'2026-07-02T12:00:40.2795756Z \x1b[31mFAILED\x1b[0m distributed/tests/test_active_memory_manager.py::\x1b[1mtest_RetireWorker_stress[False-17-100]\x1b[0m - TimeoutError: Test timeout (180) hit after 179.9853481s.'
```

HAND_EXPECTED: distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress

---

## Row 9ad2fff53c74 — sirixdb__sirix__092352347826.txt

RAW_LINE:
```
'2026-08-05T15:30:57.7205480Z RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass() FAILED'
```

HAND_EXPECTED: RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass

---

## Row 6e0955e465d6 — apache__hugegraph__086386091934.txt

RAW_LINE:
```
'2026-07-10T14:56:51.4099617Z [ERROR] testUnsetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.22 s  <<< FAILURE!'
```

HAND_EXPECTED: org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphReturnsFriendlyError

---

## Row da93371bad8a — linkedin__brooklin__077863844421.txt

RAW_LINE:
```
'2026-05-26T13:05:09.6365165Z Gradle suite > Gradle test > com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation FAILED'
```

HAND_EXPECTED: com.linkedin.datastream.server.TestCoordinator#testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation

---

## Row a235cadb12ea — agno-agi__agno__079305370965.txt

RAW_LINE (evidence line 1):
```
'2026-06-03T13:34:59.8448071Z libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer FAILED [ 12%]'
```

RAW_LINE (evidence line 2):
```
"2026-06-03T13:39:13.1733817Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'gpt2' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/openai-community/gpt2/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/gpt2/resolve/main/tokenizer.json: status code 429'}"
```

HAND_EXPECTED: libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer

---

## Row b9184834c4c8 — nats-io__nats.java__080900237539.txt

RAW_LINE (evidence line 1):
```
'2026-06-11T20:44:54.8318517Z SimplificationTests > testReconnectOverOrdered() FAILED'
```

RAW_LINE (evidence line 2):
```
'2026-06-11T20:44:54.8326421Z         at io.nats.client.impl.SimplificationTests.testReconnectOverOrdered(SimplificationTests.java:1897)'
```

HAND_EXPECTED: io.nats.client.impl.SimplificationTests#testReconnectOverOrdered

---

## Row bfce04c42964 — Stirling-Tools__Stirling-PDF__081185748047.txt

RAW_LINE:
```
'2026-06-13T11:09:29.5109777Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldCheckIfJobIsQueued() FAILED'
```

HAND_EXPECTED: JobQueueTest#shouldCheckIfJobIsQueued

---

## Row 7a69e71e197c — apache__hugegraph__086386091934.txt

RAW_LINE:
```
'2026-07-10T14:56:51.4105732Z [ERROR] testSetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.227 s  <<< FAILURE!'
```

HAND_EXPECTED: org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphReturnsFriendlyError

---

## Row 63351e37b366 — sirixdb__sirix__080642754882.txt

RAW_LINE:
```
"2026-06-10T19:16:20.6271210Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'"
```

HAND_EXPECTED: sirix-python-client/tests/test_sirix_async.py::test_database_delete

---

## Row cff48077c013 — apache__flink__078003756269.txt

RAW_LINE:
```
'2026-05-27T04:04:44.4971975Z May 27 04:04:44 04:04:44.495 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 2.485 s <<< FAILURE!'
```

HAND_EXPECTED: org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate

---
