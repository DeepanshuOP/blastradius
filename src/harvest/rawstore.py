"""Atomic raw-capture writer (T0.3a support, ROADMAP §8 / §8.3).

One gzipped JSONL file per (repo, kind, key) under `data/raw/`. "Capture
wide, parse narrow": this module only ever writes and reads whole raw
response envelopes — it never parses their contents.

Path scheme: `data/raw/{owner}__{repo}/{scope}/{shard}/{unit}/{kind}.jsonl.gz`.
`scope` is derived from `kind` via `KIND_SCOPE` — the caller never passes
it, so a kind/scope mismatch is unrepresentable. Six key spaces exist
because §8.3's nine endpoints are keyed by five different GitHub id kinds
(PR number, commit sha, run id, check-run id, job id) plus a page number
for the PR listing itself; `runs` and `checkruns` share the `sha` scope
because both are looked up by commit sha, not by an id of their own.

Deliberately NOT `{owner}__{repo}/{yyyy-mm}/{kind}.jsonl.gz` as originally
sketched in ROADMAP §8.3 — that shares one file across every run in a month,
which conflicts with cursor.py's contract that redoing an `in_flight` run
must overwrite safely: a shared monthly file would make "redo one run" cost
a full-month rewrite, and a crash mid-rewrite could damage other runs' data
that happen to share the file. Scoping one file to exactly one
(repo, kind, key) means a redo only ever touches its own bytes, and
`path_for()` is a pure function of that key alone — no timestamp in it, so
the same logical capture always resolves to the same path across redos.

Also deliberately NOT a single bare `run_id` integer accepted for every
kind (the prior scheme in this module): PR numbers, commit shas, run ids,
check-run ids, and job ids are unrelated key spaces that collide when
forced through one field — e.g. PR #1234's `pull_files` and workflow run
#1234's `jobs` would land in the same shard/unit directory with nothing in
the path to tell them apart. See D-19 in docs/DECISIONS.md.
"""

from __future__ import annotations

import base64
import gzip
import json
import logging
import os
import re
import uuid
import zlib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path("data/raw")

# Which key space each capture kind is addressed by. The caller never
# chooses a scope directly — it is looked up here from `kind`, so a
# kind/scope mismatch cannot be constructed.
KIND_SCOPE: dict[str, str] = {
    "pulls": "page",
    "pull_files": "pr",
    "pull_commits": "pr",
    "runs": "sha",
    "branch_runs": "branch",
    "checkruns": "sha",
    "jobs": "run",
    "artifacts": "run",
    "annotations": "checkrun",
    "logs": "job",
}

ALLOWED_KINDS = frozenset(KIND_SCOPE)

_SHA_SCOPE = "sha"
_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")

_logger = logging.getLogger(__name__)


class RawStoreWriteError(Exception):
    """Raised when writing a raw capture record to disk fails."""


class TruncatedRecordError(Exception):
    """Raised when a raw capture file is missing, corrupt, or cut short."""


@dataclass
class RawRecord:
    url: str
    status: int
    fetched_at: str  # ISO-8601 UTC, explicit offset
    etag: str | None
    body: bytes  # exact bytes, regardless of on-disk encoding


def _validate_kind(kind: str) -> None:
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"unknown capture kind {kind!r}; must be one of {sorted(ALLOWED_KINDS)}")


def _validate_repo(repo: str) -> None:
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"repo must be 'owner/repo': {repo!r}")
    for part in parts:
        if ".." in part or part.startswith(".") or "/" in part or "\\" in part:
            raise ValueError(f"unsafe repo string: {repo!r}")


def _validate_key(kind: str, key: int | str) -> tuple[str, str, str]:
    """Resolve (kind, key) to (scope, shard, unit), enforcing the key type each scope requires."""
    scope = KIND_SCOPE[kind]
    if scope == "branch":
        if not isinstance(key, str):
            raise ValueError(f"kind {kind!r} requires a str branch key")
        # sanitize the branch name for a safe directory name
        import urllib.parse
        safe_key = urllib.parse.quote(key, safe="")
        # make shard from first 3 chars or fallback
        shard_str = safe_key[:3].ljust(3, "_")
        return scope, shard_str, safe_key
        
    if scope == _SHA_SCOPE:
        if not isinstance(key, str):
            raise ValueError(
                f"kind {kind!r} (scope {scope!r}) requires a str sha key, "
                f"got {type(key).__name__}: {key!r}"
            )
        if not _SHA_PATTERN.fullmatch(key):
            raise ValueError(
                f"invalid sha key {key!r} for kind {kind!r}; "
                "must be exactly 40 lowercase hex characters"
            )
        return scope, key[:3], key
    if not isinstance(key, int) or isinstance(key, bool):
        raise ValueError(
            f"kind {kind!r} (scope {scope!r}) requires an int key, "
            f"got {type(key).__name__}: {key!r}"
        )
    return scope, f"{key % 1000:03d}", f"{key:012d}"


