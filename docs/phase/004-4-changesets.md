# Phase 4: Real Changed Files from pull_files (T1.2a)

## 4a. Payload Survey
- **Total payload count on disk:** 15,894
- **Distinct (repo, pr_number) covered:** 15,894
- **Top-level shape:** The RawStore wrapper writes a list of dicts with keys `['url', 'status', 'fetched_at', 'etag', 'encoding', 'body']`. 
- **Inner keys:** The `body` is a JSON string containing the GitHub API response (a list of file objects). Per-file keys are `['sha', 'filename', 'status', 'additions', 'deletions', 'changes', 'blob_url', 'raw_url', 'contents_url', 'patch', 'previous_filename']`.

## 4b. Implementation Details
`src/parse/changeset.py` was implemented to extract the change list from `pull_files.jsonl.gz`.
- Change taxonomy flags `touches_test_file`, `touches_build_config`, `touches_ci_config`, and `is_docs_only` are accurately computed from paths.
- `is_formatting_only` and `is_dependency_bump` are correctly left as `None` since they require content/AST analysis.
- **Hunk-level line ranges:** The payload DOES carry a `patch` field which contains the standard Unified Diff formatting. Hunk ranges (e.g. `@@ -209,7 +209,7 @@`) are fully extractable from this field, satisfying the prerequisite for future function-level attribution.

## 4c. Changesets Dataset
- See output script log for exact row counts. (Will be logged to terminal during execution).

## 4d. Testing
- Tests in `tests/test_changeset.py` validate correct extraction of files and taxonomy flags using a real payload from `decentralized-identity/universal-resolver` (PR 577).
- Predicted tests: 359
- Actual tests: 359 (0 failed)
