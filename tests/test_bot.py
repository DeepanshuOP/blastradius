"""PR bot (D-63, exploratory): rendering, size cap, edit-not-repost, patch geometry, and a replayed end-to-end run.

The repository is the checked-in shopcart sample as a real git repo with a base commit and a head commit that
carries the discount bug; the test suites are real pytest runs. The only thing replaced is the Groq HTTP
transport (as in `tests/test_agents_repair.py`), and the second run proves the recorded replies replay.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

from src.agents import bot
from src.agents.forge import LocalForge
from src.agents.llm import GroqLLM
from src.agents.llm_cache import CacheMiss, LLMCache
from src.eval.seeded.build import git

SAMPLE = Path(__file__).resolve().parents[1] / "src" / "agents" / "demo" / "sample_repo"
FIXED = "return subtotal - (subtotal * percent) // 100"
BUG = "return subtotal + (subtotal * percent) // 100"


# ---- rendering -----------------------------------------------------------------------------------
def rows(n: int = 3, failing: int = 1) -> list[dict]:
    return [{"test": f"tests/test_{i}.py::t{i}", "outcome": "failed" if i < failing else "passed",
             "message": "assert 1 == 2" if i < failing else ""} for i in range(n)]


def render(repair, **kw) -> str:
    base = dict(pr=7, base="a" * 40, head="b" * 40,
                risk=[{"test": "tests/test_pricing.py", "score": 1.5, "why": "hist_fail=3 (+0.40)"}],
                ranker="e1-lgbm-v1", results=rows(), n_total=3, first_failure=1,
                triage=[{"test": "tests/test_0.py::t0", "class": "mine", "confidence": 0.8, "reason": "no evidence"}],
                repair=repair, model="openai/gpt-oss-20b", tokens=1234)
    base.update(kw)
    return bot.render_comment(**base)


def test_suggestion_block_only_for_a_validated_patch() -> None:
    sug = bot.Suggestion("shopcart/pricing.py", 20, 20, ["    return subtotal - 1"])
    ok = render({"validated": True, "attempts": 1, "suggestions": [sug], "diff": "x"})
    assert "```suggestion\n    return subtotal - 1\n```" in ok
    assert "validated: full suite passed" in ok and "Not validated" not in ok
    assert ok.startswith(bot.MARKER)
    bad = render({"validated": False, "attempts": 2, "suggestions": [sug], "diff": "--- a/x\n+++ b/x", "note": "n"})
    assert "```suggestion" not in bad and "<details><summary>patch (not validated)</summary>" in bad
    assert "**Not validated**" in bad and "validated: no (see above)" in bad
    none = render(None, triage=[], results=rows(3, 0))
    assert "```suggestion" not in none and "validated: no patch to validate" in none


def test_comment_stays_under_the_cap_and_keeps_failures_and_the_suggestion() -> None:
    many = [{"test": f"tests/test_{i}.py::" + "x" * 80, "outcome": "passed", "message": ""} for i in range(2000)]
    many += [{"test": "tests/test_f.py::t_fail", "outcome": "failed", "message": "boom " * 40}]
    sug = bot.Suggestion("a.py", 3, 3, ["fixed"])
    text = render({"validated": True, "attempts": 1, "suggestions": [sug]}, results=many, n_total=len(many))
    assert len(text) < bot.MAX_COMMENT
    assert "tests/test_f.py::t_fail" in text and "```suggestion\nfixed\n```" in text
    huge = render({"validated": False, "attempts": 1, "suggestions": [], "diff": "+x\n" * 40000, "note": "n"})
    assert len(huge) <= bot.MAX_COMMENT and huge.count("```") % 2 == 0


def test_triage_table_is_capped_and_summarised() -> None:
    tri = [{"test": f"tests/t.py::t{i:03d}", "class": "inherited" if i % 4 == 0 else "mine", "confidence": 0.9,
            "reason": "r"} for i in range(60)]
    text = render(None, triage=tri)
    assert "45 mine, 15 inherited, 0 flaky (of 60 failing)." in text
    assert "_40 more failures not shown._" in text
    sec = text.split("### 3. Triage of each failure")[1]
    assert sec.count("| `tests/t.py::t") == 20 and "**inherited**" not in sec    # mine rows come first


def test_the_bot_edits_its_own_comment_instead_of_posting_again(tmp_path) -> None:
    forge = LocalForge(tmp_path, tmp_path / "state")
    forge.create_comment(5, "someone else's comment")
    first = bot.upsert_comment(forge, 5, f"{bot.MARKER}\nrun 1")
    second = bot.upsert_comment(forge, 5, f"{bot.MARKER}\nrun 2")
    assert first["id"] == second["id"]
    bodies = [c["body"] for c in forge.list_comments(5)]
    assert bodies == ["someone else's comment", f"{bot.MARKER}\nrun 2"]


# ---- patch geometry (hand-computed) -------------------------------------------------------------------
def test_patch_hunks_and_visible_lines() -> None:
    head = {"m.py": "a\nb\nc\nd\ne\n"}
    # replace c with C and e with x
    got = bot.patch_hunks(head, {"m.py": "a\nb\nC\nd\nx\n"})
    assert [(s.start, s.end, s.lines) for s in got] == [(3, 3, ["C"]), (5, 5, ["x"])]
    # a pure insertion keeps the line above and adds after it; a pure deletion replaces with nothing
    assert [(s.start, s.end, s.lines) for s in bot.patch_hunks({"m.py": "a\nb\n"}, {"m.py": "a\nX\nb\n"})] == [(1, 1, ["a", "X"])]
    assert [(s.start, s.end, s.lines) for s in bot.patch_hunks({"m.py": "a\nb\nc\n"}, {"m.py": "a\nc\n"})] == [(2, 2, [])]
    assert bot.Suggestion("m.py", 2, 2, []).body() == "```suggestion\n```"
    diff = "--- a/m.py\n+++ b/m.py\n@@ -2,4 +2,5 @@\n b\n-c\n+c2\n+c3\n d\n e\n"
    assert bot.diff_visible_lines(diff) == {"m.py": {2, 3, 4, 5, 6}}


class Resp:
    def __init__(self, text, tokens=100):
        self.status_code = 200
        self.headers: dict = {}
        self.text = ""
        self._b = {"model": "openai/gpt-oss-20b", "choices": [{"message": {"content": text}}],
                   "usage": {"prompt_tokens": tokens - 20, "completion_tokens": 20, "total_tokens": tokens},
                   "x_groq": {"id": "req_bot"}}

    def json(self):
        return self._b


@pytest.fixture()
def pr_repo(tmp_path) -> tuple[Path, str, str]:
    repo = tmp_path / "shopcart"
    shutil.copytree(SAMPLE, repo, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").strip()
    git(repo, "checkout", "-q", "-b", "bug")
    p = repo / "shopcart" / "pricing.py"
    p.write_text(p.read_text().replace(FIXED, BUG))
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "feat: discount tweak")
    head = git(repo, "rev-parse", "HEAD").strip()
    return repo, base, head


def test_full_bot_run_then_replay_from_the_recorded_reply(pr_repo, tmp_path, monkeypatch) -> None:
    repo, base, head = pr_repo
    reply = f"shopcart/pricing.py\n<<<<<<< SEARCH\n{BUG}\n=======\n{FIXED}\n>>>>>>> REPLACE"
    calls: list[dict] = []
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: calls.append(k) or Resp(reply))
    cache_path = tmp_path / "bot_cache.jsonl"

    def llm(replay: bool):
        return GroqLLM(api_key="k", model="openai/gpt-oss-20b", cache=LLMCache(cache_path, replay=replay),
                       ledger=tmp_path / "u.jsonl", sleeper=lambda s: None)

    out = bot.run_bot(repo, base, head, 7, llm=llm(False), state_dir=tmp_path / "s1", python=sys.executable)
    assert len(calls) == 1 and out.validated
    assert out.stats["failing"] >= 1 and out.stats["mine"] >= 1
    # one hunk: the bug line (pricing.py line 20) goes back to the fixed expression
    assert [(s.path, s.start, s.end) for s in out.suggestions] == [("shopcart/pricing.py", 20, 20)]
    assert out.suggestions[0].lines == [f"    {FIXED}"]
    assert "```suggestion\n    " + FIXED + "\n```" in out.comment
    assert "validated: full suite passed" in out.comment and "tests/test_pricing.py" in out.comment
    assert "**mine**" in out.comment and len(out.comment) < bot.MAX_COMMENT
    # the failing tests are ordered before the passing ones (risk-first, failures first in the table)
    table = out.comment.split("### 2. Results, risk-first")[1].split("###")[0]
    assert table.index("| failed |") < table.index("| passed |")

    # replay: the same run with the network forbidden finds every request in the cache
    monkeypatch.setattr("src.agents.llm.requests.post",
                        lambda *a, **k: pytest.fail("a replayed bot run must not reach the network"))
    again = bot.run_bot(repo, base, head, 7, llm=llm(True), state_dir=tmp_path / "s2", python=sys.executable)
    assert again.validated and again.suggestions == out.suggestions
    assert again.comment == out.comment

    # no cache entry for a different change: replay mode raises instead of calling out
    p = repo / "shopcart" / "pricing.py"
    p.write_text(p.read_text().replace("percent) // 100", "percent) // 101"))
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "feat: another change")
    with pytest.raises(CacheMiss):
        bot.run_bot(repo, base, git(repo, "rev-parse", "HEAD").strip(), 7, llm=llm(True), state_dir=tmp_path / "s3",
                    python=sys.executable)


def test_without_a_model_the_comment_says_so_and_offers_nothing(pr_repo, tmp_path) -> None:
    repo, base, head = pr_repo
    out = bot.run_bot(repo, base, head, 7, llm=None, state_dir=tmp_path / "s", python=sys.executable)
    assert not out.validated and out.suggestions == []
    assert "```suggestion" not in out.comment and "No model is configured" in out.comment
    assert "**mine**" in out.comment



# ---- indentation-tolerant apply (PR #1 on the itsdangerous fork) ----------------------------------
# The two replies are the real ones gpt-oss-20b gave on that PR (fixtures/bot_tolerant): the first shifted the
# block four columns, the second copied the "NNN| " gutter separator space. The strict applier found both 0 times.
TOL = Path(__file__).resolve().parent / "fixtures" / "bot_tolerant"
TIMED = "src/itsdangerous/timed.py"


@pytest.fixture()
def timed_repo(tmp_path) -> Path:
    (tmp_path / TIMED).parent.mkdir(parents=True)
    shutil.copy(TOL / "timed.py", tmp_path / TIMED)
    return tmp_path


def _expected(repo: Path) -> str:
    text = (repo / TIMED).read_text()
    assert text.count("            if age < max_age:\n") == 1
    return text.replace("            if age < max_age:\n", "            if age > max_age:\n")


@pytest.mark.parametrize("name", ["reply1.txt", "reply2.txt"])
def test_strict_apply_rejects_the_real_replies_and_tolerant_apply_fixes_them(timed_repo, name) -> None:
    from src.agents.repair import apply_blocks, parse_blocks

    blocks = parse_blocks((TOL / name).read_text())
    assert blocks and blocks[0][0] == TIMED
    with pytest.raises(ValueError, match="matches 0 times"):
        apply_blocks(timed_repo, blocks, {TIMED})
    out = bot.apply_blocks_tolerant(timed_repo, blocks, {TIMED})
    assert out == {TIMED: _expected(timed_repo)}


def test_tolerant_apply_still_requires_one_match_and_says_how_to_fix(timed_repo) -> None:
    miss = [(TIMED, "            if age == max_age:\n                pass", "x")]
    with pytest.raises(ValueError, match=r"matches 0 times.*without the 'NNN\|' line-number gutter.*age == max_age"):
        bot.apply_blocks_tolerant(timed_repo, miss, {TIMED})
    twice = [(TIMED, "raise SignatureExpired(", "raise SignatureExpired(")]
    with pytest.raises(ValueError, match="matches 2 times"):
        bot.apply_blocks_tolerant(timed_repo, twice, {TIMED})
    with pytest.raises(ValueError, match="was not one of the files shown"):
        bot.apply_blocks_tolerant(timed_repo, miss, {"other.py"})


def test_the_bot_retries_twice_with_the_failure_in_the_prompt(timed_repo) -> None:
    from src.agents.llm import ChatResult
    from src.agents.repair import FailureReport, RepairAgent

    assert bot.MAX_REPAIR_RETRIES == 2 and bot.MAX_REPAIR_ATTEMPTS == 3
    prompts: list[str] = []
    replies = iter(["no blocks here", (TOL / "reply2.txt").read_text(), (TOL / "reply2.txt").read_text()])

    class Fake:
        def chat(self, system, user, max_tokens):
            prompts.append(user)
            return ChatResult(next(replies), {"total_tokens": 1}, "m", False)

    report = FailureReport(failing=[{"test_id": "tests/test_timed.py::test_max_age", "output": "age check"}],
                           pr_diff="", triage="mine", changed_files=[TIMED])
    seen: list[dict] = []
    res = RepairAgent(Fake(), "R3", max_retries=bot.MAX_REPAIR_RETRIES, applier=bot.apply_blocks_tolerant).run(
        timed_repo, [TIMED], report, lambda files: (seen.append(files) or False, "tests/test_timed.py::x: still failing"))
    assert len(res.attempts) == 3 and not res.accepted
    assert "could not be applied" in prompts[1] and "no SEARCH/REPLACE blocks" in prompts[1]
    assert "tests/test_timed.py::x: still failing" in prompts[2]
    assert seen == [{TIMED: _expected(timed_repo)}] * 2
