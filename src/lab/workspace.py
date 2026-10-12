"""Scratch workspaces: where repository code is allowed to run (never the BlastRadius checkout, never data/seeded)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from src.eval.seeded.build import REPOS, ROOT, SEEDED, VENVS

PREPARED = ("click", "itsdangerous", "markupsafe", "shopcart")
LAB_ROOT = Path(tempfile.gettempdir()) / "br-lab"
URL_RE = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+?)(\.git)?$")
INSTALL_TIMEOUT_S = 180
CLONE_TIMEOUT_S = 120
_SKIP = {".git", "node_modules", "build", "target", "dist", "__pycache__", ".venv", "venv"}


@dataclass
class Workspace:
    """A repository copy the lab may run code in."""

    name: str
    url: str
    repo_dir: Path
    base: str
    language: str
    n_files: int
    prepared: bool
    python: str | None = None
    runnable: bool = False
    reason: str = ""
    src_dirs: list[str] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)


def git(repo: Path, *args: str, check: bool = True, timeout: int = 60) -> str:
    """`git -C repo args` with a timeout and a fixed identity (commits made here are scratch commits)."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_AUTHOR_NAME": "br-lab", "GIT_AUTHOR_EMAIL": "lab@example.invalid",
           "GIT_COMMITTER_NAME": "br-lab", "GIT_COMMITTER_EMAIL": "lab@example.invalid",
           "GIT_AUTHOR_DATE": "2026-10-12T00:00:00Z", "GIT_COMMITTER_DATE": "2026-10-12T00:00:00Z"}
    p = subprocess.run(["git", "-C", str(repo), "-c", "core.autocrlf=false", *args], capture_output=True, text=True,
                       env=env, timeout=timeout)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {(p.stderr or p.stdout).strip()[:300]}")
    return p.stdout.strip()


def count_files(root: Path) -> tuple[int, int, int]:
    """`(python, java, all source-like)` file counts, skipping hidden and build directories."""
    py = java = 0
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in _SKIP and not d.startswith(".")]
        for f in fns:
            py += f.endswith(".py")
            java += f.endswith(".java")
    return py, java, py + java


def new_scratch(prefix: str = "run") -> Path:
    """A fresh directory under the OS temp directory; scratch directories left by killed runs (> 3 h old) are swept."""
    import atexit
    import time

    LAB_ROOT.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for old in LAB_ROOT.iterdir():
        if old.is_dir() and old.name != "graphs" and now - old.stat().st_mtime > 3 * 3600:
            shutil.rmtree(old, ignore_errors=True)
    d = Path(tempfile.mkdtemp(prefix=f"{prefix}-", dir=LAB_ROOT))
    # registered before the graph library is imported, so it runs after that library's own exit hooks
    atexit.register(lambda: shutil.rmtree(d, ignore_errors=True))
    return d


def prepared_info() -> dict[str, dict]:
    """Pins of the four prepared repositories (`eval/seeded/repos.json`)."""
    return json.loads((ROOT / "eval" / "seeded" / "repos.json").read_text(encoding="utf-8"))


def prepare_seeded(slug: str, scratch: Path) -> Workspace:
    """Copy a prepared repository out of data/seeded (read-only use) and reuse its virtualenv."""
    if slug not in PREPARED:
        raise ValueError(f"{slug!r} is not a prepared repository ({', '.join(PREPARED)})")
    src = REPOS / slug
    py = VENVS / slug / "bin" / "python"
    if not src.is_dir():
        raise FileNotFoundError(f"{src} is missing: run `make seeded`")
    dst = scratch / slug
    shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns(".pytest_cache", "__pycache__", "*.pyc",
                                                                           ".blastradius"))
    git(dst, "checkout", "-q", "--", ".")           # the copy, never the original, is restored to the pinned tree
    pins = prepared_info().get(slug, {})
    n_py, n_java, _ = count_files(dst)
    ok = py.exists()
    return Workspace(slug, pins.get("url", f"local:{slug}"), dst, git(dst, "rev-parse", "HEAD"),
                     "python", n_py + n_java, True, str(py) if ok else None, ok,
                     "" if ok else f"virtualenv {py} is missing", list(pins.get("src_dirs", [])))


def prepare_github(url: str, scratch: Path, install: bool = True) -> Workspace:
    """Shallow-clone a public repository; for Python try `uv venv` + `uv pip install -e . pytest` (180 s cap)."""
    import time

    m = URL_RE.match(url.strip())
    if not m:
        raise ValueError("only https://github.com/<owner>/<repo> URLs are accepted")
    name = m.group(2)
    dst = scratch / name
    t0 = time.perf_counter()
    p = subprocess.run(["git", "clone", "--quiet", "--depth", "50", url, str(dst)], capture_output=True, text=True,
                       timeout=CLONE_TIMEOUT_S, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if p.returncode != 0:
        raise RuntimeError(f"git clone failed: {(p.stderr or '').strip()[-300:]}")
    ws = Workspace(name, url, dst, git(dst, "rev-parse", "HEAD"), "unknown", 0, False)
    ws.timings["clone_s"] = round(time.perf_counter() - t0, 1)
    n_py, n_java, _ = count_files(dst)
    ws.n_files = n_py + n_java
    ws.language = "python" if n_py >= n_java and n_py else ("java" if n_java else "unknown")
    if ws.language == "java":
        ws.reason = "Java: the lab builds the graph and the impact ranking; Java suites are not run here"
        return ws
    if ws.language != "python":
        ws.reason = "no .py or .java files: nothing to analyse"
        return ws
    if not install:
        ws.reason = "install skipped"
        return ws
    venv = scratch / "venv"
    t1 = time.perf_counter()
    try:
        subprocess.run(["uv", "venv", "-q", "--python", "3.11", str(venv)], check=True, capture_output=True, text=True,
                       timeout=INSTALL_TIMEOUT_S)
        py = venv / "bin" / "python"
        deadline = INSTALL_TIMEOUT_S - (time.perf_counter() - t1)
        r = subprocess.run(["uv", "pip", "install", "-q", "--python", str(py), "-e", str(dst), "pytest"],
                           capture_output=True, text=True, timeout=max(deadline, 10))
        if r.returncode != 0:
            ws.reason = "pip install -e . failed: " + (r.stderr or r.stdout).strip().splitlines()[-1][:300] \
                if (r.stderr or r.stdout).strip() else "pip install -e . failed"
        else:
            ws.python, ws.runnable = str(py), True
    except subprocess.TimeoutExpired:
        ws.reason = f"installation exceeded the {INSTALL_TIMEOUT_S} s cap"
    except subprocess.CalledProcessError as exc:
        ws.reason = "uv venv failed: " + (exc.stderr or str(exc))[-200:]
    ws.timings["install_s"] = round(time.perf_counter() - t1, 1)
    return ws
