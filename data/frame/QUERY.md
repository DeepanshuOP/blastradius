# SEART GitHub Search query — BlastRadius repository sampling frame

## 0. Fill in this form

Language → Java (Run 1) / Python (Run 2)
Stars (min) → 500
Commits (min) → 1000
Include forks → unchecked / off
Last commit (from) → 2026-06-05
License → check all SPDX license checkboxes (exclude only "None")

Leave every other field on the form at its default.

Run twice — once with Language=Java, once with Language=Python. Export each to CSV.

## Verify on site

Two of the fields above are named from memory, not confirmed against the
live form. Check both before running:

- **"Include forks"** — believed to be a fork-inclusion toggle that excludes
  forks when left unchecked. If the live form has no control matching this
  description, find whichever control actually governs fork inclusion under
  its real label. Do not run the query until you've identified it.
- **"License"** — believed to present as a set of SPDX license checkboxes.
  If it's a dropdown, multi-select, or anything else, set it to include
  every license and exclude only "no license" / unlicensed — do not narrow
  to a permissive subset. If you can't tell which setting does that, stop
  and ask rather than guessing.

Step 1 of T0.1a only. No code in this document; this is the query
specification and export procedure. Produced against ROADMAP §23.1
(criteria), §23.3 (attrition funnel), §8.1 (T0.1 subtasks). Where
`prompts/T0.1a_repo_frame.md` disagreed with §23.1, §23.1 wins — see the
disagreement note in this task's report.

## 1. Source

**SEART GitHub Search** — Dabic, O., Aghajani, E., & Bavota, G. (2021).
Sampling projects in GitHub for MSR studies. *MSR*.
<https://seart-ghs.si.usi.ch/>

Used instead of hand-rolled GitHub search because it indexes every repo with
≥10 stars across 25 characteristics and is a published, citable sampling
instrument — the query below is released verbatim in this file for
reproducibility (§23.2 point 1).

## 2. Criteria — SEART-side vs. API-side

Every criterion in ROADMAP §23.1, one row each. Columns: the criterion as
stated in §23.1, the SEART field and exact value to enter (or a dash if
SEART cannot express it), and where it lands if it can't be expressed at
query time.

| # | Criterion (§23.1) | SEART field + exact value to enter | Notes / API-side deferral |
|---|---|---|---|
| 1 | language ∈ {Java, Python} | **Language**: `Java` (run 1) / `Python` (run 2) | SEART filters one language per query (§3 below) |
| 2 | ≥500 stars | **Stars** (min): `500` | SEART-side |
| 3 | ≥1000 commits | **Commits** (min): `1000` | SEART-side. This is SEART's lifetime commit count, not a windowed count — matches §23.1's phrasing, which is also unwindowed |
| 4 | not a fork | **Include forks**: unchecked / off | *Believed* control name — SEART exposes a fork-inclusion toggle that defaults to excluding forks when unchecked; confirm the exact label against the live form before running, do not assume this row without checking |
| 5 | ≥1 commit in the last 60 days | **Last commit** (from): `2026-06-05` | Resolved against today, 2026-08-04 (§4). SEART-side via its last-commit-date range field |
| 6 | has a `LICENSE` | **License**: select all recognized SPDX license checkboxes (i.e. exclude only `None` / no-license) | SEART-side, but *presence-only* — do not restrict to a permissive subset (MIT/Apache-2.0/BSD). §23.1 requires only that a license exists, not that it is permissive. `prompts/T0.1a_repo_frame.md` asked for a permissive-only filter here; that is a disagreement, §23.1 wins — see report item 4 |
| 7 | ≥50 PRs in the last 90 days | — | **API-side.** SEART's pull-request field (if present in the export) is a lifetime total, not a rolling 90-day window — it cannot express this criterion at all, windowed or not. Deferred; §8.1 does not assign this a dedicated subtask number the way it does for workflow-run liveness (T0.1 subtask 2, `liveness.py`) or workflow triage (subtask 3, `workflow_triage.py`) — flagging this as a gap in the subtask breakdown for Deepanshu, not resolving it here. Window if implemented: `2026-05-06` to `2026-08-04` |
| 8 | ≥100 workflow runs in the last 90 days | — | **API-side**, T0.1 subtask 2 (`src/harvest/liveness.py`), per §8.1: `GET /repos/{o}/{r}/actions/runs?per_page=1` → `total_count`. Window: `2026-05-06` to `2026-08-04` |
| 9 | ≥1 workflow matching test intent (`test\|ci\|build\|pytest\|mvn\|gradle`) | — | **API-side**, T0.1 subtask 3 (`src/harvest/workflow_triage.py`) |
| 10 | excluding workflows matching `release\|deploy\|docker\|publish\|docs\|dependabot\|codeql\|lint-only` | — | **API-side**, same subtask as #9 (`workflow_triage.py`) |

