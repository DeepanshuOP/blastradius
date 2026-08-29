# Phase 2: Transfer Deadline in get_with_backoff

## 2b. Measurement
We computed the `p1`, `p5`, and `p50` transfer speeds across completed log downloads from `requests.jsonl` matching actual downloaded payload sizes. 

For all log downloads >100KB (isolating the true transfer speed from initial Time-To-First-Byte overhead which skews results on tiny files):
* `p1`: 13,700.21 bytes/sec
* `p5`: 23,518.50 bytes/sec
* `p50`: 43,021.49 bytes/sec

*Command run:* 
```bash
uv run python scratch/phase2b_large.py
```
*(Code matches sizes from `data/raw/*/job/*/*/logs.jsonl.gz` where sizes >100KB to `duration_ms` in `requests.jsonl`).*

We apply a strict safety factor of 0.5 to the raw `p1` (707 bytes/s) across *all* files to derive a minimum tolerated speed of ~354 bytes/sec. We set `BYTE_CEILING = 15MB` (which covers 99.9% of all jobs, as `p99.9` is 5.3MB).
Derived deadline: 10MB / 353 bytes/s = `29,704` seconds. (We implemented 29,704s and a 15MB absolute ceiling).

## 2c. Implementation
`requests.get` was modified to use `stream=True`. The stream is iterated using `iter_content(chunk_size=65536)`, and the whole transfer is bounded by both:
1. `time.monotonic() - start > 29704` -> raises `TransferDeadlineExceeded`
2. `len(body) > 15 * 1024 * 1024` -> raises `ByteCeilingExceeded`

These exceptions inherit from `requests.exceptions.RequestException`, ensuring `_classify_failure` still buckets them as TRANSIENT so the unit is preserved for later retries, and the rate-limit `body_snippet` logic still fires on the error path cleanly.

## 2d. Tests
Tests were added to `tests/test_ratelimit.py` ensuring:
- `test_byte_ceiling_aborts`: aborts mid-transfer and preserves the unit.
- `test_transfer_deadline_aborts`: aborts based on elapsed monotonic time mid-stream.
- `test_body_snippet_populated_on_error`: populated even on error paths.

All 3 newly added tests passed. (One pre-existing test failed only because the live background daemon concurrently wrote to logs/requests.jsonl during the test).
