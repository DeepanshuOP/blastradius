import json
import math
import re
import tempfile
from pathlib import Path
from graphify.build import build_from_json
from graphify.cluster import cluster
from graphify.export import to_json, to_html

FIXTURES = Path(__file__).parent / "fixtures"

def make_graph():
    return build_from_json(json.loads((FIXTURES / "extraction.json").read_text()))

def test_to_json_creates_file():
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.json"
        to_json(G, communities, str(out))
        assert out.exists()

def test_to_json_valid_json():
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.json"
        to_json(G, communities, str(out))
        data = json.loads(out.read_text())
        assert "nodes" in data
        assert "links" in data

def test_to_json_nodes_have_community():
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.json"
        to_json(G, communities, str(out))
        data = json.loads(out.read_text())
        for node in data["nodes"]:
            assert "community" in node


def test_to_json_sorts_graph_collections_across_insertion_order(tmp_path):
    import networkx as nx

    nodes = [("b", {"label": "Beta"}), ("a", {"label": "Alpha"}), ("c", {"label": "Gamma"})]
    links = [
        ("b", "c", {"relation": "uses", "_src": "b", "_tgt": "c"}),
        ("a", "b", {"relation": "calls", "_src": "a", "_tgt": "b"}),
    ]
    hyperedges = [
        {"id": "h2", "nodes": ["b", "c"]},
        {"id": "h1", "nodes": ["a", "b"]},
    ]

    def make_graph(reverse=False):
        graph = nx.Graph()
        graph.add_nodes_from(reversed(nodes) if reverse else nodes)
        graph.add_edges_from(reversed(links) if reverse else links)
        graph.graph["hyperedges"] = list(reversed(hyperedges)) if reverse else hyperedges
        return graph

    outputs = [tmp_path / "first.json", tmp_path / "second.json"]
    for output, reverse in zip(outputs, (False, True)):
        assert to_json(
            make_graph(reverse),
            {0: ["a", "b"], 1: ["c"]},
            str(output),
            built_at_commit="fixed",
        )

    assert outputs[0].read_bytes() == outputs[1].read_bytes()


def test_to_json_commit_fallback_uses_output_repo_not_cwd(tmp_path, monkeypatch):
    # Without an explicit built_at_commit, provenance must come from the repo
    # the graph is written into, not from whatever repo the shell happens to
    # be in — running `graphify extract <target>` from another repo's root
    # used to stamp the invoker's HEAD into the target's graph.json.
    import subprocess
    import networkx as nx

    def git(cwd, *args):
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
            cwd=cwd, check=True, capture_output=True,
        )

    target = tmp_path / "target"
    (target / "graphify-out").mkdir(parents=True)
    git(target, "init")
    git(target, "commit", "--allow-empty", "-m", "target")
    target_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=target, check=True,
        capture_output=True, text=True,
    ).stdout.strip()

    invoker = tmp_path / "invoker"
    invoker.mkdir()
    git(invoker, "init")
    git(invoker, "commit", "--allow-empty", "-m", "invoker")
    monkeypatch.chdir(invoker)

    G = nx.Graph()
    G.add_node("n1", label="n1")
    out = target / "graphify-out" / "graph.json"
    assert to_json(G, {0: ["n1"]}, str(out), force=True)
    assert json.loads(out.read_text())["built_at_commit"] == target_head


def test_to_html_creates_file():
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out))
        assert out.exists()

def test_to_html_contains_visjs():
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out))
        content = out.read_text()
        assert "vis-network" in content


def test_to_html_title_uses_portable_path_not_host_absolute():
    """#2598 / #433: <title> must not embed the generator host absolute path."""
    import re

    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        userish = Path(tmp) / "Users" / "mike" / "proj" / "graphify-out" / "graph.html"
        userish.parent.mkdir(parents=True)
        to_html(G, communities, str(userish))
        html = userish.read_text(encoding="utf-8")
    m = re.search(r"<title>(.*?)</title>", html)
    assert m, "expected a <title> tag"
    title = m.group(1)
    assert title.startswith("graphify - ")
    label = title[len("graphify - "):]
    assert "mike" not in label
    assert "Users" not in label
    assert not label.startswith("/")
    assert "graphify-out/graph.html" in label or label == "graph.html"