Rows 7–10 are exactly the CI-liveness/triage split described in §8.1: SEART
supplies static repo metadata only, nothing about Actions runs, workflow
content, or time-windowed PR activity. Rows 1–6 are the only ones that go
into the exported SEART query itself.

## 3. Two runs, one merged file

SEART filters by a single **Language** value per query — it cannot export
Java and Python in one pass. This means:

- **Run 1**: all criteria above with Language = `Java`, export to CSV.
- **Run 2**: all criteria above with Language = `Python`, export to CSV.
- **Merge**: concatenate the two exports into a single
  `data/frame/repos_raw.csv` (§6), keeping exactly one header row and
  verifying every row's language column is populated correctly (`Java` or
  `Python`) before concatenating — SEART's export may not label the
  language column identically run-to-run if the field is a repo-level
  attribute rather than an echo of the query filter, so check this by hand
  on a few rows from each file before merging.

## 4. Date-relative filters resolved to absolute dates

Resolved against today, **2026-08-04**, so the query stays re-runnable
without recomputing relative windows later:

| Filter | Window |
|---|---|
| ≥1 commit in the last 60 days (row 5, SEART-side) | `2026-06-05` → `2026-08-04` |
| ≥50 PRs in the last 90 days (row 7, API-side) | `2026-05-06` → `2026-08-04` |
| ≥100 workflow runs in the last 90 days (row 8, API-side) | `2026-05-06` → `2026-08-04` |

## 5. Expected result count

§23.3 stage 0 target: **~2,000** combined raw candidates (both languages,
before any attrition). §8.1 separately says to over-sample toward
2,000–5,000 raw candidates, since the frame is expected to attrit down to
~300 candidates by stage 3 and ~60–100 usable repos by stage 8 — aggressive
over-sampling here is the explicit design, not a mistake to correct later.

If the actual combined count is far off, see the appendix.

## 6. Export destination

Merged CSV: **`data/frame/repos_raw.csv`** — matches ROADMAP §35 (`T0.1a`)
and `prompts/T0.1a_repo_frame.md`.

This is the *raw* SEART export (columns as SEART names them, whatever those
turn out to be — not fixed by this document). It is not the same file as
the normalized `repos.csv` that `src/harvest/frame.py` (T0.1a step 2)
produces from it. That downstream file's columns are fixed by §8.1 subtask
4 and must be reproduced character-identical when `frame.py` is written:

```
owner, repo, lang, stars, commits, default_branch, n_runs_90d, test_workflow_ids, license
```

## 7. Actual result count

JAVA COUNT: 1123
PYTHON COUNT: 2548
COMBINED: 3671
DATE RUN: 2026-08-05

Java:Python ratio is ~1:2.3 by repo count — revisit against §23.4's instance-count balance target.

---

## Appendix — Rationale — read only if challenged

### Licence policy (§2.1)

§23.1 and §22.4 both govern licence, but at different stages, and they say
different things — this is not a conflict to resolve, it's two gates that
bind at different times:

- **§23.1 (frame time)** requires only that a `LICENSE` is present. **§22.4
  (release hygiene)** requires **permissive licences only** before BR-Bench
  ships. Both are in force; neither overrides the other, because they apply
  to different stages of the pipeline.
- **Frame-time policy: filter on presence only. Do not filter on licence
  type in SEART** (row 6 above stays presence-only, not permissive-only).
  Rationale: GitHub Actions logs expire after 90 days (§5, T1) — that clock
  is the one unrecoverable resource in this project, so narrowing the frame
  by licence type before harvest would permanently destroy ground truth
  that a later, more careful licence decision might have wanted to keep.
  A permissive-only filter at frame time also skews the corpus toward
  Apache-heavy Java against the §23.4 language-balance target, which is a
  sampling-bias cost paid for nothing if the repo would have been excluded
  at release anyway on other grounds.
- **Capture the SPDX identifier per repo** so licence becomes a reportable
  attrition stage (§23.3) applied at release, not silently at capture —
  the funnel should show how many repos permissive-licence filtering
  removes, not hide it by never harvesting them.
- **Open question for the guide:** whether *derived* metadata (test names,
  SHAs, outcome counts — not the source code itself) mined from a copyleft
  repo is redistributable under CC-BY 4.0 (§22.2) is a question for
  Dr. Yoga Raja C A, not something to settle unilaterally in a query
  specification file.

### Expected count — over/under guidance (§5)

**If the actual combined count is far off:**
- **Far under** (roughly <1,000): the SEART-side thresholds (rows 2–3,
  stars/commits) are likely too strict for the combined Java+Python pool —
  loosen them, document the change and the reason, and bump
  `frame_version` rather than silently re-running with different numbers.
- **Far over** (roughly >5,000): no action needed. Rows 7–10 (CI liveness
  and workflow triage) are API-side and will cut this down sharply on their
  own; record the raw stage-0 count for the attrition table (§23.3) and move
  on to `liveness.py`.
