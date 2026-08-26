import os
import pytest

from src.harvest.rawstore import KIND_SCOPE, RawRecord, RawStore, RawStoreWriteError, TruncatedRecordError

SHA_A = "a" * 40
SHA_B = "b" * 40

# One plausible key per kind, matching KIND_SCOPE's scope for that kind.
KEY_FOR_KIND = {
    "pulls": 1,  # page
    "pull_files": 1234,  # pr
    "pull_commits": 1234,  # pr
    "runs": SHA_A,  # sha
    "checkruns": SHA_B,  # sha
    "jobs": 555,  # run
    "artifacts": 555,  # run
    "annotations": 777,  # checkrun
    "logs": 888,  # job
}


def _record(url="https://api.github.com/x", status=200, body=b"hello", etag=None):
    return RawRecord(url=url, status=status, fetched_at="2026-08-05T10:00:00+00:00", etag=etag, body=body)


@pytest.mark.parametrize("kind", sorted(KIND_SCOPE))
def test_every_kind_resolves_to_its_expected_scope_directory(tmp_path, kind):
    store = RawStore(tmp_path)
    key = KEY_FOR_KIND[kind]

    path = store.path_for("owner/repo", kind, key)

    scope_dir = path.parent.parent.parent
    assert scope_dir.name == KIND_SCOPE[kind]


def test_pr_1234_and_run_1234_produce_different_directories(tmp_path):
    store = RawStore(tmp_path)

    pr_path = store.path_for("owner/repo", "pull_files", 1234)
    run_path = store.path_for("owner/repo", "jobs", 1234)

    assert pr_path != run_path
    assert not str(run_path).startswith(str(pr_path.parent))
    assert not str(pr_path).startswith(str(run_path.parent))


def test_sha_key_produces_3_char_shard_and_full_sha_unit(tmp_path):
    store = RawStore(tmp_path)
    sha = "0123456789abcdef0123456789abcdef01234567"
    assert len(sha) == 40

    path = store.path_for("owner/repo", "runs", sha)

    unit_dir = path.parent
    shard_dir = unit_dir.parent
    assert shard_dir.name == sha[:3]
    assert unit_dir.name == sha


def test_str_key_to_int_scope_raises_value_error(tmp_path):
    store = RawStore(tmp_path)

    with pytest.raises(ValueError):
        store.path_for("owner/repo", "jobs", "1234")


def test_int_key_to_sha_scope_raises_value_error(tmp_path):
    store = RawStore(tmp_path)

    with pytest.raises(ValueError):
        store.path_for("owner/repo", "runs", 1234)


def test_39_char_sha_raises_value_error(tmp_path):
    store = RawStore(tmp_path)

    with pytest.raises(ValueError):
        store.path_for("owner/repo", "runs", "a" * 39)


def test_uppercase_sha_raises_value_error(tmp_path):
    store = RawStore(tmp_path)

    with pytest.raises(ValueError):
        store.path_for("owner/repo", "runs", "A" * 40)


def test_write_then_read_back_int_keyed_capture(tmp_path):
    store = RawStore(tmp_path)

    store.write_records("owner/repo", "jobs", 42, [_record(body=b"int-keyed")])
    records = store.read_records("owner/repo", "jobs", 42)

    assert records[0].body == b"int-keyed"


def test_write_then_read_back_sha_keyed_capture(tmp_path):
    store = RawStore(tmp_path)
    sha = "f" * 40

    store.write_records("owner/repo", "runs", sha, [_record(body=b"sha-keyed")])
    records = store.read_records("owner/repo", "runs", sha)

    assert records[0].body == b"sha-keyed"


def test_write_then_read_back_byte_identical_utf8_and_binary(tmp_path):
    store = RawStore(tmp_path)
    utf8_body = "hello world ☃".encode("utf-8")
    binary_body = bytes(range(256))  # not valid UTF-8

    store.write_records(
        "owner/repo",
        "jobs",
        1,
        [_record(body=utf8_body), _record(body=binary_body)],
    )
    records = store.read_records("owner/repo", "jobs", 1)

    assert records[0].body == utf8_body
    assert records[1].body == binary_body


