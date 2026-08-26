"""Artifact capture and test result extraction module (T0.3d, ROADMAP §8.3 / §9.1).

Provides pure and HTTP-backed functions to list, filter, download, and extract
test artifacts from GitHub Actions workflow runs without coupling to daemon orchestration.

All HTTP operations go through ratelimit.py's get_with_backoff().
"""

from __future__ import annotations

import io
import logging
import re
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import requests

from src.harvest.ratelimit import TokenPool, get_with_backoff
from src.harvest.rawstore import RawRecord, RawStore

_logger = logging.getLogger(__name__)

# Default artifact name regex.
# Includes 'unit' and 'yetus' to cover systems like Apache HBase that run tests inside
# Docker containers via Apache Yetus and name artifacts 'yetus-*-unit-check-*'.
DEFAULT_ARTIFACT_NAME_PATTERN = re.compile(
    r"(?i)test|junit|report|surefire|results|unit|yetus"
)

# Default test result file pattern within unpacked zip archives.
DEFAULT_TEST_FILE_PATTERN = re.compile(
    r"(?i)(?:patch-unit-.*\.txt|TEST-.*\.xml|.*\.surefire|.*\bsurefire-reports/.*|.*\btest-results/.*|.*\.trx|.*test.*\.xml|.*test.*\.json|.*test.*\.log|.*test.*\.txt)$"
)

# Size caps and safety limits.
#
# Measured maximum test artifact in corpus: 252,250,140 bytes (~240.6 MB,
# apache/hbase yetus-jdk17-hadoop3-unit-check-large-wave-3 from fixture
# tests/fixtures/logs/apache__hbase__082907939305.txt:4681).
# Set to 300 MB to safely accommodate large Yetus archives while guarding against unbounded downloads.
#
# Note on storage budget: This cap governs temporary download bandwidth and memory cost,
# NOT disk storage. Extraction is selective (only matching test result files are extracted)
# and the downloaded zip archive is discarded immediately after extraction. The 200-500 GB
# disk budget applies to extracted test results and raw logs, not the temporary zip downloads.
DEFAULT_MAX_ARTIFACT_SIZE_BYTES = 300 * 1024 * 1024  # 300 MB
DEFAULT_MAX_EXTRACTED_BYTES = 500 * 1024 * 1024  # 500 MB decompression bomb guard
DEFAULT_MAX_MEMBER_BYTES = 100 * 1024 * 1024  # 100 MB per single file in archive


class ZipSlipError(ValueError):
    """Raised when a zip archive contains a path attempting directory traversal."""


class ExtractionBudgetExceededError(ValueError):
    """Raised when decompressed bytes exceed the safety extraction budget."""


@dataclass
class FilterResult:
    """Outcome of filtering an artifact listing for candidate test artifacts."""

    selected: list[dict[str, Any]] = field(default_factory=list)
    skipped_filter: list[str] = field(default_factory=list)
    skipped_size: list[tuple[str, int]] = field(default_factory=list)
    skipped_expired: list[str] = field(default_factory=list)
    all_names: list[str] = field(default_factory=list)

    @property
    def n_artifacts_total(self) -> int:
        return len(self.all_names)

    @property
    def n_artifacts_selected(self) -> int:
        return len(self.selected)

    @property
    def n_artifacts_skipped_filter(self) -> int:
        return len(self.skipped_filter)

    @property
    def n_artifacts_skipped_size(self) -> int:
        return len(self.skipped_size)

    @property
    def n_artifacts_skipped_expired(self) -> int:
        return len(self.skipped_expired)


@dataclass
class ExtractedFile:
    """An individual test file safely extracted from an artifact archive."""

    filename: str
    content: bytes
    size: int


@dataclass
class ExtractionResult:
    """Summary of extracting test files from a zip archive."""

    files: list[ExtractedFile] = field(default_factory=list)
    total_files_in_zip: int = 0
    total_uncompressed_bytes: int = 0
    skipped_non_matching: int = 0
    skipped_oversized: list[str] = field(default_factory=list)


def filter_test_artifacts(
    artifacts: Sequence[dict[str, Any]],
    *,
    name_pattern: re.Pattern | str = DEFAULT_ARTIFACT_NAME_PATTERN,
    max_size_bytes: int = DEFAULT_MAX_ARTIFACT_SIZE_BYTES,
) -> FilterResult:
    """Filter an artifact list for non-expired, test-relevant, size-compliant items.

    Records EVERY artifact name seen into the result so filter coverage can be
    measured empirically.
    """
    if isinstance(name_pattern, str):
        name_pattern = re.compile(name_pattern)

    result = FilterResult()
    for art in artifacts:
        name = str(art.get("name", ""))
        result.all_names.append(name)

        if art.get("expired") is True:
            result.skipped_expired.append(name)
            continue

        size = int(art.get("size_in_bytes", 0))
        if size > max_size_bytes:
            result.skipped_size.append((name, size))
            continue

        if not name_pattern.search(name):
            result.skipped_filter.append(name)
            continue

        result.selected.append(dict(art))

    return result


