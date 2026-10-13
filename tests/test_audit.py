"""D-71: the hash-chained decision log: schema, chain, tamper detection, redaction, and an audited bot run.

The bot run is the real shopcart sample as a git repo (as in tests/test_bot.py) with real pytest runs; only the Groq
HTTP transport is replaced by a recorded reply.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from analysis.secret_scan import scan_text
from src.agents import audit, bot
from src.agents.llm import GroqLLM
from src.agents.llm_cache import LLMCache
from src.eval.seeded.build import git

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "src" / "agents" / "demo" / "sample_repo"
FIXED = "return subtotal - (subtotal * percent) // 100"
BUG = "return subtotal + (subtotal * percent) // 100"
BLOCKERS = ("github_token", "bearer_token")


def _log(tmp_path: Path, n: int = 4) -> audit.DecisionLog:
    log = audit.DecisionLog("unit-run", root=tmp_path)
    log.record("system", "detect", "run_suite_risk_first", "accept", "The run had 2 failing cases", {"failed": 2})
    m = log.model_block(provider="groq", model="openai/gpt-oss-120b", prompt="p", reply="r", tokens_in=10,
                        tokens_out=5, cost_usd=0.0, cache_hit=False, tag="attempt1")
    log.record("model", "patch", "propose_patch", "accept", "Attempt 1 returned 1 character", {}, model=m)
    log.record("system", "verify", "check_full", "reject", "Attempt 1: check 'full' failed", {"check": "full"})
    log.record("system", "finish", "render_comment", "done", "Rendered the PR comment", {})
    return log


def test_chain_verifies_and_schema_is_exact(tmp_path) -> None:
    log = _log(tmp_path)
    ok, problems, n = audit.verify("unit-run", tmp_path)
    assert ok and problems == [] and n == 4
    recs = audit.read(log.path)
    assert [r["seq"] for r in recs] == [1, 2, 3, 4]
    assert recs[0]["prev_hash"] == audit.GENESIS
    assert all(b["prev_hash"] == a["hash"] for a, b in zip(recs, recs[1:]))
    assert all(sorted(r) == sorted(audit.KEYS) for r in recs)
    assert sorted(recs[1]["model"]) == sorted(audit.MODEL_KEYS)
    assert recs[1]["model"]["prompt_sha256"] == audit.sha256("p")       # hash only; text lives in the run folder
    assert (tmp_path / "unit-run" / "attempt1.prompt.txt").read_text() == "p"
    assert all(r["ts"].endswith("Z") for r in recs)
    # a second writer continues the chain instead of restarting it
    audit.DecisionLog("unit-run", root=tmp_path).record("system", "finish", "again", "done", "Again", {})
    assert audit.verify("unit-run", tmp_path)[0]


@pytest.mark.parametrize("line_no", [0, 2, 3])
def test_one_edited_byte_fails_verify(tmp_path, line_no) -> None:
    log = _log(tmp_path)
    lines = log.path.read_text().splitlines()
    i = lines[line_no].index('"reason":"') + len('"reason":"')
    lines[line_no] = lines[line_no][:i] + ("X" if lines[line_no][i] != "X" else "Y") + lines[line_no][i + 1:]
    log.path.write_text("\n".join(lines) + "\n")
    ok, problems, _ = audit.verify("unit-run", tmp_path)
    assert not ok and any("hash mismatch" in p for p in problems)
    rc = subprocess.run([sys.executable, "-m", "src.agents.audit", "verify", "unit-run", "--root", str(tmp_path)],
                        cwd=ROOT, capture_output=True, text=True)
    assert rc.returncode == 1 and rc.stdout.startswith("FAIL")


def test_dropped_record_breaks_the_chain(tmp_path) -> None:
    log = _log(tmp_path)
    lines = log.path.read_text().splitlines()
    log.path.write_text("\n".join(lines[:1] + lines[2:]) + "\n")
    ok, problems, _ = audit.verify("unit-run", tmp_path)
    assert not ok and any("prev_hash" in p for p in problems)


def test_schema_values_are_enforced(tmp_path) -> None:
    log = audit.DecisionLog("r", root=tmp_path)
    with pytest.raises(ValueError):
        log.record("robot", "detect", "x", "accept", "r")
    with pytest.raises(ValueError):
        log.record("system", "deploy", "x", "accept", "r")
    with pytest.raises(ValueError):
        log.record("system", "detect", "x", "maybe", "r")
    with pytest.raises(ValueError):
        audit.DecisionLog("../escape", root=tmp_path)
    r = log.record("system", "detect", "x", "accept", "two\nlines   of text")
    assert r["reason"] == "two lines of text."


def test_no_env_value_in_any_record_or_artifact(tmp_path, monkeypatch) -> None:
    secret = "gsk_" + "A1b2C3d4" * 6
    monkeypatch.setenv("GROQ_API_KEY", secret)
    monkeypatch.setenv("BR_TEST_TOKEN", "ghp_" + "z" * 36)
    log = audit.DecisionLog("redact", root=tmp_path)
    m = log.model_block(provider="groq", model="m", prompt=f"key is {secret}", reply="ok", tokens_in=1, tokens_out=1,
                        cost_usd=0.0, cache_hit=False, tag="a1")
    log.record("system", "detect", "x", "accept", f"saw {secret}", {"nested": {"v": "ghp_" + "z" * 36}}, model=m)
    blob = "".join(p.read_text() for p in tmp_path.rglob("*") if p.is_file())
    assert secret not in blob and "ghp_" + "z" * 36 not in blob and "[redacted]" in blob
    assert audit.verify("redact", tmp_path)[0]


def test_render_and_summary(tmp_path) -> None:
    log = _log(tmp_path)
    text = audit.render(audit.read(log.path))
    assert "detect" in text and "-> REJECT" in text and "hash " in text
    s = audit.summary(audit.read(log.path))
    assert s["records"] == 4 and s["head_hash"] == log.prev and s["stages"]["verify"] == 1


# ---- an audited bot run ---------------------------------------------------------------------------
class Resp:
    status_code, headers = 200, {}

    def __init__(self, text: str) -> None:
        self._b = {"model": "openai/gpt-oss-20b", "choices": [{"message": {"content": text}}],
                   "usage": {"prompt_tokens": 900, "completion_tokens": 40, "total_tokens": 940}, "x_groq": {"id": "r1"}}
        self.text = json.dumps(self._b)

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
    return repo, base, git(repo, "rev-parse", "HEAD").strip()


def test_audited_bot_run_records_every_stage_and_leaks_nothing(pr_repo, tmp_path, monkeypatch) -> None:
    repo, base, head = pr_repo
    key = "gsk_" + "Q9w8E7r6" * 6
    monkeypatch.setenv("GROQ_API_KEY", key)
    first = "shopcart/pricing.py\n<<<<<<< SEARCH\nthis line is not in the file\n=======\nx\n>>>>>>> REPLACE"
    good = f"shopcart/pricing.py\n<<<<<<< SEARCH\n{BUG}\n=======\n{FIXED}\n>>>>>>> REPLACE"
    replies = [first, good]
    monkeypatch.setattr("src.agents.llm.requests.post", lambda *a, **k: Resp(replies.pop(0)))
    llm = GroqLLM(api_key=key, model="openai/gpt-oss-20b", cache=LLMCache(tmp_path / "c.jsonl"),
                  ledger=tmp_path / "u.jsonl", sleeper=lambda s: None)
    root = tmp_path / "logs" / "agent"
    log = audit.DecisionLog("bot-run", root=root)
    out = bot.run_bot(repo, base, head, 7, llm=llm, state_dir=tmp_path / "s", python=sys.executable, audit=log)
    assert out.validated
    ok, problems, n = audit.verify("bot-run", root)
    assert ok, problems
    recs = audit.read(log.path)
    stages = [r["stage"] for r in recs]
    for st in ("detect", "triage", "retrieve", "patch", "verify", "retry", "finish"):
        assert st in stages, st
    assert stages[0] == "detect" and stages[-1] == "finish"
    models = [r for r in recs if r["actor"] == "model"]
    assert len(models) == 2 and all(r["model"]["provider"] == "groq" for r in models)
    assert models[0]["model"]["tokens_in"] == 900 and models[0]["model"]["cost_usd"] == 0.0
    retry = next(r for r in recs if r["stage"] == "retry")
    assert retry["decision"] == "retry" and "applies" in retry["reason"]
    checks = {r["action"]: r["decision"] for r in recs if r["stage"] == "verify" and r["evidence"].get("attempt") == 2}
    assert checks == {"check_applies": "accept", "check_syntax": "accept", "check_targeted": "accept",
                      "check_full": "accept", "check_scope": "accept",
                      "check_reverify_full": "accept", "check_reverify_scope": "accept"}   # fresh worktree (D-70)
    verdict = next(r for r in recs if r["action"] == "verdict")
    assert verdict["decision"] == "accept" and verdict["evidence"]["attempts"] == 2
    # reasons are code-written: the model's reply text never appears in a record
    blob = log.path.read_text()
    assert "this line is not in the file" not in blob and FIXED not in blob
    # nothing credential-shaped anywhere under the log root, by the project's own scanner and by value
    everything = "".join(p.read_text(encoding="utf-8") for p in root.rglob("*") if p.is_file())
    assert key not in everything
    found = scan_text(everything)
    assert not any(found.get(c) for c in BLOCKERS), found


def test_existing_logs_agent_folder_has_no_secret() -> None:
    """The real logs/agent (if any run has written it) passes the secret scanner and holds no env value."""
    root = ROOT / "logs" / "agent"
    files = [p for p in root.rglob("*") if p.is_file()] if root.exists() else []
    secrets = audit.secret_values()
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        assert not any(scan_text(text).get(c) for c in BLOCKERS), p
        assert not any(s in text for s in secrets), p