def _encode_body(body: bytes) -> tuple[str, str]:
    try:
        return body.decode("utf-8"), "utf8"
    except UnicodeDecodeError:
        return base64.b64encode(body).decode("ascii"), "base64"


def _decode_body(body_text: str, encoding: str) -> bytes:
    if encoding == "base64":
        return base64.b64decode(body_text)
    return body_text.encode("utf-8")


class RawStore:
    """Atomic, crash-safe reader/writer for one gzipped-JSONL file per capture unit."""

    def __init__(self, root: Path | str = DEFAULT_ROOT) -> None:
        self._root = Path(root)

    def path_for(self, repo: str, kind: str, key: int | str) -> Path:
        _validate_repo(repo)
        _validate_kind(kind)
        scope, shard, unit = _validate_key(kind, key)
        owner, name = repo.split("/")
        return self._root / f"{owner}__{name}" / scope / shard / unit / f"{kind}.jsonl.gz"

    def exists(self, repo: str, kind: str, key: int | str) -> bool:
        return self.path_for(repo, kind, key).is_file()

    def write_records(
        self, repo: str, kind: str, key: int | str, records: list[RawRecord]
    ) -> Path:
        path = self.path_for(repo, kind, key)
        token = uuid.uuid4().hex
        tmp_path = path.parent / f"{path.name}.{os.getpid()}.{token}.tmp"

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Clean up any legacy unadorned .tmp file left from earlier crashes
            (path.parent / f"{path.name}.tmp").unlink(missing_ok=True)

            lines = []
            for record in records:
                body_text, encoding = _encode_body(record.body)
                lines.append(
                    json.dumps(
                        {
                            "url": record.url,
                            "status": record.status,
                            "fetched_at": record.fetched_at,
                            "etag": record.etag,
                            "encoding": encoding,
                            "body": body_text,
                        }
                    )
                )
            lines.append(json.dumps({"_footer": True, "n": len(records)}))
            payload = ("\n".join(lines) + "\n").encode("utf-8")
            compressed = gzip.compress(payload, mtime=0)

            with open(tmp_path, "wb") as fh:
                fh.write(compressed)
                fh.flush()
                os.fsync(fh.fileno())

            os.replace(tmp_path, path)
            self._fsync_dir(path.parent)
        except OSError as exc:
            raise RawStoreWriteError(f"failed to write raw records to {path}: {exc}") from exc
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

        return path

    def read_records(self, repo: str, kind: str, key: int | str) -> list[RawRecord]:
        path = self.path_for(repo, kind, key)
        try:
            raw = path.read_bytes()
            payload = gzip.decompress(raw)
        except FileNotFoundError:
            raise
        except (OSError, EOFError, zlib.error) as exc:
            raise TruncatedRecordError(f"corrupt/truncated gzip stream: {path}") from exc

        lines = payload.decode("utf-8").splitlines()
        if not lines:
            raise TruncatedRecordError(f"missing footer (empty payload): {path}")

        try:
            footer = json.loads(lines[-1])
        except json.JSONDecodeError as exc:
            raise TruncatedRecordError(f"missing/corrupt footer: {path}") from exc

        if not isinstance(footer, dict) or footer.get("_footer") is not True:
            raise TruncatedRecordError(f"missing footer marker: {path}")

        data_lines = lines[:-1]
        if len(data_lines) != footer.get("n"):
            raise TruncatedRecordError(
                f"record count mismatch: footer says {footer.get('n')}, "
                f"found {len(data_lines)}: {path}"
            )

        records = []
        for line in data_lines:
            obj = json.loads(line)
            body = _decode_body(obj["body"], obj["encoding"])
            records.append(
                RawRecord(
                    url=obj["url"],
                    status=obj["status"],
                    fetched_at=obj["fetched_at"],
                    etag=obj.get("etag"),
                    body=body,
                )
            )
        return records

    @staticmethod
    def _fsync_dir(directory: Path) -> None:
        try:
            dir_fd = os.open(directory, os.O_RDONLY)
        except OSError as exc:
            _logger.warning("could not open directory %s for fsync: %s", directory, exc)
            return
        try:
            os.fsync(dir_fd)
        except OSError as exc:
            _logger.warning("directory fsync not supported for %s: %s", directory, exc)
        finally:
            os.close(dir_fd)
