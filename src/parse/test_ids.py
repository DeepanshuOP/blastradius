"""Test identifier normalization and canonical join key representation.

Normalization Rules & Architecture Notes:
- NFKC Unicode normalization is applied to the whole string. Casefolding (.casefold())
  is applied ONLY to the path component of a Python test identifier. Identifiers
  (package names, class names, method/function names) are NEVER casefolded, because
  Java and Python are case-sensitive; casefolding would silently merge testBar with
  testbar (or FooTest with Footest) — collisions in a join key look like successful joins,
  which is the worst failure mode available to us.
- The pytest classname ambiguity: a pytest JUnit XML classname like `tests.test_foo.TestFoo`
  is ambiguous between `tests/test_foo.py` (with class `TestFoo`) and
  `tests/test_foo/__init__.py` (or package directory). We resolve this to `.py`
  (`tests/test_foo.py`). This is a documented known limitation.
- Unparseable input returns None. The function never raises and never fabricates an
  identifier from prose or unrecognised log noise.
- TypeScript test identifiers return None per Decision D-03 (TypeScript is cut).
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

__all__ = ["TestId", "normalize_test_id", "derive_node_id"]


@dataclass(frozen=True)
class TestId:
    lang: str
    raw: str
    canonical: str
    params: str | None = None
    class_name: str | None = None
    method_name: str | None = None
    path: str | None = None

    __test__ = False



_ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
_ISO8601_PREFIX_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\s*"
)
_JAVA_IDENT_RE = re.compile(r"^[a-zA-Z_$][a-zA-Z0-9_$]*$")
_JAVA_CLASS_RE = re.compile(
    r"^[a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*)*(?:\$[a-zA-Z_$][a-zA-Z0-9_$]*)*$"
)
_PY_IDENT_RE = re.compile(r"^[a-zA-Z_]\w*$")
_XML_TESTCASE_RE = re.compile(r"<testcase\b([^>]*)/?>", re.DOTALL | re.IGNORECASE)
_XML_ATTR_RE = re.compile(r"(\w+)=[\"']([^\"']*)[\"']")


def _normalize_python_path(p: str) -> str:
    p = p.replace("\\", "/")
    p = re.sub(r"/+", "/", p)
    if p.startswith("./"):
        p = p[2:]
    return p.casefold()


def _derive_java_class_from_path(path: str) -> str | None:
    p = path.replace("\\", "/")
    p = re.sub(r"/+", "/", p)
    p = re.sub(r"^(?:.*?/)?(?:src/(?:test|main)/(?:java|groovy|kotlin)/)", "", p)
    if p.endswith((".java", ".groovy", ".kt")):
        p = p.rsplit(".", 1)[0]
    p = p.replace("/", ".")
    return p if _JAVA_CLASS_RE.match(p) else None


def _extract_params_and_method(name: str) -> tuple[str, str | None]:
    name = name.strip()
    m_bracket = re.search(r"^(.*?)(?:\((.*?)\))?\s*(\[.*?\])(?:\s+.*)?$", name)
    if m_bracket:
        base_method = m_bracket.group(1).strip()
        sig = m_bracket.group(2)
        bracket = m_bracket.group(3).strip()
        params = f"({sig.strip()}) {bracket}" if sig else bracket
        return base_method, params
    m_sig = re.search(r"^([a-zA-Z0-9_$.]+)\((.*?)\)$", name)
    if m_sig:
        base_method = m_sig.group(1).strip()
        sig = m_sig.group(2).strip()
        params = f"({sig})" if sig else None
        return base_method, params
    return name, None


def normalize_test_id(
    raw: str, lang: str | None = None, source: str | None = None
) -> TestId | None:
    """Normalize a raw test identifier or log snippet to a canonical TestId.

    Returns None if the input is unparseable, prose, unsupported (e.g. TypeScript),
    or does not contain a valid test identifier.
    """
    if not raw or not isinstance(raw, str):
        return None

    # Step 2: Apply unicodedata NFKC to the whole string. Always.
    cleaned = unicodedata.normalize("NFKC", raw)
    # Strip ANSI escapes, leading ISO-8601 timestamps, surrounding whitespace
    cleaned = _ANSI_ESCAPE_RE.sub("", cleaned)
    cleaned = _ISO8601_PREFIX_RE.sub("", cleaned)
    cleaned = cleaned.strip()

    if not cleaned:
        return None

    # Check for TypeScript - cut per D-03
    if (
        lang == "typescript"
        or cleaned.endswith((".ts", ".tsx"))
        or ".spec.ts" in cleaned
        or ".test.ts" in cleaned
    ):
        return None

    # 1. XML testcase format (<testcase classname="..." name="..."/>)
    xml_match = _XML_TESTCASE_RE.search(cleaned)
    if xml_match:
        attrs = dict(_XML_ATTR_RE.findall(xml_match.group(1)))
        classname = attrs.get("classname", "").strip()
        name = attrs.get("name", "").strip()
        file_attr = attrs.get("file", "").strip()
        if not classname and not name:
            return None

        is_python = (
            lang == "python"
            or file_attr.endswith(".py")
            or (classname.startswith("tests.") and not classname.endswith(".java"))
            or classname.endswith(".py")
        )
        if is_python:
            method_name, params = _extract_params_and_method(name)
            if not _PY_IDENT_RE.match(method_name):
                return None
            if file_attr:
                path = _normalize_python_path(file_attr)
                class_parts = classname.split(".")
                class_name = (
                    class_parts[-1]
                    if class_parts and class_parts[-1] and class_parts[-1][0].isupper()
                    else None
                )
                if class_name and not _PY_IDENT_RE.match(class_name):
                    return None
            else:
                parts = classname.split(".")
                if parts and parts[-1] and parts[-1][0].isupper():
                    class_name = parts[-1]
                    if not _PY_IDENT_RE.match(class_name):
                        return None
                    module_parts = parts[:-1]
                else:
                    class_name = None
                    module_parts = parts
                path = _normalize_python_path("/".join(module_parts) + ".py")

            canonical = (
                f"{path}::{class_name}::{method_name}"
                if class_name
                else f"{path}::{method_name}"
            )
            return TestId(
                lang="python",
                raw=raw,
                canonical=canonical,
                params=params,
                class_name=class_name,
                method_name=method_name,
                path=path,
            )
        else:
            # Java Surefire XML
            method_name, params = _extract_params_and_method(name)
            class_name = classname
            if not _JAVA_CLASS_RE.match(class_name) or not _JAVA_IDENT_RE.match(method_name):
                return None
            canonical = f"{class_name}#{method_name}"
            return TestId(
                lang="java",
                raw=raw,
                canonical=canonical,
                params=params,
                class_name=class_name,
                method_name=method_name,
                path=None,
            )

    # 2. GH Checkrun Annotation format (e.g. path="..." title="...")
    if "path=" in cleaned or "title=" in cleaned:
        path_m = re.search(r"path=[\"']([^\"']*)[\"']", cleaned)
        title_m = re.search(r"title=[\"']([^\"']*)[\"']", cleaned)
        ann_path = path_m.group(1).strip() if path_m else ""
        ann_title = title_m.group(1).strip() if title_m else ""

        if not ann_title or ann_title.lower() == "null":
            return None

        if ann_path.endswith(".py") or lang == "python":
            path = _normalize_python_path(ann_path)
            if "::" in ann_title:
                parts = ann_title.split("::")
                if len(parts) == 2:
                    class_candidate, method_candidate = parts[0].strip(), parts[1].strip()
                else:
                    return None
            elif "." in ann_title:
                parts = ann_title.split(".")
                if len(parts) == 2:
                    class_candidate, method_candidate = parts[0].strip(), parts[1].strip()
                else:
                    return None
            else:
                class_candidate, method_candidate = None, ann_title.strip()

            method_name, params = _extract_params_and_method(method_candidate)
            if not _PY_IDENT_RE.match(method_name):
                return None
            if class_candidate:
                if not _PY_IDENT_RE.match(class_candidate):
                    return None
                class_name = class_candidate
            else:
                class_name = None

            canonical = (
                f"{path}::{class_name}::{method_name}"
                if class_name
                else f"{path}::{method_name}"
            )
            return TestId(
                lang="python",
                raw=raw,
                canonical=canonical,
                params=params,
                class_name=class_name,
                method_name=method_name,
                path=path,
            )
        elif ann_path.endswith((".java", ".groovy", ".kt")) or lang == "java":
            java_class = _derive_java_class_from_path(ann_path)
            if not java_class:
                return None

            if "." in ann_title:
                parts = ann_title.split(".")
                method_candidate = parts[-1].strip()
                prefix = ".".join(parts[:-1]).strip()
                if not _JAVA_CLASS_RE.match(prefix):
                    return None
            elif "#" in ann_title:
                parts = ann_title.split("#")
                if len(parts) == 2:
                    prefix, method_candidate = parts[0].strip(), parts[1].strip()
                    if prefix and not _JAVA_CLASS_RE.match(prefix):
                        return None
                else:
                    return None
            else:
                method_candidate = ann_title.strip()

            method_name, params = _extract_params_and_method(method_candidate)
            if not _JAVA_IDENT_RE.match(method_name):
                return None

            canonical = f"{java_class}#{method_name}"
            return TestId(
                lang="java",
                raw=raw,
                canonical=canonical,
                params=params,
                class_name=java_class,
                method_name=method_name,
                path=None,
            )
        else:
            return None

    # 3. Python pytest style (contains "::")
    if "::" in cleaned:
        s = re.sub(r"^(?:FAILED|PASSED|SKIPPED|ERROR|XFAIL|XPASS)\s+", "", cleaned)
        if " - " in s:
            s = s.split(" - ", 1)[0]
        s = re.sub(r"\s*\((?:setup|call|teardown)\)$", "", s.strip())
        parts = s.split("::")
        if len(parts) >= 2:
            path_part = parts[0].strip()
            path_part = re.sub(r"^\[\d+\]\s*", "", path_part)
            path_part = re.sub(r":\d+(?::\d+)?$", "", path_part)
            path = _normalize_python_path(path_part)

            last_part = parts[-1].strip()
            method_name, params = _extract_params_and_method(last_part)

            if len(parts) == 2:
                class_name = None
            elif len(parts) == 3:
                class_name = parts[1].strip()
                if not _PY_IDENT_RE.match(class_name):
                    return None
            else:
                return None

            if not _PY_IDENT_RE.match(method_name):
                return None

            canonical = (
                f"{path}::{class_name}::{method_name}"
                if class_name
                else f"{path}::{method_name}"
            )
            return TestId(
                lang="python",
                raw=raw,
                canonical=canonical,
                params=params,
                class_name=class_name,
                method_name=method_name,
                path=path,
            )

    # 4. Gradle Console output (contains " > ")
    if " > " in cleaned:
        if cleaned.startswith("> Task :") or "Task :" in cleaned:
            return None
        parts = [p.strip() for p in cleaned.split(" > ")]
        parts = [p for p in parts if not p.startswith(":") and not p.startswith("Task :")]
        if len(parts) >= 2:
            class_part = parts[-2]
            method_raw = parts[-1]
            method_raw = re.sub(
                r"\s+(?:FAILED|PASSED|SKIPPED|STANDARD_OUT|STANDARD_ERROR|SUCCESS)$",
                "",
                method_raw,
                flags=re.IGNORECASE,
            )
            method_name, params = _extract_params_and_method(method_raw)

            if _JAVA_CLASS_RE.match(class_part) and _JAVA_IDENT_RE.match(method_name):
                canonical = f"{class_part}#{method_name}"
                return TestId(
                    lang="java",
                    raw=raw,
                    canonical=canonical,
                    params=params,
                    class_name=class_part,
                    method_name=method_name,
                    path=None,
                )

    # 5. Java Maven / Hash / Console format
    s = cleaned
    s = re.sub(r"^\[(?:ERROR|WARNING|WARN|INFO|DEBUG|TRACE|FATAL)\]\s*", "", s).strip()
    s = re.sub(r"^::error::\s*", "", s).strip()

    # Pattern A: testBar(com.example.FooTest) or testBar[0](com.example.FooTest)
    m_paren = re.search(
        r"([a-zA-Z_$][a-zA-Z0-9_$]*)(?:\[(.*?)\])?\(([a-zA-Z_$][a-zA-Z0-9_$.$]+)\)", s
    )
    if m_paren:
        method_name = m_paren.group(1)
        params = f"[{m_paren.group(2)}]" if m_paren.group(2) else None
        class_name = m_paren.group(3)
        if _JAVA_CLASS_RE.match(class_name) and _JAVA_IDENT_RE.match(method_name):
            canonical = f"{class_name}#{method_name}"
            return TestId(
                lang="java",
                raw=raw,
                canonical=canonical,
                params=params,
                class_name=class_name,
                method_name=method_name,
                path=None,
            )

    # Pattern B: Canonical Java format with "#": com.example.FooTest#testBar[0]
    if "#" in s:
        parts = s.split("#", 1)
        class_name = parts[0].strip()
        method_name, params = _extract_params_and_method(parts[1])
        if _JAVA_CLASS_RE.match(class_name) and _JAVA_IDENT_RE.match(method_name):
            canonical = f"{class_name}#{method_name}"
            return TestId(
                lang="java",
                raw=raw,
                canonical=canonical,
                params=params,
                class_name=class_name,
                method_name=method_name,
                path=None,
            )

    # Pattern C: Maven console line: com.example.FooTest.testBar:42 expected...
    s_clean = re.sub(r":\d+.*$", "", s).strip()
    token = s_clean.split()[0] if s_clean.split() else ""
    if "." in token:
        parts = token.split(".")
        if len(parts) >= 2:
            class_name = ".".join(parts[:-1])
            method_name, params = _extract_params_and_method(parts[-1])
            if _JAVA_CLASS_RE.match(class_name) and _JAVA_IDENT_RE.match(method_name):
                canonical = f"{class_name}#{method_name}"
                return TestId(
                    lang="java",
                    raw=raw,
                    canonical=canonical,
                    params=params,
                    class_name=class_name,
                    method_name=method_name,
                    path=None,
                )

    return None


def derive_node_id(test_id: str) -> str:
    r"""Derive an internal Graphify node ID from a canonical test identifier string.

    This implements Decision D-25: test_id and graph_node_id are two distinct keys.
    test_id is the canonical, lossless, case-preserving join key; graph_node_id is an
    internal, opaque, lossy key used solely to bind a test to a Graphify graph node.

    This function mirrors the normalization recipe in vendor/graphify-br/graphify/ids.py
    (`ids.normalize_id`):
      1. unicodedata.normalize("NFKC", s)
      2. unicodedata.normalize("NFKC", s.casefold())
      3. re.sub(r"[^\w]+", "_", s, flags=re.UNICODE)
      4. re.sub(r"_+", "_", s)
      5. s.strip("_")

    Note: In graphify, `make_id(*parts)` strips "_" and "." from individual parts before
    joining with "_". Because we derive from a single unified canonical `test_id` string
    rather than decomposed AST tokens, we apply the `normalize_id` transformation directly
    across the entire string. Any punctuation (such as the '.' in 'test_foo.py' or '#'
    in Java identifiers) is replaced by underscores, repeated underscores collapse, and
    edges are stripped.

    This is a LOSSY, MANY-TO-ONE derivation. It is the internal graph-binding key only;
    it MUST NEVER be written to the published dataset in place of test_id.
    Must be re-verified if vendor/graphify-br is updated.
    """
    if not isinstance(test_id, str):
        return ""
    s = unicodedata.normalize("NFKC", test_id)
    s = unicodedata.normalize("NFKC", s.casefold())
    s = re.sub(r"[^\w]+", "_", s, flags=re.UNICODE)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")

