# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Map ISE getSystemSummaryDetails dashboard data into per-node health.

Pure and testable: no I/O. Consumes the dict produced by
``utils.xml_parser.iter_parse_system_summary`` and returns a per-node summary of
process states (running / disabled / not_applicable / down / unknown), the list
of processes that are down (code 0 only), the ISE-reported top-level status
verbatim, and min/max/avg/latest aggregates of the 60-minute
CPU / memory / latency series.

Process-status code semantics (confirmed against the ``70001 System-Stats: ISE
Process Health`` log line): 1=running, 2=disabled, -1=not_applicable, 0=down
(the only fault). Unknown codes are surfaced as ``unknown:<n>`` and are not
faults.
"""

from typing import Any, Dict, List

# Elements of <lstProcessStatuses> that are NOT process codes.
_NON_PROCESS_FIELDS = frozenset({"server", "timestamp", "status", "message"})

_CODE_MAP = {
    "1": "running",
    "2": "disabled",
    "-1": "not_applicable",
    "0": "down",
}

_METRIC_FIELDS = (
    ("cpu_percent", "cpuUtilization"),
    ("memory_percent", "memoryUtilization"),
    ("latency", "latency"),
)


def _aggregate(values: List[float]) -> Dict[str, float]:
    return {
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 2),
        "latest": values[-1],
    }


def _blank_node() -> Dict[str, Any]:
    return {
        "reported_status": None,
        "processes_down": [],
        "processes": {},
        "cpu_percent": None,
        "memory_percent": None,
        "latency": None,
    }


class SystemSummaryParser:
    def build(self, parsed: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build a per-node summary keyed by server hostname."""
        nodes: Dict[str, Dict[str, Any]] = {}

        for row in parsed.get("process_statuses", []):
            server = row.get("server")
            if not server:
                continue
            processes: Dict[str, str] = {}
            processes_down: List[str] = []
            for field, value in row.items():
                if field in _NON_PROCESS_FIELDS:
                    continue
                state = _CODE_MAP.get(value, f"unknown:{value}")
                processes[field] = state
                if state == "down":
                    processes_down.append(field)
            node = _blank_node()
            node["reported_status"] = row.get("status")
            node["processes_down"] = processes_down
            node["processes"] = processes
            nodes[server] = node

        # Aggregate the 60-min series per server (ordered by timestamp so
        # ``latest`` is the most recent sample).
        series: Dict[str, List[dict]] = {}
        for sample in parsed.get("status_60min", []):
            server = sample.get("server")
            if not server:
                continue
            series.setdefault(server, []).append(sample)

        for server, samples in series.items():
            samples.sort(key=lambda s: s.get("timestamp") or "")
            node = nodes.setdefault(server, _blank_node())
            for out_key, src_key in _METRIC_FIELDS:
                values: List[float] = []
                for s in samples:
                    raw = s.get(src_key)
                    if raw is None:
                        continue
                    try:
                        values.append(float(raw))
                    except (TypeError, ValueError):
                        continue
                if values:
                    node[out_key] = _aggregate(values)

        return nodes
