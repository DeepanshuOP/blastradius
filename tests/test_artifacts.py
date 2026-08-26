"""Unit and contract tests for the artifact capture module (src/harvest/artifacts.py)."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest
import responses

from src.harvest.artifacts import (
    DEFAULT_MAX_ARTIFACT_SIZE_BYTES,
    ExtractionBudgetExceededError,
    ZipSlipError,
    download_artifact_zip,
    extract_test_files_from_zip,
    fetch_run_artifacts,
    filter_test_artifacts,
    store_artifacts_listing,
)
from src.harvest.ratelimit import TokenPool
from src.harvest.rawstore import RawStore


def test_filter_test_artifacts_hbase_names_and_rejections() -> None:
    """filter_test_artifacts must match the four actual HBase artifact names from
    captured fixtures, standard test report names, and reject non-test artifacts."""
    artifacts = [
        # 4 actual HBase artifact names observed in fixtures
        {"name": "yetus-jdk17-hadoop3-unit-check-large-wave-2", "size_in_bytes": 102597177},
        {"name": "yetus-jdk17-hadoop3-unit-check-large-wave-3", "size_in_bytes": 252250140},
        {"name": "yetus-jdk8-hadoop2-unit-check-small", "size_in_bytes": 7526},
        {"name": "yetus-jdk11-hadoop3-unit-check-large-wave-1", "size_in_bytes": 43053738},
        # Standard test artifact names from other repos
        {"name": "test-reports-jdk-25-flavor-proprietary", "size_in_bytes": 5568938},
        {"name": "surefire-reports", "size_in_bytes": 12345},
        {"name": "junit-xml-results", "size_in_bytes": 67890},
        # Plainly non-test artifact names to reject
        {"name": "binary-distribution-tarball", "size_in_bytes": 2048},
        {"name": "docs-html", "size_in_bytes": 4096},
        {"name": "site-preview", "size_in_bytes": 8192},
        {"name": "docker-image-layers", "size_in_bytes": 16384},
    ]

    # Use a size limit large enough to accommodate the 252 MB HBase wave
    result = filter_test_artifacts(artifacts, max_size_bytes=300 * 1024 * 1024)

    assert result.n_artifacts_total == 11
    assert result.n_artifacts_selected == 7
    assert result.n_artifacts_skipped_filter == 4
    assert result.n_artifacts_skipped_size == 0
    assert result.n_artifacts_skipped_expired == 0

    selected_names = [a["name"] for a in result.selected]
    assert "yetus-jdk17-hadoop3-unit-check-large-wave-2" in selected_names
    assert "yetus-jdk17-hadoop3-unit-check-large-wave-3" in selected_names
    assert "yetus-jdk8-hadoop2-unit-check-small" in selected_names
    assert "yetus-jdk11-hadoop3-unit-check-large-wave-1" in selected_names
    assert "test-reports-jdk-25-flavor-proprietary" in selected_names
    assert "surefire-reports" in selected_names
    assert "junit-xml-results" in selected_names

    assert set(result.skipped_filter) == {
        "binary-distribution-tarball",
        "docs-html",
        "site-preview",
        "docker-image-layers",
    }


def test_filter_test_artifacts_oversized_records_name_and_size() -> None:
    """filter_test_artifacts must reject artifacts exceeding max_size_bytes and record
    both the skipped name and size without dropping them silently."""
    artifacts = [
        {"name": "yetus-jdk17-hadoop3-unit-check-large-wave-3", "size_in_bytes": 252250140},
        {"name": "yetus-jdk8-hadoop2-unit-check-small", "size_in_bytes": 7526},
    ]

    # Standard default is 150 MB; the 252 MB artifact must be skipped for size
    result = filter_test_artifacts(artifacts, max_size_bytes=DEFAULT_MAX_ARTIFACT_SIZE_BYTES)

    assert result.n_artifacts_selected == 1
    assert result.selected[0]["name"] == "yetus-jdk8-hadoop2-unit-check-small"
    assert result.n_artifacts_skipped_size == 1
    assert result.skipped_size == [("yetus-jdk17-hadoop3-unit-check-large-wave-3", 252250140)]


def test_filter_test_artifacts_expired_records_name() -> None:
    """filter_test_artifacts must reject expired artifacts and track skipped names."""
    artifacts = [
        {"name": "test-reports", "size_in_bytes": 5000, "expired": True},
        {"name": "junit-results", "size_in_bytes": 5000, "expired": False},
    ]

    result = filter_test_artifacts(artifacts)
    assert result.n_artifacts_selected == 1
    assert result.selected[0]["name"] == "junit-results"
    assert result.n_artifacts_skipped_expired == 1
    assert result.skipped_expired == ["test-reports"]


def test_extract_test_files_real_zip() -> None:
    """extract_test_files_from_zip must safely extract matching test result files from a real zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("output/patch-unit-hbase-server.txt", b"Tests run: 50, Failures: 1, Errors: 0\n")
        zf.writestr("target/surefire-reports/TEST-org.apache.TestFoo.xml", b"<testsuite failures='0'/>")
        zf.writestr("build/test-results/test/TEST-Bar.xml", b"<testsuite failures='1'/>")
        zf.writestr("src/main/java/App.java", b"public class App {}")
        zf.writestr("target/classes/App.class", b"\xca\xfe\xba\xbe")

    zip_bytes = buf.getvalue()
    extraction = extract_test_files_from_zip(zip_bytes)

    assert extraction.total_files_in_zip == 5
    assert len(extraction.files) == 3
    assert extraction.skipped_non_matching == 2
    assert extraction.skipped_oversized == []

    filenames = [f.filename for f in extraction.files]
    assert "output/patch-unit-hbase-server.txt" in filenames
    assert "target/surefire-reports/TEST-org.apache.TestFoo.xml" in filenames
    assert "build/test-results/test/TEST-Bar.xml" in filenames

    patch_file = next(f for f in extraction.files if f.filename == "output/patch-unit-hbase-server.txt")
    assert b"Failures: 1" in patch_file.content


