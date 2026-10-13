"""One-command pre-presentation check: `make demo-check`. Offline; prints a PASS/FAIL table; exit 1 on any FAIL.

Checks, in order:

  1. the test subset the demo stands on (agents, bot, rag, E3 replay, slide figures, Ask, safety, cost, matrix);
  2. the named tests of the Compare > Safety checklist, none skipped;
  3. `make demo-data`;
  4. `npm run build` in demo-web/;
  5. `make agents-demo` (the four recorded scenarios);
  6. the 15 recorded Ask questions replayed with the network forbidden;
  7. the recorded PR-bot task replayed (the committed comment must come back byte for byte);
  8. every JSON file the website loads exists and parses;
  9. every number on Compare panels 2 and 4 appears in the generated file it was read from;
  10. the site structure: four tabs (Live Lab, Graph Explorer, Evidence, Use it), the four Evidence sections, footer;
  11. the Live Lab engine tests (`tests/test_lab.py`: stage order, streamed results, replay, injection, no writes);
  12. every recorded lab run validates against the event schema and replays identically through the CLI;
  13. `/api/lab/*` smoke calls on a started server (localhost guard, repos, mutations, file, graph, replay, one run);
  14. the strategy arena against a real recorded run, with hand-counted expected values (`tests/test_lab_arena.py`);
  15. the sys.settrace coverage plugin on itsdangerous: identical function sets across two cold runs;
  16. every presenter screen rendered from every recorded run (react-dom/server, offline, no browser);
  17. the token ledgers are separate: the lab writes only `lab_usage.jsonl`, E3's `usage.jsonl` holds no lab row;
  18. the BlastRadius test-case order against the hand-computed order of a recorded run (tests/test_lab_order.py;
      that expected order is ground truth: fix the code if it fails, never the expectation);
  19. the arena columns (orderers and selectors, `needs`) and the failure-history row with and without runs of the
      same diff (tests/test_lab_arena.py);
  20. the reviewer challenge: the same seed names the same function and operator (tests/test_lab_challenge.py);
  21. the text budget of the Live Lab main screen, counted in server-rendered HTML: no visible paragraph over 2 lines,
      no caption over 14 words (demo-web/scripts/text_budget.tsx);
  22. the review-ready lab, server-rendered (demo-web/scripts/review_check.tsx): the model chip's states, the guided demo
      completing on its recording, the recorded-repair fallback, the top-x% slider;
  23. the "vs Meta" card's numbers (pts.json) against paper/generated/pts_comparison.md and the Meta column of tab:pts;
  24. the "Results at a glance" rows (glance.json) against tab:glance of paper/full/main.tex;
  25. no "BITE" string anywhere in demo-web (sources and data; node_modules and .next excluded).

Replays run against a scratch copy of `data/seeded` (BR_SEEDED_DIR) so they never queue behind a live E3 run's repo
locks. No step can reach a model or the network: replay mode is forced and the keys are removed from the environment.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from analysis import compare_matrix as cm

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "paper/generated"
DATA = ROOT / "demo-web/public/data"
EXTRAS = ["--extra", "graph", "--extra", "ml", "--extra", "rag", "--extra", "figures"]
TEST_SUBSET = ["tests/test_agents.py", "tests/test_agents_repair.py", "tests/test_agents_triage.py", "tests/test_bot.py",
               "tests/test_bot_demo.py", "tests/test_bot_workflow.py", "tests/test_rag.py", "tests/test_rag_r4.py",
               "tests/test_rq5.py", "tests/test_ask.py", "tests/test_e3_replay.py", "tests/test_slide_figures.py",
               "tests/test_safety_claims.py", "tests/test_cost_report.py", "tests/test_compare_matrix.py",
               "tests/test_export_demo_data.py"]


def _env(replay: bool = True) -> dict[str, str]:
    """Environment without credentials. `replay` forces offline replay; the test suite runs without it, as `make test`
    does (several tests exercise live-mode code paths against recorded transports and fail if replay is forced)."""
    env = {k: v for k, v in os.environ.items()
           if not k.endswith(("_API_KEY", "_PAT_1", "_PAT_2", "_PAT_3")) and k != "AWS_BEARER_TOKEN_BEDROCK"}
    for k in ("BR_OFFLINE", "BR_LLM_REPLAY"):
        env.pop(k, None)
    if replay:
        env["BR_OFFLINE"] = "1"
        env["BR_LLM_REPLAY"] = "1"
    return env


def run(cmd: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None, timeout: int = 3600) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, env=env or _env(), capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def last(out: str, n: int = 3) -> str:
    return " | ".join(ln.strip() for ln in out.strip().splitlines()[-n:])[:200]


def scratch_seeded() -> Path:
    """A copy of data/seeded with venv paths rewritten and working trees restored (the live run is never locked)."""
    src = ROOT / "data" / "seeded"
    dst = Path(tempfile.mkdtemp(prefix="br-seeded-"))
    shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
    old = str(src)
    for f in (dst / "venvs").rglob("*"):
        if f.is_file() and not f.is_symlink() and (f.suffix in (".pth", ".cfg") or f.parent.name == "bin"):
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if old in text:
                f.write_text(text.replace(old, str(dst)), encoding="utf-8")
    for r in (dst / "repos").iterdir():
        subprocess.run(["git", "-C", str(r), "checkout", "-q", "--", "."], check=False)
    return dst


# -- individual checks ---------------------------------------------------------------------------


def check_tests() -> tuple[bool, str]:
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-p", "no:cacheprovider", *TEST_SUBSET], env=_env(replay=False))
    return rc == 0, last(out, 1)


def check_safety_tests() -> tuple[bool, str]:
    ids = sorted({t for item in cm.load()["safety"] for t in item["tests"]})
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-rs", "-p", "no:cacheprovider", *ids], env=_env(replay=False))
    skipped = re.search(r"(\d+) skipped", out)
    return rc == 0 and not skipped, f"{len(ids)} named tests; " + last(out, 1)


def check_demo_data() -> tuple[bool, str]:
    rc, out = run(["make", "demo-data"])
    wrote = [ln for ln in out.splitlines() if ln.startswith("wrote ")]
    return rc == 0, f"{len(wrote)} 'wrote' lines; " + (wrote[-1][:100] if wrote else last(out, 2))


def check_build() -> tuple[bool, str]:
    """`npm run build`. The first build fetches the three Google fonts; when that fails (offline, cold cache) the build is
    repeated with `demo-web/font-fallback.js`, which makes the page use the local font stack, and the detail says so."""
    env = {**os.environ, "NEXT_TELEMETRY_DISABLED": "1"}
    rc, out = run(["npm", "run", "build"], cwd=ROOT / "demo-web", env=env)
    note = ""
    if rc != 0 and "Google Fonts" in out:
        env["NEXT_FONT_GOOGLE_MOCKED_RESPONSES"] = str(ROOT / "demo-web/font-fallback.js")
        rc, out = run(["npm", "run", "build"], cwd=ROOT / "demo-web", env=env)
        note = " (Google Fonts unreachable: local font stack)"
    return rc == 0 and "Compiled successfully" in out, ("Compiled successfully" + note) if rc == 0 else last(out)


SECTION_IDS = ["overview", "data", "results", "compare"]
TABS = ["Live Lab", "Graph Explorer", "Evidence", "Use it"]
FORBIDDEN = ["outperforms", "state-of-the-art", "intelligent", "fixes any error", "guaranteed", "revolutionary", "seamless"]


def check_structure() -> tuple[bool, str]:
    """The four-tab site: the navigation in the built page, the four Evidence sections (ids, one element each), the
    try-it and use-it sections, the footer, the fonts, no forbidden words in the site text or its data, vendor URLs."""
    problems: list[str] = []
    comps = ROOT / "demo-web/components"
    text = "\n".join(f.read_text(encoding="utf-8") for f in list(comps.glob("*.tsx")) + list((comps / "lab").glob("*.tsx")))
    demo = (comps / "Demo.tsx").read_text(encoding="utf-8")
    app = (comps / "LabApp.tsx").read_text(encoding="utf-8")
    for sid in SECTION_IDS:
        if f'id: "{sid}"' not in demo:
            problems.append(f"Evidence table of contents lacks {sid}")
        if f'id="{sid}"' not in text:
            problems.append(f"no section element with id {sid}")
    for sid in ("try-it", "use-it"):
        if f'id="{sid}"' not in text:
            problems.append(f"no section element with id {sid}")
    for tab in TABS:
        if f'label: "{tab}"' not in app:
            problems.append(f"navigation lacks the {tab} tab")
    for need in ("Built from commit", "doi.org"):
        if need not in app:
            problems.append(f"footer lacks {need!r}")
    layout = (ROOT / "demo-web/app/layout.tsx").read_text(encoding="utf-8")
    for font in ("Source_Serif_4", "IBM_Plex_Sans", "IBM_Plex_Mono"):
        if font not in layout:
            problems.append(f"layout lacks {font}")
    html_files = list((ROOT / "demo-web/.next/server/app").glob("index.html"))
    if not html_files:
        problems.append("built index.html missing")
    else:
        html = html_files[0].read_text(encoding="utf-8")
        for tab in TABS:
            if tab not in html:
                problems.append(f"built page lacks the {tab} tab")
    blob = text + "\n" + "\n".join(p.read_text(encoding="utf-8") for p in DATA.glob("*.json"))
    for w in FORBIDDEN:
        if w in blob.lower():
            problems.append(f"forbidden word {w!r} in the site")
    ov = json.loads((DATA / "overview.json").read_text(encoding="utf-8"))
    if not ov.get("pr1") or not ov.get("built_from"):
        problems.append("overview.json lacks pr1 or built_from")
    problems += cm.validate_products(cm.load().get("products"))
    return not problems, ("4 tabs, 4 evidence sections, footer, fonts, no forbidden words, vendor URLs" if not problems
                          else "; ".join(problems[:4]))


def check_lab_tests() -> tuple[bool, str]:
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-p", "no:cacheprovider", "tests/test_lab.py", "tests/test_lab_breakit.py"],
                  env=_env(replay=False))
    return rc == 0, last(out, 1)


def check_arena() -> tuple[bool, str]:
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-p", "no:cacheprovider", "tests/test_lab_arena.py", "-k", "not coverage_plugin"],
                  env=_env(replay=False))
    return rc == 0, last(out, 1)


def check_coverage_plugin() -> tuple[bool, str]:
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-rs", "-p", "no:cacheprovider", "tests/test_lab_arena.py", "-k", "coverage_plugin"],
                  env=_env(replay=False))
    return rc == 0 and "skipped" not in out, last(out, 1)


def check_presenter() -> tuple[bool, str]:
    """Compile `demo-web/scripts/presenter_check.tsx` with the site's own TypeScript and render every screen of every
    recording with react-dom/server."""
    web = ROOT / "demo-web"
    out_dir = Path(tempfile.mkdtemp(prefix="br-presenter-"))
    try:
        rc, out = run(["npx", "tsc", "--outDir", str(out_dir), "--rootDir", ".", "--module", "commonjs", "--moduleResolution", "node",
                       "--jsx", "react-jsx", "--target", "es2020", "--esModuleInterop", "--skipLibCheck", "--resolveJsonModule",
                       "--strict", "scripts/presenter_check.tsx"], cwd=web)
        if rc != 0:
            return False, "tsc: " + last(out, 2)
        env = {**os.environ, "NODE_PATH": str(web / "node_modules")}
        rc, out = run(["node", str(out_dir / "scripts" / "presenter_check.js"), str(web / "public" / "lab" / "runs")], cwd=web, env=env)
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
    docs = [json.loads(ln) for ln in out.splitlines() if ln.startswith("{")]
    n = sum(len(d["screens"]) for d in docs)
    bad = [f"{d['recording']}/{s['id']}: {s['problem']}" for d in docs for s in d["screens"] if not s["ok"]]
    shown = sum(1 for d in docs for s in d["screens"] if s["state"] == "shown")
    return rc == 0 and not bad and n > 0, (f"{len(docs)} recordings x 8 screens: {shown} shown, {n - shown} with a stated reason"
                                           if not bad else "; ".join(bad[:3]))


def check_order_rule() -> tuple[bool, str]:
    """The tie-breaking rule against the hand-computed order of a recorded run. A failure here means the code is
    wrong; the expected order is ground truth and is never edited to make the check pass."""
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-p", "no:cacheprovider", "tests/test_lab_order.py"], env=_env(replay=False))
    return rc == 0 and "passed" in out and "skipped" not in out, last(out, 1)


def check_arena_columns() -> tuple[bool, str]:
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-p", "no:cacheprovider", "tests/test_lab_arena.py", "-k",
                   "columns or same_diff or diff_identity or cold_start or hand_counts"], env=_env(replay=False))
    return rc == 0 and "passed" in out, last(out, 1)


def check_challenge() -> tuple[bool, str]:
    rc, out = run(["uv", "run", *EXTRAS, "pytest", "-q", "-rs", "-p", "no:cacheprovider", "tests/test_lab_challenge.py"], env=_env(replay=False))
    return rc == 0 and "passed" in out, last(out, 1)


def check_text_budget() -> tuple[bool, str]:
    """Compile `demo-web/scripts/text_budget.tsx` and count paragraph lines in the server-rendered HTML of the idle page
    and of every result panel of every recording."""
    web = ROOT / "demo-web"
    out_dir = Path(tempfile.mkdtemp(prefix="br-budget-"))
    try:
        rc, out = run(["npx", "tsc", "--outDir", str(out_dir), "--rootDir", ".", "--module", "commonjs", "--moduleResolution", "node",
                       "--jsx", "react-jsx", "--target", "es2020", "--esModuleInterop", "--skipLibCheck", "--resolveJsonModule",
                       "--strict", "scripts/text_budget.tsx"], cwd=web)
        if rc != 0:
            return False, "tsc: " + last(out, 2)
        env = {**os.environ, "NODE_PATH": str(web / "node_modules")}
        rc, out = run(["node", str(out_dir / "scripts" / "text_budget.js"), str(web / "public" / "lab" / "runs")], cwd=web, env=env)
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
    docs = [json.loads(ln) for ln in out.splitlines() if ln.startswith("{")]
    bad = [f"{d['screen']}: " + (d.get("error") or "; ".join(f"{o['lines']} lines/{o['words']} words '{o['text'][:40]}'" for o in d["over"][:1]))
           for d in docs if d.get("error") or d.get("over") or d.get("ok") is False]
    n = sum(d.get("paragraphs", 0) for d in docs)
    return rc == 0 and not bad and len(docs) > 1, (f"{len(docs) - 1} screens, {n} visible paragraphs, none over 2 lines or 14 caption words"
                                                   if not bad else "; ".join(bad[:3]))


def check_review() -> tuple[bool, str]:
    """Compile `demo-web/scripts/review_check.tsx` and run it on the recorded runs."""
    web = ROOT / "demo-web"
    out_dir = Path(tempfile.mkdtemp(prefix="br-review-"))
    try:
        rc, out = run(["npx", "tsc", "--outDir", str(out_dir), "--rootDir", ".", "--module", "commonjs", "--moduleResolution", "node",
                       "--jsx", "react-jsx", "--target", "es2020", "--esModuleInterop", "--skipLibCheck", "--resolveJsonModule",
                       "--strict", "scripts/review_check.tsx"], cwd=web)
        if rc != 0:
            return False, "tsc: " + last(out, 2)
        env = {**os.environ, "NODE_PATH": str(web / "node_modules")}
        rc, out = run(["node", str(out_dir / "scripts" / "review_check.js"), str(web / "public" / "lab" / "runs")], cwd=web, env=env)
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
    docs = [json.loads(ln) for ln in out.splitlines() if ln.startswith("{")]
    bad = [f"{d['check']}: {d['detail']}" for d in docs if not d["ok"]]
    return rc == 0 and not bad and len(docs) == 8, (f"{len(docs)} checks: " + "; ".join(d["check"] for d in docs)) if not bad else "; ".join(bad[:2])[:300]


def check_meta_card() -> tuple[bool, str]:
    """Every number of the "vs Meta" card (pts.json) against `pts_comparison.md`, cell by cell, and Meta's two
    reported rates against the Meta column of `tab:pts` in the paper."""
    from analysis import export_demo_data as ex

    d = json.loads((DATA / "pts.json").read_text(encoding="utf-8"))
    src = GEN / "pts_comparison.md"
    md = src.read_text(encoding="utf-8")
    misses, n = [], 0
    for t in d["targets"]:
        n += 1
        _in(md, f"| {t['method']} | {t['test_recall_95']} | {t['change_recall_999']} |", misses, f"targets {t['method']}")
    for key, head in (("test_recall", "### micro TestRecall"), ("change_recall", "### ChangeRecall")):
        block = md.split(head, 1)[1].split("###", 1)[0]
        for c in d[key]:
            n += len(c["points"])
            _in(block, "| " + " | ".join([c["method"], *(f"{p['value']:.3f}" for p in c["points"])]) + " |", misses, f"{key} {c['method']}")
    n += 1
    _in(md, f"| candidate test files | {d['candidates_mean']} | {d['candidates_median']} |", misses, "candidates")
    ours = next((t for t in d["targets"] if t["method"] == "BlastRadius ranker"), None)
    if not ours or (ours["test_recall_95"], ours["change_recall_999"]) != ("0.764", "0.997"):
        misses.append(f"ours is not (0.764, 0.997): {ours}")
    tex = {ex.tex_plain(r[0]): ex.tex_plain(r[1]) for r in ex.tex_table("tab:pts")}
    for key, label in (("test_recall", "TestRecall"), ("change_recall", "ChangeRecall")):
        n += 1
        row = next((v for k, v in tex.items() if k.startswith(f"Rate for {label}")), None)
        if row != d["meta"][key]["rate"]:
            misses.append(f"Meta {label}: card {d['meta'][key]['rate']!r}, tab:pts {row!r}")
    return not misses, f"{n} numbers equal pts_comparison.md / tab:pts" if not misses else "; ".join(misses[:3])


def check_glance() -> tuple[bool, str]:
    """glance.json against a fresh read of tab:glance: same rows, same cells, same order; every chip one of five."""
    from analysis import export_demo_data as ex

    d = json.loads((DATA / "glance.json").read_text(encoding="utf-8"))
    fresh = ex.glance_doc(d["generated_at_git_sha"])["rows"]
    tex = (ROOT / "paper/full/main.tex").read_text(encoding="utf-8")
    body = tex.split("\\label{tab:glance}", 1)[1].split("\\midrule", 1)[1].split("\\bottomrule", 1)[0]
    n_tex = sum(1 for ln in body.split("\\\\") if "&" in ln)
    chips = {"better", "tie", "lower", "different task", "illustration"}
    problems = []
    if d["rows"] != fresh:
        problems.append("glance.json differs from tab:glance (run make demo-data)")
    if len(d["rows"]) != n_tex:
        problems.append(f"{len(d['rows'])} rows, tab:glance has {n_tex}")
    problems += [f"chip {r['chip']!r}" for r in d["rows"] if r["chip"] not in chips]
    return not problems, f"{len(d['rows'])} rows equal tab:glance" if not problems else "; ".join(problems[:3])


def check_no_bite() -> tuple[bool, str]:
    """No "BITE" string in demo-web, generated data included (node_modules and the build output excluded)."""
    web = ROOT / "demo-web"
    hits = []
    for f in web.rglob("*"):
        rel = f.relative_to(web)
        if not f.is_file() or rel.parts[0] in ("node_modules", ".next") or f.suffix in (".png", ".pdf", ".ico", ".woff2"):
            continue
        if "BITE" in f.read_text(encoding="utf-8", errors="ignore"):
            hits.append(str(rel))
    return not hits, "no BITE in demo-web" if not hits else f"BITE in {hits[:4]}"


def check_ledger() -> tuple[bool, str]:
    """The lab's calls are counted in its own ledger: the client defaults to it, the lab code never names E3's ledger,
    no lab row sits in usage.jsonl, and the ledger tests pass."""
    problems = []
    lab = ROOT / "eval/llm_cache/lab_usage.jsonl"
    e3 = ROOT / "eval/llm_cache/usage.jsonl"
    lab_rows = set(lab.read_text(encoding="utf-8").splitlines()) if lab.exists() else set()
    e3_rows = set(e3.read_text(encoding="utf-8").splitlines()) if e3.exists() else set()
    if lab_rows & e3_rows:
        problems.append(f"{len(lab_rows & e3_rows)} lab row(s) also in usage.jsonl")
    for f in (ROOT / "src/lab").rglob("*.py"):
        if "USAGE_LEDGER" in f.read_text(encoding="utf-8"):
            problems.append(f"{f.relative_to(ROOT)} names USAGE_LEDGER")
    rc, out = run(["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_lab_ledger.py"], env=_env(replay=False))
    if rc != 0:
        problems.append("ledger tests: " + last(out, 1))
    return not problems, (f"lab_usage.jsonl {len(lab_rows)} row(s), none in usage.jsonl; " + last(out, 1)) if not problems else "; ".join(problems[:3])


def check_lab_runs() -> tuple[bool, str]:
    """Every recorded run: schema-valid events, a header, a run.end, a full graph file; and `--mode replay` through the
    CLI reproduces its events exactly (except `ts` and the `replay` flag)."""
    from src.lab.events import validate_event

    runs = sorted((ROOT / "demo-web/public/lab/runs").glob("*.jsonl"))
    if not runs:
        return False, "no recorded runs"
    problems: list[str] = []
    for p in runs:
        evs = [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
        bad = [(e.get("seq"), v) for e in evs for v in [validate_event(e)] if v]
        if bad:
            problems.append(f"{p.stem}: {len(bad)} invalid, first {bad[0]}")
        if evs[0]["type"] != "run.header" or evs[-1]["type"] != "run.end":
            problems.append(f"{p.stem}: header or end missing")
        if not p.with_suffix(".graph.json").exists():
            problems.append(f"{p.stem}: graph file missing")
        rc, out = run(["uv", "run", "--extra", "graph", "python", "-m", "src.lab", "run", "--mode", "replay", p.stem,
                       "--speed", "100000"])
        got = [json.loads(ln) for ln in out.splitlines() if ln.startswith("{")]
        strip = lambda e: {k: v for k, v in e.items() if k not in ("ts", "replay")}   # noqa: E731
        if rc != 0 or [strip(e) for e in got] != [strip(e) for e in evs] or not all(e.get("replay") for e in got):
            problems.append(f"{p.stem}: replay differs ({len(got)} of {len(evs)} events)")
    return not problems, f"{len(runs)} recorded run(s) valid and replayed" if not problems else "; ".join(problems[:3])


def check_lab_api() -> tuple[bool, str]:
    """Start the built site on a spare port and call every /api/lab route once, including a real run."""
    import urllib.error
    import urllib.request

    port = 3217
    env = {**os.environ, "NEXT_TELEMETRY_DISABLED": "1"}
    env.pop("GROQ_API_KEY", None)
    # the check's run must not add to the lab's failure-history store or coverage cache: give it its own temp root
    env["TMPDIR"] = tempfile.mkdtemp(prefix="br-demo-check-")
    proc = subprocess.Popen(["npx", "next", "start", "-H", "127.0.0.1", "-p", str(port)], cwd=ROOT / "demo-web", env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    base = f"http://127.0.0.1:{port}"
    problems: list[str] = []

    def get(path: str, timeout: int = 180, headers: dict | None = None, data: bytes | None = None) -> tuple[int, bytes]:
        req = urllib.request.Request(base + path, headers=headers or {}, data=data)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    try:
        for _ in range(60):
            try:
                get("/api/lab/run", timeout=5)
                break
            except Exception:  # noqa: BLE001
                time.sleep(1)
        else:
            return False, "server did not start"
        st, body = get("/api/lab/run")
        if st != 200 or not json.loads(body).get("live"):
            problems.append(f"GET run: {st}")
        st, _ = get("/api/lab/run", headers={"Host": "evil.example"})
        if st != 403:
            problems.append(f"localhost guard: {st}")
        st, body = get("/api/lab/repos")
        names = sorted(r["name"] for r in json.loads(body).get("repos", [])) if st == 200 else []
        if names != ["click", "itsdangerous", "markupsafe", "shopcart"]:
            problems.append(f"repos: {st} {names}")
        st, body = get("/api/lab/mutations?repo=shopcart&file=shopcart/cart.py")
        if st != 200 or not json.loads(body).get("functions"):
            problems.append(f"mutations: {st}")
        st, body = get("/api/lab/file?repo=shopcart&path=shopcart/cart.py")
        if st != 200 or "class Cart" not in json.loads(body).get("text", ""):
            problems.append(f"file: {st}")
        st, _ = get("/api/lab/file?repo=shopcart&path=../../etc/passwd")
        if st != 400:
            problems.append(f"path traversal not refused: {st}")
        st, body = get("/api/lab/graph?repo=shopcart")
        if st != 200 or not json.loads(body).get("nodes"):
            problems.append(f"graph: {st}")
        name = sorted(p.stem for p in (ROOT / "demo-web/public/lab/runs").glob("*.jsonl"))[0]
        st, body = get(f"/api/lab/replay?name={name}&speed=50")
        n = sum(1 for ln in body.decode().splitlines() if ln.startswith("data: "))
        if st != 200 or n < 10:
            problems.append(f"replay: {st}, {n} events")
        st, body = get("/api/lab/run", data=json.dumps({"repo": "shopcart", "task": "shopcart-CMP_FLIP-00", "noLlm": True}).encode(),
                       headers={"Content-Type": "application/json"}, timeout=240)
        evs = [json.loads(ln[6:]) for ln in body.decode().splitlines() if ln.startswith("data: ")]
        if st != 200 or not evs or evs[-1]["type"] != "run.end" or evs[-1]["status"] != "ok":
            problems.append(f"run: {st}, {len(evs)} events, last {evs[-1]['type'] if evs else None}")
    finally:
        try:
            os.killpg(proc.pid, 15)
        except OSError:
            pass
    return not problems, "7 routes, guard, one live run" if not problems else "; ".join(problems[:3])


def check_agents_demo() -> tuple[bool, str]:
    """The `make agents-demo` command, exported to a scratch file so the site's recorded agents.json is not rewritten."""
    out = Path(tempfile.mkdtemp(prefix="br-agents-")) / "agents.json"
    try:
        rc, log = run(["uv", "run", "--extra", "graph", "python", "-m", "src.agents", "demo", "--export", str(out)])
        n = len(json.loads(out.read_text(encoding="utf-8")).get("scenarios", [])) if rc == 0 and out.exists() else 0
    finally:
        shutil.rmtree(out.parent, ignore_errors=True)
    return rc == 0 and n == 4, f"{n} scenarios" if rc == 0 else last(log)


