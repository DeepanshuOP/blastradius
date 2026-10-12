"""Regression Suite Agent: impact analysis + regression suite -> test report.

Runs the tests the impact analysis put at risk (the selected scope) and,
optionally, the full suite as well. With both, the report shows the measurement
BR-Bench is about: of the tests that actually failed, how many did the impact
analysis predict (impact recall), and how much of the suite it skipped.

Python suites run under pytest with JUnit XML output. Any other suite runs from
a command template (``--runner-cmd 'mvn -q test -Dtest={tests}'``) and its JUnit
XML reports (``--junit-glob``). Every outcome is appended to
``history/test_outcomes.jsonl``, which the Impact Analysis Agent reads as failure
history next time.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from src.agents import gitops
from src.agents.impact import ImpactAnalysis


@dataclass
class TestResult:
    """One test's outcome."""

    test_id: str
    outcome: str  # passed | failed | error | skipped
    duration_s: float
    message: str = ""


@dataclass
class SuiteRun:
    """One pytest/runner invocation. ``order`` is the execution order of the test ids."""

    label: str
    command: list[str]
    exit_code: int
    wall_s: float
    results: list[TestResult] = field(default_factory=list)
    order: list[str] = field(default_factory=list)
    timed_out: bool = False

    @property
    def failed(self) -> list[TestResult]:
        """Failed or errored tests."""
        return [r for r in self.results if r.outcome in ("failed", "error")]

    def counts(self) -> dict[str, int]:
        """Outcome counts."""
        out = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
        for r in self.results:
            out[r.outcome] = out.get(r.outcome, 0) + 1
        out["total"] = len(self.results)
        return out


def junit_test_id(file: str | None, cls: str, name: str) -> str:
    """The id `parse_junit` gives a test case (also used for results streamed by the Live Lab plugin)."""
    if file and file.endswith(".py"):
        module = file[:-3].replace("/", ".")
        owner = cls[len(module) + 1:] if cls.startswith(module + ".") else ""
        return f"{file}::{owner}::{name}" if owner else f"{file}::{name}"
    return f"{cls.split('.')[-1]}#{name}" if cls else name


def parse_junit(paths: list[Path], sort: bool = True) -> list[TestResult]:
    """Parse JUnit XML files into results; ids are pytest node ids for Python files.

    ``sort=False`` keeps the XML order, which for pytest is the execution order.
    """
    results: list[TestResult] = []
    for path in paths:
        root = ET.parse(path).getroot()
        for case in root.iter("testcase"):
            name = case.get("name", "")
            cls = case.get("classname", "")
            file = case.get("file")
            tid = junit_test_id(file, cls, name)
            outcome, message = "passed", ""
            for tag in ("failure", "error", "skipped"):
                el = case.find(tag)
                if el is not None:
                    outcome = {"failure": "failed", "error": "error", "skipped": "skipped"}[tag]
                    message = (el.get("message") or (el.text or "")).strip().splitlines()[0][:300] if (el.get("message") or el.text) else ""
                    break
            results.append(TestResult(tid, outcome, round(float(case.get("time", 0) or 0), 4), message))
    return sorted(results, key=lambda r: r.test_id) if sort else results


def execution_order(paths: list[Path]) -> list[str]:
    """Test ids in the order they appear in the JUnit XML (xunit1: execution order)."""
    return [r.test_id for r in parse_junit(paths, sort=False)]


PLUGIN_DIR = Path(__file__).resolve().parents[1] / "lab" / "plugin"


