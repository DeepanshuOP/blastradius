"""Test-node typing and the test↔code bridge (ROADMAP §10.3, §29.6, T2.3).

Graphify types files as `code | document | paper | image | rationale`. BlastRadius
needs `test`, because the join between the graph and the CI outcomes runs through
test nodes: for every `test_id` observed in a CI run, does a graph node carry
that id? If that binding is weak, every graph feature downstream is mostly
missing data (threat T8).

Three things happen here:

1. **Classification** — every node becomes `test | source | config | build` from
   path heuristics plus AST signals (JUnit annotation references, pytest naming,
   `unittest.TestCase` bases).
2. **Binding** — each test node gets its canonical `test_id` from
   `src.parse.test_ids.normalize_test_id()`. That function is the frozen Week-1
   contract and is imported, never reimplemented; `derive_node_id()` supplies the
   lossy internal key D-25 defines for graph-side matching.
3. **Test→source edges** — the three §29.6 strategies, all emitted, each with its
   own confidence so a model can learn which to trust:

   | Strategy          | `edge_type`            | confidence          |
   |-------------------|------------------------|---------------------|
   | direct dependency | `tests`                | `EXTRACTED` @ 1.00  |
   | naming convention | `tests_by_convention`  | `INFERRED` @ 0.85   |
   | directory mirror  | `tests_by_layout`      | `INFERRED` @ 0.65   |

This registers itself as a `LanguageResolver` in Graphify's `resolver_registry`
(**D-10**), not as a fork hack: the registry exists so a pass plugs in without
editing `extract()`'s body, and keeping the pass here keeps the dependency
direction `src/graph → vendor` rather than making the vendored tree import from
this project.

Fields this module writes that `docs/SCHEMAS.md` already defines (`node_type`,
`test_id`, `edge_type`, `confidence`, `confidence_score`) use those names.
Everything it needs beyond them is graph-internal and documented in
`src/graph/README.md`.

Per D-48 no number computed here reaches `make tables`, `release/` or the paper.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from src.parse.test_ids import derive_node_id, normalize_test_id

__all__ = [
    "CONFIDENCE_SCORES",
    "NODE_TYPES",
    "BindingReport",
    "add_binding_edges",
    "bind_test_ids",
    "classify_node",
    "register_test_resolver",
    "resolve_test_nodes",
    "set_extraction_root",
    "test_resolver",
]

#: The `node_type` domain `docs/SCHEMAS.md` defines for `graph_nodes`.
NODE_TYPES = ("test", "source", "config", "build")

#: Per-strategy confidence, §29.6. `tests` is an AST fact; the other two are
#: heuristics whose precision differs, and the gap is the point.
CONFIDENCE_SCORES = {
    "tests": ("EXTRACTED", 1.0),
    "tests_by_convention": ("INFERRED", 0.85),
    "tests_by_layout": ("INFERRED", 0.65),
}

# --- path heuristics (§10.3 step 1) ---------------------------------------
_TEST_PATH_RE = re.compile(
    r"(?:^|/)src/test/(?:java|kotlin|scala|groovy)/"
    r"|(?:^|/)src/(?:integrationTest|testFixtures)/"
    r"|(?:^|/)tests?/"
    r"|(?:^|/)test_[^/]+\.py$"
    r"|_test\.py$"
    r"|(?:Test|Tests|TestCase|IT|ITCase)\.java$"
)
_BUILD_PATH_RE = re.compile(
    r"(?:^|/)(?:pom\.xml|build\.gradle(?:\.kts)?|settings\.gradle(?:\.kts)?"
    r"|pyproject\.toml|setup\.py|setup\.cfg|build\.xml|BUILD(?:\.bazel)?)$"
)
_CONFIG_PATH_RE = re.compile(
    r"(?:^|/)\.github/workflows/"
    r"|(?:^|/)(?:tox\.ini|Makefile|conftest\.py|pytest\.ini|\.travis\.yml)$"
)

# --- AST signals (§10.3 step 1) -------------------------------------------
#: JUnit / TestNG annotations whose presence on a method marks it as a test.
_TEST_ANNOTATIONS = frozenset(
    {
        "test",
        "paramterizedtest",
        "parameterizedtest",
        "repeatedtest",
        "testfactory",
        "testtemplate",
        "beforeeach",
        "beforeall",
        "aftereach",
        "afterall",
    }
)
#: Base classes that make a Java or Python class a test class.
_TEST_BASES = frozenset({"testcase", "unittest.testcase", "asynctestcase"})
#: Relations that count as a direct dependency for strategy 1.
_DIRECT_RELATIONS = frozenset({"calls", "imports", "imports_from", "references"})
#: Relations that attach a member to its owner.
_MEMBER_RELATIONS = frozenset({"contains", "method"})

#: The extraction root the resolver should relativize `source_file` against.
#: `run_language_resolvers` passes no root, and at resolver time Graphify has not
#: yet relativized paths (that happens after the registry run, extract.py §"#555"),
#: so a Python `test_id` would otherwise carry the absolute worktree path and
#: could never match a CI id. Set by `src.graph.build` around each extraction;
#: the registry run is single-threaded in the parent process, so a module-level
#: context is sufficient and stays deterministic.
_EXTRACTION_ROOT: str | None = None


def set_extraction_root(root: "str | PurePosixPath | None") -> None:
    """Set the root `source_file` values are made relative to.

    Args:
        root: Absolute extraction root, or None to clear it.
    """
    global _EXTRACTION_ROOT
    _EXTRACTION_ROOT = str(root) if root is not None else None


def _relative(source_file: str) -> str:
    """Return `source_file` relative to the extraction root, if it is under it.

    Args:
        source_file: A node's `source_file`, absolute or already relative.

    Returns:
        The repo-relative posix path, or the input unchanged.
    """
    if not source_file:
        return ""
    path = PurePosixPath(str(source_file).replace("\\", "/"))
    if _EXTRACTION_ROOT:
        root = PurePosixPath(str(_EXTRACTION_ROOT).replace("\\", "/"))
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            pass
    return path.as_posix()


_PY_TEST_FUNC_RE = re.compile(r"^test[_A-Z0-9]")
_PY_TEST_CLASS_RE = re.compile(r"^Test[A-Z_0-9]|Test$|Tests$|TestCase$")
_JAVA_TEST_CLASS_RE = re.compile(r"(?:Test|Tests|TestCase|IT|ITCase)$")

#: `src/test/java/com/x/FooTest.java` ↔ `src/main/java/com/x/Foo.java`.
_LAYOUT_MIRRORS = (("src/test/", "src/main/"), ("src/integrationTest/", "src/main/"))
#: Suffixes a conventional test name adds to its subject's name.
_CONVENTION_SUFFIXES = ("TestCase", "Tests", "Test", "ITCase", "IT", "Spec")


def _label(record: dict) -> str:
    """Return a node's label with Graphify's decoration stripped.

    Java member labels arrive as `.add()` and Python functions as `area()`.

    Args:
        record: A node record.

    Returns:
        The bare symbol name.
    """
    return str(record.get("label") or "").strip().lstrip(".").rstrip("()")


def _is_file_node(record: dict) -> bool:
    """Return True when this node represents a whole file, not a symbol."""
    label = str(record.get("label") or "")
    return label.endswith((".java", ".py", ".kt", ".scala", ".groovy"))


def _language(source_file: str) -> str | None:
    """Return `"java"` or `"python"` for a path, else None."""
    suffix = PurePosixPath(source_file).suffix.lower()
    return {".java": "java", ".py": "python"}.get(suffix)


def classify_node(record: dict, *, is_test_symbol: bool = False) -> str | None:
    """Return the `node_type` for one node record.

    Path heuristics decide first, because a file under `src/test/java/**` is a
    test whatever its contents; AST signals (passed in as `is_test_symbol`)
    promote a symbol in an otherwise unremarkable path.

    Args:
        record: A node record with `source_file` and `label`.
        is_test_symbol: True when an AST signal marked this symbol as a test.

    Returns:
        One of `NODE_TYPES`, or None for a node this layer does not type (a
        Graphify `rationale` node, or an unresolved external symbol with no
        source file).
    """
    source_file = _relative(str(record.get("source_file") or ""))
    if record.get("file_type") == "rationale":
        return None
    if not source_file:
        # An unresolved external symbol (`org.junit.jupiter.api.Test`) belongs to
        # no file in this repo, so none of the four types describes it.
        return None
    if _BUILD_PATH_RE.search(source_file):
        return "build"
    if _CONFIG_PATH_RE.search(source_file):
        return "config"
    if is_test_symbol or _TEST_PATH_RE.search(source_file):
        return "test"
    return "source"


def _test_symbol_ids(nodes: list[dict], edges: list[dict]) -> set[str]:
    """Return the ids of nodes an AST signal marks as tests.

    The signals, per §10.3 step 1:

    * a Java method with a `references` edge to a JUnit/TestNG annotation —
      Graphify models `@Test` as a reference to the annotation symbol rather
      than as a node attribute, so that edge *is* the annotation;
    * a class whose name follows the JUnit or pytest convention, or that
      references a known test base class;
    * a Python function named `test_*`.

    Args:
        nodes: All node records.
        edges: All edge records.

    Returns:
        Node ids marked as tests, plus the members of marked classes.
    """
    by_id = {record["id"]: record for record in nodes if record.get("id")}
    marked: set[str] = set()

    annotation_ids = {
        record["id"]
        for record in nodes
        if _label(record).split(".")[-1].lower() in _TEST_ANNOTATIONS
        or _label(record).lower() in _TEST_BASES
    }
    for edge in edges:
        if edge.get("relation") not in ("references", "inherits", "extends"):
            continue
        if edge.get("target") in annotation_ids and edge.get("source") in by_id:
            marked.add(str(edge["source"]))

    for record in nodes:
        if not record.get("id") or _is_file_node(record):
            continue
        label = _label(record)
        language = _language(str(record.get("source_file") or ""))
        if language == "java" and record.get("_callable_class") and _JAVA_TEST_CLASS_RE.search(label):
            marked.add(record["id"])
        elif language == "python":
            if record.get("_callable_class") and _PY_TEST_CLASS_RE.search(label):
                marked.add(record["id"])
            elif record.get("_callable") and _PY_TEST_FUNC_RE.match(label):
                marked.add(record["id"])

    # A marked class makes its methods tests too.
    members: dict[str, list[str]] = {}
    for edge in edges:
        if edge.get("relation") in _MEMBER_RELATIONS:
            members.setdefault(str(edge.get("source")), []).append(str(edge.get("target")))
    frontier = list(marked)
    while frontier:
        current = frontier.pop()
        for child in members.get(current, []):
            if child in by_id and child not in marked and not _is_file_node(by_id[child]):
                marked.add(child)
                frontier.append(child)
    return marked


def _java_package(source_file: str) -> str:
    """Derive a Java package from a conventional source path.

    Graphify's node records carry no package, and re-parsing for one would
    duplicate work the extractor already did. The Maven/Gradle layout puts the
    package directly in the path, which is exactly what `test_file.py` relies on
    elsewhere in this project.

    Args:
        source_file: Repo-relative path to a `.java` file.

    Returns:
        The dotted package, or `""` when the path carries no recognisable root.
    """
    parts = PurePosixPath(source_file).parts
    for root in ("java", "kotlin", "scala", "groovy"):
        if root in parts:
            index = len(parts) - 1 - parts[::-1].index(root)
            return ".".join(parts[index + 1 : -1])
    return ""


def _owner_chain(
    node_id: str, parent_of: dict[str, str], by_id: dict[str, dict]
) -> list[dict]:
    """Return a node's owners, nearest first, following member edges upward."""
    chain: list[dict] = []
    seen = {node_id}
    current = parent_of.get(node_id)
    while current and current not in seen:
        seen.add(current)
        if current in by_id:
            chain.append(by_id[current])
        current = parent_of.get(current)
    return chain


