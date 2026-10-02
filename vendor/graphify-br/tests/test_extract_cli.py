"""Tests for `graphify extract` CLI dispatch path in graphify.__main__."""
from __future__ import annotations

import os

import pytest

import graphify.__main__ as mainmod


def test_extract_exits_nonzero_when_ast_extraction_raises(
    monkeypatch, tmp_path, capsys
):
    """#2445: an AST-pass failure on a fresh build must not be presented as a
    successful empty corpus (exit 0 + 0-node graph.json)."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "main.go").write_text("package main\nfunc main() {}\n")
    out_dir = tmp_path / "out"

    import graphify.extract as extractmod

    def _ast_failed(paths, **kwargs):
        raise RuntimeError("worker pool failed")

    monkeypatch.setattr(extractmod, "extract", _ast_failed)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    monkeypatch.setattr(
        mainmod.sys,
        "argv",
        ["graphify", "extract", str(corpus), "--code-only",
         "--out", str(out_dir)],
    )

    with pytest.raises(SystemExit) as exc_info:
        mainmod.main()

    assert exc_info.value.code == 1
    assert (
        "[graphify extract] AST extraction failed: worker pool failed"
        in capsys.readouterr().err
    )
    assert not (out_dir / "graphify-out" / "graph.json").exists(), (
        "graph.json must not be written when the whole AST pass is lost"
    )


def test_stamped_manifest_files_normalizes_both_sides(tmp_path):
    """Unit test for the #1897 helper: relative (fresh) and absolute (cache-hit)
    source_file values must both match detect()'s absolute file lists; docs with
    no output are filtered; code files pass through untouched."""
    from graphify.cli import _stamped_manifest_files

    fresh_doc = tmp_path / "fresh.md"; fresh_doc.write_text("# fresh")
    cached_doc = tmp_path / "cached.md"; cached_doc.write_text("# cached")
    omitted_doc = tmp_path / "omitted.md"; omitted_doc.write_text("# omitted")
    code = tmp_path / "app.py"; code.write_text("x = 1")

    files_by_type = {
        "code": [str(code)],
        "document": [str(fresh_doc), str(cached_doc), str(omitted_doc)],
    }
    sem_result = {
        # fresh extraction: root-relative source_file
        "nodes": [{"id": "n1", "source_file": "fresh.md"}],
        # cache replay: absolute source_file (edge-only coverage counts too)
        "edges": [{"source": "a", "target": "b", "source_file": str(cached_doc)}],
    }

    out = _stamped_manifest_files(files_by_type, sem_result, tmp_path)
    assert out["code"] == [str(code)]
    assert out["document"] == [str(fresh_doc), str(cached_doc)]


def test_stamped_manifest_files_counts_hyperedge_only_docs(tmp_path):
    """#1920: a doc whose only chunk output is a hyperedge (3+ nodes sharing a
    concept) is valid output — the semantic cache persists it per source_file —
    so it must be stamped. Before the fix the stamping loop only inspected
    ``nodes``/``edges``, leaving such a doc unstamped and re-queued forever."""
    from graphify.cli import _stamped_manifest_files

    hyper_doc = tmp_path / "hyper.md"; hyper_doc.write_text("# hyper")
    omitted_doc = tmp_path / "omitted.md"; omitted_doc.write_text("# omitted")

    files_by_type = {"document": [str(hyper_doc), str(omitted_doc)]}
    sem_result = {
        "nodes": [],
        "edges": [],
        "hyperedges": [
            {"id": "h1", "label": "L", "nodes": ["a", "b", "c"],
             "relation": "participate_in", "source_file": "hyper.md"},
        ],
    }

    out = _stamped_manifest_files(files_by_type, sem_result, tmp_path)
    assert str(hyper_doc) in out["document"], (
        "a hyperedge-only doc must be stamped (#1920)"
    )
    # A doc with no output at all still stays unstamped (#933).
    assert str(omitted_doc) not in out["document"]


# --- #1894: --force and deep-mode dispatch over a warm cache -----------------


def _run_extract(monkeypatch, argv):
    monkeypatch.setattr(mainmod.sys, "argv", argv)
    try:
        mainmod.main()
    except SystemExit as exc:
        assert exc.code in (None, 0), f"unexpected exit code {exc.code}"


def test_cache_check_mode_deep_reads_deep_namespace(monkeypatch, tmp_path, capsys):
    """cache-check --mode deep consults cache/semantic-deep/; without the flag
    it keeps reading cache/semantic/ (deep entries are invisible to it)."""
    from graphify.cache import save_semantic_cache

    doc = tmp_path / "doc.md"
    doc.write_text("# Doc\n")
    save_semantic_cache([{"id": "d", "source_file": "doc.md"}], [],
                        root=tmp_path, mode="deep")
    files_from = tmp_path / "files.txt"
    files_from.write_text(str(doc) + "\n")
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)

    _run_extract(monkeypatch, ["graphify", "cache-check", str(files_from),
                               "--root", str(tmp_path)])
    assert "Cache: 0 hit, 1 miss" in capsys.readouterr().out

    _run_extract(monkeypatch, ["graphify", "cache-check", str(files_from),
                               "--root", str(tmp_path), "--mode", "deep"])
    assert "Cache: 1 hit, 0 miss" in capsys.readouterr().out


def _code_only_corpus(tmp_path):
    """A corpus with only code — no docs/papers/images."""
    (tmp_path / "auth.py").write_text(
        "def login(user):\n    return validate(user)\n\n"
        "def validate(user):\n    return True\n"
    )
    return tmp_path


def _clear_backend_keys(monkeypatch):
    """Clear every env var that detect_backend() or _get_backend_api_key() reads."""
    for key in (
        "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "MOONSHOT_API_KEY",
        # bedrock: presence of any of these is treated as a valid credential
        "AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION", "AWS_ACCESS_KEY_ID",
        # ollama: a set OLLAMA_BASE_URL triggers backend detection
        "OLLAMA_BASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_extract_codeonly_succeeds_without_api_key(monkeypatch, tmp_path):
    """A code-only corpus must run with no LLM API key.

    Regression: graphify extract validated a backend upfront and exited 1 with
    'no LLM API key found' even for a code-only corpus that never calls a model.
    The keyless AST path now runs to a written graph.json (#1122).
    """
    corpus = _code_only_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    monkeypatch.setattr(
        mainmod.sys, "argv",
        ["graphify", "extract", str(corpus), "--out", str(out_dir)],
    )

    try:
        mainmod.main()
    except SystemExit as exc:
        assert exc.code in (None, 0), f"unexpected exit code {exc.code}"

    graph = out_dir / "graphify-out" / "graph.json"
    assert graph.exists(), "code-only extract must write graph.json without a key"
    import json
    assert len(json.loads(graph.read_text()).get("nodes", [])) > 0


def test_missing_manifest_code_only_preserves_semantic_layer(monkeypatch, tmp_path):
    """#1925: `graphify extract --code-only` with a MISSING manifest.json must
    not degrade to a full scan that discards the committed semantic layer. An
    existing graph.json is a sufficient incremental baseline, so doc/paper/image
    nodes (excluded by --code-only, not deleted) are preserved; a genuinely
    deleted source is still evicted (#1909 semantics retained)."""
    import json

    corpus = tmp_path / "proj"; corpus.mkdir()
    (corpus / "keep.py").write_text("def keep():\n    return 1\n")
    (corpus / "README.md").write_text("# Notes\nCurated docs.\n")
    out_dir = tmp_path / "out"
    graphify_out = out_dir / "graphify-out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)

    def _sem_doc_count(g):
        return sum(1 for n in g["nodes"] if n.get("source_file") == "README.md")

    # 1) seed a code-only graph
    _run_extract(monkeypatch, ["graphify", "extract", str(corpus),
                               "--code-only", "--out", str(out_dir)])
    graph_path = graphify_out / "graph.json"
    graph = json.loads(graph_path.read_text())

    # 2) inject a committed semantic layer for README.md (nodes + edge + hyperedge)
    graph["nodes"].append({"id": "doc_readme_a", "label": "Concept A",
                           "source_file": "README.md", "file_type": "document"})
    graph["nodes"].append({"id": "doc_readme_b", "label": "Concept B",
                           "source_file": "README.md", "file_type": "document"})
    graph.setdefault("edges", []).append(
        {"source": "doc_readme_a", "target": "doc_readme_b",
         "relation": "relates_to", "source_file": "README.md"})
    graph.setdefault("hyperedges", []).append(
        {"id": "h1", "label": "Shared", "nodes": ["doc_readme_a", "doc_readme_b"],
         "relation": "participate_in", "source_file": "README.md"})
    graph_path.write_text(json.dumps(graph))
    (graphify_out / ".graphify_semantic_marker").write_text(
        json.dumps({"output_tokens": 1}))

    # 3) manifest goes missing (fresh clone / deliberately untracked)
    (graphify_out / "manifest.json").unlink()

    # 4) re-run the SAME code-only extract
    _run_extract(monkeypatch, ["graphify", "extract", str(corpus),
                               "--code-only", "--out", str(out_dir)])
    after = json.loads(graph_path.read_text())
    assert _sem_doc_count(after) >= 2, (
        "committed semantic doc nodes must survive a missing-manifest "
        f"--code-only rebuild (#1925); got {_sem_doc_count(after)}"
    )
    assert any(h.get("id") == "h1" for h in after.get("hyperedges", [])), (
        "committed hyperedge must survive the rebuild"
    )
    assert any("keep" in n["id"] for n in after["nodes"]), "code nodes intact"

    # 5) a genuine deletion still evicts the doc's semantic nodes
    (corpus / "README.md").unlink()
    (graphify_out / "manifest.json").unlink(missing_ok=True)
    _run_extract(monkeypatch, ["graphify", "extract", str(corpus),
                               "--code-only", "--out", str(out_dir)])
    gone = json.loads(graph_path.read_text())
    assert _sem_doc_count(gone) == 0, (
        "a genuinely deleted doc must still be evicted (#1909 semantics preserved)"
    )


def test_extract_out_keeps_project_root_clean(monkeypatch, tmp_path):
    """`extract --out DIR` routes every artifact to DIR/graphify-out/ and the
    scanned project must not grow a graphify-out/ (or anything else) beside
    its sources.

    Guards the centralized-output workflow: run from the project root with
    --out pointing outside the repo, and the repo stays byte-identical.
    """
    project = tmp_path / "project"
    project.mkdir()
    corpus = _code_only_corpus(project)
    external = tmp_path / "external-graphs"

    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    monkeypatch.chdir(corpus)  # run from the project root, like a real user
    monkeypatch.setattr(
        mainmod.sys, "argv",
        ["graphify", "extract", ".", "--out", str(external)],
    )

    try:
        mainmod.main()
    except SystemExit as exc:
        assert exc.code in (None, 0), f"unexpected exit code {exc.code}"

    out = external / "graphify-out"
    assert (out / "graph.json").exists(), "graph.json must land under --out"
    assert (out / "manifest.json").exists(), "manifest.json must land under --out"
    assert not (corpus / "graphify-out").exists(), (
        "scanned project must not grow a graphify-out/ when --out is set"
    )
    assert sorted(p.name for p in corpus.iterdir()) == ["auth.py"], (
        "no stray files may appear in the project root"
    )


def test_extract_timing_flag_emits_stage_timings(monkeypatch, tmp_path, capsys):
    """--timing prints per-stage `[graphify timing]` lines to stderr (#1490); omitting
    it prints none, so default output is unchanged. Code-only corpus => no API key."""
    code = tmp_path / "code"
    code.mkdir()
    (code / "a.py").write_text("def a():\n    return b()\ndef b():\n    return 1\n")

    # with --timing
    monkeypatch.setattr(
        mainmod.sys, "argv",
        ["graphify", "extract", str(code), "--no-cluster", "--out", str(tmp_path / "o1"), "--timing"],
    )
    with pytest.raises(SystemExit) as exc:
        mainmod.main()
    assert exc.value.code == 0
    err = capsys.readouterr().err
    assert "[graphify timing] detect:" in err
    assert "[graphify timing] total:" in err

    # without --timing => no timing lines
    monkeypatch.setattr(
        mainmod.sys, "argv",
        ["graphify", "extract", str(code), "--no-cluster", "--out", str(tmp_path / "o2")],
    )
    with pytest.raises(SystemExit) as exc2:
        mainmod.main()
    assert exc2.value.code == 0
    assert "graphify timing" not in capsys.readouterr().err


# ---------------------------------------------------------------------------
# #1909: a newly-excluded file's nodes must be pruned from graph.json on the
# next incremental extract even when the manifest never listed the file (the
# pre-#1897 state every 0.9.16 graph is in), so the manifest-diff prune set
# (`manifest - corpus`) can never see it.
# ---------------------------------------------------------------------------

def _two_file_corpus(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "x.py").write_text(
        "def secret_helper():\n    return 42\n\n"
        "def secret_caller():\n    return secret_helper()\n"
    )
    (project / "keep.py").write_text(
        "def kept():\n    return still_here()\n\n"
        "def still_here():\n    return 1\n"
    )
    return project


def _node_sources(graph_path):
    import json
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    return {n.get("source_file", "") for n in data.get("nodes", [])}


def _run_extract(monkeypatch, argv):
    monkeypatch.setattr(mainmod.sys, "argv", argv)
    try:
        mainmod.main()
    except SystemExit as exc:
        assert exc.code in (None, 0), f"unexpected exit code {exc.code}"


def test_incremental_extract_prunes_newly_excluded_file_not_in_manifest(
    monkeypatch, tmp_path
):
    """Seed a graph with nodes for x.py, drop x.py from the manifest (pre-#1897
    manifests never listed excluded/omitted files), exclude x.py via
    .graphifyignore, re-run extract: x.py's nodes must be gone even though it
    was never on the deleted list."""
    import json
    project = _two_file_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)

    _run_extract(
        monkeypatch,
        ["graphify", "extract", str(project), "--out", str(out_dir)],
    )
    graph_path = out_dir / "graphify-out" / "graph.json"
    manifest_path = out_dir / "graphify-out" / "manifest.json"
    assert any("x.py" in s for s in _node_sources(graph_path)), (
        "seed extract must produce nodes for x.py"
    )

    # Simulate the pre-#1897 manifest state: x.py was never manifest-listed,
    # so `manifest - corpus` can never flag it.
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = {k: v for k, v in manifest.items() if "x.py" not in k}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    (project / ".graphifyignore").write_text("x.py\n")
    _run_extract(
        monkeypatch,
        ["graphify", "extract", str(project), "--out", str(out_dir)],
    )

    sources = _node_sources(graph_path)
    assert not any("x.py" in s for s in sources), (
        f"newly-excluded x.py must be pruned from graph.json, still see {sources}"
    )
    assert any("keep.py" in s for s in sources), (
        "unchanged keep.py nodes must survive the incremental merge"
    )
    # x.py exists on disk, is excluded, and must not creep into the manifest.
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert not any("x.py" in k for k in manifest), (
        f"excluded x.py must not be (re)listed in the manifest: {set(manifest)}"
    )


def test_incremental_extract_prunes_excluded_file_listed_in_manifest(
    monkeypatch, tmp_path
):
    """Post-#1897 state: the excluded file IS manifest-listed. It must be
    pruned from graph.json AND dropped from the manifest (#1908), and stay
    settled on a further run."""
    import json
    project = _two_file_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)

    _run_extract(
        monkeypatch,
        ["graphify", "extract", str(project), "--out", str(out_dir)],
    )
    graph_path = out_dir / "graphify-out" / "graph.json"
    manifest_path = out_dir / "graphify-out" / "manifest.json"
    assert any("x.py" in k for k in json.loads(manifest_path.read_text()))

    (project / ".graphifyignore").write_text("x.py\n")
    _run_extract(
        monkeypatch,
        ["graphify", "extract", str(project), "--out", str(out_dir)],
    )

    sources = _node_sources(graph_path)
    assert not any("x.py" in s for s in sources)
    assert any("keep.py" in s for s in sources)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert not any("x.py" in k for k in manifest), (
        "excluded-but-alive manifest row must be pruned (#1908)"
    )

    # Steady state: a third run neither resurrects x.py nor loses keep.py.
    _run_extract(
        monkeypatch,
        ["graphify", "extract", str(project), "--out", str(out_dir)],
    )
    sources = _node_sources(graph_path)
    assert not any("x.py" in s for s in sources)
    assert any("keep.py" in s for s in sources)


