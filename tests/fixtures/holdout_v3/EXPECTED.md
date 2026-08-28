# Hand-Labelled Held-Out Fixture Corpus (T1.1c-v3 Quarantined Evaluation Ground Truth)

This document contains hand-labelled ground truth test outcome expectations for the 30 held-out raw job logs in `tests/fixtures/holdout_v3/`.
All labels were identified **by eye directly from raw log text** without consulting, importing, or running any BlastRadius extractor or classifier.
Per ROADMAP §25.3, §26.1, DECISIONS.md (D-27, D-29, D-31), and AGENTS.md, this corpus is set aside untouched and is **NEVER** executed or scored during parser development. No parser was run against this corpus.

## Sampling Protocol & Constraints
- **Seed**: Deterministic PRNG seeded with constant `SEED = 20260828`.
- **Two-Stage Selection & Replacement**:
  - Initial draw at seed 20260828 selected `apache__atlas__087818837127.txt` (97.35 MB uncompressed) and `apache__tika__090317145602.txt` (11.71 MB uncompressed).
  - Both logs breached the 8 MB uncompressed cap added after initial draw.
  - Under documented replacement (Amendment 1), these two oversize fixtures were replaced with the next eligible Maven (Aggregate) candidates from the SAME seeded permutation at seed 20260828:
    1. `apache__tika__079360406349.txt` (0.13 MB uncompressed, 1 failure) replacing `apache__atlas__087818837127.txt`.
    2. `castorini__anserini__087122010631.txt` (0.14 MB uncompressed, 3 failures) replacing `apache__tika__090317145602.txt`.
  - Both replacements are Maven (Aggregate), preserving harness balance by construction.
- **Partition A: Core Partition (Fixtures 1–25)**:
  - 25 logs across 14 distinct unseen repositories (all Java frame repositories).
  - 18 failure-bearing logs (10 Maven/Surefire, 8 Gradle) with 1–4 failures each.
  - 7 non-failing logs (5 NO_SUMMARY, 2 Maven Clean).
  - **Zero Repository Overlap**: 0 overlap with repositories in `tests/fixtures/logs/` (Dev) and `tests/fixtures/holdout/` (v2). All 14 repositories in Partition A are completely unseen in prior corpora.
  - Maximum 2 logs per repository.
- **Partition B: Pytest Supplement Partition (Fixtures 26–30)**:
  - 5 failure-bearing Pytest logs sampled from `apache/beam`.
  - **Partitioning Rationale**: All Pytest logs on disk originate from `apache/beam`. To preserve zero-repository overlap in the primary evaluation, the 25 core fixtures are isolated in Partition A. Partition B provides held-out generalization evidence for the Pytest extractor with zero log-level overlap against Dev and v2.
  - `apache/beam` is a Java repository in `data/frame/frame_v1.csv`, so the all-Java limitation stands and zero Python-repo logs are in this corpus.
  - Both partitions are independently scorable.
- **All-Java Limitation & Pinned Manifest**:
  - The Python sweep was actively capturing Stage 4 logs during construction. To eliminate drift and guarantee determinism, candidates are drawn from a pinned manifest (`analysis/holdout_v3_manifest.json`) bounded strictly to Java-frame repositories in `data/frame/frame_v1.csv`.
- **8 MB Uncompressed Cap & Sampling Limitation**:
  - All fixtures are bounded by `MAX_UNCOMPRESSED_BYTES = 8 * 1024 * 1024` (8 MB) verified via gzip ISIZE trailer.
  - This cap removed 2.98% of the unseen candidate pool (49 / 1,642 unseen-repo candidate logs). Excluding large logs is a stated sampling limitation because long multi-hour integration runs differ systematically.
- **Gradle-Clean Blind Spot**:
  - Across the raw pool on disk, all Gradle logs with summary lines are failure-bearing, while green Gradle builds produce no harness summary banner. All zero-failure summary logs are Maven. The clean partition is therefore Maven-biased by construction.
