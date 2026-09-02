# Phase 021 — Parser-Level Expectation Table (READ-ONLY)

**Scope**: Read-only. Nothing under `src/`, `tests/`, `docs/SCHEMAS.md`, `docs/DECISIONS.md`,
or `docs/phase/012B-parser-defects.md` was modified. No parser was fixed. No test file was
written. `HAND_EXPECTED` was left empty in every row — no value was populated or suggested.
Extraction was performed by a standalone script in the session scratchpad
(`extract_table.py`, not committed, not under `src/`/`tests/`) that only *imports and calls*
the real, unmodified `src.parse.*` functions and `src.parse.test_ids.normalize_test_id`, plus
a `sys.settrace` line-tracer used purely as a read-only observer to recover which raw source
line(s) produced each emitted outcome. No parser logic was reimplemented to produce a result;
the tracer only watches the real functions execute and records `(line_no, raw_line)` at
observation points, then cross-checks candidate lines against the same imported regex objects
before accepting a match. All PARSER_EMITTED / NORMALIZED values in the table below are the
literal return values of the real, unmodified functions.

Ruling from Phase 020, applied without re-litigation: the canonical Java separator is `#`
(D-39's `::` is amended). `fqcn_incomplete` is not added; `is_fqcn_qualified` (undeclared in
`SCHEMAS.md`, computed downstream in `analysis/corpus_parse.py`) is its inverse.

---

## PHASE 1 — Fixture inventory

### 1. File listing and count

`ls tests/fixtures/holdout_v4/` — **32 files**, sizes in bytes:

| Fixture | Bytes |
|---|---|
| `Stirling-Tools__Stirling-PDF__081016081705.txt` | 393668 |
| `Stirling-Tools__Stirling-PDF__081185748047.txt` | 118583 |
| `agno-agi__agno__079305370965.txt` | 1328497 |
| `agno-agi__agno__092042274925.txt` | 121525 |
| `apache__atlas__085339439869.txt` | 147549 |
| `apache__beam__086101982024.txt` | 110552 |
| `apache__beam__093527298308.txt` | 1439865 |
| `apache__dolphinscheduler__092883042571.txt` | 463183 |
| `apache__flink__078003756269.txt` | 3231464 |
| `apache__flink__079445374425.txt` | 3234002 |
| `apache__hugegraph__084221602296.txt` | 2339792 |
| `apache__hugegraph__086386091934.txt` | 3155231 |
| `apache__tika__090757115090.txt` | 4436178 |
| `apache__zeppelin__077616025677.txt` | 5235380 |
| `dask__distributed__084645769341.txt` | 509319 |
| `dask__distributed__084757793457.txt` | 1322948 |
| `fla-org__flash-linear-attention__082566635619.txt` | 68577 |
| `fla-org__flash-linear-attention__086098926451.txt` | 89645 |
| `floci-io__floci__078678232449.txt` | 640229 |
| `floci-io__floci__085018489189.txt` | 6944620 |
| `gurkenlabs__litiengine__079152380933.txt` | 50889 |
| `linkedin__brooklin__077863844421.txt` | 395685 |
| `nats-io__nats.java__080900237539.txt` | 742798 |
| `opentripplanner__opentripplanner__081988213338.txt` | 247584 |
| `opentripplanner__opentripplanner__092404918995.txt` | 526577 |
| `robo-code__robocode__084332182805.txt` | 187119 |
| `sirixdb__sirix__080642754882.txt` | 136296 |
| `sirixdb__sirix__092352347826.txt` | 80122 |
| `spiculedata__saiku__086592116219.txt` | 285783 |
| `thealgorithms__java__095336925353.txt` | 258721 |
| `unicode-org__cldr__090672967305.txt` | 543630 |
| `webauthn4j__webauthn4j__080348707704.txt` | 254970 |

**Exact count: 32.**

### 2. The 30-vs-32 discrepancy

**Neither "docs/HANDOFF-019.md reports 32" is accurate as stated, and this needs to be said
plainly rather than reconciled away.** `docs/HANDOFF-019.md` is 246 lines long and mentions
`holdout_v4` in exactly two places, both at lines 197–198, both in a "do not touch" list:

