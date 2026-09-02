# Phase 021C — Break the Row-Number Anchor (2 files modified, 1 created)

**Scope**: Modified `docs/phase/021B-blind-worksheet.md` and `analysis/expectation_diff.py`.
Created this report. Nothing under `src/` touched, no parser fixed, `docs/SCHEMAS.md`,
`docs/DECISIONS.md`, `docs/phase/021-expectation-table.md`, and
`docs/phase/012B-holdout-v4-worksheet.md` not edited, no `HAND_EXPECTED` value filled, not
wired into `make tables`, no HTTP, nothing backgrounded.

## PHASE 1 — Stable join key

`row_key` = first 12 hex chars of `sha256(fixture + "\n" + raw evidence lines joined by
"\n")`, computed over the **raw bytes**, not the `repr()` display transform used to render
`RAW_LINE` — per predicted failure (b), which is CONFIRMED as a real risk and avoided: had
the repr() text been hashed instead, the row_key would depend on a formatting choice
(quote style, escape rendering) rather than the actual log bytes.

**Distinct row_keys: 47 / 47. No collisions.**

**Predicted failure (a) — FALSIFIED, checked directly, not assumed.** Rows 18 and 19 are
indeed the same test id (`RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate`)
in two different Flink fixtures. Fixture name is part of the hash, so they don't collide
regardless. I additionally recomputed both keys with the fixture name *removed* from the
hash input to test whether the hypothesis's underlying premise holds: they still don't
collide (`0957c5ddc7c7` vs `c5abf07a26d4`), because the two source lines differ in their
embedded timestamp (`2026-05-27T04:04:44...` vs `2026-06-04T04:09:23...` — different CI
runs). The raw evidence text itself is unique per row in this corpus even before the
fixture name is folded in; fixture name is still included per spec, and is the right
defensive choice for a corpus where that might not always hold.

## PHASE 2 — Re-keyed, shuffled worksheet

`docs/phase/021B-blind-worksheet.md` rewritten: 47 sections headed `## Row <row_key> —
<fixture>`, `row_key` being the sha256-derived key above (not a sequential number — grepped
the file to confirm no `Row [0-9]{1,2} —` sequential-number heading survives). Order shuffled
with `random.Random(20260902).shuffle()` over the original 47-row list. Content per section
unchanged from the prior version: fixture, verbatim `RAW_LINE` evidence (fenced, `repr()`
display transform disclosed in the header, neutral "evidence line 1 / evidence line 2"
labels), empty `HAND_EXPECTED`. The `KNOWN LIMITATION` text was added verbatim as specified,
confirmed by direct diff against the given string.

## PHASE 3 — Leak-proof join script

`analysis/expectation_diff.py` rewritten. Both sides now derive `row_key` independently:
the worksheet side recomputes it from each section's own displayed evidence (un-`repr()`'d
via `ast.literal_eval`, not eval'd/executed) and **raises** if that recomputed key disagrees
with the section's own header — a stored value is never trusted, an inconsistent one is
treated as corruption rather than silently accepted. The expectation-table side recomputes
`row_key` from each table row's `RAW_LINE` cell the same way; the table has no `row_key`
column to (mis)trust in the first place.

For any row with an empty `HAND_EXPECTED`, the code path that prints it never reads,
formats, or interpolates `NORMALIZED` — verified structurally (separate branch, separate
f-string, `normalized` is not even looked up before that branch returns) and empirically
(`grep -c NORMALIZED` on the run below is `0`). `CONTESTED` is attached only to filled
(AGREE/DISAGREE) rows, per the literal "print ONLY row_key, fixture, verdict=UNFILLED" for
unfilled ones — a `CONTESTED` marker on an unfilled row would itself be a partial leak
(a hint that the answer is bare-class-shaped, generic-method-shaped, or `NONE`), so it's
withheld there too, even though the task's rule 7 names only `NORMALIZED` explicitly.

