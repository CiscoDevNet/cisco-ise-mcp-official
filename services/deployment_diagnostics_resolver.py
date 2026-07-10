# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Derives deeper deployment diagnostics from the node list.

Produces human-readable observations derived from node status and roles, and —
when logs are reachable — log-backed per-node system statistics (CPU, memory,
disk) read from each node's ``iseLocalStore`` log via the log service.

Only a bounded set of nodes is sampled (unhealthy first, else connected),
because a large deployment has too many nodes to fetch logs from all of them;
the coverage-summary observation makes the sampling explicit.
"""

import asyncio

from logger import logger
from models.deployment_models import DeploymentDiagnostics, DeploymentNodeSummary
from services.log_service import log_service
from services.system_stats_parser import SystemStatsParser

_CONNECTED = "Connected"
_STATS_LOG_NAME = "iseLocalStore"
_MAX_STATS_NODES = 3


class DeploymentDiagnosticsResolver:
    def __init__(self) -> None:
        self._parser = SystemStatsParser()

    def _select_nodes(
        self, nodes: list[DeploymentNodeSummary]
    ) -> list[DeploymentNodeSummary]:
        """Pick up to _MAX_STATS_NODES: unhealthy first, else connected."""
        unhealthy = [n for n in nodes if n.node_status != _CONNECTED]
        if unhealthy:
            return unhealthy[:_MAX_STATS_NODES]
        connected = [n for n in nodes if n.node_status == _CONNECTED]
        return connected[:_MAX_STATS_NODES]

    async def _node_stats(self, node: DeploymentNodeSummary) -> dict:
        """Fetch + parse one node's stats. Never raises; returns a status block."""
        target = node.fqdn or node.hostname
        try:
            async with log_service.fetch(_STATS_LOG_NAME, target) as path:
                parsed = self._parser.parse(path)
        except Exception as exc:  # auth / HTTP / zip / parse — isolate per node
            # Full detail (status code, URL, host) goes to the server-side log
            # for operators; the returned reason stays generic so internal
            # infrastructure details are not surfaced to the caller.
            logger.info(
                "Deep diagnostics: log unavailable for node",
                hostname=node.hostname,
                error=str(exc),
            )
            return {
                "status": "unavailable",
                "reason": "system-stats log could not be fetched; no further "
                "diagnostic information available for this node",
            }

        if not parsed:
            return {
                "status": "unavailable",
                "reason": "no ISE Utilization samples in the last hour",
            }
        return {"status": "ok", **parsed}

    async def resolve(
        self, nodes: list[DeploymentNodeSummary], scoped: bool = False
    ) -> DeploymentDiagnostics:
        """Derive diagnostics for ``nodes``.

        Args:
            nodes: The node list to diagnose.
            scoped: True when the caller filtered to specific hostnames. A
                filtered slice describes only the requested nodes, so
                deployment-wide HA claims (missing Primary/Secondary PAN) are
                omitted — mirroring ``DeploymentHealthSummary``'s
                ``scope="filtered"`` behavior. Per-node observations and
                system_stats are still produced.
        """
        observations: list[str] = []

        for node in nodes:
            if node.node_status != _CONNECTED:
                observations.append(
                    f"{node.hostname}: nodeStatus={node.node_status or 'Unknown'} "
                    "(not Connected)"
                )

        # PAN redundancy is a deployment-wide property; a filtered query cannot
        # support it (the missing PAN may simply be outside the filter).
        if not scoped:
            has_primary = any("PrimaryAdmin" in n.roles for n in nodes)
            has_secondary = any("SecondaryAdmin" in n.roles for n in nodes)
            has_standalone = any("Standalone" in n.roles for n in nodes)
            if not (has_primary or has_standalone):
                observations.append(
                    "No PrimaryAdmin (Primary PAN) node present in the deployment."
                )
            elif has_primary and not has_secondary:
                observations.append(
                    "No SecondaryAdmin (Secondary PAN) node present — no PAN redundancy."
                )

        system_stats = None
        selected = self._select_nodes(nodes)
        if selected:
            results = await asyncio.gather(
                *(self._node_stats(n) for n in selected)
            )
            node_stats = {n.hostname: r for n, r in zip(selected, results)}
            succeeded = sum(1 for r in node_stats.values() if r.get("status") == "ok")
            system_stats = {
                "anchor": "latest_log_timestamp",
                "duration_minutes": 60,
                "nodes": node_stats,
            }
            observations.append(
                f"Fetched diagnostic data from {succeeded} of {len(selected)} "
                "node(s) (unhealthy nodes prioritized). Check the health of "
                "individual nodes for more details."
            )

        return DeploymentDiagnostics(
            observations=observations, system_stats=system_stats
        )