- **Scope Clarification on Fixture 19**:
  - Fixture 19 (`atmosphere__atmosphere__078279224469.txt`) is a Playwright/Node log outside D-03 Java/Python parser scope and contributes zero test identifiers (`NO_TEST_OUTCOMES`).
- **Identifier Counts & Scoring Denominator**:
  - **Partition A**: 31 per-fixture failure instances (Exp sum in audit), 28 globally distinct canonical test identifiers (3 tests in `rptools/maptool` fail across fixtures 11 & 13).
  - **Partition B**: 16 per-fixture failure instances (Exp sum in audit), 10 globally distinct canonical test identifiers (6 tests in `apache/beam` fail across fixtures 26 & 27).
  - **Total Corpus**: 47 per-fixture failure instances (Exp sum in audit), 38 globally distinct canonical test identifiers.
  - The per-fixture failure count (Exp sum: 31 for Partition A, 16 for Partition B, 47 total) is the official evaluation scoring denominator.

---

# PARTITION A: Core Fixtures (Zero Repository Overlap)

## 1. apache__tika__079360406349.txt
- **Source Repo:** `apache/tika`
- **Job ID:** `079360406349`
- **Parent Run ID:** `26903074924`
- **Fixture Filename:** `apache__tika__079360406349.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 969: `[ERROR] org.apache.tika.mime.MimeDetectionTest.testDetection -- Time elapsed: 0.070 s <<< FAILURE!` (Stack frame Line 974: `at org.apache.tika.mime.MimeDetectionTest.testDetection(MimeDetectionTest.java:92)`)
  - Canonical `normalize_test_id()`: `org.apache.tika.mime.MimeDetectionTest#testDetection`
- **Confidence:** CERTAIN

---

## 2. apache__tika__095664956225.txt
- **Source Repo:** `apache/tika`
- **Job ID:** `095664956225`
- **Parent Run ID:** `32122224074`
- **Fixture Filename:** `apache__tika__095664956225.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 14312: `[ERROR] org.apache.tika.pipes.filesystem.HandlerTypeTest.typedDocumentContractOverLiveServer -- Time elapsed: 0.512 s <<< FAILURE!` (Stack frame Line 14315: `at org.apache.tika.pipes.filesystem.HandlerTypeTest.typedDocumentContractOverLiveServer(HandlerTypeTest.java:395)`)
  - Canonical `normalize_test_id()`: `org.apache.tika.pipes.filesystem.HandlerTypeTest#typedDocumentContractOverLiveServer`
- **Confidence:** CERTAIN

---

## 3. apache__streampark__089739161046.txt
- **Source Repo:** `apache/streampark`
- **Job ID:** `089739161046`
- **Parent Run ID:** `30154978928`
- **Fixture Filename:** `apache__streampark__089739161046.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 521: `[ERROR] formatCSTTimeShouldFormatCorrectly  Time elapsed: 0.077 s  <<< FAILURE!` (Stack frame Line 523: `at org.apache.streampark.common.util.DateUtilsTest.formatCSTTimeShouldFormatCorrectly(DateUtilsTest.java:170)`)
    - Canonical `normalize_test_id()`: `org.apache.streampark.common.util.DateUtilsTest#formatCSTTimeShouldFormatCorrectly`
  - RAW Line 525: `[ERROR] secondOfDayShouldReturnCorrectSecond  Time elapsed: 0.001 s  <<< FAILURE!` (Stack frame Line 527: `at org.apache.streampark.common.util.DateUtilsTest.secondOfDayShouldReturnCorrectSecond(DateUtilsTest.java:77)`)
    - Canonical `normalize_test_id()`: `org.apache.streampark.common.util.DateUtilsTest#secondOfDayShouldReturnCorrectSecond`
  - RAW Line 529: `[ERROR] getTimeShouldReturnMilliseconds  Time elapsed: 0.011 s  <<< FAILURE!` (Stack frame Line 531: `at org.apache.streampark.common.util.DateUtilsTest.getTimeShouldReturnMilliseconds(DateUtilsTest.java:121)`)
    - Canonical `normalize_test_id()`: `org.apache.streampark.common.util.DateUtilsTest#getTimeShouldReturnMilliseconds`
  - RAW Line 533: `[ERROR] minuteOfDayShouldReturnCorrectMinute  Time elapsed: 0.001 s  <<< FAILURE!` (Stack frame Line 535: `at org.apache.streampark.common.util.DateUtilsTest.minuteOfDayShouldReturnCorrectMinute(DateUtilsTest.java:69)`)
    - Canonical `normalize_test_id()`: `org.apache.streampark.common.util.DateUtilsTest#minuteOfDayShouldReturnCorrectMinute`
