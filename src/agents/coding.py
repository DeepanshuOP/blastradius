"""Coding Agent: impact analysis + codebase -> changed files + pull request.

With an LLM configured, the model receives the story, the acceptance criteria,
and the full text of the files the impact analysis named (files to change, their
dependents, and the tests at risk), and returns complete new file contents. With
no LLM, the agent applies a recorded change set (``--patch``, JSON) instead, so
the workflow can be demonstrated offline; the PR says which mode produced it.

Guards: paths must stay inside the repository and outside ``.git`` and the state
directory; every changed ``.py`` file must compile; the branch is created from the
analysed base, and the PR body carries the impact scope so the reviewer can check it.
"""

from __future__ import annotations

import json
import py_compile
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from src.agents import gitops
from src.agents.forge import LocalForge, GitHubForge
from src.agents.impact import ImpactAnalysis
from src.agents.llm import LLMError, OfflineLLM, get_llm


class CodingError(RuntimeError):
    """The agent could not produce a valid change."""


@dataclass
class CodingResult:
    """What the Coding Agent hands to the PR Reviewer."""

    branch: str
    base: str
    commit: str
    changed_files: list[str]
    pr_number: int
    pr_url: str
    mode: str  # llm:<provider> | patch:<file>
    summary: str


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "change"


def _safe_path(repo: Path, rel: str) -> Path:
    p = (repo / rel).resolve()
    if repo not in p.parents or rel.startswith((".git/", ".blastradius/")) or "/.git/" in f"/{rel}":
        raise CodingError(f"refusing to write outside the working tree: {rel}")
    return p


class CodingAgent:
    """Impact analysis + codebase -> changed files + PR."""

    def __init__(self, provider: str | None = None) -> None:
        self.llm = get_llm(provider)

    def _from_llm(self, impact: ImpactAnalysis, repo: Path) -> dict:
        context = sorted(set(impact.change_files) | {f.path for f in impact.files} | {t.file for t in impact.tests})
        blobs = []
        for rel in context:
            p = repo / rel
            if p.exists():
                blobs.append(f"### {rel}\n```\n{p.read_text(encoding='utf-8', errors='replace')[:12000]}\n```")
        prompt = (
            f"User story:\n{impact.story}\n\nInterpretation:\n{impact.interpretation}\n\n"
            + ("Acceptance criteria:\n" + "\n".join(f"- {c}" for c in impact.acceptance_criteria) + "\n\n" if impact.acceptance_criteria else "")
            + "Files in scope (from the impact analysis):\n\n" + "\n\n".join(blobs)
            + "\n\nImplement the story. Change only what is needed, keep the existing style, and add or update tests "
              "for the new behaviour. Return JSON: {\"files\": [{\"path\": relative path, \"content\": complete new file content}], "
              "\"commit_message\": conventional commit message, \"summary\": 2-3 sentences for the PR}."
        )
        try:
            reply = self.llm.complete_json("You are a careful software engineer making a minimal, tested change.", prompt, max_tokens=16000)
        except LLMError as exc:
            raise CodingError(f"model did not return a usable change: {exc}") from exc
        files = {f["path"]: f["content"] for f in reply.get("files", []) if "path" in f and "content" in f}
        if not files:
            raise CodingError("model returned no file changes")
        return {"files": files, "commit_message": reply.get("commit_message", f"feat: {impact.title}"),
                "summary": reply.get("summary", "")}

    def run(self, impact: ImpactAnalysis, repo: Path | str, forge: LocalForge | GitHubForge, *,
            patch: Path | str | None = None, branch: str | None = None) -> CodingResult:
        """Make the change on a new branch, commit it, and open a PR.

        Args:
            impact: The impact analysis to implement.
            repo: The repository working copy (must be clean).
            forge: Where to open the PR.
            patch: A recorded change set (JSON: files, commit_message, summary), used instead of an LLM.
            branch: Branch name (default ``br/<title-slug>``).

        Raises:
            CodingError: On a dirty tree, a bad path, a compile error, or no change source.
        """
        repo = Path(repo).resolve()
        if not gitops.is_clean(repo):
            raise CodingError("working tree is not clean; commit or stash first")
        if patch:
            change = json.loads(Path(patch).read_text(encoding="utf-8"))
            mode = f"patch:{Path(patch).name}"
        elif not isinstance(self.llm, OfflineLLM):
            change = self._from_llm(impact, repo)
            mode = f"llm:{self.llm.name}"
        else:
            raise CodingError("no LLM configured (set ANTHROPIC_API_KEY) and no --patch given")

        base = impact.base_branch
        branch = branch or f"br/{_slug(impact.title)}"
        gitops.git(repo, "checkout", "-q", base)
        gitops.git(repo, "checkout", "-q", "-b", branch)
        written: list[str] = []
        try:
            for rel, content in sorted(change["files"].items()):
                target = _safe_path(repo, rel)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                written.append(rel)
                if rel.endswith(".py"):
                    try:
                        py_compile.compile(str(target), doraise=True)
                    except py_compile.PyCompileError as exc:
                        raise CodingError(f"{rel} does not compile: {exc.msg}") from exc
            gitops.git(repo, "add", "--", *written)
            if gitops.git(repo, "diff", "--cached", "--name-only") == "":
                raise CodingError("the change set does not modify anything")
            gitops.git(repo, "commit", "-q", "-m", change["commit_message"])
        except Exception:
            gitops.git(repo, "reset", "-q", "--hard", check=False)
            gitops.git(repo, "checkout", "-q", base, check=False)
            gitops.git(repo, "branch", "-D", branch, check=False)
            raise
        commit = gitops.head_sha(repo)
        changed = gitops.changed_files(repo, base, branch)
        out_of_scope = [f for f in changed if f not in impact.scope_files]
        body = "\n".join([
            change.get("summary", ""), "",
            f"**Story:** {impact.story}", "",
            f"**Impact analysis:** risk {impact.risk.upper()}, {len(impact.tests)} test(s) at risk, base `{impact.base_sha[:12]}`.", "",
            "**Changed files**", *[f"- `{f}`" + (" (outside the impact scope)" if f in out_of_scope else "") for f in changed], "",
            "**Tests at risk**", *[f"- `{t.test_id}`" for t in impact.tests[:15]], "",
            f"_Opened by the BlastRadius Coding Agent ({mode})._",
        ])
        gitops.git(repo, "checkout", "-q", base)
        pr = forge.open_pr(branch, base, change["commit_message"].splitlines()[0], body,
                           impact_doc=str(Path(repo, ".blastradius", "impact", impact.base_sha[:12], "impact.json")))
        return CodingResult(branch, base, commit, changed, pr.number, pr.url, mode, change.get("summary", ""))


def save_result(result: CodingResult, state_dir: Path) -> Path:
    """Write ``coding/<branch>.json``."""
    out = state_dir / "coding"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{_slug(result.branch)}.json"
    path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return path
