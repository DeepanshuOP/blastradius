"""Release schema v0.2 (D-54): joins, null rules, aggregation and the validator.

Every expected value below was computed by hand from the checked-in slice in
`tests/fixtures/release_v02/interim/` (see its README), never from the code
under test. If one of these fails, the code is wrong, not the expectation.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path

import duckdb
import pytest

from analysis.build_release import build
from analysis.release_schema import generate, parse_section
from analysis.validate_release import validate

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "tests/fixtures/release_v02/interim"
KEY = b"br-bench-test-key-do-not-use"

#: run_id -> (base_status, base_run_id, base_run_distance, n_files, n_lines,
#:            touches_test, touches_build, touches_ci, docs_only, changed_files)
EXPECTED_INSTANCES = {
    16250928760: ("no_base", None, None, 2, 12, True, False, False, False, [
        "zeppelin-server/src/main/java/org/apache/zeppelin/server/ZeppelinServer.java",
        "zeppelin-server/src/test/java/org/apache/zeppelin/MiniZeppelinServer.java"]),
    22419331298: ("not_attempted", None, None, 6, 188, True, False, False, False, [
        "src/main/java/io/anserini/collection/HtmlCollection.java",
        "src/main/java/io/anserini/util/BenchmarkCollectionReader.java",
        "src/main/java/io/anserini/util/ReadHtmlCollectionSegmentOverHttp.java",
        "src/main/java/io/anserini/util/StreamFileOverHttp.java",
        "src/test/java/io/anserini/collection/HtmlCollectionTest.java",
        "src/test/java/io/anserini/util/BenchmarkCollectionReaderTest.java"]),
    27210554856: ("exact", 27210507937, 0, 5, 44, True, False, False, False, [
        "distributed/config.py", "distributed/deploy/subprocess.py",
        "distributed/deploy/tests/test_subprocess.py",
        "distributed/tests/test_client.py", "pyproject.toml"]),
    27573755985: ("exact_green", 27517693080, 0, 3, 9, False, False, False, True, [
        "docs/experiments-msmarco-passage.md", "docs/experiments-msmarco-passage2.md",
        "docs/start-here.md"]),
    27810859844: ("exact_green", 27809292148, 0, 3, 164, True, False, False, False, [
        "src/main/java/io/github/hectorvent/floci/services/dynamodb/DynamoDbJsonHandler.java",
        "src/main/java/io/github/hectorvent/floci/services/dynamodb/ExpressionEvaluator.java",
        "src/test/java/io/github/hectorvent/floci/services/dynamodb/DynamoDbFilterExpressionIntegrationTest.java"]),
    28766919851: ("exact_green", 28765390711, 0, 3, 8, False, True, False, False, [
        "build.gradle",
        "spring-boot-starter/mybatis-plus-spring-boot3-starter/build.gradle",
        "spring-boot-starter/mybatis-plus-spring-boot4-starter/build.gradle"]),
    29752097395: ("exact", 32338059625, 0, 5, 375, True, False, False, False, [
        "distributed/__init__.py", "distributed/deploy/__init__.py",
        "distributed/deploy/local_env.py", "distributed/deploy/tests/test_local_env.py",
        "pyproject.toml"]),
    31218903455: ("exact_green", 31218690439, 0, 3, 228, True, False, False, False, [
        "tika-core/src/main/java/org/apache/tika/extractor/EmbeddedDocumentUtil.java",
        "tika-core/src/test/java/org/apache/tika/extractor/EmbeddedDocumentUtilExtensionTest.java",
        "tika-parsers/tika-parsers-standard/tika-parsers-standard-modules/tika-parser-mail-module/src/test/java/org/apache/tika/parser/mail/RFC822ParserTest.java"]),
    31495838733: ("not_attempted", None, None, None, None, None, None, None, None, None),
}

M_EG10 = "ExceptionGroup: multiple unraisable exception warnings (10 sub-exceptions)"
M_156 = "ValueError: ('Unclosed Comms', [<TCP  local=tcp://10.1.0.156:62552 remote=tcp://10.1.0.156:62551>])"
M_RFC = "expected: </Test Attachment Email.eml/embedded-1> but was: </Test Attachment Email.eml/embedded-1.txt>"

#: (run_id, test-id suffix) -> (n_job_rows, status_head, duration_s, test_file,
#:   binding_status, binding_confidence, hash of the pair's smallest message)
EXPECTED_OUTCOMES = {
    (27210554856, "test_freeze_batched_send"): (
        2, "fail", None, "distributed/tests/test_utils_test.py", "exact", 1.0, M_156),
    (27810859844, "scanFilterDoubleNestedParens"): (
        1, "fail", 0.016, "src/test/java/io/github/hectorvent/floci/services/dynamodb/DynamoDbFilterExpressionIntegrationTest.java",
        "exact", 1.0, "1 expectation failed."),
    (28766919851, "testBatchTransactionalClear4"): (
        1, "fail", None, "mybatis-plus/src/test/java/com/baomidou/mybatisplus/test/h2/cache/CacheTest.java",
        "exact", 0.5, None),
    (29752097395, "test_bad_executable"): (
        20, "fail", None, None, "not_found", None, M_EG10),
    (31218903455, "testExtractAttachments"): (
        1, "fail", 0.085, None, "ambiguous", None, M_RFC),
}


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build v0.2 from the fixture slice and write its schema.json."""
    out = tmp_path_factory.mktemp("rel") / "v0.2"
    build(out, INTERIM, KEY, schema="v0.2")
    generate(ROOT / "docs/SCHEMAS.md", out / "schema.json")
    return out


