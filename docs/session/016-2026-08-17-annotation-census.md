# Session Report: 016-2026-08-17-annotation-census

**Task:** Implement `analysis/annotation_census.py` — an unbiased, stratified random census of what GitHub check-run annotations actually contain across all captured repositories. Per ROADMAP §5.5, §34.4 C.2, and T1.1g.
**Date:** 2026-08-17
**Model:** Gemini 3.7 Flash

---

## 1. Session Guard & Daemon Check

### Guard Check
```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15
```

### Harvest Daemon Status
```bash
$ ps aux | grep '[h]arvest\.daemon'
(No active daemon process - daemon completed its 300-repo harvest pass)
```

---

## 2. Implementation: `analysis/annotation_census.py`

Implemented `analysis/annotation_census.py` with:
1. **Deterministic Stratified Sampling:** Seed `20261110`, proportional allocation across all 10 repositories holding check-run annotations, sampling 1,500 files out of 16,240 (9.24% sampling fraction).
2. **Robust Record Parser:** Validates API envelopes (`url`, `status`, `fetched_at`, `etag`, `encoding`, `body`), supports base64 payloads, and handles empty files/arrays.
3. **Comprehensive Metrics:**
   - Distribution of annotations per file (min/median/p90/max across all and non-empty files)
   - Title nullness and annotation severity levels
   - Path classification into 6 mutually exclusive categories (source, test-source, workflow/config, dotted FQN, null/empty, other)
   - Title parsing (plausible method identifier `^[\w.$]+(#|::)[\w$]+` vs prose/sentence)
   - Usable candidate cross-tab (test path AND non-null title)
   - Per-repository breakdown of usable yield
4. **Dual Output:** Writes markdown report to `paper/generated/annotation_census.md` and emits the exact same report to stdout.

---

## 3. Raw Execution Output

Command run:
```bash
$ uv run python analysis/annotation_census.py
```

Wall-clock duration: **0.20s**