- **Confidence:** CERTAIN

---

## 4. apache__streampark__086548451141.txt
- **Source Repo:** `apache/streampark`
- **Job ID:** `086548451141`
- **Parent Run ID:** `29153580437`
- **Fixture Filename:** `apache__streampark__086548451141.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 4539: `[ERROR] org.apache.streampark.e2e.cases.FlinkSQL120OnYarnTest  Time elapsed: 119.609 s  <<< ERROR!` (Class-level container init failure, Surefire summary line 4538: `in org.apache.streampark.e2e.cases.FlinkSQL120OnYarnTest`)
  - Canonical `normalize_test_id()`: `org.apache.streampark.e2e.cases.FlinkSQL120OnYarnTest`
- **Confidence:** CERTAIN

---

## 5. apache__atlas__080179038270.txt
- **Source Repo:** `apache/atlas`
- **Job ID:** `080179038270`
- **Parent Run ID:** `27161849057`
- **Fixture Filename:** `apache__atlas__080179038270.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 3382: `[ERROR] org.apache.atlas.discovery.AtlasDiscoveryServiceTest.setup  Time elapsed: 115.952 s  <<< FAILURE!` (Stack frame Line 3384: `at org.apache.atlas.discovery.AtlasDiscoveryServiceTest.setup(AtlasDiscoveryServiceTest.java:99)`)
  - Canonical `normalize_test_id()`: `org.apache.atlas.discovery.AtlasDiscoveryServiceTest#setup`
- **Confidence:** CERTAIN

---

## 6. jline__jline3__086340083763.txt
- **Source Repo:** `jline/jline3`
- **Job ID:** `086340083763`
- **Parent Run ID:** `29086104643`
- **Fixture Filename:** `jline__jline3__086340083763.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 1064: `[ERROR] org.jline.builtins.PosixCommandsSsrfTest.catStillReadsLocalFileJar -- Time elapsed: 0.022 s <<< ERROR!` (Surefire summary line 1063: `in org.jline.builtins.PosixCommandsSsrfTest`)
  - Canonical `normalize_test_id()`: `org.jline.builtins.PosixCommandsSsrfTest#catStillReadsLocalFileJar`
- **Confidence:** CERTAIN

---

## 7. igniterealtime__openfire__088344723575.txt
- **Source Repo:** `igniterealtime/openfire`
- **Job ID:** `088344723575`
- **Parent Run ID:** `29740131448`
- **Fixture Filename:** `igniterealtime__openfire__088344723575.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 1256: `[ERROR] org.jivesoftware.openfire.net.SASLAuthenticationTest.shouldGenerateAnonymousAuthTokenForClientWhenUsernameIsNullWithSasl2AndBind2 -- Time elapsed: 0.038 s <<< FAILURE!` (Stack frame Line 1259: `at org.jivesoftware.openfire.net.SASLAuthenticationTest.shouldGenerateAnonymousAuthTokenForClientWhenUsernameIsNullWithSasl2AndBind2(SASLAuthenticationTest.java:405)`)
    - Canonical `normalize_test_id()`: `org.jivesoftware.openfire.net.SASLAuthenticationTest#shouldGenerateAnonymousAuthTokenForClientWhenUsernameIsNullWithSasl2AndBind2`
  - RAW Line 1261: `[ERROR] org.jivesoftware.openfire.net.SASLAuthenticationTest.shouldGenerateUserAuthTokenForClientWhenUsernameIsProvidedWithSasl2AndBind2 -- Time elapsed: 0.016 s <<< FAILURE!` (Stack frame Line 1265: `at org.jivesoftware.openfire.net.SASLAuthenticationTest.shouldGenerateUserAuthTokenForClientWhenUsernameIsProvidedWithSasl2AndBind2(SASLAuthenticationTest.java:509)`)
    - Canonical `normalize_test_id()`: `org.jivesoftware.openfire.net.SASLAuthenticationTest#shouldGenerateUserAuthTokenForClientWhenUsernameIsProvidedWithSasl2AndBind2`
