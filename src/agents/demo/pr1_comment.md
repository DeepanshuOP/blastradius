<!-- blastradius-bot -->
## BlastRadius

PR #1 · `e2d4877af1` → `de92843ab4` · 297 tests · **5 failing** · first failure at position 127 of 297

### 1. Tests most at risk (e1-lgbm-v1)

| # | Test file | Score | Why |
|--:|---|--:|---|
| 1 | `tests/test_itsdangerous/__init__.py` | -0.72 | cochg_n_files_with_partner=0 (+0.94); chg_n_lines=2 (+0.52); prox_max_jaccard=0.285714 (+0.37) |
| 2 | `tests/test_itsdangerous/test_encoding.py` | -0.72 | cochg_n_files_with_partner=0 (+0.94); chg_n_lines=2 (+0.52); prox_max_jaccard=0.285714 (+0.37) |
| 3 | `tests/test_itsdangerous/test_serializer.py` | -0.72 | cochg_n_files_with_partner=0 (+0.94); chg_n_lines=2 (+0.52); prox_max_jaccard=0.285714 (+0.37) |
| 4 | `tests/test_itsdangerous/test_signer.py` | -0.72 | cochg_n_files_with_partner=0 (+0.94); chg_n_lines=2 (+0.52); prox_max_jaccard=0.285714 (+0.37) |
| 5 | `tests/test_itsdangerous/test_url_safe.py` | -0.72 | cochg_n_files_with_partner=0 (+0.94); chg_n_lines=2 (+0.52); prox_max_jaccard=0.25 (+0.36) |
| 6 | `tests/test_itsdangerous/test_timed.py` | -1.21 | cochg_n_files_with_partner=0 (+0.82); chg_n_lines=2 (+0.37); chg_touches_test=0 (+0.31) |

### 2. Results, risk-first

| Test | Outcome | Message |
|---|---|---|
| `tests/test_itsdangerous/test_timed.py::TestTimedSerializer::test_max_age` | failed | itsdangerous.exc.SignatureExpired: Signature age 1 > 10 seconds |
| `tests/test_itsdangerous/test_timed.py::TestTimestampSigner::test_max_age` | failed | itsdangerous.exc.SignatureExpired: Signature age 1 > 10 seconds |
| `tests/test_itsdangerous/test_timed.py::test_max_age` | failed | itsdangerous.exc.SignatureExpired: Signature age 1 > 10 seconds |
| `tests/test_itsdangerous/test_timed.py::test_max_age[value0]` | failed | itsdangerous.exc.SignatureExpired: Signature age 1 > 10 seconds |
| `tests/test_itsdangerous/test_timed.py::test_max_age[zlib]` | failed | itsdangerous.exc.SignatureExpired: Signature age 1 > 10 seconds |
| `tests/test_itsdangerous/test_encoding.py::test_base64[\u7121\u9650]` | passed |  |
| `tests/test_itsdangerous/test_encoding.py::test_base64[infinite]` | passed |  |
| `tests/test_itsdangerous/test_encoding.py::test_base64_bad` | passed |  |
| `tests/test_itsdangerous/test_encoding.py::test_int_bytes[0-]` | passed |  |
| `tests/test_itsdangerous/test_encoding.py::test_int_bytes[18446744073709551615-\xff\xff\xf…` | passed |  |
| `tests/test_itsdangerous/test_encoding.py::test_int_bytes[192-\xc0]` | passed |  |
| `tests/test_itsdangerous/test_encoding.py::test_want_bytes[ma\xf1ana]` | passed |  |
| `tests/test_itsdangerous/test_encoding.py::test_want_bytes[tomorrow]` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_alt_salt[Serializer]` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_alt_salt[serializer_fact…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_payload_exception[Se…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_payload_exception[se…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_signature_exception[…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_signature_exception[…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_fallback_signers[Seriali…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_fallback_signers[seriali…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_file[Serializer]` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_file[serializer_factory1]` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_iter_unsigners[Serialize…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_iter_unsigners[serialize…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_loads_unsafe[Serializer]` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_loads_unsafe[serializer_…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-No…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-Tr…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-st…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-te…` | passed |  |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-va…` | passed |  |

_257 more passing tests not shown._

### 3. Triage of each failure

5 mine, 0 inherited, 0 flaky (of 5 failing).

| Failing test | Class | Confidence | Why |
|---|---|--:|---|
| `tests/test_itsdangerous/test_timed.py::TestTimedSerializer::test_max_age` | **mine** | 0.96 | model P(not mine) = 0.04 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_timed.py::TestTimestampSigner::test_max_age` | **mine** | 0.94 | model P(not mine) = 0.06 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_timed.py::test_max_age` | **mine** | 0.94 | model P(not mine) = 0.06 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_timed.py::test_max_age[value0]` | **mine** | 0.94 | model P(not mine) = 0.06 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_timed.py::test_max_age[zlib]` | **mine** | 0.96 | model P(not mine) = 0.04 (threshold 0.84); no evidence it was already failing |

_mine = caused by this change; inherited = already failing on the base; flaky = reruns flip._

### 4. Proposed fix

Validated: the full suite passed with this patch (1 attempt(s)). Review it, then accept the suggestion on the diff.

`src/itsdangerous/timed.py` line 141:

```suggestion
            if age > max_age:
```


---
<sub>BlastRadius (exploratory) · model `openai/gpt-oss-120b` · 1,008 tokens · validated: full suite passed · this bot only comments; it never pushes or merges.</sub>