def check_ask(seeded: Path) -> tuple[bool, str]:
    answers = ROOT / "eval/ask/answers.json"
    before = answers.read_bytes()
    try:
        rc, out = run(["uv", "run", "--extra", "ml", "--extra", "rag", "python", "-m", "analysis.ask_eval", "report"],
                      env={**_env(), "BR_SEEDED_DIR": str(seeded)})
        doc = json.loads(answers.read_text(encoding="utf-8"))
    finally:
        answers.write_bytes(before)         # the replay flips `from_cache`; the committed record stays as recorded
    qs = doc["questions"]
    same = [{k: v for k, v in q.items() if k != "from_cache"} for q in qs] == \
           [{k: v for k, v in q.items() if k != "from_cache"} for q in json.loads(before)["questions"]]
    ok = rc == 0 and len(qs) == 15 and all(q.get("from_cache") for q in qs) and same
    return ok, f"{len(qs)} questions replayed from cache; answers identical to the record: {same}"


def check_bot(seeded: Path) -> tuple[bool, str]:
    comment = ROOT / "src/agents/demo/bot_comment.md"
    before = comment.read_bytes()
    try:
        rc, out = run(["uv", "run", "--extra", "graph", "--extra", "ml", "--extra", "rag", "python", "-m", "analysis.bot_demo", "replay"],
                      env={**_env(), "BR_SEEDED_DIR": str(seeded)})
        after = comment.read_bytes()
    finally:
        comment.write_bytes(before)
    return rc == 0 and after == before, f"comment {len(after):,} bytes, byte-identical: {after == before}"


