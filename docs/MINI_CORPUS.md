# MINI_CORPUS — the 3-repo graph-layer mini-corpus

Graph-layer only (D-48: out of the MSR paper, BITE497J deliverable). Nothing here
feeds `make tables`, `release/` or the paper.

## Selection rule

From `data/interim` (read-only), one repo per build system: one pytest (Python),
one Gradle (Java), one Maven (Java). Within each group, the repo with the most
**instances that have a resolved base SHA**; ties broken alphabetically.

Operationally:

- *group* — a repo's dominant harness in `data/interim/parsed_outcomes.parquet`
  (the harness with the most parsed outcomes; ties by harness name), crossed with
  `language` from `data/interim/instances_raw.parquet`.
- *instance with a resolved base SHA* — a row of `instances_raw.parquet` whose
  `run_id` appears in `data/interim/base_resolution.parquet` with
  `status != 'no_base'` and a non-null `base_sha`. The three resolved statuses are
  `exact`, `exact_green` and `ancestor`.

Every `base_sha` in `instances_raw.parquet` is non-null (165,349/165,349), so that
column alone does not distinguish a resolved base; `base_resolution.parquet` is the
authority, and it resolves 2,359/12,581 run-level rows.

## Selected repos

| Group | Repo | Clone dir | Resolved instances | Distinct base SHAs | Base SHAs in clone | Clone size | Files at HEAD |
|---|---|---|---|---|---|---|---|
| pytest (Python) | `fla-org/flash-linear-attention` | `data/clones/fla-org__flash-linear-attention` | 164 | 107 | 107/107 | 104 MB | 781 |
| Gradle (Java) | `Stirling-Tools/Stirling-PDF` | `data/clones/Stirling-Tools__Stirling-PDF` | 177 | 140 | 140/140 | 588 MB | 7955 |
| Maven (Java) | `spiculedata/saiku` | `data/clones/spiculedata__saiku` | 217 | 180 | 180/180 | 73 MB | 2069 |

## Why these three, group by group

### pytest (Python)

| Rank | Repo | Resolved instances | Distinct base SHAs |
|---|---|---|---|
| 1 | `fla-org/flash-linear-attention` ← **selected** | 164 | 107 |
| 2 | `dask/distributed` | 2 | 1 |

### Gradle (Java)

| Rank | Repo | Resolved instances | Distinct base SHAs |
|---|---|---|---|
| 1 | `Stirling-Tools/Stirling-PDF` ← **selected** | 177 | 140 |
| 2 | `apache/fineract` | 37 | 23 |
| 3 | `openremote/openremote` | 23 | 13 |
| 4 | `diffplug/spotless` | 19 | 19 |
| 5 | `mcreator/mcreator` | 17 | 9 |
| … | _9 further candidates_ | | |

### Maven (Java)

| Rank | Repo | Resolved instances | Distinct base SHAs |
|---|---|---|---|
| 1 | `spiculedata/saiku` ← **selected** | 217 | 180 |
| 2 | `atmosphere/atmosphere` | 170 | 52 |
| 3 | `apache/flink` | 134 | 30 |
| 4 | `unicode-org/cldr` | 63 | 24 |
| 5 | `apache/hugegraph` | 52 | 26 |
| … | _13 further candidates_ | | |

Notes on the ranking:

- **pytest (Python)** — only three repos have `pytest` as their dominant harness:
  `apache/beam` (392 resolved instances), `fla-org/flash-linear-attention` (164) and
  `dask/distributed` (2). `apache/beam` is excluded because its corpus `language` is
  `Java` (59,143/59,143 of its instances), so it is not the Python member of the
  split; `fla-org/flash-linear-attention` is the largest genuinely-Python candidate.
- **Gradle (Java)** — `Stirling-Tools/Stirling-PDF` leads by 177 to 37 over the
  runner-up (`apache/fineract`).
- **Maven (Java)** — `spiculedata/saiku` leads by 217 to 170 over
  `atmosphere/atmosphere`.
- `castorini/anserini` has 595 parsed Maven outcomes but 0 instances with a resolved
  base SHA, so it is not eligible despite being the only repo an existing test names
  as a clone (`tests/test_cochange_mine.py`).

## Clones

```bash
git clone --filter=blob:none https://github.com/<repo>.git data/clones/<owner>__<name>
```

`data/clones/` is git-ignored by the existing `data/*` rule in `.gitignore`
(`git check-ignore -v data/clones` → `.gitignore:2:data/*`); no clone is committed.

Size and build budgets (ROADMAP §19.4, and the 2 GB / 15 min drop rule for this
task): all three clones are far below 2 GB, so no candidate was dropped for size.
Cold-build times are recorded in the builder step's report, not here.

### One deviation worth recording

A plain `--filter=blob:none` clone of `Stirling-Tools/Stirling-PDF` carried only
38/140 of its base SHAs: the rest are commits reachable only from pull-request
refs, not from any branch or tag. They were recovered with

```bash
git fetch --filter=blob:none origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
```

which took the clone from 349 MB to 588 MB and base-SHA coverage to 140/140. The
other two repos needed no extra fetch (107/107 and 180/180 from the plain clone).

## Base SHAs used

The full per-repo base-SHA lists are regenerable from `data/interim` with the query
in *Selection rule* above. Counts: 107 + 140 + 180 = 427 distinct SHAs across 558 resolved instances, all 427 present in their clone.

The three highest-instance base SHAs per repo, as a spot-check anchor:

| Repo | Base SHA | Resolved instances at this SHA |
|---|---|---|
| `fla-org/flash-linear-attention` | `f1661afd8f87e0fc15e5e0c8b20d49c7f9d5ce10` | 9 |
| `fla-org/flash-linear-attention` | `a553ae440e274e5b1d705f074af76303ca576002` | 5 |
| `fla-org/flash-linear-attention` | `27fc450679e88401ac322e918308337d157be6d9` | 4 |
| `Stirling-Tools/Stirling-PDF` | `946c032fb55ae785d151dd26cced91ca3125aa43` | 5 |
| `Stirling-Tools/Stirling-PDF` | `4947ab12fd23017d477bf66d0c89ce2eb8fba1f0` | 4 |
| `Stirling-Tools/Stirling-PDF` | `5b433bab529a580a9d9544fef19dd2cfb450cd9c` | 4 |
| `spiculedata/saiku` | `f356353b8e2d0dafb63220933e809e632152d8a0` | 9 |
| `spiculedata/saiku` | `d4d54f70d0e61ae399e37d7bdbbf286bedf90392` | 4 |
| `spiculedata/saiku` | `0ae9f744f65b3edaa402f25ff9793db3bf995bda` | 3 |
