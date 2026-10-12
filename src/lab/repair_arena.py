"""Repair arena (Live Lab, optional, one extra model call): the same failure handled three ways.

    R1    log-only input (failing test ids and output; the inputs LogSage and CI-Bench give a model), validated with
          the same five checks as ours
    R2    change-aware input (ours): read from the run's own repair stage, which uses R2's prompt and, as the PR bot
          does, allows up to two retries with feedback (R3)
    push  what an agent that pushes its fix without full-suite validation would ship: the R1 patch, and what the full
          suite actually says about it

The R1 call goes through the lab's model client (its cache and its ledger, `eval/llm_cache/lab_usage.jsonl`).
"""

from __future__ import annotations

from pathlib import Path

from src.agents import gitops
from src.agents.bot import apply_blocks_tolerant, unified
from src.agents.regression import run_pytest
from src.agents.repair import FailureReport, RepairAgent, select_chunks
from src.eval.seeded.build import source_files
from src.parse.changeset import is_conventional_test_file

R1_INPUT = "failing test ids and their output only, as LogSage and CI-Bench give the model"
R2_INPUT = "the functions the diff touches, ranked against the failure output; triage class stated (ours)"
PUSH_INPUT = "the R1 patch pushed as soon as it applies, with no full-suite run (the behaviour GitHub's announcement describes)"


def r2_column(history: list[dict]) -> dict:
    """The run's own repair stage (R2's prompt, R3's retries) as an arena column, read from its events."""
    ev = lambda t: [e for e in history if e["type"] == t]                          # noqa: E731
    chunks = (ev("repair.chunks") or [{"data": {"chunks": []}}])[-1]["data"]["chunks"]
    replies = ev("repair.reply")
    attempts = max([e["data"].get("attempt", 1) for e in ev("validate.check")] + [len(replies), 1])
    checks = {}
    for e in ev("validate.check"):
        if e["data"].get("attempt") == attempts and e["status"] != "running":
            checks[e["data"]["name"]] = {"name": e["data"]["name"], "ok": e["data"]["ok"], "evidence": e["data"]["evidence"]}
    verdict = (ev("validate.verdict") or [{"data": {}}])[-1]["data"]
    patch = (ev("repair.patch") or [{"data": {}}])[-1]["data"]
    tokens = sum(int((e["data"].get("usage") or {}).get("total_tokens", 0)) for e in replies)
    return {"id": "R2", "title": "R2 · change-aware (ours)", "input": R2_INPUT,
            "chunks": [{"file": c["file"], "qualname": c["qualname"]} for c in chunks], "tokens": tokens,
            "from_cache": all(e["data"].get("from_cache") for e in replies) if replies else None,
            "diff": patch.get("diff", ""), "accepted": bool(verdict.get("accepted")), "checks": list(checks.values()),
            "note": ("accepted: the full suite passed" if verdict.get("accepted") else "not accepted")
                    + (f" (attempt {attempts} of up to 3)" if attempts > 1 else "")}


