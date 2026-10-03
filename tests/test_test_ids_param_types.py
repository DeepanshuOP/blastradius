"""JUnit 5 parameter types must not be read as the declaring class.

Gradle prints a JUnit 5 test method with its declared parameter types, e.g.
``UIDataTessdataControllerTest > downloadTessdataLanguages_allSuccess(Path) FAILED``
for a method taking a ``@TempDir Path``. In ``normalize_test_id``, the JUnit 4
Surefire form ``testBar(com.example.FooTest)`` -- where the parenthesised token
really is the declaring class -- was tried first, so the parameter type was read
as the class and the real class was discarded.

Fixture and hand-derived expectations:
``tests/fixtures/regression/junit5_param_types/MANIFEST.md``. Per CLAUDE.md rule
3 the log is a real checked-in capture, never a mock; neither affected job
appears in ``docs/session/holdout-exclusion.txt``.
"""

from __future__ import annotations

from pathlib import Path

from src.parse.dispatch import dispatch_parse_log
from src.parse.test_ids import normalize_test_id

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "regression" / "junit5_param_types"
STIRLING_FIXTURE = FIXTURES_DIR / "Stirling-Tools__Stirling-PDF__085060314571.txt"

# Hand-derived from the raw log text; MANIFEST.md §1 carries the same table.
STIRLING_EXPECTED_IDS = frozenset(
    {
        "UIDataTessdataControllerTest#downloadTessdataLanguages_allSuccess",
        "UIDataTessdataControllerTest#downloadTessdataLanguages_blocksPathTraversal",
        "UIDataTessdataControllerTest#downloadTessdataLanguages_handlesInvalidSanitizedLanguage",
        "UIDataTessdataControllerTest#downloadTessdataLanguages_handlesNetworkFailure",
        "UIDataTessdataControllerTest#downloadTessdataLanguages_rejectsUnknownLanguage",
        "UIDataTessdataControllerTest#downloadTessdataLanguages_returnsForbiddenWhenNotWritable",
        "UIDataTessdataControllerTest#downloadTessdataLanguages_successAndFailureMixed",
        "UIDataTessdataControllerTest#tessdataLanguages_emptyDirectory",
        "UIDataTessdataControllerTest#tessdataLanguages_handlesNonExistentDirectory",
        "UIDataTessdataControllerTest#tessdataLanguages_marksNotWritable",
        "UIDataTessdataControllerTest#tessdataLanguages_nonTraineddataFilesAreIgnored",
        "UIDataTessdataControllerTest#tessdataLanguages_returnsInstalledAvailableAndWritable",
    }
)


def _canonical_ids(body: str, job_id: str, repo: str) -> set[str]:
    """Compose dispatch and normalisation exactly as analysis/corpus_parse.py does.

    ``dispatch_parse_log`` emits the method with its parameter list still
    attached; ``analysis/corpus_parse.py`` canonicalises each ``TestOutcome``
    through ``normalize_test_id``. This mirrors that composition so the test
    pins the ids that actually reach ``parsed_outcomes.parquet``.

    Args:
        body: Raw job-log text.
        job_id: GitHub Actions job id, for the outcome records.
        repo: ``owner/name`` slug, for the outcome records.

    Returns:
        The set of canonical ``test_id`` strings the pipeline would persist.
    """
    outcomes = dispatch_parse_log(
        body, run_id="regression", job_id=job_id, repo=repo, head_sha="0" * 40
    )
    ids: set[str] = set()
    for outcome in outcomes:
        normalized = normalize_test_id(outcome.test_id)
        if normalized is not None:
            ids.add(normalized.canonical)
    return ids


def test_parameter_type_is_not_read_as_the_declaring_class():
    """A bare `(Path)` parameter type never becomes the class of a canonical id."""
    normalized = normalize_test_id(
        "UIDataTessdataControllerTest#downloadTessdataLanguages_allSuccess(Path)"
    )
    assert normalized is not None
    assert normalized.class_name == "UIDataTessdataControllerTest"
    assert normalized.method_name == "downloadTessdataLanguages_allSuccess"
    assert (
        normalized.canonical
        == "UIDataTessdataControllerTest#downloadTessdataLanguages_allSuccess"
    )
    assert normalized.params == "(Path)"


def test_an_already_qualified_class_survives_a_parameter_type():
    """The sirix case: a complete FQCN is not replaced by the parameter type.

    MANIFEST.md §2 records why that job's 12 MB body is not checked in; the
    property is asserted here against the canonical string instead.
    """
    normalized = normalize_test_id(
        "io.sirix.index.IndexListenerStaleTrxTest"
        "#perResourceIsolationAcrossOverlappingWriteTransactions(Path)"
    )
    assert normalized is not None
    assert normalized.class_name == "io.sirix.index.IndexListenerStaleTrxTest"
    assert normalized.canonical == (
        "io.sirix.index.IndexListenerStaleTrxTest"
        "#perResourceIsolationAcrossOverlappingWriteTransactions"
    )
    assert normalized.params == "(Path)"


def test_the_gradle_chevron_line_normalizes_to_the_chevron_class():
    """The raw Gradle line, verbatim from the fixture, keeps its chevron class."""
    normalized = normalize_test_id(
        "UIDataTessdataControllerTest > downloadTessdataLanguages_allSuccess(Path) FAILED"
    )
    assert normalized is not None
    assert (
        normalized.canonical
        == "UIDataTessdataControllerTest#downloadTessdataLanguages_allSuccess"
    )


def test_the_junit4_surefire_form_is_unaffected():
    """Pattern A still owns `method(DeclaringClass)`, which has no `#` to claim."""
    for raw in (
        "testBar(com.example.FooTest)",
        "[ERROR] testBar(com.example.FooTest)",
    ):
        normalized = normalize_test_id(raw)
        assert normalized is not None, raw
        assert normalized.class_name == "com.example.FooTest", raw
        assert normalized.canonical == "com.example.FooTest#testBar", raw

    parameterized = normalize_test_id("testBar[0](com.example.FooTest)")
    assert parameterized is not None
    assert parameterized.canonical == "com.example.FooTest#testBar"
    assert parameterized.params == "[0]"


def test_fixture_yields_the_twelve_hand_derived_ids():
    """Every hand-derived id in MANIFEST.md §1 is emitted for the real log."""
    ids = _canonical_ids(
        STIRLING_FIXTURE.read_text(),
        job_id="085060314571",
        repo="Stirling-Tools/Stirling-PDF",
    )
    missing = STIRLING_EXPECTED_IDS - ids
    assert not missing, f"hand-derived ids absent from parser output: {sorted(missing)}"


def test_fixture_yields_no_path_classed_id():
    """No id emitted for the real log carries `Path` as its class."""
    ids = _canonical_ids(
        STIRLING_FIXTURE.read_text(),
        job_id="085060314571",
        repo="Stirling-Tools/Stirling-PDF",
    )
    offenders = sorted(i for i in ids if i.split("#", 1)[0] == "Path")
    assert not offenders, f"parameter type read as declaring class: {offenders}"