def test_overwrite_leaves_exactly_one_file_no_tmp_residue(tmp_path):
    store = RawStore(tmp_path)
    store.write_records("owner/repo", "jobs", 2, [_record(body=b"first")])
    store.write_records("owner/repo", "jobs", 2, [_record(body=b"second")])

    leaf_dir = store.path_for("owner/repo", "jobs", 2).parent
    entries = sorted(p.name for p in leaf_dir.iterdir())

    assert entries == ["jobs.jsonl.gz"]
    records = store.read_records("owner/repo", "jobs", 2)
    assert records[0].body == b"second"


def test_leftover_tmp_from_crash_invisible_and_overwritten(tmp_path):
    store = RawStore(tmp_path)
    store.write_records("owner/repo", "jobs", 3, [_record(body=b"original")])

    final_path = store.path_for("owner/repo", "jobs", 3)
    tmp_path_on_disk = final_path.parent / f"{final_path.name}.tmp"
    tmp_path_on_disk.write_bytes(b"garbage-from-a-crashed-write")

    # the stray .tmp must not be visible to a reader
    records = store.read_records("owner/repo", "jobs", 3)
    assert records[0].body == b"original"

    store.write_records("owner/repo", "jobs", 3, [_record(body=b"redone")])

    leaf_dir = final_path.parent
    entries = sorted(p.name for p in leaf_dir.iterdir())
    assert entries == ["jobs.jsonl.gz"]
    records = store.read_records("owner/repo", "jobs", 3)
    assert records[0].body == b"redone"


def test_path_for_is_deterministic_and_stable(tmp_path):
    store_a = RawStore(tmp_path)
    store_b = RawStore(tmp_path)

    path_a = store_a.path_for("owner/repo", "jobs", 12345)
    path_b = store_b.path_for("owner/repo", "jobs", 12345)

    assert path_a == path_b
    assert path_a == store_a.path_for("owner/repo", "jobs", 12345)


def test_truncated_gzip_raises_not_partial_list(tmp_path):
    store = RawStore(tmp_path)
    store.write_records(
        "owner/repo",
        "jobs",
        4,
        [_record(body=f"record-{i}".encode()) for i in range(50)],
    )
    path = store.path_for("owner/repo", "jobs", 4)
    raw = path.read_bytes()
    truncated = raw[: int(len(raw) * 0.6)]
    path.write_bytes(truncated)

    with pytest.raises(TruncatedRecordError):
        store.read_records("owner/repo", "jobs", 4)


def test_invalid_kind_and_unsafe_repo_raise(tmp_path):
    store = RawStore(tmp_path)

    with pytest.raises(ValueError):
        store.path_for("owner/repo", "not_a_real_kind", 1)

    with pytest.raises(ValueError):
        store.path_for("owner/../../etc", "jobs", 1)


def test_zero_record_write_creates_file_and_exists_true(tmp_path):
    store = RawStore(tmp_path)

    assert store.exists("owner/repo", "jobs", 5) is False

    store.write_records("owner/repo", "jobs", 5, [])

    assert store.exists("owner/repo", "jobs", 5) is True
    assert store.read_records("owner/repo", "jobs", 5) == []


def test_two_writes_to_same_key_from_different_tmp_paths_both_succeed(tmp_path):
    store = RawStore(tmp_path)
    path = store.write_records("owner/repo", "jobs", 100, [_record(body=b"first-write")])
    assert path.is_file()
    assert store.read_records("owner/repo", "jobs", 100)[0].body == b"first-write"

    path2 = store.write_records("owner/repo", "jobs", 100, [_record(body=b"second-write")])
    assert path2 == path
    assert store.read_records("owner/repo", "jobs", 100)[0].body == b"second-write"
    # Ensure no stray tmp files left behind
    assert list(path.parent.glob("*.tmp")) == []


def test_deleting_tmp_file_mid_write_raises_rawstore_write_error(tmp_path, monkeypatch):
    store = RawStore(tmp_path)
    real_fsync = os.fsync

    def deleting_fsync(fd):
        # find and unlink the tmp file on disk while the descriptor is open
        for p in tmp_path.rglob("*.tmp"):
            p.unlink()
        return real_fsync(fd)

    monkeypatch.setattr(os, "fsync", deleting_fsync)

    with pytest.raises(RawStoreWriteError) as exc_info:
        store.write_records("owner/repo", "jobs", 42, [_record(body=b"payload")])

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)
    assert not store.exists("owner/repo", "jobs", 42)
