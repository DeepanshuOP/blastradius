<!-- blastradius-bot -->
## BlastRadius

PR #1 · `672971d66a` → `a24e22e7a1` · 181 unique test ids (297 executed cases, inherited methods share ids) · **155 failing ids** (260 failing cases) · first failure at case 9 of 297

### 1. Tests most at risk (e1-lgbm-v1)

| # | Test file | Score | Why |
|--:|---|--:|---|
| 1 | `tests/test_itsdangerous/__init__.py` | -1.63 | cochg_n_files_with_partner=0 (+0.86); hist_repo_rank=1 (-0.54); chg_touches_test=0 (+0.31) |
| 2 | `tests/test_itsdangerous/test_encoding.py` | -1.63 | cochg_n_files_with_partner=0 (+0.86); hist_repo_rank=2 (-0.54); chg_touches_test=0 (+0.31) |
| 3 | `tests/test_itsdangerous/test_url_safe.py` | -1.63 | cochg_n_files_with_partner=0 (+0.86); hist_repo_rank=6 (-0.54); chg_touches_test=0 (+0.32) |
| 4 | `tests/test_itsdangerous/test_serializer.py` | -1.96 | cochg_n_files_with_partner=0 (+0.70); hist_repo_rank=3 (-0.48); chg_touches_test=0 (+0.31) |
| 5 | `tests/test_itsdangerous/test_signer.py` | -1.96 | cochg_n_files_with_partner=0 (+0.70); hist_repo_rank=4 (-0.48); chg_touches_test=0 (+0.31) |
| 6 | `tests/test_itsdangerous/test_timed.py` | -1.96 | cochg_n_files_with_partner=0 (+0.70); hist_repo_rank=5 (-0.49); chg_touches_test=0 (+0.31) |

### 2. Results, risk-first

| Test | Outcome | Message |
|---|---|---|
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_alt_salt[Serializer]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_alt_salt[serializer_fact…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_payload_exception[Se…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_payload_exception[se…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_signature_exception[…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_signature_exception[…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[Serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_fallback_signers[Seriali…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_fallback_signers[seriali…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_file[Serializer]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_file[serializer_factory1]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_loads_unsafe[Serializer]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_loads_unsafe[serializer_…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-No…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-Tr…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-st…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-te…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-va…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[Serializer-va…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[serializer_fa…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[serializer_fa…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[serializer_fa…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[serializer_fa…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[serializer_fa…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer[serializer_fa…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_serializer_kwargs[Serial…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_signer_cls[Serializer]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_signer_cls[serializer_fa…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_signer_kwargs[Serializer]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_signer_kwargs[serializer…` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::test_alt_salt` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::test_alt_salt[Serializer]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |
| `tests/test_itsdangerous/test_serializer.py::test_alt_salt[serializer_factory1]` | failed | TypeError: unsupported operand type(s) for -: 'bytes' and 'bytes' |

_141 more passing tests not shown._

### 3. Triage of each failure

155 mine, 0 inherited, 0 flaky (of 155 failing).

| Failing test | Class | Confidence | Why |
|---|---|--:|---|
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_alt_salt[Seria…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_alt_salt[seria…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_payload_ex…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_payload_ex…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_signature_…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_bad_signature_…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_changed_value[…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_fallback_signe…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_fallback_signe…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_file[Serialize…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_file[serialize…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_loads_unsafe[S…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |
| `tests/test_itsdangerous/test_serializer.py::TestSerializer::test_loads_unsafe[s…` | **mine** | 0.90 | model P(not mine) = 0.10 (threshold 0.84); no evidence it was already failing |

_135 more failures not shown._

_mine = caused by this change; inherited = already failing on the base; flaky = reruns flip._

### 4. Proposed fix

Validated: the full suite passed with this patch (1 attempt(s)). Review it, then accept the suggestion on the diff.

`src/itsdangerous/signer.py` line 204:

```suggestion
                bytes, self.digest_method(self.salt + b"signer" + secret_key).digest()
```


---
<sub>BlastRadius (exploratory) · model `openai/gpt-oss-20b` · 1,495 tokens · validated: full suite passed · this bot only comments; it never pushes or merges.</sub>