def test_html_document_title_helper_windows_and_relative():
    from graphify.exporters.html import _html_document_title

    assert _html_document_title(r"C:\Users\mike\proj\graphify-out\graph.html") == "graphify-out/graph.html"
    assert _html_document_title("/home/u/proj/graphify-out/graph.html") == "graphify-out/graph.html"
    assert _html_document_title("graphify-out/graph.html") == "graphify-out/graph.html"
    assert _html_document_title("/tmp/only/graph.html") == "graph.html"

def test_to_html_neighbor_links_have_no_inline_onclick_xss():
    """#1838: neighbor links dropped an unescaped JSON.stringify(nid) into a
    quoted inline onclick — which broke every link (the value's own quotes
    truncated the attribute) and let a node id/label containing a double-quote
    (from a document or a scraped `graphify add` URL) inject a live event handler
    into the local report (stored XSS). The template must instead carry the id in
    an escaped data attribute and dispatch via one delegated listener."""
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out))
        html = out.read_text()
    # The vulnerable inline handler is gone entirely...
    assert 'onclick="focusNode(' not in html
    assert "JSON.stringify(nid)" not in html
    # ...replaced by an escaped data attribute + a single delegated listener.
    assert 'data-nid="${esc(nid)}"' in html
    assert "closest('.neighbor-link')" in html


def test_to_html_pins_visjs_version_with_sri():
    """vis-network script tag must use a pinned versioned URL with a sha384
    Subresource Integrity hash and crossorigin=anonymous. Without this,
    a compromised CDN could ship arbitrary JavaScript into every rendered
    graph viewer. The hash was verified against the upstream file at
    https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js
    (sha384-Ux6phic9PEHJ38YtrijhkzyJ8yQlH8i/+buBR8s3mAZOJrP1gwyvAcIYl3GWtpX1).
    Bumping the vis-network version MUST update both the URL and the hash.
    """
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out))
        content = out.read_text()

    # Versioned URL — unversioned `vis-network/standalone/...` is rejected.
    assert "vis-network@9.1.6/standalone/umd/vis-network.min.js" in content
    assert "https://unpkg.com/vis-network/standalone" not in content

    # SRI integrity attribute pinning the known-good hash.
    assert 'integrity="sha384-Ux6phic9PEHJ38YtrijhkzyJ8yQlH8i/+buBR8s3mAZOJrP1gwyvAcIYl3GWtpX1"' in content

    # crossorigin="anonymous" is required for SRI on cross-origin scripts.
    assert 'crossorigin="anonymous"' in content

def test_to_html_contains_search():
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out))
        content = out.read_text()
        assert "search" in content.lower()

def test_to_html_contains_legend_with_labels():
    G = make_graph()
    communities = cluster(G)
    labels = {cid: f"Group {cid}" for cid in communities}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out), community_labels=labels)
        content = out.read_text()
        assert "Group 0" in content

def test_to_html_contains_nodes_and_edges():
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out))
        content = out.read_text()
        assert "RAW_NODES" in content
        assert "RAW_EDGES" in content


def test_to_html_member_counts_accepted():
    """to_html accepts member_counts without raising."""
    G = make_graph()
    communities = cluster(G)
    member_counts = {cid: len(members) for cid, members in communities.items()}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out), member_counts=member_counts)
        assert out.exists()


def _vis_nodes_from_html(content: str) -> list:
    """Extract the RAW_NODES JSON array embedded in the generated HTML."""
    m = re.search(r"const RAW_NODES = (\[.*?\]);", content, re.DOTALL)
    assert m, "RAW_NODES not found in HTML"
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_to_html_annotated_node_gets_learning_status_and_ring():
    """A node with an overlay entry gets learning_status + learning_stale fields,
    a status-colored ring (border), and a Lesson line in its hover title."""
    G = make_graph()
    communities = cluster(G)
    overlay = {
        "n_transformer": {"status": "preferred", "uses": 3, "score": 2.4,
                          "stale": False, "neg": 0},
    }
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out), learning_overlay=overlay)
        content = out.read_text()
    nodes = {n["id"]: n for n in _vis_nodes_from_html(content)}
    ann = nodes["n_transformer"]
    assert ann["learning_status"] == "preferred"
    assert ann["learning_stale"] is False
    assert ann["color"]["border"] == "#22c55e"  # green ring for preferred
    assert ann.get("borderWidth") == 3
    assert "Lesson: preferred source" in ann["title"]
    # An un-annotated node carries no learning fields.
    other = next(n for nid, n in nodes.items() if nid != "n_transformer")
    assert "learning_status" not in other
    assert "learning_stale" not in other


