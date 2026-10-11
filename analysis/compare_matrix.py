"""Loader and validator of `docs/compare_matrix.yaml` (the website's capability matrix and safety checklist).

The file is YAML written in its JSON subset, so the standard library reads it (no new dependency). `validate`
returns a list of problems; empty means every rule in the file's header holds.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

MATRIX = Path("docs/compare_matrix.yaml")
LITERATURE = Path("docs/LITERATURE.md")
RESULTS = Path("docs/RESULTS_2.md")
VALUES = ("yes", "no", "not_reported")
#: Column id -> the # of the work in docs/LITERATURE.md (BlastRadius and retest-all are not literature rows).
LIT_NUMBER = {"rtptorrent": 3, "tts": 10, "logsage": 23, "ci_repair_bench": 26, "chatrepair": 29, "agentless": 31}


def load(path: Path = MATRIX) -> dict:
    """Parse the matrix file (comment lines starting with `#` are dropped)."""
    text = re.sub(r"(?m)^#.*\n", "", path.read_text(encoding="utf-8"))
    return json.loads(text)


def test_exists(ref: str, root: Path = Path(".")) -> bool:
    """`tests/test_x.py::test_name` names a test function that is defined in that file."""
    file, _, name = ref.partition("::")
    p = root / file
    if not p.exists() or not name:
        return False
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
               for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))))


def validate(doc: dict, root: Path = Path(".")) -> list[str]:
    """Rule violations of the matrix and the safety checklist."""
    problems: list[str] = []
    lit = (root / LITERATURE).read_text(encoding="utf-8")
    res = (root / RESULTS).read_text(encoding="utf-8")
    cols = [c["id"] for c in doc["columns"]]
    for row in doc["rows"]:
        if set(row["cells"]) != set(cols):
            problems.append(f"{row['id']}: cells {sorted(row['cells'])} != columns")
        for cid, cell in row["cells"].items():
            where = f"{row['id']}/{cid}"
            if cell.get("value") not in VALUES:
                problems.append(f"{where}: value {cell.get('value')!r}")
            if not cell.get("source", "").strip():
                problems.append(f"{where}: no source")
            if cell.get("value") not in ("yes", "no"):
                continue
            quotes = re.findall(r'"([^"]{8,})"', cell["source"] + " " + cell.get("note", ""))
            if cid == "br":
                if not cell.get("proof"):
                    problems.append(f"{where}: BlastRadius yes without a proof test")
                problems += [f"{where}: proof {p} does not exist" for p in cell.get("proof", []) if not test_exists(p, root)]
            elif cid in LIT_NUMBER:
                if "docs/LITERATURE.md" not in cell["source"] or f"#{LIT_NUMBER[cid]}" not in cell["source"]:
                    problems.append(f"{where}: {cell['value']} must cite docs/LITERATURE.md #{LIT_NUMBER[cid]}")
                if not quotes or any(q.lower() not in lit.lower() for q in quotes):
                    problems.append(f"{where}: quoted evidence not found verbatim in docs/LITERATURE.md")
            else:   # retest_all: established by this project's own generated files and results document
                if not any(s in cell["source"] for s in ("docs/RESULTS_2.md", "paper/generated/")):
                    problems.append(f"{where}: retest-all cell must cite docs/RESULTS_2.md or paper/generated/")
                if quotes and any(q not in res for q in quotes):
                    problems.append(f"{where}: quoted evidence not found verbatim in docs/RESULTS_2.md")
    for item in doc["safety"]:
        if not item.get("tests"):
            problems.append(f"safety {item['claim']!r}: no test")
        problems += [f"safety {item['claim']!r}: {t} does not exist" for t in item.get("tests", []) if not test_exists(t, root)]
    return problems
