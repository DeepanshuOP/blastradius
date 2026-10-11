"""Retrieved context for repair arm R4 (exploratory, D-61): change-aware hybrid chunks, fix history, similar code.

`RagContext` is the provider `repair.RepairAgent(..., arm="R4", rag=ctx)` calls:

* `select`: the arm's <= 3 target chunks by change-aware hybrid retrieval (L5): functions the diff touches, ranked by
  reciprocal rank fusion of BM25 (the E3 tokens) and dense similarity (query = failing test ids + output).
* `extras`: for the top chunk, up to two earlier commits that modified it (`history.fix_history`, strictly the
  repository's real history up to `rev`) and up to two similar functions of the same repository (dense search on the
  top chunk's code, excluding the target chunks).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from src.agents import repair
from src.agents.repair import Chunk, FailureReport, changed_line_ranges, query_tokens
from src.rag.chunks import chunk_repo
from src.rag.history import fix_history
from src.rag.index import Embedder, from_chunks

N_SIMILAR = 2


def query_text(failing: list[dict]) -> str:
    """The dense query: failing test ids, then their output capped like the prompt's output block."""
    out = "\n".join(t.get("output", "") for t in failing)[:repair.OUTPUT_CHARS]
    return "\n".join(t["test_id"] for t in failing) + "\n" + out


class RagContext:
    """Retrieval context for one repository state."""

    def __init__(self, embedder: Embedder, rev: str = "HEAD", rag_dir: Path | None = None,
                 history: Callable[..., list] = fix_history) -> None:
        """Create the provider.

        Args:
            embedder: Dense encoder (`FastEmbedder`, or a fixed-vector stand-in in tests).
            rev: Commit whose history the fix-history lookup walks (the base of the change under repair).
            rag_dir: Vector store directory (default `data/rag`).
            history: `fix_history`-compatible callable (injectable for tests).
        """
        self.embedder, self.rev, self.rag_dir, self._history = embedder, rev, rag_dir, history
        self._index = None
        self._key: tuple | None = None

    def _idx(self, repo: Path, source_files: list[str]):
        key = (str(repo), tuple(source_files))
        if self._key != key or self._index is None:
            self._index = from_chunks(chunk_repo(repo, None, source_files), self.embedder, self.rag_dir)
            self._key = key
        return self._index

    def select(self, repo: Path, source_files: list[str], report: FailureReport,
               tie_break: Callable[[str], float] | None = None) -> list[Chunk]:
        """L5: the top <= 3 touched functions by hybrid rank (ties by file, line; `tie_break` is not used)."""
        idx = self._idx(repo, source_files)
        ranges = changed_line_ranges(report.pr_diff)
        focus: dict[tuple[str, str], int] = {}
        for c in idx.chunks:
            hit = [ln for ln in ranges.get(c.file, []) if c.start <= ln <= c.end]
            if hit:
                focus[c.key] = hit[0]
        hits = idx.search(query_text(report.failing), repair.MAX_CHUNKS, "hybrid", restrict_to=focus or None,
                          tokens=query_tokens(report.failing))
        return [Chunk(h.file, h.qualname, h.start, h.end, focus.get(h.key, h.start), h.score, h.text) for h in hits]

    def extras(self, repo: Path, chunks: list[Chunk], source_files: list[str]) -> tuple[list[str], list[Chunk]]:
        """`(history blocks, similar chunks)` for the top target chunk."""
        top = chunks[0]
        hist = [h.render() for h in self._history(repo, self.rev, top.file, top.qualname)]
        idx = self._idx(repo, source_files)
        taken = {(c.file, c.qualname) for c in chunks}
        near = idx.search(top.text, N_SIMILAR + len(taken), "dense")
        sim = [Chunk(h.file, h.qualname, h.start, h.end, h.start, h.score, h.text) for h in near
               if h.key not in taken][:N_SIMILAR]
        return hist, sim
