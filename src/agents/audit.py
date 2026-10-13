"""Tamper-evident decision log of the self-healing agent (D-71).

One append-only JSONL file per run, ``logs/agent/<run_id>.jsonl``, one record per step:

    {"v": 1, "run_id", "seq", "ts", "actor": "system|model|human",
     "stage": "detect|triage|localize|retrieve|patch|verify|retry|approve|git|pr|finish",
     "action", "decision": "accept|reject|retry|skip|wait|done", "reason", "evidence": {...},
     "model": {"provider", "model", "prompt_sha256", "reply_sha256", "tokens_in", "tokens_out", "cost_usd",
               "cache_hit"} | null,
     "artifacts": {"patch_sha256", "diff_path", "branch", "commit", "pr_url"} | null,
     "prev_hash", "hash"}

``hash`` is the sha256 of the record's canonical JSON without ``hash``; ``prev_hash`` is the previous record's hash
(64 zeros for the first). ``reason`` is one sentence composed by code, never model prose. Full prompts, replies,
reasoning and diffs go in ``logs/agent/<run_id>/`` (gitignored); records carry their sha256 only.

Any value of a credential-named environment variable (``*KEY*``, ``*TOKEN*``, ``*SECRET*``, ``*PAT*``,
``*PASSWORD*``) is replaced by ``[redacted]`` before a record or an artifact is written.

    python -m src.agents.audit verify <run_id|path>     # exit 0 when the chain verifies
    python -m src.agents.audit show <run_id|path>       # readable trail
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / "logs" / "agent"
GENESIS = "0" * 64
ACTORS = ("system", "model", "human")
STAGES = ("detect", "triage", "localize", "retrieve", "patch", "verify", "retry", "approve", "git", "pr", "finish")
DECISIONS = ("accept", "reject", "retry", "skip", "wait", "done")
KEYS = ("v", "run_id", "seq", "ts", "actor", "stage", "action", "decision", "reason", "evidence", "model", "artifacts",
        "prev_hash", "hash")
MODEL_KEYS = ("provider", "model", "prompt_sha256", "reply_sha256", "tokens_in", "tokens_out", "cost_usd", "cache_hit")
ARTIFACT_KEYS = ("patch_sha256", "diff_path", "branch", "commit", "pr_url")
_SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|(^|_)PAT(_|$)|PASSWORD", re.I)
_RUN_ID = re.compile(r"[\w.-]{1,120}")
MAX_REASON = 300


def sha256(text: str | bytes) -> str:
    """Hex sha256 of text (UTF-8) or bytes."""
    return hashlib.sha256(text.encode("utf-8") if isinstance(text, str) else text).hexdigest()


def canonical(rec: dict) -> str:
    """The canonical JSON the hash is taken over: sorted keys, no whitespace, UTF-8 kept."""
    return json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_hash(rec: dict) -> str:
    """sha256 of the record without its ``hash`` field."""
    return sha256(canonical({k: v for k, v in rec.items() if k != "hash"}))


def secret_values(env: dict[str, str] | None = None) -> list[str]:
    """Values of credential-named environment variables (8+ characters), longest first."""
    env = os.environ if env is None else env
    vals = {v for k, v in env.items() if _SECRET_NAME.search(k) and v and len(v) >= 8}
    return sorted(vals, key=len, reverse=True)


def redact(text: str, secrets: list[str] | None = None) -> str:
    """`text` with every credential value replaced by ``[redacted]``."""
    for v in secret_values() if secrets is None else secrets:
        text = text.replace(v, "[redacted]")
    return text


def one_sentence(text: str) -> str:
    """Collapse whitespace, cap the length, and end with a full stop."""
    s = re.sub(r"\s+", " ", str(text)).strip()
    if len(s) > MAX_REASON:
        s = s[: MAX_REASON - 1].rstrip() + "…"
    return s if s.endswith((".", "…", "?", "!")) else s + "."


def log_path(run_id: str, root: Path = LOG_ROOT) -> Path:
    """``<root>/<run_id>.jsonl``; a path to an existing file is accepted as is."""
    p = Path(run_id)
    if p.suffix == ".jsonl" and p.exists():
        return p
    if not _RUN_ID.fullmatch(run_id):
        raise ValueError(f"bad run id {run_id!r}")
    return Path(root) / f"{run_id}.jsonl"


class DecisionLog:
    """Appends hash-chained records for one run; continues an existing file's chain."""

    def __init__(self, run_id: str, root: Path = LOG_ROOT, on_record=None) -> None:
        self.on_record = on_record
        if not _RUN_ID.fullmatch(run_id):
            raise ValueError(f"bad run id {run_id!r}")
        self.run_id, self.root = run_id, Path(root)
        self.path = self.root / f"{run_id}.jsonl"
        self.dir = self.root / run_id
        self.seq, self.prev = 0, GENESIS
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.seq, self.prev = r["seq"], r["hash"]
        self._secrets = secret_values()
        self.records: list[dict] = []

    # -- side files ----------------------------------------------------------------------------
    def store(self, name: str, text: str) -> tuple[str, str]:
        """Write a full prompt / reply / diff to the per-run folder.

        Returns:
            `(sha256 of the redacted text, path relative to the repository root when possible)`.
        """
        if not re.fullmatch(r"[\w.-]{1,120}", name):
            raise ValueError(f"bad artifact name {name!r}")
        body = redact(text, self._secrets)
        self.dir.mkdir(parents=True, exist_ok=True)
        p = self.dir / name
        p.write_text(body, encoding="utf-8")
        try:
            rel = str(p.resolve().relative_to(ROOT))
        except ValueError:
            rel = str(p)
        return sha256(body), rel

    def model_block(self, *, provider: str, model: str, prompt: str, reply: str, tokens_in: int | None,
                    tokens_out: int | None, cost_usd: float | None, cache_hit: bool, tag: str,
                    reasoning: str = "") -> dict:
        """Store prompt, reply (and reasoning) under `tag` and return the record's ``model`` block (hashes only)."""
        ph, _ = self.store(f"{tag}.prompt.txt", prompt)
        rh, _ = self.store(f"{tag}.reply.txt", reply)
        if reasoning:
            self.store(f"{tag}.reasoning.txt", reasoning)
        return {"provider": provider, "model": model, "prompt_sha256": ph, "reply_sha256": rh,
                "tokens_in": tokens_in, "tokens_out": tokens_out, "cost_usd": cost_usd, "cache_hit": bool(cache_hit)}

    # -- records -------------------------------------------------------------------------------
    def record(self, actor: str, stage: str, action: str, decision: str, reason: str, evidence: dict | None = None,
               model: dict | None = None, artifacts: dict | None = None, ts: str | None = None) -> dict:
        """Append one record and return it.

        Raises:
            ValueError: An actor, stage or decision outside the schema.
        """
        if actor not in ACTORS or stage not in STAGES or decision not in DECISIONS:
            raise ValueError(f"record outside the schema: actor={actor} stage={stage} decision={decision}")
        if model is not None:
            model = {k: model.get(k) for k in MODEL_KEYS}
        if artifacts is not None:
            artifacts = {k: artifacts.get(k) for k in ARTIFACT_KEYS}
        rec = {"v": 1, "run_id": self.run_id, "seq": self.seq + 1,
               "ts": ts or datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
               "actor": actor, "stage": stage, "action": str(action), "decision": decision,
               "reason": one_sentence(reason), "evidence": evidence or {}, "model": model, "artifacts": artifacts,
               "prev_hash": self.prev}
        # redact on the serialised form so a credential cannot hide in any nested value
        rec = json.loads(redact(json.dumps(rec, ensure_ascii=False), self._secrets))
        rec["hash"] = record_hash(rec)
        self.root.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(canonical(rec) + "\n")
        self.seq, self.prev = rec["seq"], rec["hash"]
        self.records.append(rec)
        if self.on_record is not None:
            self.on_record(rec)
        return rec


