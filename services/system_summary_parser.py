# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Map ISE getSystemSummaryDetails dashboard data into per-node health.

Pure and testable: no I/O. Consumes the dict produced by
``utils.xml_parser.iter_parse_system_summary`` and returns a per-node summary of
process states (running / disabled / initializing / down / not_monitored), the
list of processes that are down (code 0 only), and min/max/avg/latest aggregates
of the 60-minute CPU / memory / latency series.

The top-level ``<status>``/``<message>`` elements are intentionally NOT surfaced:
that endpoint's JAXB field-access serialization emits a default "Failed" because
the response is built without invoking the getter that would flip it to
"Passed", so the value is a fixed artifact, not a health verdict. The real
verdict comes only from the per-service integer codes (any 0 = down).

Process-status code semantics (confirmed against the ``70001 System-Stats: ISE
Process Health`` log line): 0=down (the only fault), 1=running, 2=disabled,
3=initializing, -1=not_monitored (null / no data). The code space tops out at 3;
any code greater than 3 — and any unrecognized/blank value — is treated as
not_monitored (the same as -1) and is never a fault.
"""

from typing import Any, Dict, List

# Elements of <lstProcessStatuses> that are NOT process codes.
_NON_PROCESS_FIELDS = frozenset({"server", "timestamp", "status", "message"})

# Codes 0-3 and -1 are the full known space. Anything else (>3, blank, or
# malformed) folds to "not_monitored" via the _CODE_MAP.get default below.
_NOT_MONITORED = "not_monitored"
_CODE_MAP = {
    "0": "down",
    "1": "running",
    "2": "disabled",
    "3": "initializing",
    "-1": _NOT_MONITORED,
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
                state = _CODE_MAP.get(value, _NOT_MONITORED)
                processes[field] = state
                if state == "down":
                    processes_down.append(field)
            node = _blank_node()
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
