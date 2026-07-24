# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


def _node(hostname, roles, node_status="Connected", fqdn=None):
    from models.deployment_models import DeploymentNodeSummary
    return DeploymentNodeSummary(
        hostname=hostname, fqdn=fqdn, ip_address=None,
        roles=roles, services=[], node_status=node_status,
    )


_SUMMARY_XML = b"""<?xml version="1.0"?>
<dashboardResult>
  <lstProcessStatuses>
    <server>vm218</server><status>Failed</status>
    <applicationServer>1</applicationServer><database>0</database>
  </lstProcessStatuses>
  <lstProcessStatuses>
    <server>vm219</server><status>Failed</status>
    <applicationServer>1</applicationServer><database>1</database>
  </lstProcessStatuses>
  <lstSystemStatus60Min>
    <server>vm218</server><timestamp>2026-07-16 07:38:00</timestamp>
    <cpuUtilization>4</cpuUtilization><memoryUtilization>57</memoryUtilization><latency>0</latency>
  </lstSystemStatus60Min>
</dashboardResult>
"""


class _FakeStreamResponse:
    def __init__(self, body: bytes, chunk: int = 32):
        self._body = body
        self._chunk = chunk

    async def aiter_bytes(self):
        for i in range(0, len(self._body), self._chunk):
            yield self._body[i:i + self._chunk]


def _mnt_streaming(body: bytes):
    """MnT client whose get_stream yields a fake streaming response."""
    mnt = MagicMock()

    @asynccontextmanager
    async def _get_stream(endpoint):
        yield _FakeStreamResponse(body)

    mnt.get_stream = _get_stream
    return mnt


def _mnt_stream_raising(exc):
    mnt = MagicMock()

    @asynccontextmanager
    async def _get_stream(endpoint):
        raise exc
        yield  # pragma: no cover

    mnt.get_stream = _get_stream
    return mnt


class _RejectingGate:
    """A gate whose guard() rejects immediately with ISE_BUSY."""

    def guard(self):
        return self

    async def __aenter__(self):
        from models.error_models import ErrorCategory, raise_tool_error
        raise_tool_error(
            ErrorCategory.EXTERNAL_ERROR, "ISE_BUSY",
            "The ISE MnT node is busy. Retry shortly.", retry=True,
        )

    async def __aexit__(self, *exc):
        return False


class _PassGate:
    """A gate whose guard() always admits."""

    def guard(self):
        return self

    async def __aenter__(self):
        return None

    async def __aexit__(self, *exc):
        return False


def _resolver(mnt, gate=None):
    from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
    return DeploymentDiagnosticsResolver(mnt, gate=gate or _PassGate())


class TestObservations:
    @pytest.mark.asyncio
    async def test_observes_unhealthy_nodes(self):
        nodes = [_node("vm218", ["PrimaryAdmin"]), _node("vm220", [], node_status="NotInSync")]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations)
        assert "vm220" in joined and "NotInSync" in joined

    @pytest.mark.asyncio
    async def test_observes_missing_pan_redundancy(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations).lower()
        assert "redundancy" in joined or "secondaryadmin" in joined.replace(" ", "")

    @pytest.mark.asyncio
    async def test_standalone_has_no_missing_pan_observation(self):
        nodes = [_node("vm1", ["Standalone"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations)
        assert "No PrimaryAdmin" not in joined and "redundancy" not in joined

    @pytest.mark.asyncio
    async def test_scoped_suppresses_pan_redundancy_observation(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes, scoped=True)
        joined = " ".join(result.observations).lower()
        assert "redundancy" not in joined
        assert "no primaryadmin" not in joined

    @pytest.mark.asyncio
    async def test_scoped_still_reports_per_node_unhealthy(self):
        nodes = [_node("vm220", ["PrimaryAdmin"], node_status="NotInSync")]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes, scoped=True)
        joined = " ".join(result.observations)
        assert "vm220" in joined and "NotInSync" in joined


class TestSystemStats:
    @pytest.mark.asyncio
    async def test_stats_keyed_by_nodes_in_list(self):
        nodes = [_node("vm218", ["PrimaryAdmin"]), _node("vm219", ["SecondaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        assert result.system_stats["source"] == "getSystemSummaryDetails"
        assert result.system_stats["duration_minutes"] == 60
        assert set(result.system_stats["nodes"].keys()) == {"vm218", "vm219"}
        assert result.system_stats["nodes"]["vm218"]["processes_down"] == ["database"]
        assert result.system_stats["nodes"]["vm218"]["cpu_percent"]["latest"] == 4.0

    @pytest.mark.asyncio
    async def test_api_row_not_in_node_list_is_excluded(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        assert set(result.system_stats["nodes"].keys()) == {"vm218"}

    @pytest.mark.asyncio
    async def test_down_process_generates_observation(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations)
        assert "vm218" in joined
        assert "database" in joined.lower() and "not running" in joined.lower()

    @pytest.mark.asyncio
    async def test_no_nodes_leaves_system_stats_none(self):
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve([])
        assert result.system_stats is None

    @pytest.mark.asyncio
    async def test_api_failure_degrades_with_generic_reason(self):
        import httpx
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        mnt = _mnt_stream_raising(httpx.ConnectError("boom to 10.0.0.1"))
        result = await _resolver(mnt).resolve(nodes)
        assert result.system_stats["status"] == "unavailable"
        reason = result.system_stats["reason"]
        assert "10.0.0.1" not in reason and "boom" not in reason.lower()
        # Base observations still run despite the API failure.
        joined = " ".join(result.observations).lower()
        assert "redundancy" in joined or "secondaryadmin" in joined.replace(" ", "")

    @pytest.mark.asyncio
    async def test_malformed_xml_degrades_with_generic_reason(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(b"<dashboardResult><nope>")).resolve(nodes)
        assert result.system_stats["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_gate_rejection_degrades_with_busy_reason(self):
        # A busy gate must NOT fail the tool; it degrades to an unavailable
        # block with a distinct retry-oriented reason.
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        resolver = _resolver(_mnt_streaming(_SUMMARY_XML), gate=_RejectingGate())
        result = await resolver.resolve(nodes)
        assert result.system_stats["status"] == "unavailable"
        reason = result.system_stats["reason"].lower()
        assert "busy" in reason or "retry" in reason
        # Distinct from the generic reason.
        from services.deployment_diagnostics_resolver import (
            _BUSY_REASON, _GENERIC_REASON,
        )
        assert result.system_stats["reason"] == _BUSY_REASON
        assert _BUSY_REASON != _GENERIC_REASON
        # Base observations still present.
        assert " ".join(result.observations)