class EventAuditor:
    """Turns the bot's stage events (`run_bot(on_event=...)`) into decision records.

    The mapping is fixed: ``tests.done`` -> detect, ``triage.result`` -> triage, ``localize.result`` -> localize,
    ``repair.chunks`` -> retrieve, each model call -> patch (actor model), ``repair.blocks`` -> patch,
    ``validate.check`` -> verify, a further attempt -> retry, ``validate.verdict`` -> verify, ``report.comment`` ->
    finish. Every reason is a template filled with numbers and names from the event, never model text.
    """

    def __init__(self, log: DecisionLog) -> None:
        self.log = log
        self.attempt = 0
        self.failed_checks: dict[int, list[str]] = {}
        self.max_attempts = 3

    def model_call(self, attempt: int, system: str, prompt: str, res, inner) -> dict:
        """Record one model call (prompt and reply stored, hashes logged)."""
        usage = res.usage or {}
        provider = res.provider or getattr(inner, "last_provider", None) or getattr(inner, "name", "unknown")
        model_id = (inner.model_id(provider) if hasattr(inner, "model_id") else getattr(inner, "model", res.model))
        tin = usage.get("prompt_tokens", usage.get("inputTokens"))
        tout = usage.get("completion_tokens", usage.get("outputTokens"))
        cost = usage.get("cost_usd")
        if cost is None and provider == "groq":
            cost = 0.0                                   # free tier (D-58)
        block = self.log.model_block(provider=provider, model=model_id, prompt=system + "\n\n" + prompt,
                                     reply=res.text, tokens_in=tin, tokens_out=tout, cost_usd=cost,
                                     cache_hit=res.from_cache, tag=f"attempt{attempt}",
                                     reasoning=getattr(inner, "last_reasoning", "") or "")
        fb = getattr(inner, "fallback_reason", None)
        ev = {"attempt": attempt, "reply_chars": len(res.text), "from_cache": bool(res.from_cache)}
        if fb:
            ev["fallback_reason"] = fb
        reason = (f"Attempt {attempt}: {model_id} via {provider} returned {len(res.text)} characters"
                  + (" from the cache" if res.from_cache else "") + (f" after a fallback ({fb})" if fb else ""))
        return self.log.record("model", "patch", "propose_patch", "accept" if res.text.strip() else "reject", reason,
                               ev, model=block)

    def on_event(self, stage: str, type_: str, status: str, data: dict) -> None:
        """Map one bot event to zero or more records."""
        L = self.log
        if type_ == "tests.done":
            c = data.get("counts") or {}
            nf = int(c.get("failed", 0)) + int(c.get("error", 0))
            pos = data.get("first_failure_position")
            L.record("system", "detect", "run_suite_risk_first", "accept" if nf else "done",
                     (f"The risk-first suite run had {nf} failing case(s) of {c.get('total', '?')}; the first failure "
                      f"was case {pos}" if nf else f"The risk-first suite run passed all {c.get('total', '?')} cases")
                     + (" and the run timed out" if data.get("timed_out") else ""),
                     {"counts": c, "first_failure_position": pos, "first_failure_test": data.get("first_failure_test"),
                      "wall_s": data.get("wall_s"), "timed_out": data.get("timed_out")})
        elif type_ == "triage.result":
            cnt = data.get("counts") or {}
            rows = [{"test": r.get("test"), "class": r.get("class"), "confidence": r.get("confidence")}
                    for r in (data.get("rows") or [])][:20]
            if status == "skipped":
                L.record("system", "triage", "triage_failures", "skip", "No test failed, so nothing was triaged", {})
            else:
                L.record("system", "triage", "triage_failures", "accept" if cnt.get("mine") else "skip",
                         f"Triage: {cnt.get('mine', 0)} mine, {cnt.get('inherited', 0)} inherited, "
                         f"{cnt.get('flaky', 0)} flaky; repair runs only on mine",
                         {"counts": cnt, "rows": rows, "base_command": data.get("base_command")})
        elif type_ == "localize.result":
            top = (data.get("ranked") or [])[:5]
            first = top[0] if top else {}
            L.record("system", "localize", "graph_localize", "accept" if top else "skip",
                     (f"Graph localisation ranked {len(data.get('ranked') or [])} function(s); top is "
                      f"{first.get('node')} at {first.get('hops')} hop(s) from a failing test" if top else
                      "Graph localisation found no candidate function"),
                     {"ranked": top, "paths": (data.get("paths") or [])[:5], "signals": data.get("signals")})
        elif type_ == "repair.chunks":
            ch = data.get("chunks") or []
            L.record("system", "retrieve", "select_context", "accept" if ch else "skip",
                     f"Selected {len(ch)} code chunk(s) as repair context"
                     + (f" ({data.get('context')})" if data.get("context") else ""),
                     {"chunks": [{k: c.get(k) for k in ("file", "qualname", "start", "end", "rank")} for c in ch][:10]})
        elif type_ == "repair.request":
            a = int(data.get("attempt") or 1)
            if a > 1:
                bad = self.failed_checks.get(a - 1) or ["apply"]
                L.record("system", "retry", "retry_with_feedback", "retry",
                         f"Attempt {a - 1} failed {', '.join(bad)}; retrying with that output as feedback "
                         f"(attempt {a} of {self.max_attempts})", {"attempt": a, "failed": bad})
            self.attempt = a
        elif type_ == "repair.blocks":
            a = int(data.get("attempt") or self.attempt)
            files = data.get("files") or sorted({b.get("path") for b in data.get("blocks") or []})
            if status == "failed":
                self.failed_checks.setdefault(a, []).append("applies")
                L.record("system", "patch", "apply_blocks", "reject",
                         f"Attempt {a}: the reply's edit blocks did not apply to the head tree",
                         {"attempt": a, "files": files, "error_sha256": sha256(str(data.get("error", "")))})
            else:
                L.record("system", "patch", "apply_blocks", "accept",
                         f"Attempt {a}: {len(data.get('blocks') or [])} edit block(s) applied to {len(files)} file(s)",
                         {"attempt": a, "files": files})
        elif type_ == "validate.check" and status in ("ok", "failed", "skipped"):
            a = int(data.get("attempt") or self.attempt)
            name = str(data.get("name"))
            if status == "failed" and name != "applies":
                self.failed_checks.setdefault(a, []).append(name)
            if name == "applies" and status == "failed":
                return                                     # already recorded by repair.blocks
            dec = {"ok": "accept", "failed": "reject", "skipped": "skip"}[status]
            L.record("system", "verify", f"check_{name}", dec,
                     f"Attempt {a}: check '{name}' " + {"accept": "passed", "reject": "failed", "skip": "was skipped"}[dec],
                     {"attempt": a, "check": name, "evidence": str(data.get("evidence", ""))[:300]})
        elif type_ == "repair.patch":
            diff = data.get("diff") or ""
            if diff:
                h, path = L.store("patch.diff", diff)
                L.record("system", "patch", "final_patch", "accept" if status == "ok" else "reject",
                         f"The last applicable patch touches {len(data.get('files') or [])} file(s) after "
                         f"{data.get('attempts')} attempt(s)", {"attempts": data.get("attempts"),
                                                                "files": [f.get("path") for f in data.get("files") or []]},
                         artifacts={"patch_sha256": h, "diff_path": path})
        elif type_ == "validate.verdict":
            ok = bool(data.get("accepted"))
            L.record("system", "verify", "verdict", "accept" if ok else "reject",
                     ("The patch passed every check" if ok else "No patch passed every check")
                     + f" after {data.get('attempts')} attempt(s)", {"accepted": ok, "attempts": data.get("attempts")})
        elif type_ == "repair.skipped":
            L.record("system", "patch", "repair", "skip", f"Repair skipped: {str(data.get('reason', ''))[:160]}",
                     {"mine": data.get("mine")})
        elif type_ == "repair.unavailable":
            L.record("system", "patch", "call_model", "reject",
                     f"The model could not be used ({data.get('kind')})", {"kind": data.get("kind")})
        elif type_ == "report.comment":
            h, path = L.store("comment.md", str(data.get("comment", "")))
            L.record("system", "finish", "render_comment", "done",
                     "Rendered the PR comment" + (" with a validated suggestion" if data.get("validated") else
                                                  " without a validated patch"),
                     {"validated": bool(data.get("validated")), "comment_sha256": h})


