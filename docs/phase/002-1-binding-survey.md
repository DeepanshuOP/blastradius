# Phase 1: Survey the Binding Problem

## 1a. Sampled Test IDs

40 distinct test_ids were sampled from `data/interim/parsed_outcomes.parquet`, stratified by harness and `is_fqcn_qualified`:

```text
[gradle] [FQCN:False] Repo: apache/beam | ID: DoFnOperatorTest#testStateGCForStatefulFn
[gradle] [FQCN:False] Repo: apache/beam | ID: ViewTest#testListSideInputIsImmutable
[gradle] [FQCN:False] Repo: baomidou/mybatis-plus | ID: H2User2Test#testCollectionUpdateById
[gradle] [FQCN:False] Repo: apache/beam | ID: StreamingGroupAlsoByWindowsReshuffleDoFnTest#testEmpty
[gradle] [FQCN:False] Repo: apache/beam | ID: DataflowBatchWorkerHarnessTest#testNumberOfWorkerHarnessThreadsIsHonored
[gradle] [FQCN:False] Repo: apache/beam | ID: InMemoryReaderFactoryTest#testCreatePlainInMemoryReader
[gradle] [FQCN:False] Repo: apache/beam | ID: IcebergWriteSchemaTransformProviderTest#testWriteCreateTableWithPartitionSpec
[gradle] [FQCN:False] Repo: baomidou/mybatis-plus | ID: H2UserTest#testUpdateBatch
[gradle] [FQCN:True] Repo: sirixdb/sirix | ID: io.sirix.service.json.serialize.JsonSerializationRoundTripTest#testRoundTripEmptyArray
[gradle] [FQCN:True] Repo: diffplug/spotless | ID: com.diffplug.gradle.spotless.KotlinExtensionTest#testWithCustomMaxWidthDefaultStyleKtfmt
[gradle] [FQCN:True] Repo: apache/fineract | ID: org.apache.fineract.integrationtests.SchedulerJobsTestResults#testApplyPenaltyForOverdueLoansJobOutcome
[gradle] [FQCN:True] Repo: diffplug/spotless | ID: com.diffplug.spotless.maven.SpecificFilesTest#singleFile
[gradle] [FQCN:True] Repo: sirixdb/sirix | ID: io.sirix.access.node.json.JsonMultiRevisionTest#testGetHistoryFromTo
[gradle] [FQCN:True] Repo: apache/fineract | ID: org.apache.fineract.integrationtests.common.organisation.EntityDatatableChecksIntegrationTest#validateCreateClientWithEntityDatatableCheckWithFailure
[gradle] [FQCN:True] Repo: sirixdb/sirix | ID: io.sirix.cache.GlobalBufferManagerIntegrationTest#testDatabaseIdPersistence
[gradle] [FQCN:True] Repo: sirixdb/sirix | ID: io.sirix.diff.algorithm.JsonFMSETest#testObjectReorderWithinArrayComplex
[maven] [FQCN:False] Repo: opentripplanner/opentripplanner | ID: ExtraJourneyTest#testRejectUnmonitoredExtraJourney
[maven] [FQCN:False] Repo: opentripplanner/opentripplanner | ID: GraphQLIntegrationTest#graphQL
[maven] [FQCN:False] Repo: apache/atlas | ID: BasicSearchIT#testDiscoveryWithSearchParameters
[maven] [FQCN:False] Repo: opentripplanner/opentripplanner | ID: ArrivalDepartureMapperTest#mapAllValues
[maven] [FQCN:False] Repo: opentripplanner/opentripplanner | ID: ScooterRentalGeofencingTest#forwardAndArriveByBothFindPath
[maven] [FQCN:False] Repo: opentripplanner/opentripplanner | ID: UnconnectedParkAndRideTest#wayCrossingPR
[maven] [FQCN:False] Repo: opentripplanner/opentripplanner | ID: ScooterRentalGeofencingTest#arriveByAdjacentNoDropOffZonesDropsOutsideBothZones
[maven] [FQCN:False] Repo: apache/hugegraph | ID: SecurityManagerTest#init
[maven] [FQCN:True] Repo: castorini/anserini | ID: io.anserini.collection.TweetCollectionCompressedTest#checkDocumentParser
[maven] [FQCN:True] Repo: floci-io/floci | ID: io.github.hectorvent.floci.services.cloudformation.CloudFormationAsgLaunchTemplateIntegrationTest#mixedInstancesPolicyInstancesDistributionIsMapped
[maven] [FQCN:True] Repo: apache/tika | ID: org.apache.tika.metadata.MetadataInternalKeyGuardTest#testTrustedWriteBypassesGuard
[maven] [FQCN:True] Repo: apache/hugegraph | ID: org.apache.hugegraph.core.RamTableTest#testReloadFromFileAndQuery
[maven] [FQCN:True] Repo: apache/flink | ID: org.apache.flink.table.api.typeutils.TraversableSerializerUpgradeTest#upgradedSerializerIsValidAfterReconfiguration
[maven] [FQCN:True] Repo: castorini/anserini | ID: io.anserini.collection.MrTyDiCollectionIdTest#testStreamIteration
[maven] [FQCN:True] Repo: apache/hugegraph | ID: org.apache.hugegraph.cmd.InitStoreTest#testInitBackendFailsFastForPermanentException
[maven] [FQCN:True] Repo: apache/hugegraph | ID: org.apache.hugegraph.core.AuthTest#testLogin
[pytest] [FQCN:True] Repo: apache/beam | ID: apache_beam/runners/portability/spark_runner_test.py::SparkRunnerTest::test_pardo_side_and_main_outputs
[pytest] [FQCN:True] Repo: apache/beam | ID: apache_beam/runners/sdf_utils_test.py::ThreadsafeRestrictionTrackerTest::test_self_checkpoint_with_relative_time
[pytest] [FQCN:True] Repo: apache/beam | ID: apache_beam/io/gcp/bigquery_test.py::BigQueryStreamingInsertsErrorHandling::test_insert_rows_json_errors_retry_never_2
[pytest] [FQCN:True] Repo: apache/beam | ID: apache_beam/io/gcp/bigquery_json_it_test.py::BigQueryJsonIT::test_direct_read
[pytest] [FQCN:True] Repo: floci-io/floci | ID: tests/test_cloudformation_naming.py::TestCloudFormationAutoNaming::test_auto_naming_sns_topic_constraints
[pytest] [FQCN:True] Repo: dask/distributed | ID: distributed/tests/test_semaphore.py::test_metrics
[pytest] [FQCN:True] Repo: apache/beam | ID: apache_beam/io/gcp/bigquery_test.py::PubSubBigQueryIT::test_file_loads
[pytest] [FQCN:True] Repo: dask/distributed | ID: distributed/deploy/tests/test_local_env.py::test_basic
```

