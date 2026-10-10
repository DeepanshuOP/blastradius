"""Source-span mutation of Python files, for BR-Seeded.

`ast` is used only to LOCATE nodes. Every edit is a text replacement of the node's
own span (`lineno`, `col_offset`, `end_col_offset`), so the resulting diff is one
minimal hunk and nothing else in the file is reformatted. A whole file is never
passed through `ast.unparse`.

Operators:
    CMP_FLIP     `<`<->`<=`, `>`<->`>=`, `==`<->`!=` in a single comparison
    ARITH_SWAP   `+`<->`-` in a binary expression
    NEGATE_COND  `if x:` / `while x:`  ->  `if not (x):`
    OFF_BY_ONE   an integer literal inside `range(...)` or a subscript, plus one
    BOOL_RETURN  `return True` <-> `return False`

`DROP_CALL_ARG` is not implemented: dropping an argument is only trivially safe
for calls with a default for it, which `ast` cannot establish alone.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

OPERATORS = ("CMP_FLIP", "ARITH_SWAP", "NEGATE_COND", "OFF_BY_ONE", "BOOL_RETURN")
_CMP_FLIP = {"<": "<=", "<=": "<", ">": ">=", ">=": ">", "==": "!=", "!=": "=="}


@dataclass(frozen=True)
class Mutation:
    """One located edit.

    Attributes:
        operator: One of :data:`OPERATORS`.
        line: 1-based line of the edit.
        start: Start offset into the source text (characters).
        end: End offset (exclusive).
        old: Replaced text.
        new: Replacement text.
        function: Qualified name of the enclosing function (`Class.method`), or `<module>`.
    """

    operator: str
    line: int
    start: int
    end: int
    old: str
    new: str
    function: str


def _line_starts(source: str) -> list[int]:
    starts, pos = [0], 0
    for line in source.splitlines(keepends=True):
        pos += len(line)
        starts.append(pos)
    return starts


class _Finder(ast.NodeVisitor):
    def __init__(self, source: str) -> None:
        self.src = source
        self.starts = _line_starts(source)
        self.lines = source.splitlines(keepends=True)
        self.scope: list[str] = []
        self.found: list[Mutation] = []

    # -- helpers ---------------------------------------------------------------------------
    def off(self, lineno: int, col_utf8: int) -> int:
        """Character offset of a (1-based line, UTF-8 byte column) position."""
        line = self.lines[lineno - 1]
        return self.starts[lineno - 1] + len(line.encode("utf-8")[:col_utf8].decode("utf-8", errors="ignore"))

    def span(self, node: ast.AST) -> tuple[int, int] | None:
        if node.lineno != node.end_lineno:  # single-line nodes only: keeps the diff to one hunk
            return None
        return self.off(node.lineno, node.col_offset), self.off(node.end_lineno, node.end_col_offset)

    def add(self, op: str, line: int, start: int, end: int, new: str) -> None:
        self.found.append(Mutation(op, line, start, end, self.src[start:end], new,
                                   ".".join(self.scope) or "<module>"))

    # -- scope -----------------------------------------------------------------------------
    def _scoped(self, node: ast.AST, name: str) -> None:
        self.scope.append(name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node):  # noqa: N802
        self._scoped(node, node.name)

    visit_AsyncFunctionDef = visit_FunctionDef  # noqa: N815

    def visit_ClassDef(self, node):  # noqa: N802
        self._scoped(node, node.name)

    # -- operators -------------------------------------------------------------------------
    def visit_Compare(self, node: ast.Compare) -> None:  # noqa: N802
        if len(node.ops) == 1 and node.lineno == node.end_lineno and node.left.end_lineno == node.comparators[0].lineno:
            lo = self.off(node.left.end_lineno, node.left.end_col_offset)
            hi = self.off(node.comparators[0].lineno, node.comparators[0].col_offset)
            seg = self.src[lo:hi]
            tok = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="}.get(
                type(node.ops[0]))
            if tok and seg.count(tok) == 1 and seg.strip() == tok:
                i = lo + seg.index(tok)
                self.add("CMP_FLIP", node.lineno, i, i + len(tok), _CMP_FLIP[tok])
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:  # noqa: N802
        if isinstance(node.op, (ast.Add, ast.Sub)) and node.left.end_lineno == node.right.lineno:
            lo = self.off(node.left.end_lineno, node.left.end_col_offset)
            hi = self.off(node.right.lineno, node.right.col_offset)
            seg = self.src[lo:hi]
            tok = "+" if isinstance(node.op, ast.Add) else "-"
            if tok in seg and seg.count(tok) == 1 and set(seg.strip()) <= {tok, "(", ")"}:
                i = lo + seg.index(tok)
                self.add("ARITH_SWAP", node.lineno, i, i + 1, "-" if tok == "+" else "+")
        self.generic_visit(node)

    def _cond(self, node: ast.If | ast.While) -> None:
        sp = self.span(node.test)
        if sp is not None and not isinstance(node.test, ast.UnaryOp):
            text = self.src[sp[0]:sp[1]]
            self.add("NEGATE_COND", node.test.lineno, sp[0], sp[1], f"not ({text})")
        self.generic_visit(node)

    visit_If = _cond  # noqa: N815
    visit_While = _cond  # noqa: N815

    def visit_Return(self, node: ast.Return) -> None:  # noqa: N802
        v = node.value
        if isinstance(v, ast.Constant) and isinstance(v.value, bool):
            sp = self.span(v)
            if sp:
                self.add("BOOL_RETURN", v.lineno, sp[0], sp[1], "False" if v.value else "True")
        self.generic_visit(node)

    def _int_literals(self, node: ast.AST) -> None:
        for child in ast.walk(node):
            if (isinstance(child, ast.Constant) and type(child.value) is int and child.lineno == child.end_lineno):
                sp = self.span(child)
                if sp and self.src[sp[0]:sp[1]].isdigit():
                    self.add("OFF_BY_ONE", child.lineno, sp[0], sp[1], str(child.value + 1))

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if isinstance(node.func, ast.Name) and node.func.id == "range":
            for a in node.args:
                self._int_literals(a)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:  # noqa: N802
        self._int_literals(node.slice)
        self.generic_visit(node)


def find_mutations(source: str) -> list[Mutation]:
    """Every operator application in `source`, in source order, de-duplicated by span.

    Args:
        source: Python source text.

    Returns:
        Mutations sorted by `(start, operator)`. Empty if the source does not parse.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    f = _Finder(source)
    f.visit(tree)
    seen, out = set(), []
    for m in sorted(f.found, key=lambda m: (m.start, m.operator, m.new)):
        if (m.start, m.end, m.operator) not in seen:
            seen.add((m.start, m.end, m.operator))
            out.append(m)
    return out


def apply(source: str, m: Mutation) -> str:
    """Return `source` with exactly the span of `m` replaced.

    Raises:
        ValueError: If the text at the span is no longer `m.old`.
    """
    if source[m.start:m.end] != m.old:
        raise ValueError("source does not match the mutation's span")
    return source[:m.start] + m.new + source[m.end:]
