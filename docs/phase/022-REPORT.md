# Phase 022 — Provenance Correction, Class-Level Ruling, and the Parser Regression Harness

**Scope honoured**: Nothing under `src/` was read-modified — `src/` was read only. No parser
was fixed. `docs/SCHEMAS.md`, `docs/phase/021-expectation-table.md`,
`docs/phase/012B-holdout-v4-worksheet.md`, and `docs/TASKS.md` were not edited. Nothing was
wired into `make tables` or `make test`. No `git add`, no `git commit`. No HTTP. Nothing
backgrounded, nohup'd, setsid'd, or delegated to a subagent.

**Files changed (3)**:

| File | Change |
|---|---|
| `docs/phase/021B-blind-worksheet.md` | +5 lines (provenance paragraph), 1 line changed (row `6a5fd9d35a1f` HAND_EXPECTED) |
| `docs/DECISIONS.md` | +16 lines (D-46 appended) |
| `tests/test_parser_regression.py` | new, 228 lines |

Plus this report. Test count, both measured, not inferred: **before** —
`uv run pytest -q --tb=no --ignore=tests/test_parser_regression.py` → `411 passed, 1 skipped
in 54.27s`; **after** — `uv run pytest -q --tb=no` → `455 passed, 1 skipped, 3 xfailed in
61.46s`. The +44 passed and all 3 xfails are this task's; the suite had no xfails before it.

---

## THE ONE DEVIATION — step 6's STOP fired, and the operator ruled

Step 6 said: *"verify the last record is D-44 before appending and STOP if it is not."*

**It is not.** `docs/DECISIONS.md` already ends at **D-45 — Secret-scan severity tiering**,
committed in `39839fd` (`fix: require a parsed base log before calling a base run green`),
the most recent commit touching that file. I stopped and asked rather than renumbering or
overwriting. The operator ruled: **append as D-46, leave the secret-scan record untouched**.

Consequences applied throughout:

- The class-level ruling is recorded as **D-46**, text otherwise verbatim.
- The row `6a5fd9d35a1f` HAND_EXPECTED string reads `(D-46)`, not `(D-45)`.
- The xfail reason for `6a5fd9d35a1f` names D-46.

`D-21` was verified **RESERVED and absent** — it appears nowhere in `docs/DECISIONS.md`,
neither in the D-01…D-31 summary table nor among the prose records. Not filled, not
renumbered. (`D-33` is likewise absent; unremarked here, outside scope.)

---

## PHASE 0 — Guard and orient

```
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15
```

```
$ git status --porcelain
?? analysis/expectation_diff.py
?? docs/phase/020-parser-survey-REPORT.md
?? docs/phase/021-expectation-table.md
?? docs/phase/021B-REPORT.md
?? docs/phase/021B-blind-worksheet.md
?? docs/phase/021C-REPORT.md
?? release/
?? tests/fixtures/holdout_v4/
?? vendor/graphify-br/
```

### What the three documents require of this task

**`docs/AGENT_RULES.md`** — Two rules bind the shape of this task directly. *"Prose is not
evidence"*: every command's raw output is pasted below, prediction before actual. *"When the
instructions are wrong… REPORT IT and stop. Do not silently work around it"* — which is
exactly what step 6's D-45 collision triggered.
It also forbids heredoc file writes and root-level throwaway scripts; the probe and the
strict-xfail demo both live under the session scratchpad and are not in the tree. **One
rule was not satisfied and I am flagging it rather than acting unilaterally**: AGENT_RULES
requires a `docs/session/NNN-…md` entry plus a `docs/HANDOFF.md` append per task, but this
task named `docs/phase/022-REPORT.md` as its single deliverable and its NON-GOALS list is
explicit. I wrote only the named file. If the session/HANDOFF pair is wanted, it is a
one-command follow-up.

**ROADMAP §9.1 (T1.1)** — Requires a hand-labelled fixture corpus and, in subtask 2, *"target
≥95% precision on test-name extraction."* This harness deliberately does **not** discharge
that clause: the 021B corpus is fitted, not blind, and yields no precision figure. §9.1
subtask 5's *"Publish the number honestly"* is what makes that distinction load-bearing —
reporting 44/47 as precision would be reporting the parser's agreement with itself.

**ROADMAP §21.3** — Governs base-run resolution, and its central warning is the reason D-46
forbids silent deletion: *"An empty base failure set must never be read as 'base was green'…
The single most dangerous bug in the labelling engine. It manufactures false positives at
scale."* A class-level event that is dropped without a counter is exactly that failure mode
one layer upstream — the brooklin D2 case proves a discarded outcome leaves no trace.

### TASKS.md divergence (reported, not edited — TASKS.md is rank 4 and known stale)

Current recorded state of T1.1:

