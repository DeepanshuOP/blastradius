"""`python -m src.lab ...`: stdout carries one JSON event per line and nothing else; diagnostics go to stderr.

    run --repo itsdangerous --task itsdangerous-ARITH_SWAP-00 [--variant hard]
    run --repo markupsafe --inject src/markupsafe/__init__.py::escape::CMP_FLIP[::LINE]
    run --repo shopcart --edit shopcart/cart.py=@/path/to/new_text
    run --url https://github.com/o/r (--inject ... | --edit ...)
    run ... --model openai/gpt-oss-120b --record NAME [--no-llm]
    run --mode replay NAME [--speed 2]
    repos | mutations --repo R --file F | tasks [--repo R] | status
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "demo-web" / "public" / "lab" / "runs"


def log(*a: object) -> None:
    print(*a, file=sys.stderr, flush=True)


def _replay(name: str, speed: float) -> int:
    from src.lab.events import validate_event

    path = RUNS / f"{name}.jsonl"
    if not name.replace("-", "").replace("_", "").isalnum() or not path.is_file():
        log(f"no recorded run named {name!r}")
        return 2
    prev: float | None = None
    from datetime import datetime

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ev = json.loads(line)
        t = datetime.fromisoformat(ev["ts"]).timestamp()
        if prev is not None and speed > 0:
            time.sleep(min(max(t - prev, 0) / speed, 4.0 / max(speed, 0.1)))   # long pauses are capped at 4 s
        prev = t
        ev["replay"] = True
        sys.stdout.write(json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n")
        sys.stdout.flush()
    return 0


@contextlib.contextmanager
def _lock():
    from src.lab.workspace import LAB_ROOT

    LAB_ROOT.mkdir(parents=True, exist_ok=True)
    fh = open(LAB_ROOT / "lock", "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fh.close()
        raise SystemExit("another lab run is active")
    try:
        yield
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def _parse_run(ns: argparse.Namespace):
    from src.lab.engine import LabArgs

    a = LabArgs(repo=ns.repo, url=ns.url, pr=ns.pr, task=ns.task, variant=ns.variant, model=ns.model, use_llm=not ns.no_llm,
                record=ns.record, timeout=ns.timeout, install=not ns.no_install, title=ns.title,
                description=ns.description, command=sys.argv[1:], repair_arena=ns.repair_arena)
    if ns.base_patch:
        a.base_patch = Path(ns.base_patch).read_text(encoding="utf-8")
    if ns.inject:
        parts = ns.inject.split("::")
        if len(parts) not in (3, 4):
            raise SystemExit("--inject FILE::FUNCTION::OPERATOR[::LINE]")
        a.inject = (parts[0], parts[1], parts[2], int(parts[3]) if len(parts) == 4 else None)
    if ns.edit:
        path, _, tmp = ns.edit.partition("=@")
        a.edit = (path, Path(tmp).read_text(encoding="utf-8"))
    return a


def cmd_run(ns: argparse.Namespace) -> int:
    from src.lab.engine import MODELS

    mode = ns.mode[0] if ns.mode else "live"
    if mode == "replay":
        if len(ns.mode) < 2:
            raise SystemExit("--mode replay NAME")
        return _replay(ns.mode[1], ns.speed)
    if mode != "live":
        raise SystemExit("--mode live | replay NAME")
    if ns.model not in MODELS:
        raise SystemExit(f"--model must be one of {', '.join(MODELS)}")
    if sum(map(bool, (ns.repo, ns.url, ns.pr))) != 1:
        raise SystemExit("give exactly one of --repo / --url / --pr")
    args = _parse_run(ns)
    from src.lab.engine import Lab
    from src.lab.events import Emitter

    def stop(_s, _f):  # noqa: ANN001
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    rec = None
    if args.record:
        if not args.record.replace("-", "").replace("_", "").isalnum():
            raise SystemExit("--record NAME: letters, digits, - and _ only")
        RUNS.mkdir(parents=True, exist_ok=True)
        rec = open(RUNS / f"{args.record}.jsonl", "w", encoding="utf-8")
    events_out = sys.stdout
    sys.stdout = sys.stderr            # vendored libraries print status lines; stdout carries events and nothing else
    em = Emitter(events_out, rec)
    llm = None
    key_present = bool(os.environ.get("GROQ_API_KEY"))
    if args.use_llm and key_present:
        from src.lab.cache import LabGroqLLM, for_model

        cache = for_model(args.model)
        llm = LabGroqLLM(api_key=os.environ["GROQ_API_KEY"], model=args.model, cache=cache, max_retries=0)
    with _lock():
        lab = Lab(args, em, llm)
        try:
            rc = lab.run()
            em.emit("meta", "run.end", "ok", {"seq_count": em.seq + 1})
        except KeyboardInterrupt:
            em.emit("meta", "run.end", "failed", {"reason": "cancelled"})
            rc = 130
        except Exception as exc:  # noqa: BLE001 - surfaced as an event, never swallowed
            import traceback

            log(traceback.format_exc())
            em.emit("meta", "run.end", "failed", {"reason": f"{type(exc).__name__}: {exc}"[:500]})
            rc = 1
        finally:
            if rec:
                gf = getattr(lab, "graph_file", None)
                if gf and Path(gf).exists():
                    (RUNS / f"{args.record}.graph.json").write_bytes(Path(gf).read_bytes())
                rec.close()
                write_index()
            lab.cleanup()
    return rc


def _test_cases(slug: str, commit: str) -> int | None:
    """Number of collected test cases, counted by pytest in a scratch copy and cached by commit."""
    import shutil
    import subprocess

    from src.lab.workspace import LAB_ROOT, new_scratch, prepare_seeded

    cache = LAB_ROOT / f"cases-{slug}-{commit[:12]}.json"
    if cache.exists():
        return json.loads(cache.read_text())["n"]
    scratch = new_scratch("count")
    try:
        ws = prepare_seeded(slug, scratch)
        if not ws.python:
            return None
        paths = [str(ws.repo_dir)] + ([str(ws.repo_dir / "src")] if (ws.repo_dir / "src").is_dir() else [])
        p = subprocess.run([ws.python, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"], cwd=ws.repo_dir,
                           capture_output=True, text=True, timeout=120,
                           env={**os.environ, "PYTHONPATH": os.pathsep.join(paths), "PYTHONDONTWRITEBYTECODE": "1"})
        n = sum(1 for ln in p.stdout.splitlines() if "::" in ln)
        cache.write_text(json.dumps({"n": n}))
        return n
    except Exception:  # noqa: BLE001
        return None
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def write_index() -> None:
    """`demo-web/public/lab/runs/index.json`: the recorded runs, so a static build can list them."""
    out = []
    for p in sorted(RUNS.glob("*.jsonl")):
        try:
            first = json.loads(p.read_text(encoding="utf-8").split("\n", 1)[0])["data"]
        except Exception:  # noqa: BLE001
            continue
        out.append({"name": p.stem, "date": first.get("date"), "model": first.get("model"), "git_sha": first.get("git_sha"),
                    "title": first.get("title"), "description": first.get("description")})
    (RUNS / "index.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def cmd_index(_ns: argparse.Namespace) -> int:
    write_index()
    return 0


def cmd_rederive(ns: argparse.Namespace) -> int:
    """Apply the 2026-10-12 test-case rule to recordings made before it (offline; see `src/lab/rederive.py`)."""
    from src.lab import rederive

    out = []
    with _lock():
        for name in ns.names:
            out.append(rederive.run(name, RUNS, write=not ns.dry_run))
    print(json.dumps(out, indent=1))
    if not ns.dry_run:
        write_index()
    return 0


def cmd_repos(ns: argparse.Namespace) -> int:
    from src.lab import changes
    from src.lab.workspace import PREPARED, REPOS, VENVS, count_files, git, prepared_info

    out = []
    pins = prepared_info()
    for slug in PREPARED:
        d = REPOS / slug
        if not d.is_dir():
            continue
        n_py, n_java, _ = count_files(d)
        tests = sum(1 for p in d.rglob("test*.py") if "__pycache__" not in p.parts)
        out.append({"name": slug, "url": pins.get(slug, {}).get("url"), "commit": git(d, "rev-parse", "HEAD"),
                    "language": "python", "n_files": n_py + n_java, "test_files": tests,
                    "n_tests": _test_cases(slug, git(d, "rev-parse", "HEAD")),
                    "runnable": (VENVS / slug / "bin" / "python").exists(),
                    "tasks": changes.list_tasks(slug)})
    runs = []
    if RUNS.is_dir():
        for p in sorted(RUNS.glob("*.jsonl")):
            first = p.read_text(encoding="utf-8").split("\n", 1)[0]
            try:
                hdr = json.loads(first)["data"]
            except Exception:  # noqa: BLE001
                hdr = {}
            runs.append({"name": p.stem, "date": hdr.get("date"), "model": hdr.get("model"),
                         "git_sha": hdr.get("git_sha"), "title": hdr.get("title"), "description": hdr.get("description")})
    print(json.dumps({"repos": out, "runs": runs, "llm": bool(os.environ.get("GROQ_API_KEY"))}))
    return 0


def cmd_mutations(ns: argparse.Namespace) -> int:
    from src.lab import changes
    from src.lab.workspace import PREPARED, REPOS

    if ns.repo not in PREPARED:
        raise SystemExit("unknown repo")
    p = (REPOS / ns.repo / ns.file).resolve()
    if REPOS.resolve() not in p.parents or not p.is_file() or p.suffix != ".py":
        raise SystemExit("not a Python file of the repository")
    print(json.dumps({"file": ns.file, "functions": changes.mutations_of(p.read_text(encoding="utf-8"))}))
    return 0


def cmd_tasks(ns: argparse.Namespace) -> int:
    from src.lab import changes

    print(json.dumps(changes.list_tasks(ns.repo)))
    return 0


def cmd_graph(ns: argparse.Namespace) -> int:
    """The whole graph of a prepared repository at its pinned commit (cached under the lab's temp directory)."""
    from src.graph.build import build_graph_at, load_graph
    from src.lab import graphview
    from src.lab.workspace import LAB_ROOT, PREPARED, git, new_scratch, prepare_seeded
    import shutil

    if ns.repo not in PREPARED:
        raise SystemExit("unknown repo")
    scratch = new_scratch("graph")
    try:
        ws = prepare_seeded(ns.repo, scratch)
        cache = LAB_ROOT / "graphs" / f"repo-{ns.repo}-{ws.base[:12]}.json"
        if not cache.exists():
            st = build_graph_at(f"lab/{ws.name}", ws.base, clone_dir=ws.repo_dir, out_dir=scratch / "graphs")
            view = graphview.to_cytoscape(load_graph(st.graph_path))
            view.update({"repo": ws.name, "commit": ws.base, "parse_failures": st.n_parse_failures,
                         "files_considered": st.n_files_considered, "failed_source_files": st.failed_source_files[:30],
                         "counts": graphview.count_by_type(view)})
            graphview.store(view, cache)
        sys.stdout.write(cache.read_text(encoding="utf-8"))
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


#: Tokens one lab repair call may take (prompt about 1,000, completion budget 1,500, with slack); used for headroom only.
CALL_ESTIMATE = 4000


def quota() -> dict:
    """Per model: tokens in the rolling 24 h over E3's ledger and the lab's together, against the daily cap."""
    from datetime import datetime, timezone

    from src.lab.cache import QUOTA_LEDGERS, day_tokens
    from src.lab.engine import MODELS

    cap = int(os.environ.get("BR_GROQ_TPD") or 200000)
    now = time.time()
    out = {}
    for m in MODELS:
        used, oldest = day_tokens(m, now)
        ok = used + CALL_ESTIMATE <= cap
        out[m] = {"used": used, "cap": cap, "ok": ok, "ledgers": [p.name for p in QUOTA_LEDGERS],
                  "resume_after": None if ok or oldest is None else
                  datetime.fromtimestamp(oldest + 86400, timezone.utc).isoformat(timespec="minutes")}
    return out


PROBE_MAX = 5
PROBE_CAP_S = 60


def cmd_probe(ns: argparse.Namespace) -> int:
    """Suite strength on one function: up to five mutants, one at a time, each against the full suite (no model).

    Stops at the cap (60 s per repository) and says so. Events go to stdout like a run's.
    """
    import shutil

    from src.agents.regression import run_pytest
    from src.eval.seeded import mutate
    from src.lab.events import Emitter, now_iso
    from src.lab.workspace import PREPARED, new_scratch, prepare_seeded

    if ns.repo not in PREPARED:
        raise SystemExit("unknown repo")
    events_out = sys.stdout
    sys.stdout = sys.stderr
    em = Emitter(events_out)
    with _lock():
        scratch = new_scratch("probe")
        try:
            em.emit("meta", "run.header", "ok", {"date": now_iso(), "mode": "probe", "model": None, "llm": "not used",
                                                 "run_id": f"probe-{ns.repo}", "command": ["python", "-m", "src.lab", *sys.argv[1:]],
                                                 "title": f"Suite strength: {ns.function}", "cap_s": PROBE_CAP_S})
            ws = prepare_seeded(ns.repo, scratch)
            em.emit("repo", "repo.info", "ok", {"name": ws.name, "url": ws.url, "commit": ws.base, "language": ws.language,
                                                "n_files": ws.n_files, "tests_runnable": ws.runnable, "reason": ws.reason,
                                                "prepared": True})
            path = ws.repo_dir / ns.file
            if ".." in Path(ns.file).parts or not path.is_file():
                raise SystemExit("not a file of the repository")
            text = path.read_text(encoding="utf-8")
            every = [m for m in mutate.find_mutations(text) if m.function == ns.function]
            seen: dict[str, int] = {}
            ranked = []                             # one of each operator first (in line order), then the rest
            for m in sorted(every, key=lambda m: (m.line, m.start)):
                seen[m.operator] = seen.get(m.operator, 0) + 1
                ranked.append((seen[m.operator], m.line, m.start, m))
            muts = [x[3] for x in sorted(ranked, key=lambda x: x[:3])][:PROBE_MAX]
            if not muts:
                em.emit("arena", "arena.probe", "skipped", {"reason": f"no mutation operator applies to {ns.function}"})
                em.emit("meta", "run.end", "ok", {})
                return 0
            rows, t0 = [], time.perf_counter()
            for i, m in enumerate(muts, 1):
                left = PROBE_CAP_S - (time.perf_counter() - t0)
                if left <= 1:
                    break
                em.emit("arena", "arena.probe", "running", {"i": i, "n": len(muts), "operator": m.operator, "line": m.line,
                                                            "old": m.old, "new": m.new})
                path.write_text(mutate.apply(text, m), encoding="utf-8")
                t1 = time.perf_counter()
                try:
                    run = run_pytest(ws.repo_dir, None, scratch / f"probe-{i}.xml", "probe", ws.python, timeout=left)
                finally:
                    path.write_text(text, encoding="utf-8")
                failed = sorted({r.test_id for r in run.failed})
                rows.append({"i": i, "operator": m.operator, "line": m.line, "old": m.old, "new": m.new,
                             "caught": bool(failed), "failed": len(failed), "first_failed": failed[0] if failed else None,
                             "cases": len(run.results), "wall_s": round(time.perf_counter() - t1, 2), "timed_out": run.timed_out})
            stopped = len(rows) < len(muts)
            em.emit("arena", "arena.probe", "ok", {
                "function": ns.function, "file": ns.file, "rows": rows, "caught": sum(r["caught"] for r in rows),
                "survived": sum(not r["caught"] for r in rows), "n": len(muts), "cap_s": PROBE_CAP_S,
                "wall_s": round(time.perf_counter() - t0, 2),
                "note": (f"stopped at the {PROBE_CAP_S} s cap after {len(rows)} of {len(muts)} mutants" if stopped else
                         f"{len(rows)} mutant(s), each run against the full suite, one at a time; no model")})
            em.emit("meta", "run.end", "ok", {})
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    return 0


def cmd_quota(ns: argparse.Namespace) -> int:
    """Exit 0 when `--need` more tokens of `--model` fit under the 24 h cap (E3 and lab ledgers together), else 3."""
    q = quota().get(ns.model)
    if q is None:
        raise SystemExit(f"unknown model {ns.model}")
    room = q["cap"] - q["used"]
    ok = room >= ns.need
    log(f"{ns.model}: {q['used']:,} of {q['cap']:,} tokens used in the last 24 h ({', '.join(q['ledgers'])}); "
        f"room {room:,}, needed {ns.need:,}: " + ("OK" if ok else "NOT ENOUGH" + (f", the oldest counted call leaves the window at {q['resume_after']} UTC" if q["resume_after"] else "")))
    return 0 if ok else 3


def cmd_status(_ns: argparse.Namespace) -> int:
    print(json.dumps({"llm": bool(os.environ.get("GROQ_API_KEY")), "quota": quota()}))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.lab")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mode", nargs="+")
    r.add_argument("--repo")
    r.add_argument("--url")
    r.add_argument("--pr", help="a public pull request URL: its merge base -> head is the change")
    r.add_argument("--task")
    r.add_argument("--variant", choices=["standard", "hard"], default="standard")
    r.add_argument("--inject")
    r.add_argument("--edit")
    r.add_argument("--model", default="openai/gpt-oss-120b")
    r.add_argument("--no-llm", action="store_true")
    r.add_argument("--no-install", action="store_true")
    r.add_argument("--record")
    r.add_argument("--title")
    r.add_argument("--description")
    r.add_argument("--base-patch")
    r.add_argument("--speed", type=float, default=1.0)
    r.add_argument("--timeout", type=int, default=300)
    r.add_argument("--repair-arena", action="store_true", help="one extra model call: R1 (log-only) against R2, and the unvalidated push")
    r.set_defaults(fn=cmd_run)
    s = sub.add_parser("repos")
    s.set_defaults(fn=cmd_repos)
    s = sub.add_parser("mutations")
    s.add_argument("--repo", required=True)
    s.add_argument("--file", required=True)
    s.set_defaults(fn=cmd_mutations)
    s = sub.add_parser("tasks")
    s.add_argument("--repo")
    s.set_defaults(fn=cmd_tasks)
    s = sub.add_parser("index")
    s.set_defaults(fn=cmd_index)
    s = sub.add_parser("rederive", help="apply the test-case rule to recordings made before it")
    s.add_argument("names", nargs="+")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_rederive)
    s = sub.add_parser("graph")
    s.add_argument("--repo", required=True)
    s.set_defaults(fn=cmd_graph)
    s = sub.add_parser("probe")
    s.add_argument("--repo", required=True)
    s.add_argument("--file", required=True)
    s.add_argument("--function", required=True)
    s.set_defaults(fn=cmd_probe)
    s = sub.add_parser("quota")
    s.add_argument("--model", default="openai/gpt-oss-120b")
    s.add_argument("--need", type=int, default=CALL_ESTIMATE)
    s.set_defaults(fn=cmd_quota)
    s = sub.add_parser("status")
    s.set_defaults(fn=cmd_status)
    ns = ap.parse_args(argv)
    return ns.fn(ns)


if __name__ == "__main__":
    sys.exit(main())
