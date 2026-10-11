"""The PR-bot workflow template (D-63): least privilege and the documented command."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_workflow_template_is_least_privilege_and_commands_the_documented_cli() -> None:
    yaml = pytest.importorskip("yaml")
    path = Path(__file__).resolve().parents[1] / "integrations" / "github-actions" / "blastradius-bot.yml"
    wf = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert wf["permissions"] == {"contents": "read", "pull-requests": "write"}
    assert wf[True]["pull_request"]["types"] == ["opened", "synchronize"]      # YAML parses `on:` as True
    step = next(s for s in wf["jobs"]["comment"]["steps"] if s.get("name") == "Run the bot")
    assert step["env"]["BR_AGENT_PROVIDER"] == "groq" and step["env"]["BR_AGENT_MODEL"] == "openai/gpt-oss-20b"
    assert "BR_LLM_CACHE_DIR" in step["env"] and "secrets.GROQ_API_KEY" in step["env"]["GROQ_API_KEY"]
    assert "python -m src.agents bot" in step["run"] and "--pr" in step["run"]
    assert "git push" not in path.read_text(encoding="utf-8")
