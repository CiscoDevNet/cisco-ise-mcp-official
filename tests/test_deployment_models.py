# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def _node(hostname, roles, node_status="Connected"):
    from models.deployment_models import DeploymentNodeSummary
    return DeploymentNodeSummary(
        hostname=hostname,
        fqdn=f"{hostname}.example.com",
        ip_address="10.0.0.1",
        roles=roles,
        services=["Session"],
        node_status=node_status,
    )


class TestFromApi:
    def test_maps_api_keys(self):
        from models.deployment_models import DeploymentNodeSummary
        raw = {
            "hostname": "vm218",
            "fqdn": "vm218.marcos.com",
            "ipAddress": "10.127.96.218",
            "roles": ["PrimaryAdmin", "PrimaryMonitoring"],
            "services": ["Session", "Profiler"],
            "nodeStatus": "Connected",
        }
        node = DeploymentNodeSummary.from_api(raw)
        assert node.hostname == "vm218"
        assert node.ip_address == "10.127.96.218"
        assert node.node_status == "Connected"
        assert node.roles == ["PrimaryAdmin", "PrimaryMonitoring"]

    def test_missing_optional_fields_default(self):
        from models.deployment_models import DeploymentNodeSummary
        node = DeploymentNodeSummary.from_api({"hostname": "vm1"})
        assert node.roles == []
        assert node.services == []
        assert node.node_status is None


class TestHealthSummaryVerdict:
    def test_healthy_two_pan_all_connected(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [
            _node("vm218", ["PrimaryAdmin", "PrimaryMonitoring"]),
            _node("vm219", ["SecondaryAdmin", "SecondaryMonitoring"]),
        ]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.verdict == "healthy"
        assert s.ha_ready is True
        assert s.primary_admin_present is True
        assert s.secondary_admin_present is True
        assert s.unhealthy_nodes == []
        assert s.status_counts == {"Connected": 2}
        assert s.total_nodes == 2

    def test_degraded_when_a_node_not_connected(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [
            _node("vm218", ["PrimaryAdmin"]),
            _node("vm219", ["SecondaryAdmin"]),
            _node("vm220", [], node_status="NotInSync"),
        ]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.verdict == "degraded"
        assert s.unhealthy_nodes == ["vm220"]
        assert s.ha_ready is True  # both PANs present and connected

    def test_degraded_when_no_secondary_admin(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.verdict == "degraded"
        assert s.secondary_admin_present is False
        assert s.ha_ready is False

    def test_critical_when_pan_not_connected(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [
            _node("vm218", ["PrimaryAdmin"], node_status="Disconnected"),
            _node("vm219", ["SecondaryAdmin"]),
        ]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.verdict == "critical"
        assert "vm218" in s.unhealthy_nodes

    def test_critical_when_no_primary_admin(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm219", ["SecondaryAdmin"])]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.verdict == "critical"
        assert s.primary_admin_present is False

    def test_empty_nodes_is_critical(self):
        from models.deployment_models import DeploymentHealthSummary
        s = DeploymentHealthSummary.from_nodes([])
        assert s.verdict == "critical"
        assert s.total_nodes == 0

    def test_status_counts_aggregates(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [
            _node("a", ["PrimaryAdmin"]),
            _node("b", ["SecondaryAdmin"]),
            _node("c", [], node_status="NotInSync"),
            _node("d", [], node_status="NotInSync"),
        ]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.status_counts == {"Connected": 2, "NotInSync": 2}

    def test_standalone_connected_is_healthy(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm1", ["Standalone"])]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.verdict == "healthy"
        assert s.ha_ready is False
        assert s.primary_admin_present is False
        assert s.secondary_admin_present is False
        assert s.unhealthy_nodes == []

    def test_standalone_disconnected_is_critical(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm1", ["Standalone"], node_status="Disconnected")]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.verdict == "critical"
        assert "vm1" in s.unhealthy_nodes


class TestDeploymentHealthResult:
    def test_diagnostics_optional_defaults_none(self):
        from models.deployment_models import (
            DeploymentHealthResult,
            DeploymentHealthSummary,
        )
        result = DeploymentHealthResult(
            nodes=[],
            summary=DeploymentHealthSummary.from_nodes([]),
        )
        assert result.diagnostics is None
        # exclude_none keeps diagnostics out of the payload when absent
        assert "diagnostics" not in result.model_dump_json(exclude_none=True)


class TestScopedHealthSummary:
    def test_scoped_single_healthy_node(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm219", ["SecondaryAdmin", "SecondaryMonitoring"])]
        s = DeploymentHealthSummary.from_nodes(nodes, requested_hostnames=["vm219"])
        assert s.scope == "filtered"
        assert s.verdict == "healthy"
        assert s.primary_admin_present is None
        assert s.secondary_admin_present is None
        assert s.ha_ready is None
        assert s.unhealthy_nodes == []
        assert s.total_nodes == 1
        assert s.not_found_hostnames is None
        assert s.scope_note is not None
        assert "redundancy" in s.scope_note.lower()

    def test_scoped_not_connected_is_critical(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm219", ["SecondaryAdmin"], node_status="NotInSync")]
        s = DeploymentHealthSummary.from_nodes(nodes, requested_hostnames=["vm219"])
        assert s.scope == "filtered"
        assert s.verdict == "critical"
        assert s.ha_ready is None
        assert "vm219" in s.unhealthy_nodes

    def test_scoped_ha_fields_dropped_from_json(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm219", ["SecondaryAdmin"])]
        s = DeploymentHealthSummary.from_nodes(nodes, requested_hostnames=["vm219"])
        payload = s.model_dump_json(exclude_none=True)
        assert "ha_ready" not in payload
        assert "primary_admin_present" not in payload
        assert '"scope":"filtered"' in payload
        # The scope note must survive serialization in filtered mode so the
        # caller sees the "don't infer deployment-wide HA" directive inline.
        assert "scope_note" in payload

    def test_unscoped_default_reports_deployment_scope(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [
            _node("vm218", ["PrimaryAdmin"]),
            _node("vm219", ["SecondaryAdmin"]),
        ]
        s = DeploymentHealthSummary.from_nodes(nodes)
        assert s.scope == "deployment"
        assert s.ha_ready is True
        assert s.scope_note is None

    def test_scoped_no_match_is_critical_and_reports_not_found(self):
        from models.deployment_models import DeploymentHealthSummary
        s = DeploymentHealthSummary.from_nodes([], requested_hostnames=["ghost"])
        assert s.scope == "filtered"
        assert s.verdict == "critical"
        assert s.total_nodes == 0
        assert s.not_found_hostnames == ["ghost"]

    def test_scoped_partial_missing_lists_not_found(self):
        from models.deployment_models import DeploymentHealthSummary
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        s = DeploymentHealthSummary.from_nodes(
            nodes, requested_hostnames=["vm218", "ghost"]
        )
        assert s.not_found_hostnames == ["ghost"]
        assert s.verdict == "healthy"  # the one matched node is Connected
