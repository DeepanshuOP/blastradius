# Hand-Labelled Held-Out Fixture Corpus (T1.1c Ground Truth)

This document contains hand-labelled ground truth test outcome expectations for the 20 held-out raw job logs in `tests/fixtures/holdout/`.
All labels were identified **by eye directly from raw log text** without consulting or running any BlastRadius extractor or classifier.
Per ROADMAP §25.3, §26.1 and AGENTS.md, this held-out set is set aside untouched and is **NEVER** scored during parser development.

---

## 1. castorini__anserini__078093909304.txt
- **Source Repo:** `castorini/anserini`
- **Job ID:** `078093909304`
- **Parent Run ID:** `26516187704`
- **Fixture Filename:** `castorini__anserini__078093909304.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW Summary: `[ERROR]   TopicReaderTest.testMSMARCO_V1:1285 » IO Error downloading topics from https://raw.githubusercontent.com/castorini/anserini-tools/master/topics-and-qrels/topics.msmarco-passage.dev-subset.cosdpr-distil.jsonl.gz`
  - Canonical `normalize_test_id()`: `io.anserini.search.topicreader.TopicReaderTest#testMSMARCO_V1`
- **Confidence:** CERTAIN

---

## 2. robo-code__robocode__079375717291.txt
- **Source Repo:** `robo-code/robocode`
- **Job ID:** `079375717291`
- **Parent Run ID:** `26907339540`
- **Build Tool:** Gradle
- **Expected Outcomes:**
  - RAW: `TestFairPlay > run FAILED`
  - Canonical `normalize_test_id()`: `net.sf.robocode.test.robots.TestFairPlay#run`
- **Confidence:** CERTAIN

---

## 3. graphql-java__graphql-java__078459457993.txt
- **Source Repo:** `graphql-java/graphql-java`
- **Job ID:** `078459457993`
- **Parent Run ID:** `26624936408`
- **Fixture Filename:** `graphql-java__graphql-java__078459457993.txt`
- **Build Tool:** GitHub Actions / bash
- **Expected Outcomes:** NO_TEST_OUTCOMES (Aggregator job check `allBuildAndTestSuccessful` failed due to upstream `buildAndTest` job failure; no test runner executed)
- **Confidence:** CERTAIN

---

## 4. igniterealtime__openfire__079332762566.txt
- **Source Repo:** `igniterealtime/openfire`
- **Job ID:** `079332762566`
- **Parent Run ID:** `26895381892`
- **Fixture Filename:** `igniterealtime__openfire__079332762566.txt`
- **Build Tool:** Maven
- **Expected Outcomes:** NO_TEST_OUTCOMES (JSP precompilation maven plugin error `jetty-ee8-jspc-maven-plugin:12.0.35:jspc` on project `xmppserver` during build; aborted before test execution)
- **Confidence:** CERTAIN

---

## 5. higress-group__himarket__078050195307.txt
- **Source Repo:** `higress-group/himarket`
- **Job ID:** `078050195307`
- **Parent Run ID:** `26503611359`
- **Fixture Filename:** `higress-group__himarket__078050195307.txt`
- **Build Tool:** GitHub Actions / `actions/github-script`
- **Expected Outcomes:** NO_TEST_OUTCOMES (PR Validation Summary script failed on `PR Content Check`; no unit or integration tests executed)
- **Confidence:** CERTAIN

---

## 6. nitrite__nitrite-java__084107680035.txt
- **Source Repo:** `nitrite/nitrite-java`
- **Job ID:** `084107680035`
- **Parent Run ID:** `28388037001`
- **Fixture Filename:** `nitrite__nitrite-java__084107680035.txt`
- **Build Tool:** Maven / CodeQL autobuild
- **Expected Outcomes:** NO_TEST_OUTCOMES (CodeQL autobuild invoked maven with `-DskipTests -Dmaven.test.skip.exec`; compilation failed in Kotlin annotation processor `kotlin-maven-plugin:2.4.0:kapt` on `potassium-nitrite`; no test suite executed)
- **Confidence:** CERTAIN

---

