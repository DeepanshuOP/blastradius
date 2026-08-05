"""Atomic raw-capture writer (T0.3a support, ROADMAP §8 / §8.3).

One gzipped JSONL file per (repo, run_id, kind) under `data/raw/`. "Capture
wide, parse narrow": this module only ever writes and reads whole raw
response envelopes — it never parses their contents.

Path scheme: `data/raw/{owner}__{repo}/{run_id % 1000:03d}/{run_id:012d}/{kind}.jsonl.gz`.
Deliberately NOT `{owner}__{repo}/{yyyy-mm}/{kind}.jsonl.gz` as originally
sketched in ROADMAP §8.3 — that shares one file across every run in a month,
which conflicts with cursor.py's contract that redoing an `in_flight` run
must overwrite safely: a shared monthly file would make "redo one run" cost
a full-month rewrite, and a crash mid-rewrite could damage other runs' data
that happen to share the file. Scoping one file to exactly one
(repo, run_id, kind) means a redo only ever touches its own bytes, and
`path_for()` is a pure function of that key alone — no timestamp in it, so
the same logical capture always resolves to the same path across redos.
"""

from __future__ import annotations

import base64
import gzip
import json
import logging
import os
import zlib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path("data/raw")

ALLOWED_KINDS = frozenset(
    {
        "pulls",
        "pull_files",
        "pull_commits",
        "runs",
        "jobs",
        "checkruns",
        "annotations",
        "artifacts",
        "logs",
    }
)

_logger = logging.getLogger(__name__)


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

    def path_for(self, repo: str, run_id: int, kind: str) -> Path:
        _validate_repo(repo)
        _validate_kind(kind)
        owner, name = repo.split("/")
        shard = f"{run_id % 1000:03d}"
        unit = f"{run_id:012d}"
        return self._root / f"{owner}__{name}" / shard / unit / f"{kind}.jsonl.gz"

    def exists(self, repo: str, run_id: int, kind: str) -> bool:
        return self.path_for(repo, run_id, kind).is_file()

    def write_records(
        self, repo: str, run_id: int, kind: str, records: list[RawRecord]
    ) -> Path:
        path = self.path_for(repo, run_id, kind)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.parent / f"{path.name}.tmp"

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

        return path

    def read_records(self, repo: str, run_id: int, kind: str) -> list[RawRecord]:
        path = self.path_for(repo, run_id, kind)
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
