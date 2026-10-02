"""Tests for the incomplete-build shrink-guard on `graphify extract`.

A full build writes the graph with `to_json(..., force=True)`, which bypasses the
#479 shrink guard. When this run's extraction was incomplete, forcing the write
can silently overwrite a good complete graph with a smaller partial one. The
build now drops back to the shrink guard (force=False) on an incomplete run —
unless `--allow-partial` is passed — and exits non-zero (before writing the
manifest) if the guard refuses.

Incompleteness used to be armed here through a stubbed semantic-chunk run. The
LLM semantic pass is removed in this fork (ROADMAP §10.1 step 2, §29.4), so the
surviving driver of a silently-partial run is an under-enumerated walk: a
subtree whose scandir raises, which `detect()` records in ``walk_errors``. These
tests arm that for real with a `chmod 000` directory, so every assertion below
about ``force``, exit codes and the untouched existing graph is unchanged.
"""
from __future__ import annotations

import os

import pytest

import graphify.__main__ as mainmod

pytestmark = pytest.mark.skipif(
    not hasattr(os, "geteuid") or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="POSIX-only and non-root: needs chmod 000 to actually block scandir",
)


def _make_corpus(tmp_path, *, incomplete: bool):
    """A one-code-file corpus. When ``incomplete``, a locked subdirectory makes
    the walk under-enumerate, which is what detect() reports as a walk error."""
    (tmp_path / "main.py").write_text("def main():\n    return 1\n")
    if incomplete:
        locked = tmp_path / "locked"
        locked.mkdir()
        (locked / "hidden.py").write_text("def hidden():\n    return 2\n")
        os.chmod(locked, 0o000)
    return tmp_path


@pytest.fixture(autouse=True)
def _unlock_after(tmp_path):
    """Restore the locked directory so pytest can clean tmp_path up."""
    yield
    locked = tmp_path / "locked"
    if locked.exists():
        os.chmod(locked, 0o755)


def _seed_to_json_recorder(monkeypatch, *, returns=True):
    """Patch export.to_json to record the ``force`` it was called with and return
    a fixed bool (True = wrote, False = shrink guard refused)."""
    rec = {"called": False, "force": None}

    def _stub(G, communities, output_path, *, force=False, **kwargs):
        rec["called"] = True
        rec["force"] = force
        return returns

    monkeypatch.setattr("graphify.export.to_json", _stub)
    return rec


def _stub_one_node_ast(monkeypatch, corpus):
    """Deterministic single-node AST result, so the shrink comparisons below are
    exact regardless of what the real extractors make of the corpus."""
    import graphify.extract as extractmod

    def _stub(paths, **kwargs):
        return {
            "nodes": [{"id": "s1", "source_file": str(corpus / "main.py"),
                       "file_type": "code", "label": "main"}],
            "edges": [], "input_tokens": 0, "output_tokens": 0,
        }

    # The package re-exports `extract` lazily, so a dotted-string target can
    # resolve to the function rather than the module (#monkeypatch quirk);
    # patch the module object directly, as test_extract_cli.py does.
    monkeypatch.setattr(extractmod, "extract", _stub)


def _arm_extract(monkeypatch, tmp_path, *, incomplete, extra_argv=()):
    corpus = _make_corpus(tmp_path, incomplete=incomplete)
    out_dir = tmp_path / "out"
    _stub_one_node_ast(monkeypatch, corpus)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    monkeypatch.setattr(
        mainmod.sys, "argv",
        ["graphify", "extract", str(corpus), "--out", str(out_dir), *extra_argv],
    )
    return out_dir


def test_partial_extraction_refuses_to_shrink_existing_graph(monkeypatch, tmp_path, capsys):
    # 1 of 3 chunks succeeded -> incomplete; the shrink guard refuses (returns False).
    rec = _seed_to_json_recorder(monkeypatch, returns=False)
    out_dir = _arm_extract(monkeypatch, tmp_path, incomplete=True)

    with pytest.raises(SystemExit) as exc:
        mainmod.main()

    assert exc.value.code == 1
    assert rec["called"] and rec["force"] is False, "incomplete build must not force the write"
    err = capsys.readouterr().err
    assert "Refusing to overwrite" in err
    # The manifest must not be stamped for a graph we declined to write.
    assert not (out_dir / "graphify-out" / "manifest.json").exists()


def test_partial_extraction_writes_when_not_shrinking(monkeypatch, tmp_path):
    # Incomplete run, but the new graph is not smaller -> the guard permits the
    # write. force is still False (guard active), and the CLI does not exit 1.
    rec = _seed_to_json_recorder(monkeypatch, returns=True)
    _arm_extract(monkeypatch, tmp_path, incomplete=True)

    mainmod.main()  # no SystemExit

    assert rec["called"] and rec["force"] is False


def test_allow_partial_forces_write_despite_incomplete(monkeypatch, tmp_path):
    rec = _seed_to_json_recorder(monkeypatch, returns=True)
    _arm_extract(monkeypatch, tmp_path, incomplete=True,
                 extra_argv=["--allow-partial"])

    mainmod.main()

    assert rec["called"] and rec["force"] is True, "--allow-partial must restore force=True"


