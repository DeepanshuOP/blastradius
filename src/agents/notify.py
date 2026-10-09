"""Notifications: always a local JSONL log + stderr; optionally a webhook.

``BR_NOTIFY_WEBHOOK`` may point at a Slack or Discord incoming webhook; the
payload carries both ``text`` (Slack) and ``content`` (Discord). ``BR_OFFLINE=1``
suppresses the webhook, never the local record.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


def notify(state_dir: Path, event: str, message: str, details: dict | None = None) -> dict:
    """Record a notification and deliver it on every configured channel.

    Args:
        state_dir: The agents' state directory; the log is ``notifications.jsonl``.
        event: Short machine name, e.g. ``build_failed``.
        message: One human sentence.
        details: Extra structured fields.

    Returns:
        The record written, including which channels were used.
    """
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
        "message": message,
        "details": details or {},
        "channels": ["log", "stderr"],
    }
    hook = os.environ.get("BR_NOTIFY_WEBHOOK", "")
    if hook and os.environ.get("BR_OFFLINE") != "1":
        try:
            r = requests.post(hook, json={"text": f"[BlastRadius] {message}", "content": f"[BlastRadius] {message}"}, timeout=(5, 15))
            record["channels"].append(f"webhook:{r.status_code}")
        except requests.RequestException as exc:  # a failed alert must not hide the failure itself
            record["channels"].append(f"webhook:error:{type(exc).__name__}")
    state_dir.mkdir(parents=True, exist_ok=True)
    with (state_dir / "notifications.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    print(f"[BlastRadius notification] {event}: {message}", file=sys.stderr)
    return record
