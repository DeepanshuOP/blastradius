# Session Report: 018-2026-08-17-d24-annotation-demotion

**Task:** Formulate and record Decision D-24 in `docs/DECISIONS.md` demoting check-run annotations from primary to fallback label source following empirical findings from `analysis/annotation_census.py`.
**Date:** 2026-08-17
**Model:** Gemini 3.7 Flash

---

## 1. Session Guard & Process Check

```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15
```

---

## 2. Background & Decision Formulation

Per ROADMAP §5.5, check-run annotations were initially assumed to be the highest-confidence structured label source. However, empirical census in `analysis/annotation_census.py` across 1,500 stratified random check-run files (seed 20261110) revealed:
- 99.73% (1,103 / 1,106) null or empty titles.
- 81.37% (900 / 1,106) paths pointing to workflow/config files (`.github`, `.yml`, `.md`).
- 0 / 1,106 annotations containing both a test path and a non-null title.
- 0 / 1,106 titles matching a canonical method identifier (`#` or `::`).

Per ROADMAP §7, changing the label source tier ordering is an architectural decision requiring an entry in `docs/DECISIONS.md`.

---

## 3. Decision Record D-24

Added to `docs/DECISIONS.md`:

- **#:** `D-24`
- **Decision:** Check-run annotation source tier
- **In Force:** Demote check-run annotations from primary to a low-confidence fallback label source; job logs and JUnit/Surefire XML artifacts become primary.
- **Measured Basis:** 1,500 files sampled (9.24% fraction), 1,106 annotations extracted, 810 empty array files (54.00%), 1,103 null titles (99.73%), 0 test-path + non-null title yield. Explicit limits noted: 10 of 32 repos held annotations, saiku contributed 56.6%, all 32 repos Java.
- **Consequences:** T0.3e (job log orchestrator) and T0.3d (artifact capture) become strictly blocking for Phase 1; parser priority shifts to JUnit XML and log parsers. Directly reinforces D-23.
- **Door:** Two-way.
- **Revisit When:** Python repos harvested or test-reporting actions demonstrate ≥10% test-path + non-null title yield.

---

## 4. Non-Goals Honoured

- No existing decision rows modified.
- D-21 preserved as RESERVED.
- No schema or test suite files touched.
- No git write or commit commands run without authorization.
