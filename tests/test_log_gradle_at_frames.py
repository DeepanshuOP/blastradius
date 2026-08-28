"""Tests for Gradle stack-frame suffix join: classloader prefixes and Spock method names.

Per ROADMAP §9.1 T1.1, DECISIONS.md D-31, and Amendment 1 & 2.
"""

from pathlib import Path

from src.parse.log_gradle import (
    _AT_FRAME_RE,
    extract_gradle_failing_test_ids,
    parse_gradle_log,
    parse_gradle_log_with_stats,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "regression" / "gradle_at_frames"


def test_at_frame_re_prefixes_and_spaces():
    """Verify _AT_FRAME_RE matches various JVM module/classloader prefixes and spaced method names."""
    # Standard Java 8 frame
    m = _AT_FRAME_RE.match("    at io.sirix.cache.LinuxMemorySegmentAllocatorTest.testAllocateMaximumSize(LinuxMemorySegmentAllocatorTest.java:48)")
    assert m is not None
    assert m.group(1) == "io.sirix.cache.LinuxMemorySegmentAllocatorTest"
    assert m.group(2) == "testAllocateMaximumSize"

    # app// classloader prefix
    m = _AT_FRAME_RE.match("    at app//io.sirix.service.json.serialize.JsonSerializerTest.testJsonDocument(JsonSerializerTest.java:498)")
    assert m is not None
    assert m.group(1) == "io.sirix.service.json.serialize.JsonSerializerTest"
    assert m.group(2) == "testJsonDocument"

    # java.base/ module prefix
    m = _AT_FRAME_RE.match("    at java.base/java.lang.Thread.run(Thread.java:840)")
    assert m is not None
    assert m.group(1) == "java.lang.Thread"
    assert m.group(2) == "run"

    # Versioned module prefix java.base@21.0.11/
    m = _AT_FRAME_RE.match("    at java.base@21.0.11/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103)")
    assert m is not None
    assert m.group(1) == "jdk.internal.reflect.DirectMethodHandleAccessor"
    assert m.group(2) == "invoke"

    # Spock / Groovy method name with spaces
    m = _AT_FRAME_RE.match("    at org.openremote.test.assets.ApplyPredictedDataPointsServiceTest.Does not emit attribute events after attribute deletion(ApplyPredictedDataPointsServiceTest.groovy:585)")
    assert m is not None
    assert m.group(1) == "org.openremote.test.assets.ApplyPredictedDataPointsServiceTest"
    assert m.group(2) == "Does not emit attribute events after attribute deletion"

    # Kotlin backticked method name with spaces
    m = _AT_FRAME_RE.match("    at org.atmosphere.ai.embabel.EmbabelAdapterTest.runtime falls back to Ai factory path when no deployed agent matches(EmbabelAdapterTest.kt:245)")
    assert m is not None
    assert m.group(1) == "org.atmosphere.ai.embabel.EmbabelAdapterTest"
    assert m.group(2) == "runtime falls back to Ai factory path when no deployed agent matches"


def test_at_frame_re_rejects_trailing_space_and_nodejs():
    """Verify Amendment 1: method group must not end in whitespace, rejecting Node.js frame shapes."""
    # Node.js frame has space before '('
    assert _AT_FRAME_RE.match("    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)") is None
    assert _AT_FRAME_RE.match("    at async Object.readFile (node:internal/fs/promises:1252:14)") is None
    assert _AT_FRAME_RE.match("    at ChildProcess.emit (node:events:521:24)") is None


def test_at_frame_re_callsite_rejects_slashes_and_chevrons():
    """Verify Amendment 2: call site skips method captures containing '/' or '>'."""
    log_text = """
> Task :test
MyTest > chevron > method FAILED
    at com.example.MyTest.bad/method(MyTest.java:10)
    at com.example.MyTest.bad>method(MyTest.java:10)
    at com.example.MyTest.goodMethod(MyTest.java:10)
"""
    outcomes, stats = parse_gradle_log_with_stats(log_text)
    # The chevron failure was MyTest > chevron > method FAILED -> test_id = 'MyTest#method'
    # 'goodMethod' is in stack_fqcns, 'bad/method' and 'bad>method' are not.
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "MyTest#method"


def test_gradle_suffix_join_with_app_prefix():
    """Verify bare class chevron failure joins FQCN when stack frame has app// prefix."""
    log_text = """
> Task :test
JsonSerializerTest > testJsonDocumentWithMetadata FAILED
    at app//org.junit.Assert.assertEquals(Assert.java:117)
    at app//io.sirix.service.json.serialize.JsonSerializerTest.testJsonDocumentWithMetadata(JsonSerializerTest.java:498)
"""
    outcomes = parse_gradle_log(log_text)
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "io.sirix.service.json.serialize.JsonSerializerTest#testJsonDocumentWithMetadata"


def test_gradle_suffix_join_with_spock_spaces():
    """Verify bare class chevron failure joins FQCN when method name contains spaces."""
    log_text = """
> Task :test
ApplyPredictedDataPointsServiceTest > Does not emit attribute events after attribute deletion FAILED
    at app//spock.util.concurrent.PollingConditions.within(PollingConditions.java:205)
    at org.openremote.test.assets.ApplyPredictedDataPointsServiceTest.Does not emit attribute events after attribute deletion(ApplyPredictedDataPointsServiceTest.groovy:585)
"""
    outcomes = parse_gradle_log(log_text)
    assert len(outcomes) == 1
    assert outcomes[0].test_id == "org.openremote.test.assets.ApplyPredictedDataPointsServiceTest#Does not emit attribute events after attribute deletion"


def test_fixture_openremote_joined_fqcn():
    """Verify regression fixture openremote__openremote__085384361687.txt joins FQCNs with spaces."""
    fixture_path = FIXTURES_DIR / "openremote__openremote__085384361687.txt"
    body = fixture_path.read_text(encoding="utf-8")

    outcomes, stats = parse_gradle_log_with_stats(body)
    test_ids = {o.test_id for o in outcomes}

    expected_ids = {
        "org.openremote.test.assets.ApplyPredictedDataPointsServiceTest#Does not emit attribute events after attribute deletion",
        "org.openremote.test.gateway.GatewayTest#Gateway asset provisioning and local manager logic test",
    }
    assert test_ids == expected_ids
    assert stats.total_outcomes == 2


def test_fixture_spring_kafka_extracted():
    """Verify regression fixture spring-projects__spring-kafka__081460620251.txt extracts outcome."""
    fixture_path = FIXTURES_DIR / "spring-projects__spring-kafka__081460620251.txt"
    body = fixture_path.read_text(encoding="utf-8")

    test_ids = extract_gradle_failing_test_ids(body)
    assert len(test_ids) == 1
    assert "AsyncCompletableFutureRetryTopicScenarioTests#oneLongSuccessMsgBetween49ShortFailMsg(TestTopicListener5, MyCustomDltProcessor)" in test_ids
