import pytest
import os
import unittest.mock
from analysis.resolve_bases import run as run_resolve
from analysis.fetch_base_logs import run as run_fetch
from analysis.parse_base_logs import run as run_parse
from src.harvest.migrations import run as run_migrations
from tests.conftest import requires_data

@unittest.mock.patch('pandas.DataFrame.to_parquet')
@requires_data("data/interim/base_resolution_new.parquet", "data/interim/instances_raw.parquet")
def test_resolve_smoke(mock_to_parquet):
    df = run_resolve(limit=1)
    assert len(df) == 1

def test_fetch_smoke():
    if not any(k in os.environ for k in ['GITHUB_PAT_1', 'GITHUB_PAT_2', 'GITHUB_PAT_3']):
        pytest.skip("No GitHub PAT found in environment")
    stats = run_fetch(limit=1)
    assert 'requests' in stats

@unittest.mock.patch('pyarrow.parquet.write_table')
@requires_data("data/interim/base_resolution_new.parquet", "data/raw")
def test_parse_smoke(mock_write_table):
    run_parse(limit=1)

@requires_data("data/state")
def test_migrations_smoke():
    run_migrations()
