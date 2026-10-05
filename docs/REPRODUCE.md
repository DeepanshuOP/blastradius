# Reproducing BlastRadius

This document covers the two reproductions that run on a laptop: the full test
suite plus the bounded graph-layer mini-corpus (`make all`), and the figure
regeneration (`make tables`). Both are measured, not estimated — every number
below was produced by the run recorded in
`docs/session/prisha-087-impl-report.md`.

Scope note (D-48): the mini-corpus reproduction exercises the **graph layer
only**. Nothing it prints reaches `make tables`, `release/` or the paper, and
the binding figure it reports is the graph-side `graph_node_binding_rate`
diagnostic. It is **not** Gate 1.5 and is not comparable with D-47's figure —
the denominators differ.

## 1. Prerequisites

| Requirement | Value |
|---|---|
| OS | WSL2 Ubuntu (not PowerShell) |
| Python | 3.11, via `uv` |
| Extras | `uv sync --extra graph` (the reproduce target needs it) |
| Clones | the three mini-corpus repos under `data/clones/` (§3) |
| Interim data | `data/interim/base_resolution.parquet`, `data/interim/parsed_outcomes.parquet` |
| Network | **none**. No GitHub HTTP, no PAT, no LLM call (D-17) |
| Disk | ~2 GB transient for `data/graphs_reproduce/`, removed on exit |

`make all` needs no credentials. `make tables` needs none either: its one
PAT-gated step (`analysis/fetch_base_logs.py`) is skipped loudly when no
`GITHUB_PAT_1/_2/_3` is in the environment, because the corpus is pinned
(`data/interim/CORPUS_PIN.json`) and the base side is fixed at the local
`RawStore` (D-49). `tests/test_makefile_pat_gate.py` holds that gate honest: it
asserts the fetch is *skipped*, never removed, and that any single key
`TokenPool` accepts is enough to run it.

## 2. The commands

```bash
uv sync --extra graph
make all                 # pytest + the mini-corpus reproduction
make tables              # regenerates every number that reaches the paper
uv run --extra graph python analysis/reproduce_mini_corpus.py --help
```

`make all` is `test` then `reproduce`. To run only the reproduction:

```bash
uv run --extra graph python analysis/reproduce_mini_corpus.py
```

Useful flags: `--shas-per-repo N` (default 3), `--instances N` (timed queries
per graph, default 50), `--out-dir DIR` (default `data/graphs_reproduce`, a
fresh dir so builds are genuinely **cold**; pass `--out-dir data/graphs` to
measure the warm path instead), `--keep` to retain the output, `--seed`
(default 42).

## 3. The mini-corpus

Three repos, as `docs/MINI_CORPUS.md` selects them:

| Repo | Clone directory |
|---|---|
| `fla-org/flash-linear-attention` | `data/clones/fla-org__flash-linear-attention` |
| `Stirling-Tools/Stirling-PDF` | `data/clones/Stirling-Tools__Stirling-PDF` |
| `spiculedata/saiku` | `data/clones/spiculedata__saiku` |

SHA selection is deterministic: the newest resolved base SHAs per repo from
`base_resolution.parquet`, restricted to `exact` / `exact_green` / `ancestor`
rows with a non-null `base_sha`, ordered by `max(run_id)` descending then by
`base_sha`. Two calls therefore agree, so a reported figure names a
reproducible SHA set.

### Why this is bounded, not a full rebuild

`data/graphs/` holds 427 graphs. A cold rebuild of all of them cannot fit a
15-minute budget on a laptop, so the target reproduces the full
build → bind → query chain over 3 SHAs per repo (9 graphs) and prints the
subset size alongside every figure.

## 4. Measured output

Measured on the development laptop (WSL2, 22 workers available to the
Graphify AST pass), cold `--out-dir`, 2026-10-04:

```
make all          : exit 0,  13:59.96 wall  (839.96 s)  — under the 15-minute target
  pytest          : 632 passed, 12 skipped in 338.88 s
  reproduce       : 514.68 s of the 900 s budget        — T5.6b MET
```

Per repo:

| Repo | SHAs | Nodes (range) | Edges (range) | Build/graph | Binding (best of 3) | Query warm median |
|---|---:|---:|---:|---:|---:|---:|
| `fla-org/flash-linear-attention` | 3 | 7,559–7,581 | 21,317–21,382 | 16.0–16.9 s | 35/37 | 55.1 ms ✅ |
| `Stirling-Tools/Stirling-PDF` | 3 | 29,582–30,278 | 161,402–163,333 | 63.3–63.9 s | 285/307 | 376.8 ms ❌ |
| `spiculedata/saiku` | 3 | 10,221–10,337 | 46,396–47,122 | 18.3–21.0 s | 18/20 | 3,039.6 ms ❌ |

Totals: 9 graphs built, build 297.96 s, bind 0.53 s, query 193.99 s.

### Reading these numbers honestly

- **The 15-minute budget is MET**, with the reproduction itself at 514.68 s of
  900 s. `make all` as a whole is 839.96 s because it runs the full test suite
  first; the T5.6b budget governs the reproduction, and both land inside
  fifteen minutes on this machine.
- **The ROADMAP §19.4 ≤100 ms per-instance query budget is MET on one repo of
  three and MISSED on two.** Stirling-PDF's warm median is 376.8 ms and
  saiku's is 3,039.6 ms — 30× over. This is reported, not hidden, and the
  reproduction deliberately **does not fail** on it: the figure measures
  whichever laptop is running, and §19.4's budget is a target for ours, not a
  property of the code. It is a real finding about query cost scaling with
  graph size and is owed a §VI limitation entry or an optimisation task.
- Cold and warm per-instance times are timed **separately**. The first instance
  at a SHA pays for the cold cache; averaging it into the rest would hide both
  figures.
- The binding figures are per-repo bests over 3 graphs, on denominators of
  observed `test_id`s for that repo (37, 307, 20). They are a graph-side
  diagnostic only — see the scope note at the top.
- The budget verdict cannot pass vacuously. With the clones absent every repo
  is skipped, wall time is a fraction of a second, and a naive
  `total < budget` check would print MET having reproduced nothing. Building
  zero graphs is a hard error (exit 1), covered by
  `tests/test_reproduce_mini_corpus.py`.

## 5. What `make tables` regenerates

Every number that reaches the paper (CLAUDE.md rule 4). It refuses to run at
all if any interim artifact is older than an input it derives from — the D-49
guard, `analysis/check_freshness.py`, placed first because a gate behind a step
that can fail is not a gate. `analysis/secret_scan.py` runs second for the same
reason. On-disk output lands in `paper/generated/` (gitignored).

Current state, regenerated 2026-10-04 from the pinned corpus:

```
[freshness] OK: 2 artifacts checked against their inputs under data/interim
```

## 6. Determinism

Seeds are pinned (`--seed`, default 42; the annotation census uses `20261110`).
No LLM call occurs anywhere in the pipeline (D-17). The corpus is pinned by
`data/interim/CORPUS_PIN.json`.

Two caveats worth stating about `analysis/binding_report.py`:

- It used to scope itself to whatever repos happened to be in `data/clones/`,
  making its row count a property of the machine. It now **refuses to run**
  unless all 43 corpus repos are cloned, naming the missing ones
  (`require_complete_clones`). `make tables` therefore needs the full clone set;
  see `docs/session/prisha-087-impl-report.md` §9.
- It resolves against each clone's `HEAD`, **not** against a pinned corpus SHA,
  so the figure still drifts with how fresh the clones are. That is a real
  reproducibility gap and is recorded in `docs/DATASHEET.md`.