def run_r1(repo: Path, base: str, head: str, mine: list[dict], llm, python: str | None, state: Path,
           timeout: float | None, others: set[str] | None = None) -> tuple[dict, dict]:
    """One R1 call on `mine` failures, validated with the five checks; returns the R1 and the push columns.

    `others` are failing ids that are not this change's (inherited or flaky): excluded from the full-suite verdict,
    exactly as the run's own validation excludes them.
    """
    others = others or set()
    fr = FailureReport(failing=[{"test_id": m["test"], "output": m.get("message", "")} for m in mine],
                       pr_diff=gitops.diff_text(repo, base, head, max_chars=10 ** 7), triage="mine",
                       changed_files=gitops.changed_files(repo, base, head))
    ids = [m["test"] for m in mine]
    record: dict = {"checks": [], "full": None}
    tmo = {"timeout": timeout} if timeout else {}
    with gitops.worktree(repo, head) as tree:
        dirs = sorted({p.split("/")[0] for p in gitops.tracked_files(tree) if p.endswith(".py") and not is_conventional_test_file(p)})
        srcs = source_files(tree, {"src_dirs": dirs})
        chunks = select_chunks("R1", tree, srcs, fr)
        allowed = {c.file for c in chunks} | set(fr.changed_files)
        head_text: dict[str, str] = {}

        def check(name: str, ok: bool | None, evidence: str) -> None:
            record["checks"].append({"name": name, "ok": ok, "evidence": evidence})

        def validate(files: dict[str, str]) -> tuple[bool, str]:
            before = {p: (tree / p).read_text(encoding="utf-8") for p in files}
            head_text.update(before)
            check("applies", True, f"{len(files)} file(s) patched")
            errors = []
            for p, text in files.items():
                if p.endswith(".py"):
                    try:
                        compile(text, p, "exec")
                    except SyntaxError as exc:
                        errors.append(f"{p}:{exc.lineno}: {exc.msg}")
            check("syntax", not errors, "; ".join(errors) or "compiles")
            if errors:
                record["full"] = {"ran": False, "reason": "the patch does not compile"}
                return False, "; ".join(errors)
            try:
                for p, text in files.items():
                    (tree / p).write_text(text, encoding="utf-8")
                tfiles = sorted({t.split("::")[0] for t in ids if (tree / t.split("::")[0]).is_file()})
                trun = run_pytest(tree, tfiles, state / "reports" / "arena-r1-targeted.xml", "targeted", python, **tmo)
                still = sorted({r.test_id for r in trun.failed} & set(ids))
                check("targeted", not still and not trun.timed_out, f"{len(ids) - len(still)}/{len(ids)} previously failing ids pass")
                run = run_pytest(tree, None, state / "reports" / "arena-r1-full.xml", "full", python, **tmo)
            finally:
                for p, text in before.items():
                    (tree / p).write_text(text, encoding="utf-8")
            c = run.counts()
            full_ok = not ({r.test_id for r in run.failed} - others) and run.exit_code in (0, 1) and not run.timed_out
            record["full"] = {"ran": True, "ok": full_ok, **c}
            check("full", full_ok, f"{c['passed']} passed, {c['failed']} failed, {c['error']} errors of {c['total']} cases")
            outside = sorted(set(files) - allowed)
            check("scope", not outside, "edits outside the shown files: " + ", ".join(outside) if outside else "in scope")
            return full_ok and not still and not outside, ""

        res = RepairAgent(llm, "R1", max_retries=0, applier=apply_blocks_tolerant).run(tree, srcs, fr, validate)
    att = res.attempts[0] if res.attempts else None
    usage = (att.usage or {}) if att else {}
    if att and not att.applied:
        record["checks"].append({"name": "applies", "ok": False, "evidence": att.error[:300]})
    diff = unified(head_text, att.files) if att and att.applied else ""
    r1 = {"id": "R1", "title": "R1 · log-only", "input": R1_INPUT,
          "chunks": [{"file": c.file, "qualname": c.qualname} for c in res.chunks],
          "tokens": int(usage.get("total_tokens", 0)) if att else 0, "from_cache": att.from_cache if att else None,
          "diff": diff, "accepted": res.accepted, "checks": record["checks"],
          "note": "accepted: the full suite passed" if res.accepted else
                  ("the reply could not be applied" if att and not att.applied else "not accepted")}
    full = record["full"]
    if not diff:
        push_note, push_ok, checks = "nothing to push: the R1 reply could not be applied", None, []
    elif full and full.get("ran"):
        push_ok = bool(full["ok"])
        push_note = ("pushed, and the full suite does pass with it" if push_ok else
                     f"pushed, but the full suite fails with it: {full['failed']} failed, {full['error']} errors of {full['total']}")
        checks = [{"name": "applies", "ok": True, "evidence": "applied, then pushed without a suite run"},
                  {"name": "full", "ok": push_ok, "evidence": f"measured afterwards in this run: {full['passed']} passed, {full['failed']} failed"}]
    else:
        push_note, push_ok = "pushed, but it does not even compile", False
        checks = [{"name": "applies", "ok": True, "evidence": "applied, then pushed"}, {"name": "syntax", "ok": False, "evidence": full.get("reason", "") if full else ""}]
    push = {"id": "push", "title": "Push without full-suite validation", "input": PUSH_INPUT, "chunks": [], "tokens": None,
            "from_cache": None, "diff": diff, "accepted": push_ok, "checks": checks, "note": push_note}
    return r1, push
