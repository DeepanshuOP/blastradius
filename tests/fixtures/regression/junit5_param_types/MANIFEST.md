# JUnit 5 parameter-type regression fixture

Real, unmodified GitHub Actions job logs. Checked in to pin the fix for the
`Path#<method>` class-attribution defect first observed in
`docs/session/prisha-085-graph-layer.md` §5 (11/20 of a sampled unbound Java key
space carried class name `Path`, which names no source symbol).

Neither job appears in `docs/session/holdout-exclusion.txt`, so neither is drawn
from any holdout worksheet, v1 through v5.

## The defect

Gradle prints a JUnit 5 test method with its declared parameter types:

```
UIDataTessdataControllerTest > downloadTessdataLanguages_allSuccess(Path) FAILED
```

`(Path)` is the type of a `@TempDir Path` argument. `src/parse/log_gradle.py`
emits `UIDataTessdataControllerTest#downloadTessdataLanguages_allSuccess(Path)`,
and `analysis/corpus_parse.py` then canonicalises that through
`src/parse/test_ids.py::normalize_test_id`. Inside `normalize_test_id`, section 5
Pattern A (the JUnit 4 Surefire form `testBar(com.example.FooTest)`, where the
parenthesised token *is* the declaring class) was tried before Pattern B (the
canonical `Class#method` form). Pattern A's `re.search` therefore matched the
parameter type and read it as the declaring class, returning
`Path#downloadTessdataLanguages_allSuccess` and discarding the real class.

The harm is not truncation. For `sirixdb/sirix` the discarded class was already
fully qualified, so a complete FQCN was replaced by `Path`.

Fix: Pattern B is tried first. It returns only when both halves validate, so any
non-match still falls through to Pattern A and the genuine JUnit 4 form is
unaffected.

## 1. Stirling-Tools__Stirling-PDF__085060314571.txt

- **Source repo:** `Stirling-Tools/Stirling-PDF`
- **Job ID:** `85060314571`
- **Raw capture:** `data/raw/Stirling-Tools__Stirling-PDF/job/571/085060314571/logs.jsonl.gz`
- **Build tool:** Gradle
- **Bytes / lines:** 670,702 / 3,400 (verbatim `body` of the capture record)
- **Affected lines:** 12

No `at` stack frame in this log carries a package for
`UIDataTessdataControllerTest` — the only reference is the bare source file name
`at UIDataTessdataControllerTest.java`. So per D-39 the package is NOT recovered
and NOT guessed: the canonical class stays the simple name and
`is_fqcn_qualified` is `False`.

Hand-derived expected canonical ids, read from the raw log text (12, all `fail`):

| # | Expected canonical `test_id` | Expected `params` |
|---|---|---|
| 1 | `UIDataTessdataControllerTest#downloadTessdataLanguages_allSuccess` | `(Path)` |
| 2 | `UIDataTessdataControllerTest#downloadTessdataLanguages_blocksPathTraversal` | `(Path)` |
| 3 | `UIDataTessdataControllerTest#downloadTessdataLanguages_handlesInvalidSanitizedLanguage` | `(Path)` |
| 4 | `UIDataTessdataControllerTest#downloadTessdataLanguages_handlesNetworkFailure` | `(Path)` |
| 5 | `UIDataTessdataControllerTest#downloadTessdataLanguages_rejectsUnknownLanguage` | `(Path)` |
| 6 | `UIDataTessdataControllerTest#downloadTessdataLanguages_returnsForbiddenWhenNotWritable` | `(Path)` |
| 7 | `UIDataTessdataControllerTest#downloadTessdataLanguages_successAndFailureMixed` | `(Path)` |
| 8 | `UIDataTessdataControllerTest#tessdataLanguages_emptyDirectory` | `(Path)` |
| 9 | `UIDataTessdataControllerTest#tessdataLanguages_handlesNonExistentDirectory` | `(Path)` |
| 10 | `UIDataTessdataControllerTest#tessdataLanguages_marksNotWritable` | `(Path)` |
| 11 | `UIDataTessdataControllerTest#tessdataLanguages_nonTraineddataFilesAreIgnored` | `(Path)` |
| 12 | `UIDataTessdataControllerTest#tessdataLanguages_returnsInstalledAvailableAndWritable` | `(Path)` |

Expected under the pre-fix parser, for the supersession record: all 12 as
`Path#<method>`, with `params` lost (`None`).

## 2. sirixdb/sirix job 86190264160 — NOT checked in

The second affected job is `sirixdb/sirix` job `86190264160`
(`data/raw/sirixdb__sirix/job/160/086190264160/logs.jsonl.gz`). Its body is
12,170,868 bytes / 90,461 lines, which exceeds the largest fixture in this repo
(8,781,529 bytes) by ~39%, for four affected lines. It is deliberately not
checked in, and no excerpt is checked in either, because truncating a Gradle log
changes what the parser sees (truncation detection, and the `at`-frame package
recovery that runs over the whole body).

Its four affected lines, verbatim with the ISO-8601 timestamp prefix stripped:

```
IndexListenerStaleTrxTest > perResourceIsolationAcrossOverlappingWriteTransactions(Path) FAILED
IndexListenerStaleTrxTest > casIndexListenerNotFiredOnLaterTransactionAfterFirstClosed(Path) FAILED
NamesReconstructionDifferentialTest > bitmapReconstructionEqualsScanWithHashCollisions(Path) FAILED
NamesReconstructionDifferentialTest > bitmapReconstructionEqualsScanUnderNameChurn(Path) FAILED
```

Unlike the Stirling-PDF log, this one *does* carry FQCN `at` frames, e.g.

```
at io.sirix.index.IndexListenerStaleTrxTest.perResourceIsolationAcrossOverlappingWriteTransactions(IndexListenerStaleTrxTest.java:76)
```

so it is the case where Pattern A destroyed an already-complete FQCN. That
property is asserted at unit level in `tests/test_test_ids_param_types.py`
against the canonical string, not against the log body.
