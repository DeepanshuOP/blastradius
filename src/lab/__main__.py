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

    a = LabArgs(repo=ns.repo, url=ns.url, task=ns.task, variant=ns.variant, model=ns.model, use_llm=not ns.no_llm,
                record=ns.record, timeout=ns.timeout, install=not ns.no_install, title=ns.title,
                description=ns.description, command=sys.argv[1:])
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
    if bool(ns.repo) == bool(ns.url):
        raise SystemExit("give exactly one of --repo / --url")
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
        from src.agents.llm import GroqLLM
        from src.lab.cache import for_model

        cache = for_model(args.model)
        llm = GroqLLM(api_key=os.environ["GROQ_API_KEY"], model=args.model, cache=cache, max_retries=0)
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
            lab.cleanup()
    return rc


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


def cmd_status(_ns: argparse.Namespace) -> int:
    print(json.dumps({"llm": bool(os.environ.get("GROQ_API_KEY"))}))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.lab")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mode", nargs="+")
    r.add_argument("--repo")
    r.add_argument("--url")
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
    s = sub.add_parser("graph")
    s.add_argument("--repo", required=True)
    s.set_defaults(fn=cmd_graph)
    s = sub.add_parser("status")
    s.set_defaults(fn=cmd_status)
    ns = ap.parse_args(argv)
    return ns.fn(ns)


if __name__ == "__main__":
    sys.exit(main())
