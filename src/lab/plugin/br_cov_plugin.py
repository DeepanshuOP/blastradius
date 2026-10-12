"""pytest plugin used by the Live Lab's coverage strategy (stdlib only; it runs inside the target repository's interpreter).

Opt-in: it does nothing unless ``BR_LAB_COV`` names an output file. Then, for every test, a global ``sys.settrace``
function records each Python function whose code object is *called* while the test runs (setup, call and teardown),
restricted to files under ``BR_LAB_COV_ROOT``. The trace function returns ``None``, so no line events are traced: the
cost is one call per Python frame. At the end of the session one JSON object is written:

    {"tests": {nodeid: {"file", "classname", "name", "functions": [[relpath, firstlineno, qualname], ...]}}}

Function lists are sorted, so the output depends only on what ran.
"""

from __future__ import annotations

import json
import os
import sys
import threading

_OUT = os.environ.get("BR_LAB_COV")
_ROOT = os.path.realpath(os.environ.get("BR_LAB_COV_ROOT") or os.getcwd()) + os.sep
_tests: dict[str, dict] = {}
_seen: set = set()
_paths: dict[str, str | None] = {}


def _rel(filename: str) -> str | None:
    r = _paths.get(filename)
    if r is None and filename not in _paths:
        real = os.path.realpath(filename)
        r = real[len(_ROOT):] if real.startswith(_ROOT) else None
        _paths[filename] = r
    return r


def _tracer(frame, event, arg):  # noqa: ANN001
    if event == "call":
        _seen.add(frame.f_code)
    return None


def _names(nodeid: str) -> tuple[str, str]:
    try:
        from _pytest.junitxml import mangle_test_address

        names = mangle_test_address(nodeid)
        return ".".join(names[:-1]), names[-1]
    except Exception:                              # private helper; fall back to a plain split
        parts = nodeid.split("::")
        return ".".join([parts[0][:-3].replace("/", ".")] + parts[1:-1]), parts[-1]


if _OUT:
    import pytest

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(item, nextitem):  # noqa: D103, ANN001
        _seen.clear()
        sys.settrace(_tracer)
        threading.settrace(_tracer)
        try:
            yield
        finally:
            sys.settrace(None)
            threading.settrace(None)
            funcs = set()
            for co in _seen:
                rel = _rel(co.co_filename)
                if rel is not None:
                    funcs.add((rel, co.co_firstlineno, getattr(co, "co_qualname", co.co_name)))
            _seen.clear()
            cls, name = _names(item.nodeid)
            _tests[item.nodeid] = {"file": item.location[0], "classname": cls, "name": name,
                                   "functions": sorted([list(f) for f in funcs])}

    def pytest_sessionfinish(session, exitstatus):  # noqa: D103, ANN001
        with open(_OUT, "w", encoding="utf-8") as fh:
            json.dump({"tests": dict(sorted(_tests.items()))}, fh, separators=(",", ":"))