- **Confidence:** CERTAIN

---

## 8. castorini__anserini__087520312502.txt
- **Source Repo:** `castorini/anserini`
- **Job ID:** `087520312502`
- **Parent Run ID:** `29463825927`
- **Fixture Filename:** `castorini__anserini__087520312502.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 928: `[ERROR] io.anserini.reproduce.ReproduceFromPrebuiltIndexesTest.testCacmEndToEnd -- Time elapsed: 6.276 s <<< FAILURE!` (Surefire summary line 927: `in io.anserini.reproduce.ReproduceFromPrebuiltIndexesTest`)
  - Canonical `normalize_test_id()`: `io.anserini.reproduce.ReproduceFromPrebuiltIndexesTest#testCacmEndToEnd`
- **Confidence:** CERTAIN

---

## 9. castorini__anserini__087122010631.txt
- **Source Repo:** `castorini/anserini`
- **Job ID:** `087122010631`
- **Parent Run ID:** `29343768126`
- **Fixture Filename:** `castorini__anserini__087122010631.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 708: `[ERROR] io.anserini.search.SearchCollectionTest.testSpecifyTopicsAsSymbol -- Time elapsed: 0.007 s <<< FAILURE!` (Stack frame Line 714: `at io.anserini.search.SearchCollectionTest.testSpecifyTopicsAsSymbol(SearchCollectionTest.java:169)`)
    - Canonical `normalize_test_id()`: `io.anserini.search.SearchCollectionTest#testSpecifyTopicsAsSymbol`
  - RAW Line 761: `[ERROR] io.anserini.search.SearchHnswDenseVectorsTest.testBasicCosDprSpecifyTopicsAsSymbol -- Time elapsed: 0.384 s <<< FAILURE!` (Stack frame Line 767: `at io.anserini.search.SearchHnswDenseVectorsTest.testBasicCosDprSpecifyTopicsAsSymbol(SearchHnswDenseVectorsTest.java:430)`)
    - Canonical `normalize_test_id()`: `io.anserini.search.SearchHnswDenseVectorsTest#testBasicCosDprSpecifyTopicsAsSymbol`
  - RAW Line 872: `[ERROR] io.anserini.search.SearchFlatDenseVectorsTest.testBasicCosDprSpecifyTopicsAsSymbol -- Time elapsed: 0.464 s <<< FAILURE!` (Stack frame Line 878: `at io.anserini.search.SearchFlatDenseVectorsTest.testBasicCosDprSpecifyTopicsAsSymbol(SearchFlatDenseVectorsTest.java:410)`)
    - Canonical `normalize_test_id()`: `io.anserini.search.SearchFlatDenseVectorsTest#testBasicCosDprSpecifyTopicsAsSymbol`
- **Confidence:** CERTAIN

---