def _canonical_test_id(
    record: dict, parent_of: dict[str, str], by_id: dict[str, dict]
) -> str | None:
    """Build the canonical `test_id` string for one test node.

    Assembles the §29.6 shapes — `{package}.{Class}#{method}` for Java and
    `{module_path}::{Class}::{func}` for Python — and hands the result to
    `normalize_test_id()`, which owns the frozen canonical form.

    Args:
        record: The test node.
        parent_of: `{child_id: owner_id}` from member edges.
        by_id: All nodes by id.

    Returns:
        The canonical id, or None when this node is not an individual test case
        (a test file or test class is a container, not a case).
    """
    source_file = _relative(str(record.get("source_file") or ""))
    language = _language(source_file)
    if language is None or _is_file_node(record) or record.get("_callable_class"):
        return None
    method = _label(record)
    if not method:
        return None

    owners = _owner_chain(record["id"], parent_of, by_id)
    classes = [
        _label(owner)
        for owner in owners
        if owner.get("_callable_class") and not _is_file_node(owner)
    ]

    if language == "java":
        if not classes:
            return None
        package = _java_package(source_file)
        outer = ".".join(reversed(classes))
        qualified = f"{package}.{outer}" if package else outer
        raw = f"{qualified}#{method}"
    else:
        path = PurePosixPath(source_file).as_posix()
        raw = "::".join([path, *reversed(classes), method])

    resolved = normalize_test_id(raw, lang=language)
    return resolved.canonical if resolved else None


