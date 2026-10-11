"""PR-bot recording run on a seeded task (exploratory, D-63).

    uv run --env-file .env --extra ml --extra rag python -m analysis.bot_demo record    one live run (Groq, cached)
    uv run --extra ml --extra rag python -m analysis.bot_demo replay                    same run from the cache, offline
    uv run --extra ml --extra rag python -m analysis.bot_demo dry                       no model: prints the comment only

Builds a real git repository from one seeded task (the itsdangerous checkout as the base commit, the task's `pr_diff`
as the head commit), runs `src.agents.bot.run_bot` on it with the seeded virtualenv's interpreter, and writes the
comment to `src/agents/demo/bot_comment.md` (the website and the slides read it). The cache is
`eval/llm_cache/bot_openai_gpt-oss-20b.jsonl`. `replay` forbids the network and fails on a cache miss.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from src.agents import bot
from src.eval.seeded.build import SEEDED

TASK_ID = "itsdangerous-ARITH_SWAP-00"        # the first itsdangerous task by id; not chosen by outcome
MODEL = "openai/gpt-oss-20b"
CACHE = Path("eval/llm_cache/bot_openai_gpt-oss-20b.jsonl")
OUT = Path("src/agents/demo/bot_comment.md")
TASKS = Path("eval/seeded/tasks.jsonl")


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), "-c", "user.name=blastradius-demo", "-c", "user.email=demo@example.invalid",
                        *args], capture_output=True, text=True, check=True)
    return p.stdout.strip()


def make_pr(workdir: Path) -> tuple[Path, str, str, dict]:
    """Copy the seeded repo, commit the task's change on a branch; returns `(repo, base, head, task)`."""
    task = next(t for t in (json.loads(ln) for ln in TASKS.read_text(encoding="utf-8").splitlines() if ln.strip())
                if t["task_id"] == TASK_ID)
    src = SEEDED / "repos" / task["repo"]
    repo = workdir / task["repo"]
    shutil.copytree(src, repo, ignore=shutil.ignore_patterns(".pytest_cache", "__pycache__", "*.pyc"))
    git(repo, "checkout", "-q", "--", ".")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "pr")
    p = subprocess.run(["git", "-C", str(repo), "apply", "--whitespace=nowarn", "-"], input=task["pr_diff"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"pr_diff does not apply: {p.stderr[:300]}")
    git(repo, "commit", "-q", "-am", f"feat: change from seeded task {TASK_ID}")
    return repo, base, git(repo, "rev-parse", "HEAD"), task


def main(argv: list[str] | None = None) -> int:
    mode = (argv or sys.argv[1:] or ["replay"])[0]
    from src.agents.llm import GroqLLM
    from src.agents.llm_cache import LLMCache

    if mode == "dry":
        llm = None
    elif mode == "record":
        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            raise SystemExit("record needs GROQ_API_KEY (`uv run --env-file .env ...`)")
        llm = GroqLLM(api_key=key, model=MODEL, cache=LLMCache(CACHE))
    else:
        os.environ["BR_LLM_REPLAY"] = "1"
        llm = GroqLLM(api_key="replay", model=MODEL, cache=LLMCache(CACHE, replay=True), ledger=Path(os.devnull))
    py = SEEDED / "venvs" / "itsdangerous" / "bin" / "python"
    if not py.exists():
        raise SystemExit(f"{py} is missing: run `make seeded` first")
    with tempfile.TemporaryDirectory(prefix="br-bot-demo-") as td:
        repo, base, head, task = make_pr(Path(td))
        out = bot.run_bot(repo, base, head, 1, llm=llm, state_dir=Path(td) / "state", python=str(py))
    if mode != "dry":
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(out.comment, encoding="utf-8")
    print(out.comment)
    print(json.dumps({"task": TASK_ID, "validated": out.validated, "suggestions": len(out.suggestions),
                      **{k: v for k, v in out.stats.items() if k != "diff"}}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