## 10. apache__hertzbeat__086747165466.txt
- **Source Repo:** `apache/hertzbeat`
- **Job ID:** `086747165466`
- **Parent Run ID:** `29228378307`
- **Fixture Filename:** `apache__hertzbeat__086747165466.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Line 505: `[hertzbeat-common-core] [ERROR] org.apache.hertzbeat.common.util.BackoffUtilsTest.shouldHandleInterruptedException -- Time elapsed: 0.211 s <<< ERROR!` (Surefire summary line 504: `in org.apache.hertzbeat.common.util.BackoffUtilsTest`)
  - Canonical `normalize_test_id()`: `org.apache.hertzbeat.common.util.BackoffUtilsTest#shouldHandleInterruptedException`
- **Confidence:** CERTAIN

---

## 11. rptools__maptool__087876393663.txt
- **Source Repo:** `rptools/maptool`
- **Job ID:** `087876393663`
- **Parent Run ID:** `29577872842`
- **Fixture Filename:** `rptools__maptool__087876393663.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 687: `CampaignPropertiesDialogTest > predefinedPropertiesComboBox_noFiles() FAILED` (No FQCN stack frame; D-29 governs)
    - Canonical `normalize_test_id()`: `CampaignPropertiesDialogTest#predefinedPropertiesComboBox_noFiles`
  - RAW Line 690: `CampaignPropertiesDialogTest > predefinedPropertiesComboBox_twoFiles() FAILED` (No FQCN stack frame; D-29 governs)
    - Canonical `normalize_test_id()`: `CampaignPropertiesDialogTest#predefinedPropertiesComboBox_twoFiles`
  - RAW Line 693: `CampaignPropertiesDialogTest > importPredefinedButton() FAILED` (No FQCN stack frame; D-29 governs)
    - Canonical `normalize_test_id()`: `CampaignPropertiesDialogTest#importPredefinedButton`
- **Confidence:** CERTAIN

---

## 12. robo-code__robocode__093833474930.txt
- **Source Repo:** `robo-code/robocode`
- **Job ID:** `093833474930`
- **Parent Run ID:** `31507725065`
- **Fixture Filename:** `robo-code__robocode__093833474930.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 523: `TestCustomEvents > run FAILED` (No FQCN stack frame; D-29 governs)
  - Canonical `normalize_test_id()`: `TestCustomEvents#run`
- **Confidence:** CERTAIN

---

## 13. rptools__maptool__087849465516.txt
- **Source Repo:** `rptools/maptool`
- **Job ID:** `087849465516`
- **Parent Run ID:** `29569426841`
- **Fixture Filename:** `rptools__maptool__087849465516.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 681: `CampaignPropertiesDialogTest > predefinedPropertiesComboBox_noFiles() FAILED` (No FQCN stack frame; D-29 governs)
    - Canonical `normalize_test_id()`: `CampaignPropertiesDialogTest#predefinedPropertiesComboBox_noFiles`
  - RAW Line 684: `CampaignPropertiesDialogTest > predefinedPropertiesComboBox_twoFiles() FAILED` (No FQCN stack frame; D-29 governs)
    - Canonical `normalize_test_id()`: `CampaignPropertiesDialogTest#predefinedPropertiesComboBox_twoFiles`
  - RAW Line 687: `CampaignPropertiesDialogTest > importPredefinedButton() FAILED` (No FQCN stack frame; D-29 governs)
    - Canonical `normalize_test_id()`: `CampaignPropertiesDialogTest#importPredefinedButton`
- **Confidence:** CERTAIN

---

## 14. webauthn4j__webauthn4j__079034957563.txt
- **Source Repo:** `webauthn4j/webauthn4j`
- **Job ID:** `079034957563`
- **Parent Run ID:** `26809361194`
- **Fixture Filename:** `webauthn4j__webauthn4j__079034957563.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 256: `FidoMDS3MetadataBLOBIntegrationTest > async_test() FAILED` (Stack frame Line 261: `at com.webauthn4j.metadata.FidoMDS3MetadataBLOBIntegrationTest.async_test(FidoMDS3MetadataBLOBIntegrationTest.java:104)`)
    - Canonical `normalize_test_id()`: `com.webauthn4j.metadata.FidoMDS3MetadataBLOBIntegrationTest#async_test`
  - RAW Line 312: `FidoMDS3MetadataBLOBIntegrationTest > sync_test() FAILED` (Stack frame Line 355: `at app//com.webauthn4j.metadata.FidoMDS3MetadataBLOBIntegrationTest.sync_test(FidoMDS3MetadataBLOBIntegrationTest.java:75)`)
    - Canonical `normalize_test_id()`: `com.webauthn4j.metadata.FidoMDS3MetadataBLOBIntegrationTest#sync_test`
