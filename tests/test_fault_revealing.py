import pytest
import pandas as pd
from src.label.fault_revealing import compute_labels

def test_no_base_omitted():
    # 25441351692 is a no_base run.
    res = pd.DataFrame([{'run_id': 25441351692, 'status': 'no_base'}])
    instances = pd.DataFrame([{'run_id': 25441351692, 'head_sha': 'abc'}])
    head = pd.DataFrame([{'run_id': 25441351692, 'test_id': 'T1'}])
    base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(res, instances, head, base)
    assert len(out) == 0

def test_no_output_base_omitted():
    # 32114688438 is a NO_TEST_OUTPUT run (status=exact, but not in base)
    res = pd.DataFrame([{'run_id': 32114688438, 'status': 'exact'}])
    instances = pd.DataFrame([{'run_id': 32114688438, 'head_sha': 'def'}])
    head = pd.DataFrame([{'run_id': 32114688438, 'test_id': 'T2'}])
    base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(res, instances, head, base)
    assert len(out) == 0

def test_exact_green_included():
    # 32188133486 is exact_green
    res = pd.DataFrame([{'run_id': 32188133486, 'status': 'exact_green'}])
    instances = pd.DataFrame([{'run_id': 32188133486, 'head_sha': 'ghi'}])
    head = pd.DataFrame([{'run_id': 32188133486, 'test_id': 'T3'}])
    base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(res, instances, head, base)
    assert len(out[out['split'] == 'strict']) == 1