def test_to_html_contested_stale_node_gets_dashed_desaturated_ring():
    G = make_graph()
    communities = cluster(G)
    overlay = {
        "n_transformer": {"status": "contested", "uses": 2, "neg": 1,
                          "verdict": "dead end", "stale": True},
    }
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "graph.html"
        to_html(G, communities, str(out), learning_overlay=overlay)
        content = out.read_text()
    ann = {n["id"]: n for n in _vis_nodes_from_html(content)}["n_transformer"]
    assert ann["learning_status"] == "contested"
    assert ann["learning_stale"] is True
    assert ann["color"]["border"] == "#9ca3af"  # desaturated when stale
    assert ann["shapeProperties"]["borderDashes"] == [4, 4]
    assert "code changed" in ann["title"]


def test_to_html_unannotated_identical_to_pre_feature():
    """With no overlay, the HTML is byte-identical whether learning_overlay is
    omitted or passed empty — no learning fields leak into the un-annotated render."""
    G = make_graph()
    communities = cluster(G)
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a.html"
        b = Path(tmp) / "b.html"
        to_html(G, communities, str(a))
        to_html(G, communities, str(b), learning_overlay={})
        # Output path appears in the title, so compare with paths normalized out.
        ca = a.read_text().replace("a.html", "X.html")
        cb = b.read_text().replace("b.html", "X.html")
    assert ca == cb
    assert "learning_status" not in ca


# ── Issue #1409: punctuation-only Obsidian/Canvas filenames ───────────────────


# ── Existing-vault safety: graphify must not clobber user notes / .obsidian (#1506) ──


# ── Case-only-distinct labels must not collide on case-insensitive filesystems ──


# ── Issue #834: backup_if_protected ──────────────────────────────────────────

def test_backup_no_graph_json(tmp_path):
    """No graph.json → no backup."""
    from graphify.export import backup_if_protected
    assert backup_if_protected(tmp_path) is None


def test_backup_no_markers(tmp_path):
    """graph.json present but no sentinel and no curated labels → no backup."""
    from graphify.export import backup_if_protected
    (tmp_path / "graph.json").write_text('{"nodes":[],"links":[]}')
    assert backup_if_protected(tmp_path) is None


def test_backup_semantic_marker(tmp_path):
    """graph.json + .graphify_semantic_marker → backup taken."""
    from graphify.export import backup_if_protected
    (tmp_path / "graph.json").write_text('{"nodes":[],"links":[]}')
    (tmp_path / "GRAPH_REPORT.md").write_text("# Report")
    (tmp_path / ".graphify_semantic_marker").write_text('{"output_tokens": 1234}')
    result = backup_if_protected(tmp_path)
    assert result is not None
    assert result.is_dir()
    assert (result / "graph.json").exists()
    assert (result / "GRAPH_REPORT.md").exists()
    assert (result / ".graphify_semantic_marker").exists()


def test_backup_curated_labels(tmp_path):
    """graph.json + non-default label in .graphify_labels.json → backup taken."""
    import json
    from graphify.export import backup_if_protected
    (tmp_path / "graph.json").write_text('{"nodes":[],"links":[]}')
    (tmp_path / ".graphify_labels.json").write_text(json.dumps({"0": "Auth Pipeline", "1": "Community 1"}))
    result = backup_if_protected(tmp_path)
    assert result is not None


def test_backup_default_labels_only(tmp_path):
    """All-default labels → no backup (not curated)."""
    import json
    from graphify.export import backup_if_protected
    (tmp_path / "graph.json").write_text('{"nodes":[],"links":[]}')
    (tmp_path / ".graphify_labels.json").write_text(json.dumps({"0": "Community 0", "1": "Community 1"}))
    assert backup_if_protected(tmp_path) is None


def test_backup_same_day_no_accumulation(tmp_path):
    """Same content on same day returns existing backup dir without re-copying."""
    from graphify.export import backup_if_protected
    from datetime import date
    (tmp_path / "graph.json").write_text('{"nodes":[],"links":[]}')
    (tmp_path / ".graphify_semantic_marker").write_text("{}")
    b1 = backup_if_protected(tmp_path)
    b2 = backup_if_protected(tmp_path)
    assert b1 is not None and b2 is not None
    assert b1 == b2  # same dir, no _2 accumulation
    assert b1.name == date.today().isoformat()


