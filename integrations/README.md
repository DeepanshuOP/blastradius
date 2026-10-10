# CI integration examples

**These are examples, not deployments.** Nothing in this directory has been run on a Jenkins server
or a GitHub Actions runner by this project; BR-Bench itself was mined from GitHub Actions logs, but
BlastRadius has not been wired into a live CI system. The commands are the real CLI of
`python -m src.agents` and are exercised offline by `tests/test_agents*.py` and `make agents-demo`.

## The division of labour

| | Jenkins / GitHub Actions | BlastRadius |
|---|---|---|
| runs the tests | yes (the executor) | no |
| decides what to run first | no (retest-all, or a static list) | **Impact**: E1 ranker over BR-Bench-trained features |
| explains a failure | no (every failure is "yours") | **Triage**: mine / inherited / flaky |
| proposes a fix | no | **Repair**: a patch accepted only if the full suite passes |
| gate on the result | yes | no: BlastRadius proposes, the CI server decides |

In every experiment the CI server's own behaviour is a baseline row: retest-all (B0), blame-all (E2),
notify-only (E3 arm R0). Per the project's non-goals, BlastRadius does not block merges on predicted
risk, and a repair is never merged without a human or the CI gate.

- `jenkins/Jenkinsfile`: Impact -> ordered test run -> Triage -> Repair suggestion -> archive.
- `github-actions/blastradius.yml`: the same as a reusable workflow.

Results to quote for what this buys are in `docs/RESULTS_2.md`, including the ones that did not work.
