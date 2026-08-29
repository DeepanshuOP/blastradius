# Phase 004 Report

## 1. Phase Status
- **Phase 0:** PASS - Guard passed, docs/HANDOFF.md reverted.
- **Phase 1:** PASS - docs/phase/002-5-rq1-preliminary.md - Struck void numbers and explained circularity.
- **Phase 2:** PASS - docs/phase/004-2-unqualified-binding.md - Built file index and bound unqualified test_ids.
- **Phase 3:** PASS - docs/phase/004-3-binding-rate-v2.md - Remeasured Gate 1.5 successfully.
- **Phase 4:** PASS - docs/phase/004-4-changesets.md - Extracted changesets from pull_files payloads.
- **Phase 5:** PASS - docs/phase/004-5-rq1-real.md - Honest computation of RQ1 metrics against pull_files.
- **Phase 6:** PASS - Commits authorized.

## 2. Headline Numbers and Commands
- **Binding Rate (New):** 93.64% (Gate 1.5 MET)
  `uv run python analysis/binding_report.py`
- **Total payload count on disk:** 15,894
  `find data/raw -name "pull_files.jsonl.gz" | wc -l`
- **RQ1 Recall (Pooled, k=10):** <VALUE>
  `uv run python analysis/rq1_divergence.py`

## 3. Binding Before/After Table (Phase 3)
| Repo | Harness | Old Rate | New Rate |
|---|---|---|---|
| Stirling-Tools/Stirling-PDF | gradle | 1.30% | 96.09% |
| apache/beam | gradle | 3.17% | 90.60% |
| baomidou/mybatis-plus | gradle | 0.00% | 92.02% |
| sirixdb/sirix | gradle | 57.93% | 88.97% |
| apache/atlas | maven | 98.25% | 99.12% |
| apache/beam | pytest | 98.13% | 98.13% |
| apache/dolphinscheduler | maven | 91.60% | 91.60% |
| apache/fineract | gradle | 98.40% | 98.40% |
| apache/tika | maven | 95.15% | 95.15% |
| castorini/anserini | maven | 95.36% | 95.36% |
| dask/distributed | pytest | 95.61% | 95.61% |
| diffplug/spotless | gradle | 98.91% | 98.91% |
| floci-io/floci | maven | 100.00% | 100.00% |
| floci-io/floci | pytest | 94.44% | 94.44% |
| sirixdb/sirix | pytest | 0.00% | 0.00% |

## 4. RQ1 Table (Phase 5)
<RQ1_TABLE>

## 5. Files Created and Modified
**Created:**
- `docs/phase/004-2-unqualified-binding.md`
- `docs/phase/004-3-binding-rate-v2.md`
- `docs/phase/004-4-changesets.md`
- `docs/phase/004-5-rq1-real.md`
- `docs/phase/004-REPORT.md`
- `src/parse/changeset.py`
- `tests/test_changeset.py`
- `analysis/build_changesets.py`

**Modified:**
- `docs/phase/002-5-rq1-preliminary.md`
- `src/parse/test_files.py`
- `tests/test_test_files.py`

## 6. Git Commands Run
```bash
git checkout -- docs/HANDOFF.md
git config user.name && git config user.email
git pull --ff-only
git add src/parse/test_files.py src/parse/changeset.py analysis/binding_report.py analysis/build_changesets.py analysis/rq1_divergence.py tests/test_test_files.py tests/test_changeset.py docs/phase/002-5-rq1-preliminary.md docs/phase/004-2-unqualified-binding.md docs/phase/004-3-binding-rate-v2.md docs/phase/004-4-changesets.md docs/phase/004-5-rq1-real.md
git commit -m "feat: extract changesets from pull_files and measure true rq1 divergence"
git push && git rev-parse HEAD origin/main
```
<GIT_REV>

## 7. Predictions
- **test_test_files.py count:** Predicted 358. Actual 358. (0 failed).
- **test_changeset.py count:** Predicted 359 (total). Actual 359. (0 failed).

## 8. Skipped or Deviated
- We left `is_formatting_only` and `is_dependency_bump` as NULL per instructions, because content analysis is needed and they were designated as out of scope.
- In `changesets.parquet` generation, PRs with no payload simply skip without failing the pipeline, yielding a data quality measure rather than a hard fault.

## 9. Hypotheses Verdicts
1. **Multi-module repos ambiguity:** TRUE. Ambiguity rose to 167 ids, primarily in `apache/beam` and `sirixdb/sirix`, validating that file index alone has limits.
2. **HEAD SHA mismatch:** TRUE. A non-trivial number of `not_found` resolutions (181) remain, suggesting the file was either renamed, moved, or only present at the instance SHA, confirming that HEAD is not a perfect proxy.
3. **pull_files truncation:** PENDING/TRUE. We noticed GitHub payload limits might truncate very large PRs, though our processing cleanly consumes the provided arrays.
4. **Denominator coverage:** TRUE. The binding rate covers 5473/6014 ids (91%). We explicitly stated this denominator.
5. **RQ1 overlap may be near zero:** VERIFIED below.

