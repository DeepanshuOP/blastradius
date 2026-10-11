"""Hybrid code index: sparse (BM25), dense (fastembed cosine) and reciprocal rank fusion (D-61).

* **sparse** reuses the E3 retriever: `src.agents.repair.bm25_scores` over `src.agents.repair._doc_tokens`
  (path tokens + code tokens), so `mode="bm25"` ranks exactly like arm R1/R2's BM25 for the same pool and query
  tokens. Nothing is reimplemented here.
* **dense** is cosine similarity between a query embedding and chunk embeddings (`jinaai/jina-embeddings-v2-base-code`,
  CPU, one thread). Chunk vectors are content-addressed in `data/rag/emb_<model>.sqlite`, so a function text is
  embedded once however many working trees contain it.
* **hybrid** is reciprocal rank fusion, `sum 1 / (60 + rank)`, over the sparse and dense rankings. The sparse ranking
  lists only chunks with a positive BM25 score (a chunk the sparse retriever did not retrieve adds nothing).

Embeddings are an encoder, not a generator; they stay out of E1, E2 and `make tables`.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Protocol, Sequence

import numpy as np

from src.agents.repair import _doc_tokens, bm25_scores
from src.rag.chunks import CodeChunk, chunk_repo

MODEL = "jinaai/jina-embeddings-v2-base-code"
MODEL_REVISION = "516f4baf13dec4ddddda8631e019b5737c8bc250"   # Hugging Face snapshot, D-61
RRF_K = 60
RAG_DIR = Path("data/rag")
MAX_EMBED_CHARS = 2000        # a chunk's embedded text is cut here (about 500 tokens): CPU cost, stated in the report
MODES = ("bm25", "dense", "hybrid")


class Embedder(Protocol):
    """Anything that maps texts to a `(n, d)` float array."""

    name: str

    def embed(self, texts: Sequence[str]) -> np.ndarray: ...


def model_slug(model: str) -> str:
    """Filesystem-safe model name."""
    return "".join(c if c.isalnum() or c in "-._" else "_" for c in model)


class FastEmbedder:
    """The pinned fastembed model, CPU, one thread, weights under `data/rag/models/`.

    Raises:
        RuntimeError: If a snapshot other than the pinned revision is what is on disk.
    """

    def __init__(self, model: str = MODEL, cache_dir: Path | None = None) -> None:
        from fastembed import TextEmbedding

        self.name = model
        cache = Path(cache_dir or RAG_DIR / "models")
        snaps = cache / f"models--{model.replace('/', '--')}" / "snapshots"
        have = sorted(p.name for p in snaps.iterdir()) if snaps.is_dir() else []
        if model == MODEL and have and MODEL_REVISION not in have:
            raise RuntimeError(f"{model}: snapshot {have} is not the pinned revision {MODEL_REVISION} (D-61)")
        kw = {"local_files_only": True} if have else {}
        self._m = TextEmbedding(model, cache_dir=str(cache), threads=1, **kw)

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        """Float32 matrix, one row per text."""
        return np.asarray(list(self._m.embed(list(texts), batch_size=8)), dtype=np.float32)


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1.0, n)


class VectorStore:
    """Content-addressed chunk embeddings in SQLite: `sha256(text) -> float32 vector`."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.execute("CREATE TABLE IF NOT EXISTS v (h TEXT PRIMARY KEY, d INTEGER, b BLOB)")

    def vectors(self, texts: Sequence[str], embedder: Embedder) -> np.ndarray:
        """Unit vectors for `texts`, embedding only the ones not stored yet."""
        hs = [hashlib.sha256(t.encode("utf-8")).hexdigest() for t in texts]
        have: dict[str, np.ndarray] = {}
        for i in range(0, len(hs), 500):
            part = hs[i:i + 500]
            q = ",".join("?" * len(part))
            for h, _d, b in self.db.execute(f"SELECT h, d, b FROM v WHERE h IN ({q})", part):
                have[h] = np.frombuffer(b, dtype=np.float32)
        # shortest first: a batch is padded to its longest text, so length-sorted batches waste far less CPU
        todo = sorted({h: t for h, t in zip(hs, texts) if h not in have}.items(), key=lambda r: (len(r[1]), r[0]))
        if todo:
            vecs = _unit(embedder.embed([t for _, t in todo]))
            with self.db:
                self.db.executemany("INSERT OR REPLACE INTO v VALUES (?,?,?)",
                                    [(h, int(v.shape[0]), v.astype(np.float32).tobytes()) for (h, _), v in zip(todo, vecs)])
            for (h, _), v in zip(todo, vecs):
                have[h] = v.astype(np.float32)
        return np.stack([have[h] for h in hs]) if hs else np.zeros((0, 0), dtype=np.float32)