def test_no_cluster_incremental_prunes_newly_excluded_file(
    monkeypatch, tmp_path, capsys
):
    """--no-cluster's exclusion-only early exit must still scrub the excluded
    file's nodes from the raw graph.json (that path never runs build_merge),
    and must not report the alive file as deleted."""
    import json
    project = _two_file_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)

    monkeypatch.setattr(
        mainmod.sys, "argv",
        ["graphify", "extract", str(project), "--no-cluster", "--out", str(out_dir)],
    )
    with pytest.raises(SystemExit) as exc:
        mainmod.main()
    assert exc.value.code == 0
    graph_path = out_dir / "graphify-out" / "graph.json"
    assert any("x.py" in s for s in _node_sources(graph_path))
    capsys.readouterr()

    (project / ".graphifyignore").write_text("x.py\n")
    with pytest.raises(SystemExit) as exc:
        mainmod.main()
    assert exc.value.code == 0
    out_text = capsys.readouterr().out
    assert "1 deleted" not in out_text, (
        "excluded-but-alive file must not be reported as deleted"
    )

    sources = _node_sources(graph_path)
    assert not any("x.py" in s for s in sources), (
        f"--no-cluster early exit must prune excluded sources, still see {sources}"
    )
    assert any("keep.py" in s for s in sources)


