# Launch readiness — harvester daemon, full 300-repo frame, stages 1+2

Read-only investigation. No file under `src/` or `tests/` was modified. No commit was made.

## CLI surface

Verbatim from `parse_args()` in `src/harvest/daemon.py`:

```python
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos", type=Path, default=DEFAULT_REPOS_PATH)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage", choices=("1", "2", "3", "both", "all"), default=DEFAULT_STAGE)
    return parser.parse_args(argv)
```

Defaults (module-level constants):

```python
DEFAULT_REPOS_PATH = Path("data/frame/frame_v1.csv")
DEFAULT_LIMIT = 2
DEFAULT_STAGE = "both"
```

Flag list:

| Flag | Type | Choices | Default |
|---|---|---|---|
| `--repos` | `Path` | any path | `data/frame/frame_v1.csv` |
| `--limit` | `int` | any int | `2` |
| `--dry-run` | flag (`store_true`) | — | `False` |
| `--stage` | `str` | `1`, `2`, `3`, `both`, `all` | `both` |

- **`--dry-run` exists** (`store_true` flag).
- **`--limit` default is `2`** — a low safety default; the full-frame run requires `--limit 300` explicitly.
- **`--stage` valid values are exactly**: `1`, `2`, `3`, `both`, `all`. Per `run()`'s docstring and body, `both` means stages 1+2 (unchanged historical meaning), `all` means 1+2+3. There is no `"1+2"` literal — `both` is the correct flag for this task.

## Frame shape

```
$ wc -l data/frame/frame_v1.csv
301 data/frame/frame_v1.csv

$ head -2 data/frame/frame_v1.csv
owner,repo,lang,stars,commits,default_branch,n_runs_90d,test_workflow_ids,license,sample_rank
graphql-java,graphql-java,Java,6225,6513,master,768,242705764;5487211,MIT License,1

$ awk -F, 'NR>1 {print $3}' data/frame/frame_v1.csv | sort | uniq -c
    150 Java
    150 Python
```

301 lines (1 header + 300 repos), 150/150 Java/Python split. Matches expectation exactly.

## Token state

Three PAT keys are present in `.env` by name (values never printed):

```
$ cut -d'=' -f1 .env
GITHUB_PAT_1
GITHUB_PAT_2
GITHUB_PAT_3
```

(Note: the literal command specified in the prompt, `grep -o '^[A-Z_]*=' .env`, matched
nothing — the character class `[A-Z_]` doesn't include digits, and these key names end
in `_1`/`_2`/`_3`, so the anchored `=` never follows a full `[A-Z_]*` run. Used `cut -d'=' -f1`
instead, which only ever prints key names, never values.)

**Remaining quota was not checked — skipped rather than worked around.** `TokenPool`
(`src/harvest/ratelimit.py`) has no ready path to report quota without spending a
request: `_TokenState.remaining` is seeded to `DEFAULT_REMAINING` at construction and is
only ever updated from live response headers inside `update()`, which is only called
after a real `get_with_backoff()` round-trip. There is no persisted/cached quota file to
read, and per ROADMAP §34.4 C.1 `get_with_backoff()` is the only place in the codebase
allowed to issue a request — so checking quota here would mean issuing one, which this
task forbids. Skipped per instructions.

## Dry-run command, output, and requests.jsonl delta

```
$ wc -l logs/requests.jsonl
40340 logs/requests.jsonl
```

Exact command run:

```
$ uv run python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both --dry-run
[dry-run] 300 repo(s) selected from data/frame/frame_v1.csv (--limit 300); at least 300 request(s) required (1 pulls-listing page per repo, minimum). Actual total also includes further pulls pages plus 2 requests per in-window PR — unknown without querying, which --dry-run does not do.
```

```
$ wc -l logs/requests.jsonl
40340 logs/requests.jsonl
```

**Delta: 0.** The dry run issued zero HTTP requests. Acceptance criterion met.

A second dry run with `--stage 1` (instead of `--stage both`) was also run, to test
Predicted Failure #2, and produced **byte-identical output**:

```
$ uv run python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage 1 --dry-run
[dry-run] 300 repo(s) selected from data/frame/frame_v1.csv (--limit 300); at least 300 request(s) required (1 pulls-listing page per repo, minimum). Actual total also includes further pulls pages plus 2 requests per in-window PR — unknown without querying, which --dry-run does not do.
```