def test_extract_test_files_zipslip_rejected() -> None:
    """ZipSlip path traversal attempts must be detected and rejected with ZipSlipError."""
    # Test relative path traversal
    buf1 = io.BytesIO()
    with zipfile.ZipFile(buf1, "w") as zf:
        zf.writestr("../../etc/passwd", b"root:x:0:0:::")
    with pytest.raises(ZipSlipError, match="unsafe relative path"):
        extract_test_files_from_zip(buf1.getvalue())

    # Test absolute path
    buf2 = io.BytesIO()
    with zipfile.ZipFile(buf2, "w") as zf:
        zf.writestr("/etc/shadow", b"root:::0:0:::")
    with pytest.raises(ZipSlipError, match="unsafe absolute path"):
        extract_test_files_from_zip(buf2.getvalue())


def test_extract_test_files_budget_exceeded() -> None:
    """Cumulative decompressed bytes exceeding safety budget must raise ExtractionBudgetExceededError."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("output/patch-unit-1.txt", b"X" * 1000)
        zf.writestr("output/patch-unit-2.txt", b"Y" * 1000)

    # Budget of 1500 bytes will fail on the second 1000-byte file
    with pytest.raises(ExtractionBudgetExceededError, match="extraction budget 1500 bytes exceeded"):
        extract_test_files_from_zip(buf.getvalue(), max_total_bytes=1500)


def test_extract_test_files_member_oversized_skipped() -> None:
    """Individual files exceeding member cap must be recorded in skipped_oversized and not extracted."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("output/patch-unit-small.txt", b"A" * 100)
        zf.writestr("output/patch-unit-large.txt", b"B" * 1000)

    extraction = extract_test_files_from_zip(buf.getvalue(), max_member_bytes=500)
    assert len(extraction.files) == 1
    assert extraction.files[0].filename == "output/patch-unit-small.txt"
    assert extraction.skipped_oversized == ["output/patch-unit-large.txt"]