# ---------------------------------------------------------------------------
# #2543: a code file whose AST extraction FAILED (error result — e.g. missing
# optional extra — or extractor-present zero nodes) must not be stamped in the
# incremental manifest, or detect_incremental reports it unchanged forever and
# only `rm -rf graphify-out` recovers. The extractor is swapped through
# extract._DISPATCH so the tests run without tree-sitter-sql installed.
# ---------------------------------------------------------------------------

def _sql_failure_corpus(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "keep.py").write_text(
        "def kept():\n    return still_here()\n\n"
        "def still_here():\n    return 1\n"
    )
    (project / "schema.sql").write_text("CREATE TABLE users (id INT);\n")
    return project


def _failing_sql(path):
    # Mirrors extractors/sql.py's missing-extra result (#1745).
    return {"nodes": [], "edges": [],
            "error": "tree_sitter_sql not installed. Run: pip install tree-sitter-sql"}


def _ok_sql(path):
    return {
        "nodes": [{"id": "sql_schema_users", "label": path.name, "file_type": "code",
                   "source_file": str(path), "source_location": None}],
        "edges": [],
    }


def _manifest_row(manifest_path, name):
    import json
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key, entry in manifest.items():
        if name in key:
            return entry
    return None


def test_failed_extra_is_retried_and_recovers(monkeypatch, tmp_path, capsys):
    """Run 1 fails on schema.sql (missing extra) -> no live manifest hash;
    run 2 with the extra 'installed' re-queues it and the graph gains its
    nodes; run 3 settles at 0 re-extracted (no requeue loop)."""
    import graphify.extract as extractmod

    project = _sql_failure_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    graph_path = out_dir / "graphify-out" / "graph.json"
    manifest_path = out_dir / "graphify-out" / "manifest.json"
    argv = ["graphify", "extract", str(project), "--out", str(out_dir)]

    # Run 1: extraction of schema.sql fails.
    failing = pytest.MonkeyPatch()
    failing.setitem(extractmod._DISPATCH, ".sql", _failing_sql)
    try:
        _run_extract(monkeypatch, argv)
    finally:
        failing.undo()
    capsys.readouterr()
    assert not any("schema.sql" in s for s in _node_sources(graph_path))
    row = _manifest_row(manifest_path, "schema.sql")
    assert row is None or (not row.get("ast_hash") and not row.get("semantic_hash")), (
        f"failed schema.sql must carry no live hash in the manifest, got {row}"
    )
    assert _manifest_row(manifest_path, "keep.py")["ast_hash"] != ""

    # Run 2: the extra is now 'installed' — the file must be re-queued.
    monkeypatch.setitem(extractmod._DISPATCH, ".sql", _ok_sql)
    _run_extract(monkeypatch, argv)
    out_text = capsys.readouterr().out
    assert "1 code" in out_text, f"schema.sql must be in the changed set: {out_text}"
    assert any("schema.sql" in s for s in _node_sources(graph_path)), (
        "recovered schema.sql must contribute nodes to graph.json"
    )
    assert _manifest_row(manifest_path, "schema.sql")["ast_hash"] != "", (
        "recovered schema.sql must be stamped up-to-date"
    )

    # Run 3: steady state — nothing re-extracted, no heal/requeue loop.
    _run_extract(monkeypatch, argv)
    out_text = capsys.readouterr().out
    assert "0 re-extracted" in out_text, f"run 3 must be a no-op: {out_text}"
    assert "re-queuing" not in out_text
    assert any("schema.sql" in s for s in _node_sources(graph_path))