def fetch_run_artifacts(
    owner: str,
    repo: str,
    run_id: int,
    *,
    pool: TokenPool,
    per_page: int = 100,
) -> tuple[int, list[dict[str, Any]], list[requests.Response]]:
    """List all artifacts uploaded for a workflow run (Endpoint 8).

    GET https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts
    Pages through results if total_count > per_page.
    Returns (status_code, all_artifacts, responses).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
    all_artifacts: list[dict[str, Any]] = []
    responses: list[requests.Response] = []
    page = 1

    while True:
        resp = get_with_backoff(
            url, params={"per_page": per_page, "page": page}, pool=pool
        )
        responses.append(resp)
        if not resp.ok:
            return resp.status_code, all_artifacts, responses

        data = resp.json()
        artifacts = data.get("artifacts", [])
        all_artifacts.extend(artifacts)

        total_count = data.get("total_count", len(all_artifacts))
        if len(all_artifacts) >= total_count or not artifacts or len(artifacts) < per_page:
            break
        page += 1

    return 200, all_artifacts, responses


def download_artifact_zip(
    owner: str,
    repo: str,
    artifact_id: int,
    *,
    pool: TokenPool,
) -> tuple[int, bytes, requests.Response]:
    """Download an artifact zip archive (GET /repos/{owner}/{repo}/actions/artifacts/{id}/zip).

    get_with_backoff follows the 302 redirect to blob storage and strips
    Authorization headers on cross-origin requests.
    Returns (status_code, zip_bytes, response).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip"
    resp = get_with_backoff(url, pool=pool)
    return resp.status_code, resp.content, resp


def extract_test_files_from_zip(
    zip_bytes: bytes,
    *,
    file_pattern: re.Pattern | str = DEFAULT_TEST_FILE_PATTERN,
    max_total_bytes: int = DEFAULT_MAX_EXTRACTED_BYTES,
    max_member_bytes: int = DEFAULT_MAX_MEMBER_BYTES,
) -> ExtractionResult:
    """Safely extract matching test files from an artifact zip archive.

    Security & resource invariants enforced:
    1. ZipSlip guard: rejects absolute paths or paths with '..' traversal components.
    2. Decompression bomb guard: tracks cumulative decompressed bytes against max_total_bytes.
    3. Member size cap: skips individual files exceeding max_member_bytes.
    4. File pattern filter: extracts only members matching file_pattern.
    """
    if isinstance(file_pattern, str):
        file_pattern = re.compile(file_pattern)

    result = ExtractionResult()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        infolist = zf.infolist()
        result.total_files_in_zip = len(infolist)

        for member in infolist:
            if member.is_dir():
                continue

            target_name = member.filename
            # ZipSlip guard
            if target_name.startswith("/") or target_name.startswith("\\"):
                raise ZipSlipError(f"unsafe absolute path in zip archive: {target_name!r}")

            path_obj = Path(target_name)
            if ".." in path_obj.parts:
                raise ZipSlipError(f"unsafe relative path traversal in zip archive: {target_name!r}")

            # Check individual member declared size
            if member.file_size > max_member_bytes:
                result.skipped_oversized.append(target_name)
                continue

            # Check file pattern
            if not file_pattern.search(target_name):
                result.skipped_non_matching += 1
                continue

            # Check decompression bomb budget against declared size
            if result.total_uncompressed_bytes + member.file_size > max_total_bytes:
                raise ExtractionBudgetExceededError(
                    f"extraction budget {max_total_bytes} bytes exceeded by member {target_name!r}"
                )

            data = zf.read(member)
            actual_size = len(data)

            if actual_size > max_member_bytes:
                result.skipped_oversized.append(target_name)
                continue

            if result.total_uncompressed_bytes + actual_size > max_total_bytes:
                raise ExtractionBudgetExceededError(
                    f"extraction budget {max_total_bytes} bytes exceeded by member {target_name!r}"
                )

            result.total_uncompressed_bytes += actual_size
            result.files.append(
                ExtractedFile(filename=target_name, content=data, size=actual_size)
            )

    return result


def _record_from_response(response: requests.Response) -> RawRecord:
    """Construct a RawRecord envelope from a requests.Response."""
    fetched_at = datetime.now(timezone.utc).isoformat()
    return RawRecord(
        url=response.url,
        status=response.status_code,
        fetched_at=fetched_at,
        etag=response.headers.get("ETag"),
        body=response.content,
    )


def store_artifacts_listing(
    store: RawStore,
    repo: str,
    run_id: int,
    responses: Sequence[requests.Response],
) -> Path:
    """Persist artifact listing response envelopes in RawStore under kind 'artifacts', key run_id."""
    records = [_record_from_response(r) for r in responses]
    return store.write_records(repo, "artifacts", run_id, records)