def test_backup_same_day_changed_content(tmp_path):
    """Changed graph.json on same day overwrites the existing backup in place."""
    from graphify.export import backup_if_protected
    from datetime import date
    (tmp_path / "graph.json").write_text('{"nodes":[],"links":[]}')
    (tmp_path / ".graphify_semantic_marker").write_text("{}")
    b1 = backup_if_protected(tmp_path)
    (tmp_path / "graph.json").write_text('{"nodes":[{"id":"x"}],"links":[]}')
    b2 = backup_if_protected(tmp_path)
    assert b1 == b2  # still one folder per day
    assert (b2 / "graph.json").read_text() == '{"nodes":[{"id":"x"}],"links":[]}'


def test_backup_env_disable(tmp_path, monkeypatch):
    """GRAPHIFY_NO_BACKUP=1 disables backup entirely."""
    from graphify.export import backup_if_protected
    monkeypatch.setenv("GRAPHIFY_NO_BACKUP", "1")
    (tmp_path / "graph.json").write_text('{"nodes":[],"links":[]}')
    (tmp_path / ".graphify_semantic_marker").write_text("{}")
    assert backup_if_protected(tmp_path) is None


def _mkG(n):
    import networkx as nx
    G = nx.Graph()
    for i in range(n):
        G.add_node(f"n{i}", label=f"n{i}", community=0)
    return G


def test_to_json_refuses_shrink(tmp_path):
    """#479: refuse to silently overwrite an existing graph with fewer nodes."""
    p = tmp_path / "graph.json"
    json.dump({"nodes": [{"id": f"n{i}"} for i in range(5)]}, p.open("w"))
    assert to_json(_mkG(2), {}, str(p), force=False) is False
    assert to_json(_mkG(2), {}, str(p), force=True) is True  # force overrides


def test_to_json_fails_safe_on_corrupt_existing(tmp_path):
    """A non-empty but unparseable existing graph.json (corrupt or mid-write)
    must NOT be silently overwritten — we can't verify the new graph isn't a
    partial shrink, so fail safe (refuse) unless force is given."""
    p = tmp_path / "graph.json"
    p.write_text("{ this has content but is not valid json")
    assert to_json(_mkG(10), {}, str(p), force=False) is False
    assert to_json(_mkG(10), {}, str(p), force=True) is True


def test_to_json_proceeds_on_empty_existing(tmp_path):
    """An empty/whitespace existing file has no nodes to lose, so it is not a
    shrink risk — the write proceeds."""
    p = tmp_path / "graph.json"
    p.write_text("")
    assert to_json(_mkG(3), {}, str(p), force=False) is True
    data = json.loads(p.read_text())
    assert len(data["nodes"]) == 3


def test_to_html_handles_null_source_file_and_label(tmp_path):
    """#1775: a node with source_file=None or label=None must not crash to_html
    (synthetic/aggregate nodes legitimately carry null source_file; JSON `null`
    survives .get()'s default). Regression guard — fixed via sanitize_label's
    None-coercion + the str(source_file or "") call-site guard."""
    import networkx as nx
    G = nx.Graph()
    G.add_node("n1", label="Foo", source_file=None, community=0)
    G.add_node("n2", label=None, source_file="a.py", community=0)
    G.add_node("n3", label=None, source_file=None, community=0)
    out = tmp_path / "graph.html"
    to_html(G, {0: ["n1", "n2", "n3"]}, str(out))
    assert out.exists() and out.stat().st_size > 0


def test_existing_graph_node_count(tmp_path):
    from graphify.export import existing_graph_node_count, MALFORMED_GRAPH
    p = tmp_path / "graph.json"
    assert existing_graph_node_count(p) is None            # absent -> nothing to protect
    p.write_text("", encoding="utf-8")
    assert existing_graph_node_count(p) is None            # empty -> nothing to protect
    # Non-empty but unparseable must fail CLOSED (sentinel), matching to_json's
    # #479 guard — a corrupt/mid-write file could be hiding a complete graph.
    p.write_text("{not json", encoding="utf-8")
    assert existing_graph_node_count(p) is MALFORMED_GRAPH  # malformed -> fail closed
    p.write_text('{"nodes": "notalist"}', encoding="utf-8")
    assert existing_graph_node_count(p) is MALFORMED_GRAPH  # structurally wrong -> fail closed
    p.write_text('{"nodes": [{"id": "a"}, {"id": "b"}], "links": []}', encoding="utf-8")
    assert existing_graph_node_count(p) == 2               # valid


