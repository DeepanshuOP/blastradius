"""The BlastRadius test-case order (Live Lab, D-65), stdlib only so the pytest plugin and the arena share one function.

Rule, fixed on 2026-10-12, after the PR 1 case had been seen (not before it, and not tuned on it afterwards):

    1. keep the E1 file rank: test files with a higher E1 score run first;
    2. test files tied in E1 score form one tier;
    3. inside a tier, test cases run by graph hop distance to the changed functions, shortest first, then by id.

Because rule 3 sorts the cases of a tier together, a single file is the one-file case of the same rule ("within a
file"). A case that has no test node in the graph, or that the change does not reach, sorts after every reached case of
its tier. The sort is stable: two cases with the same key keep their incoming order.
"""

from __future__ import annotations

RULE_ID = "e1-rank-then-hops"
RULE_FIXED = "2026-10-12"
RULE_TEXT = ("E1 file rank is kept. Within a file, and for files tied in E1 score, test cases run by graph hop distance "
             "to the changed functions (shortest first), then by id. Fixed on 2026-10-12, after the PR 1 case was seen.")
UNREACHED = 10 ** 6
UNLISTED = 10 ** 6


def junit_test_id(file: str | None, cls: str, name: str) -> str:
    """The canonical id of a collected case (`src.agents.regression.junit_test_id`, repeated here because the plugin
    runs inside the target repository's interpreter; `tests/test_lab_order.py` asserts the two agree)."""
    if file and file.endswith(".py"):
        module = file[:-3].replace("/", ".")
        owner = cls[len(module) + 1:] if cls.startswith(module + ".") else ""
        return f"{file}::{owner}::{name}" if owner else f"{file}::{name}"
    return f"{cls.split('.')[-1]}#{name}" if cls else name


def split_case_id(case_id: str) -> tuple[str, str | None, str]:
    """`(file, innermost class or None, function)` of a canonical id, parameter suffix removed."""
    base = case_id.partition("[")[0]
    parts = base.split("::")
    if len(parts) == 2:
        return parts[0], None, parts[1]
    return parts[0], parts[-2].split(".")[-1], parts[-1]


def hop_of(hops: dict[str, int], case_id: str) -> int:
    """Graph hop distance of a case, `UNREACHED` when the graph has no matching reached test node.

    `hops` maps `"file::Class::function"` (and `"file::*::function"`, the minimum over classes) to a distance. A case
    whose id carries no class (a module-level function, or a test inherited from a mixin, whose canonical id names the
    defining file only) uses the `*` entry.
    """
    file, owner, func = split_case_id(case_id)
    key = f"{file}::{owner}::{func}" if owner else f"{file}::*::{func}"
    return hops.get(key, UNREACHED)


def order(cases: list[dict], tiers: dict[str, int], hops: dict[str, int]) -> list[int]:
    """Indices of `cases` in the BlastRadius order.

    Args:
        cases: `{"id": canonical id, "nodeid": collected node id}` per case (extra keys ignored).
        tiers: test file (as collected, the node id's file part) -> tier number, 0 first; equal E1 scores, equal tier.
        hops: see `hop_of`.
    """
    def key(i: int) -> tuple:
        c = cases[i]
        file = (c.get("nodeid") or c["id"]).split("::")[0]
        return (tiers.get(file, UNLISTED), hop_of(hops, c["id"]), c["id"], i)

    return sorted(range(len(cases)), key=key)