```
- [x] `T1.1a` Build 40-log fixture corpus with hand-labelled expected output
- [x] `T1.1b` `annotations.py` parser
- [x] `T1.1c` `junit_xml.py` parser (Surefire + pytest)
- [x] `T1.1d` `log_pytest.py` parser
- [x] `T1.1e` `log_maven.py` parser
- [x] `T1.1f` `log_gradle.py` parser
- [x] `T1.1g` `normalize_test_id()` extending graphify `ids.py` + contract test ⭐
- [ ] `T1.1h` `resolve_test_file()` + binding-rate report ⭐
- [ ] `T1.1i` Per-parser coverage + precision report
```

It **does not match** what Phases 020 and 021 found. Five divergences:

1. **`T1.1e` and `T1.1f` are ticked `[x]` while carrying confirmed, reproduced defects.**
   Phase 020 §D2 confirms the Gradle chevron defect *"REPRODUCES"* and is *"silent data
   loss, not a corrupt key"*; §D3 confirms the package-drop defect reproduces and is *"the
   largest defect. 2,067 / 5,144 distinct Java ids are bare-class."* Two `[x]` marks sit on
   parsers with open, quantified correctness defects.
   *(Correction: Bare-class Java ids 2,067 / 5,144 is superseded by **2,043 / 5,115** per Phase 023 consolidation).*
2. **`T1.1a` claims a "40-log fixture corpus with hand-labelled expected output."** The
   corpus that actually exists for this work is `tests/fixtures/holdout_v4/` at **32
   fixtures / 47 rows**, and — per the correction applied in Phase 1 below — its labels were
   not hand-written by a human. The tick overstates both the count and the provenance.
3. **`T1.1b` `annotations.py` and `T1.1c` `junit_xml.py` are ticked, but neither file exists.**
   `ls src/parse/` shows `changeset.py dispatch.py log_gradle.py log_maven.py log_pytest.py
   outcome.py test_files.py test_ids.py` and nothing else. Two ticked subtasks have no
   implementation in the tree.
4. **`T1.1i` "per-parser coverage + precision report" is `[ ]`, which is correct but for the
   wrong reason** — TASKS.md reads as though it is merely pending. Phase 021B/021C establish
   that the only assembled corpus *cannot* produce the precision half of it at all. The
   blocker is corpus provenance, not effort.
5. **`src/parse/dispatch.py` — the content-signature cascade the whole parser layer routes
   through — has no subtask line at all.** It is neither ticked nor pending; it is unlisted.

No edit made. Recorded here for whoever reconciles TASKS.md.

---

## PHASE 1 — Provenance correction

Appended verbatim under the existing `## KNOWN LIMITATION` heading in
`docs/phase/021B-blind-worksheet.md`, as a new paragraph directly after the existing
fitted-corpus paragraph:

```
This worksheet was filled by the coding agent, not by the operator. The agent generated
the underlying table and had all 47 parser outputs in context while filling. Agreement rows
are therefore self-agreement and carry no evidential weight. Only disagreement rows are
evidence. This corpus is a regression fixture and yields no precision figure.
```

Nothing else in the file was touched at this step. No `row_key`, no evidence block, no other
`HAND_EXPECTED`. The paragraph sits above the first `## Row` header, so it is outside every
section body and cannot perturb `parse_worksheet`'s recompute-and-crosscheck of any row_key —
confirmed by the fact that all 47 keys still verified on the next run.

---

## PHASE 2 — D-46 recorded

Appended to `docs/DECISIONS.md`, after the existing D-45, with the file's `### D-NN: Title`
heading convention and the ruling text verbatim apart from the identifier substitution
`D-45` → `D-46`:

```
### D-46: Class-level failure events are not test ids, and are counted rather than dropped silently

D-46 — Class-level failure events are not test ids, and are counted rather than dropped
silently. A CI failure that names a class with no source-level method — a Maven class-level
`<<< ERROR!` line, or JUnit4's synthetic `classMethod` descriptor for a @BeforeClass /
@AfterClass failure — describes a fixture or suite failure, not a test. Emitting it as
<class>#<method> manufactures an identifier that names no source symbol, can never bind, and
fragments the join key. Such events MUST NOT be emitted as a test_id. They MUST be counted
and the count reported on every parse run; silent deletion is forbidden, because the
brooklin `Gradle suite` defect showed that a discarded outcome leaves no trace and is
therefore undetectable. Distinguishing rule: a method-position token is legitimate if it
names a developer-written source symbol (setup, init, run, TestAll all do); it is not
legitimate if the test framework synthesised it (classMethod does not). Revisit trigger: a
framework is added whose synthetic descriptors are not enumerable.
```

No existing record was renumbered, reworded, or touched.

---

## PHASE 3 — The ruling applied to row `6a5fd9d35a1f`

Baseline before the edit, for the one row (raw):

