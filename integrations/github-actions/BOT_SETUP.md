# BlastRadius PR bot: setup (exploratory, D-63)

The bot comments on a pull request with: the tests most at risk (E1 ranker, with reasons), the test results
ordered risk-first, a triage of each failure (mine / inherited / flaky) and, for a failure that is **mine**, a
repair patch. A patch appears as a GitHub *suggestion* only if the **full suite passed with it**; otherwise it is a
collapsed diff marked "not validated". The bot only comments: it never pushes, merges or approves.

Not run live yet by this project until you do the steps below on a repository you own (D-63).

## 1. A sandbox repository

1. Create (or fork) a small **Python** repository you own, with `pytest` tests that pass on `main`.
   Anything with 10 to 60 tests and some git history works; the E1 ranker reads the repository's own history.
2. Do not use a repository you do not own: the workflow writes comments with its token.

## 2. The Groq secret

Repository → Settings → Secrets and variables → Actions → **New repository secret**: `GROQ_API_KEY` = your Groq key.
Without it the bot still ranks, runs and triages, and says "No model is configured".
The model is `openai/gpt-oss-120b` (free tier, daily token cap); a run costs a few thousand tokens.

## 3. The workflow

1. Copy `integrations/github-actions/blastradius-bot.yml` from this repository to
   `.github/workflows/blastradius-bot.yml` in the sandbox repository.
2. **Pin the tool**: replace `ref: upgrade-2.1` with a commit sha of `DeepanshuOP/blastradius`
   (`git rev-parse HEAD` in your clone) so the bot's behaviour does not change under you.
3. **Edit the dependency step** to install your repository the way it needs (the tests run inside BlastRadius's
   environment).
4. The workflow's permissions are `contents: read` and `pull-requests: write`; each line is explained in the file.

## 4. Open a test pull request

1. On a branch, introduce a plain bug (flip a comparison, change `+` to `-`) in a function your tests cover.
2. Open a pull request into `main`. The `blastradius-bot` job runs in a few minutes.
3. Expected: one comment starting with "## BlastRadius" with sections 1 to 4, and (if the bug was repairable) a
   review with an inline suggestion on the changed line and an **Apply suggestion** button.
4. Push another commit: the bot **edits** its comment instead of posting a new one.

## Troubleshooting

| Symptom | Cause |
|---|---|
| No comment, job skipped | PR from a fork (no token, no secrets), or the workflow file is not on the base branch |
| `Resource not accessible by integration` | Settings → Actions → General → Workflow permissions must allow the token to write PRs (the `permissions:` block asks for `pull-requests: write`) |
| "E1 model unavailable" | `models/e1_lgbm_v1.txt` missing in the pinned tool checkout, or the `ml` extra not installed |
| No tests ran / all errors | The dependency step did not install the target; `ModuleNotFoundError` is in the job log |
| "No model is configured" | `GROQ_API_KEY` secret missing |
| "Not validated" patch | The model's patch did not make the full suite pass, or it broke another test: by design it is not offered |
| `DailyQuotaReached` in the log | Groq free tier daily token cap; the rest of the comment is still posted next run |

The LLM cache is uploaded as the `blastradius-bot-cache` artifact. To replay a run offline:
`BR_LLM_REPLAY=1 make bot-local REPO=<clone> BASE=<sha> HEAD=<sha>` with `BR_LLM_CACHE_DIR` pointing at the
downloaded cache.

## Local dry run (prints the comment, posts nothing)

    make bot-local REPO=/path/to/clone BASE=<base sha> HEAD=<head sha> PR=1
