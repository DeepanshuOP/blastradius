import pytest
from pathlib import Path
from src.parse.test_ids import TestId
from src.parse.test_files import resolve_test_file
from tests.conftest import requires_data

# Every test below reads a specific clone. Guarding on the `data/clones`
# directory alone was correct only while it was empty: once any other clone
# lands there (e.g. the graph layer's mini-corpus) these tests start running
# against repos that are not present and fail instead of skipping. Name what
# they actually need.
pytestmark = requires_data(
    "data/clones/apache__beam",
    "data/clones/apache__dolphinscheduler",
    "data/clones/apache__fineract",
    "data/clones/floci-io__floci",
    "data/clones/sirixdb__sirix",
)


# PREDICT: 6 tests will pass. Total suite: whatever is currently there + 6. (Actually wait, let me run `pytest` first to see current test count).

def test_resolve_exact_java():
    """Derive expectations:
    git -C data/clones/apache__fineract ls-tree -r HEAD --name-only | grep FeignExceptionTest
    Result: fineract-client-feign/src/test/java/org/apache/fineract/client/feign/FeignExceptionTest.java
    """
    repo_root = Path("data/clones/apache__fineract")
    tid = TestId(lang="java", raw="", canonical="org.apache.fineract.client.feign.FeignExceptionTest#foo",
                 params=None, class_name="org.apache.fineract.client.feign.FeignExceptionTest", method_name="foo", path=None)
    res = resolve_test_file(tid, repo_root)
    assert res.status == "exact"
    assert res.path == "fineract-client-feign/src/test/java/org/apache/fineract/client/feign/FeignExceptionTest.java"

def test_resolve_nested_class():
    """Derive expectations:
    Nested class Outer$Inner should map to Outer.java.
    """
    repo_root = Path("data/clones/apache__fineract")
    tid = TestId(lang="java", raw="", canonical="org.apache.fineract.client.feign.FeignExceptionTest$Nested#foo",
                 params=None, class_name="org.apache.fineract.client.feign.FeignExceptionTest$Nested", method_name="foo", path=None)
    res = resolve_test_file(tid, repo_root)
    assert res.status == "exact"
    assert res.path == "fineract-client-feign/src/test/java/org/apache/fineract/client/feign/FeignExceptionTest.java"

def test_resolve_kotlin():
    """Derive expectations:
    git -C data/clones/sirixdb__sirix ls-tree -r HEAD --name-only | grep ExampleResourceTest
    Result: bundles/sirix-distributed/src/test/kotlin/io/sirix/ExampleResourceTest.kt
    """
    repo_root = Path("data/clones/sirixdb__sirix")
    tid = TestId(lang="kotlin", raw="", canonical="io.sirix.ExampleResourceTest#foo",
                 params=None, class_name="io.sirix.ExampleResourceTest", method_name="foo", path=None)
    res = resolve_test_file(tid, repo_root)
    assert res.status == "exact"
    assert res.path == "bundles/sirix-distributed/src/test/kotlin/io/sirix/ExampleResourceTest.kt"

def test_resolve_python_subdir():
    """Derive expectations:
    git -C data/clones/floci-io__floci ls-tree -r HEAD --name-only | grep test_cloudformation_naming.py
    Result: compatibility-tests/sdk-test-python/tests/test_cloudformation_naming.py
    """
    repo_root = Path("data/clones/floci-io__floci")
    tid = TestId(lang="python", raw="", canonical="tests/test_cloudformation_naming.py::test_foo",
                 params=None, class_name=None, method_name="test_foo", path="tests/test_cloudformation_naming.py")
    res = resolve_test_file(tid, repo_root)
    assert res.status == "exact"
    assert res.path == "compatibility-tests/sdk-test-python/tests/test_cloudformation_naming.py"

def test_resolve_ambiguous():
    """Derive expectations:
    git -C data/clones/apache__dolphinscheduler ls-tree -r HEAD --name-only | grep FlinkArgsUtilsTest.java
    Returns two identical package paths in different modules.
    """
    repo_root = Path("data/clones/apache__dolphinscheduler")
    tid = TestId(lang="java", raw="", canonical="org.apache.dolphinscheduler.plugin.task.flink.FlinkArgsUtilsTest#foo",
                 params=None, class_name="org.apache.dolphinscheduler.plugin.task.flink.FlinkArgsUtilsTest", method_name="foo", path=None)
    res = resolve_test_file(tid, repo_root)
    assert res.status == "ambiguous"
    assert res.path is None
    assert res.candidates_considered == 2

def test_resolve_bare_class_exact():
    repo_root = Path("data/clones/apache__fineract")
    tid = TestId(lang="java", raw="", canonical="FeignExceptionTest#foo",
                 params=None, class_name="FeignExceptionTest", method_name="foo", path=None)
    res = resolve_test_file(tid, repo_root)
    assert res.status == "exact"
    assert res.confidence == 0.5
    assert res.path == "fineract-client-feign/src/test/java/org/apache/fineract/client/feign/FeignExceptionTest.java"

def test_resolve_bare_class_ambiguous():
    """Derive expectations:
    git -C data/clones/apache__beam ls-tree -r HEAD --name-only | grep /TestUtils.java$
    Returns 5 distinct paths.
    """
    repo_root = Path("data/clones/apache__beam")
    tid = TestId(lang="java", raw="", canonical="TestUtils#foo",
                 params=None, class_name="TestUtils", method_name="foo", path=None)
    res = resolve_test_file(tid, repo_root)
    assert res.status == "ambiguous"
    assert res.candidates_considered == 5
    assert res.path is None

def test_resolve_not_found():
    repo_root = Path("data/clones/apache__fineract")
    tid = TestId(lang="java", raw="", canonical="org.apache.beam.MissingTest#foo",
                 params=None, class_name="org.apache.beam.MissingTest", method_name="foo", path=None)
    res = resolve_test_file(tid, repo_root)
    assert res.status == "not_found"
    assert res.path is None
