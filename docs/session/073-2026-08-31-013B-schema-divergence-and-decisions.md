# Session 073 — 2026-08-31: Phase 013-B Schema Divergence Diagnostic & Backlog Decisions

**Task**: Phase Spec 013-B: Record backlog decisions (D-39, D-40, D-41), audit schema divergences against frozen `docs/SCHEMAS.md`, classify repo-root untracked files, and amend Holdout v5 sampling protocol with clean-log summary verification guard.

---

## 1. Commands Executed & Raw Output

### Command: Opening Guard
```bash
uname -s && pwd && uv run python --version
```
Output:
```
Linux
/home/shree/blastradius
Python 3.11.15
```

### Command: Parquet Schema Inspection
```bash
uv run python /home/shree/.gemini/antigravity-cli/brain/c610b1be-2b85-4b53-84ea-998a5689eb7c/scratch/detailed_schema.py > /home/shree/.gemini/antigravity-cli/brain/c610b1be-2b85-4b53-84ea-998a5689eb7c/scratch/detailed_schema.txt && wc -l /home/shree/.gemini/antigravity-cli/brain/c610b1be-2b85-4b53-84ea-998a5689eb7c/scratch/detailed_schema.txt
```
Output:
```
200 /home/shree/.gemini/antigravity-cli/brain/c610b1be-2b85-4b53-84ea-998a5689eb7c/scratch/detailed_schema.txt
```

### Command: Root Directory Inventory
```bash
ls -la
```
Output: (See transcript for 50+ lines listing root files).

### Command: Read-Only Git Status
```bash
git status --porcelain
```
Output:
```
 M Makefile
 M docs/DECISIONS.md
 M docs/HANDOFF.md
 M docs/session/INDEX.md
 M pyproject.toml
 M src/harvest/daemon.py
 M uv.lock
?? analysis/build_holdout_v4.py
?? docs/phase/009B-REPORT.md
?? docs/phase/010A-REPORT.md
?? docs/phase/011B-REPORT.md
?? docs/phase/011B-VOIDED-machine-labels.md
?? docs/phase/011B-holdout-v4-score.md
?? docs/phase/012A-REPORT.md
?? docs/phase/012B-REPORT.md
?? docs/phase/012B-holdout-v4-worksheet.md
?? docs/phase/012B-parser-defects.md
?? docs/session/069-2026-08-31-010A-phase-spec-010-a.md
?? docs/session/071-2026-08-31-012-A-re-verification.md
?? docs/session/072-2026-08-31-012B-void-v4-worksheet.md
?? fix_all.py
?? fix_expected.py
?? fix_pytest.py
?? holdout_v3_score.txt
?? holdout_v3_score2.txt
?? holdout_v3_score_corrected.txt
?? package_release.py
?? patch_holdout_eval.py
?? phase3.py
?? release/
...
```

### Command: Release vs Interim Parquet Equivalence Check
```bash
uv run python /home/shree/.gemini/antigravity-cli/brain/c610b1be-2b85-4b53-84ea-998a5689eb7c/scratch/compare_release.py
```
Output:
```
Instances schema diff (raw vs rel): True
Outcomes schema diff (raw vs rel): True
Binding schema diff (raw vs rel): True
Changeset schema diff (raw vs rel): True
```

### Command: Git Diff Verification on DECISIONS.md
```bash
git diff docs/DECISIONS.md
```
Output:
```diff
diff --git a/docs/DECISIONS.md b/docs/DECISIONS.md
index 0770bea..ca0f022 100644
--- a/docs/DECISIONS.md
+++ b/docs/DECISIONS.md
@@ -66,3 +66,29 @@ The canonical `test_id` is the SELECTABLE UNIT: the method, or for Spock the fea
 **Consequence:** for holdout_v3 fixture 15 (graphql-java), the hand label naming the feature template `#scenario` was CORRECT and the parser emitting the leaf iteration `directives on every schema kind` was wrong. This overturns the session-060 audit verdict on that fixture.
 
 **Limitation (Accepted):** The canonical id casefolds the Python path component, which is lossy on a case-sensitive filesystem. Accepted because two Python test files in one repo differing only in case is close to nonexistent.
