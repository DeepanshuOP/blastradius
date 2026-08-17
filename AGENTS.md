# AGENTS.md — standing rules for any coding agent in this repository

Project: BlastRadius — a GitHub Actions harvester building an execution-grounded
dataset (BR-Bench). docs/ROADMAP.md is the source of truth for what to build;
docs/DECISIONS.md for choices already made; docs/SCHEMAS.md is FROZEN and wins
on any field or type. CLAUDE.md holds build constants. This file loses to all
of them.

## STOP — a live process is running
A harvester daemon (PID in docs/HANDOFF.md) is capturing unrecoverable data on
a 90-day expiry clock. Losing it costs data that cannot be re-fetched.
- NEVER run `wsl --shutdown`, `kill`, `pkill`, `killall`, or signal any process.
- NEVER restart WSL, or suggest restarting it.
- NEVER write to, move, or delete anything under data/ or logs/.
- If you believe the daemon must be stopped, STOP and say so. Do not act.

## Absolute prohibitions
- NEVER read, print, edit, or reformat `.env`. Confirm keys by NAME only.
  Never print a PAT value or any fragment of one.
- NEVER `git add -A` or `git add .`. Always name explicit paths.
- NEVER commit without explicit operator authorization as a separate step.
- NEVER add `Co-Authored-By`, `Generated-with`, or any other trailer to a
  commit message. This repository's history carries no trailers.
- NEVER modify a test to make it pass. Fixture values are ground truth. If a
  test fails, fix the CODE. If you believe the test itself is wrong, STOP and
  explain why rather than editing it.
- NEVER change docs/SCHEMAS.md. It is frozen; a change there is an escalation.
- NEVER add a dependency without asking first.

## Every session opens with this guard
    uname -s && pwd && uv run python --version
Expected: Linux, /home/shree/blastradius, Python 3.11.15.
Stop immediately on any mismatch.

## Before any commit
    git config user.name    # must be DeepanshuOP
    git config user.email   # must be 99538840+DeepanshuOP@users.noreply.github.com
Mismatch = STOP.

## HTTP
`get_with_backoff()` in src/harvest/ratelimit.py is the ONLY place in this
codebase permitted to issue an HTTP request. Never write another one anywhere.

## Running the harvester
Credentials load via `uv run --env-file .env`. Plain `uv run` fails with
"no GitHub PAT found in environment" — TokenPool.from_env() reads os.environ
and nothing loads .env into it otherwise.

## Reporting — not optional
Prose is not evidence. "Tests pass" is a claim, not proof. Report raw command
output, verbatim and unsummarised, for every command you run, with the exact
command stated before its output. If output is long, write it to a file, print
`wc -l` first, then emit it in labelled 60-line chunks.

Before running tests, PREDICT the passing count. Report prediction and actual.
A deviation is a signal to investigate, not a nuisance to smooth over.

## Documentation — write as you go, not at the end
1. Per task: `docs/session/YYYY-MM-DD-<task-id>.md` containing: the task
   statement, every exact command run, raw output, files changed with line
   counts, test count before and after, non-goals honoured, anything found
   that contradicts the instructions, and open questions.
2. Then APPEND a dated entry to `docs/HANDOFF.md`: date, model, task id,
   one-line outcome, files touched, current test count, commit hash (or
   "uncommitted"), and the single next action.

docs/HANDOFF.md is the switchover file. Another agent, or a different tool
entirely, must be able to resume from it alone.

## Scope
One task, one deliverable, one file (or one tightly-coupled pair). If a task
cannot be stated in one sentence with one pass/fail condition, STOP and say it
is too big. Do not touch files outside the stated scope, even to improve them.

## When the instructions are wrong
The task's list of steps and predicted failures is a HYPOTHESIS, not a spec.
If you find an additional failure mode, a bug in the instructions, or a command
that cannot work as written, REPORT IT and stop. Do not silently work around
it. Catching an error in the prompt is a success, not a deviation.

## No external sources
Do NOT use web search or fetch any URL. This repository, its docs/, and its
data/ are the only permitted sources. If you cannot answer from them, say so.

## Session report naming
Session reports are `docs/session/NNN-YYYY-MM-DD-<taskid>-<slug>.md`, where
NNN is the next unused three-digit sequence number. Check the existing highest
number before writing. Update docs/session/INDEX.md in the same step.
