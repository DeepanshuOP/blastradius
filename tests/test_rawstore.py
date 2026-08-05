"""Tests for src.harvest.rawstore — RawStore against real files under tmp_path.

No mocks: every test writes and reads actual gzipped files on disk.
"""

import pytest

from src.harvest.rawstore import RawRecord, RawStore, TruncatedRecordError


def _record(url="https://api.github.com/x", status=200, body=b"hello", etag=None):
    return RawRecord(url=url, status=status, fetched_at="2026-08-05T10:00:00+00:00", etag=etag, body=body)


def test_write_then_read_back_byte_identical_utf8_and_binary(tmp_path):
    store = RawStore(tmp_path)
    utf8_body = "hello world ☃".encode("utf-8")
    binary_body = bytes(range(256))  # not valid UTF-8

    store.write_records(
        "owner/repo",
        1,
        "jobs",
        [_record(body=utf8_body), _record(body=binary_body)],
    )
    records = store.read_records("owner/repo", 1, "jobs")

    assert records[0].body == utf8_body
    assert records[1].body == binary_body


def test_overwrite_leaves_exactly_one_file_no_tmp_residue(tmp_path):
    store = RawStore(tmp_path)
    store.write_records("owner/repo", 2, "jobs", [_record(body=b"first")])
    store.write_records("owner/repo", 2, "jobs", [_record(body=b"second")])

    leaf_dir = store.path_for("owner/repo", 2, "jobs").parent
    entries = sorted(p.name for p in leaf_dir.iterdir())

    assert entries == ["jobs.jsonl.gz"]
    records = store.read_records("owner/repo", 2, "jobs")
    assert records[0].body == b"second"


def test_leftover_tmp_from_crash_invisible_and_overwritten(tmp_path):
    store = RawStore(tmp_path)
    store.write_records("owner/repo", 3, "jobs", [_record(body=b"original")])

    final_path = store.path_for("owner/repo", 3, "jobs")
    tmp_path_on_disk = final_path.parent / f"{final_path.name}.tmp"
    tmp_path_on_disk.write_bytes(b"garbage-from-a-crashed-write")

    # the stray .tmp must not be visible to a reader
    records = store.read_records("owner/repo", 3, "jobs")
    assert records[0].body == b"original"

    store.write_records("owner/repo", 3, "jobs", [_record(body=b"redone")])

    leaf_dir = final_path.parent
    entries = sorted(p.name for p in leaf_dir.iterdir())
    assert entries == ["jobs.jsonl.gz"]
    records = store.read_records("owner/repo", 3, "jobs")
    assert records[0].body == b"redone"


def test_path_for_is_deterministic_and_stable(tmp_path):
    store_a = RawStore(tmp_path)
    store_b = RawStore(tmp_path)

    path_a = store_a.path_for("owner/repo", 12345, "jobs")
    path_b = store_b.path_for("owner/repo", 12345, "jobs")

    assert path_a == path_b
    assert path_a == store_a.path_for("owner/repo", 12345, "jobs")


def test_truncated_gzip_raises_not_partial_list(tmp_path):
    store = RawStore(tmp_path)
    store.write_records(
        "owner/repo",
        4,
        "jobs",
        [_record(body=f"record-{i}".encode()) for i in range(50)],
    )
    path = store.path_for("owner/repo", 4, "jobs")
    raw = path.read_bytes()
    truncated = raw[: int(len(raw) * 0.6)]
    path.write_bytes(truncated)

    with pytest.raises(TruncatedRecordError):
        store.read_records("owner/repo", 4, "jobs")


def test_invalid_kind_and_unsafe_repo_raise(tmp_path):
    store = RawStore(tmp_path)

    with pytest.raises(ValueError):
        store.path_for("owner/repo", 1, "not_a_real_kind")

    with pytest.raises(ValueError):
        store.path_for("owner/../../etc", 1, "jobs")


def test_zero_record_write_creates_file_and_exists_true(tmp_path):
    store = RawStore(tmp_path)

    assert store.exists("owner/repo", 5, "jobs") is False

    store.write_records("owner/repo", 5, "jobs", [])

    assert store.exists("owner/repo", 5, "jobs") is True
    assert store.read_records("owner/repo", 5, "jobs") == []
