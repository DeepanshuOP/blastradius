"""Tests for `analysis/secret_scan.py` against a real checked-in fixture bundle.

Ground truth is hand-written in
`tests/fixtures/secret_scan/release/EXPECTED.md`. The `ghp_…` value in the
fixture is a sequential placeholder matching the GitHub-token shape only.
"""

from pathlib import Path

from analysis.secret_scan import redact, run, scan_file, scan_text

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "secret_scan" / "release"

FIXTURE_TOKEN = "ghp_0123456789abcdefghijABCDEFGHIJ012345"


def _by_pattern(findings):
    return {f["pattern"]: f for f in findings}


def test_clean_file_yields_no_findings():
    assert scan_file(FIXTURE_ROOT / "clean.csv") == []


def test_findings_file_matches_hand_written_expectations():
    findings = _by_pattern(scan_file(FIXTURE_ROOT / "findings.csv"))

    assert set(findings) == {"email", "github_token", "internal_host"}
    for finding in findings.values():
        assert finding["column"] == "note"
        assert finding["count"] == 1

    assert findings["email"]["severity"] == "REVIEW"
    assert findings["github_token"]["severity"] == "BLOCKER"
    # REVIEW, not BLOCKER: on the real bundle every internal_host match is a
    # harvested public identifier. See analysis/secret_scan.py's docstring.
    assert findings["internal_host"]["severity"] == "REVIEW"


def test_scan_text_finds_the_token_shape():
    assert scan_text(f"leaked {FIXTURE_TOKEN} in config") == {
        "github_token": {FIXTURE_TOKEN}
    }


def test_matched_text_is_never_reported_verbatim():
    findings = scan_file(FIXTURE_ROOT / "findings.csv")
    assert FIXTURE_TOKEN not in repr(findings)
    assert "maintainer@example.com" not in repr(findings)


def test_redact_keeps_three_characters_and_the_length():
    assert redact(FIXTURE_TOKEN) == f"ghp…({len(FIXTURE_TOKEN)})"


def test_run_over_the_bundle_reports_one_blocker():
    stats = run(root=str(FIXTURE_ROOT))

    assert stats["files_scanned"] == 2
    assert stats["files_skipped"] == 0
    assert stats["blockers"] == 1
    assert stats["review"] == 2


def test_limit_takes_a_path_sorted_prefix():
    stats = run(root=str(FIXTURE_ROOT), limit=1)

    assert stats["files_scanned"] == 1
    assert stats["findings"] == []


def test_as_of_skips_files_modified_after_the_pin():
    stats = run(root=str(FIXTURE_ROOT), as_of="2000-01-01T00:00:00Z")

    assert stats["files_scanned"] == 0
    assert stats["files_skipped"] == 2
    assert stats["blockers"] == 0


def test_missing_release_directory_is_not_a_blocker():
    stats = run(root=str(FIXTURE_ROOT / "does-not-exist"))

    assert stats["files_scanned"] == 0
    assert stats["blockers"] == 0
