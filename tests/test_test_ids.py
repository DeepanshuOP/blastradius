"""Contract tests for normalize_test_id() and TestId dataclass.

Per ROADMAP §34.4 C.2 (T1.1g), D-03, D-09.

Every test case is labelled with its provenance:
- OBSERVED: real strings captured in data/raw (check-run annotations).
- SPEC: constructed according to ROADMAP §34.4 C.2 and framework specs.
"""

from __future__ import annotations

import dataclasses
import pytest

from src.parse.test_ids import TestId, normalize_test_id


TEST_CASES = [
    # --- 17 Baseline Verified Cases ---
    # 1. Maven Surefire XML standard testcase
    (
        '<testcase classname="com.example.FooTest" name="testBar"/>',
        "com.example.FooTest#testBar",
        # SPEC: Standard Maven Surefire XML element
    ),
    # 2. Maven Surefire XML parameterized testcase
    (
        '<testcase classname="com.example.FooTest" name="testBar[0]"/>',
        "com.example.FooTest#testBar",
        # SPEC: JUnit 4/5 parameterized test in Surefire XML
    ),
    # 3. Maven Surefire XML nested class ($)
    (
        '<testcase classname="com.example.FooTest$NestedTest" name="testNested"/>',
        "com.example.FooTest$NestedTest#testNested",
        # SPEC: JUnit 5 @Nested test in Surefire XML
    ),
    # 4. Maven console error with line number
    (
        "[ERROR] com.example.FooTest.testBar:42 expected:<true>",
        "com.example.FooTest#testBar",
        # SPEC: Maven surefire / failsafe console error line
    ),
    # 5. Maven Surefire console failure summary
    (
        "[ERROR] testBar(com.example.FooTest) Time elapsed: 0.01 s <<< FAILURE!",
        "com.example.FooTest#testBar",
        # SPEC: Surefire failure summary line with elapsed time
    ),
    # 6. Gradle console test failure line
    (
        "com.example.FooTest > testBar FAILED",
        "com.example.FooTest#testBar",
        # SPEC: Gradle standard test logger failure line
    ),
    # 7. Gradle console parameterized test failure
    (
        "com.example.FooTest > testBar(String) [1] FAILED",
        "com.example.FooTest#testBar",
        # SPEC: Gradle JUnit 5 parameterized test failure line
    ),
    # 8. Pytest JUnit XML with classname module + class
    (
        '<testcase classname="tests.test_foo.TestFoo" name="test_bar"/>',
        "tests/test_foo.py::TestFoo::test_bar",
        # SPEC: pytest --junitxml output with test class
    ),
    # 9. Pytest JUnit XML module only (bare function)
    (
        '<testcase classname="tests.test_foo" name="test_bar"/>',
        "tests/test_foo.py::test_bar",
        # SPEC: pytest --junitxml output for bare test function
    ),
    # 10. Pytest console failure line
    (
        "FAILED tests/test_foo.py::TestFoo::test_bar - AssertionError",
        "tests/test_foo.py::TestFoo::test_bar",
        # SPEC: pytest standard console short summary line
    ),
    # 11. Pytest Windows backslashes normalization
    (
        "tests\\unit\\test_auth.py::TestAuth::test_login",
        "tests/unit/test_auth.py::TestAuth::test_login",
        # SPEC: Windows path separators in pytest output
    ),
    # 12. Check annotation Python with class and method
    (
        'path="tests/test_foo.py" title="TestFoo.test_bar"',
        "tests/test_foo.py::TestFoo::test_bar",
        # SPEC: GitHub check-run annotation on pytest test
    ),
    # 13. Check annotation Java with source path
    (
        'path="src/test/java/com/example/FooTest.java" title="FooTest.testBar"',
        "com.example.FooTest#testBar",
        # SPEC: GitHub check-run annotation on Java test file
    ),
    # 14. Check annotation prose from ArchUnit in captured corpus
    (
        'path="graphql.archunit.JSpecifyAnnotationsCheck" title="exempted classes should not be annotated with @NullMarked or @NullUnmarked (graphql.archunit.JSpecifyAnnotationsCheck) failed"',
        None,
        # OBSERVED: Captured from graphql-java__graphql-java check-run annotations
    ),
    # 15. Gradle task status line (non-test output)
    (
        "> Task :test FAILED",
        None,
        # SPEC: Gradle build lifecycle task failure header
    ),
    # 16. Maven build summary line (non-test output)
    (
        "[INFO] BUILD SUCCESS",
        None,
        # SPEC: Maven reactor summary line
    ),
    # 17. TypeScript test identifier (cut per Decision D-03)
    (
        "src/foo.spec.ts::Foo::renders",
        None,
        # SPEC: TypeScript/Jest test identifier
    ),

    # --- 15+ Additional Required Test Cases ---
    # 18. Java nested class via Gradle
    (
        "com.example.FooTest$NestedTest > testNested FAILED",
        "com.example.FooTest$NestedTest#testNested",
        # SPEC: Gradle console output with nested class ($)
    ),
    # 19. JUnit 5 parameterized name with a display string
    (
        "com.example.FooTest > testWithDisplayName(String) [1] custom display name FAILED",
        "com.example.FooTest#testWithDisplayName",
        # SPEC: JUnit 5 @ParameterizedTest with @DisplayName / invocation text
    ),
    # 20. Maven console with an ISO-8601 timestamp prefix
    (
        "2026-08-17T14:30:00.123Z [ERROR] com.example.FooTest.testBar:42 expected:<true>",
        "com.example.FooTest#testBar",
        # SPEC: GitHub Actions timestamped log line for Maven console error
    ),
    # 21. Maven console with ANSI escapes
    (
        "\x1b[31m[ERROR]\x1b[0m com.example.FooTest.testBar:42 expected:<true>",
        "com.example.FooTest#testBar",
        # SPEC: Terminal colored output with ANSI escape sequences
    ),
    # 22. Pytest with (setup) lifecycle suffix
    (
        "FAILED tests/test_foo.py::TestFoo::test_bar (setup) - RuntimeError",
        "tests/test_foo.py::TestFoo::test_bar",
        # SPEC: pytest fixture setup failure
    ),
    # 23. Pytest with (teardown) lifecycle suffix
    (
        "FAILED tests/test_foo.py::TestFoo::test_bar (teardown) - RuntimeError",
        "tests/test_foo.py::TestFoo::test_bar",
        # SPEC: pytest fixture teardown failure
    ),
    # 24. Pytest parameterised [2-3-5]
    (
        "tests/test_calc.py::test_add[2-3-5]",
        "tests/test_calc.py::test_add",
        # SPEC: pytest parameterized test ID with numeric argument values
    ),
    # 25. Pytest with a line-number suffix
    (
        "tests/test_foo.py:42::TestFoo::test_bar",
        "tests/test_foo.py::TestFoo::test_bar",
        # SPEC: pytest console failure reporting with source line number
    ),
    # 26. Bare Java canonical id
    (
        "com.example.FooTest#testBar",
        "com.example.FooTest#testBar",
        # SPEC: Direct canonical Java test identifier
    ),
    # 27. Java class with a $ nested class in Surefire XML
    (
        '<testcase classname="com.example.FooTest$InnerClass" name="testInner"/>',
        "com.example.FooTest$InnerClass#testInner",
        # SPEC: Inner class test execution in Surefire XML
    ),
    # 28. Empty string input
    (
        "",
        None,
        # SPEC: Genuinely unparseable empty input
    ),
    # 29. Whitespace-only string input
    (
        "   \t\n  ",
        None,
        # SPEC: Genuinely unparseable whitespace input
    ),
    # 30. Gradle subproject task line
    (
        "> Task :subproject:test FAILED",
        None,
        # SPEC: Subproject Gradle task lifecycle message
    ),
    # 31. Check annotation with a null title
    (
        'path="src/test/java/com/example/FooTest.java" title="null"',
        None,
        # SPEC: Check-run annotation where title attribute is string "null"
    ),
    # 32. Check annotation whose title is a bare method name
    (
        'path="src/test/java/com/example/FooTest.java" title="testBar"',
        "com.example.FooTest#testBar",
        # SPEC: Check-run annotation with bare Java method name in title
    ),

    # --- Supplementary Edge Cases & Observed Data ---
    # 33. Check annotation on TypeScript path (cut per D-03)
    (
        'path="saiku-ui/src/lib/dashboard/appTheme.test.ts" title="appTheme.test.ts"',
        None,
        # OBSERVED: Captured from raw annotation logs in repository frame
    ),
    # 34. Check annotation with empty title
    (
        'path="spring-cloud-config-client/src/test/java/org/springframework/cloud/config/client/ConfigServerConfigDataLoaderTests.java" title=""',
        None,
        # OBSERVED: Captured from Spring Cloud Config annotation logs
    ),
    # 35. Pytest JUnit XML with file attribute
    (
        '<testcase classname="TestFoo" name="test_bar" file="tests/test_foo.py"/>',
        "tests/test_foo.py::TestFoo::test_bar",
        # SPEC: Pytest JUnit XML with explicit file attribute
    ),
    # 36. Gradle subproject test execution line
    (
        ":core:test > com.example.FooTest > testBar FAILED",
        "com.example.FooTest#testBar",
        # SPEC: Gradle multi-project build test logger line
    ),
    # 37. NFKC fullwidth Unicode character normalization
    (
        "com.example.FooTest#test\uff22ar",
        "com.example.FooTest#testBar",
        # SPEC: Unicode NFKC normalization on method name (fullwidth B)
    ),
]