```
- Do not touch `docs/SCHEMAS.md`, `tests/fixtures/holdout_v3/` or
  `holdout_v4/`, `release/`, or the daemon. No new dependency.
```

**No fixture count for `holdout_v4` appears anywhere in `docs/HANDOFF-019.md`** — not as
"32", not as any other number, not in prose or a table. A full-file grep for `32`, `fixture`,
and `holdout` confirms this. The premise of the task as given is false on this point.

What **is** true, and is the actual discrepancy worth reporting: **Phase 020's own report**
(`docs/phase/020-parser-survey-REPORT.md`, line 279) states *"Measured across all 30
`holdout_v4` fixtures: parsers emit 47 outcomes."* The directory holds **32** files right now
(confirmed above). So the real gap is **30 (Phase 020) vs. 32 (now, this task)**, not
"32 (HANDOFF-019)".

**I cannot name the two specific files responsible for the gap.** Phase 020 names only 3
of its 30 fixtures by filename (the three defect-reproduction examples); it never enumerates
the other 27, so there is no per-filename list to diff against the current 32. What I *can*
report: re-running the full dispatcher against **all 32** files currently on disk (Phase 2,
below) yields **total_outcomes = 47** and **none_count = 1** — the identical totals Phase 020
reported for its 30. That is consistent with the 2 additional files each contributing zero
outcomes, but it is not proof of which 2 they are, and I am not asserting more than the
arithmetic supports. Six fixtures in the current set of 32 produce zero outcomes (Phase 3,
below); some subset of those six are plausibly the "extra" two, but which subset is not
determinable from the evidence available.

---

## PHASE 2 — The expectation table

### 4. Predictions, recorded before the extraction script was run

