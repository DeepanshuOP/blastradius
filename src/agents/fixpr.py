"""Approval-gated fix PR (D-70): a validated patch becomes a PR on its own branch, never a push to anyone else's.

Gate modes (``BR_FIX_MODE``):

* ``suggest`` (default): nothing is pushed; the bot's PR comment carries the suggestion only.
* ``ask``: the fix PR is opened only after a human approval record exists in the run's decision log, written by the
  Live Lab "Approve fix" button (``approve``) or by a PR comment ``/blastradius apply`` from the repository owner
  (``wait``).
* ``auto``: opened without asking, but only for a repository in ``BR_FIX_ALLOWLIST``.

Whatever the mode, :func:`apply_fix` refuses (and logs the refusal) when the repository is not in the allowlist
(default ``DeepanshuOP/itsdangerous``), when any of the five checks or the fresh-worktree re-verification did not pass,
when the fix branch would be the default branch, ``main``/``master`` or the PR's own head branch, when the fix branch
already exists on the remote, or when no git identity is configured. It creates ``blastradius/fix-<short-sha>`` from
the PR head in a fresh worktree, commits as the configured git user, pushes that one ref without ``--force`` and opens
a PR against the failing PR's head branch with ``gh``. There is no code path that merges, force-pushes, or pushes to
an existing branch.

    python -m src.agents.fixpr approve --run RUN_ID --by NAME     # the lab button: record approval, then apply
    python -m src.agents.fixpr wait --run RUN_ID [--timeout 1800]   # poll the PR for "/blastradius apply" by the owner
    python -m src.agents.fixpr status --run RUN_ID
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from src.agents import audit as audit_mod
from src.agents.audit import DecisionLog, LOG_ROOT

MODES = ("suggest", "ask", "auto")
DEFAULT_ALLOWLIST = ("DeepanshuOP/itsdangerous",)
REQUIRED_CHECKS = ("applies", "syntax", "targeted", "full", "scope", "reverify_full", "reverify_scope")
APPLY_COMMAND = "/blastradius apply"
PROTECTED = ("main", "master")
PLAN_FILE = "fixplan.json"


class FixRefused(RuntimeError):
    """The gate refused; the reason is also in the decision log."""


def fix_mode(env: dict | None = None) -> str:
    """``BR_FIX_MODE``; anything unknown falls back to ``suggest``."""
    m = ((env or os.environ).get("BR_FIX_MODE") or "suggest").strip().lower()
    return m if m in MODES else "suggest"


def allowlist(env: dict | None = None) -> set[str]:
    """``BR_FIX_ALLOWLIST`` (comma separated ``owner/name``), default the operator's itsdangerous fork."""
    raw = (env or os.environ).get("BR_FIX_ALLOWLIST")
    items = [x.strip() for x in raw.split(",")] if raw is not None else list(DEFAULT_ALLOWLIST)
    return {x.lower() for x in items if x}


def branch_name(head_sha: str) -> str:
    """``blastradius/fix-<7-char sha>``."""
    return f"blastradius/fix-{head_sha[:7]}"


@dataclass
class FixPlan:
    """Everything needed to open the fix PR later (saved as ``logs/agent/<run>/fixplan.json``)."""

    repo_dir: str
    slug: str                       # owner/name on GitHub
    pr_number: int
    head_branch: str                # the failing PR's head branch (the fix PR's base)
    head_sha: str
    files: dict[str, str]           # path -> patched text
    checks: list[dict]              # [{"name", "ok", "evidence"}]
    patch_sha256: str
    remote: str = "origin"
    ranked: list[dict] = field(default_factory=list)      # [{"test", "score", "why"}]
    triage: list[dict] = field(default_factory=list)      # [{"test", "class", "confidence", "reason"}]
    evidence_path: list[dict] = field(default_factory=list)   # [{"node", "hops", "path"}]
    diff: str = ""

    def save(self, log: DecisionLog) -> Path:
        log.dir.mkdir(parents=True, exist_ok=True)
        p = log.dir / PLAN_FILE
        p.write_text(json.dumps(asdict(self), indent=1), encoding="utf-8")
        return p

    @staticmethod
    def load(log: DecisionLog) -> "FixPlan":
        return FixPlan(**json.loads((log.dir / PLAN_FILE).read_text(encoding="utf-8")))


def _git(repo: Path | str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=300)
    if check and r.returncode != 0:
        raise FixRefused(f"git {args[0]} failed: {r.stderr.strip()[:300]}")
    return r


