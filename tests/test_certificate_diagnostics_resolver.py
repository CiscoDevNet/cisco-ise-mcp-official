# tests/test_certificate_diagnostics_resolver.py
# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


def _raw_node(hostname, services, fqdn=None, node_status="Connected"):
    return {
        "hostname": hostname,
        "fqdn": fqdn,
        "ipAddress": None,
        "roles": [],
        "services": services,
        "nodeStatus": node_status,
    }


def _fake_fetch(mapping):
    @asynccontextmanager
    async def _fetch(log_name, hostname):
        outcome = mapping.get(hostname)
        if isinstance(outcome, Exception):
            raise outcome
        yield Path(f"/tmp/{hostname}.log")
    return _fetch


def _make_resolver():
    from services.certificate_diagnostics_resolver import CertificateDiagnosticsResolver
    factory = MagicMock()
    factory.get_client.return_value = MagicMock()
    return CertificateDiagnosticsResolver(factory)


class TestPsnDetection:
    def test_is_psn_true_for_session(self):
        from services.certificate_diagnostics_resolver import is_psn
        from models.deployment_models import DeploymentNodeSummary
        node = DeploymentNodeSummary.from_api(_raw_node("p1", ["Session", "Profiler"]))
        assert is_psn(node) is True

    def test_is_psn_false_for_admin_only(self):
        from services.certificate_diagnostics_resolver import is_psn
        from models.deployment_models import DeploymentNodeSummary
        node = DeploymentNodeSummary.from_api(_raw_node("a1", []))
        assert is_psn(node) is False


class TestResolve:
    @pytest.mark.asyncio
    async def test_scans_only_psn_nodes(self):
        resolver = _make_resolver()
        nodes = {"response": [
            _raw_node("psn1", ["Session"]),
            _raw_node("admin1", []),  # not a PSN
        ]}
        with patch.object(resolver, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("services.certificate_diagnostics_resolver.log_service") as ls, \
             patch("services.certificate_diagnostics_resolver.CertificateLogScanner") as S:
            mock_exec.return_value = nodes
            ls.fetch = _fake_fetch({"psn1": None})
            S.return_value.scan.return_value = {"matches": ["Unknown CA line"], "total_matches": 1}
            result = await resolver.resolve()
        hostnames = {n.hostname for n in result.nodes}
        assert hostnames == {"psn1"}
        assert result.psn_nodes_total == 1
        assert result.psn_nodes_succeeded == 1
        assert result.nodes[0].matches[0].line == "Unknown CA line"

    @pytest.mark.asyncio
    async def test_hostnames_filter_skips_non_psn_silently(self):
        resolver = _make_resolver()
        nodes = {"response": [
            _raw_node("psn1", ["Session"]),
            _raw_node("admin1", []),
        ]}
        with patch.object(resolver, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("services.certificate_diagnostics_resolver.log_service") as ls, \
             patch("services.certificate_diagnostics_resolver.CertificateLogScanner") as S:
            mock_exec.return_value = nodes
            ls.fetch = _fake_fetch({"psn1": None})
            S.return_value.scan.return_value = None  # no matches
            # Request one PSN and one non-PSN; the non-PSN must be silently dropped.
            result = await resolver.resolve(hostnames=["psn1", "admin1"])
        assert {n.hostname for n in result.nodes} == {"psn1"}
        assert result.psn_nodes_total == 1

    @pytest.mark.asyncio
    async def test_cap_at_five_psn_nodes(self):
        resolver = _make_resolver()
        nodes = {"response": [_raw_node(f"psn{i}", ["Session"]) for i in range(7)]}
        seen = []
        @asynccontextmanager
        async def _fetch(log_name, hostname):
            seen.append(hostname)
            yield Path(f"/tmp/{hostname}.log")
        with patch.object(resolver, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("services.certificate_diagnostics_resolver.log_service") as ls, \
             patch("services.certificate_diagnostics_resolver.CertificateLogScanner") as S:
            mock_exec.return_value = nodes
            ls.fetch = _fetch
            S.return_value.scan.return_value = None
            result = await resolver.resolve()
        assert len(seen) == 5
        assert result.psn_nodes_scanned == 5
        assert result.psn_nodes_total == 7

    @pytest.mark.asyncio
    async def test_uses_fqdn_when_present(self):
        resolver = _make_resolver()
        nodes = {"response": [_raw_node("psn1", ["Session"], fqdn="psn1.marcos.com")]}
        seen = []
        @asynccontextmanager
        async def _fetch(log_name, hostname):
            seen.append(hostname)
            yield Path("/tmp/x.log")
        with patch.object(resolver, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("services.certificate_diagnostics_resolver.log_service") as ls, \
             patch("services.certificate_diagnostics_resolver.CertificateLogScanner") as S:
            mock_exec.return_value = nodes
            ls.fetch = _fetch
            S.return_value.scan.return_value = None
            await resolver.resolve()
        assert seen == ["psn1.marcos.com"]

    @pytest.mark.asyncio
    async def test_one_node_fails_others_reported_and_reason_generic(self):
        resolver = _make_resolver()
        nodes = {"response": [
            _raw_node("ok1", ["Session"]),
            _raw_node("bad1", ["Profiler"]),
        ]}
        with patch.object(resolver, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("services.certificate_diagnostics_resolver.log_service") as ls, \
             patch("services.certificate_diagnostics_resolver.CertificateLogScanner") as S:
            mock_exec.return_value = nodes
            ls.fetch = _fake_fetch({"ok1": None, "bad1": RuntimeError("404 https://10.0.0.1/admin/x")})
            S.return_value.scan.return_value = {"matches": ["Unknown CA"], "total_matches": 1}
            result = await resolver.resolve()
        by_host = {n.hostname: n for n in result.nodes}
        assert by_host["ok1"].status == "ok"
        assert by_host["bad1"].status == "unavailable"
        reason = by_host["bad1"].reason
        assert "404" not in reason and "10.0.0.1" not in reason and "http" not in reason.lower()
        assert result.psn_nodes_succeeded == 1
        assert "1 of 2" in result.coverage_note

    @pytest.mark.asyncio
    async def test_no_matches_marks_node_ok_with_empty_matches(self):
        resolver = _make_resolver()
        nodes = {"response": [_raw_node("psn1", ["Session"])]}
        with patch.object(resolver, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("services.certificate_diagnostics_resolver.log_service") as ls, \
             patch("services.certificate_diagnostics_resolver.CertificateLogScanner") as S:
            mock_exec.return_value = nodes
            ls.fetch = _fake_fetch({"psn1": None})
            S.return_value.scan.return_value = None
            result = await resolver.resolve()
        assert result.nodes[0].status == "ok"
        assert result.nodes[0].matches == []
        assert result.nodes[0].total_matches == 0

    @pytest.mark.asyncio
    async def test_no_psn_nodes_returns_empty_scan(self):
        resolver = _make_resolver()
        nodes = {"response": [_raw_node("admin1", [])]}
        with patch.object(resolver, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("services.certificate_diagnostics_resolver.log_service"):
            mock_exec.return_value = nodes
            result = await resolver.resolve()
        assert result.nodes == []
        assert result.psn_nodes_total == 0
        assert "0" in result.coverage_note