def loaded_json_names() -> set[str]:
    names: set[str] = set()
    for f in (ROOT / "demo-web").glob("components/*.tsx"):
        text = f.read_text(encoding="utf-8")
        names |= set(re.findall(r'"/data/([A-Za-z0-9_./-]+\.json)"', text))
        names |= {f"{n}.json" for n in re.findall(r'load<[^>]*>\(\s*"(\w+)"', text)}
        names |= {f"{n}.json" for n in re.findall(r'useDoc<[\s\S]*?>\(\s*"(\w+)"', text)}
        names |= set(re.findall(r"`/data/([A-Za-z0-9_./-]+\.json)`", text))
    return names


def check_json() -> tuple[bool, str]:
    names = loaded_json_names() - {n for n in loaded_json_names() if "${" in n}
    index = json.loads((DATA / "index.json").read_text(encoding="utf-8"))
    names |= {f"instances/{i['id']}.json" for i in index["instances"]}
    missing = sorted(n for n in names if not (DATA / n).exists())
    bad = []
    for p in DATA.rglob("*.json"):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            bad.append(p.name)
    return not missing and not bad, f"{len(names)} referenced, missing {missing or 'none'}, unparsable {bad or 'none'}"


def _in(text: str, needle: str, misses: list[str], what: str) -> None:
    if needle not in text:
        misses.append(f"{what}: {needle!r}")