```
row_key=6a5fd9d35a1f fixture=apache__beam__086101982024.txt HAND_EXPECTED='HadoopFormatIOCassandraTest#classMethod' NORMALIZED='HadoopFormatIOCassandraTest#classMethod' verdict=AGREE CONTESTED
```

Changed to:

```
HAND_EXPECTED: NO_TEST - JUnit4 synthetic classMethod descriptor for a class-level @BeforeClass / @AfterClass failure; names no source method (D-46)
```

### Predicted vs actual

```
DISAGREE            predicted 3   actual 3
AGREE               predicted 44  actual 44
AGREE-ON-CONTESTED  predicted 19  actual 19
```

Reasoning behind the prediction, stated before the run: the row was `AGREE CONTESTED` at
baseline (45/2/20), and `is_contested()` flags it twice over — `classMethod` is in
`_CONTESTED_METHOD_NAMES`, and `HadoopFormatIOCassandraTest` has no `.`. Flipping it to
`NO_TEST` prose moves exactly one row from the AGREE column to DISAGREE and removes exactly
one from AGREE-ON-CONTESTED.

### `$ uv run python analysis/expectation_diff.py`

```
row_key=015d3b2416a0 fixture=dask__distributed__084757793457.txt HAND_EXPECTED='distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress' NORMALIZED='distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress' verdict=AGREE
row_key=068f9bb711d8 fixture=unicode-org__cldr__090672967305.txt HAND_EXPECTED='org.unicode.cldr.unittest.TestShim#TestAll' NORMALIZED='org.unicode.cldr.unittest.TestShim#TestAll' verdict=AGREE CONTESTED
row_key=0b1dcde22361 fixture=apache__dolphinscheduler__092883042571.txt HAND_EXPECTED='org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest#testCreateDolphinDBDataSource' NORMALIZED='org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest#testCreateDolphinDBDataSource' verdict=AGREE
row_key=0e5d3a59b174 fixture=robo-code__robocode__084332182805.txt HAND_EXPECTED='TestFairPlay#run' NORMALIZED='TestFairPlay#run' verdict=AGREE CONTESTED
row_key=185149df8b18 fixture=apache__zeppelin__077616025677.txt HAND_EXPECTED='org.apache.zeppelin.rest.InterpreterRestApiTest#testCreatedInterpreterDependencies' NORMALIZED='org.apache.zeppelin.rest.InterpreterRestApiTest#testCreatedInterpreterDependencies' verdict=AGREE
row_key=1b4f2d40df89 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='JobQueueTest#shouldQueueJob' NORMALIZED='JobQueueTest#shouldQueueJob' verdict=AGREE CONTESTED
row_key=2598cf91f544 fixture=sirixdb__sirix__092352347826.txt HAND_EXPECTED='RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable' NORMALIZED='RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable' verdict=AGREE CONTESTED
row_key=2724bcfc3dff fixture=nats-io__nats.java__080900237539.txt HAND_EXPECTED='io.nats.client.api.ConsumerConfigurationTests#testBuilder' NORMALIZED='io.nats.client.api.ConsumerConfigurationTests#testBuilder' verdict=AGREE
row_key=2bec1480577b fixture=apache__hugegraph__084221602296.txt HAND_EXPECTED='org.apache.hugegraph.core.CoreTestSuite#init' NORMALIZED='org.apache.hugegraph.core.CoreTestSuite#init' verdict=AGREE CONTESTED
row_key=3269f76d726f fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='sirix-python-client/tests/test_sirix_sync.py::test_create' NORMALIZED='sirix-python-client/tests/test_sirix_sync.py::test_create' verdict=AGREE
row_key=36ea4df7a8e6 fixture=apache__flink__079445374425.txt HAND_EXPECTED='org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate' NORMALIZED='org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate' verdict=AGREE
row_key=3f74c8efd8d5 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError' verdict=AGREE
row_key=4ca072d0ebcf fixture=gurkenlabs__litiengine__079152380933.txt HAND_EXPECTED='AlignTests#getClampedLocation_InPoint' NORMALIZED='AlignTests#getClampedLocation_InPoint' verdict=AGREE CONTESTED
row_key=4d25554936d1 fixture=dask__distributed__084645769341.txt HAND_EXPECTED='distributed/tests/test_nanny.py::test_failure_during_worker_initialization' NORMALIZED='distributed/tests/test_nanny.py::test_failure_during_worker_initialization' verdict=AGREE
row_key=51208f55ec56 fixture=apache__beam__086101982024.txt HAND_EXPECTED='HadoopFormatIOElasticTest#testHifIOWithElasticQuery' NORMALIZED='HadoopFormatIOElasticTest#testHifIOWithElasticQuery' verdict=AGREE CONTESTED
row_key=561a20998890 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError' verdict=AGREE
row_key=57e11a35966e fixture=apache__hugegraph__084221602296.txt HAND_EXPECTED='NO_TEST - class-level suite error; the line names only the class org.apache.hugegraph.core.CoreTestSuite and no test method' NORMALIZED='org.apache.hugegraph.core#CoreTestSuite' verdict=DISAGREE
row_key=5ce7156d4c23 fixture=apache__atlas__085339439869.txt HAND_EXPECTED='org.apache.atlas.kafka.KafkaNotificationTest#setup' NORMALIZED='org.apache.atlas.kafka.KafkaNotificationTest#setup' verdict=AGREE CONTESTED
row_key=63351e37b366 fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='sirix-python-client/tests/test_sirix_async.py::test_database_delete' NORMALIZED='sirix-python-client/tests/test_sirix_async.py::test_database_delete' verdict=AGREE
row_key=6a5fd9d35a1f fixture=apache__beam__086101982024.txt HAND_EXPECTED='NO_TEST - JUnit4 synthetic classMethod descriptor for a class-level @BeforeClass / @AfterClass failure; names no source method (D-46)' NORMALIZED='HadoopFormatIOCassandraTest#classMethod' verdict=DISAGREE CONTESTED
row_key=6d271ffe6080 fixture=Stirling-Tools__Stirling-PDF__081016081705.txt HAND_EXPECTED='UIDataControllerTest#getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical' NORMALIZED='UIDataControllerTest#getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical' verdict=AGREE CONTESTED
row_key=6e0955e465d6 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphReturnsFriendlyError' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphReturnsFriendlyError' verdict=AGREE
row_key=7a18936bd0b6 fixture=webauthn4j__webauthn4j__080348707704.txt HAND_EXPECTED='com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest#json_serialize_deserialize_test' NORMALIZED='com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest#json_serialize_deserialize_test' verdict=AGREE
row_key=7a69e71e197c fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphReturnsFriendlyError' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphReturnsFriendlyError' verdict=AGREE
row_key=80b12bf4ef69 fixture=apache__beam__093527298308.txt HAND_EXPECTED='BigQueryMetastoreCatalogIT#testWriteRead' NORMALIZED='BigQueryMetastoreCatalogIT#testWriteRead' verdict=AGREE CONTESTED
row_key=819c2f5d708c fixture=webauthn4j__webauthn4j__080348707704.txt HAND_EXPECTED='com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest#json_serialize_deserialize_test' NORMALIZED='com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest#json_serialize_deserialize_test' verdict=AGREE
row_key=83a64a4e66bd fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='JobQueueTest#shouldGetQueueStats' NORMALIZED='JobQueueTest#shouldGetQueueStats' verdict=AGREE CONTESTED
row_key=8aabd9035ed4 fixture=apache__beam__093527298308.txt HAND_EXPECTED='BigQueryMetastoreCatalogIT#testWrite' NORMALIZED='BigQueryMetastoreCatalogIT#testWrite' verdict=AGREE CONTESTED
row_key=906fd9b5040d fixture=floci-io__floci__085018489189.txt HAND_EXPECTED='io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest#describeDefaultVpc' NORMALIZED='io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest#describeDefaultVpc' verdict=AGREE
row_key=9ad2fff53c74 fixture=sirixdb__sirix__092352347826.txt HAND_EXPECTED='RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass' NORMALIZED='RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass' verdict=AGREE CONTESTED
row_key=9be730822015 fixture=gurkenlabs__litiengine__079152380933.txt HAND_EXPECTED='AlignTests#getClampedLocation_OffPoint' NORMALIZED='AlignTests#getClampedLocation_OffPoint' verdict=AGREE CONTESTED
row_key=9e4d4bd8e591 fixture=apache__beam__086101982024.txt HAND_EXPECTED='HadoopFormatIOElasticTest#testHifIOWithElastic' NORMALIZED='HadoopFormatIOElasticTest#testHifIOWithElastic' verdict=AGREE CONTESTED
row_key=a235cadb12ea fixture=agno-agi__agno__079305370965.txt HAND_EXPECTED='libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer' NORMALIZED='libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer' verdict=AGREE
row_key=b0980797f104 fixture=fla-org__flash-linear-attention__082566635619.txt HAND_EXPECTED='tests/models/test_modeling_forgetting_transformer.py::test_modeling' NORMALIZED='tests/models/test_modeling_forgetting_transformer.py::test_modeling' verdict=AGREE
row_key=b9184834c4c8 fixture=nats-io__nats.java__080900237539.txt HAND_EXPECTED='io.nats.client.impl.SimplificationTests#testReconnectOverOrdered' NORMALIZED='io.nats.client.impl.SimplificationTests#testReconnectOverOrdered' verdict=AGREE
row_key=bc6fb538ad06 fixture=agno-agi__agno__092042274925.txt HAND_EXPECTED='tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields' NORMALIZED='tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields' verdict=AGREE
row_key=bee7e94431f6 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='JobQueueTest#shouldCancelJob' NORMALIZED='JobQueueTest#shouldCancelJob' verdict=AGREE CONTESTED
row_key=bfce04c42964 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='JobQueueTest#shouldCheckIfJobIsQueued' NORMALIZED='JobQueueTest#shouldCheckIfJobIsQueued' verdict=AGREE CONTESTED
row_key=cff48077c013 fixture=apache__flink__078003756269.txt HAND_EXPECTED='org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate' NORMALIZED='org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate' verdict=AGREE
row_key=d2acfc050586 fixture=apache__beam__093527298308.txt HAND_EXPECTED='BigQueryMetastoreCatalogIT#testStreamToPartitionedDynamicDestinations' NORMALIZED='BigQueryMetastoreCatalogIT#testStreamToPartitionedDynamicDestinations' verdict=AGREE CONTESTED
row_key=d6556fd08827 fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='sirix-python-client/tests/test_sirix_async.py::test_database_create' NORMALIZED='sirix-python-client/tests/test_sirix_async.py::test_database_create' verdict=AGREE
row_key=da93371bad8a fixture=linkedin__brooklin__077863844421.txt HAND_EXPECTED='com.linkedin.datastream.server.TestCoordinator#testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation' NORMALIZED='NONE' verdict=DISAGREE CONTESTED
row_key=dd21bdcdf521 fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='sirix-python-client/tests/test_sirix_sync.py::test_delete' NORMALIZED='sirix-python-client/tests/test_sirix_sync.py::test_delete' verdict=AGREE
row_key=e2d48d930cf9 fixture=agno-agi__agno__079305370965.txt HAND_EXPECTED='libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer' NORMALIZED='libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer' verdict=AGREE
row_key=f433234b4233 fixture=fla-org__flash-linear-attention__086098926451.txt HAND_EXPECTED='tests/models/test_modeling_comba.py::test_generation' NORMALIZED='tests/models/test_modeling_comba.py::test_generation' verdict=AGREE
row_key=f74f48f3de5e fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testGetDefaultGraphReturnsFriendlyError' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testGetDefaultGraphReturnsFriendlyError' verdict=AGREE
row_key=ff36ea9d0dbe fixture=apache__beam__093527298308.txt HAND_EXPECTED='BigQueryMetastoreCatalogIT#testReadWriteStreaming' NORMALIZED='BigQueryMetastoreCatalogIT#testReadWriteStreaming' verdict=AGREE CONTESTED

UNFILLED: 0 / 47
AGREE:    44 / 47
DISAGREE: 3 / 47
AGREE-ON-CONTESTED: 19 / 47
```

