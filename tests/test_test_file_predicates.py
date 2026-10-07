"""`is_conventional_test_file` against real paths; `is_test_filename` kept as the permissive sensitivity predicate."""

from __future__ import annotations

import pytest

from src.parse.changeset import is_conventional_test_file, is_test_filename


@pytest.mark.parametrize("path", [
    "src/test/java/org/apache/flink/FooBar.java",          # under src/test/
    "flink-table/src/test/java/org/x/Helper.java",          # under src/test/, name says nothing
    "core/src/test/kotlin/Fixture.kt",
    "src/main/java/org/x/FooTest.java",                    # *Test
    "src/main/java/org/x/FooTests.java",                   # *Tests
    "src/main/java/org/x/TestUtils.java",                  # Test*
    "src/main/java/org/x/FooIT.java",                      # *IT
    "build-logic/src/main/groovy/SpecTest.groovy",
    "tests/test_parser.py",                                 # test_*.py
    "pkg/parser_test.py",                                   # *_test.py
    "tests/helpers.py",                                     # .py under tests/
    "pkg/test/conftest.py",                                 # .py under test/
])
def test_conventional_test_files_are_accepted(path: str) -> None:
    assert is_conventional_test_file(path)


@pytest.mark.parametrize("path", [
    "src/main/python/latest.py",                           # "test" only as a substring of "latest"
    "src/contest.py",
    "pkg/attest.py",
    "src/main/java/org/x/Latest.java",
    "src/main/java/org/x/Contest.java",
    "src/main/java/org/x/Digest.java",
    "src/test/resources/x.json",                           # a test resource, not a test source
    "src/test/resources/application.yml",
    "docs/testing.md",
    "pkg/protests/handler.py",                             # directory is 'protests', not 'tests'
    "src/main/java/org/x/Foo.java",
    "README",
])
def test_non_test_files_are_rejected(path: str) -> None:
    assert not is_conventional_test_file(path)


def test_the_loose_predicate_accepts_what_the_conventional_one_rejects() -> None:
    for path in ("src/main/python/latest.py", "src/contest.py", "src/test/resources/x.json", "docs/testing.md"):
        assert is_test_filename(path)
        assert not is_conventional_test_file(path)
