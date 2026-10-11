"""Function-level chunks of a repository (Python via `ast`, Java via tree-sitter).

A chunk is one function or method with its file, qualified name, line range, text, docstring and the
subjects of the last three commits that touched those lines. Python chunks have exactly the granularity of
`src.agents.repair.index_functions` (top-level functions and class methods, decorators included), so a chunk
here and a chunk there are the same unit; a test asserts it.
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

LANGS = {".py": "python", ".java": "java"}
MAX_SUBJECTS = 3


@dataclass
class CodeChunk:
    """One function or method.

    Attributes:
        file: Repo-relative path.
        qualname: `Class.method` or `function` (nested classes joined with dots).
        start: First line (1-based, decorators / annotations included).
        end: Last line.
        text: The source lines `start..end`.
        docstring: Python docstring or the Javadoc immediately above (empty when absent).
        commits: Subjects of up to three commits that touched these lines, newest first (empty unless requested).
        lang: `python` or `java`.
        score: Filled by a search; 0.0 otherwise.
        focus: Unused by the index; present so a chunk can be handed to `repair.render_chunk`.
    """

    file: str
    qualname: str
    start: int
    end: int
    text: str
    docstring: str = ""
    commits: tuple[str, ...] = ()
    lang: str = "python"
    score: float = 0.0
    focus: int = field(default=0)

    def __post_init__(self) -> None:
        if not self.focus:
            self.focus = self.start

    @property
    def key(self) -> tuple[str, str]:
        """`(file, qualname)`: how a chunk is named in `restrict_to` (overloads and re-definitions share one)."""
        return (self.file, self.qualname)

    @property
    def ukey(self) -> tuple[str, str, int]:
        """`(file, qualname, start)`: unique per chunk, for a `restrict_to` that must not match a same-named sibling."""
        return (self.file, self.qualname, self.start)

    def search_text(self) -> str:
        """What the dense retriever embeds: path, name, then the code (docstring is inside the code)."""
        return f"# {self.file} :: {self.qualname}\n{self.text}"


def run_git(repo: Path, *args: str, check: bool = False) -> str:
    """Stdout of `git -C repo ...` ("" on failure unless `check`)."""
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, errors="replace")
    if p.returncode != 0:
        if check:
            raise RuntimeError(f"git {' '.join(args)}: {p.stderr[:300]}")
        return ""
    return p.stdout


# ---- parsing -----------------------------------------------------------------------------------
def chunk_python(src: str, path: str) -> list[CodeChunk]:
    """Functions and methods of one Python source (empty on a syntax error)."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return []
    lines = src.splitlines()
    out: list[CodeChunk] = []

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = min([child.lineno] + [d.lineno for d in child.decorator_list])
                out.append(CodeChunk(path, f"{prefix}{child.name}", start, child.end_lineno,
                                     "\n".join(lines[start - 1:child.end_lineno]),
                                     ast.get_docstring(child) or "", lang="python"))
            elif isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")

    visit(tree, "")
    return out


_JAVA_PARSER = None
_JAVA_TYPES = {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration"}
_JAVA_FUNCS = {"method_declaration", "constructor_declaration"}


def _java_parser():
    global _JAVA_PARSER
    if _JAVA_PARSER is None:
        import tree_sitter_java
        from tree_sitter import Language, Parser

        _JAVA_PARSER = Parser(Language(tree_sitter_java.language()))
    return _JAVA_PARSER


def chunk_java(src: str, path: str) -> list[CodeChunk]:
    """Methods and constructors of one Java source (tree-sitter, the parser Graphify uses)."""
    data = src.encode("utf-8")
    tree = _java_parser().parse(data)
    lines = src.splitlines()
    out: list[CodeChunk] = []

    def name_of(node) -> str:
        n = node.child_by_field_name("name")
        return data[n.start_byte:n.end_byte].decode("utf-8") if n is not None else "?"

    def visit(node, prefix: str) -> None:
        for child in node.children:
            if child.type in _JAVA_TYPES:
                body = child.child_by_field_name("body")
                visit(body if body is not None else child, f"{prefix}{name_of(child)}.")
            elif child.type in _JAVA_FUNCS:
                start, end = child.start_point[0] + 1, child.end_point[0] + 1
                doc = ""
                prev = child.prev_named_sibling
                if prev is not None and prev.type == "block_comment":
                    c = data[prev.start_byte:prev.end_byte].decode("utf-8")
                    if c.startswith("/**") and prev.end_point[0] + 1 >= start - 1:
                        doc = c
                out.append(CodeChunk(path, f"{prefix}{name_of(child)}", start, end, "\n".join(lines[start - 1:end]),
                                     doc, lang="java"))
            else:
                visit(child, prefix)

    visit(tree.root_node, "")
    return out


def chunk_source(src: str, path: str) -> list[CodeChunk]:
    """Chunks of one file by extension (empty for other languages)."""
    lang = LANGS.get(Path(path).suffix)
    if lang == "python":
        return chunk_python(src, path)
    if lang == "java":
        return chunk_java(src, path)
    return []


# ---- commit subjects ---------------------------------------------------------------------------
def commit_subjects(repo: Path, rev: str, file: str, start: int, end: int, n: int = MAX_SUBJECTS) -> tuple[str, ...]:
    """Subjects of the last `n` commits that touched `file:start-end` as of `rev`.

    Uses `git log -L` (line-range history); falls back to `git log --follow -n N -- file` when -L has
    nothing (a range that does not exist at `rev`, or a shallow clone).
    """
    out = run_git(repo, "log", "-L", f"{start},{end}:{file}", "-n", str(n), "-s", "--format=%s", rev)
    subs = [s for s in out.splitlines() if s.strip()]
    if not subs:
        out = run_git(repo, "log", "--follow", "-n", str(n), "--format=%s", rev, "--", file)
        subs = [s for s in out.splitlines() if s.strip()]
    return tuple(subs[:n])


# ---- repository ---------------------------------------------------------------------------------
def list_files(repo: Path, rev: str | None = None) -> list[str]:
    """Tracked chunkable files, sorted (`rev=None` reads the working tree's index)."""
    if rev is None:
        names = run_git(repo, "ls-files", check=True).splitlines()
    else:
        names = run_git(repo, "ls-tree", "-r", "--name-only", rev, check=True).splitlines()
    return sorted(n for n in names if Path(n).suffix in LANGS)


def read_file(repo: Path, path: str, rev: str | None = None) -> str:
    """File text at `rev`, or from disk when `rev` is None."""
    if rev is None:
        return (repo / path).read_text(encoding="utf-8", errors="replace")
    return run_git(repo, "show", f"{rev}:{path}", check=True)


def chunk_repo(repo: Path, rev: str | None = None, files: list[str] | None = None,
               with_commits: bool = False) -> list[CodeChunk]:
    """All chunks of a repository at `rev` (working tree when None), in file then line order.

    Args:
        repo: Repository root.
        rev: A commit-ish, or None for the working tree.
        files: Restrict to these repo-relative paths (default: every tracked .py / .java file).
        with_commits: Fill `commits` with `git log -L` subjects (slow: one git call per function).
    """
    out: list[CodeChunk] = []
    for f in (sorted(files) if files is not None else list_files(repo, rev)):
        try:
            src = read_file(repo, f, rev)
        except (OSError, RuntimeError):
            continue
        for c in chunk_source(src, f):
            if with_commits:
                c.commits = commit_subjects(repo, rev or "HEAD", f, c.start, c.end)
            out.append(c)
    return sorted(out, key=lambda c: (c.file, c.start, c.qualname))
