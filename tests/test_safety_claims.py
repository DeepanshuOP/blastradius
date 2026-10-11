"""Tests behind the website's Compare > Safety checklist (D-63, D-17, D-58).

Each test pins one claim to the real code or the real recorded files; nothing here mocks the thing it checks.
The checklist in `docs/compare_matrix.yaml` ("safety") names these tests, and `analysis/demo_check.py` fails if a
named test no longer exists.
"""

from __future__ import annotations

import ast
import json
import os
import re
from pathlib import Path

from analysis.secret_scan import scan_text
from src.agents import bot

ROOT = Path(__file__).resolve().parents[1]
BOT_FORGE_METHODS = {"list_comments", "create_comment", "update_comment", "list_review_comments", "review_suggestions"}
CREDENTIAL = re.compile(r"gsk_[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}")


def _calls_on_forge(path: Path) -> set[str]:
    """Attribute names called on any object named `forge` in `path` (e.g. `forge.merge(...)`)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {n.func.attr for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "forge"}


# ---- the bot never merges or pushes --------------------------------------------------------------
def test_bot_never_merges_pushes_or_approves() -> None:
    used = _calls_on_forge(Path(bot.__file__))
    assert used and used <= BOT_FORGE_METHODS, f"the bot calls forge methods beyond comment/suggestion: {used - BOT_FORGE_METHODS}"
    src = Path(bot.__file__).read_text(encoding="utf-8")
    assert not re.search(r"\bmerge\s*\(|git\W+push|\"push\"|APPROVE|REQUEST_CHANGES", src)
    forge = (ROOT / "src" / "agents" / "forge.py").read_text(encoding="utf-8")
    review = forge[forge.index("def review_suggestions"):forge.index("def dispatch_workflow")]
    assert '"event": "COMMENT"' in review and "APPROVE" not in review
    wf = "\n".join(ln.split("#")[0] for ln in (ROOT / "integrations" / "github-actions" / "blastradius-bot.yml")
                   .read_text(encoding="utf-8").splitlines())     # comments explain the permissions; check the keys
    assert "contents: read" in wf and "contents: write" not in wf and "git push" not in wf


# ---- secrets are never written to caches, the ledger or the demo comment -------------------------
def test_no_credential_in_the_llm_caches_the_ledger_or_the_recorded_comment() -> None:
    files = sorted((ROOT / "eval" / "llm_cache").glob("*.jsonl")) + [ROOT / "src" / "agents" / "demo" / "bot_comment.md"]
    assert len(files) >= 5
    live = [v for k, v in os.environ.items() if k.endswith(("_API_KEY", "_TOKEN", "_PAT_1", "_PAT_2", "_PAT_3")) and len(v) >= 12]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not CREDENTIAL.search(text), path.name
        assert not scan_text(text).get("github_token"), path.name
        assert not any(v in text for v in live), path.name
    for line in (ROOT / "eval" / "llm_cache" / "e3_openai_gpt-oss-120b.jsonl").read_text(encoding="utf-8").splitlines()[:50]:
        rec = json.loads(line)
        assert set(rec) <= {"key", "latency_s", "model", "provider_id", "request", "response_text", "timestamp", "usage"}
        assert "authorization" not in json.dumps(rec["request"]).lower()


# ---- no LLM reachable from E1, E2, the features or `make tables` ---------------------------------
LLM_MODULES = {"src.agents.llm", "src.agents.llm_cache", "src.agents.repair", "src.agents.ask", "src.agents.bot",
               "anthropic", "openai", "groq"}


def _module_path(mod: str) -> Path | None:
    p = ROOT.joinpath(*mod.split("."))
    for cand in (p.with_suffix(".py"), p / "__init__.py"):
        if cand.exists():
            return cand
    return None


def _imports(path: Path) -> set[str]:
    out: set[str] = set()
    for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(n, ast.Import):
            out |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            out.add(n.module)
            out |= {f"{n.module}.{a.name}" for a in n.names}
    return out


def _closure(entries: list[Path]) -> dict[str, Path]:
    seen: dict[str, Path] = {}
    todo = list(entries)
    while todo:
        p = todo.pop()
        if str(p) in seen.values():
            continue
        seen[p.stem] = p
        for mod in _imports(p):
            if mod.split(".")[0] in ("src", "analysis"):
                q = _module_path(mod)
                if q is not None and q not in seen.values():
                    todo.append(q)
    return seen


def _tables_entries() -> list[Path]:
    make = (ROOT / "Makefile").read_text(encoding="utf-8")
    recipe = make[make.index("\ntables:\n"):make.index("\nresolve-bases:")]
    paths = {ROOT / m for m in re.findall(r"(?:analysis|src/label)/[a-z0-9_]+\.py", recipe)}
    paths |= {_module_path(m) for m in re.findall(r"-m (analysis\.[a-z0-9_]+)", recipe)}
    return sorted(p for p in paths if p is not None)


def test_no_llm_module_is_reachable_from_e1_e2_features_or_make_tables() -> None:
    entries = _tables_entries() + sorted((ROOT / "src" / "features").glob("*.py")) + sorted((ROOT / "src" / "models").glob("*.py"))
    assert len(entries) > 15
    reach = _closure(entries)
    for path in reach.values():
        imported = _imports(path)
        bad = {m for m in imported if m in LLM_MODULES or m.split(".")[0] in ("anthropic", "openai", "groq")}
        assert not bad, f"{path.relative_to(ROOT)} imports {bad}"
        assert "api.groq.com" not in path.read_text(encoding="utf-8"), path
    make = (ROOT / "Makefile").read_text(encoding="utf-8")
    recipe = make[make.index("\ntables:\n"):make.index("\nresolve-bases:")]
    assert "repair-run" not in recipe and "repair_eval" not in recipe and "rq4_repair" not in recipe
