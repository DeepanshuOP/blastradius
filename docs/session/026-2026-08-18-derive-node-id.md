# Session Report: 026-2026-08-18-derive-node-id

**Date:** 2026-08-18 (Session timestamp: 2026-08-17T19:30Z)  
**Task ID:** D-25 / derive_node_id  
**Model:** Gemini 3.7 Flash  
**Topic:** Implement `derive_node_id()` in `src/parse/test_ids.py` per Decision D-25  

---

## 1. Task Statement
Implement `derive_node_id(test_id: str) -> str` in `src/parse/test_ids.py` per Decision D-25. Reimplement Graphify's normalization recipe (NFKC, casefold, NFKC, `[^\w]+` -> `_`, collapse `_+`, strip `_`) without importing from `vendor/`, documenting the lossy many-to-one property. Add contract unit tests in `tests/test_test_ids.py` verifying Java/Python derivations, idempotency, intentional collisions, and round-trips from normalized `TestId.canonical`.

---

## 2. Commands Run and Verbatim Output

### Guard Check
```bash
uname -s && pwd && uv run python --version && ps aux | grep '[h]arvest\.daemon' && ls data/raw | wc -l
```
```
Linux
/home/shree/blastradius
Python 3.11.15
shree      14013  0.0  0.4 219368 32896 ?        Ssl  14:39   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree      14016  1.1  1.1  98584 90836 ?        S    14:39   3:25 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
35
```

### Test Suite Execution (Prediction vs Actual)
- **Predicted:** 202 passed (193 baseline + 9 new test items in `tests/test_test_ids.py`: 1 Java canonical + 1 Python canonical + 5 parameterized idempotency + 1 intentional collision + 1 XML round-trip).
- **Command:**
```bash
uv run pytest -q
```
- **Output:**
```
........................................................................ [ 35%]
........................................................................ [ 71%]
..........................................................               [100%]
202 passed in 4.11s
```
- **Actual:** 202 passed in 4.11s (0 warnings, 0 failures).

---

## 3. Files Changed and Line Counts
- `src/parse/test_ids.py`: +37 lines (added `derive_node_id` and updated `__all__`)
- `tests/test_test_ids.py`: +60 lines (added 5 test functions covering all required scenarios)
- `docs/session/INDEX.md`: +1 line (registered session 026)
- `docs/HANDOFF.md`: +1 line (logged session 026 entry)
- `docs/session/026-2026-08-18-derive-node-id.md`: created session report

---

## 4. Test Count Before and After
- **Before:** Predicted 193, Actual 193 passed.
- **After:** Predicted 202, Actual 202 passed.

---

## 5. Non-Goals Honoured
- Did NOT import anything from `vendor/graphify-br`.
- Did NOT modify `normalize_test_id()` or `TestId`.
- Did NOT touch `src/harvest/`, `analysis/`, `dashboard.py`, or `vendor/`.
- Did NOT write to `data/` or `logs/`.
- Did NOT commit.

---

## 6. Contradictions & Predicted Failures Analysis
1. *Hypothesis 1 (Python path dot to underscore):* Verified `tests/test_foo.py::TestFoo::test_bar` hand-derivation correctly produces `tests_test_foo_py_testfoo_test_bar` (`.py` becomes `_py_`, double colons `::` collapse to `_`).
2. *Hypothesis 2 (Unicode & non-word regex):* `[^\w]+` with `flags=re.UNICODE` correctly preserves alphanumeric characters across unicode scripts while replacing punctuation cleanly.
3. *Hypothesis 3 (Graphify make_id per-part stripping vs unified string):* Confirmed that because `derive_node_id` takes a single unified `test_id` string, applying `normalize_id` across the whole string is the exact correct model without per-token stripping.
4. *Extra finding (Docstring escape sequence):* Added `r"""` raw docstring prefix to prevent Python 3.12+ `DeprecationWarning: invalid escape sequence '\w'`.

---

## 7. Open Questions
None.
