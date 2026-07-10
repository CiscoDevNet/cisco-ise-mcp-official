# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def _fake_fetch(mapping):
    """Return a fake log_service.fetch that yields a sentinel Path per target,
    or raises when the target maps to an Exception."""
    @asynccontextmanager
    async def _fetch(log_name, hostname):
        outcome = mapping.get(hostname)
        if isinstance(outcome, Exception):
            raise outcome
        yield Path(f"/tmp/{hostname}.log")
    return _fetch


class TestObservations:
    """Existing text-observation behavior is preserved (now async)."""

    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test_observes_unhealthy_nodes(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("vm218", ["PrimaryAdmin"]), _node("vm220", [], node_status="NotInSync")]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls:
            ls.fetch = _fake_fetch({"vm218": RuntimeError("x"), "vm220": RuntimeError("x")})
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        joined = " ".join(result.observations)
        assert "vm220" in joined and "NotInSync" in joined

    @pytest.mark.asyncio
    async def test_observes_missing_pan_redundancy(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls:
            ls.fetch = _fake_fetch({"vm218": RuntimeError("x")})
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        joined = " ".join(result.observations).lower()
        assert "redundancy" in joined or "secondaryadmin" in joined.replace(" ", "")

    @pytest.mark.asyncio
    async def test_standalone_has_no_missing_pan_observation(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("vm1", ["Standalone"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls:
            ls.fetch = _fake_fetch({"vm1": RuntimeError("x")})
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        joined = " ".join(result.observations)
        assert "No PrimaryAdmin" not in joined and "redundancy" not in joined

    @pytest.mark.asyncio
    async def test_scoped_suppresses_pan_redundancy_observation(self):
        # A filtered query returns only the requested node(s); deployment-wide
        # HA claims must NOT be made from that slice (mirrors the summary's
        # scope="filtered" behavior).
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls:
            ls.fetch = _fake_fetch({"vm218": RuntimeError("x")})
            result = await DeploymentDiagnosticsResolver().resolve(nodes, scoped=True)
        joined = " ".join(result.observations).lower()
        assert "redundancy" not in joined
        assert "secondaryadmin" not in joined.replace(" ", "")
        assert "no primaryadmin" not in joined

    @pytest.mark.asyncio
    async def test_scoped_still_reports_per_node_unhealthy(self):
        # Per-node status is a legitimate fact about the requested node and is
        # still reported when scoped — only deployment-wide HA claims are dropped.
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("vm220", ["PrimaryAdmin"], node_status="NotInSync")]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls:
            ls.fetch = _fake_fetch({"vm220": RuntimeError("x")})
            result = await DeploymentDiagnosticsResolver().resolve(nodes, scoped=True)
        joined = " ".join(result.observations)
        assert "vm220" in joined and "NotInSync" in joined
        assert "redundancy" not in joined.lower()


class TestNodeSelection:
    @pytest.mark.asyncio
    async def test_unhealthy_nodes_selected_first_capped_at_3(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [
            _node("c1", ["PrimaryAdmin"]),
            _node("u1", [], node_status="NotInSync"),
            _node("u2", [], node_status="Disconnected"),
            _node("u3", [], node_status="NotInSync"),
            _node("u4", [], node_status="Disconnected"),
        ]
        seen = []
        @asynccontextmanager
        async def _fetch(log_name, hostname):
            seen.append(hostname)
            yield Path(f"/tmp/{hostname}.log")
        with patch("services.deployment_diagnostics_resolver.log_service") as ls, \
             patch("services.deployment_diagnostics_resolver.SystemStatsParser") as P:
            ls.fetch = _fetch
            P.return_value.parse.return_value = {"sample_count": 1, "window": {"start": "a", "end": "b"}}
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        # Only unhealthy nodes, capped at 3
        assert set(seen) == {"u1", "u2", "u3"}
        assert set(result.system_stats["nodes"].keys()) == {"u1", "u2", "u3"}

    @pytest.mark.asyncio
    async def test_connected_fallback_when_none_unhealthy(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("c1", ["PrimaryAdmin"]), _node("c2", ["SecondaryAdmin"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls, \
             patch("services.deployment_diagnostics_resolver.SystemStatsParser") as P:
            ls.fetch = _fake_fetch({"c1": None, "c2": None})
            P.return_value.parse.return_value = {"sample_count": 1, "window": {"start": "a", "end": "b"}}
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        assert set(result.system_stats["nodes"].keys()) == {"c1", "c2"}

    @pytest.mark.asyncio
    async def test_no_nodes_leaves_system_stats_none(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        with patch("services.deployment_diagnostics_resolver.log_service"):
            result = await DeploymentDiagnosticsResolver().resolve([])
        assert result.system_stats is None

    @pytest.mark.asyncio
    async def test_uses_fqdn_when_present(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("vm218", ["PrimaryAdmin"], fqdn="vm218.marcos.com")]
        seen = []
        @asynccontextmanager
        async def _fetch(log_name, hostname):
            seen.append(hostname)
            yield Path("/tmp/x.log")
        with patch("services.deployment_diagnostics_resolver.log_service") as ls, \
             patch("services.deployment_diagnostics_resolver.SystemStatsParser") as P:
            ls.fetch = _fetch
            P.return_value.parse.return_value = {"sample_count": 1, "window": {"start": "a", "end": "b"}}
            await DeploymentDiagnosticsResolver().resolve(nodes)
        assert seen == ["vm218.marcos.com"]


class TestFailureIsolationAndSummary:
    @pytest.mark.asyncio
    async def test_one_node_fails_others_still_reported(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("ok1", ["PrimaryAdmin"]), _node("bad1", ["SecondaryAdmin"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls, \
             patch("services.deployment_diagnostics_resolver.SystemStatsParser") as P:
            ls.fetch = _fake_fetch(
                {"ok1": None, "bad1": RuntimeError("404 for https://10.0.0.1/admin/x.log.zip")}
            )
            P.return_value.parse.return_value = {"sample_count": 1, "window": {"start": "a", "end": "b"}}
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        nodes_out = result.system_stats["nodes"]
        assert nodes_out["ok1"]["status"] == "ok"
        assert nodes_out["bad1"]["status"] == "unavailable"
        assert "reason" in nodes_out["bad1"]
        # The reason must NOT leak internal fetch detail (status code, URL, host).
        reason = nodes_out["bad1"]["reason"]
        assert "404" not in reason
        assert "http" not in reason.lower()
        assert "10.0.0.1" not in reason

    @pytest.mark.asyncio
    async def test_no_samples_marks_unavailable(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("n1", ["PrimaryAdmin"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls, \
             patch("services.deployment_diagnostics_resolver.SystemStatsParser") as P:
            ls.fetch = _fake_fetch({"n1": None})
            P.return_value.parse.return_value = None  # no samples in window
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        assert result.system_stats["nodes"]["n1"]["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_summary_observation_reports_coverage(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("ok1", ["PrimaryAdmin"]), _node("bad1", ["SecondaryAdmin"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls, \
             patch("services.deployment_diagnostics_resolver.SystemStatsParser") as P:
            ls.fetch = _fake_fetch({"ok1": None, "bad1": RuntimeError("boom")})
            P.return_value.parse.return_value = {"sample_count": 1, "window": {"start": "a", "end": "b"}}
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        joined = " ".join(result.observations)
        assert "1 of 2" in joined and "individual node" in joined.lower()

    @pytest.mark.asyncio
    async def test_top_level_window_anchor_and_duration(self):
        from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
        nodes = [_node("n1", ["PrimaryAdmin"])]
        with patch("services.deployment_diagnostics_resolver.log_service") as ls, \
             patch("services.deployment_diagnostics_resolver.SystemStatsParser") as P:
            ls.fetch = _fake_fetch({"n1": None})
            P.return_value.parse.return_value = {"sample_count": 1, "window": {"start": "a", "end": "b"}}
            result = await DeploymentDiagnosticsResolver().resolve(nodes)
        assert result.system_stats["anchor"] == "latest_log_timestamp"
        assert result.system_stats["duration_minutes"] == 60
