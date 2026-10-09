"""Where pull requests live: a local forge (offline, for demos and tests) or GitHub.

``LocalForge`` keeps each PR as JSON under ``<state>/prs/`` and merges with a real
``git merge --no-ff`` into the base branch, so the merge commit id it returns is a
genuine commit. ``GitHubForge`` pushes the branch and uses the REST API: reads go
through ``get_with_backoff()`` (the project's only GET path), writes (open PR,
merge, dispatch) through the single ``_write()`` below (D-55).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.agents import gitops

API = "https://api.github.com"


@dataclass
class PullRequest:
    """A pull request, the same shape for both forges."""

    number: int
    title: str
    body: str
    head: str
    base: str
    head_sha: str
    state: str = "open"  # open | merged | closed
    url: str = ""
    merge_commit: str | None = None
    impact_doc: str | None = None
    reviews: list[dict] = field(default_factory=list)
    created_at: str = ""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class LocalForge:
    """Pull requests as JSON files beside the repository; merges are real git merges."""

    kind = "local"

    def __init__(self, repo: Path, state_dir: Path) -> None:
        self.repo = Path(repo)
        self.dir = Path(state_dir) / "prs"
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, number: int) -> Path:
        return self.dir / f"pr-{number}.json"

    def _save(self, pr: PullRequest) -> None:
        self._path(pr.number).write_text(json.dumps(asdict(pr), indent=2), encoding="utf-8")

    def open_pr(self, head: str, base: str, title: str, body: str, impact_doc: str | None = None) -> PullRequest:
        """Open a PR from ``head`` into ``base``."""
        numbers = [int(m.group(1)) for p in self.dir.glob("pr-*.json") if (m := re.match(r"pr-(\d+)", p.stem))]
        number = max(numbers, default=0) + 1
        pr = PullRequest(
            number=number, title=title, body=body, head=head, base=base,
            head_sha=gitops.head_sha(self.repo, head), url=f"local://{self._path(number)}",
            impact_doc=impact_doc, created_at=_now(),
        )
        self._save(pr)
        return pr

    def get_pr(self, number: int) -> PullRequest:
        """Load PR ``number``."""
        return PullRequest(**json.loads(self._path(number).read_text(encoding="utf-8")))

    def changed_files(self, pr: PullRequest) -> list[str]:
        """Files the PR changes relative to its base."""
        return gitops.changed_files(self.repo, pr.base, pr.head)

    def diff(self, pr: PullRequest) -> str:
        """Unified diff of the PR."""
        return gitops.diff_text(self.repo, pr.base, pr.head)

    def add_review(self, pr: PullRequest, review: dict) -> None:
        """Attach a review record."""
        pr.reviews.append(review)
        self._save(pr)

    def ci_status(self, pr: PullRequest) -> str:
        """Local forge has no CI; the reviewer runs the tests itself."""
        return "none"

    def merge(self, pr: PullRequest) -> str:
        """``git merge --no-ff`` the head into the base; return the merge commit id."""
        gitops.git(self.repo, "checkout", "-q", pr.base)
        gitops.git(self.repo, "merge", "--no-ff", "-q", pr.head, "-m",
                   f"Merge pull request #{pr.number} from {pr.head}\n\n{pr.title}")
        sha = gitops.head_sha(self.repo)
        pr.state, pr.merge_commit = "merged", sha
        self._save(pr)
        return sha


class GitHubForge:
    """GitHub REST forge. Token: ``GITHUB_TOKEN`` (or ``GH_TOKEN``)."""

    kind = "github"

    def __init__(self, repo: Path, state_dir: Path, slug: str | None = None) -> None:
        self.repo = Path(repo)
        self.state_dir = Path(state_dir)
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
        if not self.token:
            raise RuntimeError("GitHub forge needs GITHUB_TOKEN (or GH_TOKEN) in the environment")
        self.slug = slug or self._slug_from_remote()

    def _slug_from_remote(self) -> str:
        url = gitops.git(self.repo, "remote", "get-url", "origin")
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", url)
        if not m:
            raise RuntimeError(f"origin {url!r} is not a GitHub remote")
        return m.group(1)

    def _get(self, path: str, params: dict | None = None) -> dict | list:
        from src.harvest.ratelimit import TokenPool, get_with_backoff

        resp = get_with_backoff(f"{API}{path}", params, pool=TokenPool([self.token]))
        resp.raise_for_status()
        return resp.json()

    def _write(self, method: str, path: str, payload: dict) -> requests.Response:
        if os.environ.get("BR_OFFLINE") == "1":
            raise RuntimeError(f"BR_OFFLINE=1: refusing {method} {path}")
        resp = requests.request(
            method, f"{API}{path}", json=payload, timeout=(10, 60),
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28"},
        )
        log = self.state_dir / "github_writes.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": _now(), "method": method, "path": path, "status": resp.status_code}) + "\n")
        return resp

    def _pr_from(self, data: dict, impact_doc: str | None = None) -> PullRequest:
        return PullRequest(
            number=data["number"], title=data["title"], body=data.get("body") or "",
            head=data["head"]["ref"], base=data["base"]["ref"], head_sha=data["head"]["sha"],
            state="merged" if data.get("merged") else data["state"], url=data["html_url"],
            merge_commit=data.get("merge_commit_sha") if data.get("merged") else None,
            impact_doc=impact_doc, created_at=data.get("created_at", ""),
        )

    def open_pr(self, head: str, base: str, title: str, body: str, impact_doc: str | None = None) -> PullRequest:
        """Push ``head`` and open a PR into ``base``."""
        gitops.git(self.repo, "push", "-u", "origin", head)
        resp = self._write("POST", f"/repos/{self.slug}/pulls", {"title": title, "body": body, "head": head, "base": base})
        if resp.status_code >= 300:
            raise RuntimeError(f"open PR failed ({resp.status_code}): {resp.text[:300]}")
        return self._pr_from(resp.json(), impact_doc)

    def get_pr(self, number: int) -> PullRequest:
        """Fetch PR ``number``."""
        return self._pr_from(self._get(f"/repos/{self.slug}/pulls/{number}"))

    def changed_files(self, pr: PullRequest) -> list[str]:
        """Files the PR changes."""
        files = self._get(f"/repos/{self.slug}/pulls/{pr.number}/files", {"per_page": 100})
        return sorted(f["filename"] for f in files)

    def diff(self, pr: PullRequest) -> str:
        """Unified diff, reconstructed from the per-file patches."""
        files = self._get(f"/repos/{self.slug}/pulls/{pr.number}/files", {"per_page": 100})
        return "\n".join(f"--- {f['filename']}\n{f.get('patch', '')}" for f in files)[:60000]

    def add_review(self, pr: PullRequest, review: dict) -> None:
        """Post the review as a PR review (COMMENT; approval is decided by the agent)."""
        self._write("POST", f"/repos/{self.slug}/pulls/{pr.number}/reviews",
                    {"event": "COMMENT", "body": review.get("markdown", review.get("summary", ""))[:60000]})

    def ci_status(self, pr: PullRequest) -> str:
        """Aggregate check-run conclusion for the PR head: success | failure | pending | none."""
        runs = self._get(f"/repos/{self.slug}/commits/{pr.head_sha}/check-runs").get("check_runs", [])
        if not runs:
            return "none"
        if any(r["status"] != "completed" for r in runs):
            return "pending"
        bad = {"failure", "timed_out", "cancelled", "action_required"}
        return "failure" if any(r.get("conclusion") in bad for r in runs) else "success"

    def merge(self, pr: PullRequest) -> str:
        """Merge via the API; return the merge commit id."""
        resp = self._write("PUT", f"/repos/{self.slug}/pulls/{pr.number}/merge",
                           {"merge_method": "merge", "commit_title": f"Merge pull request #{pr.number}: {pr.title}"})
        if resp.status_code >= 300:
            raise RuntimeError(f"merge failed ({resp.status_code}): {resp.text[:300]}")
        return resp.json()["sha"]

    def dispatch_workflow(self, workflow: str, ref: str, inputs: dict) -> None:
        """Trigger a ``workflow_dispatch`` run."""
        resp = self._write("POST", f"/repos/{self.slug}/actions/workflows/{workflow}/dispatches", {"ref": ref, "inputs": inputs})
        if resp.status_code >= 300:
            raise RuntimeError(f"workflow dispatch failed ({resp.status_code}): {resp.text[:300]}")

    def latest_run(self, workflow: str, branch: str, commit: str) -> dict | None:
        """Most recent run of ``workflow`` on ``branch`` for ``commit``, if any."""
        runs = self._get(f"/repos/{self.slug}/actions/workflows/{workflow}/runs", {"branch": branch, "per_page": 20})
        for run in runs.get("workflow_runs", []):
            if run.get("head_sha") == commit:
                return run
        return None


def get_forge(kind: str, repo: Path, state_dir: Path) -> LocalForge | GitHubForge:
    """Factory: ``local`` or ``github``."""
    if kind == "local":
        return LocalForge(repo, state_dir)
    if kind == "github":
        return GitHubForge(repo, state_dir)
    raise ValueError(f"unknown forge {kind!r}")