def _convention_subjects(label: str) -> list[str]:
    """Return the subject names a conventional test name implies.

    `FooTest` → `Foo`; `TestFoo` → `Foo`; `test_bar` → `bar`.

    Args:
        label: The test class or function name.

    Returns:
        Candidate subject names, most specific first.
    """
    out: list[str] = []
    for suffix in _CONVENTION_SUFFIXES:
        if label.endswith(suffix) and len(label) > len(suffix):
            out.append(label[: -len(suffix)])
    for prefix in ("Test", "test_"):
        if label.startswith(prefix) and len(label) > len(prefix):
            out.append(label[len(prefix) :])
    return [name for name in dict.fromkeys(out) if name]


def _layout_subject_paths(source_file: str) -> list[str]:
    """Return the mirrored production paths a test path implies.

    `src/test/java/com/x/FooTest.java` → `src/main/java/com/x/Foo.java`;
    `tests/test_shapes.py` → `shapes.py`, `pkg/shapes.py` is found by stem.

    Args:
        source_file: Repo-relative test path.

    Returns:
        Candidate production paths.
    """
    candidates: list[str] = []
    for test_root, main_root in _LAYOUT_MIRRORS:
        if test_root in source_file:
            mirrored = source_file.replace(test_root, main_root, 1)
            stem = PurePosixPath(mirrored).stem
            for name in _convention_subjects(stem):
                candidates.append(
                    str(PurePosixPath(mirrored).with_name(f"{name}{PurePosixPath(mirrored).suffix}"))
                )
    return list(dict.fromkeys(candidates))


