"""pytest plugin used by the Live Lab (stdlib only; it runs inside the target repository's interpreter).

Two jobs, both opt-in through environment variables set by `src.agents.regression.run_pytest`:

* ``BR_LAB_ORDER`` (a JSON list of repo-relative test files): items of those files run first, in that order; every
  other item keeps pytest's own collection order after them. The sort is stable, so order inside a file is untouched.
* ``BR_LAB_RULE`` (a JSON object, see `br_order.py`): every collected item is ordered by the BlastRadius test-case rule
  (E1 file tier, graph hop distance, id) instead. ``native_out`` in it names a file that receives pytest's own
  collection order (node ids), so the order "before the rule" can be derived from the same run.
* ``BR_LAB_FD`` (an inherited pipe descriptor): one JSON line per finished test, written when its teardown ends,
  with the outcome, the summed setup+call+teardown duration, and the file / classname / name triple that
  `junitxml` would write (the parent derives the canonical test id from it, exactly as for a JUnit file).
"""

from __future__ import annotations

import json
import os
import time

_FD = int(os.environ["BR_LAB_FD"]) if os.environ.get("BR_LAB_FD") else None
_ORDER = json.loads(os.environ.get("BR_LAB_ORDER") or "[]")
_RULE = json.loads(os.environ.get("BR_LAB_RULE") or "null")
_phases: dict[str, dict] = {}


def _emit(obj: dict) -> None:
    if _FD is not None:
        os.write(_FD, (json.dumps(obj) + "\n").encode("utf-8"))


def pytest_collection_modifyitems(config, items):  # noqa: D103
    if _RULE:
        import br_order

        native = [it.nodeid for it in items]
        cases = []
        for it in items:
            cls, name = _names(it.nodeid)
            cases.append({"id": br_order.junit_test_id(it.location[0], cls, name), "nodeid": it.nodeid})
        by_pos = br_order.order(cases, _RULE["tiers"], _RULE["hops"])
        items[:] = [items[i] for i in by_pos]
        if _RULE.get("native_out"):
            with open(_RULE["native_out"], "w", encoding="utf-8") as fh:
                json.dump(native, fh)
    elif _ORDER:
        rank = {f: i for i, f in enumerate(_ORDER)}
        items.sort(key=lambda it: rank.get(it.nodeid.split("::")[0], len(rank)))
    _emit({"k": "collected", "n": len(items), "t": time.time(), "order": [it.nodeid for it in items]})


def _names(nodeid: str) -> tuple[str, str]:
    try:
        from _pytest.junitxml import mangle_test_address

        names = mangle_test_address(nodeid)
        return ".".join(names[:-1]), names[-1]
    except Exception:                              # private helper; fall back to a plain split
        parts = nodeid.split("::")
        return ".".join([parts[0][:-3].replace("/", ".")] + parts[1:-1]), parts[-1]


def pytest_runtest_logreport(report):  # noqa: D103
    st = _phases.setdefault(report.nodeid, {"duration": 0.0, "outcome": "passed", "message": ""})
    st["duration"] += float(report.duration or 0.0)
    if report.when == "call" or report.outcome != "passed":
        if report.outcome == "failed":
            st["outcome"] = "failed" if report.when == "call" else "error"
            lr = getattr(report, "longrepr", None)
            crash = getattr(lr, "reprcrash", None)
            st["message"] = (getattr(crash, "message", None) or str(lr or "")).strip().splitlines()[0][:300] if (crash or lr) else ""
        elif report.outcome == "skipped":
            st["outcome"] = "skipped"
            lr = getattr(report, "longrepr", None)
            st["message"] = str(lr[2] if isinstance(lr, tuple) and len(lr) == 3 else lr or "")[:300]
    if report.when == "teardown":
        st = _phases.pop(report.nodeid)
        cls, name = _names(report.nodeid)
        _emit({"k": "result", "t": time.time(), "nodeid": report.nodeid, "file": report.location[0], "classname": cls,
               "name": name, **st})