def test_hyperedge_perimeter_uses_convex_hull_not_member_order():
    """The hyperedge polygon must be traced in hull order. Tracing `h.nodes`
    array order self-intersects whenever the layout does not place members in
    angular order, so `fill()` paints crossed wedges instead of one region."""
    from graphify.exporters.html import _hyperedge_script
    script = _hyperedge_script("[]")
    assert "function convexHull(pts)" in script
    assert "const hull = convexHull(positions);" in script
    # the traced ring must derive from the hull, never from raw member order
    assert "const expanded = hull.map(" in script
    assert "const expanded = positions.map(" not in script


def test_hyperedge_convex_hull_js_is_geometrically_sound():
    """Execute the emitted convexHull in node: the perimeter must be simple
    (no self-intersection), convex, and contain every member point."""
    import shutil
    import subprocess
    node = shutil.which("node")
    if node is None:
        import pytest
        pytest.skip("node not available")
    from graphify.exporters.html import _hyperedge_script
    m = re.search(r"function convexHull\(pts\) \{.*?\n\}", _hyperedge_script("[]"), re.S)
    assert m, "convexHull not found in emitted script"
    harness = m.group(0) + r"""
const cross = (p,q,r) => (q.x-p.x)*(r.y-p.y) - (q.y-p.y)*(r.x-p.x);
const proper = (a,b,c,d) => {
  const s = (p,q,r) => Math.sign(cross(p,q,r));
  return s(a,b,c)*s(a,b,d) < 0 && s(c,d,a)*s(c,d,b) < 0;
};
function selfIntersects(poly){
  const n = poly.length;
  if (n < 4) return false;
  for (let i=0;i<n;i++) for (let j=i+1;j<n;j++){
    if ((i+1)%n===j || (j+1)%n===i) continue;
    if (proper(poly[i],poly[(i+1)%n],poly[j],poly[(j+1)%n])) return true;
  }
  return false;
}
let rng = 12345;
const rnd = () => (rng = (rng*1103515245+12345) & 0x7fffffff) / 0x7fffffff;
let bad = 0;
for (let t=0;t<2000;t++){
  const n = 4 + Math.floor(rnd()*4);            // real hyperedges carry 4-7 members
  const pts = Array.from({length:n}, () => ({x: rnd()*1000-500, y: rnd()*1000-500}));
  const h = convexHull(pts);
  if (selfIntersects(h)) bad++;
  for (let i=0;i<h.length;i++)                  // convex + counter-clockwise
    if (cross(h[i], h[(i+1)%h.length], h[(i+2)%h.length]) < -1e-9) bad++;
  for (const p of pts)                          // every member enclosed
    for (let i=0;i<h.length;i++)
      if (cross(h[i], h[(i+1)%h.length], p) < -1e-6) { bad++; break; }
}
// degenerate member sets must not throw or produce a crossed ring
for (const pts of [
  [{x:-2,y:0},{x:-1,y:0},{x:1,y:0},{x:2,y:0}],
  [{x:0,y:0},{x:0,y:0},{x:5,y:0},{x:0,y:5}],
  [{x:3,y:3},{x:3,y:3},{x:3,y:3},{x:3,y:3}],
  [{x:0,y:0},{x:1,y:1}],
]) {
  const h = convexHull(pts);
  if (!Array.isArray(h) || h.length < 1 || selfIntersects(h)) bad++;
  if (!h.every(p => Number.isFinite(p.x) && Number.isFinite(p.y))) bad++;
}
// the bow-tie ordering this fix exists for
if (!selfIntersects([{x:-1,y:-1},{x:1,y:1},{x:-1,y:1},{x:1,y:-1}])) bad++;
if (selfIntersects(convexHull([{x:-1,y:-1},{x:1,y:1},{x:-1,y:1},{x:1,y:-1}]))) bad++;
console.log(bad);
"""
    with tempfile.TemporaryDirectory() as tmp:
        js = Path(tmp) / "hull_check.js"
        js.write_text(harness, encoding="utf-8")
        proc = subprocess.run([node, str(js)], capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "0", f"geometry violations: {proc.stdout.strip()}"