def _emit(edges: list[dict], source: str, target: str, edge_type: str, source_file: str) -> None:
    """Append one binding edge with its strategy's confidence."""
    confidence, score = CONFIDENCE_SCORES[edge_type]
    edges.append(
        {
            "source": source,
            "target": target,
            "relation": edge_type,
            "edge_type": edge_type,
            "confidence": confidence,
            "confidence_score": score,
            "weight": score,
            "source_file": source_file,
            "_origin": "ast",
        }
    )


def resolve_test_nodes(
    per_file: list[dict], all_nodes: list[dict], all_edges: list[dict]
) -> None:
    """Type every node and bind each test node to its canonical `test_id`.

    This is the `LanguageResolver.resolve` callable: it mutates `all_nodes` in
    place, matching the contract of Graphify's existing member-call resolvers.

    It deliberately adds **no edges**. The test→source edges live in
    `add_binding_edges`, which runs after assembly — see that function for why.

    Args:
        per_file: Per-file extraction results. Unused: this pass is cross-file by
            nature and reads the merged node and edge lists instead.
        all_nodes: Merged node records, mutated in place.
        all_edges: Merged edge records, read only.
    """
    by_id = {record["id"]: record for record in all_nodes if record.get("id")}
    test_symbols = _test_symbol_ids(all_nodes, all_edges)

    for record in all_nodes:
        node_type = classify_node(record, is_test_symbol=record.get("id") in test_symbols)
        if node_type is not None:
            record["node_type"] = node_type

    parent_of: dict[str, str] = {}
    for edge in all_edges:
        if edge.get("relation") in _MEMBER_RELATIONS:
            parent_of.setdefault(str(edge.get("target")), str(edge.get("source")))

    for record in all_nodes:
        if record.get("node_type") != "test":
            continue
        canonical = _canonical_test_id(record, parent_of, by_id)
        if canonical:
            record["test_id"] = canonical
            # D-25: the lossy, many-to-one internal key. Never published in
            # place of test_id; it exists so a CI id that lost its package can
            # still be matched against the graph.
            record["graph_binding_key"] = derive_node_id(canonical)


