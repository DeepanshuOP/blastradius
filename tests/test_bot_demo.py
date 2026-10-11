"""The recorded PR-bot run replays offline to the committed comment (needs the seeded itsdangerous checkout)."""

from __future__ import annotations

from pathlib import Path

from tests.conftest import requires_data

import analysis.bot_demo as bd


@requires_data("data/seeded/repos/itsdangerous", "data/seeded/venvs/itsdangerous/bin/python")
def test_recorded_bot_run_replays_to_the_committed_comment(tmp_path, monkeypatch) -> None:
    out = tmp_path / "comment.md"
    monkeypatch.setattr(bd, "OUT", out)
    monkeypatch.setattr("src.agents.llm.requests.post",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("replay must not reach the network")))
    assert bd.main(["replay"]) == 0
    committed = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "bot_comment.md"
    assert out.read_text(encoding="utf-8") == committed.read_text(encoding="utf-8")
    text = out.read_text(encoding="utf-8")
    assert "validated: full suite passed" in text and "```suggestion" in text and len(text) < 65_000