@responses.activate
def test_fetch_run_artifacts_paginated() -> None:
    """fetch_run_artifacts must page through results when total_count exceeds per_page."""
    pool = TokenPool(["ghp_dummytoken1234567890abcdef1234567890"])
    run_id = 28155253251
    url = f"https://api.github.com/repos/apache/hbase/actions/runs/{run_id}/artifacts"

    page1_body = {
        "total_count": 3,
        "artifacts": [
            {"id": 101, "name": "yetus-jdk8-hadoop2-unit-check-small", "size_in_bytes": 7526, "expired": False},
            {"id": 102, "name": "docs-html", "size_in_bytes": 4096, "expired": False},
        ],
    }
    page2_body = {
        "total_count": 3,
        "artifacts": [
            {"id": 103, "name": "yetus-jdk11-hadoop3-unit-check-large-wave-1", "size_in_bytes": 43053738, "expired": False},
        ],
    }

    responses.add(
        responses.GET,
        url,
        json=page1_body,
        status=200,
        headers={"X-RateLimit-Remaining": "4990"},
        match=[responses.matchers.query_param_matcher({"per_page": 2, "page": 1})],
    )
    responses.add(
        responses.GET,
        url,
        json=page2_body,
        status=200,
        headers={"X-RateLimit-Remaining": "4989"},
        match=[responses.matchers.query_param_matcher({"per_page": 2, "page": 2})],
    )

    status, artifacts, resps = fetch_run_artifacts("apache", "hbase", run_id, pool=pool, per_page=2)
    assert status == 200
    assert len(artifacts) == 3
    assert len(resps) == 2
    assert artifacts[0]["id"] == 101
    assert artifacts[1]["id"] == 102
    assert artifacts[2]["id"] == 103


@responses.activate
def test_download_artifact_zip() -> None:
    """download_artifact_zip must retrieve zip archive bytes via get_with_backoff."""
    pool = TokenPool(["ghp_dummytoken1234567890abcdef1234567890"])
    artifact_id = 7871957434
    url = f"https://api.github.com/repos/apache/hbase/actions/artifacts/{artifact_id}/zip"
    fake_zip_bytes = b"PK\x03\x04fake_zip_payload"

    responses.add(
        responses.GET,
        url,
        body=fake_zip_bytes,
        status=200,
        headers={"Content-Type": "application/zip", "X-RateLimit-Remaining": "4988"},
    )

    status, content, resp = download_artifact_zip("apache", "hbase", artifact_id, pool=pool)
    assert status == 200
    assert content == fake_zip_bytes
    assert resp.status_code == 200


def test_store_artifacts_listing(tmp_path: Path) -> None:
    """store_artifacts_listing must persist artifact listing envelopes in RawStore under kind 'artifacts'."""
    store = RawStore(tmp_path)
    run_id = 28155253251

    # Construct a mock response object
    resp = responses.Response(
        method="GET",
        url=f"https://api.github.com/repos/apache/hbase/actions/runs/{run_id}/artifacts",
        body=json.dumps({"total_count": 1, "artifacts": [{"id": 1, "name": "unit-test"}]}),
        status=200,
        headers={"ETag": 'W/"12345"', "Date": "Wed, 26 Aug 2026 12:00:00 GMT"},
    )
    # Simulate a requests.Response by making a real request through responses mock
    with responses.RequestsMock() as rsps:
        rsps.add(resp)
        import requests
        real_resp = requests.get(resp.url)

    target_path = store_artifacts_listing(store, "apache/hbase", run_id, [real_resp])
    assert target_path.is_file()
    assert target_path.name == "artifacts.jsonl.gz"

    records = store.read_records("apache/hbase", "artifacts", run_id)
    assert len(records) == 1
    assert records[0].status == 200
    assert records[0].etag == 'W/"12345"'
    body_data = json.loads(records[0].body.decode("utf-8"))
    assert body_data["total_count"] == 1
    assert body_data["artifacts"][0]["name"] == "unit-test"