## 7. apache__hbase__083114718053.txt
- **Source Repo:** `apache/hbase`
- **Job ID:** `083114718053`
- **Parent Run ID:** `28074123072`
- **Fixture Filename:** `apache__hbase__083114718053.txt`
- **Build Tool:** Apache Yetus (Dockerized Maven container)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Yetus summary table reports `| -1 | unit | @@BASE@@/patch-unit-hbase-server.txt |` and `hbase-server in the patch failed.`. Artifact uploaded `yetus-jdk17-hadoop3-unit-check-large-wave-1` (ID 7841001210). Zero individual test method names or failure traces appear in the job log.)
- **Confidence:** CERTAIN

---

## 8. apache__hbase__082913156708.txt
- **Source Repo:** `apache/hbase`
- **Job ID:** `082913156708`
- **Parent Run ID:** `28013827967`
- **Fixture Filename:** `apache__hbase__082913156708.txt`
- **Build Tool:** Apache Yetus (Dockerized Maven container)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Yetus summary table reports `| -1 | mvninstall | @@BASE@@/patch-mvninstall-root.txt |` and `| -1 | unit | @@BASE@@/patch-unit-hbase-it.txt |`. Artifact uploaded `yetus-jdk17-hadoop3-unit-check-large-wave-2` (ID 7819127618). Zero individual test method names appear in the job log.)
- **Confidence:** CERTAIN

---

## 9. Stirling-Tools__Stirling-PDF__081674712291.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `081674712291`
- **Parent Run ID:** `27618062997`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__081674712291.txt`
- **Build Tool:** GitHub Actions / Tauri build reporting step `tauri-build / report`
- **Expected Outcomes:** NO_TEST_OUTCOMES (Tauri build report step failed on check `if [ "failure" = "success" ]` because preceding matrix builds failed; no test execution occurred in this job)
- **Confidence:** CERTAIN

---

## 10. Stirling-Tools__Stirling-PDF__081853656807.txt
- **Source Repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `081853656807`
- **Parent Run ID:** `27675862403`
- **Fixture Filename:** `Stirling-Tools__Stirling-PDF__081853656807.txt`
- **Build Tool:** GitHub Actions / Tauri build reporting step `tauri-build / report`
- **Expected Outcomes:** NO_TEST_OUTCOMES (Tauri build report step failed on check `if [ "cancelled" = "success" ]` because preceding matrix builds were cancelled; no test execution occurred in this job)
- **Confidence:** CERTAIN

---

## 11. crimera__piko__081451893643.txt
- **Source Repo:** `crimera/piko`
- **Job ID:** `081451893643`
- **Parent Run ID:** `27555116833`
- **Fixture Filename:** `crimera__piko__081451893643.txt`
- **Build Tool:** GitHub Actions / GitHub CLI (`gh pr create` / `gh pr edit`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (GitHub PR maintenance step `Open pull request` failed running `gh pr edit`; no test execution occurred in this job)
- **Confidence:** CERTAIN

---

## 12. crimera__piko__081577143906.txt
- **Source Repo:** `crimera/piko`
- **Job ID:** `081577143906`
- **Parent Run ID:** `27592873626`
- **Fixture Filename:** `crimera__piko__081577143906.txt`
- **Build Tool:** GitHub Actions / GitHub CLI (`gh pr create` / `gh pr edit`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (GitHub PR maintenance step `Open pull request` failed running `gh pr edit`; no test execution occurred in this job)
- **Confidence:** CERTAIN

---

## 13. apache__flink__078003756269.txt
- **Source Repo:** `apache/flink`
- **Job ID:** `078003756269`
- **Parent Run ID:** `26488073218`
- **Fixture Filename:** `apache__flink__078003756269.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:**
  - RAW: `May 27 04:04:44 04:04:44.495 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 2.485 s <<< FAILURE!`
  - RAW Summary: `May 27 04:04:45 04:04:45.887 [ERROR]   RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate:73 [Committed rest_v1_dispatcher.yml file is out of date. Please regenerate docs under flink-docs module based on README.md.]`
  - Canonical `normalize_test_id()`: `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate`
- **Confidence:** CERTAIN