def test_permanent_failure_does_not_wedge(monkeypatch, tmp_path, capsys):
    """A file that keeps failing is retried on every run (exactly 1 file), the
    runs complete, and the rest of the graph stays stable — no wedge, no loop."""
    import graphify.extract as extractmod

    project = _sql_failure_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    monkeypatch.setitem(extractmod._DISPATCH, ".sql", _failing_sql)
    graph_path = out_dir / "graphify-out" / "graph.json"
    manifest_path = out_dir / "graphify-out" / "manifest.json"
    argv = ["graphify", "extract", str(project), "--out", str(out_dir)]

    _run_extract(monkeypatch, argv)  # seed (full scan)
    capsys.readouterr()

    for run in (2, 3):
        _run_extract(monkeypatch, argv)
        out_text = capsys.readouterr().out
        assert "1 code" in out_text, (
            f"run {run}: the failed file must be retried, not frozen: {out_text}"
        )
        assert "1 re-extracted" in out_text, f"run {run}: {out_text}"
        sources = _node_sources(graph_path)
        assert any("keep.py" in s for s in sources), f"run {run}: graph must stay stable"
        assert not any("schema.sql" in s for s in sources)
        row = _manifest_row(manifest_path, "schema.sql")
        assert row is None or (not row.get("ast_hash") and not row.get("semantic_hash")), (
            f"run {run}: still-failing schema.sql must never gain a live hash, got {row}"
        )


