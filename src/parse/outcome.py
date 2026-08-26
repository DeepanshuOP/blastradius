"""BlastRadius — Canonical TestOutcome record.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and SCHEMAS.md.
Represents a single test execution outcome emitted by any label source
(GH Actions annotations, JUnit XML artifacts, raw build logs, or re-execution).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TestOutcome:
    """Canonical representation of a single test outcome.

    Attributes:
        test_id: Canonical or raw test identifier string (e.g. 'com.foo.BarTest#testBaz'
            or 'tests/test_foo.py::TestFoo::test_baz').
        parser_confidence: Provisional confidence score in [0.0, 1.0] for the extracted
            identifier and outcome. Required; no default is provided to ensure callers
            deliberately specify an explicit, shape-justified confidence level.
        run_id: Parent GitHub Actions workflow run ID, if known.
        job_id: GitHub Actions job ID, if known.
        repo: Repository name (e.g. 'owner/repo'), if known.
        head_sha: Commit SHA under test, if known.
        test_file: Repository-relative source path to the test file, if resolved.
        status: Literal["pass", "fail", "error", "skip"] = "fail"
        duration_s: Test execution duration in seconds, if recorded.
        failure_message: Failure error message or truncated assertion failure (<=2000 chars).
        label_source: Literal["annotation", "artifact", "log", "reexec"] = "log"
    """

    test_id: str
    parser_confidence: float
    run_id: int | None = None
    job_id: int | None = None
    repo: str | None = None
    head_sha: str | None = None
    test_file: str | None = None
    status: Literal["pass", "fail", "error", "skip"] = "fail"
    duration_s: float | None = None
    failure_message: str | None = None
    label_source: Literal["annotation", "artifact", "log", "reexec"] = "log"

    __test__ = False