def read(path: Path) -> list[dict]:
    """Records of a log file, in file order."""
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def verify_lines(lines: list[str]) -> tuple[bool, list[str]]:
    """Check schema, sequence, hashes and the chain of raw JSONL lines.

    Returns:
        `(ok, problems)`; a line that is not JSON is a problem, not an exception.
    """
    problems: list[str] = []
    prev, run = GENESIS, None
    n = 0
    for i, ln in enumerate(lines, 1):
        if not ln.strip():
            continue
        n += 1
        try:
            r = json.loads(ln)
        except json.JSONDecodeError as exc:
            problems.append(f"line {i}: not JSON ({exc.msg})")
            prev = None
            continue
        if sorted(r) != sorted(KEYS):
            problems.append(f"line {i}: keys differ from the schema")
        if r.get("v") != 1:
            problems.append(f"line {i}: v is not 1")
        if r.get("seq") != n:
            problems.append(f"line {i}: seq {r.get('seq')} != {n}")
        run = run or r.get("run_id")
        if r.get("run_id") != run:
            problems.append(f"line {i}: run_id changed")
        if r.get("actor") not in ACTORS or r.get("stage") not in STAGES or r.get("decision") not in DECISIONS:
            problems.append(f"line {i}: actor/stage/decision outside the schema")
        if prev is not None and r.get("prev_hash") != prev:
            problems.append(f"line {i}: prev_hash does not chain")
        if record_hash(r) != r.get("hash"):
            problems.append(f"line {i}: hash mismatch")
        prev = r.get("hash")
    if n == 0:
        problems.append("empty log")
    return not problems, problems


