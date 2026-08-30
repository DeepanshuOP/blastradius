import pytest
import pandas as pd
from src.label.fault_revealing import compute_labels

def test_no_base_omitted():
    # 25441351692 is a no_base run.
    res = pd.DataFrame([{'run_id': 25441351692, 'status': 'no_base'}])
    instances = pd.DataFrame([{'run_id': 25441351692, 'head_sha': 'abc', 'workflow_id': 1}])
    head = pd.DataFrame([{'run_id': 25441351692, 'test_id': 'T1'}])
    base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(res, instances, head, base)
    assert len(out) == 0

def test_no_output_base_omitted():
    # 32114688438 is a NO_TEST_OUTPUT run (status=exact, but not in base)
    res = pd.DataFrame([{'run_id': 32114688438, 'status': 'exact'}])
    instances = pd.DataFrame([{'run_id': 32114688438, 'head_sha': 'def', 'workflow_id': 2}])
    head = pd.DataFrame([{'run_id': 32114688438, 'test_id': 'T2'}])
    base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(res, instances, head, base)
    assert len(out) == 0

def test_exact_green_included():
    # 32188133486 is exact_green
    res = pd.DataFrame([{'run_id': 32188133486, 'status': 'exact_green'}])
    instances = pd.DataFrame([{'run_id': 32188133486, 'head_sha': 'ghi', 'workflow_id': 3}])
    head = pd.DataFrame([{'run_id': 32188133486, 'test_id': 'T3'}])
    base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(res, instances, head, base)
    assert len(out[out['split'] == 'strict']) == 1


@pytest.fixture(scope="module")
def real_data():
    res = pd.read_parquet('data/interim/base_resolution_new.parquet')
    instances = pd.read_parquet('data/interim/instances_raw.parquet')
    head = pd.read_parquet('data/interim/parsed_outcomes.parquet')
    base = pd.read_parquet('data/interim/base_outcomes.parquet')
    return res, instances, head, base

def test_matrix_legs_unioned(real_data):
    res, instances, head, base = real_data
    dups = head.groupby(['run_id', 'test_id']).size()
    multi = dups[dups > 1].index[0]
    r_id, t_id = multi
    r_res = pd.DataFrame([{'run_id': r_id, 'status': 'exact_green'}])
    r_inst = instances[instances['run_id'] == r_id]
    if r_inst.empty:
        r_inst = pd.DataFrame([{'run_id': r_id, 'head_sha': 'mock_sha', 'workflow_id': 1}])
    r_head = head[head['run_id'] == r_id].copy()
    r_base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(r_res, r_inst, r_head, r_base)
    strict = out[out['split'] == 'strict']
    assert len(strict[strict['test_id'] == t_id]) == 1

def test_fail_head_and_base_not_revealing(real_data):
    res, instances, head, base = real_data
    both = pd.merge(head, base, on=['run_id', 'test_id'])
    r_id = both['run_id'].iloc[0]
    t_id = both['test_id'].iloc[0]
    
    r_res = res[res['run_id'] == r_id]
    r_inst = instances[instances['run_id'] == r_id]
    r_head = head[head['run_id'] == r_id]
    r_base = base[base['run_id'] == r_id]
    
    out, _ = compute_labels(r_res, r_inst, r_head, r_base)
    assert len(out[(out['test_id'] == t_id) & (out['split'] == 'all')]) > 0
    assert len(out[(out['test_id'] == t_id) & (out['split'] == 'relaxed')]) == 0

def test_fail_head_not_base_is_revealing(real_data):
    res, instances, head, base = real_data
    r_id = base['run_id'].iloc[0]
    r_res = res[res['run_id'] == r_id]
    r_inst = instances[instances['run_id'] == r_id]
    r_head = head[head['run_id'] == r_id]
    r_base = base[base['run_id'] == r_id]
    
    head_tests = set(r_head['test_id'])
    base_tests = set(r_base['test_id'])
    diff = head_tests - base_tests
    if not diff:
        r_head = pd.concat([r_head, pd.DataFrame([{'run_id': r_id, 'test_id': 'MOCK_TEST'}])])
        t_id = 'MOCK_TEST'
    else:
        t_id = list(diff)[0]
        
    out, _ = compute_labels(r_res, r_inst, r_head, r_base)
    assert len(out[(out['test_id'] == t_id) & (out['split'] == 'strict')]) == 1

def test_strict_excludes_flaky(real_data):
    # This one doesn't strictly need real data to prove the logic, but uses the structure
    res, instances, head, base = real_data
    r1, r2 = 1, 2
    sha = "flaky_sha"
    wf = 999
    r_res = pd.DataFrame([
        {'run_id': r1, 'status': 'exact_green'},
        {'run_id': r2, 'status': 'exact_green'}
    ])
    r_inst = pd.DataFrame([
        {'run_id': r1, 'head_sha': sha, 'workflow_id': wf},
        {'run_id': r2, 'head_sha': sha, 'workflow_id': wf}
    ])
    r_head = pd.DataFrame([
        {'run_id': r1, 'test_id': 'T1'}
    ])
    r_base = pd.DataFrame(columns=['run_id', 'test_id'])
    
    out, _ = compute_labels(r_res, r_inst, r_head, r_base)
    assert len(out[(out['test_id'] == 'T1') & (out['run_id'] == r1) & (out['split'] == 'relaxed')]) == 1
    assert len(out[(out['test_id'] == 'T1') & (out['run_id'] == r1) & (out['split'] == 'strict')]) == 0