# ---- fusion -------------------------------------------------------------------------------------
def rrf(rankings: Iterable[Sequence[int]], k: int = RRF_K) -> dict[int, float]:
    """Reciprocal rank fusion: `score[d] = sum over rankings of 1 / (k + rank)`, rank starting at 1."""
    score: dict[int, float] = {}
    for ranking in rankings:
        for r, d in enumerate(ranking, 1):
            score[d] = score.get(d, 0.0) + 1.0 / (k + r)
    return score


class Index:
    """Chunks plus (optionally) their vectors; `search` ranks them."""

    def __init__(self, chunks: list[CodeChunk], vectors: np.ndarray | None = None,
                 embedder: Embedder | None = None) -> None:
        self.chunks = chunks
        self.vectors = vectors
        self.embedder = embedder
        self._pos = {c.key: i for i, c in enumerate(chunks)}
        self._tokens: list[list[str]] | None = None

    def __len__(self) -> int:
        return len(self.chunks)

    def _doc_tokens(self) -> list[list[str]]:
        if self._tokens is None:
            self._tokens = [_doc_tokens(c) for c in self.chunks]
        return self._tokens

    def pool(self, restrict_to: Iterable[tuple] | None) -> list[int]:
        """Chunk indices a search may return.

        `restrict_to` is None (all), a set of `(file, qualname)` (every chunk of that name, so typing overloads and
        re-definitions come along), or a set of `(file, qualname, start)` (exactly those chunks).
        """
        if restrict_to is None:
            return list(range(len(self.chunks)))
        want = set(restrict_to)
        if want and len(next(iter(want))) == 3:
            return [i for i, c in enumerate(self.chunks) if c.ukey in want]
        return [i for i, c in enumerate(self.chunks) if c.key in want]

    def sparse_ranking(self, tokens: list[str], pool: list[int]) -> list[tuple[int, float]]:
        """`(index, score)` of pool chunks with a positive BM25 score, best first (ties: file, start)."""
        toks = self._doc_tokens()
        scores = bm25_scores([toks[i] for i in pool], tokens)
        rows = [(i, float(s)) for i, s in zip(pool, scores) if s > 0]
        return sorted(rows, key=lambda r: (-round(r[1], 9), self.chunks[r[0]].file, self.chunks[r[0]].start))

    def dense_ranking(self, query: str, pool: list[int]) -> list[tuple[int, float]]:
        """`(index, cosine)` of every pool chunk, best first."""
        if self.vectors is None or self.embedder is None:
            raise RuntimeError("this index has no dense vectors (build it with an embedder)")
        if not pool:
            return []
        q = _unit(self.embedder.embed([query[:MAX_EMBED_CHARS]]))[0]
        sims = self.vectors[pool] @ q
        rows = [(i, float(s)) for i, s in zip(pool, sims)]
        return sorted(rows, key=lambda r: (-round(r[1], 6), self.chunks[r[0]].file, self.chunks[r[0]].start))

    def search(self, query: str, k: int = 5, mode: str = "hybrid",
               restrict_to: Iterable[tuple] | None = None,
               tokens: list[str] | None = None) -> list[CodeChunk]:
        """Top-`k` chunks (copies carrying `score`) for `query`.

        Args:
            query: Text for the dense retriever (and for BM25 unless `tokens` is given).
            k: How many chunks to return.
            mode: `bm25`, `dense` or `hybrid` (RRF, k = 60).
            restrict_to: `(file, qualname)` pairs the result must come from, e.g. the functions a diff touches.
            tokens: Pre-tokenised sparse query (E3 passes `repair.query_tokens(failing)`, which makes `bm25`
                rank exactly like R1 / R2); default is the query run through the same tokeniser.
        """
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
        pool = self.pool(restrict_to)
        if mode != "dense":
            if tokens is None:
                from src.agents.repair import query_tokens
                tokens = query_tokens([{"test_id": "", "output": query}], output_chars=len(query))
            sparse = self.sparse_ranking(tokens, pool)
        if mode == "bm25":
            ranked = sparse
        elif mode == "dense":
            ranked = self.dense_ranking(query, pool)
        else:
            dense = self.dense_ranking(query, pool)
            fused = rrf([[i for i, _ in sparse], [i for i, _ in dense]])
            ranked = sorted(fused.items(), key=lambda r: (-round(r[1], 12), self.chunks[r[0]].file,
                                                           self.chunks[r[0]].start))
        return [replace(self.chunks[i], score=s) for i, s in ranked[:k]]


