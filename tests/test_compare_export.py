"""The Compare tab's exporter against the real generated files (values worked by hand from `paper/generated/`)."""

from __future__ import annotations

import pytest

from analysis import export_demo_data as ex


def test_wilson_matches_a_hand_computed_interval() -> None:
    lo, hi = ex.wilson(0, 10)       # 0/10: lower bound 0, upper 3.841/(10+3.841) = 0.2775
    assert lo == 0.0 and hi == pytest.approx(0.27754, abs=1e-4)
    assert ex.wilson(0, 0) == [0.0, 1.0]
    lo, hi = ex.wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=1e-3) and hi == pytest.approx(0.7634, abs=1e-3)


def test_e1_rows_are_the_generated_numbers() -> None:
    e1 = ex.compare_e1()
    assert e1 is not None and e1["n"] == 148
    rows = {r["id"]: r for r in e1["rows"]}
    assert list(rows) == ["ours", "B7", "B6", "B5", "B4", "B1"]
    assert rows["ours"]["recall10"].startswith("0.525") and rows["B4"]["p_adj_text"] == "0.01025"
    assert rows["B7"]["p_adj_text"] == "0.3823" and rows["B7"]["magnitude"] == "negligible"
    assert "NOT MET" in e1["verdict"]


def test_interim_flag_follows_n_against_the_preregistered_total() -> None:
    prog = ex.e3_progress()
    assert prog and all(p["interim"] == (p["n"] < p["total"]) for p in prog)
    for p in prog:
        assert (f"interim, n = {p['n']} of {p['total']}; run continuing" in p["text"]) == p["interim"]


def test_table2_links_come_from_the_literature_file() -> None:
    rows = {r["lit_number"]: r for r in ex.compare_table2()["rows"]}
    assert set(rows) == {6, 10, 23, 25, 26}
    assert rows[10]["url"] == "https://arxiv.org/abs/2509.10279" and rows[26]["result"] == "Pass@1 7.9-18.9%"