def add_binding_edges(graph) -> dict[str, int]:
    """Add the three §29.6 test→source edges to an assembled graph, in place.

    **Why this runs after assembly rather than inside the resolver.** Strategy 1
    re-expresses an existing `calls`/`imports` edge as a `tests` edge, so the two
    share a `(source, target)` pair. Graphify assembles into a `nx.DiGraph`,
    which holds one edge per pair, so emitting the `tests` edge during extraction
    *overwrote* the structural edge it was derived from — measured on the
    `minirepo` fixture, 7 of 29 edges (every `calls` edge plus `imports_from`)
    were destroyed. Graphify's own multigraph mode is upstream future work with
    no call sites (`graphify/multigraph_compat.py`), so the parallel-edge
    capacity has to come from this layer: the stored graph is a `MultiDiGraph`
    keyed by `edge_type`, which is also what `docs/SCHEMAS.md`'s
    `(src, dst, edge_type)` edge rows describe.

    Args:
        graph: An assembled `nx.MultiDiGraph` whose nodes already carry
            `node_type` from `resolve_test_nodes`.

    Returns:
        `{edge_type: count}` for the edges added.
    """
    nodes = {node: data for node, data in graph.nodes(data=True)}
    test_nodes = {
        node: data for node, data in nodes.items() if data.get("node_type") == "test"
    }
    source_nodes = {
        node: data for node, data in nodes.items() if data.get("node_type") == "source"
    }

    by_name: dict[str, list[str]] = {}
    by_path: dict[str, list[str]] = {}
    for node, data in source_nodes.items():
        source_file = str(data.get("source_file") or "")
        if not source_file:
            continue
        by_path.setdefault(source_file, []).append(node)
        label = _label(data)
        if label and not _is_file_node(data):
            by_name.setdefault(label, []).append(node)

    added: dict[str, int] = {key: 0 for key in CONFIDENCE_SCORES}

    def add(source: str, target: str, edge_type: str) -> None:
        if source == target or graph.has_edge(source, target, key=edge_type):
            return
        confidence, score = CONFIDENCE_SCORES[edge_type]
        graph.add_edge(
            source,
            target,
            key=edge_type,
            edge_type=edge_type,
            relation=edge_type,
            confidence=confidence,
            confidence_score=score,
            weight=score,
            source_file=str(nodes[source].get("source_file") or ""),
            _origin="ast",
        )
        added[edge_type] += 1

    # Strategy 1 — direct dependency, EXTRACTED. The structural edge is the
    # evidence; the `tests` edge names it as a binding so one relation answers
    # "what does this test reach".
    for source, target, data in list(graph.edges(data=True)):
        if source not in test_nodes or target not in source_nodes:
            continue
        if str(data.get("edge_type") or data.get("relation") or "") not in _DIRECT_RELATIONS:
            continue
        add(source, target, "tests")

    for node, data in sorted(test_nodes.items()):
        source_file = str(data.get("source_file") or "")
        label = _label(data)
        is_class_like = bool(data.get("_callable_class")) or _is_file_node(data)

        # Strategy 2 — naming convention, INFERRED @ 0.85. A class-shaped test
        # binds to classes and files; a test function binds to functions. Without
        # that split, `CalculatorTest` also matched `.Calculator()`, the
        # constructor, which is a member rather than the subject.
        for name in _convention_subjects(label):
            for candidate in by_name.get(name, []):
                candidate_class_like = bool(
                    source_nodes[candidate].get("_callable_class")
                ) or _is_file_node(source_nodes[candidate])
                if candidate_class_like == is_class_like:
                    add(node, candidate, "tests_by_convention")

        # Strategy 3 — directory mirroring, INFERRED @ 0.65.
        for path in _layout_subject_paths(source_file):
            for candidate in by_path.get(path, []):
                if _is_file_node(source_nodes[candidate]) or source_nodes[candidate].get(
                    "_callable_class"
                ):
                    add(node, candidate, "tests_by_layout")

    return added


def register_test_resolver() -> object:
    """Register this pass in Graphify's `resolver_registry` and return it.

    Idempotent: registering twice would run the pass twice and double the
    binding edges, so an already-registered resolver is returned unchanged.

    Returns:
        The registered `LanguageResolver`.
    """
    from graphify.resolver_registry import register, registered_resolvers

    for existing in registered_resolvers():
        if existing.name == "blastradius_test_nodes":
            return existing
    return register(test_resolver())


