"""`analysis/failure_class.py` against real failure messages from the corpus.

Each message is copied verbatim (truncated as stored) from
`data/interim/parsed_outcomes.parquet`; the expected class is hand-written.
"""

from __future__ import annotations

import pytest

from analysis.failure_class import CODE, ENVIRONMENT, TIMEOUT, UNKNOWN, classify, pattern_listing

CASES = [
    # code-level
    ("AssertionError:            dk@64 diff: 2.500000 ratio: 0.534884", CODE),
    ("expected:<3> but was:<4>", CODE),
    ("1 expectation failed.", CODE),
    ("had errors ==> expected: <3> but was: <4>", CODE),
    ("did not expect to find [true] but found [false]", CODE),
    ("assert 'error' not in '2024-01-01 ... all comms\\n'", CODE),
    # an assertion whose compared text mentions a connection stays code-level
    ("AssertionError: ['Exception while handling op register-client', 'ConnectionError ...']", CODE),
    # environment
    ("RuntimeError: No CUDA GPUs are available", ENVIRONMENT),
    ("» IO Server returned HTTP response code: 429 for URL: https://huggingface.co/castorini/x", ENVIRONMENT),
    ("» Execution java.net.ConnectException", ENVIRONMENT),
    ("requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=40731)", ENVIRONMENT),
    ("» ContainerFetch Can't get Docker image: RemoteDockerImage(imageName=apache/kafka:3.8.1", ENVIRONMENT),
    # a timeout is its own class, not environment
    ("TimeoutError: Test timeout (30) hit after 30.0007685999999s.", TIMEOUT),
    ("asyncio.exceptions.TimeoutError", TIMEOUT),
    ("Failed: Timeout (>600.0s) from pytest-timeout.", TIMEOUT),
    ("OSError: Timed out trying to connect to tcp://127.0.0.1:49891 after 30 s", TIMEOUT),
    ("» Timeout Expected condition failed: waiting for visibility of element", TIMEOUT),
    ("» ConditionTimeout Condition with alias 'x' didn't complete within 10 seconds", TIMEOUT),
    ("subprocess.TimeoutExpired: Command '['git', 'fetch']' timed out after 60 seconds", TIMEOUT),
    ("java.net.SocketTimeoutException: Read timed out", TIMEOUT),
    # a strict environment pattern outranks a timeout in the same message
    ("ConnectionError: HTTPConnectionPool: Read timed out", ENVIRONMENT),
    # an identifier that merely contains the letters is not a timeout
    ("PARTIAL_TIMEOUT result must start with the partial prefix", UNKNOWN),
    # verbatim from parsed_outcomes.parquet: the path ends in `emit-partial-timeout`; the failure is an assertion
    ("PARTIAL_TIMEOUT result must still be emitted, not silently dropped: C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\\"
     "junit-3578782810607343931\\output\\json\\emit-partial-timeout ==> expected: <true> but was: <false>", CODE),
    ("see build/emit-partial-timeout/report.txt", UNKNOWN),
    ("latest_timeout_ms was not set", UNKNOWN),
    ("ReallyUntimedOutcome unexpected", UNKNOWN),
    # unknown
    ("» IllegalArgument No enum constant org.opentripplanner.transit.service.ArrivalDeparture.EITHER", UNKNOWN),
    ("» NoClassDefFound Could not initialize class org.apache.tika.metadata.TikaCoreProperties", UNKNOWN),
    ("", UNKNOWN),
]


@pytest.mark.parametrize(("message", "expected"), CASES)
def test_classification(message: str, expected: str) -> None:
    assert classify(message)[0] == expected


def test_none_and_nan_are_unknown() -> None:
    assert classify(None) == (UNKNOWN, "empty")
    assert classify(float("nan")) == (UNKNOWN, "empty")


def test_every_pattern_is_listed_for_the_audit() -> None:
    listing = "\n".join(pattern_listing())
    for name in ("cuda-gpu-unavailable", "out-of-memory", "timeout", "connection-error",
                 "dns-error", "missing-service", "assertion", "expected-vs-actual"):
        assert name in listing
