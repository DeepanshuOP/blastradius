"""RAG layer (D-61): chunks, hybrid index, fix-history. Offline; the repository is a real git repo built in tmp_path.

The one real-model test is skipped unless the pinned weights are already on disk (it never downloads).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pytest

from src.agents.repair import index_functions
from src.rag import history
from src.rag.chunks import chunk_java, chunk_repo, chunk_source, commit_subjects
from src.rag.index import MODEL, MODEL_REVISION, Index, build, from_chunks, rrf

SAMPLE = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "sample_repo"

V1 = '''"""calc"""

def add(a, b):
    """Add two numbers."""
    return a + b


class Cart:
    def total(self, items):
        return sum(items)

    def discount(self, t, pct):
        return t - t * pct // 100


def tax(t):
    return t * 18 // 100
'''
V2 = V1.replace("return t - t * pct // 100", "return t - (t * pct) // 100")
V3 = V2.replace("return t - (t * pct) // 100", "return max(0, t - (t * pct) // 100)")
SUBJECTS = ["init calc", "fix: parenthesise discount percent", "feat: clamp discount at zero"]


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                       capture_output=True, text=True, check=True)
    return p.stdout.strip()


@pytest.fixture()
def repo(tmp_path) -> Path:
    r = tmp_path / "calc"
    r.mkdir()
    git(r, "init", "-q")
    for text, msg in zip((V1, V2, V3), SUBJECTS):
        (r / "calc.py").write_text(text, encoding="utf-8")
        git(r, "add", "calc.py")
        git(r, "commit", "-q", "-m", msg)
    return r


# ---- chunks -------------------------------------------------------------------------------------
def test_chunk_boundaries_are_exactly_the_hand_written_ones(repo) -> None:
    got = [(c.qualname, c.start, c.end) for c in chunk_repo(repo)]
    assert got == [("add", 3, 5), ("Cart.total", 9, 10), ("Cart.discount", 12, 13), ("tax", 16, 17)]
    add = chunk_repo(repo)[0]
    assert add.docstring == "Add two numbers."
    assert add.text == 'def add(a, b):\n    """Add two numbers."""\n    return a + b'
    assert add.file == "calc.py" and add.lang == "python"


def test_chunks_at_an_older_revision_come_from_that_tree(repo) -> None:
    first = git(repo, "rev-list", "--max-parents=0", "HEAD")
    old = {c.qualname: c for c in chunk_repo(repo, first)}
    assert [(c.start, c.end) for c in old.values()] == [(3, 5), (9, 10), (12, 13), (16, 17)]
    assert old["Cart.discount"].text.splitlines()[-1] == "        return t - t * pct // 100"
    assert chunk_repo(repo)[2].text.splitlines()[-1] == "        return max(0, t - (t * pct) // 100)"


def test_python_chunks_have_the_granularity_of_the_repair_agent_index() -> None:
    files = sorted(str(p.relative_to(SAMPLE)) for p in SAMPLE.rglob("*.py") if "__pycache__" not in p.parts)
    want = index_functions(SAMPLE, files)
    got = [c for f in files for c in chunk_source((SAMPLE / f).read_text(encoding="utf-8"), f)]
    assert want and [(c.file, c.qualname, c.start, c.end, c.text) for c in got] == \
        [(c.file, c.qualname, c.start, c.end, c.text) for c in want]


def test_commit_subjects_are_the_last_three_touching_the_lines(repo) -> None:
    assert commit_subjects(repo, "HEAD", "calc.py", 12, 13) == tuple(reversed(SUBJECTS))
    assert commit_subjects(repo, "HEAD", "calc.py", 3, 5) == ("init calc",)   # only the first commit touched add
    by = {c.qualname: c.commits for c in chunk_repo(repo, "HEAD", with_commits=True)}
    assert by["Cart.discount"] == tuple(reversed(SUBJECTS)) and by["tax"] == ("init calc",)


def test_java_methods_constructors_and_javadoc() -> None:
    src = ("package p;\n"            # 1
           "public class Box {\n"   # 2
           "    int n;\n"           # 3
           "    /** Makes a box. */\n"  # 4
           "    public Box(int n) {\n"  # 5
           "        this.n = n;\n"      # 6
           "    }\n"                    # 7
           "\n"                         # 8
           "    @Override\n"            # 9
           "    public String toString() {\n"  # 10
           "        return \"\" + n;\n"        # 11
           "    }\n"                           # 12
           "}\n")
    got = [(c.qualname, c.start, c.end, c.docstring) for c in chunk_java(src, "Box.java")]
    # the annotation belongs to the method node, so toString starts at its @Override (line 9)
    assert got == [("Box.Box", 5, 7, "/** Makes a box. */"), ("Box.toString", 9, 12, "")]


# ---- ranking ------------------------------------------------------------------------------------
def test_bm25_ranks_the_discount_function_first(repo) -> None:
    idx = Index(chunk_repo(repo))
    hits = idx.search("discount pct", k=5, mode="bm25")
    assert [h.qualname for h in hits][0] == "Cart.discount"
    assert {h.qualname for h in hits} == {"Cart.discount"}   # no other chunk shares a token with the query
    assert hits[0].score > 0


def test_rrf_matches_the_hand_computed_fusion() -> None:
    fused = rrf([[0, 1, 2], [2, 0, 1]], k=60)
    assert fused[0] == pytest.approx(1 / 61 + 1 / 62)
    assert fused[1] == pytest.approx(1 / 62 + 1 / 63)
    assert fused[2] == pytest.approx(1 / 63 + 1 / 61)
    assert sorted(fused, key=lambda d: -fused[d]) == [0, 2, 1]
    assert rrf([[5], []]) == {5: pytest.approx(1 / 61)}


class FixedEmbedder:
    """Returns hand-written vectors by text, so fusion math does not depend on a model."""

    name = "fixed"

    def __init__(self, table: dict[str, list[float]]) -> None:
        self.table = table

    def embed(self, texts):
        return np.array([self.table[t] for t in texts], dtype=np.float32)


def test_dense_and_hybrid_use_the_fixed_vectors(repo) -> None:
    chunks = chunk_repo(repo)                      # add, Cart.total, Cart.discount, tax
    vecs = np.array([[0, 1], [0.6, 0.8], [1, 0], [0.2, 0.98]], dtype=np.float32)
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
    idx = Index(chunks, vecs, FixedEmbedder({"discount pct": [0.0, 1.0]}))
    dense = idx.search("discount pct", k=4, mode="dense")
    # cosine with (0, 1): add 1.0, tax ~0.995, total 0.8, discount 0.0
    assert [h.qualname for h in dense] == ["add", "tax", "Cart.total", "Cart.discount"]
    hyb = idx.search("discount pct", k=4, mode="hybrid")
    # sparse ranking is [discount]; dense is [add, tax, total, discount]
    # discount = 1/61 + 1/64, add = 1/61 (dense rank 1 only), tax = 1/62, total = 1/63
    want = {"Cart.discount": 1 / 61 + 1 / 64, "add": 1 / 61, "tax": 1 / 62, "Cart.total": 1 / 63}
    assert [h.qualname for h in hyb] == ["Cart.discount", "add", "tax", "Cart.total"]
    for h in hyb:
        assert h.score == pytest.approx(want[h.qualname])


def test_restrict_to_limits_every_mode(repo) -> None:
    chunks = chunk_repo(repo)
    vecs = np.eye(4, dtype=np.float32)
    idx = Index(chunks, vecs, FixedEmbedder({"discount pct": [0.0, 0.0, 1.0, 0.0]}))
    only = {("calc.py", "add"), ("calc.py", "tax")}
    assert idx.search("discount pct", mode="bm25", restrict_to=only) == []
    assert {h.qualname for h in idx.search("discount pct", mode="dense", restrict_to=only)} == {"add", "tax"}
    assert {h.qualname for h in idx.search("discount pct", mode="hybrid", restrict_to=only)} == {"add", "tax"}
    assert idx.search("discount pct", k=1, mode="dense")[0].qualname == "Cart.discount"   # unrestricted
    with pytest.raises(ValueError):
        idx.search("x", mode="nope")


def test_build_caches_by_repo_sha_model_and_reuses_it(repo, tmp_path) -> None:
    class Counting(FixedEmbedder):
        calls = 0

        def embed(self, texts):
            Counting.calls += 1
            return np.array([[1.0, float(len(t) % 7)] for t in texts], dtype=np.float32)

    sha = git(repo, "rev-parse", "HEAD")
    rag = tmp_path / "rag"
    a = build(repo, sha, Counting({}), rag_dir=rag)
    first = Counting.calls
    assert (rag / f"calc@{sha[:12]}.fixed.npz").exists() and (rag / f"calc@{sha[:12]}.fixed.json").exists()
    b = build(repo, sha, Counting({}), rag_dir=rag)
    assert Counting.calls == first and np.array_equal(a.vectors, b.vectors)
    # the content-addressed store means an index over the same chunk texts embeds nothing new
    c = from_chunks(chunk_repo(repo), Counting({}), rag)
    assert Counting.calls == first and np.array_equal(a.vectors, c.vectors)


# ---- fix history --------------------------------------------------------------------------------
def test_history_returns_the_two_commits_that_edited_the_function(repo) -> None:
    items = history.fix_history(repo, "HEAD", "calc.py", "Cart.discount")
    assert [i.subject for i in items] == [SUBJECTS[2], SUBJECTS[1]]
    assert "-        return t - (t * pct) // 100" in items[0].hunk
    assert "+        return max(0, t - (t * pct) // 100)" in items[0].hunk
    assert "-        return t - t * pct // 100" in items[1].hunk
    assert "+        return t - (t * pct) // 100" in items[1].hunk
    assert items[0].sha == git(repo, "rev-parse", "HEAD")
    # the hunk is about this function only
    assert "tax" not in items[0].hunk and "total" not in items[0].hunk
    three = history.fix_history(repo, "HEAD", "calc.py", "Cart.discount", n=3)
    assert [i.subject for i in three] == list(reversed(SUBJECTS))


def test_history_of_a_function_edited_once_and_of_a_missing_one(repo) -> None:
    assert [i.subject for i in history.fix_history(repo, "HEAD", "calc.py", "add")] == ["init calc"]
    assert history.fix_history(repo, "HEAD", "calc.py", "nope") == []
    assert history.fix_history(repo, "HEAD", "missing.py", "add") == []
    # as of the second commit, discount had two commits (the third did not exist yet)
    second = git(repo, "rev-parse", "HEAD~1")
    assert [i.subject for i in history.fix_history(repo, second, "calc.py", "Cart.discount")] == SUBJECTS[1::-1]
    assert [i.subject for i in history.fix_history(repo, "HEAD", "calc.py", "tax")] == ["init calc"]


def test_hunks_are_capped_at_forty_lines() -> None:
    out = "\x01" + "a" * 40 + "\x02big change\n" + "diff --git a/f b/f\n--- a/f\n+++ b/f\n@@ -1,50 +1,50 @@\n" \
          + "\n".join(f"+line {i}" for i in range(60)) + "\n"
    (item,) = history.parse_log_l(out)
    lines = item.hunk.splitlines()
    assert len(lines) == 40 and lines[-1].startswith("... (") and lines[0].startswith("@@")
    assert item.subject == "big change" and item.sha == "a" * 40


# ---- the real model (never downloads) -----------------------------------------------------------
_SNAP = Path("data/rag/models/models--jinaai--jina-embeddings-v2-base-code/snapshots") / MODEL_REVISION
requires_network = pytest.mark.skipif(not _SNAP.is_dir(), reason=f"pinned weights not on disk: {_SNAP}")


@requires_network
def test_real_model_embeds_deterministically() -> None:
    from src.rag.index import FastEmbedder

    m = FastEmbedder()
    a = m.embed(["def add(a, b):\n    return a + b", "def sub(a, b):\n    return a - b"])
    b = m.embed(["def add(a, b):\n    return a + b"])
    assert m.name == MODEL and a.shape == (2, 768) and np.isfinite(a).all()
    assert np.allclose(a[0], b[0], atol=1e-5)


def test_history_ignores_the_boundary_commit_of_a_shallow_clone(repo, tmp_path) -> None:
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)], check=True)
    assert (shallow / ".git" / "shallow").is_file()
    # the grafted root "adds" every line of the function; it is not an earlier change to it
    assert history.fix_history(shallow, "HEAD", "calc.py", "Cart.discount") == []
    # at depth 2 the newest commit is a real change; the second is the grafted boundary and is dropped
    deeper = tmp_path / "deeper"
    subprocess.run(["git", "clone", "-q", "--depth", "2", f"file://{repo}", str(deeper)], check=True)
    assert [i.subject for i in history.fix_history(deeper, "HEAD", "calc.py", "Cart.discount")] == [SUBJECTS[2]]