**A note on what these totals mean now.** Per the Phase 1 correction, the 44 AGREE rows are
self-agreement and are not evidence. The number that matters is DISAGREE = 3, and all three
are the known defects. The harness in Phase 4 is what converts those three from a prose
observation into an executable guard.

---

## PHASE 4 — `tests/test_parser_regression.py`

### How cases are derived

The module **imports `parse_worksheet` and `parse_expectation_table` from
`analysis.expectation_diff` and calls them**, rather than reimplementing the derivation. That
is the strongest available reading of "derive its cases the same way": it is not *the same
way*, it is *the same code*. Consequently every `row_key` is recomputed from the raw bytes of
the fixture name plus evidence lines via `compute_row_key`, and `parse_worksheet` itself
raises `ValueError` if a section's stored header key disagrees with the key recomputed from
that section's own evidence. No stored key is trusted anywhere.

`_build_cases()` additionally raises — rather than skipping — if the two documents' row_key
sets differ, or if any HAND_EXPECTED is unfilled. Both are corpus corruption; a silent skip
there would be the same class of invisible loss D-46 exists to forbid.

Dependency direction is preserved: `analysis/` still depends on `src/parse/`, never the
inverse. `tests/` importing `analysis/` introduces no cycle.

### Assertion shape — and why predicted failure (c) cannot hold as written