def _rows(path: Path, sql: str) -> list[tuple]:
    return duckdb.sql(sql.format(f=f"read_parquet('{path.as_posix()}')")).fetchall()


def test_row_counts_and_grain(bundle: Path) -> None:
    """Row counts equal the slice: 9 runs, 15 long-grain outcome rows, 24 messages, 3 cochange."""
    n = lambda t: _rows(bundle / t, "select count(*) from {f}")[0][0]
    assert (n("instances.parquet"), n("outcomes.parquet"),
            n("failure_messages.parquet"), n("cochange.parquet")) == (9, 15, 24, 3)


def test_instance_fills(bundle: Path) -> None:
    """Base fields, changeset aggregates and sorted path lists match hand sums."""
    rows = _rows(bundle / "instances.parquet",
                 "select run_id, base_status, base_run_id, base_run_distance, n_files_changed, "
                 "n_lines_changed, touches_test_file, touches_build_config, touches_ci_config, "
                 "is_docs_only, changed_files from {f}")
    got = {r[0]: r[1:] for r in rows}
    assert set(got) == set(EXPECTED_INSTANCES)
    for run_id, want in EXPECTED_INSTANCES.items():
        assert got[run_id] == want, run_id


def test_no_changeset_is_null_never_zero(bundle: Path) -> None:
    """A run without a changeset has NULL (not 0/false/[]) in every changeset column."""
    cols = ("n_files_changed, n_lines_changed, touches_test_file, touches_build_config, "
            "touches_ci_config, is_docs_only, changed_files")
    row = _rows(bundle / "instances.parquet", f"select {cols} from {{f}} where run_id = 31495838733")[0]
    assert row == (None,) * 7


def test_run_started_at_is_utc_timestamp(bundle: Path) -> None:
    """The ISO-8601 Z string becomes a TIMESTAMP with the same wall-clock value."""
    path = bundle / "instances.parquet"
    assert _rows(path, "select typeof(run_started_at) from {f} limit 1")[0][0] == "TIMESTAMP"
    got = _rows(path, "select run_started_at from {f} where run_id = 27210554856")[0][0]
    assert got == dt.datetime(2026, 6, 9, 13, 45, 42)


def test_authors_pseudonymised(bundle: Path) -> None:
    """No `user-N` fixture login survives; every author is a 16-hex pseudonym."""
    bad = _rows(bundle / "instances.parquet",
                "select count(*) from {f} where not regexp_matches(author_login, '^[0-9a-f]{{16}}$')")
    assert bad[0][0] == 0


