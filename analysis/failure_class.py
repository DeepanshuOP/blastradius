"""Classify a test failure message as environment, code-level or unknown.

Measurement and display only: nothing here changes a label. The patterns are a
fixed, ordered, case-insensitive list (no model, no randomness), shared by
`analysis/demo_walkthrough.py` (selection preference) and
`analysis/infra_failure_audit.py` (the audit).

Order of decision:
  1. the message STARTS with an assertion marker  -> code-level (an assertion
     whose compared text happens to mention a timeout or a host is still an
     assertion);
  2. any ENVIRONMENT pattern matches anywhere     -> environment;
  3. any CODE pattern matches anywhere            -> code-level;
  4. otherwise (including an empty message)       -> unknown.
"""

from __future__ import annotations

import re

ENVIRONMENT = "environment"
CODE = "code-level"
UNKNOWN = "unknown"

#: (name, regex) pairs. Environment: GPU/CUDA unavailable, out-of-memory,
#: timeouts, connection/DNS errors, a missing service.
ENVIRONMENT_PATTERNS: tuple[tuple[str, str], ...] = (
    ("cuda-gpu-unavailable",
     r"no cuda gpus|cuda (error|driver|runtime)|cuda.{0,30}(not available|unavailable)"
     r"|(no|without) gpu|gpu.{0,30}(not available|unavailable)|torch\.cuda|nvidia-smi"),
    ("out-of-memory", r"out ?of ?memory|outofmemoryerror|\bMemoryError\b|\boom\b|cannot allocate memory"),
    ("timeout", r"timeouterror|timed? ?out|\btimeout\b|deadline exceeded"),
    ("connection-error",
     r"connectionerror|connection (refused|reset|aborted|closed)|connectexception"
     r"|sockettimeout|ssl(error|handshake)|network is unreachable|broken pipe"
     r"|failed to connect|could not connect|http response code: (429|5\d\d)"),
    ("dns-error",
     r"unknownhostexception|name or service not known|temporary failure in name resolution"
     r"|getaddrinfo|nodename nor servname|no such host"),
    ("missing-service",
     r"service (is )?(not available|unavailable)|serviceunavailable|docker.{0,40}(not running|daemon)"
     r"|cannot connect to the docker|no such container|testcontainers|can.t get docker image"),
)

#: Code-level: an assertion, or an expected-vs-actual comparison.
CODE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("assertion", r"assertionerror|\bassert\b|assertion failed|assertionfailed|expectation failed"),
    ("expected-vs-actual",
     r"expected:?\s*<?\[?.{0,200}?\s(but was|but got|actual)|expected.{0,80}\bbut\b.{0,40}\b(was|got|found)\b"
     r"|did not expect|not equal to|should (be|not)|to be thrown|no exception was thrown"),
)

#: Rule 1: only these, and only at the very start of the message.
_LEADING_ASSERTION = re.compile(
    r"^\W*(assertionerror|assert\b|expected\b|\d+ expectations? failed|.{0,120}==> expected)", re.I
)

_ENV = [(n, re.compile(p, re.I | re.S)) for n, p in ENVIRONMENT_PATTERNS]
_CODE = [(n, re.compile(p, re.I | re.S)) for n, p in CODE_PATTERNS]


def classify(message: str | None) -> tuple[str, str]:
    """Classify one failure message.

    Args:
        message: The parsed `failure_message` (None or empty means no evidence).

    Returns:
        `(class, rule)` where class is one of ENVIRONMENT / CODE / UNKNOWN and
        rule names the pattern (or `leading-assertion`, or `no-match`/`empty`).
    """
    if not isinstance(message, str) or not message.strip():
        return UNKNOWN, "empty"
    if _LEADING_ASSERTION.search(message):
        return CODE, "leading-assertion"
    for name, rx in _ENV:
        if rx.search(message):
            return ENVIRONMENT, name
    for name, rx in _CODE:
        if rx.search(message):
            return CODE, name
    return UNKNOWN, "no-match"


def pattern_listing() -> list[str]:
    """Human-readable list of every rule, in decision order (for the audit)."""
    out = [f"1. leading-assertion (message start) -> {CODE}: `{_LEADING_ASSERTION.pattern}`"]
    out += [f"2. {n} -> {ENVIRONMENT}: `{p}`" for n, p in ENVIRONMENT_PATTERNS]
    out += [f"3. {n} -> {CODE}: `{p}`" for n, p in CODE_PATTERNS]
    out.append(f"4. no match, or empty message -> {UNKNOWN}")
    return out