def ensure_repo(plan: FixPlan, log: DecisionLog) -> Path:
    """The plan's repository; when its directory is gone (a Live Lab scratch copy), a clone of the allowlisted slug in
    the run's gitignored folder, with the PR head fetched."""
    repo = Path(plan.repo_dir)
    if (repo / ".git").exists() and _git(repo, "cat-file", "-e", plan.head_sha, check=False).returncode == 0:
        return repo
    dst = log.dir / "repo"
    if not (dst / ".git").exists():
        r = subprocess.run(["git", "clone", "--quiet", "--filter=blob:none", f"https://github.com/{plan.slug}.git", str(dst)],
                           capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise FixRefused(f"clone of {plan.slug} failed: {r.stderr.strip()[:200]}")
    _git(dst, "fetch", "--quiet", plan.remote, plan.head_sha, check=False)
    _git(dst, "fetch", "--quiet", plan.remote, f"refs/heads/{plan.head_branch}", check=False)
    plan.repo_dir = str(dst)
    return dst


def default_branch(repo: Path | str, remote: str = "origin") -> str:
    """The remote's default branch (its HEAD symref), falling back to the local symref, then ``main``."""
    r = _git(repo, "ls-remote", "--symref", remote, "HEAD", check=False)
    for ln in r.stdout.splitlines():
        if ln.startswith("ref: refs/heads/"):
            return ln.split()[1].removeprefix("refs/heads/")
    r = _git(repo, "symbolic-ref", "--short", f"refs/remotes/{remote}/HEAD", check=False)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().split("/", 1)[-1]
    return "main"


def remote_has_branch(repo: Path | str, remote: str, branch: str) -> bool:
    r = _git(repo, "ls-remote", "--heads", remote, f"refs/heads/{branch}", check=False)
    return bool(r.stdout.strip())


def approval_of(records: list[dict], patch_sha256: str) -> dict | None:
    """The human approval for this exact patch, if any (actor human, stage approve, decision accept)."""
    for r in records:
        if (r.get("actor") == "human" and r.get("stage") == "approve" and r.get("decision") == "accept"
                and (r.get("evidence") or {}).get("patch_sha256") == patch_sha256):
            return r
    return None


def record_approval(log: DecisionLog, by: str, source: str, patch_sha256: str, extra: dict | None = None) -> dict:
    """Write the human approval record."""
    return log.record("human", "approve", "approve_fix", "accept",
                      f"{by} approved opening the fix PR via {source}",
                      {"by": by, "source": source, "patch_sha256": patch_sha256, **(extra or {})})


def failed_checks(checks: list[dict]) -> list[str]:
    """Required checks that are missing or did not pass."""
    by = {c["name"]: c for c in checks}
    return [n for n in REQUIRED_CHECKS if not (by.get(n) or {}).get("ok")]


# ---- re-verification on a fresh worktree ---------------------------------------------------------
def reverify(repo_dir: Path | str, head_sha: str, files: dict[str, str], allowed: set[str], others: set[str],
             python: str | None = None, timeout: float | None = None) -> list[dict]:
    """Apply the patch to a fresh worktree of the PR head and run the FULL suite there, plus the scope check.

    Args:
        repo_dir: Repository holding `head_sha`.
        head_sha: PR head commit.
        files: Patched text per path.
        allowed: Paths the patch may touch (the changed files and the shown chunks).
        others: Test ids already failing on the base (excluded from the verdict).
        python: Interpreter for the target's suite.
        timeout: Seconds for the pytest process.

    Returns:
        ``[{"name": "reverify_full", ...}, {"name": "reverify_scope", ...}]``.
    """
    from src.agents import gitops
    from src.agents.regression import run_pytest

    out_dir = Path(tempfile.mkdtemp(prefix="br-reverify-"))
    try:
        with gitops.worktree(repo_dir, head_sha) as tree:
            for p, text in files.items():
                (tree / p).write_text(text, encoding="utf-8")
            run = run_pytest(tree, None, out_dir / "reverify.xml", "reverify", python,
                             **({"timeout": timeout} if timeout else {}))
            changed = set(_git(tree, "diff", "--name-only").stdout.split())
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
    bad = sorted({r.test_id for r in run.failed} - set(others))
    c = run.counts()
    full_ok = not bad and run.exit_code in (0, 1) and not run.timed_out
    outside = sorted(changed - set(allowed))
    return [{"name": "reverify_full", "ok": full_ok,
             "evidence": ("timed out" if run.timed_out else f"fresh worktree at {head_sha[:10]}: {c['passed']} passed, "
                          f"{c['failed']} failed, {c['error']} errors of {c['total']} cases")
             + (f"; still failing: {bad[0]}" if bad else "")},
            {"name": "reverify_scope", "ok": not outside and changed == set(files),
             "evidence": ("edits outside the changed or shown files: " + ", ".join(outside)) if outside
             else "git diff touches only " + ", ".join(sorted(changed))}]


# ---- the PR body ---------------------------------------------------------------------------------
def pr_body(plan: FixPlan, summary: dict, branch: str, mode: str, approver: str | None) -> str:
    """Markdown body: ranked tests, triage, graph evidence, check results, decision-log summary and hash."""
    L = [f"Automated fix for #{plan.pr_number} proposed by BlastRadius (mode `{mode}`"
         + (f", approved by @{approver}" if approver else "") + ").", "",
         f"Base of this PR: `{plan.head_branch}` (the failing PR's head). Branch: `{branch}`. "
         "BlastRadius never merges; review and merge it yourself, or close it.", "",
         "### Tests most at risk", ""]
    L += [f"{i}. `{r['test']}` ({float(r.get('score', 0)):.2f}) {r.get('why', '')}" for i, r in enumerate(plan.ranked[:5], 1)] or ["(none)"]
    L += ["", "### Triage", ""]
    L += [f"- `{t['test']}`: **{t['class']}** ({float(t.get('confidence', 0)):.2f}) {t.get('reason', '')}"
          for t in plan.triage[:10]] or ["(none)"]
    L += ["", "### Graph evidence", ""]
    L += [f"- `{e.get('node')}` at {e.get('hops')} hop(s): {' -> '.join(e.get('path') or [])}"
          for e in plan.evidence_path[:5]] or ["(no graph path recorded)"]
    L += ["", "### Checks", "", "| Check | Result | Evidence |", "|---|---|---|"]
    L += [f"| {c['name']} | {'pass' if c.get('ok') else 'FAIL'} | {str(c.get('evidence', '')).replace('|', '/')[:160]} |"
          for c in plan.checks]
    L += ["", "### Decision log", "",
          f"{summary.get('records')} records; stages {json.dumps(summary.get('stages'), sort_keys=True)}; "
          f"model cost USD {summary.get('cost_usd', 0):.6f}.", "",
          f"Audit hash (head of the chain before this PR): `{summary.get('head_hash')}`. "
          "Verify with `python -m src.agents.audit verify <run_id>`.", "",
          "<!-- blastradius-fix-pr -->"]
    return "\n".join(L) + "\n"


def gh_open_pr(slug: str, base: str, head: str, title: str, body: str) -> str:
    """`gh pr create`; returns the PR URL."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(body)
        path = fh.name
    try:
        r = subprocess.run(["gh", "pr", "create", "--repo", slug, "--base", base, "--head", head, "--title", title,
                            "--body-file", path], capture_output=True, text=True, timeout=120)
    finally:
        os.unlink(path)
    if r.returncode != 0:
        raise FixRefused(f"gh pr create failed: {r.stderr.strip()[:300]}")
    return r.stdout.strip().splitlines()[-1]


# ---- the gate and the action ---------------------------------------------------------------------
def apply_fix(plan: FixPlan, log: DecisionLog, *, mode: str | None = None, allow: set[str] | None = None,
              open_pr: Callable[[str, str, str, str, str], str] = gh_open_pr) -> dict:
    """Gate, then branch -> commit -> push -> PR. Every outcome is a decision record.

    Returns:
        ``{"status": "suggested|refused|waiting|opened", "reason", "branch", "commit", "pr_url"}``.
    """
    mode = mode or fix_mode()
    allow = allowlist() if allow is None else {a.lower() for a in allow}
    branch = branch_name(plan.head_sha)

    def refuse(reason: str, evidence: dict | None = None, stage: str = "pr") -> dict:
        log.record("system", stage, "gate", "reject", reason, {"mode": mode, "slug": plan.slug, **(evidence or {})})
        return {"status": "refused", "reason": reason, "branch": None, "commit": None, "pr_url": None}

    if mode == "suggest":
        log.record("system", "pr", "gate", "skip", "Fix mode is suggest, so the fix stays a suggestion and nothing is pushed",
                   {"mode": mode})
        return {"status": "suggested", "reason": "suggest mode", "branch": None, "commit": None, "pr_url": None}
    if plan.slug.lower() not in allow:
        return refuse(f"Repository {plan.slug} is not in BR_FIX_ALLOWLIST, so no branch is pushed",
                      {"allowlist": sorted(allow)})
    bad = failed_checks(plan.checks)
    if bad:
        return refuse(f"Check(s) {', '.join(bad)} did not pass, so no fix PR is opened", {"failed": bad})
    try:
        repo = ensure_repo(plan, log)
    except FixRefused as exc:
        return refuse(str(exc), stage="git")
    default = default_branch(repo, plan.remote)
    if plan.head_branch in PROTECTED or plan.head_branch == default:
        return refuse(f"The PR's head branch is {plan.head_branch}, the default or a protected branch; the fix PR "
                      "needs a feature branch as its base", {"head_branch": plan.head_branch, "default": default})
    if branch in PROTECTED or branch == default or branch == plan.head_branch or not branch.startswith("blastradius/fix-"):
        return refuse(f"The fix branch {branch} would be the default, a protected or the PR's own head branch",
                      {"branch": branch, "default": default})
    if mode == "ask":
        ok = approval_of(audit_mod.read(log.path) if log.path.exists() else [], plan.patch_sha256)
        if ok is None:
            log.record("system", "approve", "await_approval", "wait",
                       f"Ask mode: waiting for the repository owner to approve (Live Lab button or a PR comment "
                       f"'{APPLY_COMMAND}'); nothing is pushed until then", {"patch_sha256": plan.patch_sha256})
            return {"status": "waiting", "reason": "no approval record", "branch": None, "commit": None, "pr_url": None}
        approver = ok["evidence"].get("by")
    elif mode == "auto":
        log.record("system", "approve", "auto_approve", "accept",
                   f"Auto mode on allowlisted repository {plan.slug}", {"patch_sha256": plan.patch_sha256})
        approver = None
    else:
        return refuse(f"Unknown fix mode {mode}")
    name = _git(repo, "config", "user.name", check=False).stdout.strip()
    email = _git(repo, "config", "user.email", check=False).stdout.strip()
    if not name or not email:
        return refuse("No git identity is configured in the repository, so nothing is committed", stage="git")
    if remote_has_branch(repo, plan.remote, branch):
        return refuse(f"Branch {branch} already exists on {plan.remote}; it is never overwritten", stage="git")

    tmp = Path(tempfile.mkdtemp(prefix="br-fixpr-"))
    tree = tmp / "tree"
    try:
        _git(repo, "worktree", "add", "--detach", str(tree), plan.head_sha)
        for p, text in plan.files.items():
            if ".." in Path(p).parts:
                return refuse(f"Patch path {p} escapes the repository", stage="git")
            (tree / p).write_text(text, encoding="utf-8")
        changed = set(_git(tree, "diff", "--name-only").stdout.split())
        if changed != set(plan.files):
            return refuse("The worktree diff does not match the validated patch", {"changed": sorted(changed)}, stage="git")
        _git(tree, "checkout", "-q", "-b", branch)
        _git(tree, "add", "--", *sorted(plan.files))
        _git(tree, "commit", "-q", "-m", f"fix: BlastRadius repair for #{plan.pr_number}")
        commit = _git(tree, "rev-parse", "HEAD").stdout.strip()
        log.record("system", "git", "commit_fix", "accept",
                   f"Committed the validated patch on {branch} as the configured git user",
                   {"files": sorted(plan.files), "author": name, "parent": plan.head_sha},
                   artifacts={"patch_sha256": plan.patch_sha256, "branch": branch, "commit": commit})
        # one explicit ref, no --force: a branch that appeared meanwhile makes the push fail instead of being replaced
        push = _git(tree, "push", plan.remote, f"{commit}:refs/heads/{branch}", check=False)
        if push.returncode != 0:
            return refuse(f"Push of {branch} failed", {"stderr": push.stderr.strip()[:200]}, stage="git")
        log.record("system", "git", "push_fix_branch", "accept", f"Pushed {branch} only, without force",
                   {"remote": plan.remote}, artifacts={"branch": branch, "commit": commit})
    finally:
        _git(repo, "worktree", "remove", "--force", str(tree), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
    summ = audit_mod.summary(audit_mod.read(log.path))
    try:
        url = open_pr(plan.slug, plan.head_branch, branch, f"BlastRadius fix for #{plan.pr_number}",
                      pr_body(plan, summ, branch, mode, approver))
    except FixRefused as exc:
        return refuse(str(exc), {"branch": branch})
    log.record("system", "pr", "open_fix_pr", "accept", f"Opened the fix PR against {plan.head_branch}; it is not merged",
               {"base": plan.head_branch, "audit_head_hash": summ["head_hash"]},
               artifacts={"patch_sha256": plan.patch_sha256, "branch": branch, "commit": commit, "pr_url": url})
    return {"status": "opened", "reason": "", "branch": branch, "commit": commit, "pr_url": url}


# ---- approval sources ----------------------------------------------------------------------------
def gh_comments(slug: str, pr: int) -> list[dict]:
    """Issue comments of a PR via `gh api` (paginated)."""
    r = subprocess.run(["gh", "api", "--paginate", f"repos/{slug}/issues/{pr}/comments"], capture_output=True,
                       text=True, timeout=120)
    if r.returncode != 0:
        raise FixRefused(f"gh api comments failed: {r.stderr.strip()[:200]}")
    out: list[dict] = []
    for chunk in r.stdout.replace("][", "]\n[").splitlines():
        if chunk.strip():
            out += json.loads(chunk)
    return out


def owner_apply_comment(comments: list[dict], owner: str) -> dict | None:
    """The first comment that is exactly the apply command, by the repository owner."""
    for c in comments:
        user = (c.get("user") or {}).get("login", "")
        if (c.get("body") or "").strip().lower().startswith(APPLY_COMMAND) and user.lower() == owner.lower() \
                and c.get("author_association") == "OWNER":
            return c
    return None


def wait_for_comment(plan: FixPlan, log: DecisionLog, timeout: float = 1800, poll: float = 15,
                     comments: Callable[[str, int], list[dict]] = gh_comments, sleep=time.sleep) -> dict | None:
    """Poll the PR until the owner comments the apply command; record the approval and return the comment."""
    owner = plan.slug.split("/")[0]
    t0 = time.time()
    while time.time() - t0 < timeout:
        c = owner_apply_comment(comments(plan.slug, plan.pr_number), owner)
        if c is not None:
            record_approval(log, (c.get("user") or {}).get("login", owner), "PR comment", plan.patch_sha256,
                            {"comment_id": c.get("id"), "comment_url": c.get("html_url"), "created_at": c.get("created_at")})
            return c
        sleep(poll)
    log.record("system", "approve", "await_approval", "skip", f"No approval within {int(timeout)} s; nothing was pushed",
               {"timeout_s": timeout})
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.agents.fixpr")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("approve")
    a.add_argument("--run", required=True)
    a.add_argument("--by", required=True)
    a.add_argument("--source", default="Live Lab button")
    w = sub.add_parser("wait")
    w.add_argument("--run", required=True)
    w.add_argument("--timeout", type=float, default=1800)
    w.add_argument("--poll", type=float, default=15)
    s = sub.add_parser("status")
    s.add_argument("--run", required=True)
    ns = ap.parse_args(argv)
    log = DecisionLog(ns.run, LOG_ROOT)
    if not (log.dir / PLAN_FILE).exists():
        print(json.dumps({"status": "no-plan", "reason": f"no {PLAN_FILE} for run {ns.run} (nothing validated to apply)"}))
        return 2
    plan = FixPlan.load(log)
    if ns.cmd == "status":
        recs = audit_mod.read(log.path)
        print(json.dumps({"mode": fix_mode(), "approved": approval_of(recs, plan.patch_sha256) is not None,
                          "branch": branch_name(plan.head_sha), "slug": plan.slug,
                          "pr_url": next((r["artifacts"]["pr_url"] for r in recs if (r.get("artifacts") or {}).get("pr_url")), None)}))
        return 0
    if ns.cmd == "approve":
        if fix_mode() != "ask":
            print(json.dumps({"status": "refused", "reason": f"BR_FIX_MODE is {fix_mode()}, not ask"}))
            return 3
        record_approval(log, ns.by, ns.source, plan.patch_sha256)
    elif ns.cmd == "wait":
        if wait_for_comment(plan, log, ns.timeout, ns.poll) is None:
            print(json.dumps({"status": "timeout"}))
            return 4
    res = apply_fix(plan, log)
    print(json.dumps(res))
    return 0 if res["status"] == "opened" else 5


if __name__ == "__main__":
    raise SystemExit(main())