- **Confidence:** CERTAIN

---

## 15. graphql-java__graphql-java__091882138158.txt
- **Source Repo:** `graphql-java/graphql-java`
- **Job ID:** `091882138158`
- **Parent Run ID:** `30874176641`
- **Fixture Filename:** `graphql-java__graphql-java__091882138158.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 12148: `SUSchemaRoundTripTest > GraphQLSchema and SUSchema remain identical through bidirectional SDL round trips: #scenario > GraphQLSchema and SUSchema remain identical through bidirectional SDL round trips: directives on every schema kind FAILED` (Stack frame Line 12154: `at graphql.schema.universe.SUSchemaRoundTripTest.GraphQLSchema and SUSchema remain identical through bidirectional SDL round trips: #scenario(SUSchemaRoundTripTest.groovy:17)`)
  - Canonical `normalize_test_id()`: `graphql.schema.universe.SUSchemaRoundTripTest#GraphQLSchema and SUSchema remain identical through bidirectional SDL round trips: #scenario`
- **Confidence:** CERTAIN

---

## 16. graphql-java__graphql-java__092512975734.txt
- **Source Repo:** `graphql-java/graphql-java`
- **Job ID:** `092512975734`
- **Parent Run ID:** `31069057782`
- **Fixture Filename:** `graphql-java__graphql-java__092512975734.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 2368: `Issue3434 > allow printing of union types FAILED` (Stack frame Line 2382: `at graphql.Issue3434.allow printing of union types(Issue3434.groovy:20)`)
  - Canonical `normalize_test_id()`: `graphql.Issue3434#allow printing of union types`
- **Confidence:** CERTAIN

---

## 17. robo-code__robocode__090325561628.txt
- **Source Repo:** `robo-code/robocode`
- **Job ID:** `090325561628`
- **Parent Run ID:** `30374207514`
- **Fixture Filename:** `robo-code__robocode__090325561628.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 518: `TestFairPlay > run FAILED` (No FQCN stack frame; D-29 governs)
  - Canonical `normalize_test_id()`: `TestFairPlay#run`
- **Confidence:** CERTAIN

---

## 18. webauthn4j__webauthn4j__080544806420.txt
- **Source Repo:** `webauthn4j/webauthn4j`
- **Job ID:** `080544806420`
- **Parent Run ID:** `27272376216`
- **Fixture Filename:** `webauthn4j__webauthn4j__080544806420.txt`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW Line 2747: `MetadataBLOBPayloadEntryTest > test() FAILED` (Stack frame Line 2750: `at com.webauthn4j.metadata.data.MetadataBLOBPayloadEntryTest.test(MetadataBLOBPayloadEntryTest.java:93)`)
    - Canonical `normalize_test_id()`: `com.webauthn4j.metadata.data.MetadataBLOBPayloadEntryTest#test`
  - RAW Line 2776: `AuthenticatorGetInfoTest > options_old_format_deserialization_test() FAILED` (Stack frame Line 2780: `at app//com.webauthn4j.metadata.data.statement.AuthenticatorGetInfoTest.options_old_format_deserialization_test(AuthenticatorGetInfoTest.java:116)`)
    - Canonical `normalize_test_id()`: `com.webauthn4j.metadata.data.statement.AuthenticatorGetInfoTest#options_old_format_deserialization_test`
  - RAW Line 2782: `AuthenticatorGetInfoTest > options_oldFormat_roundTrip_test() FAILED` (Stack frame Line 2788: `at com.webauthn4j.metadata.data.statement.AuthenticatorGetInfoTest.options_oldFormat_roundTrip_test(AuthenticatorGetInfoTest.java:167)`)
    - Canonical `normalize_test_id()`: `com.webauthn4j.metadata.data.statement.AuthenticatorGetInfoTest#options_oldFormat_roundTrip_test`