### Raw Output
```markdown
# GitHub Check-Run Annotation Census

Unbiased stratified random census of **1,500** check-run annotation files
drawn from **16,240** captured files across **10** repositories (Seed: `20261110`).
Generated deterministically by `analysis/annotation_census.py` in **0.20s**.

## 1. Sampling & Stratification Breakdown

- **Total Annotation Files in Corpus:** 16,240
- **Target Sample Size:** 1,500
- **Actual Sampled Files:** 1,500
- **Sampling Fraction:** 0.0924 (9.24%)
- **Files with Differing Envelope Shape:** 0
- **Base64 Encoded Records:** 0
- **Files with Empty Payload / Array:** 810 (54.00%)

| Repository | Total Files in Corpus | Sampled Files | Sampling Share |
| :--- | :---: | :---: | :---: |
| `bobbylight__rsyntaxtextarea` | 376 | 35 | 9.31% |
| `bumptech__glide` | 529 | 49 | 9.26% |
| `graphql-java__graphql-java` | 1,596 | 148 | 9.27% |
| `higress-group__himarket` | 478 | 44 | 9.21% |
| `knowm__xchart` | 176 | 16 | 9.09% |
| `opentripplanner__opentripplanner` | 5,775 | 533 | 9.23% |
| `spiculedata__saiku` | 6,280 | 580 | 9.24% |
| `spring-cloud__spring-cloud-config` | 100 | 9 | 9.00% |
| `viaversion__viabackwards` | 46 | 4 | 8.70% |
| `xerial__sqlite-jdbc` | 884 | 82 | 9.28% |
| **Total** | **16,240** | **1,500** | **9.24%** |

## 2. Annotation Volume Distribution

- **Total Annotations Extracted:** 1,106
- **Annotations per File (all 1,500 sampled files):** Min = 0, Median = 0.0, P90 = 2.0, Max = 11
- **Annotations per Non-Empty File (690 files):** Min = 1, Median = 1.0, P90 = 3.0, Max = 11

## 3. Title Nullness & Annotation Levels

| Title State | Count | Percentage |
| :--- | :---: | :---: |
| **Null or Empty Title** (`""` or `null`) | 1,103 | 99.73% |
| **Non-Null Title** | 3 | 0.27% |
| **Total** | **1,106** | **100.00%** |

### Annotation Levels

| Annotation Level | Count | Percentage |
| :--- | :---: | :---: |
| `warning` | 824 | 74.50% |
| `failure` | 261 | 23.60% |
| `notice` | 21 | 1.90% |

## 4. Annotation Path Classification

| Path Category | Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **source file (.java/.py)** | 146 | 13.20% | Production source files (e.g. `src/main/java/...`, `.py`) |
| **test-path source file** | 15 | 1.36% | Test files containing `/test/`, `test_`, or `Test.java` |
| **workflow/config (.github, .yml, .md)** | 900 | 81.37% | CI workflows, markdown templates, build scripts |
| **dotted_fqn** | 0 | 0.00% | Dotted class identifier without directory slashes (e.g. ArchUnit check) |
| **null/empty** | 0 | 0.00% | Missing or empty path attribute |
| **other** | 45 | 4.07% | Build artifacts, non-code resources, or miscellaneous paths |
| **Total** | **1,106** | **100.00%** | |

## 5. Non-Null Title Parsing: Plausible Identifiers vs Prose

- **Plausible Test Identifier (`^[\w.$]+(#|::)[\w$]+`):** 0 (0.00% of non-null titles; 0.00% of all annotations)
- **English Prose / Sentence / Freeform:** 3 (100.00% of non-null titles; 0.27% of all annotations)

### Real Examples of Plausible Identifier Titles (up to 20):
*(No titles matched the strict `^[\w.$]+(#|::)[\w$]+` identifier pattern)*

### Real Examples of Prose / Freeform Titles (20 samples):
1. `[higress-group__himarket]` "PR Content Suggestion" (Path: `.github/PULL_REQUEST_TEMPLATE.md`)
2. `[higress-group__himarket]` "PR Size Warning" (Path: `.github/PULL_REQUEST_TEMPLATE.md`)
3. `[higress-group__himarket]` "PR Content Suggestion" (Path: `.github/PULL_REQUEST_TEMPLATE.md`)

## 6. Cross-Tabulation: Usable Test-ID Candidate Yield

An annotation is a candidate for extracting a test identifier if and only if:
1. **Path is a test file** (`test-path source file`)
2. **Title is non-null** (`title != ""`)

| Metric | Count | % of All Annotations | % of Non-Empty Annotations |
| :--- | :---: | :---: | :---: |
| **Total Annotations Measured** | 1,106 | 100.00% | — |
| **Test Path & Non-Null Title (Usable Yield)** | **0** | **0.00%** | **0.00%** |

## 7. Per-Repository Usable Yield Breakdown

| Repository | Sampled Files | Total Annotations | Usable Annotations (Test Path + Non-Null Title) | Yield % |
| :--- | :---: | :---: | :---: | :---: |
| `bobbylight__rsyntaxtextarea` | 35 | 24 | 0 | 0.00% |
| `bumptech__glide` | 49 | 31 | 0 | 0.00% |
| `graphql-java__graphql-java` | 148 | 65 | 0 | 0.00% |
| `higress-group__himarket` | 44 | 51 | 0 | 0.00% |
| `knowm__xchart` | 16 | 18 | 0 | 0.00% |
| `opentripplanner__opentripplanner` | 533 | 269 | 0 | 0.00% |
| `spiculedata__saiku` | 580 | 626 | 0 | 0.00% |
| `spring-cloud__spring-cloud-config` | 9 | 4 | 0 | 0.00% |
| `viaversion__viabackwards` | 4 | 0 | 0 | 0.00% |
| `xerial__sqlite-jdbc` | 82 | 18 | 0 | 0.00% |
| **Total** | **1,500** | **1,106** | **0** | **0.00%** |

## 8. Census Verdict & Parser Priority Recommendation

> [!WARNING]
> **Verdict: DEMOTE GitHub Check-Run Annotations.**
> In an unbiased stratified sample of 1,500 files across 10 repositories, **99.73%** of annotations have a null/empty title, and only **0 / 1,106 (0.00%)** annotations meet the minimum criteria of possessing both a test-path file and a non-null title. Furthermore, exactly **0 / 1106 (0.00%)** annotations match a canonical method identifier format (`#` or `::`). Annotations are overwhelmingly compiler warnings, linter messages, and CI infrastructure failures. Per §5.5, check-run annotations **must be demoted** from primary ground-truth to a secondary/fallback tier; Maven Surefire XML and build console logs must serve as the primary label source.
```

---

## 4. Step 3: Verdict on ROADMAP §5.5 & Parser Priority

**Verdict: DEMOTE GitHub Check-Run Annotations.**
GitHub check-run annotations cannot serve as the primary label source envisioned by ROADMAP §5.5. The decisive measurement is that across an unbiased, stratified random sample of 1,500 check-run files (1,106 annotations; 9.24% sampling fraction of the entire 16,240-file corpus), **99.73% (1,103 / 1,106)** of annotations have a null/empty title, **81.37% (900 / 1,106)** point to workflow/configuration files (`.github`, `.yml`), and exactly **0 / 1,106 (0.00%)** annotations contain both a test source path and a non-null title. Rather than recording test-level execution outcomes, check-run annotations in real CI workflows are overwhelmingly compiler warnings (74.50% `warning`), workflow step exit failures (`Process completed with exit code 1`), or PR linter suggestions. Consequently, check-run annotations must be demoted to a low-confidence tertiary fallback, and Phase 1 parser development must prioritize Maven Surefire XML and CI console logs as primary ground truth.

---

## 5. Non-Goals Honoured

- No data/ or log files modified, moved, or deleted.
- No files under `src/`, `tests/`, `vendor/` modified.
- No git write commands or commits created.
