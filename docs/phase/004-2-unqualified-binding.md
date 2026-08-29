# Phase 2: Bind Unqualified Identifiers by File Index

## 2a. Per-Repo Index of Test-File Basenames
Building a baseline index of test file basenames shows that bare class name lookup is viable, as the ambiguity rate is very low for most repositories.

| Repo | Distinct Test Basenames | Ambiguous (Appears >1) |
|---|---|---|
| Stirling-Tools/Stirling-PDF | 939 | 11 |
| apache/atlas | 504 | 3 |
| apache/beam | 3161 | 122 |
| apache/dolphinscheduler | 581 | 16 |
| apache/fineract | 1349 | 14 |
| apache/tika | 708 | 47 |
| baomidou/mybatis-plus | 371 | 53 |
| castorini/anserini | 217 | 0 |
| dask/distributed | 152 | 7 |
| diffplug/spotless | 249 | 12 |
| floci-io/floci | 1240 | 2 |
| sirixdb/sirix | 888 | 21 |

## 2b & 2c. Extending `resolve_test_file`
We extended `src/parse/test_files.py` to match bare class names directly against filenames within the tree (e.g., `FeignExceptionTest` -> `FeignExceptionTest.java`).
- Nested classes like `Outer$Inner` are successfully extracted as `Outer` for file-level mapping.
- Exact matches yield `status="exact"` with a lowered confidence of `0.5` (since package validation is absent).
- If multiple candidates exist, `status="ambiguous"` is returned and no guess is made.

## 2d. Tests
Tests were updated and passed against real partial clones using `git ls-tree`.
- **Count predicted:** 358
- **Count actual:** 358 (0 failed)