---

## 14. apache__flink__080017889012.txt
- **Source Repo:** `apache/flink`
- **Job ID:** `080017889012`
- **Parent Run ID:** `27113488102`
- **Fixture Filename:** `apache__flink__080017889012.txt`
- **Build Tool:** Maven/Surefire
- **Expected Outcomes:** NO_TEST_OUTCOMES (Test harness timed out / hung; watchdog killed process with exit code 143; zero individual test assertion failures or errors reported)
- **Confidence:** CERTAIN

---

## 15. openremote__openremote__086150295955.txt
- **Source Repo:** `openremote/openremote`
- **Job ID:** `086150295955`
- **Parent Run ID:** `29026970986`
- **Fixture Filename:** `openremote__openremote__086150295955.txt`
- **Build Tool:** Gradle / Playwright (`:ui:app:manager:npmTest`)
- **Expected Outcomes:**
  - RAW: `[cleanup manager] › test/test.cleanup.ts:32:8 › Delete the "smartcity" realm ───────────────────`
  - Canonical `normalize_test_id()`: `test/test.cleanup.ts:32:8::Delete the "smartcity" realm`
- **Confidence:** AMBIGUOUS (JavaScript Playwright browser test invoked through Gradle `:ui:app:manager:npmTest` task)

---

## 16. openremote__openremote__085859996738.txt
- **Source Repo:** `openremote/openremote`
- **Job ID:** `085859996738`
- **Parent Run ID:** `28939531248`
- **Fixture Filename:** `openremote__openremote__085859996738.txt`
- **Build Tool:** GitHub Actions / Workflow status aggregation step `Test / UI App Tests Status`
- **Expected Outcomes:** NO_TEST_OUTCOMES (Aggregator job executed `exit 1` due to upstream test failure; no test runner executed in this job)
- **Confidence:** CERTAIN

---

## 17. thealgorithms__java__078736649370.txt
- **Source Repo:** `thealgorithms/java`
- **Job ID:** `078736649370`
- **Parent Run ID:** `26716776074`
- **Fixture Filename:** `thealgorithms__java__078736649370.txt`
- **Build Tool:** Maven (`maven-compiler-plugin:3.15.0:compile`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Compilation failure in `com.thealgorithms.simulation.NRobotsCollision`: cannot find symbol `ArrayList`; build failed before test phase executed)
- **Confidence:** CERTAIN

---

## 18. thealgorithms__java__083289143209.txt
- **Source Repo:** `thealgorithms/java`
- **Job ID:** `083289143209`
- **Parent Run ID:** `28125793500`
- **Fixture Filename:** `thealgorithms__java__083289143209.txt`
- **Build Tool:** Infer static analyzer (`run_infer`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Facebook Infer static analysis tool reported 3 `NULLPTR_DEREFERENCE` issues and exited with code 2; no test suite executed)
- **Confidence:** CERTAIN

---

## 19. baomidou__mybatis-plus__084724355515.txt
- **Source Repo:** `baomidou/mybatis-plus`
- **Job ID:** `084724355515`
- **Parent Run ID:** `28575925752`
- **Fixture Filename:** `baomidou__mybatis-plus__084724355515.txt`
- **Build Tool:** Gradle (`gradle/actions/dependency-submission`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (GitHub Action `gradle/actions/dependency-submission` resolved dependencies for submission snapshot; post-step submission failed due to `HttpError: Resource not accessible by integration`; no tests were executed)
- **Confidence:** CERTAIN

---

## 20. baomidou__mybatis-plus__083974499807.txt
- **Source Repo:** `baomidou/mybatis-plus`
- **Job ID:** `083974499807`
- **Parent Run ID:** `28347771813`
- **Fixture Filename:** `baomidou__mybatis-plus__083974499807.txt`
- **Build Tool:** Gradle (`./gradlew build`)
- **Expected Outcomes:** NO_TEST_OUTCOMES (Gradle build compilation task `:mybatis-plus-core:compileJava` failed resolving dependency `org.springframework:spring-aop:7.0.8` on JVM 8; aborted before testing phase)
- **Confidence:** CERTAIN