`dispatch_parse_log` returns a `list[TestOutcome]` for a whole log, and **`TestOutcome`
retains no reference to the raw line that produced it** (`src/parse/outcome.py`: the
dataclass has `test_id`, `parser_confidence`, ids, `test_file`, `status`, `duration_s`,
`failure_message`, `label_source` — no source line, no line number). So a row cannot be
matched to one list element *by evidence line either*: the evidence line is simply not
carried. The expectation table recovered it only via a `sys.settrace` line-tracer, which is a
one-off extraction technique, not something a test should depend on.

The assertion is therefore **set membership over the normalised ids emitted for the whole
fixture**:

- HAND_EXPECTED is an identifier → it MUST appear in that set.
- HAND_EXPECTED starts with `NO_TEST` → the expectation table's recorded NORMALIZED for that
  row (the id the parser currently emits for that evidence) MUST NOT appear in the set.

Nothing anywhere assumes list position.

### Known defects, marked `xfail(strict=True)`

| row_key | fixture | defect named in the reason |
|---|---|---|
| `da93371bad8a` | `linkedin__brooklin__077863844421.txt` | D2 Gradle chevron mis-segmentation |
| `57e11a35966e` | `apache__hugegraph__084221602296.txt` | D4 Maven class-level last-dot split |
| `6a5fd9d35a1f` | `apache__beam__086101982024.txt` | D-46 synthetic classMethod |

