"""Knowledge base for "Ask BlastRadius" (exploratory, D-61): code, BR-Bench failure history, and the repo's docs.

Three sources, one hybrid index (`src.rag.index`):

* `code`     function chunks of the repository (Step 1), tests included
* `failure`  one document per (test_id, run_id) failure in BR-Bench that has a parsed failure message: message,
             run date, repo and label class (mine / inherited / flaky where the run's base is known)
* `doc`      the repository's README and `docs/*.md`, one document per heading section

Failure documents carry the run time (`ts`), so a search can be limited to what was known strictly before a given
time (`before_ts`). No LLM, nothing outside the repository and `data/interim` is read.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.rag.chunks import CodeChunk, chunk_repo
from src.rag.index import Embedder, Index, from_chunks

SOURCES = ("code", "failure", "doc")
INTERIM = Path("data/interim")
MAX_DOC_CHARS = 1500
MESSAGE_CHARS = 600


@dataclass
class KDoc(CodeChunk):
    """One retrievable item. `file` / `qualname` are a unique name (path and section, or repo/test and run)."""

    source: str = "code"
    ts: int | None = None          # epoch seconds of the run (failure documents only)
    meta: dict = field(default_factory=dict)

    @property
    def ref(self) -> str:
        """Where a reader can find it: `file:line` for code and docs, `run <id>` for a failure."""
        if self.source == "failure":
            return f"run {self.meta['run_id']} ({self.meta['repo']}, {self.meta['date']})"
        return f"{self.file}:{self.start}" if self.source == "code" else f"{self.file}#{self.qualname}"


def _ts(value) -> int | None:
    if value is None or (isinstance(value, float) and value != value):
        return None
    s = pd.Timestamp(value)
    if s.tzinfo is None:
        s = s.tz_localize("UTC")
    return int(s.timestamp())


# ---- failure history -----------------------------------------------------------------------------
def load_failure_docs(interim: Path = INTERIM, with_labels: bool = True) -> list[KDoc]:
    """Failure documents from `data/interim`: parsed head failures that carry a message.

    The label class follows `analysis/rq3_triage.load_labels` (strict -> mine; all minus relaxed -> inherited;
    relaxed minus strict -> flaky) and is `unknown` for runs whose base outcome is not known.
    """
    p = pd.read_parquet(interim / "parsed_outcomes.parquet",
                        columns=["run_id", "test_id", "repo", "status", "failure_message", "job_id"])
    p = p[p["status"].isin(["fail", "error"]) & p["failure_message"].fillna("").str.strip().ne("")]
    g = (p.sort_values(["run_id", "test_id", "job_id"]).groupby(["run_id", "test_id", "repo"], sort=False)
         .agg(message=("failure_message", "first")).reset_index())
    inst = pd.read_parquet(interim / "instances_raw.parquet", columns=["run_id", "run_started_at"]) \
        .drop_duplicates("run_id")
    g = g.merge(inst, on="run_id", how="left")
    labels: dict[tuple[int, str], str] = {}
    if with_labels:
        o = pd.read_parquet(interim / "outcomes.parquet").drop_duplicates(["run_id", "test_id", "split"])
        piv = o.assign(v=1).pivot_table(index=["run_id", "test_id"], columns="split", values="v", fill_value=0)
        for (run, test), r in piv.iterrows():
            lab = "mine"
            if r.get("all", 0) == 1 and r.get("relaxed", 0) == 0:
                lab = "inherited"
            if r.get("relaxed", 0) == 1 and r.get("strict", 0) == 0:
                lab = "flaky"
            if r.get("strict", 0) == 1:
                lab = "mine"
            labels[(run, test)] = lab
    out: list[KDoc] = []
    for r in g.sort_values(["run_started_at", "run_id", "test_id"]).itertuples():
        ts = _ts(r.run_started_at)
        date = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts is not None else "unknown"
        label = labels.get((r.run_id, r.test_id), "unknown")
        msg = r.message[:MESSAGE_CHARS]
        out.append(KDoc(file=f"{r.repo}/{r.test_id}", qualname=f"run-{r.run_id}", start=0, end=0,
                        text=f"{r.test_id} | {r.repo} | {date} | {label}\n{msg}", lang="text", source="failure",
                        ts=ts, meta={"run_id": int(r.run_id), "test_id": r.test_id, "repo": r.repo, "date": date,
                                     "label": label, "message": msg}))
    return out


# ---- docs ----------------------------------------------------------------------------------------
_HEADING = re.compile(r"^(#{1,4})\s+(.*\S)\s*$")


def doc_sections(text: str, path: str) -> list[KDoc]:
    """Split a Markdown file at headings; sections over `MAX_DOC_CHARS` are cut into consecutive pieces."""
    secs: list[tuple[str, int, list[str]]] = []
    title, start, buf = "(top)", 1, []
    for i, ln in enumerate(text.splitlines(), 1):
        m = _HEADING.match(ln)
        if m and not ln.startswith("#!"):
            if "".join(buf).strip():
                secs.append((title, start, buf))
            title, start, buf = m.group(2), i, [ln]
        else:
            buf.append(ln)
    if "".join(buf).strip():
        secs.append((title, start, buf))
    out: list[KDoc] = []
    for title, start, lines in secs:
        body = "\n".join(lines)
        for n, off in enumerate(range(0, max(len(body), 1), MAX_DOC_CHARS)):
            piece = body[off:off + MAX_DOC_CHARS]
            if piece.strip():
                name = title if n == 0 else f"{title} (part {n + 1})"
                out.append(KDoc(path, name, start, start + piece.count("\n"), piece, lang="markdown", source="doc"))
    return out


def load_repo_docs(repo: Path) -> list[KDoc]:
    """README (any case) at the root and every `docs/*.md`, as heading sections."""
    paths = sorted(p for p in repo.iterdir() if p.is_file() and p.name.lower().startswith("readme") and p.suffix == ".md")
    docs = repo / "docs"
    if docs.is_dir():
        paths += sorted(docs.glob("*.md"))
    out: list[KDoc] = []
    for p in paths:
        out += doc_sections(p.read_text(encoding="utf-8", errors="replace"), str(p.relative_to(repo)))
    return out


def code_docs(repo: Path, rev: str | None = None, files: list[str] | None = None) -> list[KDoc]:
    """Function chunks of the repo as `KDoc`s."""
    return [KDoc(**{**c.__dict__}, source="code") for c in chunk_repo(repo, rev, files)]


# ---- the index -----------------------------------------------------------------------------------
class Knowledge:
    """A hybrid index over mixed-source documents with per-source caps and a time bound."""

    def __init__(self, docs: list[KDoc], embedder: Embedder | None = None, rag_dir: Path | None = None,
                 dense: bool = True) -> None:
        self.docs = docs
        self.index = from_chunks(list(docs), embedder, rag_dir, dense and embedder is not None)

    @property
    def has_dense(self) -> bool:
        """True when documents carry vectors (otherwise every search is BM25)."""
        return self.index.vectors is not None

    def search(self, query: str, k: int = 8, per_source: int = 4, mode: str = "hybrid",
               sources: Iterable[str] | None = None, before_ts: int | None = None,
               tokens: list[str] | None = None) -> list[KDoc]:
        """Top-`k` documents, at most `per_source` from each source.

        Args:
            query: Natural-language question or failure message.
            k: Total documents returned.
            per_source: Cap per source (so one source cannot crowd out the others).
            mode: `bm25`, `dense` or `hybrid`.
            sources: Restrict to these sources (default all).
            before_ts: Only documents whose run time is strictly earlier (documents without a time are kept).
            tokens: Pre-tokenised sparse query.
        """
        if self.index.vectors is None and mode != "bm25":
            mode = "bm25"          # no embedding model on this machine: sparse only (callers can see `has_dense`)
        want = set(sources) if sources is not None else set(SOURCES)
        keys = [d.key for d in self.docs
                if d.source in want and (before_ts is None or d.ts is None or d.ts < before_ts)]
        ranked = self.index.search(query, len(self.docs), mode, restrict_to=keys, tokens=tokens)
        out: list[KDoc] = []
        used: dict[str, int] = {}
        for h in ranked:
            if used.get(h.source, 0) >= per_source:
                continue
            used[h.source] = used.get(h.source, 0) + 1
            out.append(h)
            if len(out) == k:
                break
        return out


def with_score(doc: KDoc, score: float) -> KDoc:
    """Copy of `doc` with a score."""
    return replace(doc, score=score)
