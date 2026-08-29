# Phase 4: Binding Rate Report

## 4b. Metrics

**Overall binding rate:** 3350 / 5429 (61.71%)

**Status breakdown:**
- exact: 3350 (61.71%)
- unqualified: 1970 (36.29%)
- not_found: 105 (1.93%)
- ambiguous: 4 (0.07%)

**Binding rate per (repo, harness):**
- Stirling-Tools/Stirling-PDF [gradle]: 4 / 307 (1.30%)
- apache/atlas [maven]: 112 / 114 (98.25%)
- apache/beam [gradle]: 32 / 1011 (3.17%)
- apache/beam [pytest]: 683 / 696 (98.13%)
- apache/dolphinscheduler [maven]: 240 / 262 (91.60%)
- apache/fineract [gradle]: 184 / 187 (98.40%)
- apache/tika [maven]: 157 / 165 (95.15%)
- baomidou/mybatis-plus [gradle]: 0 / 163 (0.00%)
- castorini/anserini [maven]: 534 / 560 (95.36%)
- dask/distributed [pytest]: 109 / 114 (95.61%)
- diffplug/spotless [gradle]: 91 / 92 (98.91%)
- floci-io/floci [maven]: 431 / 431 (100.00%)
- floci-io/floci [pytest]: 17 / 18 (94.44%)
- sirixdb/sirix [gradle]: 756 / 1305 (57.93%)
- sirixdb/sirix [pytest]: 0 / 4 (0.00%)

**Repos below 70% gate:** 4 / 12 (Stirling-Tools, apache/beam, baomidou/mybatis-plus, sirixdb/sirix).

**Binding rate split by is_fqcn_qualified:**
- False: 0 / 1970 (0.00%)
- True: 3350 / 3459 (96.85%)

**20 sampled UNBOUND test_ids:**
- Repo: baomidou/mybatis-plus | Status: unqualified | ID: H2UserMapperTest#testSaveOrUpdateBatch2
- Repo: sirixdb/sirix | Status: unqualified | ID: FrameSlotAllocatorTest#exhaustionReturnsNull
- Repo: apache/beam | Status: unqualified | ID: GroupingShuffleReaderTest#testBytesReadNonEmptyShuffleDataTwiceUnsorted
- Repo: Stirling-Tools/Stirling-PDF | Status: unqualified | ID: CertificateValidationServiceTest#testIsSelfSigned_SelfSignedCert
- Repo: apache/beam | Status: unqualified | ID: StorageApiSinkSchemaUpdateIT#testExactlyOnceWithIgnoreUnknownValues
- Repo: apache/beam | Status: unqualified | ID: WindmillStateCacheTest#conflictingUserAndSystemTags
- Repo: Stirling-Tools/Stirling-PDF | Status: unqualified | ID: McpOAuthIntegrationTest#noToken_returns401WithResourceMetadataHeader
- Repo: apache/beam | Status: unqualified | ID: SimpleParDoFnTest#testOutputsPerElementCounterDisabledViaExperiment
- Repo: apache/beam | Status: unqualified | ID: MongoDBGridFSIOTest#classMethod
- Repo: Stirling-Tools/Stirling-PDF | Status: unqualified | ID: InternalApiClientTest#postRejectsAiEndpointsOutsideToolsSubnamespace
- Repo: sirixdb/sirix | Status: unqualified | ID: PageTest#initializationError
- Repo: baomidou/mybatis-plus | Status: unqualified | ID: H2UserTest#testLambdaTypeHandler
- Repo: sirixdb/sirix | Status: unqualified | ID: MinimumCommitTest#testCommitMessage
- Repo: apache/beam | Status: unqualified | ID: IcebergIOReadTest#testStreamingReadBetweenTimestamps
- Repo: Stirling-Tools/Stirling-PDF | Status: unqualified | ID: InviteLinkControllerTest#generateInviteLinkBlocksOnLicenseLimit
- Repo: sirixdb/sirix | Status: unqualified | ID: ParallelJsonShredderTest#existingResourceNameFailsFastWithoutTouchingAnything
- Repo: Stirling-Tools/Stirling-PDF | Status: unqualified | ID: AiWorkflowServiceTest#generateFileStoresContentDirectlyWithoutToolCall
- Repo: apache/beam | Status: unqualified | ID: StorageApiSinkFailedRowsIT#testInvalidRowCaughtByBigquery
- Repo: apache/beam | Status: unqualified | ID: DataflowWorkProgressUpdaterTest#workProgressAdaptsNextDuration
- Repo: sirixdb/sirix | Status: unqualified | ID: LinuxMemorySegmentAllocatorTest#testAllocate64KB

## 4c. Gate 1.5 Assessment

Gate 1.5 (≥70% binding rate) is **missed** overall (61.71%).

The dominant failure class is `unqualified` identifiers (36.29% of all tests). These are bare class names primarily originating from Gradle harness output, missing the package path.
This is **fixable**, not structural. According to Decision D-31, Gradle logs emit bare identifiers in summaries but the FQCN can be recovered via a suffix join from stack trace frames. A parser update to implement this suffix join will lift `is_fqcn_qualified` and thus the binding rate above 70%.
