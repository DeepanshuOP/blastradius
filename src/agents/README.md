# BlastRadius agents: user story to deployed, regression-tested change

Five agents that hand work to each other. The impact analysis is built on the
BlastRadius code graph (the same commit-pinned tree-sitter extractor as
`src/graph/`), and every later agent checks its work against that analysis.

| # | Agent | Input | Action | Output |
|---|---|---|---|---|
| 1 | Impact Analysis | user story, codebase | match the story to source files; find the tests that depend on them in the code graph; weight by past failures | `impact.md` (document) + `impact.json` |
| 2 | Coding | impact analysis, codebase | write the change on a new branch (LLM, or a recorded change set offline); every `.py` must compile | changed files, commit, pull request |
| 3 | PR Reviewer | PR, impact analysis | scope check against the impact analysis, compile check, run the tests at risk, CI status, optional model review | verdict; on APPROVE merges and returns the merge **commit id** |
| 4 | Build & Deploy | commit id, branch | build at the commit (full test suite / Maven / Gradle), package (`git archive`), deploy; GitHub mode dispatches a workflow | deployed package, or **notification** on build failure |
| 5 | Regression Suite | impact analysis, regression suite | run the selected scope and the full suite | test report with impact recall (failing tests the analysis predicted) |

## Run it

From the repository root, in WSL2:

```bash
make agents-demo                 # three recorded scenarios, offline; writes demo-web/public/data/agents.json
make demo-web                    # then open the "Agents" tab on http://localhost:3000
```

Any agent on any git repository:

```bash
uv run --extra graph python -m src.agents impact   --repo ../myrepo --story "As a user I want ..."
uv run --extra graph python -m src.agents code     --repo ../myrepo --impact ../myrepo/.blastradius/impact/<sha>/impact.json
uv run --extra graph python -m src.agents review   --repo ../myrepo --impact <impact.json> --pr 1
uv run --extra graph python -m src.agents deploy   --repo ../myrepo --commit <merge sha> --branch main
uv run --extra graph python -m src.agents regress  --repo ../myrepo --impact <impact.json> --full
uv run --extra graph python -m src.agents pipeline --repo ../myrepo --story "..."      # all five in order
```

Outputs go to `<repo>/.blastradius/` (added to `.git/info/exclude` automatically).

| Setting | Effect |
|---|---|
| `ANTHROPIC_API_KEY` | enables the model: story interpretation and acceptance criteria, code generation, review comments (`BR_AGENT_MODEL` picks the model) |
| `--forge github` + `GITHUB_TOKEN` | push branches, open and merge real PRs; `deploy --github-workflow <file>` dispatches a workflow and waits for it |
| `BR_NOTIFY_WEBHOOK` | build-failure notifications also go to a Slack or Discord webhook (always logged to `notifications.jsonl`) |
| `BR_OFFLINE=1` | no network at all; the model is off and the webhook is skipped |
| `review --scope-policy warn` | out-of-scope files are reported but do not block the merge |

## The demo scenarios (`make agents-demo`)

Same story each time: *"As a shopper, I want to apply the discount code FESTIVE20 at checkout to get 20% off my cart total, capped at Rs 500."* on the bundled `shopcart` library (15 tests).

1. **Clean change.** Impact analysis puts 7 of 15 tests at risk (pricing and cart; tax, catalog, inventory and receipt untouched). The change set edits `pricing.py` and adds 3 tests; the reviewer approves and merges; the build passes and deploys; regression PASS (10 of 18 tests selected, 18/18 in the full suite).
2. **Out-of-scope change blocked.** The change set also rewrites `receipt.py`. The reviewer's scope check fails and it requests changes; nothing merges.
3. **Build fails, team notified.** The same change with the reviewer in warn mode: it merges, the full build fails on the two receipt tests, the deploy agent sends a `build_failed` notification and deploys nothing, and the regression report shows impact recall 0/2, both failures outside the predicted scope.

## Decision D-55 and limits

This package is a separate, cuttable demo path with the same standing as the T4.4 re-ranker under D-17. It may call an LLM, so nothing in the reproducible pipeline imports it, and no number it produces reaches `make tables`, `release/` or the paper. GitHub reads go through `get_with_backoff()`; writes (open PR, review, merge, workflow dispatch) go through the single `GitHubForge._write()`.

- Static reachability misses dynamic dispatch and reflection, so the impact scope is a ranked scope, not an RTS-style safety guarantee. The regression agent's full-suite run is the check on it.
- Offline, the requirement-to-code step is keyword matching, and the coding agent only replays recorded change sets.
- Selection is by Python test file (pytest) or by test id through a runner template (`--runner-cmd 'mvn -q test -Dtest={tests}'`).
