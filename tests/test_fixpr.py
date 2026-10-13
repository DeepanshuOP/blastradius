"""D-70: the approval-gated fix PR, against a temp git repo whose `origin` is a local bare repository.

Everything git does here is real (worktree, commit, push to the bare remote, ls-remote). The only replaced step is
`gh pr create`, which is passed in as `open_pr` and records its arguments: no GitHub call is made.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.agents import audit
from src.agents.fixpr import (APPLY_COMMAND, FixPlan, allowlist, apply_fix, approval_of, branch_name, fix_mode,
                              owner_apply_comment, record_approval, wait_for_comment)

GOOD = [{"name": n, "ok": True, "evidence": "ok"} for n in
        ("applies", "syntax", "targeted", "full", "scope", "reverify_full", "reverify_scope")]


def git(cwd: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *a], check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture()
def world(tmp_path):
    """origin.git (bare, default branch main) and a clone with a PR branch `feature` carrying a bug."""
    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
    repo = tmp_path / "clone"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    git(repo, "config", "user.name", "Fixture Operator")
    git(repo, "config", "user.email", "operator@example.invalid")
    (repo / "m.py").write_text("def expired(age, max_age):\n    return age > max_age\n")
    git(repo, "add", "m.py")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "remote", "add", "origin", str(bare))
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "-b", "feature")
    (repo / "m.py").write_text("def expired(age, max_age):\n    return age < max_age\n")
    git(repo, "commit", "-q", "-am", "flip")
    git(repo, "push", "-q", "origin", "feature")
    head = git(repo, "rev-parse", "HEAD")
    refs_before = git(bare, "for-each-ref", "--format=%(refname) %(objectname)")
    plan = FixPlan(repo_dir=str(repo), slug="DeepanshuOP/itsdangerous", pr_number=3, head_branch="feature",
                   head_sha=head, files={"m.py": "def expired(age, max_age):\n    return age > max_age\n"},
                   checks=[dict(c) for c in GOOD], patch_sha256="p" * 64,
                   ranked=[{"test": "tests/test_m.py", "score": 0.9, "why": "touches m.py"}],
                   triage=[{"test": "tests/test_m.py::test_expired", "class": "mine", "confidence": 0.9, "reason": "new"}],
                   evidence_path=[{"node": "m.expired", "hops": 1, "path": ["tests.test_m.test_expired", "m.expired"]}])
    log = audit.DecisionLog("fix-run", root=tmp_path / "logs")
    log.record("system", "verify", "verdict", "accept", "The patch passed every check", {"accepted": True})
    return {"bare": bare, "repo": repo, "plan": plan, "log": log, "refs_before": refs_before}


class PRs:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def __call__(self, slug, base, head, title, body) -> str:
        self.calls.append((slug, base, head, title, body))
        return f"https://github.com/{slug}/pull/99"


def refs(bare: Path) -> str:
    return git(bare, "for-each-ref", "--format=%(refname) %(objectname)")


def last(log) -> dict:
    return audit.read(log.path)[-1]


def test_defaults() -> None:
    assert fix_mode({}) == "suggest" and fix_mode({"BR_FIX_MODE": "yolo"}) == "suggest"
    assert allowlist({}) == {"deepanshuop/itsdangerous"}
    assert branch_name("abcdef1234") == "blastradius/fix-abcdef1"


def test_suggest_mode_pushes_nothing(world) -> None:
    prs = PRs()
    res = apply_fix(world["plan"], world["log"], mode="suggest", open_pr=prs)
    assert res["status"] == "suggested" and prs.calls == [] and refs(world["bare"]) == world["refs_before"]
    assert last(world["log"])["decision"] == "skip"


def test_refuses_repo_outside_allowlist(world) -> None:
    prs = PRs()
    world["plan"].slug = "pallets/itsdangerous"
    res = apply_fix(world["plan"], world["log"], mode="auto", open_pr=prs)
    assert res["status"] == "refused" and "not in BR_FIX_ALLOWLIST" in res["reason"]
    assert prs.calls == [] and refs(world["bare"]) == world["refs_before"]
    assert last(world["log"])["decision"] == "reject" and audit.verify("fix-run", world["log"].root)[0]


@pytest.mark.parametrize("bad", ["full", "scope", "reverify_full", "reverify_scope"])
def test_refuses_when_any_check_failed(world, bad) -> None:
    prs = PRs()
    for c in world["plan"].checks:
        if c["name"] == bad:
            c["ok"] = False
    res = apply_fix(world["plan"], world["log"], mode="auto", open_pr=prs)
    assert res["status"] == "refused" and bad in res["reason"]
    assert prs.calls == [] and refs(world["bare"]) == world["refs_before"]


def test_refuses_a_missing_check(world) -> None:
    world["plan"].checks = [c for c in world["plan"].checks if c["name"] != "reverify_full"]
    res = apply_fix(world["plan"], world["log"], mode="auto", open_pr=PRs())
    assert res["status"] == "refused" and "reverify_full" in res["reason"]


@pytest.mark.parametrize("head_branch", ["main", "master"])
def test_refuses_default_or_protected_branch_as_base(world, head_branch) -> None:
    prs = PRs()
    world["plan"].head_branch = head_branch
    res = apply_fix(world["plan"], world["log"], mode="auto", open_pr=prs)
    assert res["status"] == "refused" and "default or a protected branch" in res["reason"]
    assert prs.calls == [] and refs(world["bare"]) == world["refs_before"]


def test_refuses_when_fix_branch_exists_on_remote(world) -> None:
    git(world["repo"], "push", "-q", "origin", f"main:refs/heads/{branch_name(world['plan'].head_sha)}")
    before = refs(world["bare"])
    res = apply_fix(world["plan"], world["log"], mode="auto", open_pr=PRs())
    assert res["status"] == "refused" and "never overwritten" in res["reason"] and refs(world["bare"]) == before


def test_ask_mode_does_nothing_without_an_approval_record(world) -> None:
    prs = PRs()
    res = apply_fix(world["plan"], world["log"], mode="ask", open_pr=prs)
    assert res["status"] == "waiting" and prs.calls == [] and refs(world["bare"]) == world["refs_before"]
    rec = last(world["log"])
    assert rec["stage"] == "approve" and rec["decision"] == "wait"
    # an approval for a different patch does not count
    record_approval(world["log"], "DeepanshuOP", "Live Lab button", "q" * 64)
    assert apply_fix(world["plan"], world["log"], mode="ask", open_pr=prs)["status"] == "waiting"
    assert prs.calls == []


def test_ask_mode_with_approval_pushes_only_the_fix_branch_and_opens_one_pr(world) -> None:
    prs = PRs()
    plan, log, bare = world["plan"], world["log"], world["bare"]
    record_approval(log, "DeepanshuOP", "Live Lab button", plan.patch_sha256)
    res = apply_fix(plan, log, mode="ask", open_pr=prs)
    assert res["status"] == "opened" and res["pr_url"].endswith("/pull/99")
    branch = branch_name(plan.head_sha)
    # exactly one new ref, the fix branch; main and the author's branch are unchanged
    before = dict(ln.split()[::-1][::-1] for ln in world["refs_before"].splitlines())
    after = dict(ln.split() for ln in refs(bare).splitlines())
    assert {k: v for k, v in after.items() if k in before} == before
    assert set(after) - set(before) == {f"refs/heads/{branch}"}
    # the fix commit's parent is the PR head, its author the configured identity, and it holds the patch
    c = after[f"refs/heads/{branch}"]
    assert git(bare, "rev-parse", f"{c}^") == plan.head_sha
    assert git(bare, "log", "-1", "--format=%an <%ae>", c) == "Fixture Operator <operator@example.invalid>"
    assert git(bare, "show", f"{c}:m.py") == plan.files["m.py"].rstrip("\n")
    assert "Co-Authored-By" not in git(bare, "log", "-1", "--format=%B", c)
    # one PR, against the failing PR's head branch, with the evidence in the body
    (slug, base, head, _title, body), = prs.calls
    assert (slug, base, head) == ("DeepanshuOP/itsdangerous", "feature", branch)
    for needle in ("tests/test_m.py", "**mine**", "m.expired", "reverify_full", "Audit hash", "never merges"):
        assert needle in body, needle
    recs = audit.read(log.path)
    assert [r["stage"] for r in recs[-3:]] == ["git", "git", "pr"]
    assert recs[-1]["artifacts"]["pr_url"] == res["pr_url"] and audit.verify("fix-run", log.root)[0]


def test_auto_mode_on_allowlisted_repo_opens_pr(world) -> None:
    prs = PRs()
    res = apply_fix(world["plan"], world["log"], mode="auto", open_pr=prs)
    assert res["status"] == "opened" and len(prs.calls) == 1
    assert any(r["action"] == "auto_approve" for r in audit.read(world["log"].path))


def test_module_has_no_merge_or_force_path() -> None:
    src = (Path(__file__).resolve().parents[1] / "src" / "agents" / "fixpr.py").read_text()
    code = "\n".join(ln for ln in src.splitlines() if not ln.strip().startswith(("#", '"', "*")))
    for banned in ('"merge"', "gh pr merge", "--force-with-lease"):
        assert banned not in code, banned
    pushes = [ln for ln in code.splitlines() if '"push"' in ln]
    assert len(pushes) == 1 and "force" not in pushes[0] and '"-f"' not in pushes[0] and "+" not in pushes[0]


def test_owner_comment_approval(world) -> None:
    owner = "DeepanshuOP"
    comments = [{"id": 1, "body": APPLY_COMMAND, "user": {"login": "someone"}, "author_association": "CONTRIBUTOR"},
                {"id": 2, "body": "looks good", "user": {"login": owner}, "author_association": "OWNER"},
                {"id": 3, "body": f"{APPLY_COMMAND} please", "user": {"login": owner}, "author_association": "OWNER",
                 "html_url": "https://github.com/x/y/pull/3#issuecomment-3"}]
    assert owner_apply_comment(comments[:2], owner) is None
    assert owner_apply_comment(comments, owner)["id"] == 3
    got = wait_for_comment(world["plan"], world["log"], timeout=5, poll=0, comments=lambda s, n: comments,
                           sleep=lambda s: None)
    assert got["id"] == 3
    assert approval_of(audit.read(world["log"].path), world["plan"].patch_sha256)["evidence"]["comment_id"] == 3
