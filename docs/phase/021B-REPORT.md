# Phase 021B — Blind Ground-Truth Worksheet (READ-ONLY except two new files)

**Scope**: Created exactly two files: `docs/phase/021B-blind-worksheet.md` and
`analysis/expectation_diff.py`. Nothing under `src/` was touched, no parser was fixed,
`docs/SCHEMAS.md`, `docs/DECISIONS.md`, `docs/phase/021-expectation-table.md`, and
`docs/phase/012B-holdout-v4-worksheet.md` were not edited, no `HAND_EXPECTED` value was
filled, `analysis/expectation_diff.py` was not wired into `make tables`, no HTTP was issued,
nothing ran in background/nohup/setsid/async.

## PHASE 1 — Scratch script location

`git status --porcelain` (before this task) showed no `extract_table.py` tracked or
untracked inside the repo. The script used in Phase 021 has always lived at
`/tmp/claude-1000/-home-shree-blastradius/5ef6bc03-a10d-4672-b502-10a0014c3131/scratchpad/extract_table.py`
— already outside `/home/shree/blastradius`, so nothing needed moving. Confirmed with
`find /home/shree/blastradius -iname extract_table.py`, which returned no matches. Repo
root was already clean of it.

## PHASE 2 — Blind worksheet

`docs/phase/021B-blind-worksheet.md`: 47 `## Row N — fixture` sections, one per row of
`docs/phase/021-expectation-table.md`, generated directly from the same underlying
extraction data (not re-parsed from the 021 markdown) so row numbers 1..47 line up exactly.
Each section shows only the fixture, the verbatim `RAW_LINE` evidence (both lines, neutrally
labelled "evidence line 1" / "evidence line 2" where the outcome spans two source lines),
and an empty `HAND_EXPECTED:` field. No `PARSER_EMITTED`, no `NORMALIZED`, no hint.

**Predicted failure (a) — CONFIRMED, and one more turned up.** Raw evidence lines do contain
characters that would break a markdown table cell (the 021 table needed `|`-escaping for
exactly this). Fencing each `RAW_LINE` in a code block, as suggested, avoids needing any
piecemeal character escaping. A second, unprompted problem showed up during generation: two
Gradle rows carry literal ANSI colour-escape bytes (`\x1b[33m...\x1b[0m`) which render as
garbled/invisible control sequences when embedded raw inside a fence. Fixed by reusing the
same convention already established in `docs/phase/021-expectation-table.md` — display the
line as a Python `repr()` (control bytes shown as visible escape-sequence text) inside the
fence. This is disclosed in the worksheet's own header as a display transform, byte-exact and
reversible, adding/removing/reordering nothing.

**Predicted failure (b) — CONFIRMED as stated.** The original evidence notes computed in
Phase 021 (e.g. *"stack-trace 'at' frame supplying the FQCN used in the Pass-1 suffix join"*)
name the mechanism, which tells the operator in advance that the package must be assembled
from a second line via a Java stack frame — exactly the answer. Replaced with the neutral
"evidence line 1" / "evidence line 2" labels the task suggested, with a header note that the
order carries no meaning about which line (if either) supplies the class, package, or method.

## PHASE 3 — Join script

`analysis/expectation_diff.py` parses both files by row number and prints one line per row
(`row=… fixture=… HAND_EXPECTED=… NORMALIZED=… verdict=…`) plus three totals lines with
numerator and denominator written out. One bug surfaced and was fixed before the final run:
the first regex used a lookahead to stop before each row's trailing `---` section delimiter,
but `\s*` before the capture group backtracked past the delimiter's own leading newline,
so the delimiter (`'---'`) was captured as if it were the operator's answer on every row.
Replaced with a simpler "capture to end of section, then strip a trailing `---` line"
two-step, verified against synthetic AGREE/DISAGREE/UNFILLED cases (on throwaway copies —
the real worksheet was never written to) before the final run below.

Raw output of `python3 analysis/expectation_diff.py` against the currently-unfilled
worksheet, pasted in full:

```
row=1 fixture=Stirling-Tools__Stirling-PDF__081016081705.txt HAND_EXPECTED='' NORMALIZED='UIDataControllerTest#getPipelineData_usesEachSourceFilenameWhenJsonContentIsIdentical' verdict=UNFILLED
row=2 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='' NORMALIZED='JobQueueTest#shouldCheckIfJobIsQueued' verdict=UNFILLED
row=3 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='' NORMALIZED='JobQueueTest#shouldCancelJob' verdict=UNFILLED
row=4 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='' NORMALIZED='JobQueueTest#shouldGetQueueStats' verdict=UNFILLED
row=5 fixture=Stirling-Tools__Stirling-PDF__081185748047.txt HAND_EXPECTED='' NORMALIZED='JobQueueTest#shouldQueueJob' verdict=UNFILLED
row=6 fixture=agno-agi__agno__079305370965.txt HAND_EXPECTED='' NORMALIZED='libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_gpt2_tokenizer' verdict=UNFILLED
row=7 fixture=agno-agi__agno__079305370965.txt HAND_EXPECTED='' NORMALIZED='libs/agno/tests/unit/knowledge/chunking/test_code_chunking.py::test_code_chunking_cl100k_tokenizer' verdict=UNFILLED
row=8 fixture=agno-agi__agno__092042274925.txt HAND_EXPECTED='' NORMALIZED='tests/integration/models/deepinfra/test_structured_response.py::test_structured_response_with_enum_fields' verdict=UNFILLED
row=9 fixture=apache__atlas__085339439869.txt HAND_EXPECTED='' NORMALIZED='org.apache.atlas.kafka.KafkaNotificationTest#setup' verdict=UNFILLED
row=10 fixture=apache__beam__086101982024.txt HAND_EXPECTED='' NORMALIZED='HadoopFormatIOCassandraTest#classMethod' verdict=UNFILLED
row=11 fixture=apache__beam__086101982024.txt HAND_EXPECTED='' NORMALIZED='HadoopFormatIOElasticTest#testHifIOWithElastic' verdict=UNFILLED
row=12 fixture=apache__beam__086101982024.txt HAND_EXPECTED='' NORMALIZED='HadoopFormatIOElasticTest#testHifIOWithElasticQuery' verdict=UNFILLED
row=13 fixture=apache__beam__093527298308.txt HAND_EXPECTED='' NORMALIZED='BigQueryMetastoreCatalogIT#testWrite' verdict=UNFILLED
row=14 fixture=apache__beam__093527298308.txt HAND_EXPECTED='' NORMALIZED='BigQueryMetastoreCatalogIT#testWriteRead' verdict=UNFILLED
row=15 fixture=apache__beam__093527298308.txt HAND_EXPECTED='' NORMALIZED='BigQueryMetastoreCatalogIT#testReadWriteStreaming' verdict=UNFILLED
row=16 fixture=apache__beam__093527298308.txt HAND_EXPECTED='' NORMALIZED='BigQueryMetastoreCatalogIT#testStreamToPartitionedDynamicDestinations' verdict=UNFILLED
row=17 fixture=apache__dolphinscheduler__092883042571.txt HAND_EXPECTED='' NORMALIZED='org.apache.dolphinscheduler.e2e.cases.DolphinDBDataSourceE2ETest#testCreateDolphinDBDataSource' verdict=UNFILLED
row=18 fixture=apache__flink__078003756269.txt HAND_EXPECTED='' NORMALIZED='org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate' verdict=UNFILLED
row=19 fixture=apache__flink__079445374425.txt HAND_EXPECTED='' NORMALIZED='org.apache.flink.docs.rest.RuntimeOpenRestAPIDocsCompletenessITCase#testRuntimeRestApiDocsUpToDate' verdict=UNFILLED
row=20 fixture=apache__hugegraph__084221602296.txt HAND_EXPECTED='' NORMALIZED='org.apache.hugegraph.core#CoreTestSuite' verdict=UNFILLED
row=21 fixture=apache__hugegraph__084221602296.txt HAND_EXPECTED='' NORMALIZED='org.apache.hugegraph.core.CoreTestSuite#init' verdict=UNFILLED
row=22 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphWithGetCompatibilityReturnsFriendlyError' verdict=UNFILLED
row=23 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testUnsetDefaultGraphReturnsFriendlyError' verdict=UNFILLED
row=24 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphReturnsFriendlyError' verdict=UNFILLED
row=25 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testSetDefaultGraphWithGetCompatibilityReturnsFriendlyError' verdict=UNFILLED
row=26 fixture=apache__hugegraph__086386091934.txt HAND_EXPECTED='' NORMALIZED='org.apache.hugegraph.api.GraphsApiStandaloneTest#testGetDefaultGraphReturnsFriendlyError' verdict=UNFILLED
row=27 fixture=apache__zeppelin__077616025677.txt HAND_EXPECTED='' NORMALIZED='org.apache.zeppelin.rest.InterpreterRestApiTest#testCreatedInterpreterDependencies' verdict=UNFILLED
row=28 fixture=dask__distributed__084645769341.txt HAND_EXPECTED='' NORMALIZED='distributed/tests/test_nanny.py::test_failure_during_worker_initialization' verdict=UNFILLED
row=29 fixture=dask__distributed__084757793457.txt HAND_EXPECTED='' NORMALIZED='distributed/tests/test_active_memory_manager.py::test_RetireWorker_stress' verdict=UNFILLED
row=30 fixture=fla-org__flash-linear-attention__082566635619.txt HAND_EXPECTED='' NORMALIZED='tests/models/test_modeling_forgetting_transformer.py::test_modeling' verdict=UNFILLED
row=31 fixture=fla-org__flash-linear-attention__086098926451.txt HAND_EXPECTED='' NORMALIZED='tests/models/test_modeling_comba.py::test_generation' verdict=UNFILLED
row=32 fixture=floci-io__floci__085018489189.txt HAND_EXPECTED='' NORMALIZED='io.github.hectorvent.floci.services.ec2.Ec2IntegrationTest#describeDefaultVpc' verdict=UNFILLED
row=33 fixture=gurkenlabs__litiengine__079152380933.txt HAND_EXPECTED='' NORMALIZED='AlignTests#getClampedLocation_InPoint' verdict=UNFILLED
row=34 fixture=gurkenlabs__litiengine__079152380933.txt HAND_EXPECTED='' NORMALIZED='AlignTests#getClampedLocation_OffPoint' verdict=UNFILLED
row=35 fixture=linkedin__brooklin__077863844421.txt HAND_EXPECTED='' NORMALIZED='NONE' verdict=UNFILLED
row=36 fixture=nats-io__nats.java__080900237539.txt HAND_EXPECTED='' NORMALIZED='io.nats.client.api.ConsumerConfigurationTests#testBuilder' verdict=UNFILLED
row=37 fixture=nats-io__nats.java__080900237539.txt HAND_EXPECTED='' NORMALIZED='io.nats.client.impl.SimplificationTests#testReconnectOverOrdered' verdict=UNFILLED
row=38 fixture=robo-code__robocode__084332182805.txt HAND_EXPECTED='' NORMALIZED='TestFairPlay#run' verdict=UNFILLED
row=39 fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='' NORMALIZED='sirix-python-client/tests/test_sirix_async.py::test_database_create' verdict=UNFILLED
row=40 fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='' NORMALIZED='sirix-python-client/tests/test_sirix_async.py::test_database_delete' verdict=UNFILLED
row=41 fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='' NORMALIZED='sirix-python-client/tests/test_sirix_sync.py::test_create' verdict=UNFILLED
row=42 fixture=sirixdb__sirix__080642754882.txt HAND_EXPECTED='' NORMALIZED='sirix-python-client/tests/test_sirix_sync.py::test_delete' verdict=UNFILLED
row=43 fixture=sirixdb__sirix__092352347826.txt HAND_EXPECTED='' NORMALIZED='RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable' verdict=UNFILLED
row=44 fixture=sirixdb__sirix__092352347826.txt HAND_EXPECTED='' NORMALIZED='RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass' verdict=UNFILLED
row=45 fixture=unicode-org__cldr__090672967305.txt HAND_EXPECTED='' NORMALIZED='org.unicode.cldr.unittest.TestShim#TestAll' verdict=UNFILLED
row=46 fixture=webauthn4j__webauthn4j__080348707704.txt HAND_EXPECTED='' NORMALIZED='com.webauthn4j.data.attestation.authenticator.EC2COSEKeyTest#json_serialize_deserialize_test' verdict=UNFILLED
row=47 fixture=webauthn4j__webauthn4j__080348707704.txt HAND_EXPECTED='' NORMALIZED='com.webauthn4j.data.attestation.authenticator.RSACOSEKeyTest#json_serialize_deserialize_test' verdict=UNFILLED

UNFILLED: 47 / 47
AGREE:    0 / 47
DISAGREE: 0 / 47
```

Exit code: 0.

## My own predicted failure

**(c) Row-number drift if either file is hand-edited out of order.** The join is purely by
row number, trusting both files stay in lockstep. Nothing enforces that `docs/phase/021-expectation-table.md`
(frozen, not touched here) and `docs/phase/021B-blind-worksheet.md` (the operator will edit
by hand) keep the same 47 rows in the same order — if a row were ever inserted, deleted, or
renumbered in the worksheet during hand-filling, the join would silently pair the wrong
`HAND_EXPECTED` to the wrong `NORMALIZED` with no error. Not fixed here (out of scope); flagged
for the operator to preserve row numbers exactly while filling.

**Nothing else was changed. Nothing was committed.**
