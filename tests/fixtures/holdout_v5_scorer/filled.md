# Hand-filled two-section worksheet (test fixture)

Written by hand for `tests/test_score_holdout_v5.py`. The two sections name
real fixtures from `tests/fixtures/holdout_v5/`. Values here are illustrative
test input, NOT ground truth for the real corpus, and this file is never scored
by `analysis/score_holdout_v5.py` against the real seal path.

---

## 1. `Stirling-Tools__Stirling-PDF__089792061823.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/Stirling-Tools__Stirling-PDF__089792061823.txt`

### Answers (fill every field; leave nothing blank)

- **Build Tool:** gradle
- **Expected Class:** TEST_FAILURE
- **Expected Identifier Count:** 2
- **Expected Identifiers:** com.example.AlphaTest#one, com.example.BetaTest#two
- **Confidence:** CERTAIN

---

## 2. `Stirling-Tools__Stirling-PDF__092039331010.txt`

- **Fixture path**: `tests/fixtures/holdout_v5/Stirling-Tools__Stirling-PDF__092039331010.txt`

### Answers (fill every field; leave nothing blank)

- **Build Tool:** maven
- **Expected Class:** NO_TEST_OUTPUT
- **Expected Identifier Count:** 0
- **Expected Identifiers:** NO_TEST_OUTCOMES
- **Confidence:** CERTAIN

---
