"""The lab pipeline: repository -> graph -> change -> impact -> tests -> triage -> repair -> validate -> report.

The stages after `change` are `src.agents.bot.run_bot` (impact ranking, one risk-first suite run, triage against the
base commit, R3 repair, validation on the full suite), reached through its `on_event` callback. This module adds what
the bot does not know about: the graph, the graph paths and reachability, the race against alphabetical order, and the
run summary. Nothing here is a second implementation of an agent.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from src.lab import changes, graphview, order as case_order
from src.lab.events import Emitter
from src.lab.workspace import LAB_ROOT, Workspace, new_scratch, prepare_github, prepare_seeded

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "openai/gpt-oss-120b"
MODELS = ("openai/gpt-oss-120b", "openai/gpt-oss-20b")
TEST_TIMEOUT_S = 300
FAILED = ("failed", "error")


@dataclass
class LabArgs:
    """What to run."""

    repo: str | None = None                 # a prepared repository slug
    url: str | None = None                  # or a public GitHub URL
    pr: str | None = None                   # or a public pull request URL: its base -> head is the change
    task: str | None = None
    variant: str = "standard"
    inject: tuple[str, str, str, int | None] | None = None   # (file, function, operator, line)
    edit: tuple[str, str] | None = None     # (file, new text)
    model: str = DEFAULT_MODEL
    use_llm: bool = True
    record: str | None = None
    timeout: int = TEST_TIMEOUT_S
    install: bool = True
    base_patch: str | None = None           # a diff committed as the base commit first (scenario construction)
    repair_arena: bool = False              # one extra model call: R1 (log-only) against the run's R2, and the unvalidated push
    exclude_same_diff: bool = True          # the arena's failure-history row ignores earlier runs of this same diff
    title: str | None = None
    description: str | None = None
    command: list[str] = field(default_factory=list)


def git_sha() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=10", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def race(results: list[dict], order_files: list[str], t_start: float | None, rule: dict | None = None,
         native: list[str] | None = None, derived: bool = False) -> dict:
    """Risk-first (as run) against alphabetical (what a retest-all job does), from this run's measured durations.

    The alphabetical lane is *computed*: the same measured per-test durations summed in alphabetical id order. It was
    not run separately, and the data says so. `rule` is the test-case rule payload the run used (`order.rule_payload`);
    with `native` (pytest's own collection order as node ids) the order *before* the rule is derived from the same
    measured durations and reported as `order_rule.before`. `derived=True` is for a recording made before the rule:
    the top lane is then the rule's order computed over the stored results, not an order pytest ran.
    """
    ticks = [{"i": i, "id": r["id"], "outcome": r["outcome"], "ms": round(float(r["duration_s"]) * 1000, 2)}
             for i, r in enumerate(results, 1)]

    def lane(name: str, label: str, seq: list[dict], basis: str) -> dict:
        ff = next((k for k, t in enumerate(seq) if t["outcome"] in FAILED), None)
        elapsed = round(sum(t["ms"] for t in seq[: ff + 1]), 1) if ff is not None else None
        return {"name": name, "label": label, "ticks": seq, "total_ms": round(sum(t["ms"] for t in seq), 1),
                "first_failure_position": ff + 1 if ff is not None else None,
                "first_failure_id": seq[ff]["id"] if ff is not None else None,
                "elapsed_to_first_failure_ms": elapsed, "basis": basis}

    if derived and rule:
        by_pos = case_order.derive(results, rule)
        risk = lane("risk-first", "BlastRadius risk-first", [ticks[i] for i in by_pos],
                    "computed: this run's measured per-test durations summed in the BlastRadius order; this recording "
                    "was executed before the rule existed, so that order was not run")
    else:
        risk = lane("risk-first", "BlastRadius risk-first", ticks,
                    "the order pytest actually ran; durations measured per test in this run")
    alpha = lane("alphabetical", "Retest-all (alphabetical id order)",
                 sorted(ticks, key=lambda t: (t["id"], t["i"])),
                 "computed: this run's measured per-test durations summed in alphabetical id order; "
                 "that order was not run separately")
    ff = next((r for r in results if r["outcome"] in FAILED), None)
    if ff is not None and t_start and ff.get("t") and not derived:
        risk["measured_wall_to_first_failure_ms"] = round((float(ff["t"]) - t_start) * 1000, 1)
    out = {"lanes": [risk, alpha], "unit": "test cases (one JUnit testcase each); ids can repeat when a subclass "
                                           "inherits a test"}
    if rule:
        by_pos = case_order.derive(results, rule)
        respected = by_pos == list(range(len(results)))
        out["order_respected"] = None if derived else respected
        out["order_note"] = (
            "re-derived: this recording was executed in the earlier order (E1 file rank, then collection order); the top "
            "lane is the rule's order over the same measured durations" if derived else
            "pytest ran the cases in the rule's order: E1 file tier, then graph hops, then id" if respected else
            "pytest did NOT keep the requested order; the lanes show what actually ran")
        out["order_rule"] = {"id": case_order.RULE_ID, "fixed": case_order.RULE_FIXED, "text": case_order.RULE_TEXT,
                             "source": "derived" if derived else "as run", "before": None}
        if native:
            from src.lab import arena

            b = arena.score(results, case_order.old_order(results, native, order_files))
            out["order_rule"]["before"] = {
                "first_failure_position": b["first_failure_position"], "first_failure_ms": b["first_failure_ms"],
                "basis": "derived from this run's measured durations in the order before the rule (E1 file rank, then "
                         "pytest's collection order); that order was not run separately"}
        return out
    rank = {f: i for i, f in enumerate(order_files)}
    # the collected node id (not the canonical id, which carries the file that *defines* an inherited test)
    seq_rank = [rank.get((r.get("nodeid") or r["id"]).split("::")[0], len(rank)) for r in results]
    respected = all(a <= b for a, b in zip(seq_rank, seq_rank[1:]))
    out["order_respected"] = respected
    out["order_note"] = ("pytest ran every at-risk file before the others, in ranking order" if respected else
                         "pytest did NOT keep the requested order; the lanes show what actually ran")
    return out


class Lab:
    """One run."""

    def __init__(self, args: LabArgs, em: Emitter, llm=None) -> None:
        self.a, self.em, self.llm = args, em, llm
        self.scratch = new_scratch("run")
        self.run_id = args.record or uuid.uuid4().hex[:12]
        self.results: list[dict] = []
        self.order_files: list[str] = []
        self.t_tests: float | None = None
        self.view: dict = {"nodes": [], "edges": []}
        self.change: changes.Change | None = None
        self.changed_nodes: list[str] = []
        self.tokens = {"prompt": 0, "completion": 0, "total": 0, "cached": 0, "calls": 0}
        self.validate_seen = False
        self.extra_header: dict = {}
        self.rule: dict | None = None          # the test-case rule the suite runs under (order.rule_payload)
        self.native_path = self.scratch / "native-order.json"

    # -- stages ------------------------------------------------------------------------------
    def repo_stage(self) -> Workspace:
        e = self.em
        e.emit("repo", "repo.info", "running", {"name": self.a.repo or self.a.url or self.a.pr})
        t0 = time.perf_counter()
        if self.a.pr:
            from src.lab.workspace import prepare_pr

            ws, self.pr_info = prepare_pr(self.a.pr, self.scratch, install=self.a.install)
        else:
            ws = (prepare_seeded(self.a.repo, self.scratch) if self.a.repo
                  else prepare_github(self.a.url, self.scratch, install=self.a.install))
        e.emit("repo", "repo.info", "ok", {
            "name": ws.name, "url": ws.url, "commit": ws.base, "language": ws.language, "n_files": ws.n_files,
            "prepared": ws.prepared, "tests_runnable": ws.runnable, "reason": ws.reason, "timings": ws.timings,
            "interpreter": "the prepared virtualenv of data/seeded (read-only)" if ws.prepared else
                           ("a fresh scratch virtualenv" if ws.runnable else None),
            **({"pr": self.pr_info} if self.a.pr else {})},
               dur_ms=(time.perf_counter() - t0) * 1000)
        return ws

    def _commit_base(self, ws: Workspace) -> str:
        """Scenario construction: commit `base_patch` first, so the base itself carries that content (stated in the
        header event and in the repo event). Used for the recorded 'inherited failure' run."""
        import subprocess as sp

        p = sp.run(["git", "-C", str(ws.repo_dir), "apply", "--whitespace=nowarn", "-"], input=self.a.base_patch,
                   capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            raise RuntimeError(f"base patch does not apply: {(p.stderr or p.stdout)[:300]}")
        from src.lab.workspace import git

        git(ws.repo_dir, "add", "-u")
        git(ws.repo_dir, "commit", "-q", "-m", "scenario: base commit carries a pre-existing defect")
        sha = git(ws.repo_dir, "rev-parse", "HEAD")
        self.extra_header["base_patch"] = self.a.base_patch
        self.extra_header["scenario_note"] = ("scratch repository: its base commit was edited before the change so that "
                                              "it already carries the defect shown in base_patch")
        self.em.emit("repo", "repo.info", "ok", {
            "name": ws.name, "url": ws.url, "commit": sha, "language": ws.language, "n_files": ws.n_files,
            "prepared": ws.prepared, "tests_runnable": ws.runnable, "reason": ws.reason, "timings": ws.timings,
            "scenario_note": self.extra_header["scenario_note"], "base_patch": self.a.base_patch})
        return sha

    def change_commit(self, ws: Workspace) -> changes.Change:
        a = self.a
        if a.pr:
            return changes.from_pr(ws, self.pr_info)
        if a.task:
            return changes.apply_task(ws, a.task, a.variant)
        if a.inject:
            return changes.inject_bug(ws, *a.inject)
        if a.edit:
            return changes.custom_edit(ws, *a.edit)
        raise ValueError("choose a change: --task, --inject or --edit")

    def graph_stage(self, ws: Workspace, ch: changes.Change) -> None:
        e = self.em
        e.emit("graph", "graph.built", "running", {})
        t0 = time.perf_counter()
        try:
            from src.graph.build import build_graph_at, load_graph

            st = build_graph_at(f"lab/{ws.name}", ws.base, clone_dir=ws.repo_dir, out_dir=self.scratch / "graphs")
            view = graphview.to_cytoscape(load_graph(st.graph_path))
        except Exception as exc:  # noqa: BLE001 - the stage reports its own failure; the run goes on
            e.emit("graph", "graph.built", "failed", {"nodes": [], "edges": [], "counts": {}, "parse_failures": None,
                                                      "truncated": False, "reason": f"{type(exc).__name__}: {exc}"[:300]})
            return
        self.view = view
        self.changed_nodes, self.changed_detail = graphview.map_changed_nodes(view, ch.diff, ch.base_sources)
        sub, truncated = graphview.stream_subset(view, self.changed_nodes, ch.changed_files)
        full_path = LAB_ROOT / "graphs" / f"{self.run_id}.json"
        graphview.store({**view, "repo": ws.name, "commit": ws.base}, full_path)
        self.graph_file = full_path
        e.emit("graph", "graph.built", "ok", {
            "graph_id": self.run_id, "repo": ws.name, "commit": ws.base, "nodes": sub["nodes"], "edges": sub["edges"],
            "counts": graphview.count_by_type(view), "n_nodes": len(view["nodes"]), "n_edges": len(view["edges"]),
            "parse_failures": st.n_parse_failures, "files_considered": st.n_files_considered,
            "failed_source_files": st.failed_source_files[:20], "truncated": truncated,
            "streamed_nodes": len(sub["nodes"]), "streamed_edges": len(sub["edges"]),
            "external_nodes_omitted": view["external_nodes_omitted"], "orphan_rate": st.orphan_rate,
            "builder": f"src.graph.build (graphify {st.graphify_commit[:10]})"},
               dur_ms=(time.perf_counter() - t0) * 1000)

    def change_stage(self, ch: changes.Change) -> None:
        u = graphview.undirected(self.view) if self.view["nodes"] else None
        hops = graphview.hops_from(u, self.changed_nodes) if u is not None and self.changed_nodes else {}
        self.hops = hops
        self.em.emit("change", "change.applied", "ok", {
            "source": ch.source, "diff": ch.diff, "changed_files": ch.changed_files, "changed_nodes": self.changed_nodes,
            "changed_functions": getattr(self, "changed_detail", []), "base": ch.base, "head": ch.head,
            "wave": {"hops": hops, "limit": graphview.HOP_LIMIT}, "note": ch.note,
            "before": {f: t[:60000] for f, t in ch.base_sources.items()}})

    # -- bot events --------------------------------------------------------------------------
    def on_bot_event(self, stage: str, type_: str, status: str, data: dict) -> None:
        e = self.em
        if type_ == "impact.ranking":
            e.emit("impact", type_, status, data)
            self.order_files = data["at_risk_files"]
            self.rule = {**case_order.rule_payload(data["rows"], self.order_files, self.view, self.changed_nodes),
                         "native_out": str(self.native_path)}
            paths = graphview.paths_to_tests(self.view, self.changed_nodes, data["at_risk_files"])
            reach = {k: v for k, v in self.hops.items()}
            e.emit("impact", "impact.paths", "ok", {
                "paths": paths, "changed_nodes": self.changed_nodes,
                "reachability": {"limit": graphview.HOP_LIMIT, "hops": reach, "n_reachable": len(reach),
                                 "n_nodes": len(self.view["nodes"]),
                                 "definition": "nodes within 4 undirected hops of a changed node in the base-commit graph"}})
        elif type_ == "tests.start":
            self.t_tests = time.time()
            if self.rule:
                data = {**data, "order_enforced_by": "pytest plugin: collected items sorted by E1 file tier, then graph "
                        "hop distance to the changed functions, then id", "order_rule": {
                            "id": case_order.RULE_ID, "fixed": case_order.RULE_FIXED, "text": case_order.RULE_TEXT,
                            "n_tiers": len(set(self.rule["tiers"].values())), "n_hops_known": len(self.rule["hops"])}}
            e.emit(stage, type_, status, data)
        elif type_ == "test.result":
            self.results.append(data)
            e.emit(stage, type_, "failed" if data["outcome"] in FAILED else "ok", data, dur_ms=data["duration_s"] * 1000)
        elif type_ == "tests.done":
            data = {**data, "n_results": len(self.results)}
            native = None
            if self.rule and self.native_path.exists():
                native = json.loads(self.native_path.read_text(encoding="utf-8"))
            rc = race(self.results, self.order_files, self.t_tests, self.rule, native)
            self.native = native
            e.emit(stage, type_, status, {**data, "order_respected": rc["order_respected"],
                                          "order_note": rc["order_note"]})
            e.emit("tests", "tests.race", "ok", rc)
            if self.results and not data.get("timed_out"):
                self.arena_stage()
        elif type_ == "report.comment":
            if not self.validate_seen:                   # no patch was proposed: validation is a stage that did not run
                self.validate_seen = True
                e.emit("validate", "validate.verdict", "skipped", {"accepted": False, "reason": "no patch was proposed"})
            e.emit(stage, type_, status, data)
        elif type_ == "repair.reply":
            u = data.get("usage") or {}
            self.tokens["calls"] += 1
            self.tokens["prompt"] += int(u.get("prompt_tokens", 0))
            self.tokens["completion"] += int(u.get("completion_tokens", 0))
            self.tokens["total"] += int(u.get("total_tokens", 0))
            self.tokens["cached"] += int(u.get("total_tokens", 0)) if data.get("from_cache") else 0
            e.emit(stage, type_, status, {**data, "tokens_so_far": dict(self.tokens)})
        else:
            if stage == "validate":
                self.validate_seen = True
            e.emit(stage, type_, status, data)

    # -- arena -------------------------------------------------------------------------------
    def repo_key(self) -> str:
        """History and coverage are kept per repository: the prepared slug, or owner__repo for a URL."""
        ws = self.ws
        if ws.prepared:
            return ws.name
        m = re.match(r"^https://github\.com/([\w.-]+)/([\w.-]+?)(\.git)?$", ws.url or "")
        return f"{m.group(1)}__{m.group(2)}" if m else ws.name

    def arena_stage(self) -> None:
        """Six strategies scored on this run's measured results (no strategy is run separately)."""
        from src.lab import arena

        e, ws, ch = self.em, self.ws, self.change
        key = self.repo_key()
        e.emit("arena", "arena.coverage", "running", {"what": "per-test function coverage at the base commit"})
        cov: dict | None
        if ws.python:
            try:
                cov = arena.run_coverage(ws.repo_dir, ch.base, ws.python, key)
            except Exception as exc:  # noqa: BLE001 - the strategy is reported unavailable, the run goes on
                cov = {"status": "skipped", "reason": f"{type(exc).__name__}: {exc}"[:300]}
        else:
            cov = {"status": "skipped", "reason": "no interpreter for this repository"}
        e.emit("arena", "arena.coverage", "ok" if cov["status"] == "ok" else "skipped",
               {k: v for k, v in cov.items() if k != "tests"})
        hist = arena.read_history(key)
        e.emit("arena", "arena.upstream", "running", {"what": "git history for co-change"})
        from src.lab.workspace import fetch_upstream_history

        up = fetch_upstream_history(ws)
        e.emit("arena", "arena.upstream", "ok" if up["status"] in ("fetched", "cached", "not-needed") else "skipped", up)
        try:
            cc = arena.cochange_counts(ws.repo_dir, ch.base, ch.changed_files)
        except Exception as exc:  # noqa: BLE001
            cc = (arena.Counter(), 0, f"git log failed: {exc}"[:200])
        if cc[2] and up["status"] == "unavailable":      # say why the history is missing, not just that it is
            cc = (cc[0], cc[1], up["reason"])
        dkey = arena.diff_key(ch.diff)
        doc = arena.compute(self.results, order_files=self.order_files, view=self.view, changed_nodes=self.changed_nodes,
                            changed_fns=getattr(self, "changed_detail", []), coverage=cov, history=hist, cochange=cc,
                            rule=self.rule, cochange_info={"source": up["status"] if up["status"] in ("fetched", "cached") else None,
                                                           "fetch_s": up.get("fetch_s", 0.0)},
                            same_diff=lambda r: arena.is_same_diff(r, ch.source, dkey),
                            exclude_same_diff=self.a.exclude_same_diff)
        doc["coverage"] = {k: v for k, v in cov.items() if k != "tests"}
        doc["history"] = {**doc["history"], "store": str(arena.history_path(key))}
        doc["cochange"] = {"n_commits": cc[1], "upstream": up, **({"reason": cc[2]} if cc[2] else {})}
        e.emit("arena", "arena.result", "ok", doc)
        if ch.source.get("kind") == "inject" and doc["n_failing"] == 0:
            e.emit("arena", "arena.gap", "ok", self.test_gap(doc, cov))
        from src.lab.events import now_iso

        arena.append_history(key, {"run_id": self.run_id, "date": now_iso(), "change": ch.source, "diff_key": dkey,
                                   "failed": sorted({r["id"] for r in self.results if r["outcome"] in FAILED}),
                                   "n_cases": len(self.results)})

    def test_gap(self, doc: dict, cov: dict) -> dict:
        """A known semantic change (an injected mutation) that the whole suite let through, and the tests that reach it."""
        from src.lab import arena

        src = self.change.source
        before = self.change.base_sources.get(src["file"], "").splitlines()
        line = before[src["line"] - 1] if 0 < src["line"] <= len(before) else ""
        after = line.replace(src["old"], src["new"], 1)
        fns = [{"file": src["file"], "function": src["function"]}]
        covering: list[str] = []
        if cov.get("status") == "ok":
            covering = [self.results[i]["id"] for i in arena.coverage_selection(self.results, cov, fns)[0]]
        files = sorted(arena.reaching_test_files(self.view, self.changed_nodes)) if self.view.get("nodes") and self.changed_nodes else []
        n, k = doc["n_cases"], len(dict.fromkeys(covering))
        if cov.get("status") != "ok":
            reach = f"coverage was not recorded ({cov.get('reason')}), and {len(files)} test file(s) reach it in the graph"
        elif k:
            reach = f"{k} test(s) execute {src['function']} at the base commit and {len(files)} test file(s) reach it in the graph"
        else:
            reach = f"no test executes {src['function']} at all, though {len(files)} test file(s) reach it in the graph"
        sentence = (f"All {n} tests passed with `{src['old']}` changed to `{src['new']}` on line {src['line']} of {src['file']}. "
                    f"{reach[0].upper() + reach[1:]}, yet none of them tells the two versions of this line apart, so "
                    f"this change would ship unnoticed.")
        return {"file": src["file"], "function": src["function"], "operator": src["operator"], "line": src["line"],
                "old": src["old"], "new": src["new"], "before": line, "after": after, "n_cases": n,
                "covering": list(dict.fromkeys(covering)), "coverage_status": cov.get("status"), "graph_files": files,
                "sentence": sentence}

    def repair_arena_stage(self) -> None:
        """R1 (log-only) against the run's R2 on the same failures, and what an unvalidated push would ship."""
        from src.lab import repair_arena

        e = self.em
        tri = next((ev for ev in reversed(e.history) if ev["type"] == "triage.result"), None)
        mine = [r for r in (tri["data"]["rows"] if tri else []) if r["class"] == "mine"]
        if not self.llm:
            e.emit("arena", "arena.repair", "skipped", {"reason": "no model is available, so the extra R1 call cannot be made"})
            return
        if not mine:
            e.emit("arena", "arena.repair", "skipped", {"reason": "no failure was triaged mine, so there is nothing to repair"})
            return
        e.emit("arena", "arena.repair", "running", {"failure": [m["test"] for m in mine[:8]]})
        try:
            r1, push = repair_arena.run_r1(self.ws.repo_dir, self.change.base, self.change.head, mine, self.llm, self.ws.python,
                                           self.scratch / "state", self.a.timeout,
                                           {r["test"] for r in tri["data"]["rows"] if r["class"] != "mine"})
        except Exception as exc:  # noqa: BLE001 - quota, network, cache miss: say so and keep the run
            e.emit("arena", "arena.repair", "skipped", {"reason": f"the R1 call could not be made: {type(exc).__name__}: {exc}"[:400]})
            return
        if r1.get("tokens"):
            self.tokens["calls"] += 1
            self.tokens["total"] += int(r1["tokens"])
            self.tokens["cached"] += int(r1["tokens"]) if r1.get("from_cache") else 0
        r2 = repair_arena.r2_column(e.history)
        e.emit("arena", "arena.repair", "ok", {
            "failure": [m["test"] for m in mine[:8]], "columns": [r1, r2, push], "tokens": (r1.get("tokens") or 0) + (r2.get("tokens") or 0),
            "note": ("The same failing tests, the same model and the same five checks. R1 sees only the failure log; R2 also "
                     "sees the change. The third column is what an agent that pushes without running the full suite would "
                     "have shipped: the R1 patch, with the full-suite result measured afterwards in this run.")})

    # -- run ---------------------------------------------------------------------------------
    def header(self) -> None:
        """First event of every run: what is about to execute, and with which model."""
        from src.lab.events import now_iso

        a = self.a
        cache = f"eval/llm_cache/lab_{a.model.replace('/', '_')}.jsonl" if self.llm else None
        self.em.emit("meta", "run.header", "ok", {
            "date": now_iso(), "git_sha": git_sha(), "model": a.model if self.llm else None, "mode": "live",
            "llm": "enabled" if self.llm else ("disabled by --no-llm" if not a.use_llm else "no GROQ_API_KEY"),
            "temperature": 0, "seed": 0, "cache": cache,
            "ledger": "eval/llm_cache/lab_usage.jsonl" if self.llm else None, "command": ["python", "-m", "src.lab", *a.command],
            "run_id": self.run_id, "timeout_s": a.timeout, "title": a.title, "description": a.description,
            **self.extra_header})

    def run(self) -> int:
        from src.agents import bot

        e = self.em
        self.header()
        ws = self.repo_stage()
        self.ws = ws
        if self.a.base_patch:
            ws.base = self._commit_base(ws)
        ch = self.change_commit(ws)
        self.change = ch
        self.graph_stage(ws, ch)
        self.change_stage(ch)
        py = ws.python
        if ws.runnable:
            out = bot.run_bot(ws.repo_dir, ch.base, ch.head, 1, llm=self.llm if self.a.use_llm else None,
                              state_dir=self.scratch / "state", python=py, on_event=self.on_bot_event,
                              timeout=self.a.timeout, case_order=lambda: self.rule, audit=self.open_audit())
            stats = out.stats
            validated = out.validated
            if self.a.repair_arena:
                self.repair_arena_stage()
        else:
            self._impact_only(ws, ch, bot)
            stats, validated = {}, False
        self.summary(ws, stats, validated)
        self.close_audit()
        return 0

    # -- decision log (D-71) ---------------------------------------------------------------------
    def open_audit(self):
        """A fresh hash-chained decision log for this run; each record is also streamed as an `audit.record` event."""
        from datetime import datetime, timezone

        from src.agents.audit import DecisionLog

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.audit = DecisionLog(f"lab-{self.run_id}-{stamp}",
                                 on_record=lambda r: self.em.emit("audit", "audit.record", "ok", r))
        return self.audit

    def close_audit(self) -> None:
        """Verify the chain and emit the result (`audit.verify`)."""
        from src.agents.audit import summary, verify

        log = getattr(self, "audit", None)
        if log is None or not log.records:
            return
        ok, problems, n = verify(log.run_id, log.root)
        self.em.emit("audit", "audit.verify", "ok" if ok else "failed", {
            "run_id": log.run_id, "ok": ok, "records": n, "problems": problems[:10], "summary": summary(log.records),
            "file": f"logs/agent/{log.run_id}.jsonl"})

    def _impact_only(self, ws: Workspace, ch: changes.Change, bot) -> None:
        e = self.em
        reason = ws.reason or "tests are not runnable in this environment"
        try:
            impact, rows, name = bot.build_impact(ws.repo_dir, ch.base, ch.head, 1)
            self.on_bot_event("impact", "impact.ranking", "ok", {
                "ranker": name, "changed_files": ch.changed_files, "changed_lines": 0, "n_test_files": len(rows),
                "at_risk_files": [t.file for t in impact.tests],
                "rows": [{"test": r["test"], "score": round(float(r["score"]), 4),
                          "reasons": [x for x in str(r["why"]).split("; ") if x][:3], "why": r["why"]} for r in rows]})
            comment = bot.render_comment(pr=1, base=ch.base, head=ch.head, risk=rows, ranker=name, results=[], n_total=0,
                                         first_failure=None, triage=[], repair=None, model="none", tokens=0,
                                         notes=[f"Tests were not run: {reason}"])
        except Exception as exc:  # noqa: BLE001
            e.emit("impact", "impact.ranking", "failed", {"ranker": "none", "rows": [], "changed_files": ch.changed_files,
                                                          "reason": f"{type(exc).__name__}: {exc}"[:300]})
            comment = f"Impact analysis failed: {exc}\n"
        e.emit("tests", "tests.done", "skipped", {"counts": {}, "reason": reason})
        e.emit("triage", "triage.result", "skipped", {"rows": [], "counts": {}, "reason": reason})
        e.emit("repair", "repair.skipped", "skipped", {"reason": reason})
        self.on_bot_event("report", "report.comment", "ok", {"comment": comment, "validated": False})

    def summary(self, ws: Workspace, stats: dict, validated: bool) -> None:
        e = self.em
        stages: dict[str, dict] = {}
        for ev in e.history:
            if ev["stage"] == "meta":
                continue
            s = stages.setdefault(ev["stage"], {"statuses": [], "dur_ms": 0.0, "events": 0})
            s["events"] += 1
            if ev["type"] == "test.result":           # a failing test is a result, not a failed stage
                continue
            s["statuses"].append(ev["status"])
            s["dur_ms"] = max(s["dur_ms"], ev["dur_ms"])
        for s in stages.values():
            st = s.pop("statuses")
            s["status"] = ("failed" if "failed" in st else "ok" if "ok" in st else
                           "skipped" if st and set(st) == {"skipped"} else "running")
        race_ev = next((ev for ev in e.history if ev["type"] == "tests.race"), None)
        e.emit("report", "report.summary", "ok", {
            "mode": "live", "repo": ws.name, "commit": ws.base, "model": self.a.model if self.llm else None,
            "stages": stages, "tokens": self.tokens, "validated": validated,
            "failing_ids": stats.get("failing"), "failing_cases": stats.get("failing_cases"),
            "mine": stats.get("mine"), "cases": stats.get("cases"), "unit": stats.get("unit"),
            "race": ({l["name"]: {k: l[k] for k in ("first_failure_position", "elapsed_to_first_failure_ms", "total_ms")}
                      for l in race_ev["data"]["lanes"]} if race_ev else None),
            "total_ms": round((time.perf_counter() - self.em.started.get("repo", time.perf_counter())) * 1000, 1)})

    def cleanup(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)
