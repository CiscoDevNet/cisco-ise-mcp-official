# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

from typing import Any, Literal, Optional

from pydantic import Field

from models.base import IseResultModel

_CONNECTED = "Connected"


class DeploymentNodeSummary(IseResultModel):
    """A single deployed ISE node as reported by GET /deployment/node."""

    hostname: str = Field(..., description="Short hostname of the node")
    fqdn: Optional[str] = Field(None, description="Fully qualified domain name")
    ip_address: Optional[str] = Field(None, description="Management IP address")
    roles: list[str] = Field(
        default_factory=list,
        description="Node personas/roles, e.g. PrimaryAdmin, SecondaryMonitoring",
    )
    services: list[str] = Field(
        default_factory=list,
        description="Enabled services, e.g. Session, Profiler, pxGrid",
    )
    node_status: Optional[str] = Field(
        None,
        description="Deployment status, e.g. Connected, Disconnected, NotInSync",
    )

    @classmethod
    def from_api(cls, raw: dict) -> "DeploymentNodeSummary":
        """Build from a raw ISE deployment-node dict (camelCase keys)."""
        return cls(
            hostname=raw.get("hostname", ""),
            fqdn=raw.get("fqdn"),
            ip_address=raw.get("ipAddress"),
            roles=raw.get("roles") or [],
            services=raw.get("services") or [],
            node_status=raw.get("nodeStatus"),
        )


class DeploymentHealthSummary(IseResultModel):
    """Derived, deterministic health assessment over the node list."""

    total_nodes: int = Field(..., ge=0)
    status_counts: dict[str, int] = Field(
        ..., description="Count of nodes by nodeStatus value"
    )
    unhealthy_nodes: list[str] = Field(
        ..., description="Hostnames whose nodeStatus is not Connected"
    )
    scope: Literal["deployment", "filtered"] = Field(
        ...,
        description=(
            "'deployment' when the summary covers every node; 'filtered' when the "
            "caller restricted the query to specific hostnames. Deployment-wide HA "
            "claims are omitted for a filtered scope."
        ),
    )
    primary_admin_present: Optional[bool] = Field(
        None,
        description=(
            "A node with the PrimaryAdmin (Primary PAN) role exists. Null when "
            "scope is 'filtered', since HA is a deployment-wide property."
        ),
    )
    secondary_admin_present: Optional[bool] = Field(
        None,
        description=(
            "A node with the SecondaryAdmin (Secondary PAN) role exists. Null when "
            "scope is 'filtered'."
        ),
    )
    ha_ready: Optional[bool] = Field(
        None,
        description=(
            "True iff both PrimaryAdmin and SecondaryAdmin nodes exist and every "
            "admin (PAN) node is Connected. Reflects PAN redundancy only. Null "
            "when scope is 'filtered'."
        ),
    )
    not_found_hostnames: Optional[list[str]] = Field(
        None,
        description=(
            "Requested hostnames that matched no node in the deployment. Present "
            "only for a filtered scope when one or more requested nodes were not "
            "found; null otherwise."
        ),
    )
    scope_note: Optional[str] = Field(
        None,
        description=(
            "Present only for a filtered scope. States that this result "
            "describes only the requested nodes and that deployment-wide "
            "conclusions (PAN redundancy, HA readiness, whether a Secondary "
            "PAN exists) cannot be drawn from it."
        ),
    )
    verdict: Literal["healthy", "degraded", "critical"] = Field(
        ..., description="Overall deployment health verdict"
    )

    @classmethod
    def from_nodes(
        cls,
        nodes: list[DeploymentNodeSummary],
        requested_hostnames: Optional[list[str]] = None,
    ) -> "DeploymentHealthSummary":
        """Derive a health summary over ``nodes``.

        Args:
            nodes: The node list to summarize.
            requested_hostnames: The hostnames the caller filtered on, if any.
                When non-empty the summary is "filtered": it cannot support
                deployment-wide HA claims, so the HA fields are omitted, the
                verdict is derived purely from node status, and any requested
                name that matched no node is reported in not_found_hostnames.
        """
        requested = requested_hostnames or []
        scoped = bool(requested)
        status_counts: dict[str, int] = {}
        unhealthy: list[str] = []
        primary = False
        secondary = False
        standalone = False
        admin_all_connected = True

        for node in nodes:
            status = node.node_status or "Unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
            connected = node.node_status == _CONNECTED
            if not connected:
                unhealthy.append(node.hostname)
            is_primary = "PrimaryAdmin" in node.roles
            is_secondary = "SecondaryAdmin" in node.roles
            is_standalone = "Standalone" in node.roles
            if is_primary:
                primary = True
            if is_secondary:
                secondary = True
            if is_standalone:
                standalone = True
            if (is_primary or is_secondary or is_standalone) and not connected:
                admin_all_connected = False

        if scoped:
            # A filtered slice describes only the requested nodes; it makes no
            # deployment-wide HA claims. Verdict is binary: healthy iff every
            # requested node is Connected and at least one matched, otherwise
            # critical. Requested names that matched no node are surfaced so a
            # typo/removed-node query is not falsely reported healthy.
            found_hostnames = {node.hostname for node in nodes}
            not_found = [h for h in requested if h not in found_hostnames]
            verdict: Literal["healthy", "degraded", "critical"] = (
                "critical" if (unhealthy or not nodes) else "healthy"
            )
            return cls(
                total_nodes=len(nodes),
                status_counts=status_counts,
                unhealthy_nodes=unhealthy,
                scope="filtered",
                primary_admin_present=None,
                secondary_admin_present=None,
                ha_ready=None,
                not_found_hostnames=(not_found or None),
                scope_note=(
                    "Scoped to the requested hostname(s); describes only these "
                    "nodes. Do not infer deployment-wide HA, PAN redundancy, or "
                    "the absence of a Secondary PAN from this result — "
                    "non-matching nodes were excluded. Re-run without "
                    "`hostnames` to assess deployment HA."
                ),
                verdict=verdict,
            )

        admin_present = primary or standalone
        ha_ready = primary and secondary and admin_all_connected

        if (not admin_present) or (not admin_all_connected):
            verdict = "critical"
        elif unhealthy or (primary and not secondary):
            verdict = "degraded"
        else:
            verdict = "healthy"

        return cls(
            total_nodes=len(nodes),
            status_counts=status_counts,
            unhealthy_nodes=unhealthy,
            scope="deployment",
            primary_admin_present=primary,
            secondary_admin_present=secondary,
            ha_ready=ha_ready,
            verdict=verdict,
        )


class DeploymentDiagnostics(IseResultModel):
    """Deeper diagnostics, populated only when deep_diagnostics=True.

    Today this carries derived observations. The next feature adds
    log-backed system statistics via the `system_stats` field without
    changing this model's consumers.
    """

    observations: list[str] = Field(
        default_factory=list,
        description="Human-readable derived observations about node health",
    )
    system_stats: Optional[dict[str, Any]] = Field(
        None,
        description="Log-derived per-node system statistics (added by a later feature)",
    )


class DeploymentHealthResult(IseResultModel):
    """Full response for the ise_deployment_health tool."""

    nodes: list[DeploymentNodeSummary] = Field(..., description="Deployed nodes")
    summary: DeploymentHealthSummary = Field(..., description="Derived health summary")
    diagnostics: Optional[DeploymentDiagnostics] = Field(
        None, description="Deep diagnostics; present only when deep_diagnostics=True"
    )