def check_numbers() -> tuple[bool, str]:
    """Panels 2 and 4 of compare.json against the generated files they were read from."""
    from analysis.slide_figures import wilson

    d = json.loads((DATA / "compare.json").read_text(encoding="utf-8"))
    misses: list[str] = []
    n = 0
    e1 = (GEN / "rq2_predictor.md").read_text(encoding="utf-8")
    for r in (d["e1"] or {}).get("rows", []):
        for needle in (r["recall10"], r["map"], f"[{r['ci'][0]:.3f}, {r['ci'][1]:.3f}]", r["p_adj_text"], r["delta"]):
            if needle is not None:
                n += 1
                _in(e1, needle, misses, f"E1 {r['id']}")
    if d["e1"]:
        n += 1
        _in(e1, d["e1"]["verdict"], misses, "E1 verdict")
    e3 = (GEN / "rq4_repair.md").read_text(encoding="utf-8")
    for m in (d["e3"] or {}).get("models", []):
        for a in m["arms"]:
            n += 2
            _in(e3, f"| {a['arm']} | {a['n']} | {a['k']}/{a['n']} (", misses, f"E3 {m['model']} {a['arm']}")
            lo, hi = wilson(a["k"], a["n"])
            if abs(lo - a["wilson"][0]) > 1e-9 or abs(hi - a["wilson"][1]) > 1e-9:
                misses.append(f"E3 {m['model']} {a['arm']}: Wilson interval differs from analysis.slide_figures.wilson")
    if d["e3"]:
        n += 1
        _in(e3, d["e3"]["primary"], misses, "E3 primary test")
    rq5 = (GEN / "rq5_retrieval.md").read_text(encoding="utf-8")
    for rows in (d["localization"] or {}).get("variants", {}).values():
        for r in rows:
            n += 1
            _in(rq5, f"| {r['cell']} |", misses, f"L {r['mode']}")
    cost_md = (GEN / "cost_report.md").read_text(encoding="utf-8") if (GEN / "cost_report.md").exists() else ""
    cost_json = json.loads((GEN / "cost_report.json").read_text(encoding="utf-8")) if (GEN / "cost_report.json").exists() else None
    # the Live Lab's ledger (D-65) is read by export_demo_data directly, so compare.json may carry it before the committed
    # report is regenerated: those two keys are checked against the ledger itself, everything else against the report
    lab_keys = ("lab_ledger", "lab")
    if d["cost"] is not None and cost_json is not None:
        from analysis import cost_report as cr

        core = {k: v for k, v in d["cost"].items() if k not in lab_keys or k in cost_json}
        if core != cost_json:
            misses.append("panel 4: compare.json cost differs from paper/generated/cost_report.json")
        if "lab_ledger" in d["cost"] and d["cost"]["lab_ledger"] != cr.ledger_summary(cr.LAB_LEDGER):
            misses.append("panel 4: compare.json lab_ledger differs from eval/llm_cache/lab_usage.jsonl")
        if "lab" in d["cost"] and d["cost"]["lab"] != cr.recorded_runs("lab"):
            misses.append("panel 4: compare.json lab runs differ from eval/llm_cache/lab_*.jsonl")
    elif d["cost"] != cost_json:
        misses.append("panel 4: compare.json cost differs from paper/generated/cost_report.json")
    if d["cost"]:
        for r in d["cost"]["e3"]:
            for key, dec in (("in_per_task", 0), ("out_per_task", 0), ("in_per_fix", 0), ("out_per_fix", 0),
                             ("usd_list_per_task", 5), ("usd_list_per_fix", 5)):
                if r[key] is not None:
                    n += 1
                    _in(cost_md, f"{r[key]:,.{dec}f}", misses, f"cost {r['model']} {r['arm']} {key}")
        n += 1
        _in(cost_md, f"USD actually paid: {d['cost']['ledger']['paid_usd']:.2f}", misses, "paid USD")
    return not misses, f"{n} numbers checked" + (f"; {len(misses)} not found: {misses[:3]}" if misses else "")