## 1b. Discovered Source Roots

Command used:
`git -C data/clones/<repo> ls-tree -r HEAD --name-only` followed by python heuristic filtering to detect `src/test/java`, `src/test/kotlin`, `src/test/groovy`, `tests`, `test`, `sdks/python`.

A sample of test roots discovered (up to 50):
```text
[apache/fineract]
  fineract-accounting/src/test/java
  fineract-client/src/test/java
  fineract-core/src/test/java
  fineract-doc/src/test/java
  fineract-e2e-tests-core/src/test/java
  fineract-e2e-tests-runner/src/test/java
  fineract-investor/src/test/java
  fineract-loan/src/test/java
  fineract-provider/src/test/java
[dask/distributed]
  distributed/cli/tests
  distributed/comm/tests
  distributed/dashboard/tests
  distributed/deploy/tests
  distributed/diagnostics/tests
  distributed/http/scheduler/tests
  distributed/http/tests
  distributed/http/worker/tests
  distributed/protocol/tests
  distributed/shuffle/tests
  distributed/tests
[floci-io/floci]
  compatibility-tests/compat-cdk/test
  compatibility-tests/compat-opentofu/test
  compatibility-tests/compat-terraform/test
  compatibility-tests/sdk-test-awscli/test
  compatibility-tests/sdk-test-go/tests
  compatibility-tests/sdk-test-java/src/test/java
  compatibility-tests/sdk-test-node/tests
  compatibility-tests/sdk-test-python/tests
  src/test/java
[sirixdb/sirix]
  bundles/sirix-core/src/test/java
  bundles/sirix-distributed/src/test/java
  bundles/sirix-distributed/src/test/kotlin
  bundles/sirix-jax-rx/src/test/java
  bundles/sirix-kotlin-api/src/test/kotlin
  bundles/sirix-kotlin-cli/src/test/kotlin
  bundles/sirix-mcp/src/test/java
  bundles/sirix-query/src/test/java
  bundles/sirix-rest-api/src/test/kotlin
  bundles/sirix-saxon/src/test/java
```

## 1c. Hit Rate at HEAD

Of the 40 sampled IDs, 29 belonged to cloned repos.
Using a basic heuristic resolver:
- **Hits: 18 / 29** (62% hit rate)

## 1d. Failure Classes

1. **Bare class name with no package (9 instances)**
   E.g. `DoFnOperatorTest` in `apache/beam`. Because the ID lacks a package prefix, it cannot be reliably mapped to a path (e.g. `org/apache/beam/.../DoFnOperatorTest.java`), resulting in an unresolved ("unqualified") status.
2. **Pytest paths rooted at a subdirectory (1 instance)**
   `tests/test_cloudformation_naming.py` in `floci-io/floci` does not exist at the repository root but at `compatibility-tests/sdk-test-python/tests/test_cloudformation_naming.py`.
3. **Not found at HEAD due to moves/renames (1 instance)**
   `distributed/deploy/tests/test_local_env.py` in `dask/distributed` no longer exists at HEAD (likely renamed or deleted since the test run). (Hypothesis #2)
4. **Nested classes**
   While not hit in this exact random 29 subset, nested classes like `Outer$Inner` require mapping to `Outer.java`, which a naive resolver misses.
5. **Multi-module ambiguity**
   If the same package/class path exists in multiple modules (e.g., `core/src/test/java/A.java` and `api/src/test/java/A.java`), the simple resolver might guess wrong or find multiple candidates. (Hypothesis #1)
