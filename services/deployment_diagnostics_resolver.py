# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Derive deployment diagnostics from the node list and the MnT dashboard API.

Produces human-readable observations derived from node status and roles, plus
per-node system statistics (process health and CPU/memory/latency) fetched in a
single call to the MnT ``getSystemSummaryDetails`` endpoint. The call covers all
nodes at once; results are filtered to the hostnames in the caller's node list.

The response is read with a streaming, memory-bounded parse (the AuthList
pattern: ``get_stream`` -> spooled temp file -> ``iterparse`` off the event loop)
and the fetch runs inside the shared ``mnt_gate`` so it shares MnT-node
backpressure with the session tools.

Diagnostics degrade gracefully: a gate rejection folds into an ``unavailable``
system_stats block with a distinct retry-oriented reason, and any other failure
(auth / HTTP / parse) into one generic reason. The base observations still run,
and the tool never fails because diagnostics could not be produced.
"""

import asyncio
import tempfile

from fastmcp.exceptions import ToolError as McpToolError

from logger import logger
from clients.mnt_gate import mnt_gate
from models.deployment_models import DeploymentDiagnostics, DeploymentNodeSummary
from services.system_summary_parser import SystemSummaryParser
from utils.xml_parser import iter_parse_system_summary

_CONNECTED = "Connected"
_SUMMARY_ENDPOINT = "dashboard/getSystemSummaryDetails"
_SPOOL_MAX_BYTES = 64 * 1024 * 1024

_BUSY_REASON = (
    "diagnostics skipped: the ISE MnT node is busy or under load; retry shortly"
)
_GENERIC_REASON = (
    "diagnostics unavailable; no system-summary data could be retrieved"
)


class DeploymentDiagnosticsResolver:
    def __init__(self, mnt_client, gate=None) -> None:
        self._mnt_client = mnt_client
        self._gate = gate if gate is not None else mnt_gate
        self._parser = SystemSummaryParser()

    async def _fetch_and_parse(self) -> dict:
        """Stream + parse the summary XML. Raises on gate/API/parse failure."""
        async with self._gate.guard():
            async with self._mnt_client.get_stream(_SUMMARY_ENDPOINT) as response:
                with tempfile.SpooledTemporaryFile(max_size=_SPOOL_MAX_BYTES) as buf:
                    async for chunk in response.aiter_bytes():
                        buf.write(chunk)
                    buf.seek(0)
                    # iterparse is synchronous/CPU-bound and may read a
                    # spilled-to-disk temp file; run it off the event loop.
                    return await asyncio.to_thread(iter_parse_system_summary, buf)

    async def _system_stats(
        self, nodes: list[DeploymentNodeSummary]
    ) -> tuple[dict, list[str]]:
        """Fetch + parse system summary. Never raises.

        Returns ``(system_stats, extra_observations)``. On a gate rejection the
        block carries the busy/retry reason; on any other failure the generic
        reason.
        """
        try:
            parsed = await self._fetch_and_parse()
            per_node = self._parser.build(parsed)
        except McpToolError as exc:
            # Gate rejection (ISE_BUSY) -> degrade, do NOT re-raise.
            logger.info("Deployment diagnostics gated (MnT busy)", error=str(exc))
            return ({"status": "unavailable", "reason": _BUSY_REASON}, [])
        except Exception as exc:  # auth / HTTP / parse — isolate, log full detail
            logger.info(
                "Deployment diagnostics: system summary unavailable",
                error=str(exc),
            )
            return ({"status": "unavailable", "reason": _GENERIC_REASON}, [])

        wanted = {n.hostname for n in nodes}
        scoped_nodes = {h: v for h, v in per_node.items() if h in wanted}
        if per_node and not scoped_nodes:
            # The summary returned rows but none matched the requested
            # hostnames (e.g. the summary keys by a name form the node list
            # does not use). Surface it so an all-empty nodes block is not
            # mistaken for a healthy deployment with no faults.
            logger.info(
                "Deployment diagnostics: system summary rows did not match "
                "any requested node",
                summary_row_count=len(per_node),
                requested_node_count=len(wanted),
            )

        observations: list[str] = []
        for hostname, data in scoped_nodes.items():
            down = data.get("processes_down") or []
            if down:
                observations.append(
                    f"{hostname}: process(es) not running: {', '.join(down)} "
                    "(admin-guide: Process Down)."
                )

        return (
            {
                "source": "getSystemSummaryDetails",
                "duration_minutes": 60,
                "nodes": scoped_nodes,
            },
            observations,
        )

    async def resolve(
        self, nodes: list[DeploymentNodeSummary], scoped: bool = False
    ) -> DeploymentDiagnostics:
        """Derive diagnostics for ``nodes``.

        Args:
            nodes: The node list to diagnose.
            scoped: True when the caller filtered to specific hostnames.
                Deployment-wide HA claims (missing Primary/Secondary PAN) are
                omitted for a filtered slice; per-node observations and
                system_stats are still produced.
        """
        observations: list[str] = []

        for node in nodes:
            if node.node_status != _CONNECTED:
                observations.append(
                    f"{node.hostname}: nodeStatus={node.node_status or 'Unknown'} "
                    "(not Connected)"
                )

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
        if nodes:
            system_stats, stats_observations = await self._system_stats(nodes)
            observations.extend(stats_observations)

        return DeploymentDiagnostics(
            observations=observations, system_stats=system_stats
        )