@pytest.mark.parametrize("raw_input,expected_canonical", [
    (raw, exp) for raw, exp, *_ in TEST_CASES
])
def test_normalize_test_id_table(raw_input: str, expected_canonical: str | None) -> None:
    result = normalize_test_id(raw_input)
    if expected_canonical is None:
        assert result is None, f"Expected None for {raw_input!r}, got {result!r}"
    else:
        assert result is not None, f"Expected {expected_canonical!r} for {raw_input!r}, got None"
        assert result.canonical == expected_canonical
        assert isinstance(result.canonical, str)
        assert result.raw == raw_input


def test_test_id_dataclass_fields() -> None:
    t = TestId(
        lang="java",
        raw="com.example.FooTest#testBar",
        canonical="com.example.FooTest#testBar",
        params=None,
        class_name="com.example.FooTest",
        method_name="testBar",
        path=None,
    )
    assert t.lang == "java"
    assert t.raw == "com.example.FooTest#testBar"
    assert t.canonical == "com.example.FooTest#testBar"
    assert t.class_name == "com.example.FooTest"
    assert t.method_name == "testBar"
    assert t.path is None
    assert t.params is None

    # Dataclass is frozen (immutable)
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.canonical = "other"  # type: ignore[misc]


def test_parameter_extraction_details() -> None:
    # Pytest parameterized
    t_py = normalize_test_id("tests/test_calc.py::test_add[2-3-5]")
    assert t_py is not None
    assert t_py.canonical == "tests/test_calc.py::test_add"
    assert t_py.params == "[2-3-5]"
    assert t_py.method_name == "test_add"
    assert t_py.path == "tests/test_calc.py"

    # Gradle JUnit 5 parameterized
    t_gradle = normalize_test_id("com.example.FooTest > testBar(String) [1] FAILED")
    assert t_gradle is not None
    assert t_gradle.canonical == "com.example.FooTest#testBar"
    assert t_gradle.params == "(String) [1]"
    assert t_gradle.class_name == "com.example.FooTest"
    assert t_gradle.method_name == "testBar"

    # Maven Surefire XML parameterized
    t_xml = normalize_test_id('<testcase classname="com.example.FooTest" name="testBar[0]"/>')
    assert t_xml is not None
    assert t_xml.canonical == "com.example.FooTest#testBar"
    assert t_xml.params == "[0]"


def test_case_preservation_guarantee() -> None:
    # Java class and method names must NEVER be casefolded
    t1 = normalize_test_id("com.example.FooTest#testBar")
    t2 = normalize_test_id("com.example.footest#testbar")
    assert t1 is not None and t2 is not None
    assert t1.canonical == "com.example.FooTest#testBar"
    assert t2.canonical == "com.example.footest#testbar"
    assert t1.canonical != t2.canonical  # Crucial: NO collision in join key

    # Python path component IS casefolded, but class and func names are preserved
    t_py = normalize_test_id("Tests/Test_Foo.py::TestFoo::test_bar")
    assert t_py is not None
    assert t_py.canonical == "tests/test_foo.py::TestFoo::test_bar"
    assert t_py.class_name == "TestFoo"
    assert t_py.method_name == "test_bar"


def test_unparseable_inputs_return_none() -> None:
    assert normalize_test_id("") is None
    assert normalize_test_id("   ") is None
    assert normalize_test_id("Random prose that does not match any format") is None
    assert normalize_test_id("::error:: Workflow timed out") is None
    assert normalize_test_id("> Task :compileJava") is None
