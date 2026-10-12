"""The Live Lab's token ledger is its own file, and the daily cap counts E3's ledger and the lab's together.

Fixtures are real ledger rows: three gpt-oss-120b and one qwen row of `eval/llm_cache/usage.jsonl` and the lab's
first live call (`lab_usage.jsonl`). Expected totals are hand-summed.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from src.lab import cache

FIX = Path(__file__).parent / "fixtures" / "lab" / "ledgers"


def ts(s: str) -> float:
    return datetime.fromisoformat(s).timestamp()


def test_day_tokens_sums_both_ledgers_inside_the_window() -> None:
    ledgers = (FIX / "usage.jsonl", FIX / "lab_usage.jsonl")
    total, oldest = cache.day_tokens("openai/gpt-oss-120b", ts("2026-10-12T16:00:00+00:00"), ledgers)
    assert total == 1743 + 1794 + 2097 + 681 == 6315
    assert oldest == ts("2026-10-11T17:10:57+00:00")
    # 24 h after the first row it has left the window
    total, _ = cache.day_tokens("openai/gpt-oss-120b", ts("2026-10-12T17:11:00+00:00"), ledgers)
    assert total == 1794 + 2097 + 681 == 4572
    # rows of another model never count
    assert cache.day_tokens("qwen/qwen3.8-27b", ts("2026-10-12T16:00:00+00:00"), ledgers)[0] == 1367


def test_lab_client_writes_only_the_lab_ledger(tmp_path: Path) -> None:
    e3 = tmp_path / "usage.jsonl"
    lab = tmp_path / "lab_usage.jsonl"
    shutil.copy(FIX / "usage.jsonl", e3)
    before = e3.read_bytes()
    llm = cache.LabGroqLLM(api_key="unused", model="openai/gpt-oss-120b", ledger=lab, quota_ledgers=(e3, lab),
                           clock=lambda: ts("2026-10-12T05:00:00+00:00"))
    llm._record_usage(500)
    assert e3.read_bytes() == before
    assert lab.read_text(encoding="utf-8") == '{"timestamp": "2026-10-12T05:00:00+00:00", "model": "openai/gpt-oss-120b", "tokens": 500}\n'
    assert llm._day_total() == (1743 + 1794 + 2097 + 500, ts("2026-10-11T17:10:57+00:00"))


def test_defaults_point_at_the_separate_ledger() -> None:
    llm = cache.LabGroqLLM(api_key="unused")
    assert llm.ledger.name == "lab_usage.jsonl"
    assert {p.name for p in llm.quota_ledgers} == {"usage.jsonl", "lab_usage.jsonl"}
