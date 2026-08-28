# Regression Fixture Manifest: Gradle Stack-Frame Suffix Join (Classloader Prefixes & Spock Method Names)

This directory contains regression fixtures for JVM stack frame parsing in `src/parse/log_gradle.py`.
These labels are provisional and derived via raw grep evidence.

---

## 1. `openremote__openremote__085384361687.txt`

- **Repository:** `openremote__openremote`
- **Job ID:** `085384361687`
- **ISIZE Trailer:** `143686` bytes
- **Why Chosen:** Smallest log in candidate pool combining both `app//` classloader prefix frames and Spock narrative test method names with spaces.
- **Raw Grep Derivation:**
  ```bash
  $ grep -n "FAILED" tests/fixtures/regression/gradle_at_frames/openremote__openremote__085384361687.txt
  822:2026-07-06T13:38:42.2796007Z   Test Does not emit attribute events after attribute deletion FAILED (22.9s)
  1047:2026-07-06T13:49:45.2656400Z   Test Gateway asset provisioning and local manager logic test FAILED (17.6s)

  $ grep -n "at " tests/fixtures/regression/gradle_at_frames/openremote__openremote__085384361687.txt
  825:2026-07-06T13:38:42.2907283Z       at app//spock.util.concurrent.PollingConditions.within(PollingConditions.java:205)
  826:2026-07-06T13:38:42.2932723Z       at app//spock.util.concurrent.PollingConditions.eventually(PollingConditions.java:157)
  827:2026-07-06T13:38:42.2968817Z       at org.openremote.test.assets.ApplyPredictedDataPointsServiceTest.Does not emit attribute events after attribute deletion(ApplyPredictedDataPointsServiceTest.groovy:516)
  834:2026-07-06T13:38:42.3044286Z       at org.openremote.test.assets.ApplyPredictedDataPointsServiceTest.Does not emit attribute events after attribute deletion_closure19(ApplyPredictedDataPointsServiceTest.groovy:517)
  835:2026-07-06T13:38:42.3046889Z       at org.openremote.test.assets.ApplyPredictedDataPointsServiceTest.Does not emit attribute events after attribute deletion_closure19(ApplyPredictedDataPointsServiceTest.groovy)
  836:2026-07-06T13:38:42.3049174Z       at app//spock.util.concurrent.PollingConditions.within(PollingConditions.java:185)
  1054:2026-07-06T13:49:45.2891963Z       at org.openremote.test.gateway.GatewayTest.Gateway asset provisioning and local manager logic test(GatewayTest.groovy:754)
  ```
- **Expected Identifiers:**
  1. `org.openremote.test.assets.ApplyPredictedDataPointsServiceTest#Does not emit attribute events after attribute deletion`
  2. `org.openremote.test.gateway.GatewayTest#Gateway asset provisioning and local manager logic test`

---

## 2. `spring-projects__spring-kafka__081460620251.txt`

- **Repository:** `spring-projects__spring-kafka`
- **Job ID:** `081460620251`
- **ISIZE Trailer:** `65750` bytes
- **Why Chosen:** Minimal plain Java log exercising `app//` classloader prefix stack frames in standard Gradle execution.
- **Raw Grep Derivation:**
  ```bash
  $ grep -n "FAILED" tests/fixtures/regression/gradle_at_frames/spring-projects__spring-kafka__081460620251.txt
  555:2026-06-15T15:41:27.3351164Z AsyncCompletableFutureRetryTopicScenarioTests > oneLongSuccessMsgBetween49ShortFailMsg(TestTopicListener5, MyCustomDltProcessor) FAILED
  639:2026-06-15T15:44:45.2350514Z > Task :spring-kafka:test FAILED

  $ grep -n "at " tests/fixtures/regression/gradle_at_frames/spring-projects__spring-kafka__081460620251.txt
  558:2026-06-15T15:41:27.3482393Z       at app//org.springframework.kafka.retrytopic.AsyncCompletableFutureRetryTopicScenarioTests.oneLongSuccessMsgBetween49ShortFailMsg(AsyncCompletableFutureRetryTopicScenarioTests.java:495)
  ```
- **Expected Identifiers:**
  1. `AsyncCompletableFutureRetryTopicScenarioTests#oneLongSuccessMsgBetween49ShortFailMsg(TestTopicListener5, MyCustomDltProcessor)`