- **Confidence:** CERTAIN

---

## 19. atmosphere__atmosphere__078279224469.txt
- **Source Repo:** `atmosphere/atmosphere`
- **Job ID:** `078279224469`
- **Parent Run ID:** `26571138839`
- **Fixture Filename:** `atmosphere__atmosphere__078279224469.txt`
- **Build Tool:** Playwright / Node
- **Expected Outcomes:** NO_TEST_OUTCOMES (Playwright TypeScript matrix failure in `e2e/sample-matrix-smoke.spec.ts`; no Java test runner executed)
- **Confidence:** CERTAIN

---

## 20. apache__hertzbeat__089678606855.txt
- **Source Repo:** `apache/hertzbeat`
- **Job ID:** `089678606855`
- **Parent Run ID:** `30157852491`
- **Fixture Filename:** `apache__hertzbeat__089678606855.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:** NO_TEST_OUTCOMES (Clean Maven test execution with 0 failures / 0 errors reported in all modules; job failure occurred in post-packaging / Docker push step)
- **Confidence:** CERTAIN

---

## 21. atmosphere__atmosphere__089421932457.txt
- **Source Repo:** `atmosphere/atmosphere`
- **Job ID:** `089421932457`
- **Parent Run ID:** `30074414287`
- **Fixture Filename:** `atmosphere__atmosphere__089421932457.txt`
- **Build Tool:** Maven (`./mvnw clean install -DskipTests`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Maven build invoked with `-DskipTests -Dgpg.skip=true`; aborted during compile/packaging before test execution)
- **Confidence:** CERTAIN

---

## 22. jline__jline3__094582811397.txt
- **Source Repo:** `jline/jline3`
- **Job ID:** `094582811397`
- **Parent Run ID:** `31740616611`
- **Fixture Filename:** `jline__jline3__094582811397.txt`
- **Build Tool:** Maven
- **Expected Outcomes:** NO_TEST_OUTCOMES (Build aborted during early verification / setup before Surefire test execution)
- **Confidence:** CERTAIN

---

## 23. oracle__opengrok__083435392401.txt
- **Source Repo:** `oracle/opengrok`
- **Job ID:** `083435392401`
- **Parent Run ID:** `28171151402`
- **Fixture Filename:** `oracle__opengrok__083435392401.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:** NO_TEST_OUTCOMES (Clean test run reporting 286 tests run with 0 failures and 0 errors; job failure occurred due to unhandled thread leak in test cleanup)
- **Confidence:** CERTAIN

---

## 24. nitrite__nitrite-java__081478189534.txt
- **Source Repo:** `nitrite/nitrite-java`
- **Job ID:** `081478189534`
- **Parent Run ID:** `27562595403`
- **Fixture Filename:** `nitrite__nitrite-java__081478189534.txt`
- **Build Tool:** GitHub CodeQL Autobuild
- **Expected Outcomes:** NO_TEST_OUTCOMES (CodeQL autobuild failed during project structure analysis; no test harness executed)
- **Confidence:** CERTAIN

---

## 25. igniterealtime__openfire__079333905347.txt
- **Source Repo:** `igniterealtime/openfire`
- **Job ID:** `079333905347`
- **Parent Run ID:** `26895691485`
- **Fixture Filename:** `igniterealtime__openfire__079333905347.txt`
- **Build Tool:** GitHub Actions / Bash
- **Expected Outcomes:** NO_TEST_OUTCOMES (Workflow cancelled or skipped at actions/cache step; no test runner executed)
- **Confidence:** CERTAIN

---

# PARTITION B: Pytest Supplement (apache/beam Held-Out Partition)

