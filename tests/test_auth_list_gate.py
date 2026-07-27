# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

import httpx
import pytest
from fastmcp.exceptions import ToolError as McpToolError

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class FakeClock:
    """Deterministic monotonic clock for gate tests."""

    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, secs):
        self.t += secs


def _gate(max_concurrency=1, min_interval_s=0.0, base=5.0, mx=300.0, clock=None):
    from clients.auth_list_gate import AuthListGate

    return AuthListGate(
        max_concurrency=max_concurrency,
        min_interval_s=min_interval_s,
        backoff_base_s=base,
        backoff_max_s=mx,
        time_fn=(clock or FakeClock()),
        jitter_fn=lambda: 0.0,
    )


@pytest.mark.asyncio
async def test_second_concurrent_call_rejects_immediately():
    gate = _gate(max_concurrency=1)
    async with gate.guard():
        with pytest.raises(McpToolError) as ei:
            async with gate.guard():
                pass
        assert "ISE_BUSY" in str(ei.value)


@pytest.mark.asyncio
async def test_sequential_calls_after_release_succeed():
    gate = _gate(max_concurrency=1)
    async with gate.guard():
        pass
    async with gate.guard():
        pass  # no error


@pytest.mark.asyncio
async def test_min_interval_floor_rejects_too_soon():
    clock = FakeClock()
    gate = _gate(min_interval_s=10.0, clock=clock)
    async with gate.guard():
        pass
    # Only 3s later -> too soon.
    clock.advance(3.0)
    with pytest.raises(McpToolError) as ei:
        async with gate.guard():
            pass
    assert "ISE_BUSY" in str(ei.value)
    # Past the interval -> allowed.
    clock.advance(10.0)
    async with gate.guard():
        pass


@pytest.mark.asyncio
async def test_breaker_opens_on_502_then_rejects():
    clock = FakeClock()
    gate = _gate(base=5.0, mx=300.0, clock=clock)
    resp = httpx.Response(502, request=httpx.Request("GET", "https://x/y"))
    with pytest.raises(httpx.HTTPStatusError):
        async with gate.guard():
            raise httpx.HTTPStatusError("bad gateway", request=resp.request, response=resp)
    # Breaker open for base (5s) -> immediate call rejects.
    with pytest.raises(McpToolError) as ei:
        async with gate.guard():
            pass
    assert "ISE_BUSY" in str(ei.value)


@pytest.mark.asyncio
async def test_breaker_window_doubles_and_caps():
    clock = FakeClock()
    gate = _gate(base=5.0, mx=8.0, clock=clock)

    async def fail():
        resp = httpx.Response(503, request=httpx.Request("GET", "https://x/y"))
        with pytest.raises(httpx.HTTPStatusError):
            async with gate.guard():
                raise httpx.HTTPStatusError("x", request=resp.request, response=resp)

    await fail()                 # window = 5
    clock.advance(5.0)           # window elapsed -> half-open probe allowed
    await fail()                 # probe failed -> window = min(10, 8) = 8
    # t = 1005, open_until = 1005 + 8 = 1013
    clock.advance(7.9)           # t = 1012.9, still within window
    with pytest.raises(McpToolError):
        async with gate.guard():
            pass                 # still within 8s window
    # Now advance just past the 8s cap to verify probe is admitted.
    # An uncapped 10s window would reject until t=1015, but the cap ends at 1013.
    clock.advance(0.2)           # t = 1013.1, past the capped window
    async with gate.guard():
        pass                     # half-open probe admitted (cap effective)


@pytest.mark.asyncio
async def test_half_open_probe_success_resets_breaker():
    clock = FakeClock()
    gate = _gate(base=5.0, clock=clock)
    resp = httpx.Response(504, request=httpx.Request("GET", "https://x/y"))
    with pytest.raises(httpx.HTTPStatusError):
        async with gate.guard():
            raise httpx.HTTPStatusError("x", request=resp.request, response=resp)
    clock.advance(5.0)           # window elapsed -> probe allowed
    async with gate.guard():
        pass                     # probe succeeds -> reset
    # Breaker fully closed now: another call proceeds with no wait.
    async with gate.guard():
        pass


@pytest.mark.asyncio
async def test_non_distress_exception_does_not_open_breaker():
    gate = _gate()
    with pytest.raises(ValueError):
        async with gate.guard():
            raise ValueError("parse error, not MnT distress")
    # Breaker stayed closed -> next call proceeds.
    async with gate.guard():
        pass


@pytest.mark.asyncio
async def test_non_distress_exception_during_probe_does_not_lock_gate():
    """A non-distress failure during a half-open probe must not permanently lock the gate."""
    clock = FakeClock()
    gate = _gate(base=5.0, clock=clock)
    # Open the breaker with a distress failure.
    resp = httpx.Response(502, request=httpx.Request("GET", "https://x/y"))
    with pytest.raises(httpx.HTTPStatusError):
        async with gate.guard():
            raise httpx.HTTPStatusError("bad gateway", request=resp.request, response=resp)
    # Advance past the window so the next call is admitted as a half-open probe.
    clock.advance(5.0)
    # The probe raises a non-distress exception (e.g. ValueError).
    with pytest.raises(ValueError):
        async with gate.guard():
            raise ValueError("non-distress parse error during probe")
    # The gate must NOT be permanently locked. The next call should succeed.
    async with gate.guard():
        pass  # must be admitted, not reject with ISE_BUSY
