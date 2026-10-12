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


def test_recorded_comment_counts_one_unit_and_agrees_with_its_own_triage_table() -> None:
    """Part 0b: header, triage summary and table count unique canonical test ids; cases are stated, not mixed in.

    The seeded itsdangerous run executes 297 cases; inherited test methods run under several subclasses share one
    canonical id (class dropped, frozen contract), so 181 ids, 155 of them failing (260 failing cases).
    """
    import re

    text = (Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "bot_comment.md").read_text(encoding="utf-8")
    head = text.splitlines()[3]
    m = re.search(r"(\d+) unique test ids \((\d+) executed cases.*\*\*(\d+) failing ids\*\* \((\d+) failing cases\)", head)
    assert m, head
    ids, cases, failing_ids, failing_cases = map(int, m.groups())
    assert failing_ids <= failing_cases <= cases and failing_ids < failing_cases     # duplicates are the whole point
    s = re.search(r"(\d+) mine, (\d+) inherited, (\d+) flaky \(of (\d+) failing\)", text)
    assert s and int(s.group(4)) == failing_ids == sum(map(int, s.groups()[:3]))
    rows = re.findall(r"^\| `[^`]+` \| \*\*(?:mine|inherited|flaky)\*\* \|", text, flags=re.M)
    assert len(rows) <= failing_ids                      # the table is capped (TRIAGE_ROWS), never longer than the count
    assert "260 mine" not in text


def test_bot_triage_ignores_measured_durations() -> None:
    """Part 0a: confidence must not depend on how long a test happened to take on this machine."""
    from src.agents import bot

    src = Path(bot.__file__).read_text(encoding="utf-8")
    assert '"duration_s": None' in src
