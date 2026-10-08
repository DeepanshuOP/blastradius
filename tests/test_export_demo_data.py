"""Tests for `analysis/export_demo_data.py`.

The markdown-table reader runs against a real generated paper table. The
end-to-end test runs the real exporter against `data/interim` into a temp dir
(skipped where that data is absent) and checks the default instance's JSON.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from analysis.demo_walkthrough import holdout_job_ids
from analysis.export_demo_data import find_table, rate

ROOT = Path(__file__).resolve().parent.parent
STAGES = {"change", "raw_log", "parsed_outcome", "head_vs_base", "verdict", "binding", "graph",
          "predictions"}
WALL_CLOCK_KEY = re.compile(r"(^|_)(now|timestamp|exported_at|generated_at|date|time)($|_)")


def test_rate_parses_paper_cells() -> None:
    assert rate("5,643/5,985 (94.29%)") == {"n": 5643, "d": 5985, "text": "5,643/5,985 (94.29%)"}


def test_find_table_reads_the_gates_table() -> None:
    cols, rows = find_table(ROOT / "paper/generated/gates.md", "Gates")
    assert cols[:2] == ["gate", "measured (n/d)"]
    assert any(r[0].startswith("Gate 1.5: combined binding") for r in rows)


def _keys(obj: object) -> list[str]:
    if isinstance(obj, dict):
        return [k for k in obj] + [x for v in obj.values() for x in _keys(v)]
    if isinstance(obj, list):
        return [x for v in obj for x in _keys(v)]
    return []


def _ints(obj: object) -> set[int]:
    if isinstance(obj, dict):
        return {x for v in obj.values() for x in _ints(v)}
    if isinstance(obj, list):
        return {x for v in obj for x in _ints(v)}
    return {obj} if isinstance(obj, int) and not isinstance(obj, bool) else set()


@pytest.mark.skipif(
    not (ROOT / "data/interim/outcomes.parquet").exists(), reason="needs data/interim"
)
def test_default_instance_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from analysis import export_demo_data

    monkeypatch.chdir(ROOT)
    monkeypatch.setitem(os.environ, "GIT_NO_LAZY_FETCH", "1")
    assert export_demo_data.main(tmp_path) == 0

    index = json.loads((tmp_path / "index.json").read_text())
    doc = json.loads((tmp_path / "instances" / f"{index['default']}.json").read_text())
    assert set(doc["stages"]) == STAGES
    assert re.fullmatch(r"[0-9a-f]{40}", doc["generated_at_git_sha"])

    keys = _keys(doc) + _keys(index) + _keys(json.loads((tmp_path / "results.json").read_text()))
    assert not [k for k in keys if k != "generated_at_git_sha" and not k.endswith("_git_sha")
                and WALL_CLOCK_KEY.search(k)]

    holdout, _ = holdout_job_ids()
    assert doc["stages"]["raw_log"]["job_id"] not in holdout
    assert not _ints(doc) & holdout