**Naming flag.** `D2` and `D3` are established labels — Phase 020 §§D2, D3. **`D4` is not.**
`grep -rn "\bD4\b" docs/` returns nothing; the label is introduced by this task's prompt. I
used it verbatim in the xfail reason as instructed, but it is currently an orphan reference
and should either be given a home in the defect docs or renamed.

### Fresh-clone safety — proven, not asserted

`tests/fixtures/holdout_v4/` is untracked, and so are **both** Phase 021 documents and
`analysis/expectation_diff.py`. A fresh clone has none of them, so the guard covers all
three paths, not just the fixture directory, and runs *before* any import of `analysis` or
`src` is attempted. Proven by copying the module to an empty directory and running it there:

```
$ cd <scratchpad>/freshclone && uv run --project /home/shree/blastradius pytest test_parser_regression.py -rs -q
=========================== short test summary info ============================
SKIPPED [1] test_parser_regression.py:62: Phase 021B regression corpus is not present in this checkout, missing: tests/fixtures/holdout_v4, docs/phase/021B-blind-worksheet.md, docs/phase/021-expectation-table.md
1 skipped in 0.00s
```

### `$ uv run pytest tests/test_parser_regression.py -v`

**Predicted: 44 passed, 3 xfailed, 0 failed.**

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /home/shree/blastradius/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/shree/blastradius
configfile: pyproject.toml
plugins: anyio-4.14.2
collecting ... collected 47 items

