"""Fix-history retrieval (the RelRepair / InferFix idea, on the target repository's own git history).

For a candidate function, return up to two earlier commits that modified it, each as
`(sha, subject, the hunk on that function, at most 40 lines)`. The function's line range is taken from the
tree at `rev`, and `git log -L` follows that range back through history, so the hunk shown is the change to
that function and nothing else in the file. History is whatever the repository has before and including
`rev`: on a shallow clone it can be empty, and then nothing is returned (never invented).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.rag.chunks import chunk_source, read_file, run_git

MAX_COMMITS = 2
MAX_HUNK_LINES = 40


@dataclass(frozen=True)
class HistoryItem:
    """One earlier commit that modified a function."""

    sha: str
    subject: str
    hunk: str

    def render(self) -> str:
        """Prompt text: subject, then the hunk."""
        return f"commit {self.sha[:10]}: {self.subject}\n{self.hunk}"


def parse_log_l(out: str, max_lines: int = MAX_HUNK_LINES) -> list[HistoryItem]:
    """Parse `git log -L ... --format=%x01%H%x02%s` output into items (hunk = diff lines, header dropped)."""
    items: list[HistoryItem] = []
    for block in out.split("\x01"):
        if not block.strip():
            continue
        head, _, body = block.partition("\n")
        sha, _, subject = head.partition("\x02")
        keep = [ln for ln in body.splitlines()
                if ln.startswith(("@@", "+", "-", " ")) and not ln.startswith(("+++", "---"))]
        if len(keep) > max_lines:
            keep = keep[:max_lines - 1] + [f"... ({len(keep) - max_lines + 1} more lines)"]
        items.append(HistoryItem(sha.strip(), subject.strip(), "\n".join(keep)))
    return items


def fix_history(repo: Path, rev: str, file: str, qualname: str, n: int = MAX_COMMITS,
                max_lines: int = MAX_HUNK_LINES) -> list[HistoryItem]:
    """Up to `n` earlier commits (newest first) that changed `file::qualname`, as of `rev`.

    Args:
        repo: Repository with real history.
        rev: Commit whose tree defines the function's lines; commits reachable from it are searched.
        file: Repo-relative path.
        qualname: Qualified function name, as in `CodeChunk.qualname`.
        n: Number of commits (default 2).
        max_lines: Cap on each hunk.

    Returns:
        The items; empty when the function is not at `rev` or has no earlier history.
    """
    try:
        src = read_file(repo, file, rev)
    except RuntimeError:
        return []
    for c in chunk_source(src, file):
        if c.qualname == qualname:
            break
    else:
        return []
    out = run_git(repo, "log", "-L", f"{c.start},{c.end}:{file}", "-n", str(n), "--format=%x01%H%x02%s", rev)
    return parse_log_l(out, max_lines)[:n]