def run_pytest(workdir: Path, test_ids: list[str] | None, out_xml: Path, label: str, python: str | None = None, *,
               on_result=None, order_files: list[str] | None = None, timeout: float | None = None,
               rule: dict | None = None) -> SuiteRun:
    """Run pytest in ``workdir`` (all tests when ``test_ids`` is None).

    Args:
        workdir: Working tree.
        test_ids: Node ids or files to run; None runs everything.
        out_xml: JUnit XML path.
        label: Name of the run.
        python: Interpreter (default: this one).
        on_result: Optional callable receiving one dict per finished test while the suite runs (`id`, `outcome`,
            `duration_s`, `message`, `index`, `t`); selects the streaming path, which loads the Live Lab plugin.
        order_files: Optional repo-relative test files that must run first, in this order (needs the plugin).
        timeout: Seconds before the process is killed; the run is then marked `timed_out` and keeps what finished.
        rule: Optional test-case order for the Live Lab plugin (`src/lab/plugin/br_order.py`); replaces `order_files`.
    """
    cmd = [python or sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           "-o", "junit_family=xunit1", f"--junitxml={out_xml}"]
    if test_ids is not None:
        if not test_ids:
            return SuiteRun(label, cmd, 0, 0.0, [])
        cmd += test_ids
    started = time.perf_counter()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    # Import the code of THIS worktree, not an editable install of another checkout (a `src/` layout installed with
    # `pip install -e` would otherwise run the tests against the checkout the install points at).
    paths = [str(workdir)] + ([str(workdir / "src")] if (workdir / "src").is_dir() else [])
    if on_result is None and order_files is None and timeout is None and rule is None:
        env["PYTHONPATH"] = os.pathsep.join(paths + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, env=env)
        wall = time.perf_counter() - started
        results = parse_junit([out_xml]) if out_xml.exists() else []
        order = execution_order([out_xml]) if out_xml.exists() else []
        return SuiteRun(label, cmd, proc.returncode, round(wall, 3), results, order)
    return _run_pytest_streaming(workdir, cmd, env, paths, out_xml, label, on_result, order_files, timeout, started, rule)


