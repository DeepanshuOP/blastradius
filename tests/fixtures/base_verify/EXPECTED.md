# Expected output — `tests/fixtures/base_verify/`

Hand-written ground truth for the invariant-6 guard in
`src/label/base_resolve.py`. These are real files, extracted unmodified from
`data/raw` during the Phase 017 `exact_green` verification sweep. Nothing here
is synthetic.

## Provenance

| | |
|---|---|
| Repository | `agno-agi/agno` |
| Base workflow run | `32727954465` |
| Job | `97433407085`, "Lint PR Title and Body" |
| Run conclusion (GitHub API) | `success` |
| Jobs in the run | 1 |

`agno-agi__agno__run32727954465__jobs.json` is the merged `/actions/runs/{id}/jobs`
payload. `agno-agi__agno__job97433407085__log.txt` is that job's raw log, 3,016
bytes.

## The case this fixture exists to pin

This run **concluded `success` and ran no tests at all** — it lints a pull
request title. Under the old code path `conclusion == "success"` alone assigned
`exact_green`, which asserts `T_base_fail = ∅` and licenses every failing head
test to become a fault-revealing label. That is exactly the trap integrity
invariant 6 forbids: an empty base failure set is not evidence that the base
was green.

## Expected

| Assertion | Value |
|---|---|
| `classify_dispatch_log(log)` | `NO_TEST_OUTPUT` |
| Test identifiers extracted | 0 |
| Verified `base_parse_status` | `no_tests_confirmed` |
| Resulting `BaseResolution.status` | `no_base` |
| `BaseResolution.base_run_id` | `None` |
| `BaseResolution.can_emit_labels` | `False` |
| Labels emitted | **0** |

Constructing `BaseResolution(status="exact_green")` with this
`base_parse_status` must raise `ValueError`. A run conclusion is never
sufficient.

**These values are ground truth. If a test against them fails, fix the code.**