tests/test_parser_regression.py::test_parser_matches_hand_expected[015d3b2416a0] PASSED [  2%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[068f9bb711d8] PASSED [  4%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[0b1dcde22361] PASSED [  6%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[0e5d3a59b174] PASSED [  8%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[185149df8b18] PASSED [ 10%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[1b4f2d40df89] PASSED [ 12%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[2598cf91f544] PASSED [ 14%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[2724bcfc3dff] PASSED [ 17%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[2bec1480577b] PASSED [ 19%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[3269f76d726f] PASSED [ 21%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[36ea4df7a8e6] PASSED [ 23%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[3f74c8efd8d5] PASSED [ 25%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[4ca072d0ebcf] PASSED [ 27%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[4d25554936d1] PASSED [ 29%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[51208f55ec56] PASSED [ 31%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[561a20998890] PASSED [ 34%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[57e11a35966e] XFAIL [ 36%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[5ce7156d4c23] PASSED [ 38%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[63351e37b366] PASSED [ 40%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[6a5fd9d35a1f] XFAIL [ 42%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[6d271ffe6080] PASSED [ 44%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[6e0955e465d6] PASSED [ 46%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[7a18936bd0b6] PASSED [ 48%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[7a69e71e197c] PASSED [ 51%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[80b12bf4ef69] PASSED [ 53%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[819c2f5d708c] PASSED [ 55%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[83a64a4e66bd] PASSED [ 57%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[8aabd9035ed4] PASSED [ 59%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[906fd9b5040d] PASSED [ 61%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[9ad2fff53c74] PASSED [ 63%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[9be730822015] PASSED [ 65%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[9e4d4bd8e591] PASSED [ 68%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[a235cadb12ea] PASSED [ 70%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[b0980797f104] PASSED [ 72%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[b9184834c4c8] PASSED [ 74%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[bc6fb538ad06] PASSED [ 76%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[bee7e94431f6] PASSED [ 78%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[bfce04c42964] PASSED [ 80%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[cff48077c013] PASSED [ 82%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[d2acfc050586] PASSED [ 85%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[d6556fd08827] PASSED [ 87%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[da93371bad8a] XFAIL [ 89%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[dd21bdcdf521] PASSED [ 91%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[e2d48d930cf9] PASSED [ 93%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[f433234b4233] PASSED [ 95%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[f74f48f3de5e] PASSED [ 97%]
tests/test_parser_regression.py::test_parser_matches_hand_expected[ff36ea9d0dbe] PASSED [100%]

======================== 44 passed, 3 xfailed in 1.70s =========================
```

**Predicted 44 / 3 / 0 — actual 44 / 3 / 0. Exact.**

### The xfails are real failures, not vacuous passes being hidden

Per AGENT_RULES — *"A zero is not evidence until the counter has been seen to increment"* —
an `XFAIL` that would also be an `XFAIL` if the assertion were a no-op proves nothing.
Forcing the assertions to be reported:

```
$ uv run pytest tests/test_parser_regression.py --runxfail -q
...
E       AssertionError: da93371bad8a (linkedin__brooklin__077863844421.txt): expected 'com.linkedin.datastream.server.TestCoordinator#testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation' among the emitted ids, parser currently records 'NONE' for this evidence; emitted set = []
E       assert 'com.linkedin.datastream.server.TestCoordinator#testLeaderDoAssignmentForNewlyElectedLeaderFailurePathVariation' in set()

tests/test_parser_regression.py:224: AssertionError
=========================== short test summary info ============================
FAILED tests/test_parser_regression.py::test_parser_matches_hand_expected[57e11a35966e]
FAILED tests/test_parser_regression.py::test_parser_matches_hand_expected[6a5fd9d35a1f]
FAILED tests/test_parser_regression.py::test_parser_matches_hand_expected[da93371bad8a]
3 failed, 44 passed in 2.20s
```

All three genuinely fail. And the `strict=True` half — that a *fix* turns the marker red —
demonstrated on a throwaway in the scratchpad rather than assumed from the docs:

```
$ cd <scratchpad>/strictdemo && uv run --project /home/shree/blastradius pytest test_strict.py -q
=================================== FAILURES ===================================
____________________________ test_defect_now_fixed _____________________________
[XPASS(strict)] pretend defect, now fixed
=========================== short test summary info ============================
FAILED test_strict.py::test_defect_now_fixed - [XPASS(strict)] pretend defect...
1 failed in 0.00s
```

### `$ uv run pytest tests/test_test_ids.py -v --tb=no -q`

Summary line, frozen `test_id` contract intact:

```
============================== 50 passed in 0.11s ==============================
```

Full suite before and after this task, for completeness:

```
$ uv run pytest -q --tb=no --ignore=tests/test_parser_regression.py
411 passed, 1 skipped in 54.27s

$ uv run pytest -q --tb=no
455 passed, 1 skipped, 3 xfailed in 61.46s (0:01:01)
```

---

## PREDICTED FAILURES — verdicts

**(a) "Parsing all 26 outcome-bearing fixtures makes the suite slow enough to be unpleasant"
— FALSIFIED.** Measured wall clock: **1.70 s for all 47 cases**, of which parsing is ~1.6 s.
The largest fixtures are cheap: `apache__zeppelin` (5.2 MB) 0.28 s, `floci` 0.29 s,
`apache__flink__078003756269` (3.2 MB) 0.16 s; most are under 0.05 s. The session-scope cache
is still worth keeping — it collapses 47 parses to 26 — but it is an economy, not a rescue.

**No, a smaller fixture set would not preserve coverage, and shrinking it would be a
mistake.** 47 rows span 26 fixtures with a long tail of one-row fixtures; dropping fixtures
drops whole framework/format shapes, and at 1.7 s there is nothing to buy. The opposite
problem is the real one: **6 of the 32 fixtures contribute no rows at all** —
`apache__tika__090757115090.txt`, `floci-io__floci__078678232449.txt`,
`opentripplanner__opentripplanner__081988213338.txt`,
`opentripplanner__opentripplanner__092404918995.txt`,
`spiculedata__saiku__086592116219.txt`, `thealgorithms__java__095336925353.txt`. Those six
are checked into the corpus and guarded by nothing.

**(b) "HAND_EXPECTED values beginning with NO_TEST are prose, not identifiers, and the
assertion needs an explicit branch" — CONFIRMED.** `test_parser_matches_hand_expected`
branches on `hand_expected.startswith("NO_TEST")` and inverts the assertion: for those rows
the check is that the currently-emitted id is *absent*. A plain string compare would have
compared an English sentence against a test id and failed for the wrong reason — passing the
suite while proving nothing about the ruling.

**(c) "The dispatcher returns a list per fixture, so mapping one row_key to one outcome
requires matching on the evidence line, not on list position" — HALF CONFIRMED, HALF
IMPOSSIBLE.** The premise is right: it is a list, and position is meaningless. Position was
**not** assumed anywhere. But the proposed remedy cannot be implemented — `TestOutcome`
carries no evidence line, so there is nothing to match on. Set membership over the whole
fixture's normalised ids is the correct available construct, and is what was built.

**(d) MY OWN — the two `NO_TEST` assertions are weaker than they look, and can be satisfied
by a *different* wrong answer.** Each asserts that one specific recorded string is absent:
`org.apache.hugegraph.core#CoreTestSuite` and `HadoopFormatIOCassandraTest#classMethod`. If
the D4 fix changes the split point rather than suppressing the emission — say it starts
emitting `org.apache.hugegraph.core.CoreTestSuite#CoreTestSuite` — the recorded string is
gone, the strict xfail flips to XPASS, the marker gets removed as "fixed", and the harness
goes green on an identifier that still names no source symbol and still violates D-46. The
assertion pins *this* wrong answer, not the *class* of wrong answers.

Closing it properly requires what D-46 actually mandates and the parser does not yet have:
a **counter** for suppressed class-level events. Once `parse_*_log_with_stats` reports
`class_level_events_suppressed`, the NO_TEST rows should assert on that counter incrementing
rather than on a string's absence — which is also the only way to satisfy D-46's *"the count
reported on every parse run"* clause. That is parser work and is correctly out of scope here;
recorded so the next task does not inherit a harness that looks stronger than it is.

---

## Should `tests/fixtures/holdout_v4/` be committed? — **Yes. Recommend committing it.**
### Not committed here, and no `git add` was run, per the non-goals.

The evidence:

| | |
|---|---|
| Size on disk | 38 MB (39,040,981 bytes), 32 files |
| Size as git objects (gzip -6, measured) | **4.7 MB** — CI logs are highly repetitive text |
| Current `.git` | 26 MB |
| Not in `.gitignore` | `git check-ignore` → not ignored |

**Precedent already settled this.** Three sibling fixture corpora are tracked today:
`tests/fixtures/holdout/` (61 MB on disk, 21 files tracked), `holdout_v3/` (21 MB, 31 tracked),
`logs/` (26 MB, 41 tracked). `holdout_v4` is the *smallest* of the four. Committing it is
consistent, not novel; leaving it untracked is the anomaly.

**Three reasons it should not stay untracked:**

1. **CLAUDE.md rule 3 requires "a checked-in log file with hand-written expected output."**
   Untracked, this harness is a test that exists only on one laptop. `make test` on any
   other machine skips it — cleanly, but silently.
2. **The source logs cannot be re-fetched.** GitHub Actions logs expire at 90 days
   (`docs/DATA_DEPENDENCIES.md`, and the harvester's whole expiry-clock design). These 32
   fixtures are from May–September 2026 runs; a meaningful share is already past or near
   expiry. If this directory is lost, the corpus, the expectation table, the worksheet, and
   this harness all become unreproducible together.
3. **It is the evidence base for three phase reports.** Phases 020, 021, 021B and 021C all
   quote line numbers and byte offsets inside these files. Those citations are unverifiable
   against an untracked directory.

**Two things to do at the same commit, not after:**

- `docs/phase/021B-blind-worksheet.md`, `docs/phase/021-expectation-table.md`, and
  `analysis/expectation_diff.py` are **also untracked** and are hard dependencies of this
  harness. Committing the fixtures without them leaves the module skipping anyway. All five
  paths belong in one commit.
- **Secret-scan them first.** `analysis/secret_scan.py` exists and is a T1.6b release
  blocker; per D-45 its BLOCKER tier is `github_token` / `bearer_token`. These are raw CI
  logs from public repositories, which is the low-risk case, but 38 MB of unscanned build
  output going into permanent git history is exactly the thing that scan is for, and git
  history is not retractable.

---

## Non-goals honoured

No parser was fixed — D2, D3, D4 and D-46 all remain live, and the three xfails are the
receipt. Nothing under `src/` was modified. `docs/SCHEMAS.md`,
`docs/phase/021-expectation-table.md`, `docs/phase/012B-holdout-v4-worksheet.md` and
`docs/TASKS.md` are untouched (the TASKS.md divergence is reported above, not edited).
Nothing wired into `make tables` or `make test`. No `git add`, no `git commit`. No HTTP
issued. No background, `nohup`, `setsid`, or subagent execution — every command ran in the
foreground and its output is above. Throwaway scripts live under the session scratchpad;
`git status` shows no new file at the repository root.

## Open questions for the operator

1. **`D4` has no home.** It is referenced in an xfail reason but defined in no document.
   Give it a section in the defect docs, or rename the marker to whatever the Maven
   class-level defect is actually called.
2. **Commit the five untracked paths?** Recommendation above is yes, in one commit, after a
   secret scan. Needs explicit authorization — none was given and none was assumed.
3. **AGENT_RULES' `docs/session/NNN-…md` + `docs/HANDOFF.md` pair was not written**, because
   this task named one deliverable and listed explicit non-goals. Say the word and it is one
   more step.
4. **D-46's counter is not implemented.** The ruling requires class-level events to be
   counted and the count reported on every parse run. No such counter exists in
   `src/parse/`. Until it does, D-46 is recorded but only half-enforceable — see predicted
   failure (d).
