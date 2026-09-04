# Holdout v5 Hand-Labelling Worksheet (Blind Evaluation)

**Target Corpus**: `tests/fixtures/holdout_v5/` (40 logs)  
**Date**: 2026-09-02  
**Deterministic Seed**: `20261111`  
**Governing Decisions**: D-27, D-29, D-37, D-38  
**Labelling Contract**: Expected fields are BLANK. Zero parser output. Hand-labelled strictly from raw log text.  

---

## 1. `apache__beam__088751256715.txt`
- **Section Index**: 1
- **Fixture Filename**: `apache__beam__088751256715.txt`
- **Content Hash**: `2878c96ceaa7eb9f`
- **Repository**: `apache/beam`
- **Raw Evidence Excerpt**:
```text
2026-07-21T20:46:53.8313130Z SKIPPED [1] apache_beam/ml/transforms/embeddings/open_ai_it_test.py:72: OpenAI Python SDK is not installed.
2026-07-21T20:46:53.8315340Z SKIPPED [2] apache_beam/ml/transforms/embeddings/tensorflow_hub_test.py:127: Tensorflow is not installed.
2026-07-21T20:46:53.8317797Z SKIPPED [2] apache_beam/ml/transforms/embeddings/tensorflow_hub_test.py:163: Tensorflow is not installed.
2026-07-21T20:46:53.8320241Z SKIPPED [1] apache_beam/ml/transforms/embeddings/open_ai_it_test.py:53: OpenAI Python SDK is not installed.
2026-07-21T20:46:53.8322428Z SKIPPED [1] apache_beam/ml/transforms/embeddings/open_ai_it_test.py:189: OpenAI Python SDK is not installed.
2026-07-21T20:46:53.8324644Z SKIPPED [1] apache_beam/ml/transforms/embeddings/open_ai_it_test.py:134: OpenAI Python SDK is not installed.
2026-07-21T20:46:53.8327055Z SKIPPED [2] apache_beam/ml/transforms/embeddings/tensorflow_hub_test.py:85: Tensorflow is not installed.
2026-07-21T20:46:53.8329323Z SKIPPED [1] apache_beam/ml/transforms/embeddings/tensorflow_hub_test.py:211: Tensorflow is not installed.
2026-07-21T20:46:53.8331423Z SKIPPED [1] apache_beam/ml/transforms/embeddings/open_ai_it_test.py:173: OpenAI Python SDK is not installed.
2026-07-21T20:46:53.8333515Z SKIPPED [2] apache_beam/ml/transforms/embeddings/tensorflow_hub_test.py:67: Tensorflow is not installed.
2026-07-21T20:46:53.8335602Z SKIPPED [1] apache_beam/ml/transforms/embeddings/vertex_ai_it_test.py:93: Tensorflow Transform is not installed.
2026-07-21T20:46:53.8338453Z SKIPPED [1] apache_beam/ml/transforms/embeddings/tensorflow_hub_test.py:191: Tensorflow is not installed.
2026-07-21T20:46:53.8340812Z ===== 1 failed, 476 passed, 146 skipped, 104 warnings in 555.28s (0:09:15) =====
2026-07-21T20:46:55.0196649Z Running sequential tests with: pytest -m "(not require_docker_in_docker) and (no_xdist)"  --pyargs  apache_beam/ml/
2026-07-21T20:47:00.6196340Z
2026-07-21T20:47:00.6210252Z --- Applying global testcontainers timeout configuration ---
2026-07-21T20:47:00.6212772Z Successfully set waiting utils config
2026-07-21T20:47:00.6214148Z ============================= test session starts ==============================
2026-07-21T20:47:00.6216636Z platform linux -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- /runner/_work/beam/beam/sdks/python/test-suites/tox/py313/build/srcs/sdks/python/target/.tox-py313-ml/py313-ml/bin/python
2026-07-21T20:47:00.6218631Z cachedir: target/.tox-py313-ml/py313-ml/.pytest_cache
2026-07-21T20:47:00.6220428Z hypothesis profile 'ci' -> database=None, deadline=None, print_blob=True, derandomize=True, suppress_health_check=(HealthCheck.too_slow,)
2026-07-21T20:47:00.6223188Z rootdir: /runner/_work/beam/beam/sdks/python/test-suites/tox/py313/build/srcs/sdks/python
2026-07-21T20:47:00.6224310Z configfile: pytest.ini
2026-07-21T20:47:00.6225283Z plugins: timeout-2.4.0, xdist-3.8.0, hypothesis-6.148.3, langsmith-0.10.9, anyio-4.14.2, requests-mock-1.12.1
2026-07-21T20:47:00.6226429Z timeout: 600.0s
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failure count only, no test named
- **Justification / Notes**: Failure count is shown, but no failed test or method is identified in the raw lines.

---

## 2. `fla-org__flash-linear-attention__082350718781.txt`
- **Section Index**: 2
- **Fixture Filename**: `fla-org__flash-linear-attention__082350718781.txt`
- **Content Hash**: `20031117edd68219`
- **Repository**: `fla-org/flash-linear-attention`
- **Raw Evidence Excerpt**:
```text
2026-06-19T12:37:45.6601689Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-19T12:37:45.6602347Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074: UserWarning: Can't initialize NVML
2026-06-19T12:37:45.6602885Z     raw_cnt = _raw_device_count_nvml()
2026-06-19T12:37:45.6603058Z
2026-06-19T12:37:45.6603319Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: 14 warnings
2026-06-19T12:37:45.6604257Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: DeprecationWarning: `torch.jit.script_method` is deprecated. Please switch to `torch.compile` or `torch.export`.
2026-06-19T12:37:45.6604993Z     warnings.warn(
2026-06-19T12:37:45.6605115Z
2026-06-19T12:37:45.6605321Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-06-19T12:37:45.6605726Z =========================== short test summary info ============================
2026-06-19T12:37:45.6606319Z FAILED tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx[linear_attn] - RuntimeError: No CUDA GPUs are available
2026-06-19T12:37:45.6606891Z !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
2026-06-19T12:37:45.6607261Z ================== 1 failed, 2 skipped, 18 warnings in 0.13s ===================
2026-06-19T12:37:46.6018663Z ##[error]Process completed with exit code 1.
2026-06-19T12:37:46.6128132Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-19T12:37:46.6129368Z Post job cleanup.
2026-06-19T12:37:46.6926100Z [command]/usr/bin/git version
2026-06-19T12:37:46.6955976Z git version 2.34.1
2026-06-19T12:37:46.6981466Z Copying '/home/ubuntu/.gitconfig' to '/home/ubuntu/actions-runner/_work/_temp/6e2783ac-1b77-4f29-bb5a-533cd9e8abcc/.gitconfig'
2026-06-19T12:37:46.6989904Z Temporarily overriding HOME='/home/ubuntu/actions-runner/_work/_temp/6e2783ac-1b77-4f29-bb5a-533cd9e8abcc' before making global git config changes
2026-06-19T12:37:46.6991003Z Adding repository directory to the temporary git global config as a safe directory
2026-06-19T12:37:46.6993519Z [command]/usr/bin/git config --global --add safe.directory /home/ubuntu/actions-runner/_work/flash-linear-attention/flash-linear-attention
2026-06-19T12:37:46.7020529Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-19T12:37:46.7045492Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-19T12:37:46.7225089Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
```
- **Expected Class**: test_layer_cache_layer_idx.py
- **Expected Identifier Count**: 1
- **Expected Identifiers**: tests/layers/test_layer_cache_layer_idx.py::test_cache_requires_layer_idx
- **Justification / Notes**: Explicit pytest FAILED line; bracketed parameter [linear_attn] is dropped.

---

## 3. `apache__beam__082969168132.txt`
- **Section Index**: 3
- **Fixture Filename**: `apache__beam__082969168132.txt`
- **Content Hash**: `ac36f75f37785845`
- **Repository**: `apache/beam`
- **Raw Evidence Excerpt**:
```text
2026-06-23T14:11:31.0193476Z SKIPPED [1] apache_beam/transforms/trigger_test.py:889: Non-fnapi timestamp combiner: OUTPUT_AT_EARLIEST_TRANSFORMED
2026-06-23T14:11:31.0194724Z SKIPPED [2] apache_beam/transforms/trigger_test.py:889: Batch mode only makes sense for accumulating.
2026-06-23T14:11:31.0195820Z SKIPPED [5] apache_beam/transforms/trigger_test.py:889: Batch mode never has late data.
2026-06-23T14:11:31.0227795Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:296: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0229275Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:317: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0230745Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:321: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0232119Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:278: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0233682Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:302: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0235052Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:284: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0236615Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:379: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0238076Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:290: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0239443Z SKIPPED [1] apache_beam/transforms/validate_runner_xlang_test.py:308: EXPANSION_PORT environment var is not provided.
2026-06-23T14:11:31.0241192Z ====== 2 failed, 962 passed, 81 skipped, 21 warnings in 675.12s (0:11:15) ======
2026-06-23T14:11:32.2505195Z Running sequential tests with: pytest -m "no_xdist"  --pyargs  apache_beam/transforms/
2026-06-23T14:11:36.4505008Z
2026-06-23T14:11:36.4539009Z --- Applying global testcontainers timeout configuration ---
2026-06-23T14:11:36.4545321Z Successfully set waiting utils config
2026-06-23T14:11:36.4546174Z ============================= test session starts ==============================
2026-06-23T14:11:36.4563926Z platform linux -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0 -- /runner/_work/beam/beam/sdks/python/test-suites/tox/py314/build/srcs/sdks/python/target/.tox-py314-cloud/py314-cloud/bin/python
2026-06-23T14:11:36.4566111Z cachedir: target/.tox-py314-cloud/py314-cloud/.pytest_cache
2026-06-23T14:11:36.4567781Z hypothesis profile 'ci' -> database=None, deadline=None, print_blob=True, derandomize=True, suppress_health_check=(HealthCheck.too_slow,)
2026-06-23T14:11:36.4569463Z rootdir: /runner/_work/beam/beam/sdks/python/test-suites/tox/py314/build/srcs/sdks/python
2026-06-23T14:11:36.4570593Z configfile: pytest.ini
2026-06-23T14:11:36.4571507Z plugins: timeout-2.4.0, xdist-3.8.0, hypothesis-6.148.3, anyio-4.14.0, requests-mock-1.12.1
2026-06-23T14:11:36.4572539Z timeout: 600.0s
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failure count only, no test named
- **Justification / Notes**: Failure count is shown, but no failed test or method is identified in the raw lines.

---

## 4. `fla-org__flash-linear-attention__082477100071.txt`
- **Section Index**: 4
- **Fixture Filename**: `fla-org__flash-linear-attention__082477100071.txt`
- **Content Hash**: `d2fe7507ebde424d`
- **Repository**: `fla-org/flash-linear-attention`
- **Raw Evidence Excerpt**:
```text
2026-06-20T10:45:37.0999960Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074
2026-06-20T10:45:37.1000640Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/cuda/__init__.py:1074: UserWarning: Can't initialize NVML
2026-06-20T10:45:37.1001211Z     raw_cnt = _raw_device_count_nvml()
2026-06-20T10:45:37.1001374Z
2026-06-20T10:45:37.1001644Z ../../../../miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: 14 warnings
2026-06-20T10:45:37.1002574Z   /home/ubuntu/miniconda3/envs/pytorch_2_12/lib/python3.12/site-packages/torch/jit/_script.py:365: DeprecationWarning: `torch.jit.script_method` is deprecated. Please switch to `torch.compile` or `torch.export`.
2026-06-20T10:45:37.1003318Z     warnings.warn(
2026-06-20T10:45:37.1003447Z
2026-06-20T10:45:37.1003651Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-06-20T10:45:37.1004060Z =========================== short test summary info ============================
2026-06-20T10:45:37.1004751Z FAILED tests/models/test_modeling_nsa.py::test_modeling[L4-B4-T1024-H4-D64-l2True-bsNone-torch.bfloat16] - RuntimeError: No CUDA GPUs are available
2026-06-20T10:45:37.1005386Z !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
2026-06-20T10:45:37.1005751Z ======================== 1 failed, 18 warnings in 0.66s ========================
2026-06-20T10:45:38.2889958Z ##[error]Process completed with exit code 1.
2026-06-20T10:45:38.3006206Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-20T10:45:38.3007423Z Post job cleanup.
2026-06-20T10:45:38.3886478Z [command]/usr/bin/git version
2026-06-20T10:45:38.3922583Z git version 2.34.1
2026-06-20T10:45:38.3963382Z Copying '/home/ubuntu/.gitconfig' to '/home/ubuntu/actions-runner/_work/_temp/91696746-5d5c-4a23-a2f8-40034279c166/.gitconfig'
2026-06-20T10:45:38.3972280Z Temporarily overriding HOME='/home/ubuntu/actions-runner/_work/_temp/91696746-5d5c-4a23-a2f8-40034279c166' before making global git config changes
2026-06-20T10:45:38.3973238Z Adding repository directory to the temporary git global config as a safe directory
2026-06-20T10:45:38.3977606Z [command]/usr/bin/git config --global --add safe.directory /home/ubuntu/actions-runner/_work/flash-linear-attention/flash-linear-attention
2026-06-20T10:45:38.4009121Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-06-20T10:45:38.4037699Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-06-20T10:45:38.4238544Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
```
- **Expected Class**: test_modeling_nsa.py
- **Expected Identifier Count**: 1
- **Expected Identifiers**: tests/models/test_modeling_nsa.py::test_modeling
- **Justification / Notes**: Explicit pytest FAILED line; all bracketed parameters are dropped.

---

## 5. `floci-io__floci__091421214772.txt`
- **Section Index**: 5
- **Fixture Filename**: `floci-io__floci__091421214772.txt`
- **Content Hash**: `9a5131f768d2768d`
- **Repository**: `floci-io/floci`
- **Raw Evidence Excerpt**:
```text
2026-08-01T22:24:37.5232655Z tests/test_ses_templates.py: 66 warnings
2026-08-01T22:24:37.5232901Z tests/test_sns.py: 53 warnings
2026-08-01T22:24:37.5233114Z tests/test_sqs.py: 74 warnings
2026-08-01T22:24:37.5233326Z tests/test_ssm.py: 38 warnings
2026-08-01T22:24:37.5233539Z tests/test_sts.py: 7 warnings
2026-08-01T22:24:37.5234488Z   /usr/local/lib/python3.12/site-packages/botocore/auth.py:425: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
2026-08-01T22:24:37.5235498Z     datetime_now = datetime.datetime.utcnow()
2026-08-01T22:24:37.5235737Z
2026-08-01T22:24:37.5235946Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-08-01T22:24:37.5236396Z -------------------- generated xml file: /results/junit.xml --------------------
2026-08-01T22:24:37.5236790Z =========================== short test summary info ============================
2026-08-01T22:24:37.5237595Z FAILED tests/test_sagemaker.py::test_sagemaker_control_plane_and_training - botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "http://localhost:4566/"
2026-08-01T22:24:37.5238401Z =========== 1 failed, 311 passed, 1317 warnings in 74.56s (0:01:14) ============
2026-08-01T22:24:37.8318657Z ##[error]Process completed with exit code 1.
2026-08-01T22:24:37.8397536Z ##[group]Run test-summary/action@37b508cfee6d4d080eedd00b5bb240a6a784a6a5
2026-08-01T22:24:37.8397922Z with:
2026-08-01T22:24:37.8398099Z   paths: test-results/*.xml
2026-08-01T22:24:37.8398304Z ##[endgroup]
2026-08-01T22:24:37.9035541Z ##[group]Run docker logs floci
2026-08-01T22:24:37.9035843Z docker logs floci
2026-08-01T22:24:37.9060230Z shell: /usr/bin/bash -e {0}
2026-08-01T22:24:37.9060482Z ##[endgroup]
2026-08-01T22:24:37.9205902Z  _____  _      ___   ____   __
2026-08-01T22:24:37.9211201Z |  ___|| |    / _ \ / ___| | |
2026-08-01T22:24:37.9211860Z | |_   | |   | | | || |    | |
```
- **Expected Class**: test_sagemaker.py
- **Expected Identifier Count**: 1
- **Expected Identifiers**: tests/test_sagemaker.py::test_sagemaker_control_plane_and_training
- **Justification / Notes**: Explicit pytest FAILED line.

---

## 6. `dask__distributed__084757050312.txt`
- **Section Index**: 6
- **Fixture Filename**: `dask__distributed__084757050312.txt`
- **Content Hash**: `de3a23f971790d6f`
- **Repository**: `dask/distributed`
- **Raw Evidence Excerpt**:
```text
2026-07-02T11:17:54.1137996Z 0.43s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[98-100]
2026-07-02T11:17:54.1138576Z 0.43s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[95-100]
2026-07-02T11:17:54.1139278Z 0.43s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[81-100]
2026-07-02T11:17:54.1139864Z 0.43s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[100-100]
2026-07-02T11:17:54.1140447Z 0.43s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[89-100]
2026-07-02T11:17:54.1141024Z 0.43s call     distributed/tests/test_nanny.py::test_failure_during_worker_initialization[87-100]
2026-07-02T11:17:54.1141663Z =========================== short test summary info ============================
2026-07-02T11:17:54.1142765Z FAILED distributed/tests/test_nanny.py::test_failure_during_worker_initialization[76-100] - asyncio.exceptions.TimeoutError: Test timeout (30) hit after 30.001440683999988s.
2026-07-02T11:17:54.1143502Z ========== Test stack trace starts here ==========
2026-07-02T11:17:54.1144453Z Stack for <Task pending name='Task-1430' coro=<test_failure_during_worker_initialization() running at /home/runner/work/distributed/distributed/distributed/tests/test_nanny.py:637> wait_for=<Future pending cb=[Task.task_wakeup()]>> (most recent call last):
2026-07-02T11:17:54.1145725Z   File "/home/runner/work/distributed/distributed/distributed/tests/test_nanny.py", line 637, in test_failure_during_worker_initialization
2026-07-02T11:17:54.1146419Z     await Nanny(s.address, foo="bar")
2026-07-02T11:17:54.1147028Z ============== 1 failed, 99 passed, 1 leaked in 75.33s (0:01:15) ===============
2026-07-02T11:17:54.4342834Z ##[error]Process completed with exit code 1.
2026-07-02T11:17:54.4395210Z ##[group]Run pixi run post-test-ci
2026-07-02T11:17:54.4395545Z pixi run post-test-ci
2026-07-02T11:17:54.4414344Z shell: /usr/bin/bash -e {0}
2026-07-02T11:17:54.4414580Z env:
2026-07-02T11:17:54.4414778Z   TEST_ID: ubuntu-24.04-arm-py310-test-ci-ci1
2026-07-02T11:17:54.4415064Z   DISABLE_IPV6: 1
2026-07-02T11:17:54.4415240Z ##[endgroup]
2026-07-02T11:17:54.6881549Z ✨ Pixi task (post-test-ci in default): bash continuous_integration/scripts/post_test_ci.sh
2026-07-02T11:18:03.9738987Z Wrote XML report to coverage.xml
2026-07-02T11:18:04.1135442Z ##[group]Run codecov/codecov-action@v7
2026-07-02T11:18:04.1135750Z with:
```
- **Expected Class**: test_nanny.py
- **Expected Identifier Count**: 1
- **Expected Identifiers**: distributed/tests/test_nanny.py::test_failure_during_worker_initialization
- **Justification / Notes**: Explicit pytest FAILED line; bracketed parameter [76-100] is dropped. The stack trace repeats the same test.

---

## 7. `floci-io__floci__089834122110.txt`
- **Section Index**: 7
- **Fixture Filename**: `floci-io__floci__089834122110.txt`
- **Content Hash**: `3c332a181e22fc2b`
- **Repository**: `floci-io/floci`
- **Raw Evidence Excerpt**:
```text
2026-07-26T19:48:11.6825792Z tests/test_ses_templates.py: 66 warnings
2026-07-26T19:48:11.6826040Z tests/test_sns.py: 53 warnings
2026-07-26T19:48:11.6826257Z tests/test_sqs.py: 74 warnings
2026-07-26T19:48:11.6826468Z tests/test_ssm.py: 38 warnings
2026-07-26T19:48:11.6826681Z tests/test_sts.py: 7 warnings
2026-07-26T19:48:11.6827638Z   /usr/local/lib/python3.12/site-packages/botocore/auth.py:425: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
2026-07-26T19:48:11.6828658Z     datetime_now = datetime.datetime.utcnow()
2026-07-26T19:48:11.6828850Z
2026-07-26T19:48:11.6829029Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-07-26T19:48:11.6829479Z -------------------- generated xml file: /results/junit.xml --------------------
2026-07-26T19:48:11.6829875Z =========================== short test summary info ============================
2026-07-26T19:48:11.6830934Z FAILED tests/test_sagemaker.py::test_sagemaker_control_plane_and_training - botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "http://localhost:4566/"
2026-07-26T19:48:11.6831750Z =========== 1 failed, 311 passed, 1317 warnings in 75.11s (0:01:15) ============
2026-07-26T19:48:11.9397107Z ##[error]Process completed with exit code 1.
2026-07-26T19:48:11.9476548Z ##[group]Run test-summary/action@37b508cfee6d4d080eedd00b5bb240a6a784a6a5
2026-07-26T19:48:11.9476923Z with:
2026-07-26T19:48:11.9477093Z   paths: test-results/*.xml
2026-07-26T19:48:11.9477296Z ##[endgroup]
2026-07-26T19:48:12.0105094Z ##[group]Run docker logs floci
2026-07-26T19:48:12.0105418Z docker logs floci
2026-07-26T19:48:12.0129691Z shell: /usr/bin/bash -e {0}
2026-07-26T19:48:12.0129916Z ##[endgroup]
2026-07-26T19:48:12.0271316Z  _____  _      ___   ____   __
2026-07-26T19:48:12.0271768Z |  ___|| |    / _ \ / ___| | |
2026-07-26T19:48:12.0271995Z | |_   | |   | | | || |    | |
```
- **Expected Class**: test_sagemaker.py
- **Expected Identifier Count**: 1
- **Expected Identifiers**: tests/test_sagemaker.py::test_sagemaker_control_plane_and_training
- **Justification / Notes**: Explicit pytest FAILED line.

---

## 8. `apache__flink__080107589164.txt`
- **Section Index**: 8
- **Fixture Filename**: `apache__flink__080107589164.txt`
- **Content Hash**: `7a09d1d6354aa713`
- **Repository**: `apache/flink`
- **Raw Evidence Excerpt**:
```text
2026-06-08T13:56:54.7658880Z Jun 08 13:56:54 5.08s teardown pyflink/datastream/tests/test_data_stream.py::EmbeddedDataStreamBatchTests::test_side_output_tag_reusing
2026-06-08T13:56:54.7660396Z Jun 08 13:56:54 4.15s call     pyflink/datastream/tests/test_async_function.py::AsyncFunctionTests::test_processing_timeout
2026-06-08T13:56:54.7661757Z Jun 08 13:56:54 3.59s call     pyflink/datastream/tests/test_data_stream.py::ProcessDataStreamBatchTests::test_partition_custom
2026-06-08T13:56:54.7663002Z Jun 08 13:56:54 3.53s call     pyflink/datastream/formats/tests/test_avro.py::FileSourceAvroInputFormatTests::test_avro_array_read
2026-06-08T13:56:54.7664246Z Jun 08 13:56:54 3.50s call     pyflink/datastream/connectors/tests/test_file_system.py::FileSystemTests::test_stream_file_sink
2026-06-08T13:56:54.7665524Z Jun 08 13:56:54 3.42s call     pyflink/datastream/tests/test_async_function.py::AsyncFunctionTests::test_raise_exception_in_timeout
2026-06-08T13:56:54.7666874Z Jun 08 13:56:54 3.24s call     pyflink/datastream/tests/test_data_stream.py::ProcessDataStreamBatchTests::test_basic_co_operations
2026-06-08T13:56:54.7668112Z Jun 08 13:56:54 3.22s call     pyflink/datastream/tests/test_async_function.py::AsyncFunctionTests::test_non_iterable_result
2026-06-08T13:56:54.7669524Z Jun 08 13:56:54 3.22s call     pyflink/datastream/tests/test_data_stream.py::ProcessDataStreamBatchTests::test_basic_co_operations_with_output_type
2026-06-08T13:56:54.7671273Z Jun 08 13:56:54 3.05s setup    pyflink/datastream/connectors/tests/test_cassandra.py::CassandraSinkTest::test_cassandra_sink
2026-06-08T13:56:54.7671929Z Jun 08 13:56:54 =========================== short test summary info ============================
2026-06-08T13:56:54.7672956Z Jun 08 13:56:54 FAILED pyflink/datastream/tests/test_stream_execution_environment.py::StreamExecutionEnvironmentTests::test_generate_stream_graph_with_dependencies - FileNotFoundError: [Errno 2] No such file or directory
2026-06-08T13:56:54.7673943Z Jun 08 13:56:54 ====== 1 failed, 280 passed, 59 skipped, 15 warnings in 301.43s (0:05:01) ======
2026-06-08T13:56:54.9784055Z Jun 08 13:56:54 test module /root/flink/flink-python/pyflink/datastream failed
2026-06-08T13:56:54.9785220Z Jun 08 13:56:54 ERROR: InvocationError for command /usr/bin/bash ./dev/integration_test.sh (exited with code 1)
2026-06-08T13:56:54.9786191Z Jun 08 13:56:54 py39-cython finish: run-test  after 303.93 seconds
2026-06-08T13:56:54.9786827Z Jun 08 13:56:54 py39-cython start: run-test-post
2026-06-08T13:56:54.9787468Z Jun 08 13:56:54 py39-cython finish: run-test-post  after 0.00 seconds
2026-06-08T13:56:54.9788223Z Jun 08 13:56:54 ___________________________________ summary ____________________________________
2026-06-08T13:56:54.9788927Z Jun 08 13:56:54 ERROR:   py39-cython: commands failed
2026-06-08T13:56:54.9789834Z Jun 08 13:56:54 cleanup /root/flink/flink-python/.tox/.tmp/package/1/apache_flink-2.3.dev0.zip
2026-06-08T13:56:55.0224574Z Jun 08 13:56:55 ============tox checks... [FAILED]============
2026-06-08T13:56:55.0230666Z ./flink-python/dev/lint-python.sh: line 593: deactivate: command not found
2026-06-08T13:56:55.0252216Z Jun 08 13:56:55 Process exited with EXIT CODE: 1.
2026-06-08T13:56:55.0253121Z Jun 08 13:56:55 Trying to KILL watchdog (1655).
```
- **Expected Class**: test_stream_execution_environment.py
- **Expected Identifier Count**: 1
- **Expected Identifiers**: pyflink/datastream/tests/test_stream_execution_environment.py::test_generate_stream_graph_with_dependencies
- **Justification / Notes**: Explicit pytest FAILED line; nearby test listing and failure line identify the test.

---

## 9. `farama-foundation__highwayenv__082832194425.txt`
- **Section Index**: 9
- **Fixture Filename**: `farama-foundation__highwayenv__082832194425.txt`
- **Content Hash**: `2b70a6572e313d07`
- **Repository**: `farama-foundation/highwayenv`
- **Raw Evidence Excerpt**:
```text
2026-06-22T22:12:44.9185405Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: WARN: The environment u-turn-v0 is out of date. You should consider upgrading to version `v1`.
2026-06-22T22:12:44.9186225Z     logger.deprecation(
2026-06-22T22:12:44.9186353Z
2026-06-22T22:12:44.9186717Z tests/envs/test_gym.py::test_connected_lane_neighbour_versions[intersection-multi-agent-v0-intersection-multi-agent-v2]
2026-06-22T22:12:44.9188014Z   /opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/gymnasium/envs/registration.py:513: DeprecationWarning: WARN: The environment intersection-multi-agent-v0 is out of date. You should consider upgrading to version `v2`.
2026-06-22T22:12:44.9188900Z     logger.deprecation(
2026-06-22T22:12:44.9189037Z
2026-06-22T22:12:44.9189242Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-06-22T22:12:44.9189815Z ================================ tests coverage ================================
2026-06-22T22:12:44.9190342Z _______________ coverage: platform linux, python 3.11.15-final-0 _______________
2026-06-22T22:12:44.9190618Z
2026-06-22T22:12:44.9190730Z Coverage XML written to file coverage.xml
2026-06-22T22:12:44.9191080Z ============ 108 passed, 2 skipped, 27 warnings in 77.07s (0:01:17) ============
2026-06-22T22:12:45.1215826Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-22T22:12:45.1216996Z Post job cleanup.
2026-06-22T22:12:45.2377255Z (node:4278) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-06-22T22:12:45.2378393Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-06-22T22:12:45.2519237Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-06-22T22:12:45.2520505Z Post job cleanup.
2026-06-22T22:12:45.3317246Z [command]/usr/bin/git version
2026-06-22T22:12:45.3351256Z git version 2.54.0
2026-06-22T22:12:45.3384227Z Temporarily overriding HOME='/home/runner/work/_temp/585d7c5a-b0eb-40e0-912b-bce133bf86ef' before making global git config changes
2026-06-22T22:12:45.3385688Z Adding repository directory to the temporary git global config as a safe directory
2026-06-22T22:12:45.3389598Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/HighwayEnv/HighwayEnv
2026-06-22T22:12:45.3425334Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no failed test identified
- **Justification / Notes**: The visible test line is not marked failed and the summary shows all tests passed.

---

## 10. `agno-agi__agno__096352887725.txt`
- **Section Index**: 10
- **Fixture Filename**: `agno-agi__agno__096352887725.txt`
- **Content Hash**: `6c24a57a5bbb169b`
- **Repository**: `agno-agi/agno`
- **Raw Evidence Excerpt**:
```text
2026-08-20T07:44:27.0279889Z tests/test_connect_cmd.py .............................................. [ 33%]
2026-08-20T07:44:27.2346629Z ....................                                                     [ 39%]
2026-08-20T07:44:29.1489452Z tests/test_create_lifecycle.py ......................................... [ 51%]
2026-08-20T07:44:29.2859880Z ............................                                             [ 59%]
2026-08-20T07:44:29.5675737Z tests/test_disconnect_cmd.py .........................                   [ 66%]
2026-08-20T07:44:29.6451468Z tests/test_discovery.py .....................................            [ 77%]
2026-08-20T07:44:29.6760881Z tests/test_main.py ....                                                  [ 78%]
2026-08-20T07:44:29.6919921Z tests/test_mcp_client.py ..........                                      [ 81%]
2026-08-20T07:44:29.7202331Z tests/test_security.py .......................................           [ 93%]
2026-08-20T07:44:29.7470014Z tests/test_status_cmd.py ...                                             [ 93%]
2026-08-20T07:44:29.9582655Z tests/test_tokens_cmd.py .....................                           [100%]
2026-08-20T07:44:29.9583661Z
2026-08-20T07:44:29.9583913Z ============================= 344 passed in 4.44s ==============================
2026-08-20T07:44:30.0441136Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-20T07:44:30.0442320Z Post job cleanup.
2026-08-20T07:44:30.1688904Z Cache hit occurred on the primary key setup-python-Linux-24.04-Ubuntu-python-3.10.20-pip-02800bd8c2c2b72a3c51ab0caea6aeb5c2ca083ad4867f939181bef45cb0531a, not saving cache.
2026-08-20T07:44:30.1690608Z (node:2405) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-08-20T07:44:30.1691308Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-08-20T07:44:30.1852498Z Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to temporarily use Node 20, you can set the ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true environment variable. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
2026-08-20T07:44:30.1853675Z Post job cleanup.
2026-08-20T07:44:30.2560240Z (node:2413) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
2026-08-20T07:44:30.2561005Z (Use `node --trace-deprecation ...` to show where the warning was created)
2026-08-20T07:44:30.2589597Z [command]/usr/bin/git version
2026-08-20T07:44:30.2625480Z git version 2.54.0
2026-08-20T07:44:30.2662697Z Temporarily overriding HOME='/home/runner/work/_temp/bb3c065f-da20-4be1-9a55-2a7b0ba329a0' before making global git config changes
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no failed test identified
- **Justification / Notes**: The raw lines show 344 passed tests and no failed test.

---

## 11. `diffplug__spotless__095081359640.txt`
- **Section Index**: 11
- **Fixture Filename**: `diffplug__spotless__095081359640.txt`
- **Content Hash**: `f92db7c79c52d4f3`
- **Repository**: `diffplug/spotless`
- **Raw Evidence Excerpt**:
```text
2026-08-15T23:02:35.4147182Z
2026-08-15T23:02:35.4296520Z   java.util.NoSuchElementException: Resolved to an empty result: org.eclipse.jdt:org.eclipse.jdt.core:3.46.0, net.java.dev.jna:jna-platform:5.18.1, org.eclipse.jdt:ecj:3.46.0, org.eclipse.platform:org.eclipse.core.commands:3.12.500, org.eclipse.platform:org.eclipse.core.contenttype:3.9.800, org.eclipse.platform:org.eclipse.core.expressions:3.9.600, org.eclipse.platform:org.eclipse.core.filesystem:1.11.400, org.eclipse.platform:org.eclipse.core.jobs:3.15.800, org.eclipse.platform:org.eclipse.core.resources:3.24.0, org.eclipse.platform:org.eclipse.core.runtime:3.34.200, org.eclipse.platform:org.eclipse.equinox.app:1.7.600, org.eclipse.platform:org.eclipse.equinox.common:3.20.400, org.eclipse.platform:org.eclipse.equinox.preferences:3.12.100, org.eclipse.platform:org.eclipse.equinox.registry:3.12.600, org.eclipse.platform:org.eclipse.equinox.supplement:1.12.300, org.eclipse.platform:org.eclipse.osgi:3.24.200, org.eclipse.platform:org.eclipse.text:3.14.700, org.osgi:org.osgi.service.prefs:1.1.2
2026-08-15T23:02:35.4303094Z       at com.diffplug.spotless.maven.FormatterStepFactoryTest.assertP2ProvisionerReceives(FormatterStepFactoryTest.java:121)
2026-08-15T23:02:35.4304517Z
2026-08-15T23:02:35.4305580Z com.diffplug.spotless.maven.FormatterStepFactoryTest eclipseUsesDefaultCacheDirectory() FAILED
2026-08-15T23:02:35.4306415Z
2026-08-15T23:02:35.4314820Z   java.util.NoSuchElementException: Resolved to an empty result: org.eclipse.jdt:org.eclipse.jdt.core:3.46.0, net.java.dev.jna:jna-platform:5.18.1, org.eclipse.jdt:ecj:3.46.0, org.eclipse.platform:org.eclipse.core.commands:3.12.500, org.eclipse.platform:org.eclipse.core.contenttype:3.9.800, org.eclipse.platform:org.eclipse.core.expressions:3.9.600, org.eclipse.platform:org.eclipse.core.filesystem:1.11.400, org.eclipse.platform:org.eclipse.core.jobs:3.15.800, org.eclipse.platform:org.eclipse.core.resources:3.24.0, org.eclipse.platform:org.eclipse.core.runtime:3.34.200, org.eclipse.platform:org.eclipse.equinox.app:1.7.600, org.eclipse.platform:org.eclipse.equinox.common:3.20.400, org.eclipse.platform:org.eclipse.equinox.preferences:3.12.100, org.eclipse.platform:org.eclipse.equinox.registry:3.12.600, org.eclipse.platform:org.eclipse.equinox.supplement:1.12.300, org.eclipse.platform:org.eclipse.osgi:3.24.200, org.eclipse.platform:org.eclipse.text:3.14.700, org.osgi:org.osgi.service.prefs:1.1.2
2026-08-15T23:02:35.4321955Z       at com.diffplug.spotless.maven.FormatterStepFactoryTest.assertP2ProvisionerReceives(FormatterStepFactoryTest.java:121)
2026-08-15T23:02:35.4323566Z
2026-08-15T23:02:35.5632035Z
2026-08-15T23:02:35.5632071Z
2026-08-15T23:02:35.5634579Z FAILURE: Executed 233 tests in 7m 10s (6 failed, 2 skipped)
2026-08-15T23:02:35.5635412Z 233 tests completed, 6 failed, 2 skipped
2026-08-15T23:02:35.5636188Z
2026-08-15T23:02:35.7012998Z
2026-08-15T23:02:35.7013643Z > Task :plugin-maven:test FAILED
2026-08-15T23:02:35.7014276Z gradle/actions: Writing build results to D:\a\_temp\.gradle-actions\build-results\__run-1786834469843.json
2026-08-15T23:02:35.8141579Z
2026-08-15T23:02:35.8141615Z
2026-08-15T23:02:35.8142817Z FAILURE: Build failed with an exception.
2026-08-15T23:02:35.8144206Z [Incubating] Problems report is available at: file:///D:/a/spotless/spotless/build/reports/problems/problems-report.html
2026-08-15T23:02:35.8144894Z
2026-08-15T23:02:35.8145054Z * What went wrong:
2026-08-15T23:02:35.8145470Z Execution failed for task ':plugin-maven:test'.
2026-08-15T23:02:35.8146290Z > There were failing tests. See the report at: file:///D:/a/spotless/spotless/plugin-maven/build/reports/tests/test/index.html
```
- **Expected Class**: com.diffplug.spotless.maven.FormatterStepFactoryTest
- **Expected Identifier Count**: 1
- **Expected Identifiers**: com.diffplug.spotless.maven.FormatterStepFactoryTest#eclipseUsesDefaultCacheDirectory
- **Justification / Notes**: Explicit Java failure line plus stack frame supplies the package.

---

## 12. `Stirling-Tools__Stirling-PDF__089792061823.txt`
- **Section Index**: 12
- **Fixture Filename**: `Stirling-Tools__Stirling-PDF__089792061823.txt`
- **Content Hash**: `47a1c37d5b33ee63`
- **Repository**: `Stirling-Tools/Stirling-PDF`
- **Raw Evidence Excerpt**:
```text
2026-07-26T12:11:47.0632120Z Note: Some input files use or override a deprecated API.
2026-07-26T12:11:47.0633018Z
2026-07-26T12:11:47.0633465Z Note: Recompile with -Xlint:deprecation for details.
2026-07-26T12:11:47.0634231Z > Task :***-pdf:compileTestJava
2026-07-26T12:11:47.0667624Z Note: Some input files use unchecked or unsafe operations.
2026-07-26T12:11:47.0693324Z Note: Recompile with -Xlint:unchecked for details.
2026-07-26T12:11:56.0610087Z
2026-07-26T12:11:56.0610638Z > Task :common:test
2026-07-26T12:11:56.0611065Z
2026-07-26T12:11:56.0611760Z JarPathUtilTest > restartHelperJar_notFound_returnsNull() FAILED
2026-07-26T12:11:56.0612919Z     org.opentest4j.AssertionFailedError at JarPathUtilTest.java:22
2026-07-26T12:12:01.2610340Z
2026-07-26T12:12:01.2612279Z 1859 tests completed, 1 failed, 5 skipped
2026-07-26T12:12:01.9623376Z
2026-07-26T12:12:01.9663761Z FAILURE: Build completed with 2 failures.
2026-07-26T12:12:01.9664237Z
2026-07-26T12:12:01.9664866Z > Task :common:test FAILED
2026-07-26T12:12:01.9673168Z
2026-07-26T12:12:01.9683756Z 1: Task failed with an exception.
2026-07-26T12:12:01.9684883Z -----------
2026-07-26T12:12:01.9685434Z * What went wrong:
2026-07-26T12:12:01.9686585Z Execution failed for task ':proprietary:compileTestJava' (registered by plugin class 'org.gradle.api.plugins.JavaBasePlugin').
2026-07-26T12:12:01.9687888Z > Compilation failed; see the compiler output below.
2026-07-26T12:12:01.9690162Z   /home/runner/work/Stirling-PDF/Stirling-PDF/app/proprietary/src/test/java/***/software/proprietary/security/controller/api/AdminSettingsControllerTest.java:609: error: unreported exception IOException; must be caught or declared to be thrown
2026-07-26T12:12:01.9692554Z gradle/actions: Writing build results to /home/runner/work/_temp/.gradle-actions/build-results/__run_4-1785067803705.json
```
- **Expected Class**: JarPathUtilTest
- **Expected Identifier Count**: 1
- **Expected Identifiers**: JarPathUtilTest#restartHelperJar_notFound_returnsNull
- **Justification / Notes**: The failed Java test is named, but no package for JarPathUtilTest appears in the section; do not infer one.

---

## 13. `baomidou__mybatis-plus__083974450312.txt`
- **Section Index**: 13
- **Fixture Filename**: `baomidou__mybatis-plus__083974450312.txt`
- **Content Hash**: `4e00f1214cfd9154`
- **Repository**: `baomidou/mybatis-plus`
- **Raw Evidence Excerpt**:
```text
2026-06-29T04:03:53.6661772Z Note: Recompile with -Xlint:removal for details.
2026-06-29T04:03:53.6714801Z 14 warnings
2026-06-29T04:03:56.6621444Z
2026-06-29T04:03:56.6632067Z > Task :mybatis-plus-core:testClasses
2026-06-29T04:03:58.1608263Z > Task :mybatis-plus-extension:compileKotlin
2026-06-29T04:03:59.8607372Z OpenJDK 64-Bit Server VM warning: Sharing is only supported for boot loader classes because bootstrap classpath has been appended
2026-06-29T04:04:00.7631504Z
2026-06-29T04:04:00.7642662Z > Task :mybatis-plus-core:test
2026-06-29T04:04:00.7670266Z
2026-06-29T04:04:00.7682870Z MybatisConfigurationTest > testReload() FAILED
2026-06-29T04:04:00.7701574Z     org.opentest4j.AssertionFailedError at MybatisConfigurationTest.java:126
2026-06-29T04:04:01.2606970Z
2026-06-29T04:04:01.2608776Z 165 tests completed, 1 failed, 23 skipped
2026-06-29T04:04:01.3621434Z
2026-06-29T04:04:01.3621460Z
2026-06-29T04:04:01.3647157Z FAILURE: Build failed with an exception.
2026-06-29T04:04:01.3647788Z > Task :mybatis-plus-core:test FAILED
2026-06-29T04:04:01.3648892Z > Task :mybatis-plus-generator:generateEffectiveLombokConfig
2026-06-29T04:04:01.3649688Z > Task :mybatis-plus-extension:generateTestEffectiveLombokConfig
2026-06-29T04:04:01.3649987Z
2026-06-29T04:04:01.3650453Z [Incubating] Problems report is available at: file:///home/runner/work/mybatis-plus/mybatis-plus/build/reports/problems/problems-report.html
2026-06-29T04:04:01.3651489Z
2026-06-29T04:04:01.3651930Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 9.0.
2026-06-29T04:04:01.3652502Z
2026-06-29T04:04:01.3653495Z You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
```
- **Expected Class**: MybatisConfigurationTest
- **Expected Identifier Count**: 1
- **Expected Identifiers**: MybatisConfigurationTest#testReload
- **Justification / Notes**: The failed Java test is named, but no package for MybatisConfigurationTest appears in the section; do not infer one.

---

## 14. `sirixdb__sirix__092355497985.txt`
- **Section Index**: 14
- **Fixture Filename**: `sirixdb__sirix__092355497985.txt`
- **Content Hash**: `4a40b85a5c74b1aa`
- **Repository**: `sirixdb/sirix`
- **Raw Evidence Excerpt**:
```text
2026-08-05T15:35:53.3476203Z     [sirix-vec] compileToClass failed for Crating:gt:2.5;|f:rating,dept#gb:dept — falling back (IllegalStateException: unsupported opcode 9)
2026-08-05T15:35:53.3477184Z
2026-08-05T15:35:53.3477614Z TypedGroupByDifferentialTest > projectionTwoStringKeys() STANDARD_OUT
2026-08-05T15:35:53.3478666Z     # Projection persisted: 2 leaves, raw 82,148 bytes -> compact 7,630 bytes (9.3%)
2026-08-05T15:35:53.4474892Z
2026-08-05T15:35:53.4476098Z TypedGroupByDifferentialTest > projectionSumOverDoubleField() STANDARD_OUT
2026-08-05T15:35:53.4476791Z     # Projection persisted: 2 leaves, raw 82,148 bytes -> compact 7,630 bytes (9.3%)
2026-08-05T15:35:54.5474879Z
2026-08-05T15:35:54.5475590Z Gradle Test Executor 1 finished executing tests.
2026-08-05T15:35:54.6475258Z # [StorageProfile] dump called: enabled=false byKind.size=0
2026-08-05T15:35:54.9511507Z
2026-08-05T15:35:54.9511531Z
2026-08-05T15:35:54.9512187Z 1054 tests completed, 3 failed, 4 skipped
2026-08-05T15:35:54.9512819Z > Task :sirix-query:test FAILED
2026-08-05T15:35:54.9513272Z
2026-08-05T15:35:54.9513280Z
2026-08-05T15:35:54.9513698Z FAILURE: Build failed with an exception.
2026-08-05T15:35:54.9514242Z ===== FAILED TESTS (3) =====
2026-08-05T15:35:54.9514656Z
2026-08-05T15:35:54.9516268Z FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > negationConjoinedWithAnAnchoringLeafIsRepresentable(): org.opentest4j.AssertionFailedError: predicate not claimed at all: $u.year gt 1990 and not($u.active) ==> expected: <true> but was: <false>
2026-08-05T15:35:54.9518423Z * What went wrong:
2026-08-05T15:35:54.9520309Z FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > numericAndBooleanFuseIntoOnePass(): org.opentest4j.AssertionFailedError: no page served from the fused columns for $u.year gt 1990 and not($u.active) (served=0, fellBack=0) ==> expected: <true> but was: <false>
2026-08-05T15:35:54.9522704Z Execution failed for task ':sirix-query:test'.
2026-08-05T15:35:54.9524852Z FAILED-TEST: io.sirix.query.scan.RegionOnlyPredicateCountTest > multiFieldConjunctionsAreAnsweredFromColumns(): org.opentest4j.AssertionFailedError: no page served from the fused columns for $u.year gt 1950 and $u.id lt 15000 and not($u.active) (served=0, fellBack=0) ==> expected: <true> but was: <false>
2026-08-05T15:35:54.9527731Z > There were failing tests. See the report at: file:///home/runner/work/sirix/sirix/bundles/sirix-query/build/reports/tests/test/index.html
```
- **Expected Class**: io.sirix.query.scan.RegionOnlyPredicateCountTest
- **Expected Identifier Count**: 3
- **Expected Identifiers**: io.sirix.query.scan.RegionOnlyPredicateCountTest#negationConjoinedWithAnAnchoringLeafIsRepresentable; io.sirix.query.scan.RegionOnlyPredicateCountTest#numericAndBooleanFuseIntoOnePass; io.sirix.query.scan.RegionOnlyPredicateCountTest#multiFieldConjunctionsAreAnsweredFromColumns
- **Justification / Notes**: Three FAILED-TEST lines identify the class and all three methods; the package is explicitly visible.

---

## 15. `openremote__openremote__086930896418.txt`
- **Section Index**: 15
- **Fixture Filename**: `openremote__openremote__086930896418.txt`
- **Content Hash**: `5abd32671222f73a`
- **Repository**: `openremote/openremote`
- **Raw Evidence Excerpt**:
```text
2026-07-13T21:03:47.0332000Z org.openremote.test.users.UserResourceTest > Create user requires realm administration rights took: 74ms
2026-07-13T21:03:47.0341451Z   Test Create user requires realm administration rights PASSED
2026-07-13T21:03:47.1313230Z org.openremote.test.users.UserResourceTest > Reset secret requires realm administration rights took: 50ms
2026-07-13T21:03:47.1314040Z   Test Reset secret requires realm administration rights PASSED
2026-07-13T21:03:47.2315355Z org.openremote.test.users.UserResourceTest > Update user client roles requires realm administration rights took: 151ms
2026-07-13T21:03:47.2319877Z   Test Update user client roles requires realm administration rights PASSED
2026-07-13T21:03:47.3313682Z org.openremote.test.users.UserResourceTest > Update default client roles requires realm administration rights took: 69ms
2026-07-13T21:03:47.3329443Z   Test Update default client roles requires realm administration rights PASSED
2026-07-13T21:03:47.3337779Z org.openremote.test.users.UserResourceTest > Update client roles requires realm administration rights took: 68ms
2026-07-13T21:03:47.3378516Z   Test Update client roles requires realm administration rights PASSED
2026-07-13T21:03:53.2391861Z
2026-07-13T21:03:53.2529455Z
2026-07-13T21:03:53.2829971Z 365 tests completed, 1 failed, 18 skipped
2026-07-13T21:03:53.2830456Z --------------------------------------------------------------------
2026-07-13T21:03:53.3009947Z |  Results: FAILURE (365 tests, 346 passed, 1 failed, 18 skipped)  |
2026-07-13T21:03:53.3161529Z --------------------------------------------------------------------
2026-07-13T21:03:53.3311920Z
2026-07-13T21:03:53.3610393Z FAILURE: Executed 365 tests in 12m 48s (1 failed, 18 skipped)
2026-07-13T21:03:53.3759452Z
2026-07-13T21:03:56.2314181Z
2026-07-13T21:03:56.2314911Z > Task :test:test FAILED
2026-07-13T21:03:56.2315133Z
2026-07-13T21:03:56.2315810Z [Incubating] Problems report is available at: file:///home/runner/work/openremote/openremote/build/reports/problems/problems-report.html
2026-07-13T21:03:56.3312664Z
2026-07-13T21:03:56.3315733Z FAILURE: Build failed with an exception.
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failure count only, no test named
- **Justification / Notes**: The section reports one failed test but does not identify its name or method.

---

## 16. `baomidou__mybatis-plus__084235124274.txt`
- **Section Index**: 16
- **Fixture Filename**: `baomidou__mybatis-plus__084235124274.txt`
- **Content Hash**: `29b095d8eba7ab0f`
- **Repository**: `baomidou/mybatis-plus`
- **Raw Evidence Excerpt**:
```text
2026-06-30T07:31:52.8467417Z 07:31:52.808 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@5dff108c, started on Tue Jun 30 07:31:43 UTC 2026
2026-06-30T07:31:52.8468728Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@77e2a5d3, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8470045Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@217abcc9, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8471367Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@c9518ee, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8473444Z 07:31:52.810 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@41fbe8c0, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8475484Z 07:31:52.811 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@15549dd7, started on Tue Jun 30 07:31:42 UTC 2026
2026-06-30T07:31:52.8477517Z 07:31:52.812 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@331fe6d4, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8479874Z 07:31:52.812 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@62243a7a, started on Tue Jun 30 07:31:49 UTC 2026
2026-06-30T07:31:52.8481547Z 07:31:52.814 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@75c2a35, started on Tue Jun 30 07:31:52 UTC 2026
2026-06-30T07:31:52.8483210Z 07:31:52.814 [SpringContextShutdownHook] DEBUG o.s.c.s.GenericApplicationContext - Closing org.springframework.context.support.GenericApplicationContext@746da54f, started on Tue Jun 30 07:31:42 UTC 2026
2026-06-30T07:31:52.9473109Z
2026-06-30T07:31:52.9473135Z
2026-06-30T07:31:52.9512595Z 1239 tests completed, 2 failed, 1 skipped
2026-06-30T07:31:52.9513167Z > Task :mybatis-plus:test
2026-06-30T07:31:53.4465145Z
2026-06-30T07:31:53.4483719Z > Task :mybatis-plus:test FAILED
2026-06-30T07:31:53.4484513Z
2026-06-30T07:31:53.4485401Z [Incubating] Problems report is available at: file:///home/runner/work/mybatis-plus/mybatis-plus/build/reports/problems/problems-report.html
2026-06-30T07:31:53.5457104Z
2026-06-30T07:31:53.5472124Z
2026-06-30T07:31:53.5483196Z FAILURE: Build failed with an exception.
2026-06-30T07:31:53.5484014Z Deprecated Gradle features were used in this build, making it incompatible with Gradle 9.0.
2026-06-30T07:31:53.5496608Z
2026-06-30T07:31:53.5522300Z * What went wrong:
2026-06-30T07:31:53.5522532Z
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failure count only, no test named
- **Justification / Notes**: The section reports two failed tests but does not identify their names or methods.

---

## 17. `openremote__openremote__086149354006.txt`
- **Section Index**: 17
- **Fixture Filename**: `openremote__openremote__086149354006.txt`
- **Content Hash**: `0611218da9353e8a`
- **Repository**: `openremote/openremote`
- **Raw Evidence Excerpt**:
```text
2026-07-09T15:08:28.3050340Z   Test Create user requires realm administration rights PASSED
2026-07-09T15:08:28.4055031Z org.openremote.test.users.UserResourceTest > Reset secret requires realm administration rights took: 45ms
2026-07-09T15:08:28.4057240Z   Test Reset secret requires realm administration rights PASSED
2026-07-09T15:08:28.5046553Z org.openremote.test.users.UserResourceTest > Update user client roles requires realm administration rights took: 148ms
2026-07-09T15:08:28.5048719Z   Test Update user client roles requires realm administration rights PASSED
2026-07-09T15:08:28.6045672Z org.openremote.test.users.UserResourceTest > Update default client roles requires realm administration rights took: 80ms
2026-07-09T15:08:28.6050650Z   Test Update default client roles requires realm administration rights PASSED
2026-07-09T15:08:28.6060063Z org.openremote.test.users.UserResourceTest > Update client roles requires realm administration rights took: 66ms
2026-07-09T15:08:28.6062744Z   Test Update client roles requires realm administration rights PASSED
2026-07-09T15:08:34.6046639Z
2026-07-09T15:08:34.6055401Z
2026-07-09T15:08:34.6084184Z --------------------------------------------------------------------
2026-07-09T15:08:34.6085118Z 362 tests completed, 4 failed, 18 skipped
2026-07-09T15:08:34.6085861Z |  Results: FAILURE (362 tests, 340 passed, 4 failed, 18 skipped)  |
2026-07-09T15:08:34.6121457Z --------------------------------------------------------------------
2026-07-09T15:08:34.6676413Z
2026-07-09T15:08:34.6964853Z FAILURE: Executed 362 tests in 14m 35s (4 failed, 18 skipped)
2026-07-09T15:08:34.7233656Z
2026-07-09T15:08:39.4045746Z
2026-07-09T15:08:39.4064172Z > Task :test:test FAILED
2026-07-09T15:08:39.5073939Z
2026-07-09T15:08:39.5073972Z
2026-07-09T15:08:39.5097586Z [Incubating] Problems report is available at: file:///home/runner/work/openremote/openremote/build/reports/problems/problems-report.html
2026-07-09T15:08:39.5103468Z FAILURE: Build failed with an exception.
2026-07-09T15:08:39.5103856Z
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failure count only, no test named
- **Justification / Notes**: The section reports four failed tests but does not identify their names or methods.

---

## 18. `sirixdb__sirix__088196470656.txt`
- **Section Index**: 18
- **Fixture Filename**: `sirixdb__sirix__088196470656.txt`
- **Content Hash**: `d4932af43685ad17`
- **Repository**: `sirixdb/sirix`
- **Raw Evidence Excerpt**:
```text
2026-07-19T13:29:34.3854120Z
2026-07-19T13:29:34.3854700Z ProjectionIndexStressTest > tombstoneRebuildCyclesKeepServingExactly() FAILED
2026-07-19T13:29:34.3855420Z     org.opentest4j.AssertionFailedError at ProjectionIndexStressTest.java:523
2026-07-19T13:49:19.0284700Z
2026-07-19T13:49:19.0286530Z # [StorageProfile] dump called: enabled=false byKind.size=0
2026-07-19T13:49:19.1882680Z
2026-07-19T13:49:19.2081700Z > Task :sirix-query:test
2026-07-19T13:49:19.2195140Z
2026-07-19T13:49:19.2312080Z ===== FAILED TESTS (1) =====
2026-07-19T13:49:19.2415950Z FAILED-TEST: io.sirix.query.ProjectionIndexStressTest > tombstoneRebuildCyclesKeepServingExactly(): org.opentest4j.AssertionFailedError: cycle 0: a moved-out record must invalidate the projection ==> expected: <null> but was: <io.sirix.index.projection.ProjectionIndexRegistry$Handle@28068327>
2026-07-19T13:49:19.2564750Z ===== END FAILED TESTS =====
2026-07-19T13:49:19.3760500Z
2026-07-19T13:49:19.3762090Z 952 tests completed, 1 failed, 6 skipped
2026-07-19T13:49:19.9106490Z
2026-07-19T13:49:19.9208080Z > Task :sirix-query:test FAILED
2026-07-19T13:49:19.9308380Z > Task :sirix-kotlin-api:checkKotlinGradlePluginConfigurationErrors SKIPPED
2026-07-19T13:49:21.2462980Z > Task :sirix-kotlin-api:processResources NO-SOURCE
2026-07-19T13:49:21.3594770Z > Task :sirix-kotlin-api:generatePomFileForMavenPublication
2026-07-19T13:49:21.5266810Z > Task :sirix-kotlin-api:processTestResources
2026-07-19T13:49:21.5368880Z > Task :sirix-kotlin-cli:checkKotlinGradlePluginConfigurationErrors SKIPPED
2026-07-19T13:49:21.5470560Z > Task :sirix-kotlin-cli:processResources
2026-07-19T13:49:21.5571080Z > Task :sirix-kotlin-cli:generatePomFileForMavenPublication
2026-07-19T13:49:21.5572090Z > Task :sirix-kotlin-cli:processTestResources
2026-07-19T13:49:26.6800610Z
2026-07-19T13:49:26.6857980Z > Task :sirix-kotlin-api:compileKotlin
```
- **Expected Class**: io.sirix.query.ProjectionIndexStressTest
- **Expected Identifier Count**: 1
- **Expected Identifiers**: io.sirix.query.ProjectionIndexStressTest#tombstoneRebuildCyclesKeepServingExactly
- **Justification / Notes**: Explicit Java failure line and FAILED-TEST line identify the class and method.

---

## 19. `diffplug__spotless__080436519238.txt`
- **Section Index**: 19
- **Fixture Filename**: `diffplug__spotless__080436519238.txt`
- **Content Hash**: `f763b558d8519e27`
- **Repository**: `diffplug/spotless`
- **Raw Evidence Excerpt**:
```text
2026-06-09T22:19:17.6172016Z   org.gradle.api.tasks.TaskExecutionException: Execution failed for task ':spotlessJavaApply'.
2026-06-09T22:19:17.6172822Z   	at org.gradle.api.internal.tasks.execution.ExecuteActionsTaskExecuter.lambda$executeIfValid$1(ExecuteActionsTaskExecuter.java:149)
2026-06-09T22:19:17.6173588Z   	at org.gradle.internal.Try$Failure.ifSuccessfulOrElse(Try.java:282)
2026-06-09T22:19:17.6174597Z   	at org.gradle.api.internal.tasks.execution.ExecuteActionsTaskExecuter.executeIfValid(ExecuteActionsTaskExecuter.java:147)
2026-06-09T22:19:17.6175954Z   	at org.gradle.api.internal.tasks.execution.ExecuteActionsTaskExecuter.execute(ExecuteActionsTaskExecuter.java:135)
2026-06-09T22:19:17.6176820Z   	at org.gradle.api.internal.tasks.execution.FinalizePropertiesTaskExecuter.execute(FinalizePropertiesTaskExecuter.java:46)
2026-06-09T22:19:17.6177816Z   	at org.gradle.api.internal.tasks.execution.ResolveTaskExecutionModeExecuter.execute(ResolveTaskExecutionModeExecuter.java:51)
2026-06-09T22:19:17.6178593Z   	at org.gradle.api.internal.tasks.execution.SkipTaskWithNoActionsExecuter.execute(SkipTaskWithNoActionsExecuter.java:57)
2026-06-09T22:19:17.6179442Z   	at org.gradle.api.internal.tasks.execution.SkipOnlyIfTaskExecuter.execute(SkipOnlyIfTaskExecuter.java:74)
2026-06-09T22:19:17.6180552Z   	at org.gradle.api.internal.tasks.execution.CatchExceptionTaskExecuter.execute(CatchExceptionTaskExecuter.java:36)
2026-06-09T22:19:17.6195435Z   	at org.gradle.api.internal.tasks.execution.EventFiringTaskExecuter$1.executeTask(EventFiringTaskExecuter.java:77)
2026-06-09T22:19:17.6195999Z
2026-06-09T22:19:17.6196125Z 285 tests completed, 3 failed, 3 skipped
2026-06-09T22:19:17.6196693Z   	at org.gradle.api.internal.tasks.execution.EventFiringTaskExecuter$1.call(EventFiringTaskExecuter.java:55)
2026-06-09T22:19:17.6197512Z   	at org.gradle.api.internal.tasks.execution.EventFiringTaskExecuter$1.call(EventFiringTaskExecuter.java:52)
2026-06-09T22:19:17.6198425Z   	at org.gradle.internal.operations.DefaultBuildOperationRunner$CallableBuildOperationWorker.execute(DefaultBuildOperationRunner.java:204)
2026-06-09T22:19:17.6199497Z   	at org.gradle.internal.operations.DefaultBuildOperationRunner$CallableBuildOperationWorker.execute(DefaultBuildOperationRunner.java:199)
2026-06-09T22:19:17.6200435Z   	at org.gradle.internal.operations.DefaultBuildOperationRunner$2.execute(DefaultBuildOperationRunner.java:66)
2026-06-09T22:19:17.6202968Z   	at org.gradle.internal.operations.DefaultBuildOperationRunner$2.execute(DefaultBuildOperationRunner.java:59)
2026-06-09T22:19:17.6204083Z   	at org.gradle.internal.operations.DefaultBuildOperationRunner.execute(DefaultBuildOperationRunner.java:157)
2026-06-09T22:19:17.6204927Z   	at org.gradle.internal.operations.DefaultBuildOperationRunner.execute(DefaultBuildOperationRunner.java:59)
2026-06-09T22:19:17.6205759Z   	at org.gradle.internal.operations.DefaultBuildOperationRunner.call(DefaultBuildOperationRunner.java:53)
2026-06-09T22:19:17.6206590Z   	at org.gradle.internal.operations.DefaultBuildOperationExecutor.call(DefaultBuildOperationExecutor.java:73)
2026-06-09T22:19:17.6207431Z   	at org.gradle.api.internal.tasks.execution.EventFiringTaskExecuter.execute(EventFiringTaskExecuter.java:52)
2026-06-09T22:19:17.6208214Z   	at org.gradle.execution.plan.LocalTaskNodeExecutor.execute(LocalTaskNodeExecutor.java:42)
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - build error, no test named
- **Justification / Notes**: The raw lines show a Gradle spotlessJavaApply task failure and no named failed test.

---

## 20. `grobidOrg__grobid__082786414435.txt`
- **Section Index**: 20
- **Fixture Filename**: `grobidOrg__grobid__082786414435.txt`
- **Content Hash**: `ed8a3d8ff9379ed8`
- **Repository**: `grobidOrg/grobid`
- **Raw Evidence Excerpt**:
```text
2026-06-22T18:20:26.9304991Z   Test testPostProcessLabeledAbstract_shouldTransformTableLabelInParagraphLabel() PASSED
2026-06-22T18:20:26.9305912Z   Test testPostProcessFulltextFixInvalidTableOrFigure_noChangeNeeded_shouldReturnSameTableOrFigureSequence() PASSED
2026-06-22T18:20:26.9306965Z   Test testPostProcessFulltextFixInvalidTableOrFigure_MultipleChangeNeeded_shouldCorrectTheTableOrFigureSequence() PASSED
2026-06-22T18:20:26.9312081Z Starting process 'Gradle Test Executor 92'. Working directory: /home/runner/work/grobid/grobid/grobid-core Command: /opt/hostedtoolcache/Java_Temurin-Hotspot_jdk/21.0.11-10.0.LTS/arm64/bin/java -Djava.library.path=/usr/java/packages/lib:/usr/lib64:/lib64:/lib:/usr/lib:/home/runner/work/grobid/grobid/grobid-home/lib/lin-64/jep:/home/runner/work/grobid/grobid/grobid-home/lib/lin-64 -Dorg.gradle.internal.worker.tmpdir=/home/runner/work/grobid/grobid/grobid-core/build/tmp/test/work --add-opens java.base/java.util.stream=ALL-UNNAMED --add-opens java.base/java.io=ALL-UNNAMED --add-opens java.xml/jdk.xml.internal=ALL-UNNAMED -javaagent:/home/runner/.gradle/caches/modules-2/files-2.1/org.mockito/mockito-core/5.20.0/a32f446f38acf636363c5693db6498047731b9e0/mockito-core-5.20.0.jar -javaagent:/home/runner/work/grobid/grobid/grobid-core/build/tmp/.cache/expanded/zip_9892ccb804f78c0637616b68610d363f/jacocoagent.jar=destfile=build/jacoco/test.exec,append=true,inclnolocationclasses=false,dumponexit=true,output=file,jmx=false @/home/runner/.gradle/.tmp/gradle-worker-classpath739356851533028460txt -Xmx1024m -Dfile.encoding=UTF-8 -Duser.country -Duser.language=en -Duser.variant -ea worker.org.gradle.process.internal.worker.GradleWorkerMain 'Gradle Test Executor 92'
2026-06-22T18:20:26.9316650Z Successfully started process 'Gradle Test Executor 92'
2026-06-22T18:20:27.4257143Z
2026-06-22T18:20:27.4288613Z Gradle Test Executor 92 started executing tests.
2026-06-22T18:20:28.1257778Z Gradle Test Executor 92 finished executing tests.
2026-06-22T18:20:28.3287891Z
2026-06-22T18:20:28.3287910Z
2026-06-22T18:20:28.3288532Z > Task :grobid-core:test FAILED
2026-06-22T18:20:28.3288884Z
2026-06-22T18:20:28.3293316Z 565 tests completed, 3 failed, 43 skipped
2026-06-22T18:20:28.3293741Z SentenceUtilitiesKTest > testToSkipTokenNoHypen_shouldReturnTrue STANDARD_OUT
2026-06-22T18:20:28.3294348Z
2026-06-22T18:20:28.3294738Z FAILURE: Build failed with an exception.
2026-06-22T18:20:28.3295038Z
2026-06-22T18:20:28.3295236Z * What went wrong:
2026-06-22T18:20:28.3295572Z Execution failed for task ':grobid-core:test'.
2026-06-22T18:20:28.3296293Z > There were failing tests. See the report at: file:///home/runner/work/grobid/grobid/grobid-core/build/reports/tests/test/index.html
2026-06-22T18:20:28.3296864Z
2026-06-22T18:20:28.3297051Z * Try:
2026-06-22T18:20:28.3297417Z > Run with --scan to generate a Build Scan (Powered by Develocity).
2026-06-22T18:20:28.3298110Z
2026-06-22T18:20:28.3298289Z * Exception is:
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failed count but no failed test named
- **Justification / Notes**: A test name appears in STANDARD_OUT, but it is not identified as failed; the section only reports three failed tests.

---

## 21. `Stirling-Tools__Stirling-PDF__092039331010.txt`
- **Section Index**: 21
- **Fixture Filename**: `Stirling-Tools__Stirling-PDF__092039331010.txt`
- **Content Hash**: `e52a595a5742b8ad`
- **Repository**: `Stirling-Tools/Stirling-PDF`
- **Raw Evidence Excerpt**:
```text
2026-08-04T15:19:48.3700984Z [backend:build] Note: Recompile with -Xlint:deprecation for details.
2026-08-04T15:19:48.3731208Z [backend:build] Note: /home/runner/work/Stirling-PDF/Stirling-PDF/app/proprietary/src/main/java/stirling/software/proprietary/policy/s3/EmbeddedS3CredentialMigration.java uses unchecked or unsafe operations.
2026-08-04T15:19:48.3801092Z [backend:build] Note: Recompile with -Xlint:unchecked for details.
2026-08-04T15:19:48.4531631Z [backend:build]
2026-08-04T15:19:48.4581746Z [backend:build] > Task :stirling-pdf:resolveMainClassName
2026-08-04T15:19:51.7478052Z [backend:build] OpenJDK 64-Bit Server VM warning: Sharing is only supported for boot loader classes because bootstrap classpath has been appended
2026-08-04T15:19:55.6531818Z [backend:build] > Task :proprietary:classes
2026-08-04T15:19:55.6581598Z [backend:build] > Task :compileJava NO-SOURCE
2026-08-04T15:19:55.6651568Z [backend:build] > Task :classes UP-TO-DATE
2026-08-04T15:19:55.6680956Z [backend:build] > Task :resolveMainClassName
2026-08-04T15:19:55.6740688Z [backend:build] > Task :jar SKIPPED
2026-08-04T15:19:55.6786106Z [backend:build] > Task :compileTestJava NO-SOURCE
2026-08-04T15:19:55.6812418Z [backend:build] > Task :testClasses UP-TO-DATE
2026-08-04T15:19:55.9561464Z [backend:build] > Task :proprietary:jar
2026-08-04T15:19:55.9611190Z [backend:build] > Task :bootJar SKIPPED
2026-08-04T15:19:55.9641108Z [backend:build] > Task :assemble UP-TO-DATE
2026-08-04T15:19:56.0551399Z [backend:build] > Task :test NO-SOURCE
2026-08-04T15:19:56.0597409Z [backend:build] > Task :check
2026-08-04T15:19:56.0651114Z [backend:build] > Task :proprietary:resolveMainClassName
2026-08-04T15:19:56.1483409Z [backend:build] > Task :proprietary:bootJar SKIPPED
2026-08-04T15:19:56.1522890Z [backend:build] > Task :proprietary:assemble
2026-08-04T15:20:03.9552795Z [backend:build] > Task :stirling-pdf:bootJar
2026-08-04T15:20:03.9600537Z [backend:build] > Task :stirling-pdf:assemble
2026-08-04T15:20:04.0518607Z [backend:build]
2026-08-04T15:20:04.0570836Z [backend:build] > Task :build
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no tests ran
- **Justification / Notes**: The raw lines show compileTestJava/test NO-SOURCE and do not identify a test.

---

## 22. `apple__servicetalk__094207332011.txt`
- **Section Index**: 22
- **Fixture Filename**: `apple__servicetalk__094207332011.txt`
- **Content Hash**: `cf8a027f28a2b925`
- **Repository**: `apple/servicetalk`
- **Raw Evidence Excerpt**:
```text
2026-08-12T17:49:36.9214012Z > Task :servicetalk-benchmarks:clean UP-TO-DATE
2026-08-12T17:49:36.9249377Z > Task :servicetalk-circuit-breaker-api:clean UP-TO-DATE
2026-08-12T17:49:36.9250442Z > Task :servicetalk-circuit-breaker-resilience4j:clean UP-TO-DATE
2026-08-12T17:49:36.9251340Z > Task :clean UP-TO-DATE
2026-08-12T17:49:36.9252043Z > Task :servicetalk-client-api-internal:clean UP-TO-DATE
2026-08-12T17:49:36.9252916Z > Task :servicetalk-buffer-netty:clean UP-TO-DATE
2026-08-12T17:49:36.9254043Z > Task :servicetalk-capacity-limiter-api:clean UP-TO-DATE
2026-08-12T17:49:36.9254952Z > Task :servicetalk-concurrent-api-internal:clean UP-TO-DATE
2026-08-12T17:49:36.9256261Z > Task :servicetalk-client-api:clean UP-TO-DATE
2026-08-12T17:49:36.9257075Z > Task :servicetalk-concurrent-api:clean UP-TO-DATE
2026-08-12T17:49:36.9257944Z > Task :servicetalk-concurrent-jdkflow:clean UP-TO-DATE
2026-08-12T17:49:36.9258800Z > Task :servicetalk-concurrent-internal:clean UP-TO-DATE
2026-08-12T17:49:36.9259673Z > Task :servicetalk-concurrent-test-internal:clean UP-TO-DATE
2026-08-12T17:49:36.9260589Z > Task :servicetalk-concurrent-api-test:clean UP-TO-DATE
2026-08-12T17:49:36.9261435Z > Task :servicetalk-context-api:clean UP-TO-DATE
2026-08-12T17:49:36.9262274Z > Task :servicetalk-data-jackson:clean UP-TO-DATE
2026-08-12T17:49:36.9263135Z > Task :servicetalk-data-jackson-jersey:clean UP-TO-DATE
2026-08-12T17:49:36.9267362Z > Task :servicetalk-concurrent:clean UP-TO-DATE
2026-08-12T17:49:36.9279802Z > Task :servicetalk-data-jackson-jersey3-jakarta9:clean UP-TO-DATE
2026-08-12T17:49:36.9294018Z > Task :servicetalk-data-jackson3:clean UP-TO-DATE
2026-08-12T17:49:36.9295018Z > Task :servicetalk-data-jackson3-jersey4-jakarta11:clean UP-TO-DATE
2026-08-12T17:49:36.9296035Z > Task :servicetalk-data-protobuf:clean UP-TO-DATE
2026-08-12T17:49:36.9296904Z > Task :servicetalk-data-protobuf-jersey:clean UP-TO-DATE
2026-08-12T17:49:36.9298220Z > Task :servicetalk-data-protobuf-jersey3-jakarta9:clean UP-TO-DATE
2026-08-12T17:49:36.9299340Z > Task :servicetalk-data-protobuf-jersey4-jakarta11:clean UP-TO-DATE
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no tests identified
- **Justification / Notes**: The raw lines contain clean/build tasks only and no test name.

---

## 23. `webauthn4j__webauthn4j__085896676258.txt`
- **Section Index**: 23
- **Fixture Filename**: `webauthn4j__webauthn4j__085896676258.txt`
- **Content Hash**: `f97b490898943314`
- **Repository**: `webauthn4j/webauthn4j`
- **Raw Evidence Excerpt**:
```text
2026-07-08T14:36:04.6469476Z > Task :maven-central-publish-plugin:processResources
2026-07-08T14:36:11.2474578Z > Task :maven-central-publish-plugin:compileKotlin
2026-07-08T14:36:11.2483033Z > Task :maven-central-publish-plugin:compileJava NO-SOURCE
2026-07-08T14:36:11.2484115Z > Task :maven-central-publish-plugin:classes
2026-07-08T14:36:11.2484883Z > Task :maven-central-publish-plugin:jar
2026-07-08T14:36:42.8474922Z > Task :compileJava NO-SOURCE
2026-07-08T14:36:42.8509222Z > Task :processResources NO-SOURCE
2026-07-08T14:36:42.8551861Z > Task :classes UP-TO-DATE
2026-07-08T14:36:42.8552544Z > Task :jar
2026-07-08T14:36:42.8582895Z > Task :assemble
2026-07-08T14:36:42.8611774Z > Task :compileTestJava NO-SOURCE
2026-07-08T14:36:42.8641798Z > Task :processTestResources NO-SOURCE
2026-07-08T14:36:42.8642517Z > Task :testClasses UP-TO-DATE
2026-07-08T14:36:42.8682904Z > Task :test NO-SOURCE
2026-07-08T14:36:42.8701896Z > Task :check UP-TO-DATE
2026-07-08T14:36:42.8728396Z > Task :build
2026-07-08T14:36:42.8783886Z > Task :integration-tests:compileJava NO-SOURCE
2026-07-08T14:36:42.8784707Z > Task :integration-tests:processResources NO-SOURCE
2026-07-08T14:36:42.8785385Z > Task :integration-tests:classes UP-TO-DATE
2026-07-08T14:36:42.8785991Z > Task :integration-tests:jar
2026-07-08T14:36:42.8786542Z > Task :integration-tests:javadoc NO-SOURCE
2026-07-08T14:36:42.8787143Z > Task :integration-tests:javadocJar
2026-07-08T14:36:42.8787706Z > Task :integration-tests:sourcesJar
2026-07-08T14:36:42.8788238Z > Task :integration-tests:assemble
2026-07-08T14:36:42.8788826Z > Task :integration-tests:compileTestJava NO-SOURCE
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no tests ran
- **Justification / Notes**: The raw lines show compileTestJava/test NO-SOURCE and do not identify a test.

---

## 24. `apple__servicetalk__093415674647.txt`
- **Section Index**: 24
- **Fixture Filename**: `apple__servicetalk__093415674647.txt`
- **Content Hash**: `5845470fade3b424`
- **Repository**: `apple/servicetalk`
- **Raw Evidence Excerpt**:
```text
2026-08-10T09:46:56.4166053Z > Task :servicetalk-annotations:clean UP-TO-DATE
2026-08-10T09:46:56.4175970Z > Task :servicetalk-buffer-api:clean UP-TO-DATE
2026-08-10T09:46:56.4198345Z > Task :servicetalk-buffer-netty:clean UP-TO-DATE
2026-08-10T09:46:56.4201510Z > Task :servicetalk-capacity-limiter-api:clean UP-TO-DATE
2026-08-10T09:46:56.4247910Z > Task :servicetalk-circuit-breaker-resilience4j:clean UP-TO-DATE
2026-08-10T09:46:56.4249157Z > Task :servicetalk-circuit-breaker-api:clean UP-TO-DATE
2026-08-10T09:46:56.4263243Z > Task :servicetalk-benchmarks:clean UP-TO-DATE
2026-08-10T09:46:56.4282984Z > Task :servicetalk-client-api-internal:clean UP-TO-DATE
2026-08-10T09:46:56.4306010Z > Task :servicetalk-client-api:clean UP-TO-DATE
2026-08-10T09:46:56.4310173Z > Task :servicetalk-concurrent-api:clean UP-TO-DATE
2026-08-10T09:46:56.4336301Z > Task :servicetalk-concurrent-api-internal:clean UP-TO-DATE
2026-08-10T09:46:56.4338274Z > Task :servicetalk-concurrent:clean UP-TO-DATE
2026-08-10T09:46:56.4339355Z > Task :servicetalk-concurrent-api-test:clean UP-TO-DATE
2026-08-10T09:46:56.4367255Z > Task :servicetalk-concurrent-jdkflow:clean UP-TO-DATE
2026-08-10T09:46:56.4368392Z > Task :servicetalk-concurrent-reactivestreams:clean UP-TO-DATE
2026-08-10T09:46:56.4369760Z > Task :servicetalk-concurrent-internal:clean UP-TO-DATE
2026-08-10T09:46:56.4370711Z > Task :servicetalk-context-api:clean UP-TO-DATE
2026-08-10T09:46:56.4371587Z > Task :servicetalk-data-jackson:clean UP-TO-DATE
2026-08-10T09:46:56.4372618Z > Task :servicetalk-data-jackson-jersey3-jakarta10:clean UP-TO-DATE
2026-08-10T09:46:56.4374217Z > Task :servicetalk-concurrent-test-internal:clean UP-TO-DATE
2026-08-10T09:46:56.4375491Z > Task :servicetalk-data-jackson-jersey:clean UP-TO-DATE
2026-08-10T09:46:56.4376781Z > Task :servicetalk-data-jackson3-jersey4-jakarta11:clean UP-TO-DATE
2026-08-10T09:46:56.4377752Z > Task :servicetalk-data-protobuf:clean UP-TO-DATE
2026-08-10T09:46:56.4378720Z > Task :servicetalk-data-jackson-jersey3-jakarta9:clean UP-TO-DATE
2026-08-10T09:46:56.4379685Z > Task :servicetalk-data-jackson3:clean UP-TO-DATE
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no tests identified
- **Justification / Notes**: The raw lines contain clean/build tasks only and no test name.

---

## 25. `webauthn4j__webauthn4j__084798963375.txt`
- **Section Index**: 25
- **Fixture Filename**: `webauthn4j__webauthn4j__084798963375.txt`
- **Content Hash**: `b0c3b21b6751bbb7`
- **Repository**: `webauthn4j/webauthn4j`
- **Raw Evidence Excerpt**:
```text
2026-07-02T14:34:36.4695269Z > Task :maven-central-publish-plugin:processResources
2026-07-02T14:34:43.5684339Z > Task :maven-central-publish-plugin:compileKotlin
2026-07-02T14:34:43.6692872Z > Task :maven-central-publish-plugin:compileJava NO-SOURCE
2026-07-02T14:34:43.6714546Z > Task :maven-central-publish-plugin:classes
2026-07-02T14:34:43.6732302Z > Task :maven-central-publish-plugin:jar
2026-07-02T14:35:19.1693071Z > Task :compileJava NO-SOURCE
2026-07-02T14:35:19.1693904Z > Task :processResources NO-SOURCE
2026-07-02T14:35:19.1694638Z > Task :classes UP-TO-DATE
2026-07-02T14:35:19.1695280Z > Task :jar
2026-07-02T14:35:19.1695774Z > Task :assemble
2026-07-02T14:35:19.1696332Z > Task :compileTestJava NO-SOURCE
2026-07-02T14:35:19.1697002Z > Task :processTestResources NO-SOURCE
2026-07-02T14:35:19.1697691Z > Task :testClasses UP-TO-DATE
2026-07-02T14:35:19.1698287Z > Task :test NO-SOURCE
2026-07-02T14:35:19.1698891Z > Task :check UP-TO-DATE
2026-07-02T14:35:19.1699447Z > Task :build
2026-07-02T14:35:19.1700837Z > Task :integration-tests:compileJava NO-SOURCE
2026-07-02T14:35:19.1701848Z > Task :integration-tests:processResources NO-SOURCE
2026-07-02T14:35:19.1702595Z > Task :integration-tests:classes UP-TO-DATE
2026-07-02T14:35:19.2693728Z > Task :integration-tests:jar
2026-07-02T14:35:19.2694811Z > Task :integration-tests:javadoc NO-SOURCE
2026-07-02T14:35:19.2695564Z > Task :integration-tests:javadocJar
2026-07-02T14:35:19.2696229Z > Task :integration-tests:sourcesJar
2026-07-02T14:35:19.2696883Z > Task :integration-tests:assemble
2026-07-02T14:35:19.2697598Z > Task :integration-tests:compileTestJava NO-SOURCE
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no tests ran
- **Justification / Notes**: The raw lines show compileTestJava/test NO-SOURCE and do not identify a test.

---

## 26. `unicode-org__cldr__077741081038.txt`
- **Section Index**: 26
- **Fixture Filename**: `unicode-org__cldr__077741081038.txt`
- **Content Hash**: `9eb129f05fb52129`
- **Repository**: `unicode-org/cldr`
- **Raw Evidence Excerpt**:
```text
2026-05-25T16:37:16.6457703Z 	at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
2026-05-25T16:37:16.6458662Z 	at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
2026-05-25T16:37:16.6459608Z 	at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
2026-05-25T16:37:16.6460173Z
2026-05-25T16:37:16.6460445Z [INFO] Running org.unicode.cldr.json.LdmlConvertRulesTest
2026-05-25T16:37:16.6461465Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.004 s -- in org.unicode.cldr.json.LdmlConvertRulesTest
2026-05-25T16:37:25.1269431Z [INFO]
2026-05-25T16:37:25.1269888Z [INFO] Results:
2026-05-25T16:37:25.1270229Z [INFO]
2026-05-25T16:37:25.1270599Z [ERROR] Failures:
2026-05-25T16:37:25.1271218Z [ERROR]   TestShim.TestAll:41  had errors ==> expected: <0> but was: <681>
2026-05-25T16:37:25.1271736Z [INFO]
2026-05-25T16:37:25.1271984Z [ERROR] Tests run: 657, Failures: 1, Errors: 0, Skipped: 23
2026-05-25T16:37:25.1272857Z [INFO]
2026-05-25T16:37:25.1306907Z [INFO] ------------------------------------------------------------------------
2026-05-25T16:37:25.1307648Z [INFO] Reactor Summary for CLDR All Tools 49.0-SNAPSHOT:
2026-05-25T16:37:25.1308153Z [INFO]
2026-05-25T16:37:25.1310842Z [INFO] CLDR All Tools ..................................... SUCCESS [  0.001 s]
2026-05-25T16:37:25.1311840Z [INFO] CLDR Code .......................................... FAILURE [21:15 min]
2026-05-25T16:37:25.1312899Z [INFO] CLDR RDF Tools ..................................... SKIPPED
2026-05-25T16:37:25.1313585Z [INFO] CLDR Survey Tool ................................... SKIPPED
2026-05-25T16:37:25.1314269Z [INFO] CLDR Keyboard Charts ............................... SKIPPED
2026-05-25T16:37:25.1314948Z [INFO] ------------------------------------------------------------------------
2026-05-25T16:37:25.1315528Z [INFO] BUILD FAILURE
2026-05-25T16:37:25.1316011Z [INFO] ------------------------------------------------------------------------
```
- **Expected Class**: TestShim
- **Expected Identifier Count**: 1
- **Expected Identifiers**: TestShim#TestAll
- **Justification / Notes**: Explicit Maven failure line identifies TestShim.TestAll; no package for TestShim appears in the section.

---

## 27. `apache__zeppelin__093702538653.txt`
- **Section Index**: 27
- **Fixture Filename**: `apache__zeppelin__093702538653.txt`
- **Content Hash**: `f5f3a098754451c7`
- **Repository**: `apache/zeppelin`
- **Raw Evidence Excerpt**:
```text
2026-08-11T07:20:51.7839179Z 07:20:51,733  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: sh-shared_process is terminated
2026-08-11T07:20:51.8840221Z 07:20:51,794  INFO org.apache.zeppelin.interpreter.remote.ExecRemoteInterpreterProcess:136 - Remote exec process of interpreter group: spark-shared_process is terminated
2026-08-11T07:20:51.8841276Z 07:20:51,795  INFO org.apache.zeppelin.notebook.repo.NotebookRepoSync:424 - Closing all notebook storages
2026-08-11T07:20:51.8841752Z 07:20:51,795  INFO org.apache.zeppelin.server.ZeppelinServer:370 - Bye
2026-08-11T07:20:53.8157286Z 07:20:53,797  INFO org.apache.zeppelin.MiniZeppelinServer:305 - ZeppelinServerMock terminated.
2026-08-11T07:20:53.8220421Z [WARNING] Tests run: 21, Failures: 0, Errors: 0, Skipped: 3, Time elapsed: 263.2 s -- in org.apache.zeppelin.integration.ParagraphActionsIT
2026-08-11T07:20:54.1632181Z [INFO]
2026-08-11T07:20:54.1632406Z [INFO] Results:
2026-08-11T07:20:54.1632635Z [INFO]
2026-08-11T07:20:54.1635008Z [ERROR] Errors:
2026-08-11T07:20:54.1635927Z [ERROR]   AuthenticationIT.testAnyOfRolesUser:146  Expected ngToast not found
2026-08-11T07:20:54.1638893Z [INFO]
2026-08-11T07:20:54.1639465Z [ERROR] Tests run: 39, Failures: 0, Errors: 1, Skipped: 8
2026-08-11T07:20:54.1639804Z [INFO]
2026-08-11T07:20:54.1699617Z [INFO]
2026-08-11T07:20:54.1700039Z [INFO] --- failsafe:3.3.0:verify (default) @ zeppelin-integration ---
2026-08-11T07:20:54.2180456Z [INFO] ------------------------------------------------------------------------
2026-08-11T07:20:54.2181234Z [INFO] BUILD FAILURE
2026-08-11T07:20:54.2181946Z [INFO] ------------------------------------------------------------------------
2026-08-11T07:20:54.2182440Z [INFO] Total time:  10:33 min
2026-08-11T07:20:54.2182815Z [INFO] Finished at: 2026-08-11T07:20:54Z
2026-08-11T07:20:54.2183407Z [INFO] ------------------------------------------------------------------------
2026-08-11T07:20:54.2184170Z [WARNING] The requested profile "spark-3.5" could not be activated because it does not exist.
2026-08-11T07:20:54.2185023Z [WARNING] The requested profile "web-dist" could not be activated because it does not exist.
2026-08-11T07:20:54.2209384Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-failsafe-plugin:3.3.0:verify (default) on project zeppelin-integration:
```
- **Expected Class**: AuthenticationIT
- **Expected Identifier Count**: 1
- **Expected Identifiers**: AuthenticationIT#testAnyOfRolesUser
- **Justification / Notes**: Explicit Maven error line names the test; no package for AuthenticationIT appears in the section.

---

## 28. `unicode-org__cldr__088667882207.txt`
- **Section Index**: 28
- **Fixture Filename**: `unicode-org__cldr__088667882207.txt`
- **Content Hash**: `5ee4c5dac98ddd68`
- **Repository**: `unicode-org/cldr`
- **Raw Evidence Excerpt**:
```text
2026-07-21T15:10:39.4710019Z 	at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.invoke(JUnitPlatformProvider.java:122)
2026-07-21T15:10:39.4711484Z 	at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
2026-07-21T15:10:39.4712679Z 	at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
2026-07-21T15:10:39.4713734Z 	at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
2026-07-21T15:10:39.4714727Z 	at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
2026-07-21T15:10:39.4715324Z
2026-07-21T15:10:39.7331617Z [INFO]
2026-07-21T15:10:39.7332064Z [INFO] Results:
2026-07-21T15:10:39.7332443Z [INFO]
2026-07-21T15:10:39.7332785Z [ERROR] Failures:
2026-07-21T15:10:39.7333429Z [ERROR]   TestShim.TestAll:41  had errors ==> expected: <0> but was: <1654>
2026-07-21T15:10:39.7334177Z [INFO]
2026-07-21T15:10:39.7334657Z [ERROR] Tests run: 670, Failures: 1, Errors: 0, Skipped: 23
2026-07-21T15:10:39.7335252Z [INFO]
2026-07-21T15:10:39.7357721Z [INFO] ------------------------------------------------------------------------
2026-07-21T15:10:39.7358640Z [INFO] Reactor Summary for CLDR All Tools 49.0-SNAPSHOT:
2026-07-21T15:10:39.7368850Z [INFO]
2026-07-21T15:10:39.7369973Z [INFO] CLDR All Tools ..................................... SUCCESS [  0.002 s]
2026-07-21T15:10:39.7371172Z [INFO] CLDR Code .......................................... FAILURE [22:48 min]
2026-07-21T15:10:39.7372233Z [INFO] CLDR RDF Tools ..................................... SKIPPED
2026-07-21T15:10:39.7373239Z [INFO] CLDR Survey Tool ................................... SKIPPED
2026-07-21T15:10:39.7416953Z [INFO] CLDR Keyboard Charts ............................... SKIPPED
2026-07-21T15:10:39.7418021Z [INFO] ------------------------------------------------------------------------
2026-07-21T15:10:39.7418924Z [INFO] BUILD FAILURE
2026-07-21T15:10:39.7420259Z [INFO] ------------------------------------------------------------------------
```
- **Expected Class**: TestShim
- **Expected Identifier Count**: 1
- **Expected Identifiers**: TestShim#TestAll
- **Justification / Notes**: Explicit Maven failure line identifies TestShim.TestAll; no package for TestShim appears in the section.

---

## 29. `apache__atlas__092533695478.txt`
- **Section Index**: 29
- **Fixture Filename**: `apache__atlas__092533695478.txt`
- **Content Hash**: `b9e8b32992648d8e`
- **Repository**: `apache/atlas`
- **Raw Evidence Excerpt**:
```text
2026-08-06T06:33:34.8760488Z Actual invocations have different arguments:
2026-08-06T06:33:34.8760790Z atlasAuditService.add(
2026-08-06T06:33:34.8761010Z     AUTO_PURGE,
2026-08-06T06:33:34.8761217Z     "[11111111-1111-1111-1111-111111111111]",
2026-08-06T06:33:34.8762549Z     "{"requestedCount":1,"purgedCount":0,"purgedDependenciesCount":0,"failedCount":0,"failedDependenciesCount":0,"skippedCount":0,"validGuidCount":1,"executionFailed":true,"expandedEntityCount":0,"skippedRequestedCount":0,"skippedDependenciesCount":0,"unprocessedCount":0,"batchCount":0,"runId":"479aa91c-b5f4-4cfd-9826-d3edbca73a52"}",
2026-08-06T06:33:34.8763874Z     0L,
2026-08-06T06:33:34.8764086Z     "479aa91c-b5f4-4cfd-9826-d3edbca73a52",
2026-08-06T06:33:34.8764359Z     SUMMARY
2026-08-06T06:33:34.8764527Z );
2026-08-06T06:33:34.8764919Z -> at org.apache.atlas.services.PurgeAuditWriter.writeSummary(PurgeAuditWriter.java:115)
2026-08-06T06:33:34.8765327Z
2026-08-06T06:33:34.8765401Z [INFO]
2026-08-06T06:33:34.8765670Z [ERROR] Tests run: 2500, Failures: 2, Errors: 0, Skipped: 16
2026-08-06T06:33:34.8765979Z [INFO]
2026-08-06T06:33:34.9125232Z [INFO] ------------------------------------------------------------------------
2026-08-06T06:33:34.9126506Z [INFO] Reactor Summary for apache-atlas 3.0.0-SNAPSHOT:
2026-08-06T06:33:34.9127250Z [INFO]
2026-08-06T06:33:34.9128016Z [INFO] Apache Atlas Server Build Tools .................... SUCCESS [  0.713 s]
2026-08-06T06:33:34.9148357Z [INFO] apache-atlas ....................................... SUCCESS [  2.785 s]
2026-08-06T06:33:34.9149281Z [INFO] Apache Atlas Integration ........................... SUCCESS [02:34 min]
2026-08-06T06:33:34.9150187Z [INFO] Apache Atlas Client ................................ SUCCESS [  0.320 s]
2026-08-06T06:33:34.9151487Z [INFO] atlas-client-common ................................ SUCCESS [  4.948 s]
2026-08-06T06:33:34.9152361Z [INFO] atlas-client-v2 .................................... SUCCESS [  9.398 s]
2026-08-06T06:33:34.9153207Z [INFO] Apache Atlas Common ................................ SUCCESS [ 16.190 s]
2026-08-06T06:33:34.9154068Z [INFO] atlas-client-v1 .................................... SUCCESS [ 14.339 s]
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failure count and stack frame only
- **Justification / Notes**: The raw lines show two failures and a stack frame, but no test class or method for a failed test.

---

## 30. `apache__flink__080018153058.txt`
- **Section Index**: 30
- **Fixture Filename**: `apache__flink__080018153058.txt`
- **Content Hash**: `621a2725b34505f6`
- **Repository**: `apache/flink`
- **Raw Evidence Excerpt**:
```text
2026-06-08T03:38:19.9955928Z Jun 08 03:38:19 03:38:19.989 [INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.024 s -- in org.apache.flink.streaming.util.LatencyStatsTest
2026-06-08T03:38:20.3928443Z Jun 08 03:38:20 03:38:20.390 [INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.643 s -- in org.apache.flink.streaming.util.AbstractStreamOperatorTestHarnessTest
2026-06-08T03:38:20.5429764Z Jun 08 03:38:20 03:38:20.541 [INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 6.858 s -- in org.apache.flink.streaming.runtime.io.benchmark.StreamNetworkBroadcastThroughputBenchmarkTest
2026-06-08T03:39:44.8164522Z Jun 08 03:39:44 03:39:44.814 [INFO] Tests run: 100000, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 320.5 s -- in org.apache.flink.runtime.scheduler.adaptive.ForwardEdgesAdapterTest
2026-06-08T03:39:45.2596666Z Jun 08 03:39:45 03:39:45.258 [INFO]
2026-06-08T03:39:45.2597418Z Jun 08 03:39:45 03:39:45.258 [INFO] Results:
2026-06-08T03:39:45.2597954Z Jun 08 03:39:45 03:39:45.258 [INFO]
2026-06-08T03:39:45.2598492Z Jun 08 03:39:45 03:39:45.258 [ERROR] Failures:
2026-06-08T03:39:45.2604756Z Jun 08 03:39:45 03:39:45.259 [ERROR]   AbstractAsyncRunnableStreamOperatorTest.testCheckpointDrain:254
2026-06-08T03:39:45.2605637Z Jun 08 03:39:45 expected: 1
2026-06-08T03:39:45.2606108Z Jun 08 03:39:45  but was: 0
2026-06-08T03:39:45.2606554Z Jun 08 03:39:45 03:39:45.259 [INFO]
2026-06-08T03:39:45.2607219Z Jun 08 03:39:45 03:39:45.259 [ERROR] Tests run: 109933, Failures: 1, Errors: 0, Skipped: 356
2026-06-08T03:39:45.2607877Z Jun 08 03:39:45 03:39:45.259 [INFO]
2026-06-08T03:39:45.2615312Z Jun 08 03:39:45 03:39:45.261 [INFO] ------------------------------------------------------------------------
2026-06-08T03:39:45.2619162Z Jun 08 03:39:45 03:39:45.261 [INFO] Reactor Summary for Flink : Annotations 2.3-SNAPSHOT:
2026-06-08T03:39:45.2619803Z Jun 08 03:39:45 03:39:45.261 [INFO]
2026-06-08T03:39:45.2643658Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : Annotations ................................ SUCCESS [  1.617 s]
2026-06-08T03:39:45.2646518Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : Metrics : .................................. SUCCESS [  0.106 s]
2026-06-08T03:39:45.2647650Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : Metrics : Core ............................. SUCCESS [  2.816 s]
2026-06-08T03:39:45.2649073Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : Core ....................................... SUCCESS [ 59.233 s]
2026-06-08T03:39:45.2650285Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : RPC : ...................................... SUCCESS [  0.076 s]
2026-06-08T03:39:45.2651287Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : RPC : Core ................................. SUCCESS [  2.309 s]
2026-06-08T03:39:45.2652279Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : RPC : Akka ................................. SUCCESS [ 24.052 s]
2026-06-08T03:39:45.2653268Z Jun 08 03:39:45 03:39:45.261 [INFO] Flink : RPC : Akka-Loader .......................... SUCCESS [  3.589 s]
```
- **Expected Class**: AbstractAsyncRunnableStreamOperatorTest
- **Expected Identifier Count**: 1
- **Expected Identifiers**: AbstractAsyncRunnableStreamOperatorTest#testCheckpointDrain
- **Justification / Notes**: Explicit Maven failure line names the method and the earlier Flink package appears in the section's test class lines.

---

## 31. `apache__hugegraph__088106696924.txt`
- **Section Index**: 31
- **Fixture Filename**: `apache__hugegraph__088106696924.txt`
- **Content Hash**: `c314e9e68eb2bb01`
- **Repository**: `apache/hugegraph`
- **Raw Evidence Excerpt**:
```text
2026-07-18T18:01:12.2785223Z [ERROR] testQueryByNonEqLabelAndIndexedProperty(org.apache.hugegraph.core.VertexCoreTest)  Time elapsed: 0.577 s  <<< FAILURE!
2026-07-18T18:01:12.2787697Z java.lang.AssertionError: No exception was thrown(expected org.apache.hugegraph.exception.NoIndexException)
2026-07-18T18:01:12.2789571Z 	at org.apache.hugegraph.core.VertexCoreTest.testQueryByNonEqLabelAndIndexedProperty(VertexCoreTest.java:9100)
2026-07-18T18:01:12.2790990Z
2026-07-18T18:01:12.2819259Z 2026-07-18 18:01:12 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeGraph is shutting down
2026-07-18T18:01:12.3729457Z 2026-07-18 18:01:12 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeFactory shutdown
2026-07-18T18:01:12.7266573Z [INFO]
2026-07-18T18:01:12.7266942Z [INFO] Results:
2026-07-18T18:01:12.7267285Z [INFO]
2026-07-18T18:01:12.7267646Z [ERROR] Failures:
2026-07-18T18:01:12.7268946Z [ERROR]   VertexCoreTest.testQueryByNonEqLabelAndIndexedProperty:9100 No exception was thrown(expected org.apache.hugegraph.exception.NoIndexException)
2026-07-18T18:01:12.7270547Z [INFO]
2026-07-18T18:01:12.7271384Z [ERROR] Tests run: 798, Failures: 1, Errors: 0, Skipped: 41
2026-07-18T18:01:12.7271793Z [INFO]
2026-07-18T18:01:12.7282840Z [INFO] ------------------------------------------------------------------------
2026-07-18T18:01:12.7283597Z [INFO] Reactor Summary for hugegraph 1.7.0:
2026-07-18T18:01:12.7284063Z [INFO]
2026-07-18T18:01:12.7284605Z [INFO] hugegraph .......................................... SUCCESS [  1.314 s]
2026-07-18T18:01:12.7285724Z [INFO] hugegraph-commons .................................. SUCCESS [  1.005 s]
2026-07-18T18:01:12.7286948Z [INFO] hugegraph-common ................................... SUCCESS [  4.798 s]
2026-07-18T18:01:12.7287984Z [INFO] hugegraph-pd ....................................... SUCCESS [  0.338 s]
2026-07-18T18:01:12.7288787Z [INFO] hg-pd-grpc ......................................... SUCCESS [  8.286 s]
2026-07-18T18:01:12.7289557Z [INFO] hg-pd-common ....................................... SUCCESS [  0.171 s]
2026-07-18T18:01:12.7290632Z [INFO] hg-pd-client ....................................... SUCCESS [  1.563 s]
2026-07-18T18:01:12.7291269Z [INFO] hugegraph-struct ................................... SUCCESS [  2.116 s]
```
- **Expected Class**: org.apache.hugegraph.core.VertexCoreTest
- **Expected Identifier Count**: 1
- **Expected Identifiers**: org.apache.hugegraph.core.VertexCoreTest#testQueryByNonEqLabelAndIndexedProperty
- **Justification / Notes**: Explicit Java failure line and stack frame identify the fully qualified class and method.

---

## 32. `apache__zeppelin__087393956477.txt`
- **Section Index**: 32
- **Fixture Filename**: `apache__zeppelin__087393956477.txt`
- **Content Hash**: `2a6dfd08663fed81`
- **Repository**: `apache/zeppelin`
- **Raw Evidence Excerpt**:
```text
2026-07-15T15:41:06.1860843Z [INFO]
2026-07-15T15:41:06.1861072Z [ERROR] Errors:
2026-07-15T15:41:06.1869933Z [ERROR]   AuthenticationIT.testSimpleAuthentication:96->AbstractZeppelinIT.authenticationUser:56 » ElementClickIntercepted element click intercepted: Element <button class="btn nav-login-btn" data-toggle="modal" data-target="#loginModal" ng-click="navbar.showLoginWindow()">...</button> is not clickable at point (1869, 25). Other element would receive the click: <div id="loginModal" class="modal fade ng-scope in" role="dialog" tabindex="-1" style="display: block;">...</div>
2026-07-15T15:41:06.1871339Z   (Session info: chrome=150.0.7871.114)
2026-07-15T15:41:06.1871620Z Build info: version: '4.20.0', revision: '866c76ca80'
2026-07-15T15:41:06.1872031Z System info: os.name: 'Linux', os.arch: 'amd64', os.version: '6.17.0-1020-azure', java.version: '11.0.31'
2026-07-15T15:41:06.1894095Z Driver info: org.openqa.selenium.chrome.ChromeDriver
2026-07-15T15:41:06.1894875Z Command: [7a6813181ceb7c34a100135f999ba5ef, clickElement {id=f.03D0B01D45D88269CA059EEC64EE3B68.d.6A76AECE49963A20194E18A27035D05F.e.22}]
2026-07-15T15:41:06.1925776Z Capabilities {acceptInsecureCerts: false, browserName: chrome, browserVersion: 150.0.7871.114, chrome: {chromedriverVersion: 150.0.7871.115 (25f5b661e5b..., userDataDir: /tmp/org.chromium.Chromium....}, fedcm:accounts: true, goog:chromeOptions: {debuggerAddress: localhost:36629}, goog:processID: 3194, networkConnectionEnabled: false, pageLoadStrategy: normal, platformName: linux, proxy: Proxy(), se:cdp: ws://localhost:36629/devtoo..., se:cdpVersion: 150.0.7871.114, setWindowRect: true, strictFileInteractability: false, timeouts: {implicit: 0, pageLoad: 300000, script: 30000}, unhandledPromptBehavior: dismiss and notify, webauthn:extension:credBlob: true, webauthn:extension:largeBlob: true, webauthn:extension:minPinLength: true, webauthn:extension:prf: true, webauthn:virtualAuthenticators: true}
2026-07-15T15:41:06.1928114Z Element: [[ChromeDriver: chrome on linux (7a6813181ceb7c34a100135f999ba5ef)] -> xpath: //div[contains(@class, 'navbar-collapse')]//li//button[contains(.,'Login')]]
2026-07-15T15:41:06.1928648Z Session ID: 7a6813181ceb7c34a100135f999ba5ef
2026-07-15T15:41:06.1928890Z [INFO]
2026-07-15T15:41:06.1929107Z [ERROR] Tests run: 39, Failures: 0, Errors: 1, Skipped: 9
2026-07-15T15:41:06.1929476Z [INFO]
2026-07-15T15:41:06.1948350Z [INFO]
2026-07-15T15:41:06.1948810Z [INFO] --- failsafe:3.3.0:verify (default) @ zeppelin-integration ---
2026-07-15T15:41:06.2408853Z [INFO] ------------------------------------------------------------------------
2026-07-15T15:41:06.2409245Z [INFO] BUILD FAILURE
2026-07-15T15:41:06.2409565Z [INFO] ------------------------------------------------------------------------
2026-07-15T15:41:06.2409988Z [INFO] Total time:  09:46 min
2026-07-15T15:41:06.2411666Z [INFO] Finished at: 2026-07-15T15:41:06Z
2026-07-15T15:41:06.2412360Z [INFO] ------------------------------------------------------------------------
2026-07-15T15:41:06.2413077Z [WARNING] The requested profile "spark-3.5" could not be activated because it does not exist.
2026-07-15T15:41:06.2414009Z [WARNING] The requested profile "web-dist" could not be activated because it does not exist.
2026-07-15T15:41:06.2419112Z [ERROR] Failed to execute goal org.apache.maven.plugins:maven-failsafe-plugin:3.3.0:verify (default) on project zeppelin-integration:
```
- **Expected Class**: AuthenticationIT
- **Expected Identifier Count**: 1
- **Expected Identifiers**: AuthenticationIT#testSimpleAuthentication
- **Justification / Notes**: Explicit Maven error line names the test; no package for AuthenticationIT appears in the section.

---

## 33. `apache__hertzbeat__091878341153.txt`
- **Section Index**: 33
- **Fixture Filename**: `apache__hertzbeat__091878341153.txt`
- **Content Hash**: `ee37d3864a1bf8d7`
- **Repository**: `apache/hertzbeat`
- **Raw Evidence Excerpt**:
```text
2026-08-04T03:06:12.5482583Z [hertzbeat-observability-e2e] [INFO] [stdout]
2026-08-04T03:06:12.5484367Z [hertzbeat-observability-e2e] [INFO] [stdout] 2026-08-04 03:06:12 [docker-java-stream-1599143771] INFO  org.apache.hertzbeat.observability.ingestion.LogIngestionE2eTest - Vector: 2026-08-04T03:06:12.466139Z ERROR sink{component_kind="sink" component_id=emit_syslog component_type=opentelemetry}:request{request_id=49}: vector_common::internal_event::component_events_dropped: Events dropped intentional=false count=2 reason="Service call failed. No retries or retries exhausted."
2026-08-04T03:06:12.5486454Z [hertzbeat-observability-e2e] [INFO] [stdout]
2026-08-04T03:06:12.5487033Z [hertzbeat-observability-e2e] [ERROR] Surefire is going to kill self fork JVM. The exit has elapsed 30 seconds after System.exit(0).
2026-08-04T03:06:12.8897949Z [hertzbeat-observability-e2e] [INFO]
2026-08-04T03:06:12.8898679Z [hertzbeat-observability-e2e] [INFO] Results:
2026-08-04T03:06:12.8901688Z [hertzbeat-observability-e2e] [INFO]
2026-08-04T03:06:12.8902319Z [hertzbeat-observability-e2e] [ERROR] Errors:
2026-08-04T03:06:12.8904803Z [hertzbeat-observability-e2e] [ERROR]   LogRealTimeAlertE2eTest.testRealTimeLogAlertWithGroupAlert:145 » ConditionTimeout Assertion condition Should have generated high frequency warning group alert ==> expected: <false> but was: <true> within 2 minutes.
2026-08-04T03:06:12.8916295Z [hertzbeat-observability-e2e] [ERROR]   LogRealTimeAlertE2eTest.testRealTimeLogAlertWithIndividualAlert:118 » ConditionTimeout Assertion condition Should have generated at least one alert for error logs ==> expected: <false> but was: <true> within 2 minutes.
2026-08-04T03:06:12.8920925Z [hertzbeat-observability-e2e] [ERROR]   LogIngestionE2eTest.testLogIngestion:95 » ConditionTimeout Assertion condition null within 1 minutes.
2026-08-04T03:06:12.8922235Z [hertzbeat-observability-e2e] [INFO]
2026-08-04T03:06:12.8923226Z [hertzbeat-observability-e2e] [ERROR] Tests run: 7, Failures: 0, Errors: 3, Skipped: 0
2026-08-04T03:06:12.8924052Z [hertzbeat-observability-e2e] [INFO]
2026-08-04T03:06:12.9036117Z [INFO] ----------------------------------------------------------------------------------------------------------------
2026-08-04T03:06:12.9045211Z [INFO] Reactor Summary for hertzbeat 2.0-SNAPSHOT:
2026-08-04T03:06:12.9046770Z [INFO]
2026-08-04T03:06:12.9049448Z [INFO] hertzbeat .................................................................................. SUCCESS [ 10.013 s]
2026-08-04T03:06:12.9050797Z [INFO] hertzbeat-common-core ...................................................................... SUCCESS [ 32.460 s]
2026-08-04T03:06:12.9052210Z [INFO] hertzbeat-common-spring .................................................................... SUCCESS [ 25.849 s]
2026-08-04T03:06:12.9053536Z [INFO] hertzbeat-base ............................................................................. SUCCESS [  0.487 s]
2026-08-04T03:06:12.9054840Z [INFO] hertzbeat-plugin ........................................................................... SUCCESS [  2.180 s]
2026-08-04T03:06:12.9056196Z [INFO] hertzbeat-warehouse ........................................................................ SUCCESS [ 42.496 s]
2026-08-04T03:06:12.9057836Z [INFO] hertzbeat-alerter .......................................................................... SUCCESS [02:29 min]
2026-08-04T03:06:12.9059288Z [INFO] hertzbeat-remoting ......................................................................... SUCCESS [ 11.034 s]
```
- **Expected Class**: LogRealTimeAlertE2eTest
- **Expected Identifier Count**: 2
- **Expected Identifiers**: LogRealTimeAlertE2eTest#testRealTimeLogAlertWithGroupAlert; LogRealTimeAlertE2eTest#testRealTimeLogAlertWithIndividualAlert
- **Justification / Notes**: Two explicit Maven error lines identify two methods in the same test class.

---

## 34. `apache__hugegraph__085380370363.txt`
- **Section Index**: 34
- **Fixture Filename**: `apache__hugegraph__085380370363.txt`
- **Content Hash**: `eb2d705b5831fe51`
- **Repository**: `apache/hugegraph`
- **Raw Evidence Excerpt**:
```text
2026-07-06T13:33:11.4968400Z [ERROR] testDistributedDeleteKeepsTaskResultRecoverable(org.apache.hugegraph.task.TaskAndResultSchedulerTest)  Time elapsed: 0.506 s  <<< FAILURE!
2026-07-06T13:33:11.4975110Z java.lang.AssertionError: expected:<DELETING> but was:<SUCCESS>
2026-07-06T13:33:11.4980340Z 	at org.apache.hugegraph.task.TaskAndResultSchedulerTest.testDistributedDeleteKeepsTaskResultRecoverable(TaskAndResultSchedulerTest.java:122)
2026-07-06T13:33:11.4984100Z
2026-07-06T13:33:11.5126140Z 2026-07-06 13:33:11 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeGraph is shutting down
2026-07-06T13:33:11.7034350Z 2026-07-06 13:33:11 [hugegraph-shutdown] [INFO] o.a.h.HugeFactory - HugeFactory shutdown
2026-07-06T13:33:13.1945040Z [INFO]
2026-07-06T13:33:13.1946030Z [INFO] Results:
2026-07-06T13:33:13.1946890Z [INFO]
2026-07-06T13:33:13.1948070Z [ERROR] Failures:
2026-07-06T13:33:13.1952170Z [ERROR]   TaskAndResultSchedulerTest.testDistributedDeleteKeepsTaskResultRecoverable:122 expected:<DELETING> but was:<SUCCESS>
2026-07-06T13:33:13.1953400Z [INFO]
2026-07-06T13:33:13.1955370Z [ERROR] Tests run: 781, Failures: 1, Errors: 0, Skipped: 41
2026-07-06T13:33:13.1957040Z [INFO]
2026-07-06T13:33:13.2094930Z [INFO] ------------------------------------------------------------------------
2026-07-06T13:33:13.2095680Z [INFO] Reactor Summary for hugegraph 1.7.0:
2026-07-06T13:33:13.2096190Z [INFO]
2026-07-06T13:33:13.2117960Z [INFO] hugegraph .......................................... SUCCESS [  4.620 s]
2026-07-06T13:33:13.2119840Z [INFO] hugegraph-commons .................................. SUCCESS [  2.954 s]
2026-07-06T13:33:13.2121040Z [INFO] hugegraph-common ................................... SUCCESS [  9.296 s]
2026-07-06T13:33:13.2122320Z [INFO] hugegraph-pd ....................................... SUCCESS [  0.690 s]
2026-07-06T13:33:13.2124470Z [INFO] hg-pd-grpc ......................................... SUCCESS [ 24.923 s]
2026-07-06T13:33:13.2125750Z [INFO] hg-pd-common ....................................... SUCCESS [  1.069 s]
2026-07-06T13:33:13.2126980Z [INFO] hg-pd-client ....................................... SUCCESS [  9.653 s]
2026-07-06T13:33:13.2128370Z [INFO] hugegraph-struct ................................... SUCCESS [  7.068 s]
```
- **Expected Class**: org.apache.hugegraph.task.TaskAndResultSchedulerTest
- **Expected Identifier Count**: 1
- **Expected Identifiers**: org.apache.hugegraph.task.TaskAndResultSchedulerTest#testDistributedDeleteKeepsTaskResultRecoverable
- **Justification / Notes**: Explicit Java failure line and stack frame identify the fully qualified class and method.

---

## 35. `apache__tika__093653111110.txt`
- **Section Index**: 35
- **Fixture Filename**: `apache__tika__093653111110.txt`
- **Content Hash**: `93db19c4496b704f`
- **Repository**: `apache/tika`
- **Raw Evidence Excerpt**:
```text
2026-08-11T02:02:13.2736706Z   {"key":"zip:duplicate-entry-names","namespace":"zip","valueType":"TEXT","cardinality":"BAG"},
2026-08-11T02:02:13.2736910Z   {"key":"zip:encrypted","namespace":"zip","valueType":"BOOLEAN","cardinality":"SIMPLE"},
2026-08-11T02:02:13.2737166Z   {"key":"zip:integrity-check-result","namespace":"zip","valueType":"TEXT","cardinality":"SIMPLE"},
2026-08-11T02:02:13.2737419Z   {"key":"zip:local-header-only-entries","namespace":"zip","valueType":"TEXT","cardinality":"BAG"},
2026-08-11T02:02:13.2737621Z   {"key":"zip:platform","namespace":"zip","valueType":"INTEGER","cardinality":"SIMPLE"},
2026-08-11T02:02:13.2737826Z   {"key":"zip:salvaged","namespace":"zip","valueType":"BOOLEAN","cardinality":"SIMPLE"},
2026-08-11T02:02:13.2738061Z   {"key":"zip:uncompressed-size","namespace":"zip","valueType":"TEXT","cardinality":"SIMPLE"},
2026-08-11T02:02:13.2738261Z   {"key":"zip:unix-mode","namespace":"zip","valueType":"INTEGER","cardinality":"SIMPLE"},
2026-08-11T02:02:13.2738492Z   {"key":"zip:version-made-by","namespace":"zip","valueType":"INTEGER","cardinality":"SIMPLE"}
2026-08-11T02:02:13.2738559Z ]
2026-08-11T02:02:13.2738623Z >
2026-08-11T02:02:13.2738693Z [INFO]
2026-08-11T02:02:13.2738852Z [ERROR] Tests run: 13, Failures: 2, Errors: 0, Skipped: 0
2026-08-11T02:02:13.2738919Z [INFO]
2026-08-11T02:02:13.2738982Z [INFO]
2026-08-11T02:02:13.2739148Z [INFO] ------------------------------------------------------------------------
2026-08-11T02:02:13.2739242Z [INFO] Skipping Apache Tika
2026-08-11T02:02:13.2739650Z [INFO] This project has been banned from the build due to previous failures.
2026-08-11T02:02:13.2739832Z [INFO] ------------------------------------------------------------------------
2026-08-11T02:02:13.2739977Z [INFO] ------------------------------------------------------------------------
2026-08-11T02:02:13.2740992Z [INFO] Reactor Summary for Apache Tika 4.0.0-SNAPSHOT:
2026-08-11T02:02:13.2741105Z [INFO]
2026-08-11T02:02:13.2741319Z [INFO] Apache Tika parent ................................. SUCCESS [  4.495 s]
2026-08-11T02:02:13.2741502Z [INFO] Apache Tika BOM .................................... SUCCESS [  0.392 s]
2026-08-11T02:02:13.2741691Z [INFO] Apache Tika Annotation Processor ................... SUCCESS [  7.337 s]
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - failure count only, no test named
- **Justification / Notes**: Two failures are reported, but no failed test class or method is identified.

---

## 36. `jline__jline3__086920871447.txt`
- **Section Index**: 36
- **Fixture Filename**: `jline__jline3__086920871447.txt`
- **Content Hash**: `626d425848185eb3`
- **Repository**: `jline/jline3`
- **Raw Evidence Excerpt**:
```text
2026-07-13T20:01:19.4045809Z [INFO]
2026-07-13T20:01:19.4070926Z [INFO] -------------------------------------------------------
2026-07-13T20:01:19.4071547Z [INFO]  T E S T S
2026-07-13T20:01:19.4071901Z [INFO] -------------------------------------------------------
2026-07-13T20:01:19.5145746Z WARNING: Unknown module: org.jline.terminal specified to --add-opens
2026-07-13T20:01:19.8091242Z [INFO] Running org.jline.nativ.JLineLibraryTest
2026-07-13T20:01:19.8788196Z [INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.054 s -- in org.jline.nativ.JLineLibraryTest
2026-07-13T20:01:19.8814312Z [INFO] Running org.jline.nativ.JLineNativeLoaderTest
2026-07-13T20:01:19.9244276Z [INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.053 s -- in org.jline.nativ.JLineNativeLoaderTest
2026-07-13T20:01:20.0748423Z [INFO]
2026-07-13T20:01:20.0748769Z [INFO] Results:
2026-07-13T20:01:20.0748953Z [INFO]
2026-07-13T20:01:20.0763732Z [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
2026-07-13T20:01:20.0763946Z [INFO]
2026-07-13T20:01:20.0769948Z [INFO]
2026-07-13T20:01:20.0770454Z [INFO] --- jar:3.5.0:jar (default-jar) @ jline-native ---
2026-07-13T20:01:20.1743645Z [INFO] Building jar: /home/runner/work/jline3/jline3/native/target/jline-native-0.1.0-1-SNAPSHOT.jar
2026-07-13T20:01:20.2818896Z [INFO]
2026-07-13T20:01:20.2823811Z [INFO] --- source:3.4.0:jar-no-fork (source-jar) @ jline-native ---
2026-07-13T20:01:20.2929791Z [INFO] Building jar: /home/runner/work/jline3/jline3/native/target/jline-native-0.1.0-1-SNAPSHOT-sources.jar
2026-07-13T20:01:20.3230003Z [INFO]
2026-07-13T20:01:20.3230726Z [INFO] ----------------------< org.jline:jline-terminal >----------------------
2026-07-13T20:01:20.3231351Z [INFO] Building JLine Terminal 0.1.0-1-SNAPSHOT                          [3/21]
2026-07-13T20:01:20.3231820Z [INFO]   from terminal/.inlined-pom.xml
2026-07-13T20:01:20.3233251Z [INFO] --------------------------------[ jar ]---------------------------------
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no failed test identified
- **Justification / Notes**: The raw lines show four tests, all with zero failures/errors, and no failed test.

---

## 37. `nitrite__nitrite-java__090043799546.txt`
- **Section Index**: 37
- **Fixture Filename**: `nitrite__nitrite-java__090043799546.txt`
- **Content Hash**: `1defb841c8c8c0d9`
- **Repository**: `nitrite/nitrite-java`
- **Raw Evidence Excerpt**:
```text
2026-07-27T16:44:58.4697060Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.302 s -- in org.dizitart.nitrite.test.collection.CollectionTest
2026-07-27T16:44:58.4719780Z [INFO] Running org.dizitart.nitrite.test.transaction.TransactionTest
2026-07-27T16:44:58.5600997Z [INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.103 s -- in org.dizitart.nitrite.test.transaction.TransactionTest
2026-07-27T16:44:58.5602495Z [INFO] Running org.dizitart.nitrite.test.compat.CompatTest
2026-07-27T16:44:58.6239972Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.072 s -- in org.dizitart.nitrite.test.compat.CompatTest
2026-07-27T16:44:58.6241474Z [INFO] Running org.dizitart.nitrite.test.migration.MigrationTest
2026-07-27T16:44:58.7198099Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.089 s -- in org.dizitart.nitrite.test.migration.MigrationTest
2026-07-27T16:44:58.7219282Z [INFO] Running org.dizitart.nitrite.test.repository.RepositoryTest
2026-07-27T16:44:58.7690174Z [INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.050 s -- in org.dizitart.nitrite.test.repository.RepositoryTest
2026-07-27T16:44:58.7934016Z [INFO]
2026-07-27T16:44:58.7934349Z [INFO] Results:
2026-07-27T16:44:58.7934662Z [INFO]
2026-07-27T16:44:58.7939659Z [INFO] Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
2026-07-27T16:44:58.7940198Z [INFO]
2026-07-27T16:44:58.7976621Z [INFO]
2026-07-27T16:44:58.7977410Z [INFO] --- native:1.1.6:test (native-test) @ nitrite-native-tests ---
2026-07-27T16:44:58.8076138Z [INFO] Using configuration from maven-surefire-plugin, execution id "default-test"
2026-07-27T16:44:58.8127727Z [INFO] ====================
2026-07-27T16:44:58.8128622Z [INFO] Initializing project: Nitrite Native Tests
2026-07-27T16:44:58.8129323Z [INFO] ====================
2026-07-27T16:44:58.8142133Z [WARNING] No jdk toolchain configuration found
2026-07-27T16:44:58.8160142Z [INFO] Found GraalVM installation from GRAALVM_HOME variable.
2026-07-27T16:44:58.9109966Z [INFO] Downloaded GraalVM reachability metadata repository from file:/home/runner/.m2/repository/org/graalvm/buildtools/graalvm-reachability-metadata/1.1.6/graalvm-reachability-metadata-1.1.6-repository.zip
2026-07-27T16:44:59.3034070Z [INFO] Using GraalVM reachability metadata repository version 1.0.7
2026-07-27T16:44:59.3317662Z [INFO] [graalvm reachability metadata repository for org.slf4j:slf4j-api:2.0.18]: Configuration directory not found. Trying latest version.
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no failed test identified
- **Justification / Notes**: The raw lines show tests with zero failures/errors and no failed test.

---

## 38. `thealgorithms__java__079347942021.txt`
- **Section Index**: 38
- **Fixture Filename**: `thealgorithms__java__079347942021.txt`
- **Content Hash**: `4e65ba5f08664755`
- **Repository**: `thealgorithms/java`
- **Raw Evidence Excerpt**:
```text
2026-06-03T16:50:45.4408695Z [INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.002 s -- in com.thealgorithms.divideandconquer.SkylineAlgorithmTest
2026-06-03T16:50:45.4410021Z [INFO] Running com.thealgorithms.divideandconquer.BinaryExponentiationTest
2026-06-03T16:50:45.4411726Z [INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.001 s -- in com.thealgorithms.divideandconquer.BinaryExponentiationTest
2026-06-03T16:50:45.4413085Z [INFO] Running com.thealgorithms.divideandconquer.ClosestPairTest
2026-06-03T16:50:45.4414298Z [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.002 s -- in com.thealgorithms.divideandconquer.ClosestPairTest
2026-06-03T16:50:45.4415818Z [INFO] Running com.thealgorithms.divideandconquer.CountingInversionsTest
2026-06-03T16:50:45.4467668Z [INFO] Tests run: 8, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.004 s -- in com.thealgorithms.divideandconquer.CountingInversionsTest
2026-06-03T16:50:45.4469146Z [INFO] Running com.thealgorithms.divideandconquer.StrassenMatrixMultiplicationTest
2026-06-03T16:50:45.4470673Z [INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.002 s -- in com.thealgorithms.divideandconquer.StrassenMatrixMultiplicationTest
2026-06-03T16:50:45.8635008Z [INFO]
2026-06-03T16:50:45.8635654Z [INFO] Results:
2026-06-03T16:50:45.8636004Z [INFO]
2026-06-03T16:50:45.8642793Z [INFO] Tests run: 9302, Failures: 0, Errors: 0, Skipped: 0
2026-06-03T16:50:45.8643500Z [INFO]
2026-06-03T16:50:45.8667412Z [INFO]
2026-06-03T16:50:45.8668303Z [INFO] --- jacoco:0.8.14:report (generate-code-coverage-report) @ Java ---
2026-06-03T16:50:45.8740116Z [INFO] Loading execution data file /home/runner/work/Java/Java/target/jacoco.exec
2026-06-03T16:50:46.3212106Z [INFO] Analyzed bundle 'Java' with 1023 classes
2026-06-03T16:50:47.2406928Z [INFO]
2026-06-03T16:50:47.2425587Z [INFO] --- jar:3.5.0:jar (default-jar) @ Java ---
2026-06-03T16:50:47.2483233Z [INFO] Downloading from central: https://repo.maven.apache.org/maven2/org/apache/maven/maven-archiver/3.6.5/maven-archiver-3.6.5.pom
2026-06-03T16:50:47.2996767Z [INFO] Downloaded from central: https://repo.maven.apache.org/maven2/org/apache/maven/maven-archiver/3.6.5/maven-archiver-3.6.5.pom (4.7 kB at 93 kB/s)
2026-06-03T16:50:47.3025982Z [INFO] Downloading from central: https://repo.maven.apache.org/maven2/org/apache/maven/shared/maven-shared-components/45/maven-shared-components-45.pom
2026-06-03T16:50:47.3488616Z [INFO] Downloaded from central: https://repo.maven.apache.org/maven2/org/apache/maven/shared/maven-shared-components/45/maven-shared-components-45.pom (3.8 kB at 81 kB/s)
2026-06-03T16:50:47.3520522Z [INFO] Downloading from central: https://repo.maven.apache.org/maven2/org/codehaus/plexus/plexus-archiver/4.10.2/plexus-archiver-4.10.2.pom
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no failed test identified
- **Justification / Notes**: The raw lines show tests with zero failures/errors and no failed test.

---

## 39. `spiculedata__saiku__079996412627.txt`
- **Section Index**: 39
- **Fixture Filename**: `spiculedata__saiku__079996412627.txt`
- **Content Hash**: `30335a7a876eab4b`
- **Repository**: `spiculedata/saiku`
- **Raw Evidence Excerpt**:
```text
2026-06-07T22:18:07.3120420Z [INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.008 s -- in org.saiku.service.schema.generate.enrich.SuggestionSetTest
2026-06-07T22:18:07.3121260Z [INFO] Running org.saiku.service.schema.generate.session.RepositorySidecarStoreTest
2026-06-07T22:18:07.3122090Z [INFO] Tests run: 6, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0 s -- in org.saiku.service.schema.generate.session.RepositorySidecarStoreTest
2026-06-07T22:18:07.3122960Z [INFO] Running org.saiku.service.schema.generate.session.SchemaGenOrchestratorTest
2026-06-07T22:18:07.6429490Z [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.324 s -- in org.saiku.service.schema.generate.session.SchemaGenOrchestratorTest
2026-06-07T22:18:07.6557420Z [INFO] Running org.saiku.service.schema.generate.session.SchemaGenSessionStoreTest
2026-06-07T22:18:07.6674460Z [INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.004 s -- in org.saiku.service.schema.generate.session.SchemaGenSessionStoreTest
2026-06-07T22:18:07.6778890Z [INFO] Running org.saiku.service.history.DashboardHistoryServiceTest
2026-06-07T22:18:07.7081100Z [INFO] Tests run: 6, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.050 s -- in org.saiku.service.history.DashboardHistoryServiceTest
2026-06-07T22:18:07.7274480Z [INFO]
2026-06-07T22:18:07.7274720Z [INFO] Results:
2026-06-07T22:18:07.7276660Z [INFO]
2026-06-07T22:18:07.7277090Z [WARNING] Tests run: 541, Failures: 0, Errors: 0, Skipped: 1
2026-06-07T22:18:07.7277370Z [INFO]
2026-06-07T22:18:07.7312400Z [INFO]
2026-06-07T22:18:07.7316870Z [INFO] --- jar:3.5.0:jar (default-jar) @ saiku-service ---
2026-06-07T22:18:07.7617050Z [INFO] Building jar: /Users/runner/work/saiku/saiku/saiku-core/saiku-service/target/saiku-service-4.4.0.jar
2026-06-07T22:18:07.8372150Z [INFO]
2026-06-07T22:18:07.8416530Z [INFO] --- source:2.3:jar-no-fork (attach-sources) @ saiku-service ---
2026-06-07T22:18:07.8743690Z [INFO] Building jar: /Users/runner/work/saiku/saiku/saiku-core/saiku-service/target/saiku-service-4.4.0-sources.jar
2026-06-07T22:18:08.0067080Z [INFO]
2026-06-07T22:18:08.0067690Z [INFO] --- source:2.3:test-jar-no-fork (attach-sources) @ saiku-service ---
2026-06-07T22:18:08.0188700Z [INFO] Building jar: /Users/runner/work/saiku/saiku/saiku-core/saiku-service/target/saiku-service-4.4.0-test-sources.jar
2026-06-07T22:18:08.0561990Z [INFO]
2026-06-07T22:18:08.0562480Z [INFO] --- spotless:2.46.1:check (spotless-check) @ saiku-service ---
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no failed test identified
- **Justification / Notes**: The raw lines show tests with zero failures/errors and no failed test.

---

## 40. `apache__tika__087468230709.txt`
- **Section Index**: 40
- **Fixture Filename**: `apache__tika__087468230709.txt`
- **Content Hash**: `bb38de75587660e3`
- **Repository**: `apache/tika`
- **Raw Evidence Excerpt**:
```text
2026-07-15T20:48:06.4194287Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.284 s -- in org.apache.tika.parser.apple.PListParserTest
2026-07-15T20:48:06.4195886Z [INFO] Running org.apache.tika.parser.iwork.AutoPageNumberUtilsTest
2026-07-15T20:48:06.4359957Z [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.014 s -- in org.apache.tika.parser.iwork.AutoPageNumberUtilsTest
2026-07-15T20:48:06.4361363Z [INFO] Running org.apache.tika.parser.iwork.iwana.IWork13ParserTest
2026-07-15T20:48:06.5688233Z [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.126 s -- in org.apache.tika.parser.iwork.iwana.IWork13ParserTest
2026-07-15T20:48:06.5689358Z [INFO] Running org.apache.tika.parser.iwork.IWorkParserTest
2026-07-15T20:48:07.3807006Z [INFO] Tests run: 21, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.806 s -- in org.apache.tika.parser.iwork.IWorkParserTest
2026-07-15T20:48:07.3808297Z [INFO] Running org.apache.tika.parser.iwork.KeynoteContentHandlerTest
2026-07-15T20:48:07.3809573Z [INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.003 s -- in org.apache.tika.parser.iwork.KeynoteContentHandlerTest
2026-07-15T20:48:07.4261539Z [INFO]
2026-07-15T20:48:07.4262080Z [INFO] Results:
2026-07-15T20:48:07.4262621Z [INFO]
2026-07-15T20:48:07.4263029Z [INFO] Tests run: 33, Failures: 0, Errors: 0, Skipped: 0
2026-07-15T20:48:07.4263510Z [INFO]
2026-07-15T20:48:07.4281321Z [INFO]
2026-07-15T20:48:07.4281670Z [INFO] --- jacoco:0.8.15:report (report) @ tika-parser-apple-module ---
2026-07-15T20:48:07.4288753Z [INFO] Loading execution data file D:\a\tika\tika\tika-parsers\tika-parsers-standard\tika-parsers-standard-modules\tika-parser-apple-module\target\jacoco.exec
2026-07-15T20:48:07.4501291Z [INFO] Analyzed bundle 'Apache Tika Apple parser module' with 21 classes
2026-07-15T20:48:07.4891236Z [INFO]
2026-07-15T20:48:07.4892136Z [INFO] --- enforcer:3.6.3:enforce (enforce-maven-version) @ tika-parser-apple-module ---
2026-07-15T20:48:07.4899622Z [INFO]
2026-07-15T20:48:07.4900358Z [INFO] --- enforcer:3.6.3:enforce (enforce-java-version) @ tika-parser-apple-module ---
2026-07-15T20:48:07.4904009Z [INFO]
2026-07-15T20:48:07.4904663Z [INFO] --- enforcer:3.6.3:enforce (enforce-maven) @ tika-parser-apple-module ---
2026-07-15T20:48:07.4922743Z [INFO] Rule 0: org.apache.maven.enforcer.rules.dependency.DependencyConvergence passed
```
- **Expected Class**: NO_TEST
- **Expected Identifier Count**: 0
- **Expected Identifiers**: NO_TEST - no failed test identified
- **Justification / Notes**: The raw lines show tests with zero failures/errors and no failed test.

---