def verify(run_id: str, root: Path = LOG_ROOT) -> tuple[bool, list[str], int]:
    """Verify a run's log file. Returns `(ok, problems, number of records)`."""
    p = log_path(run_id, root)
    if not p.exists():
        return False, [f"{p} does not exist"], 0
    lines = p.read_text(encoding="utf-8").splitlines()
    ok, problems = verify_lines(lines)
    return ok, problems, sum(1 for ln in lines if ln.strip())


def render(records: list[dict]) -> str:
    """A readable trail: one block per record."""
    out = []
    for r in records:
        m = r.get("model") or {}
        a = r.get("artifacts") or {}
        head = f"#{r['seq']:>3} {r['ts']}  {r['actor']:<6} {r['stage']:<8} {r['action']:<22} -> {r['decision'].upper()}"
        out.append(head)
        out.append(f"      {r['reason']}")
        if r.get("evidence"):
            ev = json.dumps(r["evidence"], ensure_ascii=False, sort_keys=True)
            out.append(f"      evidence: {ev if len(ev) <= 400 else ev[:399] + '…'}")
        if m:
            cost = "n/a" if m.get("cost_usd") is None else f"USD {m['cost_usd']:.6f}"
            out.append(f"      model: {m.get('provider')}/{m.get('model')} in={m.get('tokens_in')} out={m.get('tokens_out')} "
                       f"{cost} cache_hit={m.get('cache_hit')} prompt={str(m.get('prompt_sha256'))[:12]} "
                       f"reply={str(m.get('reply_sha256'))[:12]}")
        if a and any(a.values()):
            out.append("      artifacts: " + ", ".join(f"{k}={v}" for k, v in a.items() if v))
        out.append(f"      hash {r['hash'][:16]} <- {r['prev_hash'][:16]}")
    return "\n".join(out)


