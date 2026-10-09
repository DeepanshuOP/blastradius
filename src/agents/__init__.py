"""BlastRadius agentic workflow: five agents that take a user story to a deployed, regression-tested change.

    Impact Analysis Agent   user story + codebase        -> impact analysis document
    Coding Agent            impact analysis + codebase   -> changed files + pull request
    PR Reviewer Agent       pull request + impact doc    -> review, merge, merge commit id
    Build & Deploy Agent    commit id + branch           -> build, package, deploy (notify on failure)
    Regression Suite Agent  impact doc + regression suite-> test report

This package is a separate, cuttable demo path (D-55), the same standing as the
T4.4 re-ranker under D-17: it may call an LLM, so nothing here is imported by the
reproducible pipeline (`src/harvest`, `src/parse`, `src/label`, `analysis/`) and
no number it produces reaches `make tables`, `release/` or the paper.

Every agent also runs fully offline: without an LLM the impact analysis is
keyword + code-graph based, and the coding agent applies a recorded patch.
"""

__all__ = ["__doc__"]