## 26. apache__beam__083002648254.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `083002648254`
- **Parent Run ID:** `28039705407`
- **Fixture Filename:** `apache__beam__083002648254.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 2580: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_local_model_injection_and_propagation`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_local_model_injection_and_propagation`
  - RAW Line 2584: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_port_update_propagation`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_port_update_propagation`
  - RAW Line 2586: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_fails_does_not_mask_original_error`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_fails_does_not_mask_original_error`
  - RAW Line 2588: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_on_failure`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_on_failure`
  - RAW Line 2597: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_validation_fails_with_remote_model_and_local_configured`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_validation_fails_with_remote_model_and_local_configured`
  - RAW Line 2714: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLoadModel::test_load_model_calls_factory_with_model`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLoadModel::test_load_model_calls_factory_with_model`
- **Confidence:** CERTAIN

---

## 27. apache__beam__083002648219.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `083002648219`
- **Parent Run ID:** `28039705407`
- **Fixture Filename:** `apache__beam__083002648219.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 2602: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_local_model_injection_and_propagation`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_local_model_injection_and_propagation`
  - RAW Line 2606: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_port_update_propagation`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_port_update_propagation`
  - RAW Line 2608: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_fails_does_not_mask_original_error`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_fails_does_not_mask_original_error`
  - RAW Line 2610: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_on_failure`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_recovery_on_failure`
  - RAW Line 2612: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_validation_fails_with_remote_model_and_local_configured`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLocalModelIntegration::test_validation_fails_with_remote_model_and_local_configured`
  - RAW Line 2736: `FAILED apache_beam/ml/inference/agent_development_kit_test.py::TestLoadModel::test_load_model_calls_factory_with_model`
    - Canonical `normalize_test_id()`: `apache_beam/ml/inference/agent_development_kit_test.py::TestLoadModel::test_load_model_calls_factory_with_model`
- **Confidence:** CERTAIN

---

## 28. apache__beam__079355463403.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `079355463403`
- **Parent Run ID:** `26901682356`
- **Fixture Filename:** `apache__beam__079355463403.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 4206: `FAILED apache_beam/ml/rag/ingestion/qdrant_it_test.py::TestQdrantIngestion::test_write_dense_embeddings_only`
  - Canonical `normalize_test_id()`: `apache_beam/ml/rag/ingestion/qdrant_it_test.py::TestQdrantIngestion::test_write_dense_embeddings_only`
- **Confidence:** CERTAIN

---

## 29. apache__beam__092813893757.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `092813893757`
- **Parent Run ID:** `31161891522`
- **Fixture Filename:** `apache__beam__092813893757.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 4221: `FAILED apache_beam/transforms/util_test.py::BatchElementsTest::test_constant_batch_no_metrics`
  - Canonical `normalize_test_id()`: `apache_beam/transforms/util_test.py::BatchElementsTest::test_constant_batch_no_metrics`
- **Confidence:** CERTAIN

---

## 30. apache__beam__084686152561.txt
- **Source Repo:** `apache/beam`
- **Job ID:** `084686152561`
- **Parent Run ID:** `28563566578`
- **Fixture Filename:** `apache__beam__084686152561.txt`
- **Build Tool:** Pytest
- **Expected Outcomes:**
  - RAW Line 3386: `FAILED apache_beam/transforms/async_dofn_test.py::AsyncTest_0::test_reset_state_concurrent_teardown`
    - Canonical `normalize_test_id()`: `apache_beam/transforms/async_dofn_test.py::AsyncTest_0::test_reset_state_concurrent_teardown`
  - RAW Line 4308: `FAILED apache_beam/transforms/async_dofn_test.py::AsyncTest_1::test_reset_state_concurrent_teardown`
    - Canonical `normalize_test_id()`: `apache_beam/transforms/async_dofn_test.py::AsyncTest_1::test_reset_state_concurrent_teardown`
- **Confidence:** CERTAIN