# -- D-69..D-71 ------------------------------------------------------------------------------------
GUIDED_AUDIT = ROOT / "demo-web/public/lab/runs/audit/guided-demo.jsonl"


def check_provider() -> tuple[bool, str]:
    """D-69: the provider tests (recorded 429 -> Bedrock, budget refusal, cache-key separation) pass, and the status the
    model chip reads names Bedrock when it is forced and Groq otherwise (no network)."""
    rc, out = run(["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_llm_provider.py"], env=_env(replay=False))
    code = ("import json,os;from src.agents.llm_provider import status;"
            "os.environ.update(GROQ_API_KEY='x'*20,AWS_BEARER_TOKEN_BEDROCK='y'*20);a=status('openai/gpt-oss-120b')['provider'];"
            "os.environ['BR_LLM_PROVIDER']='bedrock';b=status('openai/gpt-oss-120b')['provider'];print(json.dumps([a,b]))")
    rc2, out2 = run(["uv", "run", "python", "-c", code], env={k: v for k, v in _env(replay=False).items()
                                                               if k not in ("BR_LLM_PROVIDER",)})
    got = next((json.loads(ln) for ln in out2.splitlines() if ln.startswith("[")), None)
    ok = rc == 0 and rc2 == 0 and got == ["groq", "bedrock"]
    return ok, f"provider tests: {last(out, 1)}; chip provider default/forced: {got}"