def test_complete_extraction_keeps_force_write(monkeypatch, tmp_path):
    # All chunks succeeded -> a complete build legitimately keeps force=True so a
    # genuine dedup/deletion shrink still overwrites.
    rec = _seed_to_json_recorder(monkeypatch, returns=True)
    _arm_extract(monkeypatch, tmp_path, incomplete=False)

    mainmod.main()

    assert rec["called"] and rec["force"] is True


def _seed_existing_graph(gout, n):
    import json
    gout.mkdir(parents=True, exist_ok=True)
    (gout / "graph.json").write_text(
        json.dumps({"nodes": [{"id": f"keep{i}", "label": f"k{i}"} for i in range(n)],
                    "links": []}),
        encoding="utf-8",
    )


def _arm_no_cluster(monkeypatch, tmp_path, *, extra_argv=()):
    corpus = _make_corpus(tmp_path, incomplete=True)
    out_dir = tmp_path / "out"
    gout = out_dir / "graphify-out"
    _seed_existing_graph(gout, 5)  # existing complete graph
    _stub_one_node_ast(monkeypatch, corpus)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    monkeypatch.setattr(
        mainmod.sys, "argv",
        ["graphify", "extract", str(corpus), "--no-cluster",
         "--out", str(out_dir), *extra_argv],
    )
    return gout / "graph.json"


def test_no_cluster_incomplete_build_refuses_to_shrink(tmp_path, monkeypatch, capsys):
    # --force: the non-incremental raw-dump path, where the shrink guard is the
    # only thing standing between a partial 1-node extraction and the existing
    # complete 5-node graph. (Incremental runs merge the existing graph forward
    # first — #2169 — so a partial run no longer shrinks there; see below.)
    import json
    graph = _arm_no_cluster(monkeypatch, tmp_path, extra_argv=["--force"])

    with pytest.raises(SystemExit) as exc:
        mainmod.main()

    assert exc.value.code == 1
    assert "Refusing to overwrite" in capsys.readouterr().err
    # The existing 5-node graph is untouched — the partial 1-node graph was refused.
    assert len(json.loads(graph.read_text())["nodes"]) == 5


def test_no_cluster_incremental_incomplete_build_carries_existing_nodes(
    tmp_path, monkeypatch
):
    """#2169: an INCREMENTAL --no-cluster run merges the existing graph forward,
    so even an incomplete extraction does not shrink the graph — the existing
    nodes are carried and this run's partial chunk is added, no guard refusal."""
    import json
    graph = _arm_no_cluster(monkeypatch, tmp_path)

    with pytest.raises(SystemExit) as exc:
        mainmod.main()

    assert exc.value.code == 0  # the raw --no-cluster path exits 0 on success
    ids = {n["id"] for n in json.loads(graph.read_text())["nodes"]}
    assert {f"keep{i}" for i in range(5)} <= ids, ids
    assert "s1" in ids, ids


def test_no_cluster_allow_partial_overwrites(tmp_path, monkeypatch):
    import json
    graph = _arm_no_cluster(
        monkeypatch, tmp_path, extra_argv=["--force", "--allow-partial"]
    )

    with pytest.raises(SystemExit) as exc:
        mainmod.main()

    assert exc.value.code == 0  # the raw --no-cluster path exits 0 on success
    assert len(json.loads(graph.read_text())["nodes"]) == 1


def test_no_cluster_incomplete_build_fails_closed_on_malformed_existing_graph(
    tmp_path, monkeypatch, capsys
):
    """A present-but-unparseable existing graph.json (corrupt or mid-write) could
    be hiding a complete graph, so an incomplete --no-cluster build must refuse
    to overwrite it — matching to_json's #479 fail-closed handling, not the
    fail-open 'proceed when we can't count' path. --force: the non-incremental
    raw-dump path (the incremental path fails even earlier, at the forward
    merge — see the test below)."""
    graph = _arm_no_cluster(monkeypatch, tmp_path, extra_argv=["--force"])
    graph.write_text("{corrupt json", encoding="utf-8")  # non-empty, unparseable

    with pytest.raises(SystemExit) as exc:
        mainmod.main()

    assert exc.value.code == 1
    assert "unparseable" in capsys.readouterr().err
    # The corrupt file is left untouched rather than clobbered by the partial build.
    assert graph.read_text() == "{corrupt json"


def test_no_cluster_incremental_malformed_existing_graph_refuses_merge(
    tmp_path, monkeypatch, capsys
):
    """#2169: an incremental --no-cluster run must hard-fail on an unparseable
    existing graph.json (build_merge's message) instead of raw-dumping this
    run's chunks over it."""
    graph = _arm_no_cluster(monkeypatch, tmp_path)
    graph.write_text("{corrupt json", encoding="utf-8")  # non-empty, unparseable

    with pytest.raises(SystemExit) as exc:
        mainmod.main()

    assert exc.value.code == 1
    assert "Cannot read" in capsys.readouterr().err
    # The corrupt file is left untouched rather than clobbered.
    assert graph.read_text() == "{corrupt json"