def test_success_and_unchanged_unaffected(monkeypatch, tmp_path, capsys):
    """Healthy corpus: second run re-extracts nothing and hashes stay live."""
    project = _two_file_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    manifest_path = out_dir / "graphify-out" / "manifest.json"
    argv = ["graphify", "extract", str(project), "--out", str(out_dir)]

    _run_extract(monkeypatch, argv)
    capsys.readouterr()
    _run_extract(monkeypatch, argv)
    out_text = capsys.readouterr().out
    assert "0 re-extracted" in out_text, f"warm healthy run must be a no-op: {out_text}"
    for name in ("x.py", "keep.py"):
        assert _manifest_row(manifest_path, name)["ast_hash"] != "", (
            f"{name} must keep its live stamp on a no-op run"
        )


def test_poisoned_manifest_is_healed(monkeypatch, tmp_path, capsys):
    """A manifest poisoned BEFORE the #2543 fix (live hash stamped, file absent
    from graph.json) must be re-queued and healed by the next run."""
    import json
    import graphify.extract as extractmod
    from graphify.detect import save_manifest

    project = _sql_failure_corpus(tmp_path)
    out_dir = tmp_path / "out"
    _clear_backend_keys(monkeypatch)
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)
    monkeypatch.setitem(extractmod._DISPATCH, ".sql", _ok_sql)
    graph_path = out_dir / "graphify-out" / "graph.json"
    manifest_path = out_dir / "graphify-out" / "manifest.json"
    argv = ["graphify", "extract", str(project), "--out", str(out_dir)]

    _run_extract(monkeypatch, argv)  # healthy seed: schema.sql stamped + in graph
    capsys.readouterr()
    assert any("schema.sql" in s for s in _node_sources(graph_path))

    # Poison: pre-fix state — manifest keeps the live hash while the graph has
    # no nodes for the file (the old stamping path never saw the failure).
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    graph["nodes"] = [n for n in graph["nodes"] if "schema.sql" not in n.get("source_file", "")]
    for key in ("links", "edges"):
        if key in graph:
            graph[key] = [e for e in graph[key] if "schema.sql" not in e.get("source_file", "")]
    graph_path.write_text(json.dumps(graph), encoding="utf-8")
    save_manifest(
        {"code": [str(project / "schema.sql")]},
        manifest_path=str(manifest_path), kind="both", root=project,
    )
    assert _manifest_row(manifest_path, "schema.sql")["ast_hash"] != ""

    _run_extract(monkeypatch, argv)
    out_text = capsys.readouterr().out
    assert "re-queuing 1" in out_text, (
        f"poisoned stamped file must be healed via re-queue (#2543): {out_text}"
    )
    assert any("schema.sql" in s for s in _node_sources(graph_path)), (
        "healed schema.sql must be back in graph.json"
    )