`requests.jsonl` was still 40340 lines after this second run — cumulative delta across
both dry runs is also **0**.

## Predicted-failure check

1. **`--dry-run` does not exist** — not triggered. It exists.
2. **`--dry-run` exists but ignores `--stage`** — **CONFIRMED.** `main()` calls
   `dry_run_estimate(args.repos, args.limit)` — `args.stage` is never passed in. The
   function signature is `dry_run_estimate(repos_path: Path, limit: int) -> int`, with no
   stage parameter at all. Empirically verified above: `--stage both` and `--stage 1`
   produce identical output. The tool computes a single stage-agnostic floor
   ("1 pulls-listing page per repo, minimum") and cannot distinguish a stage-1-only run
   from a stage-1+2 run from a stage-1+2+3 run. Per instructions: stopping here rather
   than fixing or working around it.
3. **`--limit` clamping / off-by-one on the header row** — not triggered. `_load_repos()`
   uses `csv.DictReader`, which consumes the header row itself; `rows[:limit]` then
   slices only data rows. With `--limit 300` on a 301-line file (300 data rows), exactly
   300 repos were selected — verified in the dry-run output above ("300 repo(s) selected").

No fourth failure mode was observed beyond what's noted below.

## Estimated total requests for stages 1+2 across 300 repos

**Not producible from `--dry-run` as it stands.** Because of confirmed Failure #2, the
tool's own number (300) is only ever a stage-1 floor — one pulls-listing page per repo —
and, by the code's own docstring, explicitly excludes further pulls pages, all of stage
2 (run discovery), and the "2 requests per in-window PR" cost. Reporting 300 as "the
stage 1+2 estimate" would misrepresent what the tool measured.

I deliberately did not substitute an estimate derived by mining `logs/requests.jsonl`
history instead — that log mixes provenance (see below) and building a number from it
would be exactly the kind of "work around it" the task told me not to do in place of a
real fix to the estimator.

**Verdict: no reliable requests total for stages 1+2/300 repos exists today.**

## Estimated wall-clock hours

Same caveat applies — no honest per-stage number exists to convert into hours. The only
mechanically available figure is the stage-1 floor:

- 300 requests ÷ 15,000 req/hr ≈ **0.02 hours**
- 300 requests ÷ 10,000 req/hr ≈ **0.03 hours**

**These numbers are not a usable estimate of real run time** — they cover only the
guaranteed-minimum first pulls-listing page per repo, not stage 2, not additional pulls
pages, not per-PR costs. Treat them as a floor, not a forecast.

## Anything found that contradicts the above

- `logs/requests.jsonl` (40340 lines) contains real per-repo request history for a
  subset of frame repos, but it is of **mixed, unclear provenance**: 10 frame repos show
  `pulls`-endpoint activity (2,602 requests total — consistent with a partial/interrupted
  stage-1 pilot), while all 300 frame repos show `actions/runs`-endpoint activity (10,369
  requests total). The latter's full 300/300 coverage looks more consistent with the
  process that computed the frame's own `n_runs_90d` column than with a stage-2 harvest
  run (stage 2 has apparently never been run daemon-side across the full frame). This
  data was not used to build the estimate above, since its origin can't be confirmed from
  read-only inspection.
- `logs/requests.jsonl` also contains ~84 entries against a dummy `repos/x/y` URL,
  consistent with test-suite traffic sharing the same log file — a further reason not to
  treat this file as a clean harvest-history source without more digging.
- `dry_run_estimate()`'s own docstring already says as much: *"A request-count floor, not
  a full estimate... neither knowable without actually querying — which `--dry-run`
  exists specifically to avoid."* The tool is behaving as documented; the gap is that its
  floor is stage-1-only, undocumented as such, and silently identical for every `--stage`
  value including `3` and `all`.

## Go / no-go

**NO-GO** for launching the full 300-repo stage-1+2 run today, on measurement grounds
(not safety grounds — nothing here suggests the run would fail or corrupt data). The
blocker is that there is currently no way to state, before launch, how many requests or
hours a 300-repo stage-1+2 run will actually cost: `--dry-run` only floors stage 1 and is
silent on stage 2 regardless of `--stage`. Before a full launch, either (a) fix
`dry_run_estimate()` to be stage-aware (out of scope for this report — a separate
decision), or (b) run a small calibration batch (e.g. `--limit 10 --stage both`, live)
to measure real per-repo request cost empirically and extrapolate from that instead of
from `--dry-run`.