def _run_pytest_streaming(workdir: Path, cmd: list[str], env: dict, paths: list[str], out_xml: Path, label: str,
                          on_result, order_files: list[str] | None, timeout: float | None, started: float,
                          rule: dict | None = None) -> SuiteRun:
    import json as _json
    import tempfile
    import threading

    r_fd, w_fd = os.pipe()
    env["PYTHONPATH"] = os.pathsep.join([str(PLUGIN_DIR), *paths] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
    env["BR_LAB_FD"] = str(w_fd)
    if rule:
        env["BR_LAB_RULE"] = _json.dumps(rule)
    elif order_files:
        env["BR_LAB_ORDER"] = _json.dumps(order_files)
    cmd = [*cmd[:3], "-p", "br_lab_plugin", *cmd[3:]]
    streamed: list[TestResult] = []
    n_collected: int | None = None             # the plugin reports how many items pytest collected, before the first result
    with tempfile.TemporaryFile() as sink:
        proc = subprocess.Popen(cmd, cwd=workdir, env=env, stdout=sink, stderr=subprocess.STDOUT, pass_fds=[w_fd])
        os.close(w_fd)
        timed_out = threading.Event()

        def _kill() -> None:
            timed_out.set()
            proc.kill()

        timer = threading.Timer(timeout, _kill) if timeout else None
        if timer:
            timer.start()
        try:
            with os.fdopen(r_fd, "r", encoding="utf-8") as rf:
                for line in rf:
                    try:
                        ev = _json.loads(line)
                    except ValueError:
                        continue
                    if ev.get("k") == "collected":
                        n_collected = int(ev.get("n") or 0) or None
                        continue
                    if ev.get("k") != "result":
                        continue
                    tid = junit_test_id(ev.get("file"), ev.get("classname", ""), ev.get("name", ""))
                    res = TestResult(tid, ev["outcome"], round(float(ev["duration"]), 4), ev.get("message", ""))
                    streamed.append(res)
                    if on_result:
                        on_result({"id": tid, "nodeid": ev.get("nodeid", ""), "outcome": res.outcome,
                                   "duration_s": res.duration_s, "message": res.message, "index": len(streamed),
                                   "t": ev.get("t"), "of": n_collected})
            proc.wait()
        finally:
            if timer:
                timer.cancel()
    wall = time.perf_counter() - started
    if out_xml.exists() and not timed_out.is_set():
        results = parse_junit([out_xml])
        order = execution_order([out_xml])
    else:                                    # killed before pytest wrote its XML: what finished is what we have
        results = sorted(streamed, key=lambda r: r.test_id)
        order = [r.test_id for r in streamed]
    return SuiteRun(label, cmd, proc.returncode if proc.returncode is not None else -9, round(wall, 3), results, order,
                    timed_out.is_set())


def run_template(workdir: Path, template: str, tests: list[str] | None, junit_glob: str, label: str) -> SuiteRun:
    """Run a non-Python suite from a command template; read its JUnit XML."""
    cmd_str = template.replace("{tests}", ",".join(tests or [])) if tests else template.replace("-Dtest={tests}", "").replace("{tests}", "")
    started = time.perf_counter()
    proc = subprocess.run(cmd_str, cwd=workdir, shell=True, capture_output=True, text=True)
    wall = time.perf_counter() - started
    files = [Path(p) for p in sorted(glob.glob(str(workdir / junit_glob)))]
    return SuiteRun(label, [cmd_str], proc.returncode, round(wall, 3), parse_junit(files))


@dataclass
class RegressionReport:
    """What the agent hands back."""

    title: str
    commit: str
    verdict: str  # PASS | FAIL
    selected: dict
    full: dict | None
    impact_recall: str | None
    missed_failures: list[str]
    selection_ratio: str
    markdown_path: str
    json_path: str
    first_failure_position: int | None = None   # 1-based, in execution order (selected tests first, then the rest)
    first_failure_test: str | None = None
    ranker: str = "heuristic"
    timed_out: bool = False


class RegressionSuiteAgent:
    """Impact analysis + regression suite -> test report."""

    def run(self, impact: ImpactAnalysis, repo: Path | str, state_dir: Path | str | None = None, *,
            commit: str | None = None, full: bool = False, runner_cmd: str | None = None,
            junit_glob: str = "**/TEST-*.xml", python: str | None = None, on_test=None, single_pass: bool = False,
            timeout: float | None = None, case_order=None) -> RegressionReport:
        """Run the selected scope (and optionally the full suite) at ``commit``.

        Args:
            impact: The impact analysis whose tests form the selected scope.
            repo: The repository (its tests are the regression suite).
            state_dir: Agents' state directory.
            commit: Revision to test (default: the checked-out HEAD).
            full: Also run the full suite and measure impact recall.
            runner_cmd: Non-Python runner template with ``{tests}``.
            junit_glob: Where that runner writes JUnit XML.
            python: Interpreter for pytest (default: this one).
            on_test: Called with one dict per finished test (streaming; Python suites only).
            single_pass: Run the suite once, the impact files first, instead of the selected scope and then the
                whole suite. The selected results are the subset of that run in the at-risk files. Needs `full`.
            timeout: Seconds before a pytest process is killed.
            case_order: Optional zero-argument callable returning the Live Lab test-case rule (a dict, see
                `run_pytest(rule=...)`) or None; called just before the single pass starts.
        """
        repo = Path(repo).resolve()
        state = Path(state_dir) if state_dir else repo / ".blastradius"
        commit = gitops.head_sha(repo, commit or "HEAD")
        out = state / "reports" / f"regression-{commit[:12]}"
        out.mkdir(parents=True, exist_ok=True)
        # File-level selection for Python: every test in a file the impact analysis put at risk, so tests the
        # change itself added to those files are run too. Other runners get the individual test ids.
        # In the impact analysis's ranked order (E1 order when the model ranked them), so the likeliest
        # failures run first; ``first_failure_position`` below measures how early the first one surfaces.
        selected_targets = list(dict.fromkeys(t.file for t in impact.tests)) if not runner_cmd else [t.test_id for t in impact.tests]

        with gitops.worktree(repo, commit) as tree:
            if runner_cmd:
                sel = run_template(tree, runner_cmd, selected_targets, junit_glob, "selected")
                full_run = run_template(tree, runner_cmd, None, junit_glob, "full") if full else None
            elif single_pass and full:
                full_run = run_pytest(tree, None, out / "full.xml", "full", python, on_result=on_test,
                                      order_files=selected_targets, timeout=timeout,
                                      rule=case_order() if case_order else None)
                in_scope = [r for r in full_run.results if r.test_id.split("::")[0] in set(selected_targets)]
                sel = SuiteRun("selected", full_run.command, full_run.exit_code,
                               round(sum(r.duration_s for r in in_scope), 3), in_scope,
                               [t for t in full_run.order if t.split("::")[0] in set(selected_targets)])
            else:
                sel = run_pytest(tree, selected_targets, out / "selected.xml", "selected", python, on_result=on_test,
                                 timeout=timeout)
                full_run = run_pytest(tree, None, out / "full.xml", "full", python, on_result=on_test,
                                      timeout=timeout) if full else None

        missed: list[str] = []
        recall = None
        if full_run:
            actual = {r.test_id for r in full_run.failed}
            selected_ids = {r.test_id for r in sel.results}
            caught = actual & selected_ids
            missed = sorted(actual - caught)
            recall = f"{len(caught)}/{len(actual)}" if actual else "n/a (no failures)"
        n_sel = len(sel.results)
        total = len(full_run.results) if full_run else n_sel + len(impact.unaffected_tests)
        verdict = "FAIL" if sel.failed or (full_run and full_run.failed) or sel.exit_code not in (0, 5) else "PASS"

        order = list(sel.order or [r.test_id for r in sel.results])
        if full_run is not None:
            seen = set(order)
            order += [t for t in (full_run.order or [r.test_id for r in full_run.results]) if t not in seen]
        failed_ids = {r.test_id for r in sel.failed} | ({r.test_id for r in full_run.failed} if full_run else set())
        ff_pos = next((i for i, t in enumerate(order, 1) if t in failed_ids), None)
        ff_test = order[ff_pos - 1] if ff_pos else None

        hist = state / "history" / "test_outcomes.jsonl"
        hist.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with hist.open("a", encoding="utf-8") as fh:
            for r in (full_run or sel).results:
                fh.write(json.dumps({"ts": ts, "commit": commit, "test_id": r.test_id, "outcome": r.outcome,
                                     "message": r.message, "branch": impact.base_branch}) + "\n")

        md = self._markdown(impact, commit, verdict, sel, full_run, recall, missed, total)
        if ff_pos:
            md += (f"\n_Execution order ({impact.ranker} ranking first): the first failing test, `{ff_test}`, ran at "
                   f"position {ff_pos} of {len(order)}._\n")
        (out / "report.md").write_text(md, encoding="utf-8")
        report = RegressionReport(
            title=impact.title, commit=commit, verdict=verdict,
            selected={"counts": sel.counts(), "wall_s": sel.wall_s, "results": [asdict(r) for r in sel.results]},
            full={"counts": full_run.counts(), "wall_s": full_run.wall_s, "results": [asdict(r) for r in full_run.results]} if full_run else None,
            impact_recall=recall, missed_failures=missed, selection_ratio=f"{n_sel}/{total}",
            markdown_path=str(out / "report.md"), json_path=str(out / "report.json"),
            first_failure_position=ff_pos, first_failure_test=ff_test, ranker=impact.ranker,
            timed_out=bool((full_run and full_run.timed_out) or sel.timed_out),
        )
        (out / "report.json").write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
        return report

    @staticmethod
    def _markdown(impact: ImpactAnalysis, commit: str, verdict: str, sel: SuiteRun, full: SuiteRun | None,
                  recall: str | None, missed: list[str], total: int) -> str:
        c = sel.counts()
        L = [f"# Regression Test Report: {impact.title}", "",
             "| | |", "|---|---|",
             f"| Commit | `{commit[:12]}` |",
             f"| Verdict | **{verdict}** |",
             f"| Selected scope | {len(sel.results)} of {total} tests (the test files the impact analysis put at risk) |",
             f"| Selected run | {c['passed']} passed, {c['failed']} failed, {c['error']} errors, {c['skipped']} skipped in {sel.wall_s:.2f} s |"]
        if full:
            fc = full.counts()
            L += [f"| Full suite | {fc['passed']} passed, {fc['failed']} failed, {fc['error']} errors, {fc['skipped']} skipped in {full.wall_s:.2f} s |",
                  "| Impact recall | " + (f"{recall} of the failing tests were in the selected scope |" if not str(recall).startswith("n/a") else "no test failed, so there was nothing to miss |")]
        L += ["", "## Selected tests", "", "| Test | Outcome | Time (s) |", "|---|---|---:|"]
        L += [f"| `{r.test_id}` | {r.outcome} | {r.duration_s:.3f} |" for r in sel.results]
        failures = (full.failed if full else []) + [r for r in sel.failed if not full]
        if failures:
            L += ["", "## Failures", ""]
            L += [f"- `{r.test_id}`: {r.message or r.outcome}" + (" (**outside the impact scope**)" if r.test_id in missed else "") for r in failures]
        if missed:
            L += ["", "## Missed by the impact analysis", "",
                  f"{len(missed)} failing test(s) were outside the selected scope. Either the change touched code the "
                  "story did not call for (check the PR's out-of-scope files), or the dependency was invisible to static analysis."]
        L += ["", "_Generated by the BlastRadius Regression Suite Agent._", ""]
        return "\n".join(L)