One bug surfaced before the final run: the worksheet's fenced `RAW_LINE` blocks carry no
`L\d+:` line-number prefix (only the expectation table's inline cells do), so the single
regex reused from the prior script matched zero evidence lines inside worksheet sections,
producing an empty-string hash that didn't match any section's own header — caught
immediately by the new mismatch check raising `ValueError` on the very first row, rather
than silently joining wrong. Fixed by adding a second, fenced-block-based extractor for the
worksheet side and keeping the `L\d+:`-anchored one for the table side.

Verified end-to-end against a synthetic 4-row fixture pair (AGREE/DISAGREE/UNFILLED/
AGREE-CONTESTED, isolated in a temp directory, not touching the real files) before the
run below.

Raw output of `python3 analysis/expectation_diff.py` against the currently-unfilled,
re-keyed worksheet, pasted in full:

```
row_key=015d3b2416a0 fixture=dask__distributed__084757793457.txt verdict=UNFILLED
row_key=068f9bb711d8 fixture=unicode-org__cldr__090672967305.txt verdict=UNFILLED
row_key=0b1dcde22361 fixture=apache__dolphinscheduler__092883042571.txt verdict=UNFILLED
row_key=0e5d3a59b174 fixture=robo-code__robocode__084332182805.txt verdict=UNFILLED
row_key=185149df8b18 fixture=apache__zeppelin__077616025677.txt verdict=UNFILLED
row_key=1b4f2d40df89 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt verdict=UNFILLED
row_key=2598cf91f544 fixture=sirixdb__sirix__092352347826.txt verdict=UNFILLED
row_key=2724bcfc3dff fixture=nats-io__nats.java__080900237539.txt verdict=UNFILLED
row_key=2bec1480577b fixture=apache__hugegraph__084221602296.txt verdict=UNFILLED
row_key=3269f76d726f fixture=sirixdb__sirix__080642754882.txt verdict=UNFILLED
row_key=36ea4df7a8e6 fixture=apache__flink__079445374425.txt verdict=UNFILLED
row_key=3f74c8efd8d5 fixture=apache__hugegraph__086386091934.txt verdict=UNFILLED
row_key=4ca072d0ebcf fixture=gurkenlabs__litiengine__079152380933.txt verdict=UNFILLED
row_key=4d25554936d1 fixture=dask__distributed__084645769341.txt verdict=UNFILLED
row_key=51208f55ec56 fixture=apache__beam__086101982024.txt verdict=UNFILLED
row_key=561a20998890 fixture=apache__hugegraph__086386091934.txt verdict=UNFILLED
row_key=57e11a35966e fixture=apache__hugegraph__084221602296.txt verdict=UNFILLED
row_key=5ce7156d4c23 fixture=apache__atlas__085339439869.txt verdict=UNFILLED
row_key=63351e37b366 fixture=sirixdb__sirix__080642754882.txt verdict=UNFILLED
row_key=6a5fd9d35a1f fixture=apache__beam__086101982024.txt verdict=UNFILLED
row_key=6d271ffe6080 fixture=Stirling-Tools__Stirling-PDF__081016081705.txt verdict=UNFILLED
row_key=6e0955e465d6 fixture=apache__hugegraph__086386091934.txt verdict=UNFILLED
row_key=7a18936bd0b6 fixture=webauthn4j__webauthn4j__080348707704.txt verdict=UNFILLED
row_key=7a69e71e197c fixture=apache__hugegraph__086386091934.txt verdict=UNFILLED
row_key=80b12bf4ef69 fixture=apache__beam__093527298308.txt verdict=UNFILLED
row_key=819c2f5d708c fixture=webauthn4j__webauthn4j__080348707704.txt verdict=UNFILLED
row_key=83a64a4e66bd fixture=Stirling-Tools__Stirling-PDF__081185748047.txt verdict=UNFILLED
row_key=8aabd9035ed4 fixture=apache__beam__093527298308.txt verdict=UNFILLED
row_key=906fd9b5040d fixture=floci-io__floci__085018489189.txt verdict=UNFILLED
row_key=9ad2fff53c74 fixture=sirixdb__sirix__092352347826.txt verdict=UNFILLED
row_key=9be730822015 fixture=gurkenlabs__litiengine__079152380933.txt verdict=UNFILLED
row_key=9e4d4bd8e591 fixture=apache__beam__086101982024.txt verdict=UNFILLED
row_key=a235cadb12ea fixture=agno-agi__agno__079305370965.txt verdict=UNFILLED
row_key=b0980797f104 fixture=fla-org__flash-linear-attention__082566635619.txt verdict=UNFILLED
row_key=b9184834c4c8 fixture=nats-io__nats.java__080900237539.txt verdict=UNFILLED
row_key=bc6fb538ad06 fixture=agno-agi__agno__092042274925.txt verdict=UNFILLED
row_key=bee7e94431f6 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt verdict=UNFILLED
row_key=bfce04c42964 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt verdict=UNFILLED
row_key=cff48077c013 fixture=apache__flink__078003756269.txt verdict=UNFILLED
row_key=d2acfc050586 fixture=apache__beam__093527298308.txt verdict=UNFILLED
row_key=d6556fd08827 fixture=sirixdb__sirix__080642754882.txt verdict=UNFILLED
row_key=da93371bad8a fixture=linkedin__brooklin__077863844421.txt verdict=UNFILLED
row_key=dd21bdcdf521 fixture=sirixdb__sirix__080642754882.txt verdict=UNFILLED
row_key=e2d48d930cf9 fixture=agno-agi__agno__079305370965.txt verdict=UNFILLED
row_key=f433234b4233 fixture=fla-org__flash-linear-attention__086098926451.txt verdict=UNFILLED
row_key=f74f48f3de5e fixture=apache__hugegraph__086386091934.txt verdict=UNFILLED
row_key=ff36ea9d0dbe fixture=apache__beam__093527298308.txt verdict=UNFILLED

UNFILLED: 47 / 47
AGREE:    0 / 47
DISAGREE: 0 / 47
AGREE-ON-CONTESTED: 0 / 47
```

Exit code: 0. `grep -c NORMALIZED` on this output: `0`.

## My own predicted failure

**(c) The row_key is still deterministic and reproducible by the operator.** Re-keying and
shuffling remove the *sequential* anchor the operator already saw, but nothing stops the
operator from re-running `analysis/expectation_diff.py` (or hashing a fixture+line by hand)
against the unfilled worksheet again before finishing the fill and reconstructing the same
row_key → fixture mapping they already partially memorized from the incident that triggered
this task. Re-keying defeats position-based anchoring, not content-based recall of what was
already read. This is inherent to any deterministic key and is exactly why the header states
plainly that this corpus is FITTED, not blind, rather than claiming the re-key restores
blindness.

**Nothing else was changed. Nothing was committed.**
