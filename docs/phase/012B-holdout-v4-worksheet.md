# Holdout v4 Hand-Labelling Worksheet

**Target Corpus**: `tests/fixtures/holdout_v4/` (32 logs)  
**Protocol**: D-27 / D-29 / D-38 ground-truth labelling discipline.  
**Instructions for Operator**:
- Read raw log excerpts byte-for-byte. Do NOT run any BlastRadius parser.
- Fill the three empty fields per log: `Expected Class`, `Expected Identifier Count`, and `Expected Identifiers`.
- Expected Classes: `TEST_FAILURE`, `TEST_RAN_CLEAN`, `NO_TEST_OUTPUT`.
- Identifiers must reflect canonical representation derived strictly from information visible in the raw log.

---
## 1. `Stirling-Tools__Stirling-PDF__081016081705.txt`
- **Log Filename**: `Stirling-Tools__Stirling-PDF__081016081705.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-12T11:17:50.6209069Z 
2026-06-12T11:17:50.6210748Z > Task :***-pdf:test
2026-06-12T11:17:50.6211094Z 
2026-06-12T11:17:50.6211639Z UIDataControllerTest > getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical() FAILED
2026-06-12T11:17:50.6212242Z     java.lang.AssertionError at UIDataControllerTest.java:61
2026-06-12T11:18:00.1269594Z 
2026-06-12T11:18:00.1327263Z 1518 tests completed, 1 failed
2026-06-12T11:18:00.2211350Z 
2026-06-12T11:18:00.2219900Z > Task :***-pdf:test FAILED
2026-06-12T11:18:00.2996847Z 
2026-06-12T11:18:00.2998359Z gradle/actions: Writing build results to /home/runner/work/_temp/.gradle-actions/build-results/__run_4-1781263027829.json
2026-06-12T11:18:00.2998923Z 35 actionable tasks: 23 executed, 11 from cache, 1 up-to-date
2026-06-12T11:18:00.3010139Z FAILURE: Build failed with an exception.
2026-06-12T11:18:00.3010423Z 
2026-06-12T11:18:00.3010524Z * What went wrong:
2026-06-12T11:18:00.3010783Z Execution failed for task ':***-pdf:test'.
2026-06-12T11:18:00.3011171Z > There were failing tests. See the report at: file:///home/runner/work/Stirling-PDF/Stirling-PDF/app/core/build/reports/tests/test/index.html
2026-06-12T11:18:00.3011474Z 
2026-06-12T11:18:00.3011564Z * Try:
2026-06-12T11:18:00.3011783Z > Run with --scan to get full insights from a Build Scan (powered by Develocity).
2026-06-12T11:18:00.3011985Z 
2026-06-12T11:18:00.3012066Z BUILD FAILED in 52s
2026-06-12T11:18:00.3055684Z Gradle build failed with security disabled, exiting script.
2026-06-12T11:18:00.9673696Z ##[endgroup]
2026-06-12T11:18:00.9691946Z JSON test report written to: /home/runner/work/Stirling-PDF/Stirling-PDF/testing/reports/test-report.json
2026-06-12T11:18:00.9696149Z GitHub Actions job summary written.
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 2. `Stirling-Tools__Stirling-PDF__081185748047.txt`
- **Log Filename**: `Stirling-Tools__Stirling-PDF__081185748047.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-13T11:09:29.5109192Z [[33mbackend:build:ci[0m] > Task :common:test
2026-06-13T11:09:29.5109506Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:29.5109777Z [[33mbackend:build:ci[0m] JobQueueTest > shouldCheckIfJobIsQueued() FAILED
2026-06-13T11:09:29.5110285Z [[33mbackend:build:ci[0m]     java.lang.NullPointerException at JobQueueTest.java:94
2026-06-13T11:09:29.5110697Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:29.5110981Z [[33mbackend:build:ci[0m] JobQueueTest > shouldCancelJob() FAILED
2026-06-13T11:09:29.5111392Z [[33mbackend:build:ci[0m]     java.lang.NullPointerException at JobQueueTest.java:60
2026-06-13T11:09:29.5111694Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:29.5112069Z [[33mbackend:build:ci[0m] JobQueueTest > shouldGetQueueStats() FAILED
2026-06-13T11:09:29.5112419Z [[33mbackend:build:ci[0m]     java.lang.NullPointerException at JobQueueTest.java:71
2026-06-13T11:09:29.5112706Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:29.5112976Z [[33mbackend:build:ci[0m] JobQueueTest > shouldQueueJob() FAILED
2026-06-13T11:09:29.5113321Z [[33mbackend:build:ci[0m]     java.lang.NullPointerException at JobQueueTest.java:49
2026-06-13T11:09:29.6106743Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:29.6108186Z [[33mbackend:build:ci[0m] Skipping sticky-note[1]: pageIndex=99 out of range [0, 2).
    [... elided 166 lines ...]
2026-06-13T11:09:36.0107596Z [[33mbackend:build:ci[0m] Removing event handler attribute: onclick
2026-06-13T11:09:36.0107901Z [[33mbackend:build:ci[0m] Removing dangerous SVG element: script
2026-06-13T11:09:38.3122310Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:38.3123571Z [[33mbackend:build:ci[0m] > Task :common:test FAILED
2026-06-13T11:09:38.3124005Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:38.3124400Z [[33mbackend:build:ci[0m] 810 tests completed, 4 failed, 5 skipped
2026-06-13T11:09:38.4106303Z [[33mbackend:build:ci[0m] gradle/actions: Writing build results to /home/runner/work/_temp/.gradle-actions/build-results/__run_2-1781348918928.json
2026-06-13T11:09:38.4107802Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:38.4108550Z [[33mbackend:build:ci[0m] [Incubating] Problems report is available at: file:///home/runner/work/Stirling-PDF/Stirling-PDF/build/reports/problems/problems-report.html
2026-06-13T11:09:38.4109178Z [[33mbackend:build:ci[0m] 
2026-06-13T11:09:38.4109514Z [[33mbackend:build:ci[0m] FAILURE: Build completed with 3 failures.
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 3. `agno-agi__agno__079305370965.txt`
- **Log Filename**: `agno-agi__agno__079305370965.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-03T13:39:13.1731273Z 
2026-06-03T13:39:13.1731479Z Coverage JSON written to file coverage-agno.json
2026-06-03T13:39:13.1732023Z =========================== short test summary info ============================
2026-06-03T13:39:13.1733817Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'gpt2' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/openai-community/gpt2/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/gpt2/resolve/main/tokenizer.json: status code 429'}
2026-06-03T13:39:13.1736939Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'cl100k_base' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/Xenova/gpt-4/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/cl100k_base/resolve/main/tokenizer.json: status code 429'}
2026-06-03T13:39:13.1738686Z ===== 2 failed, 8494 passed, 41 skipped, 34 warnings in 593.27s (0:09:53) ======
2026-06-03T13:39:19.4825684Z ##[error]Process completed with exit code 1.
2026-06-03T13:39:19.4932811Z Post job cleanup.
2026-06-03T13:39:19.5706075Z [command]/usr/bin/git version
2026-06-03T13:39:19.5744064Z git version 2.54.0
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 4. `agno-agi__agno__092042274925.txt`
- **Log Filename**: `agno-agi__agno__092042274925.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-08-04T15:29:41.6262683Z WARNING  agno:log.py:225 Failed to convert response to output_schema
2026-08-04T15:29:41.6263518Z =========================== short test summary info ============================
2026-08-04T15:29:41.6265273Z FAILED tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields - AttributeError: 'str' object has no attribute 'rating'
2026-08-04T15:29:41.6266827Z =============== 1 failed, 16 passed, 1 rerun in 99.45s (0:01:39) ===============
2026-08-04T15:29:41.8800947Z 
2026-08-04T15:29:41.8802009Z === Test Results ===
2026-08-04T15:29:41.8802991Z Tests failed for deepinfra
2026-08-04T15:29:41.8811888Z ##[error]Process completed with exit code 1.
2026-08-04T15:29:41.8935113Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 5. `apache__atlas__085339439869.txt`
- **Log Filename**: `apache__atlas__085339439869.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-06T09:38:42.3905026Z [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 13.83 s -- in org.apache.atlas.hook.AtlasTopicCreatorTest
2026-07-06T09:38:42.5384890Z [INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 42.69 s -- in org.apache.atlas.notification.RestNotificationTest
2026-07-06T09:38:44.1556323Z [INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 16.18 s -- in org.apache.atlas.kafka.KafkaConsumerTest
2026-07-06T09:38:44.7358454Z [ERROR] Tests run: 3, Failures: 1, Errors: 0, Skipped: 2, Time elapsed: 17.98 s <<< FAILURE! -- in org.apache.atlas.kafka.KafkaNotificationTest
2026-07-06T09:38:44.7360321Z [ERROR] org.apache.atlas.kafka.KafkaNotificationTest.setup -- Time elapsed: 17.90 s <<< FAILURE!
2026-07-06T09:38:44.7361702Z java.lang.NoClassDefFoundError: org/junit/jupiter/api/Assertions
2026-07-06T09:38:44.7362794Z 	at org.apache.kafka.test.TestUtils.lambda$waitForCondition$3(TestUtils.java:397)
2026-07-06T09:38:44.7364192Z 	at org.apache.kafka.test.TestUtils.retryOnExceptionWithTimeout(TestUtils.java:445)
2026-07-06T09:38:44.7365415Z 	at org.apache.kafka.test.TestUtils.waitForCondition(TestUtils.java:394)
2026-07-06T09:38:44.7366465Z 	at org.apache.kafka.test.TestUtils.waitForCondition(TestUtils.java:378)
2026-07-06T09:38:44.7367525Z 	at org.apache.kafka.test.TestUtils.waitForCondition(TestUtils.java:351)
2026-07-06T09:38:44.7368624Z 	at kafka.testkit.KafkaClusterTestKit.waitForReadyBrokers(KafkaClusterTestKit.java:467)
2026-07-06T09:38:44.7370126Z 	at org.apache.atlas.kafka.EmbeddedKafkaServer.startKraftBroker(EmbeddedKafkaServer.java:124)
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 6. `apache__beam__086101982024.txt`
- **Log Filename**: `apache__beam__086101982024.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-09T11:09:03.8534071Z > Task :sdks:java:io:hadoop-format:test
2026-07-09T11:09:03.8534812Z 
2026-07-09T11:09:03.8535306Z HadoopFormatIOCassandraTest > classMethod FAILED
2026-07-09T11:09:03.8536980Z     java.lang.UnsupportedOperationException at HadoopFormatIOCassandraTest.java:189
2026-07-09T11:09:03.8538833Z 
2026-07-09T11:09:03.8539833Z HadoopFormatIOCassandraTest > classMethod FAILED
2026-07-09T11:09:03.8542225Z     java.lang.NullPointerException at HadoopFormatIOCassandraTest.java:217
2026-07-09T11:10:15.1521823Z 
2026-07-09T11:10:15.1523730Z HadoopFormatIOElasticTest > testHifIOWithElastic FAILED
2026-07-09T11:10:15.1525429Z     java.lang.ExceptionInInitializerError at HadoopFormatIOElasticTest.java:109
2026-07-09T11:10:15.1527328Z         Caused by: java.lang.reflect.InaccessibleObjectException at HadoopFormatIOElasticTest.java:109
2026-07-09T11:10:15.6515924Z 
2026-07-09T11:10:15.6517616Z HadoopFormatIOElasticTest > testHifIOWithElasticQuery FAILED
2026-07-09T11:10:15.6519017Z     java.lang.NoClassDefFoundError at HadoopFormatIOElasticTest.java:144
2026-07-09T11:10:15.6521055Z         Caused by: java.lang.ExceptionInInitializerError at HadoopFormatIOElasticTest.java:109
2026-07-09T11:10:42.9514887Z 
2026-07-09T11:10:42.9515800Z 66 tests completed, 4 failed
2026-07-09T11:10:43.0515447Z 
2026-07-09T11:10:43.0517174Z > Task :sdks:java:io:hadoop-format:test FAILED
2026-07-09T11:10:43.1516461Z gradle/actions: Writing build results to /runner/_work/_temp/.gradle-actions/build-results/__self_5-1783595171169.json
2026-07-09T11:10:43.2513558Z 
2026-07-09T11:10:43.2513581Z 
2026-07-09T11:10:43.2514911Z FAILURE: Build failed with an exception.
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 7. `apache__beam__093527298308.txt`
- **Log Filename**: `apache__beam__093527298308.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-08-10T17:31:38.8282815Z     Aug 10, 2026 5:31:38 PM org.apache.beam.sdk.io.iceberg.catalog.IcebergCatalogBaseIT cleanUp
2026-08-10T17:31:38.8286208Z     INFO: Successfully cleaned up namespaces: [bqms_test_catalog_1786382704778_testWriteRead]
2026-08-10T17:31:48.9283182Z 
2026-08-10T17:31:48.9284336Z BigQueryMetastoreCatalogIT > testWriteRead FAILED
2026-08-10T17:31:48.9286232Z     org.apache.iceberg.exceptions.NoSuchTableException: Table does not exist: bqms_test_catalog_1786382704778_testWriteRead.test_table_2
2026-08-10T17:31:48.9288534Z         at app//org.apache.iceberg.BaseMetastoreCatalog.loadTable(BaseMetastoreCatalog.java:55)
2026-08-10T17:31:48.9290475Z         at app//org.apache.beam.sdk.io.iceberg.catalog.IcebergCatalogBaseIT.testWriteRead(IcebergCatalogBaseIT.java:735)
2026-08-10T17:31:48.9292741Z         at java.base@21.0.11/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103)
    [... elided 598 lines ...]
2026-08-10T17:48:56.7463183Z 
2026-08-10T17:48:56.7463448Z Gradle Test Executor 11 finished executing tests.
2026-08-10T17:48:57.8289055Z 
2026-08-10T17:48:57.8290859Z 5 tests completed, 4 failed
2026-08-10T17:48:57.8302353Z 
2026-08-10T17:48:57.8303242Z > Task :sdks:java:io:iceberg:dataflowIntegrationTest FAILED
2026-08-10T17:48:57.8305253Z Finished generating test XML results (0.183 secs) into: /runner/_work/beam/beam/sdks/java/io/iceberg/build/test-results/dataflowIntegrationTest
2026-08-10T17:48:57.8307187Z Generating HTML test report...
2026-08-10T17:48:57.8308787Z Finished generating test html results (0.27 secs) into: /runner/_work/beam/beam/sdks/java/io/iceberg/build/reports/tests/dataflowIntegrationTest
2026-08-10T17:48:57.9284372Z Resolve mutations for :runners:google-cloud-dataflow-java:cleanUpDockerJavaImages (Thread[#128,Execution worker Thread 2,5,main]) started.
2026-08-10T17:48:57.9288865Z :runners:google-cloud-dataflow-java:cleanUpDockerJavaImages (Thread[#128,Execution worker Thread 2,5,main]) started.
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 8. `apache__dolphinscheduler__092883042571.txt`
- **Log Filename**: `apache__dolphinscheduler__092883042571.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-08-07T13:46:49.4941152Z 2026-08-07 13:46:49,493 tc.docker 35 [Thread-27] INFO  [] -  Network swrks4pbculu_e2e  Removing
2026-08-07T13:46:49.5782741Z 2026-08-07 13:46:49,578 tc.docker 35 [Thread-27] INFO  [] -  Network swrks4pbculu_e2e  Removed
2026-08-07T13:46:49.5810576Z 2026-08-07 13:46:49,580 tc.docker 115 [main] INFO  [] - Docker Compose has finished running
2026-08-07T13:46:49.6025516Z [ERROR] Tests run: 2, Failures: 0, Errors: 1, Skipped: 1, Time elapsed: 97.179 s <<< FAILURE! - in org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest
2026-08-07T13:46:49.6026738Z [ERROR] testCreateDolphinDBDataSource  Time elapsed: 1.254 s  <<< ERROR!
2026-08-07T13:46:49.6027372Z org.openqa.selenium.NoSuchElementException: 
2026-08-07T13:46:49.6028119Z no such element: Unable to locate element: {"method":"css selector","selector":".dialog\-create\-data\-source"}
2026-08-07T13:46:49.6028803Z   (Session info: chrome=125.0.6422.76)
2026-08-07T13:46:49.6029685Z For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception
2026-08-07T13:46:49.6030817Z Build info: version: '4.21.0', revision: '79ed462ef4'
2026-08-07T13:46:49.6031608Z System info: os.name: 'Linux', os.arch: 'amd64', os.version: '6.17.0-1020-azure', java.version: '11.0.32'
2026-08-07T13:46:49.6032274Z Driver info: org.openqa.selenium.remote.RemoteWebDriver
2026-08-07T13:46:49.6033070Z Command: [b561a413570f6b2edd9825fc2d38eef6, findElement {value=dialog-create-data-source, using=class name}]
2026-08-07T13:46:49.6038131Z Capabilities {acceptInsecureCerts: false, browserName: chrome, browserVersion: 125.0.6422.76, chrome: {chromedriverVersion: 125.0.6422.76 (67dcf7562b8f..., userDataDir: /tmp/.org.chromium.Chromium...}, fedcm:accounts: true, goog:chromeOptions: {debuggerAddress: localhost:33873}, networkConnectionEnabled: false, pageLoadStrategy: normal, platformName: linux, proxy: Proxy(), se:bidiEnabled: false, se:cdp: ws://172.19.0.2:4444/sessio..., se:cdpVersion: 125.0.6422.76, se:vnc: ws://172.19.0.2:4444/sessio..., se:vncEnabled: true, se:vncLocalAddress: ws://172.19.0.2:7900, setWindowRect: true, strictFileInteractability: false, timeouts: {implicit: 0, pageLoad: 300000, script: 30000}, unhandledPromptBehavior: dismiss and notify, webauthn:extension:credBlob: true, webauthn:extension:largeBlob: true, webauthn:extension:minPinLength: true, webauthn:extension:prf: true, webauthn:virtualAuthenticators: true}
2026-08-07T13:46:49.6042287Z Session ID: b561a413570f6b2edd9825fc2d38eef6
2026-08-07T13:46:49.6043552Z 	at org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest.testCreateDolphinDBDataSource(DolphinDBDataSourceE2ETest.java:79)
2026-08-07T13:46:49.6044566Z 
2026-08-07T13:46:49.6080625Z 2026-08-07 13:46:49,607 pool-1-thread-1 DEBUG Stopping LoggerContext[name=5c29bfd, org.apache.logging.log4j.core.LoggerContext@4fc5e095]
2026-08-07T13:46:49.6083180Z 2026-08-07 13:46:49,607 pool-1-thread-1 DEBUG Stopping LoggerContext[name=5c29bfd, org.apache.logging.log4j.core.LoggerContext@4fc5e095]...
2026-08-07T13:46:49.6097677Z 2026-08-07 13:46:49,609 pool-1-thread-1 DEBUG Shutting down OutputStreamManager SYSTEM_OUT.false.false
2026-08-07T13:46:49.6115981Z 2026-08-07 13:46:49,609 pool-1-thread-1 DEBUG OutputStream closed
2026-08-07T13:46:49.6124671Z 2026-08-07 13:46:49,609 pool-1-thread-1 DEBUG Shut down OutputStreamManager SYSTEM_OUT.false.false, all resources released: true
2026-08-07T13:46:49.6125770Z 2026-08-07 13:46:49,609 pool-1-thread-1 DEBUG Appender Console stopped with status true
2026-08-07T13:46:49.6127207Z 2026-08-07 13:46:49,609 pool-1-thread-1 DEBUG Stopped XmlConfiguration[location=/home/runner/work/dolphinscheduler/dolphinscheduler/dolphinscheduler-e2e/dolphinscheduler-e2e-core/target/classes/log4j2.xml] OK
2026-08-07T13:46:49.6128922Z 2026-08-07 13:46:49,609 pool-1-thread-1 DEBUG Stopped LoggerContext[name=5c29bfd, org.apache.logging.log4j.core.LoggerContext@4fc5e095] with status true
2026-08-07T13:46:49.9366442Z [INFO] 
2026-08-07T13:46:49.9366789Z [INFO] Results:
2026-08-07T13:46:49.9367191Z [INFO] 
2026-08-07T13:46:49.9367431Z [ERROR] Errors: 
2026-08-07T13:46:49.9368742Z [ERROR]   DolphinDBDataSourceE2ETest.testCreateDolphinDBDataSource:79 » NoSuchElement no...
2026-08-07T13:46:49.9369341Z [INFO] 
2026-08-07T13:46:49.9369698Z [ERROR] Tests run: 2, Failures: 0, Errors: 1, Skipped: 1
2026-08-07T13:46:49.9370230Z [INFO] 
2026-08-07T13:46:49.9402619Z [INFO] ------------------------------------------------------------------------
2026-08-07T13:46:49.9403081Z [INFO] Reactor Summary for dolphinscheduler-e2e 1.0-SNAPSHOT:
2026-08-07T13:46:49.9403501Z [INFO] 
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 9. `apache__flink__078003756269.txt`
- **Log Filename**: `apache__flink__078003756269.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-05-27T04:04:42.8687805Z May 27 04:04:42 04:04:42.867 [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.889 s -- in org.apache.flink.docs.rest.SqlGatewayOpenRestAPIDocsCompletenessITCase
2026-05-27T04:04:43.5850526Z Picked up JAVA_TOOL_OPTIONS: -XX:+HeapDumpOnOutOfMemoryError
2026-05-27T04:04:44.4960610Z May 27 04:04:44 04:04:44.495 [ERROR] Tests run: 1, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 2.512 s <<< FAILURE! -- in org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase
2026-05-27T04:04:44.4971975Z May 27 04:04:44 04:04:44.495 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 2.485 s <<< FAILURE!
2026-05-27T04:04:44.4973299Z May 27 04:04:44 java.lang.AssertionError: 
2026-05-27T04:04:44.4974149Z May 27 04:04:44 [Committed `rest_v1_dispatcher.yml` file is out of date. Please regenerate docs under `flink-docs` module based on `README.md`.] 
2026-05-27T04:04:44.4975050Z May 27 04:04:44 Path:
2026-05-27T04:04:44.4975416Z May 27 04:04:44   /root/flink/docs/static/generated/rest_v1_dispatcher.yml
2026-05-27T04:04:44.4975834Z May 27 04:04:44 and path:
2026-05-27T04:04:44.4976192Z May 27 04:04:44   /tmp/junit-11341368333834843314/rest_v1_dispatcher.yml
2026-05-27T04:04:44.4976626Z May 27 04:04:44 do not have same content:
    [... elided 104 lines ...]
2026-05-27T04:04:45.8901692Z May 27 04:04:45    "          $ref: "#/components/schemas/JobRescaleDetails""]
2026-05-27T04:04:45.8902088Z May 27 04:04:45 
2026-05-27T04:04:45.8902308Z May 27 04:04:45 04:04:45.887 [INFO] 
2026-05-27T04:04:45.8902718Z May 27 04:04:45 04:04:45.887 [ERROR] Tests run: 3, Failures: 1, Errors: 0, Skipped: 0
2026-05-27T04:04:45.8903167Z May 27 04:04:45 04:04:45.887 [INFO] 
2026-05-27T04:04:45.8903638Z May 27 04:04:45 04:04:45.888 [INFO] ------------------------------------------------------------------------
2026-05-27T04:04:45.8904486Z May 27 04:04:45 04:04:45.888 [INFO] Reactor Summary for Flink : Architecture Tests 2.3-SNAPSHOT:
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 10. `apache__flink__079445374425.txt`
- **Log Filename**: `apache__flink__079445374425.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-04T04:09:20.8744185Z Jun 04 04:09:20 04:09:20.873 [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 1.396 s -- in org.apache.flink.docs.rest.SqlGatewayOpenRestAPIDocsCompletenessITCase
2026-06-04T04:09:21.7031919Z Jun 04 04:09:21 04:09:21.702 [INFO] Running org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase
2026-06-04T04:09:23.4240829Z Jun 04 04:09:23 04:09:23.422 [ERROR] Tests run: 1, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 1.712 s <<< FAILURE! -- in org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase
2026-06-04T04:09:23.4243464Z Jun 04 04:09:23 04:09:23.422 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 1.690 s <<< FAILURE!
2026-06-04T04:09:23.4245713Z Jun 04 04:09:23 java.lang.AssertionError: 
2026-06-04T04:09:23.4246839Z Jun 04 04:09:23 [Committed `rest_v1_dispatcher.yml` file is out of date. Please regenerate docs under `flink-docs` module based on `README.md`.] 
2026-06-04T04:09:23.4247923Z Jun 04 04:09:23 Path:
2026-06-04T04:09:23.4248482Z Jun 04 04:09:23   /root/flink/docs/static/generated/rest_v1_dispatcher.yml
2026-06-04T04:09:23.4249150Z Jun 04 04:09:23 and path:
    [... elided 103 lines ...]
2026-06-04T04:09:23.7673377Z Jun 04 04:09:23    "        last:",
2026-06-04T04:09:23.7674200Z Jun 04 04:09:23    "          $ref: "#/components/schemas/JobRescaleDetails""]
2026-06-04T04:09:23.7674832Z Jun 04 04:09:23 
2026-06-04T04:09:23.7675201Z Jun 04 04:09:23 04:09:23.761 [INFO] 
2026-06-04T04:09:23.7675859Z Jun 04 04:09:23 04:09:23.761 [ERROR] Tests run: 3, Failures: 1, Errors: 0, Skipped: 0
2026-06-04T04:09:23.7676556Z Jun 04 04:09:23 04:09:23.761 [INFO] 
2026-06-04T04:09:23.7677289Z Jun 04 04:09:23 04:09:23.763 [INFO] ------------------------------------------------------------------------
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 11. `apache__hugegraph__084221602296.txt`
- **Log Filename**: `apache__hugegraph__084221602296.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-30T06:02:24.4943551Z 2026-06-30 06:02:24 [main] [WARN] o.a.h.c.HugeConfig - The config option 'test.tinkerpop.filter' is redundant, please ensure it has been registered
2026-06-30T06:02:24.6899429Z 2026-06-30 06:02:24 [main] [INFO] o.a.h.b.c.CacheManager - Init RamCache for 'schema-id-DEFAULT-hugegraph' with capacity 10000
2026-06-30T06:02:24.6907239Z 2026-06-30 06:02:24 [main] [INFO] o.a.h.b.c.CacheManager - Init RamCache for 'schema-name-DEFAULT-hugegraph' with capacity 10000
2026-06-30T06:02:25.0551965Z 2026-06-30 06:02:25 [main] [INFO] o.a.h.p.c.KvClient - wait for client starting....
2026-06-30T06:02:25.8930403Z [ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 2.946 s <<< FAILURE! - in org.apache.hugegraph.core.CoreTestSuite
2026-06-30T06:02:25.8950390Z [ERROR] org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2.946 s  <<< ERROR!
2026-06-30T06:02:25.8951618Z org.apache.hugegraph.HugeException: Failed to listen 'HUGEGRAPH/hg/EVENT/GRAPH/SCHEMA/CLEAR' to pd
2026-06-30T06:02:25.8952786Z 	at org.apache.hugegraph.core.CoreTestSuite.init(CoreTestSuite.java:98)
2026-06-30T06:02:25.8954585Z Caused by: org.apache.hugegraph.pd.common.PDException: org.apache.hugegraph.pd.common.PDException: PD unreachable, pd.peers=127.0.0.1:8686
2026-06-30T06:02:25.8956044Z 	at org.apache.hugegraph.core.CoreTestSuite.init(CoreTestSuite.java:98)
2026-06-30T06:02:25.8957379Z Caused by: org.apache.hugegraph.pd.common.PDException: PD unreachable, pd.peers=127.0.0.1:8686
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 12. `apache__hugegraph__086386091934.txt`
- **Log Filename**: `apache__hugegraph__086386091934.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-10T14:55:23.7408659Z [INFO] -------------------------------------------------------
2026-07-10T14:55:24.4399315Z [INFO] Running org.apache.hugegraph.api.ApiTestSuite
2026-07-10T14:56:51.4088467Z [ERROR] Tests run: 161, Failures: 5, Errors: 0, Skipped: 13, Time elapsed: 86.967 s <<< FAILURE! - in org.apache.hugegraph.api.ApiTestSuite
2026-07-10T14:56:51.4090752Z [ERROR] testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.249 s  <<< FAILURE!
2026-07-10T14:56:51.4092774Z java.lang.AssertionError: Response with status 200 and content {"default_graph":[]} expected:<400> but was:<200>
2026-07-10T14:56:51.4094733Z 	at org.apache.hugegraph.api.GraphsApiStandaloneTest.testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError(GraphsApiStandaloneTest.java:211)
2026-07-10T14:56:51.4096156Z 
2026-07-10T14:56:51.4099617Z [ERROR] testUnsetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.22 s  <<< FAILURE!
2026-07-10T14:56:51.4101982Z java.lang.AssertionError: Response with status 200 and content {"default_graph":[]} expected:<400> but was:<200>
2026-07-10T14:56:51.4103662Z 	at org.apache.hugegraph.api.GraphsApiStandaloneTest.testUnsetDefaultGraphReturnsFriendlyError(GraphsApiStandaloneTest.java:191)
2026-07-10T14:56:51.4104796Z 
2026-07-10T14:56:51.4105732Z [ERROR] testSetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.227 s  <<< FAILURE!
2026-07-10T14:56:51.4107404Z java.lang.AssertionError: Response with status 200 and content {"default_graph":["gst_test_graph"]} expected:<400> but was:<200>
2026-07-10T14:56:51.4109042Z 	at org.apache.hugegraph.api.GraphsApiStandaloneTest.testSetDefaultGraphReturnsFriendlyError(GraphsApiStandaloneTest.java:180)
2026-07-10T14:56:51.4110068Z 
2026-07-10T14:56:51.4111044Z [ERROR] testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.224 s  <<< FAILURE!
2026-07-10T14:56:51.4112608Z java.lang.AssertionError
2026-07-10T14:56:51.4113914Z 	at org.apache.hugegraph.api.GraphsApiStandaloneTest.testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError(GraphsApiStandaloneTest.java:202)
2026-07-10T14:56:51.4115225Z 
2026-07-10T14:56:51.4116484Z [ERROR] testGetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.027 s  <<< FAILURE!
2026-07-10T14:56:51.4118206Z java.lang.AssertionError: Response with status 200 and content {"default_graph":["gst_test_graph"]} expected:<400> but was:<200>
2026-07-10T14:56:51.4119900Z 	at org.apache.hugegraph.api.GraphsApiStandaloneTest.testGetDefaultGraphReturnsFriendlyError(GraphsApiStandaloneTest.java:218)
2026-07-10T14:56:51.4120983Z 
2026-07-10T14:56:51.8264784Z [INFO] 
2026-07-10T14:56:51.8272378Z [INFO] Results:
2026-07-10T14:56:51.8274220Z [INFO] 
2026-07-10T14:56:51.8274613Z [ERROR] Failures: 
2026-07-10T14:56:51.8275674Z [ERROR]   GraphsApiStandaloneTest.testGetDefaultGraphReturnsFriendlyError:218->BaseApiTest.assertResponseStatus:573 Response with status 200 and content {"default_graph":["gst_test_graph"]} expected:<400> but was:<200>
2026-07-10T14:56:51.8277350Z [ERROR]   GraphsApiStandaloneTest.testSetDefaultGraphReturnsFriendlyError:180->BaseApiTest.assertResponseStatus:573 Response with status 200 and content {"default_graph":["gst_test_graph"]} expected:<400> but was:<200>
2026-07-10T14:56:51.8279265Z [ERROR]   GraphsApiStandaloneTest.testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError:202
2026-07-10T14:56:51.8280531Z [ERROR]   GraphsApiStandaloneTest.testUnsetDefaultGraphReturnsFriendlyError:191->BaseApiTest.assertResponseStatus:573 Response with status 200 and content {"default_graph":[]} expected:<400> but was:<200>
2026-07-10T14:56:51.8282861Z [ERROR]   GraphsApiStandaloneTest.testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError:211->BaseApiTest.assertResponseStatus:573 Response with status 200 and content {"default_graph":[]} expected:<400> but was:<200>
2026-07-10T14:56:51.8284026Z [INFO] 
2026-07-10T14:56:51.8284528Z [ERROR] Tests run: 161, Failures: 5, Errors: 0, Skipped: 13
2026-07-10T14:56:51.8285142Z [INFO] 
2026-07-10T14:56:51.8285908Z [INFO] ------------------------------------------------------------------------
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 13. `apache__tika__090757115090.txt`
- **Log Filename**: `apache__tika__090757115090.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-30T02:23:19.4393803Z [INFO] 
2026-07-30T02:23:19.4394445Z [INFO] --- surefire:3.5.6:test (default-test) @ tika-woodstox-tests ---
2026-07-30T02:23:19.4411469Z [INFO] Using auto detected provider org.apache.maven.surefire.junitplatform.JUnitPlatformProvider
2026-07-30T02:23:19.4480811Z [INFO] 
2026-07-30T02:23:19.4481705Z [INFO] -------------------------------------------------------
2026-07-30T02:23:19.4482615Z [INFO]  T E S T S
2026-07-30T02:23:19.4483201Z [INFO] -------------------------------------------------------
2026-07-30T02:23:21.1784355Z [INFO] Running org.apache.tika.woodstox.WoodstoxXMLReaderUtilsTest
2026-07-30T02:23:21.3680471Z SLF4J(W): No SLF4J providers were found.
2026-07-30T02:23:21.3685993Z SLF4J(W): Defaulting to no-operation (NOP) logger implementation
2026-07-30T02:23:21.3693575Z SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details.
2026-07-30T02:23:22.3059766Z [INFO] Tests run: 6, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 1.097 s -- in org.apache.tika.woodstox.WoodstoxXMLReaderUtilsTest
2026-07-30T02:23:22.3646863Z [INFO] 
2026-07-30T02:23:22.3655787Z [INFO] Results:
2026-07-30T02:23:22.3656424Z [INFO] 
2026-07-30T02:23:22.3657305Z [INFO] Tests run: 6, Failures: 0, Errors: 0, Skipped: 0
2026-07-30T02:23:22.3658422Z [INFO] 
2026-07-30T02:23:22.3669477Z [INFO] 
2026-07-30T02:23:22.3670355Z [INFO] --- jacoco:0.8.15:report (report) @ tika-woodstox-tests ---
2026-07-30T02:23:22.3676833Z [INFO] Loading execution data file D:\a\tika\tika\tika-integration-tests\tika-woodstox-tests\target\jacoco.exec
2026-07-30T02:23:22.3726440Z [INFO] Analyzed bundle 'tika-woodstox-tests' with 0 classes
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 14. `apache__zeppelin__077616025677.txt`
- **Log Filename**: `apache__zeppelin__077616025677.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-05-24T18:24:20.9865560Z  INFO [2026-05-24 18:24:20,888] ({main} NotebookRepoSync.java[close]:419) - Closing all notebook storages
2026-05-24T18:24:20.9866068Z  INFO [2026-05-24 18:24:20,891] ({main} ZeppelinServer.java[shutdown]:365) - Bye
2026-05-24T18:24:22.9166602Z  INFO [2026-05-24 18:24:22,895] ({main} MiniZeppelinServer.java[shutDown]:305) - ZeppelinServerMock terminated.
2026-05-24T18:24:22.9211279Z [ERROR] Tests run: 11, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 19.55 s <<< FAILURE! -- in org.apache.zeppelin.rest.InterpreterRestApiTest
2026-05-24T18:24:22.9212470Z [ERROR] org.apache.zeppelin.rest.InterpreterRestApiTest.testCreatedInterpreterDependencies -- Time elapsed: 0.017 s <<< FAILURE!
2026-05-24T18:24:22.9213664Z java.lang.AssertionError: 
2026-05-24T18:24:22.9214254Z test create method:
2026-05-24T18:24:22.9214570Z Expected: HTTP response <200>
2026-05-24T18:24:22.9214896Z      but: got <404>
2026-05-24T18:24:22.9215334Z 	at org.hamcrest.MatcherAssert.assertThat(MatcherAssert.java:20)
2026-05-24T18:24:22.9216384Z 	at org.apache.zeppelin.rest.InterpreterRestApiTest.testCreatedInterpreterDependencies(InterpreterRestApiTest.java:189)
    [... elided 2542 lines ...]
2026-05-24T18:29:21.3677467Z [ERROR]   InterpreterRestApiTest.testCreatedInterpreterDependencies:189 test create method:
2026-05-24T18:29:21.3678294Z Expected: HTTP response <200>
2026-05-24T18:29:21.3678661Z      but: got <404>
2026-05-24T18:29:21.3678938Z [INFO] 
2026-05-24T18:29:21.3679311Z [ERROR] Tests run: 1563, Failures: 1, Errors: 0, Skipped: 11
2026-05-24T18:29:21.3680067Z [INFO] 
2026-05-24T18:29:21.3831056Z [INFO] ------------------------------------------------------------------------
2026-05-24T18:29:21.3831509Z [INFO] Reactor Summary for Zeppelin 0.13.0-SNAPSHOT:
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 15. `dask__distributed__084645769341.txt`
- **Log Filename**: `dask__distributed__084645769341.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-01T22:02:54.1281409Z 0.82s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[28-100]
2026-07-01T22:02:54.1281990Z 0.82s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[58-100]
2026-07-01T22:02:54.1282578Z 0.82s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[65-100]
2026-07-01T22:02:54.1283673Z 0.82s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[66-100]
2026-07-01T22:02:54.1285268Z [36m[1m=========================== short test summary info ===========================[0m
2026-07-01T22:02:54.1287396Z [31mFAILED[0m distributed/tests/test_nanny.py::[1mtest_failure_during_worker_initialization[45-100][0m - TimeoutError: Test timeout (30) hit after 30.000552999999968s.
2026-07-01T22:02:54.1288193Z ========== Test stack trace starts here ==========
2026-07-01T22:02:54.1290211Z Stack for <Task pending name='Task-928' coro=<test_failure_during_worker_initialization() running at D:\a\distributed\distributed\distributed\tests\test_nanny.py:637> wait_for=<Future pending cb=[Task.task_wakeup()]>> (most recent call last):
2026-07-01T22:02:54.1291487Z   File "D:\a\distributed\distributed\distributed\tests\test_nanny.py", line 637, in test_failure_during_worker_initialization
2026-07-01T22:02:54.1292031Z     await Nanny(s.address, foo="bar")
2026-07-01T22:02:54.1292602Z [31m================== [31m[1m1 failed[0m, [32m99 passed[0m[31m in 111.91s (0:01:51)[0m[31m ===================[0m
2026-07-01T22:02:54.4788618Z ##[error]Process completed with exit code 1.
2026-07-01T22:02:54.4961399Z ##[group]Run pixi run post-test-ci
2026-07-01T22:02:54.4961758Z [36;1mpixi run post-test-ci[0m
2026-07-01T22:02:54.5020581Z shell: C:\Program Files\PowerShell\7\pwsh.EXE -command ". '{0}'"
2026-07-01T22:02:54.5020934Z env:
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 16. `dask__distributed__084757793457.txt`
- **Log Filename**: `dask__distributed__084757793457.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-02T12:00:40.2791206Z 13.26s call     distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[True-2-100]
2026-07-02T12:00:40.2791948Z 13.26s call     distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-96-100]
2026-07-02T12:00:40.2792825Z 13.07s call     distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[True-14-100]
2026-07-02T12:00:40.2793520Z [36m[1m=========================== short test summary info ===========================[0m
2026-07-02T12:00:40.2795756Z [31mFAILED[0m distributed/tests/test_active_memory_manager.py::[1mtest_RetireWorker_stress[False-17-100][0m - TimeoutError: Test timeout (180) hit after 179.9853481s.
2026-07-02T12:00:40.2796517Z ========== Test stack trace starts here ==========
2026-07-02T12:00:40.2797532Z Stack for <Task pending name='Task-92417' coro=<test_RetireWorker_stress() running at D:\a\distributed\distributed\distributed\tests\test_active_memory_manager.py:1394> wait_for=<_GatheringFuture pending cb=[Task.task_wakeup()]>> (most recent call last):
2026-07-02T12:00:40.2798818Z   File "D:\a\distributed\distributed\distributed\tests\test_active_memory_manager.py", line 1394, in test_RetireWorker_stress
2026-07-02T12:00:40.2799376Z     await asyncio.gather(*tasks)
2026-07-02T12:00:40.2799909Z [31m================= [31m[1m1 failed[0m, [32m199 passed[0m[31m in 2321.17s (0:38:41)[0m[31m ==================[0m
2026-07-02T12:01:09.1499193Z ##[error]Process completed with exit code 1.
2026-07-02T12:01:09.1755082Z ##[group]Run pixi run post-test-ci
2026-07-02T12:01:09.1755524Z [36;1mpixi run post-test-ci[0m
2026-07-02T12:01:09.1825980Z shell: C:\Program Files\PowerShell\7\pwsh.EXE -command ". '{0}'"
2026-07-02T12:01:09.1826344Z env:
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 17. `fla-org__flash-linear-attention__082566635619.txt`
- **Log Filename**: `fla-org__flash-linear-attention__082566635619.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-21T11:35:36.7151167Z     warnings.warn(
2026-06-21T11:35:36.7151292Z 
2026-06-21T11:35:36.7151503Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-06-21T11:35:36.7151904Z =========================== short test summary info ============================
2026-06-21T11:35:36.7152616Z FAILED tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] - RuntimeError: No CUDA GPUs are available
2026-06-21T11:35:36.7153601Z !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
2026-06-21T11:35:36.7154034Z ======================== 1 failed, 18 warnings in 0.57s ========================
2026-06-21T11:35:37.4778429Z ##[error]Process completed with exit code 1.
2026-06-21T11:35:37.4889154Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-21T11:35:37.4890444Z Post job cleanup.
2026-06-21T11:35:37.5664413Z [command]/usr/bin/git version
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 18. `fla-org__flash-linear-attention__086098926451.txt`
- **Log Filename**: `fla-org__flash-linear-attention__086098926451.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-09T10:42:18.0444480Z     instance = cls(
2026-07-09T10:42:18.0444607Z 
2026-07-09T10:42:18.0444809Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-07-09T10:42:18.0445207Z =========================== short test summary info ============================
2026-07-09T10:42:18.0446013Z FAILED tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16] - TypeError: Can't instantiate abstract class FLALayer without an implementation for abstract method 'get_max_length'
2026-07-09T10:42:18.0446799Z !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
2026-07-09T10:42:18.0447166Z ================== 1 failed, 5 passed, 23 warnings in 48.31s ===================
2026-07-09T10:42:18.9930863Z ##[error]Process completed with exit code 1.
2026-07-09T10:42:19.0043740Z Post job cleanup.
2026-07-09T10:42:19.0852243Z [command]/usr/bin/git version
2026-07-09T10:42:19.0893091Z git version 2.34.1
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 19. `floci-io__floci__078678232449.txt`
- **Log Filename**: `floci-io__floci__078678232449.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-05-30T21:20:12.8279103Z /codebuild/output/src
2026-05-30T21:20:12.8279241Z 
2026-05-30T21:20:12.8279655Z [ERROR] Tests run: 26, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 12.39 s <<< FAILURE! -- in com.floci.test.CodeBuildTest
2026-05-30T21:20:12.8280399Z [ERROR] com.floci.test.CodeBuildTest.batchGetBuilds_eventuallySucceeds -- Time elapsed: 2.019 s <<< FAILURE!
2026-05-30T21:20:12.8280911Z org.opentest4j.AssertionFailedError: 
2026-05-30T21:20:12.8281094Z 
2026-05-30T21:20:12.8281186Z expected: "SUCCEEDED"
2026-05-30T21:20:12.8281553Z  but was: "FAULT"
2026-05-30T21:20:12.8282247Z 	at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
2026-05-30T21:20:12.8283641Z 	at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
2026-05-30T21:20:12.8285275Z 	at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
2026-05-30T21:20:12.8286882Z 	at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:500)
2026-05-30T21:20:12.8288187Z 	at com.floci.test.CodeBuildTest.batchGetBuilds_eventuallySucceeds(CodeBuildTest.java:253)
2026-05-30T21:20:12.8289145Z 	at java.base/java.lang.reflect.Method.invoke(Method.java:569)
2026-05-30T21:20:12.8289886Z 	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)
2026-05-30T21:20:12.8290523Z 	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)
2026-05-30T21:20:12.8290953Z 
2026-05-30T21:22:14.6039510Z Filter: email = "compat-user-2baeb8d5-7f8e-49e9-913c-59a3bb1f417e@example.com"
2026-05-30T21:22:14.6055472Z Users found: 1
2026-05-30T21:22:14.6062764Z  - User: compat-user-2baeb8d5-7f8e-49e9-913c-59a3bb1f417e@example.com, email: compat-user-2baeb8d5-7f8e-49e9-913c-59a3bb1f417e@example.com
2026-05-30T21:22:17.0829324Z [ERROR] Failures: 
2026-05-30T21:22:17.0829928Z [ERROR]   CodeBuildTest.batchGetBuilds_eventuallySucceeds:253 
2026-05-30T21:22:17.0830600Z expected: "SUCCEEDED"
2026-05-30T21:22:17.0830999Z  but was: "FAULT"
2026-05-30T21:22:17.0831468Z [ERROR] Tests run: 1087, Failures: 1, Errors: 0, Skipped: 9
2026-05-30T21:22:17.0867670Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.2.5:test (default-test) on project sdk-test-java: There are test failures.
2026-05-30T21:22:17.0868720Z [ERROR] 
2026-05-30T21:22:17.0869245Z [ERROR] Please refer to /app/target/surefire-reports for the individual test results.
2026-05-30T21:22:17.0870209Z [ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 20. `floci-io__floci__085018489189.txt`
- **Log Filename**: `floci-io__floci__085018489189.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-03T14:22:11.7848694Z   </vpcSet>
2026-07-03T14:22:11.7849217Z </DescribeVpcsResponse>
2026-07-03T14:22:14.0336917Z [ERROR] Tests run: 129, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 2.266 s <<< FAILURE! -- in io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest
2026-07-03T14:22:14.0339511Z [ERROR] io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest.describeDefaultVpc -- Time elapsed: 0.025 s <<< FAILURE!
2026-07-03T14:22:14.0340778Z java.lang.AssertionError: 
2026-07-03T14:22:14.0341347Z 1 expectation failed.
2026-07-03T14:22:14.0342035Z XML path DescribeVpcsResponse.vpcSet.item[0].vpcId doesn't match.
2026-07-03T14:22:14.0342921Z Expected: vpc-default
2026-07-03T14:22:14.0343455Z   Actual: vpc-c0f5edad
2026-07-03T14:22:14.0343851Z 
2026-07-03T14:22:14.0344420Z 	at org.codehaus.groovy.vmplugin.v8.IndyInterface.fromCache(IndyInterface.java:344)
    [... elided 38589 lines ...]
2026-07-03T14:27:11.0692126Z [ERROR]   Ec2IntegrationTest.describeDefaultVpc:72 1 expectation failed.
2026-07-03T14:27:11.0693174Z XML path DescribeVpcsResponse.vpcSet.item[0].vpcId doesn't match.
2026-07-03T14:27:11.0694147Z Expected: vpc-default
2026-07-03T14:27:11.0694839Z   Actual: vpc-c0f5edad
2026-07-03T14:27:11.0695328Z 
2026-07-03T14:27:11.0695714Z [INFO] 
2026-07-03T14:27:11.0696477Z [ERROR] Tests run: 7293, Failures: 1, Errors: 0, Skipped: 8
2026-07-03T14:27:11.0697470Z [INFO] 
2026-07-03T14:27:11.0718616Z [INFO] ------------------------------------------------------------------------
2026-07-03T14:27:11.0719499Z [INFO] BUILD FAILURE
2026-07-03T14:27:11.0719839Z [INFO] ------------------------------------------------------------------------
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 21. `gurkenlabs__litiengine__079152380933.txt`
- **Log Filename**: `gurkenlabs__litiengine__079152380933.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-02T19:15:22.2875585Z > Task :litiengine:testClasses
2026-06-02T19:15:25.8818115Z 
2026-06-02T19:15:25.8857098Z > Task :litiengine:test
2026-06-02T19:15:25.8857744Z 
2026-06-02T19:15:25.8858314Z AlignTests > getClampedLocation_InPoint() FAILED
2026-06-02T19:15:25.8859289Z     java.lang.IllegalArgumentException at AlignTests.java:73
2026-06-02T19:15:25.8859964Z 
2026-06-02T19:15:25.8860406Z AlignTests > getClampedLocation_OffPoint() FAILED
2026-06-02T19:15:25.8861396Z     java.lang.IllegalArgumentException at AlignTests.java:64
2026-06-02T19:15:25.9825107Z 
2026-06-02T19:15:25.9856155Z OpenJDK 64-Bit Server VM warning: Sharing is only supported for boot loader classes because bootstrap classpath has been appended
2026-06-02T19:15:28.0875309Z 
2026-06-02T19:15:28.0935485Z > Task :utiliti:test
2026-06-02T19:15:29.2817713Z > Task :utiliti:jacocoTestReport
2026-06-02T19:15:39.0848937Z WARNING: A restricted method in java.lang.foreign.Linker has been called
2026-06-02T19:15:39.0855107Z WARNING: java.lang.foreign.Linker::downcallHandle has been called by de.gurkenlabs.input4j.foreign.NativeHelper in an unnamed module (file:/home/runner/.gradle/caches/modules-2/files-2.1/de.gurkenlabs/input4j/1.2.0/afeb8b9e9c2ff9e40ab0a0b1abf6e85b8bc1a5a5/input4j-1.2.0.jar)
2026-06-02T19:15:39.0858431Z WARNING: Use --enable-native-access=ALL-UNNAMED to avoid a warning for callers in this module
2026-06-02T19:15:39.0872736Z WARNING: Restricted methods will be blocked in a future release unless native access is enabled
2026-06-02T19:15:39.0873643Z 
2026-06-02T19:15:42.8830061Z 
2026-06-02T19:15:42.8854241Z > Task :litiengine:test
2026-06-02T19:15:42.8893293Z 
2026-06-02T19:15:42.8935234Z 1245 tests completed, 2 failed, 3 skipped
2026-06-02T19:15:43.1826377Z 
2026-06-02T19:15:43.1856600Z > Task :litiengine:test FAILED
2026-06-02T19:15:43.1859339Z gradle/actions: Writing build results to /home/runner/work/_temp/.gradle-actions/build-results/__coactions_setup-xvfb-1780427721216.json
2026-06-02T19:15:43.1860549Z 
2026-06-02T19:15:43.1860897Z FAILURE: Build failed with an exception.
2026-06-02T19:15:43.1863911Z 
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 22. `linkedin__brooklin__077863844421.txt`
- **Log Filename**: `linkedin__brooklin__077863844421.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-05-26T13:05:09.6364130Z 2026-05-26 13:05:09 INFO  ClientCnxn:578 - EventThread shut down for session: 0x1000014547c0000
2026-05-26T13:05:09.6364446Z 
2026-05-26T13:05:09.6364592Z 
2026-05-26T13:05:09.6365165Z Gradle suite > Gradle test > com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation FAILED
2026-05-26T13:05:09.6366103Z     java.lang.AssertionError: expected [type:LEADER_DO_ASSIGNMENT] but found [type:HANDLE_ASSIGNMENT_CHANGE]
2026-05-26T13:05:09.6366600Z         at org.testng.Assert.fail(Assert.java:97)
2026-05-26T13:05:09.6366944Z         at org.testng.Assert.assertEqualsImpl(Assert.java:136)
2026-05-26T13:05:09.6367310Z         at org.testng.Assert.assertEquals(Assert.java:118)
2026-05-26T13:05:09.6367639Z         at org.testng.Assert.assertEquals(Assert.java:563)
    [... elided 295 lines ...]
2026-05-26T13:10:59.4571759Z Gradle suite > Gradle test > com.linkedin.datastream.server.dms.TestZookeeperBackedDatastreamStore.testUpdatePartitionAssignmentsWithoutValidHost PASSED
2026-05-26T13:11:07.3564646Z 
2026-05-26T13:11:07.3565057Z 111 tests completed, 1 failed
2026-05-26T13:11:07.7565375Z 
2026-05-26T13:11:07.7565987Z > Task :datastream-server-restli:test FAILED
2026-05-26T13:11:07.7848836Z 
2026-05-26T13:11:07.7849277Z FAILURE: Build failed with an exception.
2026-05-26T13:11:07.7849625Z 
2026-05-26T13:11:07.7849744Z * What went wrong:
2026-05-26T13:11:07.7850175Z Execution failed for task ':datastream-server-restli:test'.
2026-05-26T13:11:07.7851240Z > There were failing tests. See the report at: file:///home/runner/work/brooklin/brooklin/out/datastream-server-restli/test/index.html
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 23. `nats-io__nats.java__080900237539.txt`
- **Log Filename**: `nats-io__nats.java__080900237539.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-11T20:42:58.2318721Z 
2026-06-11T20:42:58.2318981Z ConsumerConfigurationTests > testBuilder() STARTED
2026-06-11T20:42:58.2319353Z 
2026-06-11T20:42:58.2319604Z ConsumerConfigurationTests > testBuilder() FAILED
2026-06-11T20:42:58.2320337Z     org.opentest4j.AssertionFailedError: expected: <PT0S> but was: <null>
2026-06-11T20:42:58.2321316Z         at org.junit.jupiter.api.AssertionFailureBuilder.build(AssertionFailureBuilder.java:151)
2026-06-11T20:42:58.2322414Z         at org.junit.jupiter.api.AssertionFailureBuilder.buildAndThrow(AssertionFailureBuilder.java:132)
    [... elided 6243 lines ...]
2026-06-11T20:50:55.4321059Z         at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:182)
2026-06-11T20:50:55.4321925Z         at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:177)
2026-06-11T20:50:55.4322812Z         at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:1145)
2026-06-11T20:50:55.4323834Z         at io.nats.client.api.ConsumerConfigurationTests.testBuilder(ConsumerConfigurationTests.java:172)
2026-06-11T20:50:55.5318186Z 
2026-06-11T20:50:55.5349288Z 953 tests completed, 6 failed, 5 skipped
2026-06-11T20:50:55.6317346Z 
2026-06-11T20:50:55.6318354Z > Task :test FAILED
2026-06-11T20:50:55.7317388Z 
2026-06-11T20:50:55.7318165Z FAILURE: Build failed with an exception.
2026-06-11T20:50:55.7318674Z 
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 24. `opentripplanner__opentripplanner__081988213338.txt`
- **Log Filename**: `opentripplanner__opentripplanner__081988213338.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-17T19:57:13.5189194Z [[1;31mERROR[m] [1;31m/D:/a/OpenTripPlanner/OpenTripPlanner/street/src/test-fixtures/java/org/opentripplanner/street/GeoJsonIo.java:[24,5] incompatible types: com.bedatadriven.jackson.datatype.jts.JtsModule cannot be converted to com.fasterxml.jackson.databind.Module[m
2026-06-17T19:57:13.5191351Z [[1;31mERROR[m] [1;31m[m
2026-06-17T19:57:13.5191822Z [[1;31mERROR[m] -> [1m[Help 1][m
2026-06-17T19:57:13.5192262Z [[1;31mERROR[m] 
2026-06-17T19:57:13.5192995Z [[1;31mERROR[m] To see the full stack trace of the errors, re-run Maven with the [1m-e[m switch.
2026-06-17T19:57:13.5194104Z [[1;31mERROR[m] Re-run Maven using the [1m-X[m switch to enable full debug logging.
2026-06-17T19:57:13.5194822Z [[1;31mERROR[m] 
2026-06-17T19:57:13.5195692Z [[1;31mERROR[m] For more information about the errors and possible solutions, please read the following articles:
2026-06-17T19:57:13.5197079Z [[1;31mERROR[m] [1m[Help 1][m http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-06-17T19:57:13.5197940Z [[1;31mERROR[m] 
2026-06-17T19:57:13.5198656Z [[1;31mERROR[m] After correcting the problems, you can resume the build with the command
2026-06-17T19:57:13.5199734Z [[1;31mERROR[m]   [1mmvn <args> -rf :street[m
2026-06-17T19:57:13.8781905Z ##[error]Process completed with exit code 1.
2026-06-17T19:57:13.9007671Z Post job cleanup.
2026-06-17T19:57:14.0888528Z Post job cleanup.
2026-06-17T19:57:14.3224762Z [command]"C:\Program Files\Git\bin\git.exe" version
2026-06-17T19:57:14.3523596Z git version 2.54.0.windows.1
2026-06-17T19:57:14.3608854Z Temporarily overriding HOME='D:\a\_temp\6b1c9931-ee2e-4026-a6cc-f13c2b428785' before making global git config changes
2026-06-17T19:57:14.3610166Z Adding repository directory to the temporary git global config as a safe directory
2026-06-17T19:57:14.3619988Z [command]"C:\Program Files\Git\bin\git.exe" config --global --add safe.directory D:\a\OpenTripPlanner\OpenTripPlanner
2026-06-17T19:57:14.3955982Z Removing SSH command configuration
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 25. `opentripplanner__opentripplanner__092404918995.txt`
- **Log Filename**: `opentripplanner__opentripplanner__092404918995.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-08-05T18:33:57.4837253Z [[1;31mERROR[m] [1;31m  location: package org.opentripplanner.transit.service[m
2026-08-05T18:33:57.4838089Z [[1;31mERROR[m] [1;31m[m
2026-08-05T18:33:57.4838691Z [[1;31mERROR[m] -> [1m[Help 1][m
2026-08-05T18:33:57.4839232Z [[1;31mERROR[m] 
2026-08-05T18:33:57.4840309Z [[1;31mERROR[m] To see the full stack trace of the errors, re-run Maven with the [1m-e[m switch.
2026-08-05T18:33:57.4841680Z [[1;31mERROR[m] Re-run Maven using the [1m-X[m switch to enable full debug logging.
2026-08-05T18:33:57.4842494Z [[1;31mERROR[m] 
2026-08-05T18:33:57.4843699Z [[1;31mERROR[m] For more information about the errors and possible solutions, please read the following articles:
2026-08-05T18:33:57.4845623Z [[1;31mERROR[m] [1m[Help 1][m http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-08-05T18:33:57.4846573Z [[1;31mERROR[m] 
2026-08-05T18:33:57.4847556Z [[1;31mERROR[m] After correcting the problems, you can resume the build with the command
2026-08-05T18:33:57.4848661Z [[1;31mERROR[m]   [1mmvn <args> -rf :application[m
2026-08-05T18:33:57.5307162Z ##[error]Process completed with exit code 1.
2026-08-05T18:33:57.5591785Z ##[group]Run codecov/codecov-action@v7
2026-08-05T18:33:57.5592281Z with:
2026-08-05T18:33:57.5592472Z   files: *TEST-*.xml
2026-08-05T18:33:57.5592692Z   report_type: test_results
2026-08-05T18:33:57.5592935Z   disable_file_fixes: false
2026-08-05T18:33:57.5593170Z   disable_search: false
2026-08-05T18:33:57.5593395Z   disable_safe_directory: false
2026-08-05T18:33:57.5593634Z   disable_telem: false
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 26. `robo-code__robocode__084332182805.txt`
- **Log Filename**: `robo-code__robocode__084332182805.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-30T15:36:04.1742847Z > Task :robocode.tests.robots:copyRobotClasses
2026-06-30T15:36:04.1743766Z > Task :robocode.tests.robots:jar
2026-06-30T15:36:20.8716932Z 
2026-06-30T15:36:20.8719880Z > Task :robocode.tests:test
2026-06-30T15:36:20.8720669Z 
2026-06-30T15:36:20.9720512Z TestFairPlay > run FAILED
2026-06-30T15:36:20.9722068Z     java.lang.AssertionError at TestFairPlay.java:31
2026-06-30T15:37:07.1721142Z 
2026-06-30T15:37:07.1829487Z 59 tests completed, 1 failed, 1 skipped
2026-06-30T15:37:07.2720064Z There were failing tests. See the report at: file:///home/runner/work/robocode/robocode/robocode.tests/build/reports/tests/test/index.html
2026-06-30T15:37:07.3729314Z 
2026-06-30T15:37:07.3730171Z > Task :robocode.tests:check
2026-06-30T15:37:07.3730870Z > Task :robocode.tests:build
2026-06-30T15:37:07.3731853Z > Task :robocode.tests.robots:assemble
2026-06-30T15:37:07.3732721Z > Task :robocode.tests.robots:compileTestJava NO-SOURCE
2026-06-30T15:37:07.3733617Z > Task :robocode.tests.robots:processTestResources NO-SOURCE
2026-06-30T15:37:07.3734556Z > Task :robocode.tests.robots:testClasses UP-TO-DATE
2026-06-30T15:37:07.3735319Z > Task :robocode.tests.robots:test NO-SOURCE
2026-06-30T15:37:07.3736085Z > Task :robocode.tests.robots:check UP-TO-DATE
2026-06-30T15:37:07.3736913Z > Task :robocode.tests.robots:build
2026-06-30T15:37:07.3737468Z > Task :robocode.ui:javadocJar
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 27. `sirixdb__sirix__080642754882.txt`
- **Log Filename**: `sirixdb__sirix__080642754882.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-10T19:16:20.6266770Z E           SirixDB error message: {"statusCode":500,"message":"Internal server error"}
2026-06-10T19:16:20.6267097Z 
2026-06-10T19:16:20.6267271Z sirix-python-client/pysirix/errors.py:12: SirixServerError
2026-06-10T19:16:20.6267706Z =========================== short test summary info ============================
2026-06-10T19:16:20.6268645Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'
2026-06-10T19:16:20.6269633Z For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500
2026-06-10T19:16:20.6270216Z SirixDB error message: {"statusCode":500,"message":"Internal server error"}
2026-06-10T19:16:20.6271210Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'
2026-06-10T19:16:20.6272508Z For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500
2026-06-10T19:16:20.6273090Z SirixDB error message: {"statusCode":500,"message":"Internal server error"}
2026-06-10T19:16:20.6274000Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'
2026-06-10T19:16:20.6275325Z For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500
2026-06-10T19:16:20.6275903Z SirixDB error message: {"statusCode":500,"message":"Internal server error"}
2026-06-10T19:16:20.6276807Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'
2026-06-10T19:16:20.6277747Z For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500
2026-06-10T19:16:20.6278314Z SirixDB error message: {"statusCode":500,"message":"Internal server error"}
2026-06-10T19:16:20.6278802Z =================== 4 failed, 62 passed, 1 skipped in 11.80s ===================
2026-06-10T19:16:20.6357206Z Task was destroyed but it is pending!
2026-06-10T19:16:20.6359365Z task: <Task pending name='Task-3' coro=<Auth._sleep_then_refresh() running at /home/runner/work/sirix/sirix/sirix-python-client/pysirix/auth.py:132> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x7f7c48cdb610>()]>>
2026-06-10T19:16:20.6367265Z Task was destroyed but it is pending!
2026-06-10T19:16:20.6368806Z task: <Task pending name='Task-13' coro=<Auth._sleep_then_refresh() running at /home/runner/work/sirix/sirix/sirix-python-client/pysirix/auth.py:132> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x7f7c48ce98b0>()]>>
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 28. `sirixdb__sirix__092352347826.txt`
- **Log Filename**: `sirixdb__sirix__092352347826.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-08-05T15:20:04.2732240Z WARNING: sun.misc.Unsafe::arrayBaseOffset will be removed in a future release
2026-08-05T15:30:56.2939510Z 
2026-08-05T15:30:56.2944890Z > Task :sirix-query:test
2026-08-05T15:30:56.2946890Z 
2026-08-05T15:30:56.2947870Z RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable() FAILED
2026-08-05T15:30:56.2950160Z     org.opentest4j.AssertionFailedError at RegionOnlyPredicateCountTest.java:368
2026-08-05T15:30:57.7198160Z 
2026-08-05T15:30:57.7205480Z RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass() FAILED
2026-08-05T15:30:57.7206860Z     org.opentest4j.AssertionFailedError at RegionOnlyPredicateCountTest.java:436
2026-08-05T15:31:18.3041610Z 
2026-08-05T15:31:18.3045590Z # [StorageProfile] dump called: enabled=false byKind.size=0
2026-08-05T15:31:18.4668800Z 
2026-08-05T15:31:18.4688570Z > Task :sirix-query:test
2026-08-05T15:31:18.4726980Z 
2026-08-05T15:31:18.4732180Z ===== FAILED TESTS (2) =====
2026-08-05T15:31:18.4774570Z FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable(): org.opentest4j.AssertionFailedError: predicate not claimed at all: $u.year gt 1990 and not($u.active) ==> expected: <true> but was: <false>
2026-08-05T15:31:18.4812950Z FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass(): org.opentest4j.AssertionFailedError: no page served from the fused columns for $u.year gt 1990 and not($u.active) (served=0, fellBack=0) ==> expected: <true> but was: <false>
2026-08-05T15:31:18.4974470Z ===== END FAILED TESTS =====
2026-08-05T15:31:18.5314150Z 
2026-08-05T15:31:18.5315260Z 1052 tests completed, 2 failed, 7 skipped
2026-08-05T15:31:19.5519940Z 
2026-08-05T15:31:19.5622730Z > Task :sirix-query:test FAILED
2026-08-05T15:31:19.5695850Z > Task :sirix-kotlin-api:checkKotlinGradlePluginConfigurationErrors SKIPPED
2026-08-05T15:31:22.0562260Z > Task :sirix-kotlin-api:processResources NO-SOURCE
2026-08-05T15:31:22.0573640Z > Task :sirix-kotlin-api:generatePomFileForMavenPublication
2026-08-05T15:31:22.2386130Z > Task :sirix-kotlin-api:processTestResources
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 29. `spiculedata__saiku__086592116219.txt`
- **Log Filename**: `spiculedata__saiku__086592116219.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-11T22:45:37.0439298Z [INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.857 s -- in org.saiku.web.graphql.CubeTypeGeneratorFuzzTest
2026-07-11T22:45:37.0463925Z [INFO] Running org.saiku.web.graphql.CubeTypeGeneratorTest
2026-07-11T22:45:37.0774119Z [INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.002 s -- in org.saiku.web.graphql.CubeTypeGeneratorTest
2026-07-11T22:45:37.1202713Z [INFO] 
2026-07-11T22:45:37.1203063Z [INFO] Results:
2026-07-11T22:45:37.1203453Z [INFO] 
2026-07-11T22:45:37.1203878Z [INFO] Tests run: 495, Failures: 0, Errors: 0, Skipped: 0
2026-07-11T22:45:37.1204424Z [INFO] 
2026-07-11T22:45:37.1210648Z [INFO] 
2026-07-11T22:45:37.1211090Z [INFO] --- jar:3.5.0:jar (default-jar) @ saiku-web ---
2026-07-11T22:45:37.1315409Z [INFO] Building jar: /home/runner/work/saiku/saiku/saiku-core/saiku-web/target/saiku-web-4.6.0.jar
    [... elided 864 lines ...]
2026-07-11T22:47:34.1537148Z [ERROR] -> [Help 1]
2026-07-11T22:47:34.1537781Z [ERROR] 
2026-07-11T22:47:34.1538554Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-07-11T22:47:34.1542589Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-07-11T22:47:34.1543814Z [ERROR] 
2026-07-11T22:47:34.1551536Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-07-11T22:47:34.1552409Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoExecutionException
2026-07-11T22:47:34.1552957Z [ERROR] 
2026-07-11T22:47:34.1553432Z [ERROR] After correcting the problems, you can resume the build with the command
2026-07-11T22:47:34.1553972Z [ERROR]   mvn <args> -rf :saiku-launcher
2026-07-11T22:47:34.2333273Z ##[error]Process completed with exit code 1.
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 30. `thealgorithms__java__095336925353.txt`
- **Log Filename**: `thealgorithms__java__095336925353.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-08-17T09:03:12.0672770Z [INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.002 s -- in com.thealgorithms.backtracking.PermutationTest
2026-08-17T09:03:12.0699711Z [INFO] Running com.thealgorithms.backtracking.KnightsTourTest
2026-08-17T09:03:12.0701208Z [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.003 s -- in com.thealgorithms.backtracking.KnightsTourTest
2026-08-17T09:03:12.4520248Z [INFO] 
2026-08-17T09:03:12.4520767Z [INFO] Results:
2026-08-17T09:03:12.4521624Z [INFO] 
2026-08-17T09:03:12.4535236Z [INFO] Tests run: 9477, Failures: 0, Errors: 0, Skipped: 0
2026-08-17T09:03:12.4536491Z [INFO] 
2026-08-17T09:03:12.4557768Z [INFO] 
2026-08-17T09:03:12.4558539Z [INFO] --- jacoco:0.8.15:report (generate-code-coverage-report) @ Java ---
2026-08-17T09:03:12.4633233Z [INFO] Loading execution data file /home/runner/work/Java/Java/target/jacoco.exec
    [... elided 354 lines ...]
2026-08-17T09:03:35.1286232Z [INFO] Total time:  14.635 s
2026-08-17T09:03:35.1290864Z [INFO] Finished at: 2026-08-17T09:03:35Z
2026-08-17T09:03:35.1291869Z [INFO] ------------------------------------------------------------------------
2026-08-17T09:03:35.1299778Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-checkstyle-plugin:3.6.0:check (default-cli) on project Java: You have 1 Checkstyle violation. -> [Help 1]
2026-08-17T09:03:35.1301393Z [ERROR] 
2026-08-17T09:03:35.1302291Z [ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
2026-08-17T09:03:35.1303455Z [ERROR] Re-run Maven using the -X switch to enable full debug logging.
2026-08-17T09:03:35.1304713Z [ERROR] 
2026-08-17T09:03:35.1305932Z [ERROR] For more information about the errors and possible solutions, please read the following articles:
2026-08-17T09:03:35.1307368Z [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
2026-08-17T09:03:35.1663486Z ##[error]Process completed with exit code 1.
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 31. `unicode-org__cldr__090672967305.txt`
- **Log Filename**: `unicode-org__cldr__090672967305.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-07-29T19:01:50.5668286Z << 25 TEST(S) FAILED >>
2026-07-29T19:01:50.5669120Z [ERROR] Tests run: 2, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 1484 s <<< FAILURE! -- in org.unicode.cldr.unittest.TestShim
2026-07-29T19:01:50.5670322Z [ERROR] org.unicode.cldr.unittest.TestShim.TestAll -- Time elapsed: 1484 s <<< FAILURE!
2026-07-29T19:01:50.5671340Z org.opentest4j.AssertionFailedError:  had errors ==> expected: <0> but was: <25>
2026-07-29T19:01:50.5672245Z 	at org.junit.jupiter.api.AssertionUtils.fail(AssertionUtils.java:55)
2026-07-29T19:01:50.5673130Z 	at org.junit.jupiter.api.AssertionUtils.failNotEqual(AssertionUtils.java:62)
2026-07-29T19:01:50.5674044Z 	at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:150)
2026-07-29T19:01:50.5674924Z 	at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:559)
    [... elided 299 lines ...]
2026-07-29T19:06:59.9927391Z [ERROR] Failures: 
2026-07-29T19:06:59.9927950Z [ERROR]   TestShim.TestAll:41  had errors ==> expected: <0> but was: <25>
2026-07-29T19:06:59.9928351Z [INFO] 
2026-07-29T19:06:59.9928630Z [ERROR] Tests run: 1820, Failures: 1, Errors: 0, Skipped: 24
2026-07-29T19:06:59.9929312Z [INFO] 
2026-07-29T19:06:59.9955303Z [INFO] ------------------------------------------------------------------------
2026-07-29T19:06:59.9956179Z [INFO] Reactor Summary for CLDR All Tools 49.0-SNAPSHOT:
2026-07-29T19:06:59.9956545Z [INFO] 
2026-07-29T19:06:59.9958046Z [INFO] CLDR All Tools ..................................... SUCCESS [  0.002 s]
2026-07-29T19:06:59.9958712Z [INFO] CLDR Code .......................................... FAILURE [29:56 min]
2026-07-29T19:06:59.9959380Z [INFO] CLDR RDF Tools ..................................... SKIPPED
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

## 32. `webauthn4j__webauthn4j__080348707704.txt`
- **Log Filename**: `webauthn4j__webauthn4j__080348707704.txt`
- **Workflow Conclusion**: `failure`
- **Raw Test Result Summary Excerpt**:
```text
2026-06-09T14:35:50.7780354Z EC2COSEKeyTest > validate_with_invalid_curve_test() PASSED
2026-06-09T14:35:50.7780945Z 
2026-06-09T14:35:50.7781357Z EC2COSEKeyTest > json_serialize_deserialize_test() FAILED
2026-06-09T14:35:50.7783112Z     tools.jackson.databind.exc.InvalidDefinitionException: Conflict between type id property '1' and bean property with same name; consider using `JsonTypeInfo.As.EXISTING_PROPERTY` to avoid duplication
2026-06-09T14:35:50.7784767Z      at [No location information]
2026-06-09T14:35:50.7785812Z         at app//tools.jackson.databind.exc.InvalidDefinitionException.from(InvalidDefinitionException.java:80)
2026-06-09T14:35:50.7787608Z         at app//tools.jackson.databind.SerializationContext.reportBadDefinition(SerializationContext.java:1394)
    [... elided 1413 lines ...]
2026-06-09T14:35:57.0726270Z UserVerifyingAuthenticatorAuthenticationVerificationTest > should_throw_when_invalid_challenge_is_provided() PASSED
2026-06-09T14:35:57.0727680Z 
2026-06-09T14:35:57.0728607Z UserVerifyingAuthenticatorAuthenticationVerificationTest > should_throw_when_invalid_tokenBinding_is_provided() PASSED
2026-06-09T14:35:57.0729685Z 
2026-06-09T14:35:57.0730691Z UserVerifyingAuthenticatorAuthenticationVerificationTest > should_throw_when_uv_false_with_userVerificationRequired_true_option() PASSED
2026-06-09T14:35:57.1769548Z 
2026-06-09T14:35:57.1784153Z 1122 tests completed, 2 failed, 2 skipped
2026-06-09T14:35:57.4737232Z 
2026-06-09T14:35:57.4737732Z > Task :webauthn4j-core:test FAILED
2026-06-09T14:35:57.5751441Z 
2026-06-09T14:35:57.5777062Z 
```
- **Expected Class**: ___
- **Expected Identifier Count**: ___
- **Expected Identifiers**: ___