def test_cache_check_prompt_file_scopes_hits_to_that_prompt(monkeypatch, tmp_path, capsys):
    """#1939: cache-check --prompt-file only counts entries produced by that same
    extraction prompt, so an upgraded prompt reports a miss (re-extract) rather
    than replaying the older vintage."""
    from graphify.cache import save_semantic_cache

    doc = tmp_path / "doc.md"
    doc.write_text("# Doc\n")
    spec = tmp_path / "extraction-spec.md"
    spec.write_text("PROMPT V1", encoding="utf-8")
    save_semantic_cache([{"id": "d", "source_file": "doc.md"}], [],
                        root=tmp_path, prompt_file=str(spec))
    files_from = tmp_path / "files.txt"
    files_from.write_text(str(doc) + "\n")
    monkeypatch.setattr(mainmod, "_check_skill_version", lambda _: None)

    base = ["graphify", "cache-check", str(files_from), "--root", str(tmp_path)]
    _run_extract(monkeypatch, base + ["--prompt-file", str(spec)])
    assert "Cache: 1 hit, 0 miss" in capsys.readouterr().out

    # An upgrade rewrites the prompt: the entry must no longer satisfy the run.
    spec.write_text("PROMPT V2 — rewritten by an upgrade", encoding="utf-8")
    os.utime(spec, ns=(0, 0))
    _run_extract(monkeypatch, base + ["--prompt-file", str(spec)])
    assert "Cache: 0 hit, 1 miss" in capsys.readouterr().out
