# Project Evidence and Provenance

## Goal

Ground the paper in the user's real project rather than in assumptions made by the writing assistant.

## Evidence Inventory

Before writing technical claims, identify:

1. Project objective and task definition.
2. System/pipeline implementation.
3. Datasets and splits.
4. Baselines and their implementations or cited numbers.
5. Experimental configurations.
6. Raw metrics and result files.
7. Figures, plots, tables, screenshots, and qualitative examples.
8. Known failure cases and limitations.
9. Existing manuscript/draft text.

## Provenance Labels

Mark important facts as:

- `author-provided`: directly supplied by the author.
- `experiment-derived`: produced by an actual run or result artifact.
- `literature-derived`: supported by a cited publication or authoritative source.
- `inference`: a reasoned interpretation, not a measured fact.

Do not silently turn an inference into experiment-derived evidence.

## Claim Ledger

Use this structure during drafting:

| Claim | Evidence | Provenance | Scope | Status |
|---|---|---|---|---|
| [claim] | [table/figure/run/citation] | [label] | [dataset/setting] | supported / needs evidence / etc. |

## Result Integrity

- Never invent a number.
- Never round a value differently just to make a gain look larger.
- Keep metric direction and units clear.
- Distinguish reproduced numbers from numbers copied from the literature.
- Distinguish a single run from an aggregate result.
- Record the experimental setting next to each important result.

## Baseline Integrity

When comparing against a baseline, verify as much as the project evidence allows:

1. Dataset and split.
2. Preprocessing.
3. Evaluation metric and implementation.
4. Training/evaluation conditions.
5. Whether the number is reproduced or taken from the paper.

Do not present literature numbers as directly comparable when the protocols differ materially.

## Novelty Discipline

A writing assistant may help articulate novelty, but it must not manufacture it. A novelty statement must be traceable to the actual method, task, evaluation, or finding.
