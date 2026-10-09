"""Pluggable LLM access for the agents (D-55: outside the reproducible pipeline).

Two providers:

* ``offline`` returns ``None`` for every request. Each agent has a deterministic
  fallback, so the whole workflow runs with no key and no network.
* ``anthropic`` calls the Anthropic Messages API over plain ``requests`` (already a
  project dependency, so no new package). Key: ``ANTHROPIC_API_KEY``. Model:
  ``BR_AGENT_MODEL``.

Selection: ``BR_AGENT_PROVIDER`` if set, else ``anthropic`` when a key is present,
else ``offline``. ``BR_OFFLINE=1`` always forces ``offline``.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import requests

DEFAULT_MODEL = "claude-sonnet-5-5"
API_URL = "https://api.anthropic.com/v1/messages"
TIMEOUT = (10, 180)


class LLMError(RuntimeError):
    """The provider answered, but not with usable JSON."""


@dataclass
class OfflineLLM:
    """Provider that never answers; agents fall back to deterministic logic."""

    name: str = "offline"

    def available(self) -> bool:
        """Offline never answers."""
        return False

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        """Always ``None``."""
        return None


@dataclass
class AnthropicLLM:
    """Anthropic Messages API provider."""

    api_key: str
    model: str = DEFAULT_MODEL
    name: str = "anthropic"

    def available(self) -> bool:
        """True when a key is configured."""
        return bool(self.api_key)

    def complete_json(self, system: str, prompt: str, max_tokens: int = 4000) -> dict | None:
        """Ask for a JSON object and parse the first one in the reply.

        Raises:
            LLMError: On an HTTP error or a reply with no parseable JSON object.
        """
        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system + "\nReply with a single JSON object and nothing else.",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            raise LLMError(f"Anthropic API returned {resp.status_code}: {resp.text[:300]}")
        text = "".join(b.get("text", "") for b in resp.json().get("content", []) if b.get("type") == "text")
        return extract_json(text)


def extract_json(text: str) -> dict:
    """Parse the first JSON object in ``text`` (tolerates ```json fences).

    Raises:
        LLMError: When no JSON object can be parsed.
    """
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]
    try:
        value = json.loads(candidate)
    except (json.JSONDecodeError, ValueError) as exc:
        raise LLMError(f"no JSON object in model reply: {text[:200]!r}") from exc
    if not isinstance(value, dict):
        raise LLMError("model reply JSON is not an object")
    return value


def get_llm(provider: str | None = None) -> OfflineLLM | AnthropicLLM:
    """Return the configured provider (see module docstring)."""
    if os.environ.get("BR_OFFLINE") == "1":
        return OfflineLLM()
    choice = (provider or os.environ.get("BR_AGENT_PROVIDER") or "").strip().lower()
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if choice == "offline" or (not choice and not key):
        return OfflineLLM()
    if choice in ("", "anthropic"):
        if not key:
            raise LLMError("BR_AGENT_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set")
        return AnthropicLLM(api_key=key, model=os.environ.get("BR_AGENT_MODEL", DEFAULT_MODEL))
    raise LLMError(f"unknown provider {choice!r} (use 'offline' or 'anthropic')")