def test_outcome_aggregation(bundle: Path) -> None:
    """Per-pair aggregation rules: n_job_rows, status, min confidence, binding, hash."""
    rows = _rows(bundle / "outcomes.parquet",
                 "select run_id, test_id, split, n_job_rows, status_head, parser_confidence, "
                 "duration_s, test_file, binding_status, binding_confidence, failure_message_hash, "
                 "label_source from {f}")
    seen = set()
    for run_id, test_id, split, njr, st, conf, dur, tf, bs, bc, h, src in rows:
        suffix = test_id.replace("::", "#").split("#")[-1]
        want = EXPECTED_OUTCOMES[(run_id, suffix)]
        seen.add((run_id, suffix))
        assert split in ("all", "strict", "relaxed")
        assert (njr, st, tf, bs, bc) == (want[0], want[1], want[3], want[4], want[5])
        assert src == "log"
        assert abs(conf - (0.85 if suffix == "testBatchTransactionalClear4" else 0.9)) < 1e-6
        if want[2] is None:
            assert dur is None
        else:
            assert abs(dur - want[2]) < 1e-6
        expect_hash = None if want[6] is None else hashlib.sha256(want[6].encode()).hexdigest()
        assert h == expect_hash
    assert seen == set(EXPECTED_OUTCOMES)


def test_no_base_means_no_labels(bundle: Path) -> None:
    """Every outcomes run has a non-null base_run_id; the no_base run has no outcome rows."""
    orphans = duckdb.sql(
        f"select count(*) from read_parquet('{bundle / 'outcomes.parquet'}') o "
        f"join read_parquet('{bundle / 'instances.parquet'}') i using (run_id) "
        "where i.base_run_id is null").fetchone()[0]
    assert orphans == 0


def test_failure_message_hash_matches_shipped_text(bundle: Path) -> None:
    """The hash equals sha256 of a text actually present in failure_messages."""
    shipped = {r[0] for r in _rows(bundle / "failure_messages.parquet",
                                   "select failure_message from {f}")}
    hashes = {r[0] for r in _rows(bundle / "outcomes.parquet",
                                  "select failure_message_hash from {f} where failure_message_hash is not null")}
    assert hashes <= {hashlib.sha256(m.encode()).hexdigest() for m in shipped}


def test_schema_section_parses_to_expected_widths() -> None:
    """The markdown contract yields 31/12/12/5 columns and no `actual_changed_files`."""
    tables = parse_section((ROOT / "docs/SCHEMAS.md").read_text(encoding="utf-8"))
    assert {k: len(v) for k, v in tables.items()} == {
        "instances.parquet": 31, "outcomes.parquet": 12,
        "cochange.parquet": 12, "failure_messages.parquet": 5}
    names = {c["name"] for c in tables["instances.parquet"]}
    assert "actual_changed_files" not in names and "changed_files" in names


def test_validator_passes_built_bundle(bundle: Path) -> None:
    """A correct v0.2 bundle validates clean."""
    assert validate(bundle, bundle / "schema.json") == []


def test_validator_catches_each_violation_kind(bundle: Path, tmp_path: Path) -> None:
    """Missing column, extra column, wrong type, NULL in non-nullable, bad enum."""
    bad = tmp_path / "bad"
    shutil.copytree(bundle, bad)
    con = duckdb.connect()
    def rewrite(name: str, select: str) -> None:
        p = bad / name
        con.execute(f"copy (select {select} from read_parquet('{(bundle / name).as_posix()}')) "
                    f"to '{p.as_posix()}' (format parquet)")
    rewrite("instances.parquet",
            "* exclude (changed_files, base_status, run_id), cast(run_id as varchar) as run_id, "
            "1 as extra_col, 'bogus' as base_status")
    rewrite("outcomes.parquet", "* replace (null as test_id)")
    errs = " | ".join(validate(bad, bad / "schema.json"))
    for needle in ("missing column changed_files", "unexpected column extra_col",
                   "instances.parquet.run_id: type VARCHAR != BIGINT",
                   "outcomes.parquet.test_id: 15 NULLs in a non-nullable column",
                   "instances.parquet.base_status: values outside enum"):
        assert needle in errs, needle


def test_validator_fails_v01_shape(tmp_path: Path) -> None:
    """A v0.1-shaped bundle (verbatim copies) is rejected by the v0.2 schema."""
    v01 = tmp_path / "v0.1"
    build(v01, INTERIM, KEY, schema="v0.1")
    generate(ROOT / "docs/SCHEMAS.md", tmp_path / "schema.json")
    errs = validate(v01, tmp_path / "schema.json")
    assert any("missing column base_status" in e for e in errs)
    assert any("unexpected column __index_level_0__" in e for e in errs)
    assert json.loads((tmp_path / "schema.json").read_text())["release_schema"] == "v0.2"