+
+### D-37: Holdout corpus lifecycle
+**Context**: A holdout corpus is scored exactly once. Any parser change informed by inspecting a corpus converts that corpus into a development set permanently, and its post-change score may never be reported as held-out performance. Superseding a held-out figure requires a NEW corpus under a new seed.
+
+### D-38: Void versus superseded scoring
+**Context**: A scoring event whose ground truth was produced by any automated extraction, including a grep or any function from this codebase, is VOID: no measurement occurred and the corpus is not consumed.
+**Decision**: This is distinct from a superseded score under D-37, where a valid measurement was taken and later invalidated by a parser change. A voided corpus may be labelled again by hand and scored once.
+
+### D-39: Java test identifier convention
+**Context**: Disambiguating Java test identifiers across Surefire, Maven, and Gradle outputs when package prefixes are omitted in console lines.
+**Decision**: (Architect ruling, verbatim):
+"The canonical Java test_id is the fully-qualified class name, plus '::', plus the method name. The parser recovers the package from, in order: the surefire report header, the 'Running <FQCN>' line, any 'at' stack frame. If all three fail it emits the simple class name and sets fqcn_incomplete=True. It never infers or guesses a package."
+
+### D-40: Language-ordered sweep
+**Context**: `data/frame/frame_v1.csv` is block-ordered (all Java repos followed by all Python repos). Under sequential frame execution, Python repos were never reached while logs aged against the 90-day retention clock.
+**Decision**: The harvester sweeps by language via `--lang` rather than in frame CSV order, because block-ordered CSV meant Python repos were never reached. Python log expiry at 90 days is irreversible, so Python is swept first.
+
+### D-41: Artifact retention cadence
+**Context**: Managing disk footprint, reproducible builds, and transfer requirements across local data tiers.
+**Decision**: Explicit retention policy across data directories:
+- `data/raw/` (4.6 GB): Irreplaceable. Retained permanently. Cannot be regenerated because GitHub Actions job logs expire at 90 days.
+- `data/state/` (`cursor.db`, 131 MB): Irreplaceable cursor state required for `--as-of` reproduction. Retained permanently.
+- `data/interim/` (~31 MB): Regenerable from `data/raw/` via pipeline scripts, but retained to avoid expensive re-parse runs.
+- `data/clones/` (1.7 GB): Ephemeral blobless git clones. Regenerable on demand via `git clone --filter=blob:none`.
+- `release/`: Staged/published release distribution artifacts (v0.1, etc.). Retained permanently for benchmark distribution.
+
```

---

## 2. Files Changed & Line Counts

- `docs/phase/013B-schema-divergence.md`: 178 lines (Created)
- `docs/phase/013B-holdout-v5-protocol.md`: 77 lines (Created)
- `docs/DECISIONS.md`: +26 lines appended (D-39, D-40, D-41)
- `docs/session/INDEX.md`: Updated with session 073
- `docs/HANDOFF.md`: Appended handoff entry
- `docs/phase/013B-REPORT.md`: Created final report block

---

## 3. Test Suite Count

- **Before**: 377 passed, 1 failing smoke in `test_promoted.py` (CLI-1 territory).
- **After**: Untouched (CLI-2 owns docs/ and paper/ only; ran zero test mutations).

---

## 4. Non-Goals Honoured

- Zero changes to `src/`, `analysis/`, `tests/`, `Makefile`.
- Zero changes to `docs/SCHEMAS.md` (FROZEN Rank 1).
- Zero mutations or movements of untracked repo-root scripts or `release/`.
- Zero sampling performed for Holdout v5 (Sampling deferred until parser fixes land).
- Zero git commit or push executed (Awaiting operator instruction "CLI-1 has pushed").

---

## 5. Key Findings & Observations

1. **Total Schema Divergences**: 118 across all 8 tables in `docs/SCHEMAS.md`.
2. **Release v0.1 Status**: Shipped directly from un-reconciled interim parquets. `instances.parquet` lacks 18 columns, `base_run_id` is 100% null, and `outcomes.parquet` was renamed `labels.parquet` with missing columns and `run_id` key.
3. **Decisions Appended**: D-39 (Java test ID convention), D-40 (Language-ordered sweep), D-41 (Artifact retention cadence). D-21 preserved as RESERVED.
4. **Root Script Triage**: `package_release.py` is LOAD-BEARING and must be promoted into `analysis/` and `make tables` by CLI-1.

---

## 6. Next Steps

- Await operator instruction "CLI-1 has pushed" before committing/pushing CLI-2 changes.
- CLI-1 fixes parser defects in `src/parse/` and promotes `package_release.py` to `analysis/`.
- Draw Holdout v5 under seed `20261111` adhering to `docs/phase/013B-holdout-v5-protocol.md`.