| Quantity | Predicted | Actual | Verdict |
|---|---|---|---|
| Number of fixtures | 32 | **32** | exact (already counted in Phase 1 before predicting) |
| Total outcomes emitted | 50 (scaled from Phase 020's 47/30 rate to 32 fixtures) | **47** | over by 3 — the 2 extra fixtures contributed 0 net outcomes, not a proportional share |
| Outcomes normalizing to `NONE` | 2 (scaled from Phase 020's 1/47) | **1** | over by 1 — same single `Gradle suite` case Phase 020 found; no new NONE cases among the added fixtures |

Both misses point the same direction: I assumed the 2 additional fixtures would contribute
proportionally to totals; they contributed nothing measurable. That's consistent with the
Phase 1 finding above (6 zero-outcome fixtures in the current 32; the "extra" fixtures beyond
Phase 020's 30 are plausibly among them).

### 5. The table

47 rows, one per outcome the dispatcher (`dispatch_parse_log_with_stats`) returned across all
32 fixtures. Columns exactly as specified: `RAW_LINE` is the verbatim source line(s), `HAND_EXPECTED`
is empty in every row.

**RAW_LINE formatting note**: cell text uses Python `repr()` of the exact line (so control
bytes such as ANSI escapes — `\x1b[31m` etc. — are visible as escape sequences rather than
executing/corrupting the table) and prefixes the 1-indexed source line number. This is a
*display* transform only — it does not add, remove, or reorder any byte of the underlying
line; it exists so the row renders as one table cell in Markdown.

**Predicted failure (a) — CONFIRMED, generalized beyond the hypothesis.** The hypothesis
named pytest specifically ("the parser retains only the capture group"). In fact **none of
the three parsers ever store a source line anywhere in a `TestOutcome`** — Maven and Gradle
discard `raw_line` at the end of each loop iteration, keeping only extracted tuples/strings;
pytest keeps only the regex capture group as `test_id`. For single-line-origin outcomes this
capture group happens to reconstruct almost the entire line, so RAW_LINE was recoverable by
re-observing the real parser's execution (not by reconstructing text) in **35 / 47** rows. In
the remaining **12 / 47** rows, the final `test_id` was assembled by the parser itself from
**two different source lines** (Gradle's Pass-1 stack-frame suffix join, 4 rows; Maven's
FORM-C/D cross-line FQCN join, 2 rows; pytest's progress+summary dedup-merge, 6 rows) — for
those, RAW_LINE reports **both** contributing lines labeled by role, per the instruction not
to synthesize a single line where none exists. No row was NOT RECOVERABLE — the tracer found
supporting line(s) for all 47.

Row 20 (`apache__hugegraph__084221602296.txt`, `org.apache.hugegraph.core#CoreTestSuite`) is
worth flagging for the operator's `HAND_EXPECTED` pass specifically: the source line is a
class-level JUnit `ERROR!` with no method (`org.apache.hugegraph.core.CoreTestSuite  Time
elapsed: 2.946 s  <<< ERROR!`), and FORM A's regex splits it at the last `.` regardless,
producing a `class#method` shape from what is actually a bare class failure. This is exactly
the Amendment-1 "class-only" shape the module's own docstring says should be dropped when
*unattached* — here it is not dropped because the regex greedily treats the trailing segment
as a method name. Not fixed here; flagged as ground-truth-relevant.

| # | fixture | RAW_LINE | PARSER_EMITTED | NORMALIZED | HAND_EXPECTED |
|---|---|---|---|---|---|
| 1 | `Stirling-Tools__Stirling-PDF__081016081705.txt` | L908: '2026-06-12T11:17:50.6211639Z UIDataControllerTest > getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical() FAILED' | `UIDataControllerTest#getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical()` | `UIDataControllerTest#getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical` |  |
| 2 | `Stirling-Tools__Stirling-PDF__081185748047.txt` | L576: '2026-06-13T11:09:29.5109777Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldCheckIfJobIsQueued() FAILED' | `JobQueueTest#shouldCheckIfJobIsQueued()` | `JobQueueTest#shouldCheckIfJobIsQueued` |  |
| 3 | `Stirling-Tools__Stirling-PDF__081185748047.txt` | L579: '2026-06-13T11:09:29.5110981Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldCancelJob() FAILED' | `JobQueueTest#shouldCancelJob()` | `JobQueueTest#shouldCancelJob` |  |
| 4 | `Stirling-Tools__Stirling-PDF__081185748047.txt` | L582: '2026-06-13T11:09:29.5112069Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldGetQueueStats() FAILED' | `JobQueueTest#shouldGetQueueStats()` | `JobQueueTest#shouldGetQueueStats` |  |
| 5 | `Stirling-Tools__Stirling-PDF__081185748047.txt` | L585: '2026-06-13T11:09:29.5112976Z [\x1b[33mbackend:build:ci\x1b[0m] JobQueueTest > shouldQueueJob() FAILED' | `JobQueueTest#shouldQueueJob()` | `JobQueueTest#shouldQueueJob` |  |
| 6 | `agno-agi__agno__079305370965.txt` | **NOT SINGLE-LINE** (2 lines matched this node id (progress+summary dedup-merge or timeout pairing); dict-overwrite keeps one canonical TestOutcome but multiple source lines contributed) — L2481: '2026-06-03T13:34:59.8448071Z libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer FAILED [ 12%]' <br> L10206: "2026-06-03T13:39:13.1733817Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'gpt2' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/openai-community/gpt2/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/gpt2/resolve/main/tokenizer.json: status code 429'}" | `libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer` | `libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer` |  |
| 7 | `agno-agi__agno__079305370965.txt` | **NOT SINGLE-LINE** (2 lines matched this node id (progress+summary dedup-merge or timeout pairing); dict-overwrite keeps one canonical TestOutcome but multiple source lines contributed) — L2482: '2026-06-03T13:34:59.9163951Z libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer FAILED [ 12%]' <br> L10207: "2026-06-03T13:39:13.1736939Z FAILED libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer - chonkie.tokenizer.InvalidTokenizerError: Tokenizer 'cl100k_base' could not be loaded: {'tokie (mapped)': 'failed to download tokenizer: request error: https://huggingface.co/Xenova/gpt-4/resolve/main/tokenizer.json: status code 429', 'tokie': 'failed to download tokenizer: request error: https://huggingface.co/cl100k_base/resolve/main/tokenizer.json: status code 429'}" | `libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer` | `libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer` |  |
| 8 | `agno-agi__agno__092042274925.txt` | L1250: "2026-08-04T15:29:41.6265273Z FAILED tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields - AttributeError: 'str' object has no attribute 'rating'" | `tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields` | `tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields` |  |
| 9 | `apache__atlas__085339439869.txt` | L1362: '2026-07-06T09:38:44.7360321Z [ERROR] org.apache.atlas.kafka.KafkaNotificationTest.setup -- Time elapsed: 17.90 s <<< FAILURE!' | `org.apache.atlas.kafka.KafkaNotificationTest#setup` | `org.apache.atlas.kafka.KafkaNotificationTest#setup` |  |
| 10 | `apache__beam__086101982024.txt` | L1093: '2026-07-09T11:09:03.8539833Z HadoopFormatIOCassandraTest > classMethod FAILED' | `HadoopFormatIOCassandraTest#classMethod` | `HadoopFormatIOCassandraTest#classMethod` |  |
| 11 | `apache__beam__086101982024.txt` | L1096: '2026-07-09T11:10:15.1523730Z HadoopFormatIOElasticTest > testHifIOWithElastic FAILED' | `HadoopFormatIOElasticTest#testHifIOWithElastic` | `HadoopFormatIOElasticTest#testHifIOWithElastic` |  |
| 12 | `apache__beam__086101982024.txt` | L1100: '2026-07-09T11:10:15.6517616Z HadoopFormatIOElasticTest > testHifIOWithElasticQuery FAILED' | `HadoopFormatIOElasticTest#testHifIOWithElasticQuery` | `HadoopFormatIOElasticTest#testHifIOWithElasticQuery` |  |
| 13 | `apache__beam__093527298308.txt` | L4633: '2026-08-10T17:18:38.4314148Z BigQueryMetastoreCatalogIT > testWrite FAILED' | `BigQueryMetastoreCatalogIT#testWrite` | `BigQueryMetastoreCatalogIT#testWrite` |  |
| 14 | `apache__beam__093527298308.txt` | L8479: '2026-08-10T17:31:48.9284336Z BigQueryMetastoreCatalogIT > testWriteRead FAILED' | `BigQueryMetastoreCatalogIT#testWriteRead` | `BigQueryMetastoreCatalogIT#testWriteRead` |  |
| 15 | `apache__beam__093527298308.txt` | L8788: '2026-08-10T17:40:41.8287404Z BigQueryMetastoreCatalogIT > testReadWriteStreaming FAILED' | `BigQueryMetastoreCatalogIT#testReadWriteStreaming` | `BigQueryMetastoreCatalogIT#testReadWriteStreaming` |  |
| 16 | `apache__beam__093527298308.txt` | L8972: '2026-08-10T17:48:56.7296640Z BigQueryMetastoreCatalogIT > testStreamToPartitionedDynamicDestinations FAILED' | `BigQueryMetastoreCatalogIT#testStreamToPartitionedDynamicDestinations` | `BigQueryMetastoreCatalogIT#testStreamToPartitionedDynamicDestinations` |  |
| 17 | `apache__dolphinscheduler__092883042571.txt` | **NOT SINGLE-LINE** (FORM C emission line (simple class#method) + FORM B line supplying the FQCN used in the cross-line join) — L2464: '2026-08-07T13:46:49.9368742Z [ERROR]   DolphinDBDataSourceE2ETest.testCreateDolphinDBDataSource:79 » NoSuchElement no...' <br> L2438: '2026-08-07T13:46:49.6025516Z [ERROR] Tests run: 2, Failures: 0, Errors: 1, Skipped: 1, Time elapsed: 97.179 s <<< FAILURE! - in org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest' | `org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest#testCreateDolphinDBDataSource` | `org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest#testCreateDolphinDBDataSource` |  |
| 18 | `apache__flink__078003756269.txt` | L26441: '2026-05-27T04:04:44.4971975Z May 27 04:04:44 04:04:44.495 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 2.485 s <<< FAILURE!' | `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate` | `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate` |  |
| 19 | `apache__flink__079445374425.txt` | L26465: '2026-06-04T04:09:23.4243464Z Jun 04 04:09:23 04:09:23.422 [ERROR] org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase.testRuntimeRestApiDocsUpToDate(Path) -- Time elapsed: 1.690 s <<< FAILURE!' | `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate` | `org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate` |  |
| 20 | `apache__hugegraph__084221602296.txt` | L14455: '2026-06-30T06:02:25.8950390Z [ERROR] org.apache.hugegraph.core.CoreTestSuite  Time elapsed: 2.946 s  <<< ERROR!' | `org.apache.hugegraph.core#CoreTestSuite` | `org.apache.hugegraph.core#CoreTestSuite` |  |
| 21 | `apache__hugegraph__084221602296.txt` | **NOT SINGLE-LINE** (FORM C emission line (simple class#method) + FORM B line supplying the FQCN used in the cross-line join) — L14534: "2026-06-30T06:02:26.2679783Z [ERROR]   CoreTestSuite.init:98 » Huge Failed to listen 'HUGEGRAPH/hg/EVENT/GRAPH/SCHEMA..." <br> L14454: '2026-06-30T06:02:25.8930403Z [ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 2.946 s <<< FAILURE! - in org.apache.hugegraph.core.CoreTestSuite' | `org.apache.hugegraph.core.CoreTestSuite#init` | `org.apache.hugegraph.core.CoreTestSuite#init` |  |
| 22 | `apache__hugegraph__086386091934.txt` | L20801: '2026-07-10T14:56:51.4090752Z [ERROR] testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.249 s  <<< FAILURE!' | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError` | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError` |  |
| 23 | `apache__hugegraph__086386091934.txt` | L20805: '2026-07-10T14:56:51.4099617Z [ERROR] testUnsetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.22 s  <<< FAILURE!' | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphReturnsFriendlyError` | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphReturnsFriendlyError` |  |
| 24 | `apache__hugegraph__086386091934.txt` | L20809: '2026-07-10T14:56:51.4105732Z [ERROR] testSetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.227 s  <<< FAILURE!' | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphReturnsFriendlyError` | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphReturnsFriendlyError` |  |
| 25 | `apache__hugegraph__086386091934.txt` | L20813: '2026-07-10T14:56:51.4111044Z [ERROR] testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.224 s  <<< FAILURE!' | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError` | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError` |  |
| 26 | `apache__hugegraph__086386091934.txt` | L20817: '2026-07-10T14:56:51.4116484Z [ERROR] testGetDefaultGraphReturnsFriendlyError(org.apache.hugegraph.api.GraphsApiStandaloneTest)  Time elapsed: 0.027 s  <<< FAILURE!' | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testGetDefaultGraphReturnsFriendlyError` | `org.apache.hugegraph.api.GraphsApiStandaloneTest#testGetDefaultGraphReturnsFriendlyError` |  |
| 27 | `apache__zeppelin__077616025677.txt` | L35269: '2026-05-24T18:24:22.9212470Z [ERROR] org.apache.zeppelin.rest.InterpreterRestApiTest.testCreatedInterpreterDependencies -- Time elapsed: 0.017 s <<< FAILURE!' | `org.apache.zeppelin.rest.InterpreterRestApiTest#testCreatedInterpreterDependencies` | `org.apache.zeppelin.rest.InterpreterRestApiTest#testCreatedInterpreterDependencies` |  |
| 28 | `dask__distributed__084645769341.txt` | **NOT SINGLE-LINE** (2 lines matched this node id (progress+summary dedup-merge or timeout pairing); dict-overwrite keeps one canonical TestOutcome but multiple source lines contributed) — L3756: '2026-07-01T22:02:10.3797799Z distributed/tests/test_nanny.py::test_failure_during_worker_initialization[45-100] \x1b[31mFAILED\x1b[0m\x1b[31m [ 45%]\x1b[0m' <br> L4015: '2026-07-01T22:02:54.1287396Z \x1b[31mFAILED\x1b[0m distributed/tests/test_nanny.py::\x1b[1mtest_failure_during_worker_initialization[45-100]\x1b[0m - TimeoutError: Test timeout (30) hit after 30.000552999999968s.' | `distributed/tests/test_nanny.py::test_failure_during_worker_initialization[45-100]` | `distributed/tests/test_nanny.py::test_failure_during_worker_initialization` |  |
| 29 | `dask__distributed__084757793457.txt` | **NOT SINGLE-LINE** (2 lines matched this node id (progress+summary dedup-merge or timeout pairing); dict-overwrite keeps one canonical TestOutcome but multiple source lines contributed) — L3728: '2026-07-02T11:27:28.6182458Z distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100] \x1b[31mFAILED\x1b[0m\x1b[31m [  8%]\x1b[0m' <br> L10792: '2026-07-02T12:00:40.2795756Z \x1b[31mFAILED\x1b[0m distributed/tests/test_active_memory_manager.py::\x1b[1mtest_RetireWorker_stress[False-17-100]\x1b[0m - TimeoutError: Test timeout (180) hit after 179.9853481s.' | `distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress[False-17-100]` | `distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress` |  |
| 30 | `fla-org__flash-linear-attention__082566635619.txt` | **NOT SINGLE-LINE** (2 lines matched this node id (progress+summary dedup-merge or timeout pairing); dict-overwrite keeps one canonical TestOutcome but multiple source lines contributed) — L593: '2026-06-21T11:35:36.7113481Z tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] FAILED' <br> L709: '2026-06-21T11:35:36.7152616Z FAILED tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] - RuntimeError: No CUDA GPUs are available' | `tests/models/test_modeling_forgetting_transformer.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16]` | `tests/models/test_modeling_forgetting_transformer.py::test_modeling` |  |
| 31 | `fla-org__flash-linear-attention__086098926451.txt` | **NOT SINGLE-LINE** (2 lines matched this node id (progress+summary dedup-merge or timeout pairing); dict-overwrite keeps one canonical TestOutcome but multiple source lines contributed) — L650: '2026-07-09T10:42:18.0395527Z tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16] FAILED' <br> L779: "2026-07-09T10:42:18.0446013Z FAILED tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16] - TypeError: Can't instantiate abstract class FLALayer without an implementation for abstract method 'get_max_length'" | `tests/models/test_modeling_comba.py::test_generation[L2-B4-T2000-H8-D64-torch.float16]` | `tests/models/test_modeling_comba.py::test_generation` |  |
| 32 | `floci-io__floci__085018489189.txt` | L9808: '2026-07-03T14:22:14.0339511Z [ERROR] io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest.describeDefaultVpc -- Time elapsed: 0.025 s <<< FAILURE!' | `io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest#describeDefaultVpc` | `io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest#describeDefaultVpc` |  |
| 33 | `gurkenlabs__litiengine__079152380933.txt` | L554: '2026-06-02T19:15:25.8858314Z AlignTests > getClampedLocation_InPoint() FAILED' | `AlignTests#getClampedLocation_InPoint()` | `AlignTests#getClampedLocation_InPoint` |  |
| 34 | `gurkenlabs__litiengine__079152380933.txt` | L557: '2026-06-02T19:15:25.8860406Z AlignTests > getClampedLocation_OffPoint() FAILED' | `AlignTests#getClampedLocation_OffPoint()` | `AlignTests#getClampedLocation_OffPoint` |  |
| 35 | `linkedin__brooklin__077863844421.txt` | L3577: '2026-05-26T13:05:09.6365165Z Gradle suite > Gradle test > com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation FAILED' | `Gradle suite#com.linkedin.datastream.server.TestCoordinator.testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation` | `NONE` |  |
| 36 | `nats-io__nats.java__080900237539.txt` | **NOT SINGLE-LINE** (emission line (S3/S4, bare/simple class); stack-trace 'at' frame supplying the FQCN used in the Pass-1 suffix join) — L3033: '2026-06-11T20:42:58.2319604Z ConsumerConfigurationTests > testBuilder() FAILED' <br> L3041: '2026-06-11T20:42:58.2327031Z         at io.nats.client.api.ConsumerConfigurationTests.testBuilder(ConsumerConfigurationTests.java:172)' | `io.nats.client.api.ConsumerConfigurationTests#testBuilder()` | `io.nats.client.api.ConsumerConfigurationTests#testBuilder` |  |
| 37 | `nats-io__nats.java__080900237539.txt` | **NOT SINGLE-LINE** (emission line (S3/S4, bare/simple class); stack-trace 'at' frame supplying the FQCN used in the Pass-1 suffix join) — L5704: '2026-06-11T20:44:54.8318517Z SimplificationTests > testReconnectOverOrdered() FAILED' <br> L5712: '2026-06-11T20:44:54.8326421Z         at io.nats.client.impl.SimplificationTests.testReconnectOverOrdered(SimplificationTests.java:1897)' | `io.nats.client.impl.SimplificationTests#testReconnectOverOrdered()` | `io.nats.client.impl.SimplificationTests#testReconnectOverOrdered` |  |
| 38 | `robo-code__robocode__084332182805.txt` | L500: '2026-06-30T15:36:20.9720512Z TestFairPlay > run FAILED' | `TestFairPlay#run` | `TestFairPlay#run` |  |
| 39 | `sirixdb__sirix__080642754882.txt` | L1319: "2026-06-10T19:16:20.6268645Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'" | `sirix-python-client/tests/test_sirix_async.py::test_database_create` | `sirix-python-client/tests/test_sirix_async.py::test_database_create` |  |
| 40 | `sirixdb__sirix__080642754882.txt` | L1322: "2026-06-10T19:16:20.6271210Z FAILED sirix-python-client/tests/test_sirix_async.py::test_database_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'" | `sirix-python-client/tests/test_sirix_async.py::test_database_delete` | `sirix-python-client/tests/test_sirix_async.py::test_database_delete` |  |
| 41 | `sirixdb__sirix__080642754882.txt` | L1325: "2026-06-10T19:16:20.6274000Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_create - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'" | `sirix-python-client/tests/test_sirix_sync.py::test_create` | `sirix-python-client/tests/test_sirix_sync.py::test_create` |  |
| 42 | `sirixdb__sirix__080642754882.txt` | L1328: "2026-06-10T19:16:20.6276807Z FAILED sirix-python-client/tests/test_sirix_sync.py::test_delete - pysirix.errors.SirixServerError: Server error '500 Internal Server Error' for url 'http://localhost:9443/First'" | `sirix-python-client/tests/test_sirix_sync.py::test_delete` | `sirix-python-client/tests/test_sirix_sync.py::test_delete` |  |
| 43 | `sirixdb__sirix__092352347826.txt` | L384: '2026-08-05T15:30:56.2947870Z RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable() FAILED' | `RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable()` | `RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable` |  |
| 44 | `sirixdb__sirix__092352347826.txt` | L387: '2026-08-05T15:30:57.7205480Z RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass() FAILED' | `RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass()` | `RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass` |  |
| 45 | `unicode-org__cldr__090672967305.txt` | L6090: '2026-07-29T19:01:50.5670322Z [ERROR] org.unicode.cldr.unittest.TestShim.TestAll -- Time elapsed: 1484 s <<< FAILURE!' | `org.unicode.cldr.unittest.TestShim#TestAll` | `org.unicode.cldr.unittest.TestShim#TestAll` |  |
| 46 | `webauthn4j__webauthn4j__080348707704.txt` | **NOT SINGLE-LINE** (emission line (S3/S4, bare/simple class); stack-trace 'at' frame supplying the FQCN used in the Pass-1 suffix join) — L1832: '2026-06-09T14:35:50.7781357Z EC2COSEKeyTest > json_serialize_deserialize_test() FAILED' <br> L1847: '2026-06-09T14:35:50.7805802Z         at app//com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest.json_serialize_deserialize_test(EC2COSEKeyTest.java:130)' | `com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest#json_serialize_deserialize_test()` | `com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest#json_serialize_deserialize_test` |  |
| 47 | `webauthn4j__webauthn4j__080348707704.txt` | **NOT SINGLE-LINE** (emission line (S3/S4, bare/simple class); stack-trace 'at' frame supplying the FQCN used in the Pass-1 suffix join) — L1917: '2026-06-09T14:35:52.1721696Z RSACOSEKeyTest > json_serialize_deserialize_test() FAILED' <br> L1932: '2026-06-09T14:35:52.1741411Z         at app//com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest.json_serialize_deserialize_test(RSACOSEKeyTest.java:116)' | `com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest#json_serialize_deserialize_test()` | `com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest#json_serialize_deserialize_test` |  |

---

## PHASE 3 — Coverage check

### 5. Fixtures producing outcomes vs. zero

- Fixtures that produced **at least one outcome: 26 / 32**.
- Fixtures that produced **zero outcomes: 6 / 32**.

The 6 zero-outcome fixtures, with their `classify_log_format` result and
`classify_dispatch_log` classification (both from the real, unmodified `dispatch.py`):

| Fixture | `classify_log_format` | `classify_dispatch_log` |
|---|---|---|
| `apache__tika__090757115090.txt` | `maven` | `TEST_RAN_CLEAN` |
| `floci-io__floci__078678232449.txt` | `unknown` | `NO_TEST_OUTPUT` |
| `opentripplanner__opentripplanner__081988213338.txt` | `maven` | `TEST_RAN_CLEAN` |
| `opentripplanner__opentripplanner__092404918995.txt` | `maven` | `TEST_RAN_CLEAN` |
| `spiculedata__saiku__086592116219.txt` | `maven` | `TEST_RAN_CLEAN` |
| `thealgorithms__java__095336925353.txt` | `maven` | `TEST_RAN_CLEAN` |

**5 of the 6 are distinguishable as clean logs, not misses**: `classify_dispatch_log` reports
`TEST_RAN_CLEAN` for all 5 Maven ones — each matched Maven's `_CLEAN_TEST_RE` ("Tests run: N,
Failures: 0, Errors: 0") with no `[ERROR]`/`<<<` failure line anywhere in the file, so a zero
count there is the expected output of a genuinely green run, not evidence of a parser gap.

**The 6th, `floci-io__floci__078678232449.txt`, is the one predicted-failure (b) actually
describes, though not exactly as hypothesized.** Hypothesis (b) predicted "some fixtures
classify to a harness with no parser." That's not quite what happens — `classify_log_format`
returns `unknown`, which *is* a defined outcome with defined (empty) handling in
`dispatch.py`, not a harness lacking a parser. Inspecting the file directly (byte 1–15 and a
sample past byte 500 of the raw text) shows why: it is a GitHub Actions **runner
provisioning / Docker buildx setup log** — runner image info, OS version, a JSON blob of
Docker builder disk stats — and never reaches a test-framework invocation at all. It contains
no Maven/Gradle/pytest lifecycle marker because no test framework ever ran in this log
capture. So this is neither "a clean log" nor "a total parser miss" in the sense the task's
framing poses the question — it's a third case the framing didn't anticipate: **the captured
log segment never contains a test run to miss.** Whether the actual test-run log for that job
exists in a different log segment/artifact is outside what this file alone can answer.

### My own predicted failure, per the task's request for one

**(c) The zero-outcome count is dominated by one format, not spread evenly.** 5 of 6
zero-outcome fixtures are Maven; 0 are Gradle; 0 are pytest; 1 is `unknown`. Given the
dispatcher runs 3 independent single-format parsers plus an `ambiguous` union path, a naive
prior would spread zero-outcome fixtures roughly evenly across formats. They don't — every
Maven zero-outcome fixture verified as `TEST_RAN_CLEAN` via `_CLEAN_TEST_RE`, meaning Maven's
clean-run detection regex is doing real, load-bearing work in this holdout set specifically;
Gradle and pytest's zero-outcome fixtures (if any exist beyond this 32-fixture set) are
untested by this sample.

---

## Summary

1. Fixture count is **32**, not 30 (Phase 020) or a "32" HANDOFF-019 never states.
2. Total outcomes across all 32: **47**. `NONE` after `normalize_test_id()`: **1** (the same
   `Gradle suite` case Phase 020 found). Both figures are identical to Phase 020's reported
   30-fixture totals — the 2 additional fixtures net zero outcomes, but which 2 they are is
   not determinable from Phase 020's report (it never lists its 30 by name).
3. RAW_LINE is genuinely not a single line for 12 / 47 outcomes — this is a structural
   property of how Maven's FORM-C/D reconciliation and Gradle's Pass-1 stack-suffix join and
   pytest's progress/summary dedup-merge work, not a limitation of this extraction. All 12
   are reported as two labeled, verbatim lines rather than one synthesized line.
4. 26 / 32 fixtures yield ≥1 outcome; 6 / 32 yield zero. 5 of those 6 are provably clean runs
   (`TEST_RAN_CLEAN`); the 6th never contains a test-framework invocation at all (a runner
   provisioning log), which is a third category the task's own two-way framing
   (clean vs. miss) doesn't cover.
5. `HAND_EXPECTED` is empty in all 47 rows, as instructed.

**Nothing was changed. Nothing was committed.**