def test_resolver() -> object:
    """Build the `LanguageResolver` for this pass (D-10).

    Returns:
        A `LanguageResolver` gated on the corpus languages (D-03).
    """
    from graphify.resolver_registry import LanguageResolver

    return LanguageResolver(
        name="blastradius_test_nodes",
        suffixes=frozenset({".java", ".py"}),
        resolve=resolve_test_nodes,
    )


test_resolver.__test__ = False
resolve_test_nodes.__test__ = False


@dataclass(frozen=True)
class BindingReport:
    """`graph_node_binding_rate` for one (repo, graph) pair.

    This is a graph-side diagnostic reported in session records only. Per D-48
    it is **not** Gate 1.5 and it does not replace or compare against D-47's
    figure: the denominators are different populations.

    Attributes:
        repo: Repo in `owner/name` form.
        n_observed: Distinct `test_id`s observed in CI outcomes — the denominator.
        n_bound: How many of them matched a graph test node — the numerator.
        n_bound_exact: Matched on the canonical `test_id` itself.
        n_bound_lossy: Matched only through the D-25 lossy key, which is how a
            CI id that lost its package (D-39's `fqcn_incomplete`) still binds.
        n_test_nodes: Test nodes in the graph.
        n_test_nodes_with_id: Test nodes that carry a `test_id`.
        unbound_sample: Up to 20 sorted unbound `test_id`s, for inspection.
    """

    repo: str
    n_observed: int
    n_bound: int
    n_bound_exact: int
    n_bound_lossy: int
    n_test_nodes: int
    n_test_nodes_with_id: int
    unbound_sample: list[str] = field(default_factory=list)

    @property
    def rate(self) -> float:
        """Return `n_bound / n_observed`, or 0.0 when nothing was observed."""
        return self.n_bound / self.n_observed if self.n_observed else 0.0

    def as_fraction(self) -> str:
        """Return the rate as `numerator/denominator`, never as a bare percent."""
        return f"{self.n_bound}/{self.n_observed}"


def bind_test_ids(
    graph, observed_test_ids, *, repo: str, sample_size: int = 20
) -> BindingReport:
    """Measure `graph_node_binding_rate` for one graph against observed test ids.

    Two tiers, reported separately because they are not equally trustworthy:

    1. **exact** — the CI `test_id` equals a node's canonical `test_id`;
    2. **lossy** — the CI id's D-25 key is a suffix of a node's key. A Gradle
       corpus reports bare class names (`JobQueueTest#shouldCancelJob`) with no
       package, so an exact match is impossible however good the graph is; the
       suffix match is what recovers them, and it is reported apart because a
       suffix can collide.

    Args:
        graph: A graph from `src.graph.build.load_graph`.
        observed_test_ids: The `test_id`s seen in CI outcomes for this repo.
        repo: Repo in `owner/name` form.
        sample_size: How many unbound ids to keep for inspection.

    Returns:
        The `BindingReport`.
    """
    node_ids: set[str] = set()
    keys: dict[str, list[str]] = {}
    n_test_nodes = 0
    for _, data in graph.nodes(data=True):
        if data.get("node_type") != "test":
            continue
        n_test_nodes += 1
        canonical = data.get("test_id")
        if not canonical:
            continue
        node_ids.add(str(canonical))
        key = str(data.get("graph_binding_key") or derive_node_id(str(canonical)))
        keys.setdefault(key, []).append(str(canonical))

    observed = sorted({str(t) for t in observed_test_ids if t})
    exact = lossy = 0
    unbound: list[str] = []
    key_list = sorted(keys)
    for test_id in observed:
        if test_id in node_ids:
            exact += 1
            continue
        probe = derive_node_id(test_id)
        if probe and any(
            candidate == probe or candidate.endswith("_" + probe) for candidate in key_list
        ):
            lossy += 1
            continue
        unbound.append(test_id)

    return BindingReport(
        repo=repo,
        n_observed=len(observed),
        n_bound=exact + lossy,
        n_bound_exact=exact,
        n_bound_lossy=lossy,
        n_test_nodes=n_test_nodes,
        n_test_nodes_with_id=len(node_ids),
        unbound_sample=unbound[:sample_size],
    )
