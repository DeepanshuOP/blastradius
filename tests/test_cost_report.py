"""`analysis/cost_report.py` against the real recorded caches and ledger (expected values worked by hand)."""

from __future__ import annotations

import pytest

from analysis import cost_report as cr


def test_list_price_arithmetic_for_the_recorded_bot_call() -> None:
    # 1,362 prompt + 133 completion tokens on gpt-oss-20b: 1362 * 0.075e-6 + 133 * 0.30e-6
    usd = cr.usd_at_list("openai/gpt-oss-20b", 1362, 133)
    assert usd == pytest.approx(0.00014205)
    assert cr.usd_at_list("openai/gpt-oss-120b", 1_000_000, 1_000_000) == pytest.approx(0.75)
    assert cr.usd_at_list("qwen/qwen3.8-27b", 10, 10) is None      # no list price recorded: not guessed


def test_the_recorded_bot_run_is_one_call_of_1495_tokens() -> None:
    (run,) = cr.recorded_runs("bot")
    assert run["model"] == "openai/gpt-oss-20b" and run["calls"] == 1
    assert (run["prompt_tokens"], run["completion_tokens"]) == (1362, 133)
    assert run["tokens_per_call"] == 1495


def test_nothing_was_paid_and_the_report_says_so() -> None:
    assert cr.ledger_summary()["paid_usd"] == 0.0
    doc = {"prices": {"date": cr.PRICES_DATE, "url": cr.PRICES_URL,
                      "usd_per_million_in_out": {m: list(p) for m, p in cr.GROQ_LIST_PRICES.items()}},
           "ledger": cr.ledger_summary(), "e3": [], "bot": cr.recorded_runs("bot"), "bot_live": cr.live_pr_run(), "ask": cr.recorded_runs("ask"),
           "context": cr.CHATREPAIR_CONTEXT}
    text = cr.render(doc)
    assert "**USD actually paid: 0.00**" in text and "https://groq.com/pricing" in text and "2026-10-11" in text
    assert "ChatRepair reported $0.42 per fixed bug (ChatGPT, Defects4J, 2024). Different bugs and model; context only." in text


def test_per_fix_is_total_tokens_over_fixes_and_none_for_zero_fixes() -> None:
    usage = {"openai/gpt-oss-120b|standard": {"model": "openai/gpt-oss-120b", "variant": "standard", "n_tasks": 4, "arms": {
        "R1": {"n": 4, "accepted": 2, "prompt_tokens": 4000, "completion_tokens": 800, "calls": 4},
        "R0": {"n": 4, "accepted": 0, "prompt_tokens": 0, "completion_tokens": 0, "calls": 0}}}}
    r0, r1 = cr.e3_rows(usage)
    assert r1["in_per_task"] == 1000 and r1["in_per_fix"] == 2000 and r1["out_per_fix"] == 400
    assert r0["in_per_fix"] is None and r0["usd_list_per_fix"] is None


def test_the_live_pr_run_is_read_from_the_comment_footer() -> None:
    run = cr.live_pr_run()
    assert run == {"model": "openai/gpt-oss-120b", "tokens": 1008, "file": "pr1_comment.md"}
