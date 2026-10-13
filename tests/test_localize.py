"""Graph-guided localisation (no model): id forms, traceback frames, RRF, and a run on the real shopcart sample.

The shopcart run builds the real code graph (`src.graph.build.build_graph_at`) of the checked-in sample repository as a
git repo; the failing tests are the ones the seeded discount bug really breaks (asserted by running them).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from src.agents import localize as L
from src.agents.repair import index_functions
from src.eval.seeded.build import git

SAMPLE = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "sample_repo"
FIXED = "return subtotal - (subtotal * percent) // 100"
BUG = "return subtotal + (subtotal * percent) // 100"

# pytest --tb=short output of a failing seeded itsdangerous test, as stored in the BR-Seeded tasks
PYTEST_OUT = """def test_signer_kwargs(self, serializer, value):
>       assert serializer.loads(serializer.dumps(value)) == value

tests/test_itsdangerous/test_serializer.py:120:
_ _ _ _
src/itsdangerous/serializer.py:254: in loads
    return self.load_payload(s.unsign(s))
src/itsdangerous/signer.py:251: in unsign
    if self.verify_signature(value, sig):
E   itsdangerous.exc.BadSignature: Signature does not match

src/itsdangerous/signer.py:240: BadSignature"""


def test_test_key_both_forms() -> None:
    files = {"tests/test_itsdangerous/test_serializer.py"}
    assert L.test_key("tests/test_itsdangerous/test_serializer.py::TestS::test_x[a-b]") == \
        ("tests/test_itsdangerous/test_serializer.py", "test_x")
    assert L.test_key("tests.test_itsdangerous.test_serializer.TestSerializer::test_signer_cls[Serializer]", files) == \
        ("tests/test_itsdangerous/test_serializer.py", "test_signer_cls")


def test_frames_outermost_first() -> None:
    assert L.frames(PYTEST_OUT) == [("tests/test_itsdangerous/test_serializer.py", 120),
                                    ("src/itsdangerous/serializer.py", 254), ("src/itsdangerous/signer.py", 251),
                                    ("src/itsdangerous/signer.py", 240)]
    assert L.frames('File "/r/pkg/m.py", line 7, in f', "/r") == [("pkg/m.py", 7)]


def test_competition_ranks_share_ties() -> None:
    v = {("a", "f"): 1.0, ("b", "g"): 1.0, ("c", "h"): 3.0}
    assert L._ranks(v, False) == {("a", "f"): 1, ("b", "g"): 1, ("c", "h"): 3}
    assert L._ranks(v, True) == {("a", "f"): 2, ("b", "g"): 2, ("c", "h"): 1}


@pytest.fixture()
def bug_repo(tmp_path) -> tuple[Path, str, str]:
    repo = tmp_path / "shopcart"
    shutil.copytree(SAMPLE, repo, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    p = repo / "shopcart" / "pricing.py"
    p.write_text(p.read_text().replace(FIXED, BUG))
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "bug")
    return repo, base, git(repo, "diff", base, "HEAD")


def test_localize_on_the_shopcart_bug(bug_repo, tmp_path) -> None:
    from src.graph.build import build_graph_at, load_graph
    from src.lab import graphview

    repo, base, diff = bug_repo
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_pricing.py"],
                         cwd=repo, capture_output=True, text=True)
    failing_ids = sorted({ln.split(" ")[1] for ln in run.stdout.splitlines() if ln.startswith("FAILED ")}) or \
        ["tests/test_pricing.py::test_welcome10_takes_ten_percent"]
    assert run.returncode == 1
    failing = [{"test_id": t, "output": run.stdout} for t in failing_ids]
    st = build_graph_at("t/shopcart", git(repo, "rev-parse", "HEAD").strip(), clone_dir=repo, out_dir=tmp_path / "g")
    view = graphview.to_cytoscape(load_graph(st.graph_path))
    srcs = sorted(str(p.relative_to(repo)) for p in (repo / "shopcart").glob("*.py"))
    chunks = index_functions(repo, srcs)
    ranked = L.localize(repo, srcs, failing, diff, view, chunks)
    top = ranked[0]
    assert top.key == ("shopcart/pricing.py", "apply_discount")
    assert "diff" in top.ranks and "hops" in top.ranks and top.hops == 1 and top.reach == len(failing)
    assert top.path[0].startswith("tests_test_pricing") and top.path[-1] == top.node
    ev = L.evidence(ranked)
    assert ev["paths"][0]["hops"] == 1 and json.dumps(ev)          # JSON-serialisable for the decision log
    cov = L.graph_coverage(view, chunks, failing)
    assert cov["mapped_tests"] == len(failing) and cov["reachable_functions"] >= 1
    # deterministic: the same inputs give the same order
    assert [c.key for c in L.localize(repo, srcs, failing, diff, view, chunks)] == [c.key for c in ranked]
    assert [c.file for c in L.as_chunks(ranked, repo, 1)] == ["shopcart/pricing.py"]
