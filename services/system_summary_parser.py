# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Map ISE getSystemSummaryDetails dashboard data into per-node health.

Pure and testable: no I/O. Consumes the dict produced by
``utils.xml_parser.iter_parse_system_summary`` and returns a per-node summary of
process states (running / disabled / initializing / down), the list of processes
that are down (code 0 only), and min/max/avg/latest aggregates of the 60-minute
CPU / memory / latency series. Processes are keyed by their human-readable
service name (e.g. "Application Server"), not the raw camelCase bean field.

Services that resolve to ``not_monitored`` are omitted entirely rather than
surfaced. That state covers three cases that all mean "no signal": the ``-1``
nvl fallback (service not reported), any unrecognized/blank code, and the
dead-wired bean fields whose DB columns no writer ever populates (e.g.
``alertManager``, the ``xgrid*`` fields) — so they never carry a real state.

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

# Bean field (XML child tag) -> human-readable service name, per the ISE
# syslog "ISE Process Health" -> mnt_process_status -> ProcessStatus bean
# mapping. Fields not listed here fall back to the raw bean field name.
_DISPLAY_NAMES = {
    "databaseListener": "Database Listener",
    "database": "Database Server",
    "applicationServer": "Application Server",
    "sessionDatabase": "M&T Session Database",
    "logCollector": "M&T Log Collector",
    "logProcessor": "M&T Log Processor",
    "profilerDb": "Profiler Database",
    "sxpEngine": "SXP Engine Service",
    "deviceAdmin": "Device Admin Service",
    "ipepService": "IPEP Service",
    "certificateAuthority": "Certificate Authority Service",
    "identityMapping": "PassiveID WMI Service",
    "aDConnector": "AD Connector",
}


def _display_name(field: str) -> str:
    """Human-readable service name for a bean field.

    Unmapped fields fall back to the raw bean field name verbatim rather than a
    guessed humanization, so an unknown service is never given a fabricated
    display name.
    """
    return _DISPLAY_NAMES.get(field, field)

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
                if state == _NOT_MONITORED:
                    # No signal (-1 nvl fallback, unknown code, or a dead-wired
                    # bean field). Omit rather than surface a non-state.
                    continue
                name = _display_name(field)
                processes[name] = state
                if state == "down":
                    processes_down.append(name)
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