def summary(records: list[dict]) -> dict:
    """Counts per stage and decision, total model cost, and the head hash (for a PR body)."""
    stages: dict[str, int] = {}
    decisions: dict[str, int] = {}
    cost = 0.0
    for r in records:
        stages[r["stage"]] = stages.get(r["stage"], 0) + 1
        decisions[r["decision"]] = decisions.get(r["decision"], 0) + 1
        cost += float((r.get("model") or {}).get("cost_usd") or 0.0)
    return {"records": len(records), "stages": stages, "decisions": decisions, "cost_usd": round(cost, 6),
            "head_hash": records[-1]["hash"] if records else None}


def main(argv: list[str] | None = None) -> int:
    """CLI: ``verify`` and ``show``."""
    ap = argparse.ArgumentParser(prog="python -m src.agents.audit")
    ap.add_argument("cmd", choices=("verify", "show"))
    ap.add_argument("run")
    ap.add_argument("--root", default=str(LOG_ROOT))
    ns = ap.parse_args(argv)
    if ns.cmd == "verify":
        ok, problems, n = verify(ns.run, Path(ns.root))
        if ok:
            recs = read(log_path(ns.run, Path(ns.root)))
            print(f"OK {log_path(ns.run, Path(ns.root)).name}: {n} records, chain intact, head {recs[-1]['hash']}")
            return 0
        print(f"FAIL {ns.run}: " + "; ".join(problems[:20]))
        return 1
    p = log_path(ns.run, Path(ns.root))
    if not p.exists():
        print(f"{p} does not exist", file=sys.stderr)
        return 1
    print(render(read(p)))
    ok, problems, _ = verify(ns.run, Path(ns.root))
    print("\nchain: " + ("OK" if ok else "BROKEN: " + "; ".join(problems[:5])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
