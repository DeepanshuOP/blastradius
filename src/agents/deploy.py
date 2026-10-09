"""Build & Deploy Agent: commit id + branch -> build, package, deploy; notify on failure.

Local mode (default): check out ``commit`` in a throw-away worktree, run the build
command (auto-detected: the full pytest suite for Python, ``mvn -q package`` or
``./gradlew build`` for Java), package the tree with ``git archive``, and deploy by
copying the package into ``<deploy_dir>/releases/<short-sha>/`` and pointing
``<deploy_dir>/CURRENT`` at it. A failed build is never deployed and always
triggers a notification.

GitHub mode: dispatch a ``workflow_dispatch`` workflow on ``branch`` and poll the
run for ``commit`` until it completes; anything but success notifies.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.agents import gitops
from src.agents.notify import notify


@dataclass
class DeployResult:
    """What the Build & Deploy Agent reports."""

    commit: str
    branch: str
    status: str  # deployed | build_failed | rejected
    build_command: str
    build_exit_code: int | None
    build_seconds: float
    log_tail: list[str]
    package: str | None
    deployed_to: str | None
    notification: dict | None


def detect_build(tree: Path) -> list[str]:
    """Pick a build command for the tree at ``tree``."""
    if (tree / "pom.xml").exists():
        return ["mvn", "-q", "-B", "package"]
    if (tree / "gradlew").exists():
        return ["./gradlew", "build", "--no-daemon"]
    return [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]


class BuildDeployAgent:
    """Commit id + branch -> build and deploy package; notify on failure."""

    def run(self, commit: str, branch: str, repo: Path | str, state_dir: Path | str | None = None, *,
            build_cmd: str | None = None, deploy_dir: Path | str | None = None) -> DeployResult:
        """Build ``commit`` (which must be on ``branch``) and deploy it locally."""
        repo = Path(repo).resolve()
        state = Path(state_dir) if state_dir else repo / ".blastradius"
        commit = gitops.head_sha(repo, commit)
        deploy_root = Path(deploy_dir) if deploy_dir else state / "deploy"
        if not gitops.is_ancestor(repo, commit, branch):
            rec = notify(state, "deploy_rejected", f"{commit[:12]} is not on {branch}; refusing to build it.", {"commit": commit, "branch": branch})
            return self._save(state, DeployResult(commit, branch, "rejected", "", None, 0.0, [], None, None, rec))

        with gitops.worktree(repo, commit) as tree:
            cmd = shlex.split(build_cmd) if build_cmd else detect_build(tree)
            started = time.perf_counter()
            proc = subprocess.run(cmd, cwd=tree, capture_output=True, text=True,
                                  env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            secs = round(time.perf_counter() - started, 3)
            log = (proc.stdout + proc.stderr).strip().splitlines()
            builds = state / "builds" / commit[:12]
            builds.mkdir(parents=True, exist_ok=True)
            (builds / "build.log").write_text("\n".join(log) + "\n", encoding="utf-8")
            cmd_str = " ".join(Path(c).name if i == 0 else c for i, c in enumerate(cmd))
            if proc.returncode != 0:
                failed = [ln for ln in log if ln.startswith(("FAILED", "ERROR"))][:10]
                rec = notify(state, "build_failed",
                             f"Build FAILED for {branch} @ {commit[:12]} ({cmd_str} exited {proc.returncode}); not deployed.",
                             {"commit": commit, "branch": branch, "failed": failed, "log": str(builds / "build.log")})
                return self._save(state, DeployResult(commit, branch, "build_failed", cmd_str, proc.returncode, secs, log[-15:], None, None, rec))

        pkg_dir = state / "artifacts"
        pkg_dir.mkdir(parents=True, exist_ok=True)
        package = pkg_dir / f"{repo.name}-{commit[:12]}.tar.gz"
        gitops.git(repo, "archive", "--format=tar.gz", f"--prefix={repo.name}/", "-o", str(package), commit)
        release = deploy_root / "releases" / commit[:12]
        release.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package, release / package.name)
        (deploy_root / "CURRENT").write_text(f"{commit}\n", encoding="utf-8")
        with (deploy_root / "deployments.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "commit": commit,
                                 "branch": branch, "package": package.name}) + "\n")
        return self._save(state, DeployResult(commit, branch, "deployed", cmd_str, 0, secs, log[-5:], str(package), str(release), None))

    def run_github(self, commit: str, branch: str, repo: Path | str, forge, workflow: str,
                   state_dir: Path | str | None = None, timeout_s: int = 1800, poll_s: int = 20) -> DeployResult:
        """Dispatch ``workflow`` on GitHub for ``branch`` and wait for the run on ``commit``."""
        repo = Path(repo).resolve()
        state = Path(state_dir) if state_dir else repo / ".blastradius"
        forge.dispatch_workflow(workflow, branch, {"commit": commit})
        deadline = time.time() + timeout_s
        run = None
        while time.time() < deadline:
            run = forge.latest_run(workflow, branch, commit)
            if run and run.get("status") == "completed":
                break
            time.sleep(poll_s)
        conclusion = (run or {}).get("conclusion") or "timed_out"
        url = (run or {}).get("html_url", "")
        if conclusion != "success":
            rec = notify(state, "build_failed", f"Workflow {workflow} on {branch} @ {commit[:12]}: {conclusion}. {url}",
                         {"commit": commit, "branch": branch, "run": url})
            return self._save(state, DeployResult(commit, branch, "build_failed", f"workflow:{workflow}", None, 0.0, [url], None, None, rec))
        return self._save(state, DeployResult(commit, branch, "deployed", f"workflow:{workflow}", 0, 0.0, [url], None, url, None))

    @staticmethod
    def _save(state: Path, result: DeployResult) -> DeployResult:
        out = state / "builds" / result.commit[:12]
        out.mkdir(parents=True, exist_ok=True)
        (out / "deploy.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
        return result