def check_audit_guided() -> tuple[bool, str]:
    """D-71: `audit verify` passes on the guided-demo run's log, and the log is the one the recording streamed."""
    rc, out = run(["uv", "run", "python", "-m", "src.agents.audit", "verify", str(GUIDED_AUDIT)])
    recs = [json.loads(ln) for ln in GUIDED_AUDIT.read_text(encoding="utf-8").splitlines() if ln.strip()]
    evs = [json.loads(ln) for ln in (ROOT / "demo-web/public/lab/runs/guided-demo.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
    streamed = [e["data"] for e in evs if e["type"] == "audit.record"]
    same = streamed == recs
    return rc == 0 and out.startswith("OK") and same, f"{out.strip().splitlines()[-1][:90]}; streamed records identical: {same}"


def check_fixpr() -> tuple[bool, str]:
    """D-70: the fix-PR gate tests (default branch, allowlist, failed checks, ask without approval) pass."""
    rc, out = run(["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_fixpr.py"], env=_env(replay=False))
    return rc == 0, last(out, 1)


def check_agent_logs_secret_free() -> tuple[bool, str]:
    """No credential in logs/agent: the release secret scanner's BLOCKER classes, and no value of a credential-named
    variable of the environment or of .env (read in memory, never printed)."""
    from analysis.secret_scan import scan_text
    from src.agents.audit import secret_values

    env = dict(os.environ)
    dot = ROOT / ".env"
    if dot.exists():
        for ln in dot.read_text(encoding="utf-8").splitlines():
            if "=" in ln and not ln.lstrip().startswith("#"):
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    secrets = secret_values(env)
    root = ROOT / "logs/agent"
    files = [p for p in root.rglob("*") if p.is_file()] if root.exists() else []
    files += [GUIDED_AUDIT]
    bad = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        if any(scan_text(text).get(c) for c in ("github_token", "bearer_token")) or any(s in text for s in secrets):
            bad.append(str(p.relative_to(ROOT)))
    return not bad, f"{len(files)} file(s) scanned, {len(secrets)} credential value(s) checked, none found" if not bad else f"secret in {bad[:3]}"


def main() -> int:
    rows: list[tuple[str, bool, str, float]] = []
    seeded: Path | None = None
    steps = [("make test subset (agents, bot, rag, e3 replay, slide figures, ask, safety)", check_tests),
             ("safety checklist: named tests pass, none skipped", check_safety_tests),
             ("make demo-data", check_demo_data),
             ("npm run build", check_build),
             ("site structure: four tabs, evidence sections, footer, fonts, wording, vendor sources", check_structure),
             ("agents demo, 4 recorded scenarios (the make agents-demo command)", check_agents_demo),
             ("Ask replay of the 15 recorded questions", None),
             ("PR bot replay on the recorded task", None),
             ("every JSON file the website loads exists and parses", check_json),
             ("Compare panels 2 and 4 match their generated sources", check_numbers),
             ("live lab engine tests (stage order, streaming, replay, injection, no writes, test gap, probe, PR)", check_lab_tests),
             ("recorded lab runs: schema-valid and replay identically", check_lab_runs),
             ("/api/lab/* smoke calls on a started server", check_lab_api),
             ("strategy arena against a recorded run, hand-counted values", check_arena),
             ("coverage plugin on itsdangerous: same function sets in two runs", check_coverage_plugin),
             ("presenter: every screen renders from every recording", check_presenter),
             ("token ledgers separated (lab_usage.jsonl vs usage.jsonl)", check_ledger),
             ("BlastRadius test-case order against the hand-computed order of a recorded run", check_order_rule),
             ("arena columns, and the history row with and without runs of the same diff", check_arena_columns),
             ("reviewer challenge: the same seed names the same bug", check_challenge),
             ("text budget of the main screen in server-rendered HTML (2 lines, 14 caption words)", check_text_budget),
             ("review lab: model chip, guided demo on its recording, recorded-repair fallback, slider", check_review),
             ("vs Meta card numbers equal pts_comparison.md and tab:pts", check_meta_card),
             ("results-at-a-glance rows equal tab:glance of paper/full/main.tex", check_glance),
             ("no BITE string in demo-web", check_no_bite),
             ("provider chip and Groq -> Bedrock fallback (D-69)", check_provider),
             ("Decisions tab renders from the recorded run (review check above) and audit verify passes on it (D-71)", check_audit_guided),
             ("fix-PR gate refusals (D-70)", check_fixpr),
             ("no secret in logs/agent (D-71)", check_agent_logs_secret_free)]
    try:
        for name, fn in steps:
            t0 = time.time()
            try:
                if fn is None:
                    seeded = seeded or scratch_seeded()
                    ok, detail = (check_ask if name.startswith("Ask") else check_bot)(seeded)
                else:
                    ok, detail = fn()
            except Exception as exc:          # a crashed check is a FAIL, not a crash of the report
                ok, detail = False, f"{type(exc).__name__}: {exc}"[:200]
            rows.append((name, ok, detail, time.time() - t0))
            print(f"{'PASS' if ok else 'FAIL'}  {name}  ({time.time() - t0:.0f}s)", flush=True)
    finally:
        if seeded:
            shutil.rmtree(seeded, ignore_errors=True)
    w = max(len(r[0]) for r in rows)
    print("\n" + "=" * (w + 14))
    print(f"{'check':<{w}}  result")
    for name, ok, detail, _ in rows:
        print(f"{name:<{w}}  {'PASS' if ok else 'FAIL'}  {detail}")
    bad = [r for r in rows if not r[1]]
    print(f"\ndemo-check: {len(rows) - len(bad)} of {len(rows)} PASS" + ("" if not bad else f"; FAIL: {', '.join(r[0] for r in bad)}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