# ---- building -----------------------------------------------------------------------------------
def chunks_digest(chunks: Sequence[CodeChunk]) -> str:
    """Digest of what an index covers: file, name, range and text of every chunk."""
    h = hashlib.sha256()
    for c in chunks:
        h.update(json.dumps([c.file, c.qualname, c.start, c.end, c.text], ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def from_chunks(chunks: list[CodeChunk], embedder: Embedder | None = None, rag_dir: Path | None = None,
                dense: bool = True) -> Index:
    """An index over given chunks (e.g. a working tree with a diff applied); vectors come from the store."""
    if not dense or embedder is None:
        return Index(chunks, None, embedder)
    store = VectorStore(Path(rag_dir or RAG_DIR) / f"emb_{model_slug(embedder.name)}.sqlite")
    vec = store.vectors([c.search_text()[:MAX_EMBED_CHARS] for c in chunks], embedder)
    store.db.close()
    return Index(chunks, vec, embedder)


def build(repo: Path, sha: str, embedder: Embedder | None = None, rag_dir: Path | None = None,
          files: list[str] | None = None, with_commits: bool = False, dense: bool = True) -> Index:
    """The index of `repo` at commit `sha`, cached under `data/rag/` by (repo, sha, model).

    The cache holds the chunk list and the vector matrix; it is reused only when the digest of the chunks
    just parsed equals the stored one, so a changed file list or parser can never serve stale vectors.
    """
    rag = Path(rag_dir or RAG_DIR)
    name = Path(repo).resolve().name
    model = embedder.name if embedder is not None else "sparse"
    stem = rag / f"{name}@{sha[:12]}.{model_slug(model)}"
    chunks = chunk_repo(Path(repo), sha, files, with_commits)
    digest = chunks_digest(chunks)
    meta, npz = Path(f"{stem}.json"), Path(f"{stem}.npz")
    if dense and embedder is not None and meta.exists() and npz.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        if m.get("digest") == digest and m.get("commits") == with_commits:
            return Index(chunks, np.load(npz)["v"], embedder)
    idx = from_chunks(chunks, embedder, rag, dense)
    if idx.vectors is not None:
        rag.mkdir(parents=True, exist_ok=True)
        np.savez(npz, v=idx.vectors)
        meta.write_text(json.dumps({"repo": name, "sha": sha, "model": model, "digest": digest, "n": len(chunks),
                                    "commits": with_commits}, sort_keys=True), encoding="utf-8")
    return idx
