# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from services.system_summary_parser import SystemSummaryParser


def _parsed():
    return {
        "process_statuses": [
            {
                "server": "vm218",
                "status": "Failed",
                "message": None,
                "timestamp": "2026-07-16 08:30:51.488",
                "applicationServer": "1",
                "database": "0",
                "sxpEngine": "2",
                "profilerServer": "3",
                "alertManager": "-1",
                "identityMapping": "7",
            },
        ],
        "status_60min": [
            {"server": "vm218", "timestamp": "2026-07-16 07:38:00",
             "cpuUtilization": "4", "memoryUtilization": "57", "latency": "0"},
            {"server": "vm218", "timestamp": "2026-07-16 07:43:00",
             "cpuUtilization": "3", "memoryUtilization": "57", "latency": "2"},
        ],
    }


def test_process_code_mapping():
    out = SystemSummaryParser().build(_parsed())
    procs = out["vm218"]["processes"]
    assert procs["applicationServer"] == "running"       # 1
    assert procs["database"] == "down"                   # 0
    assert procs["sxpEngine"] == "disabled"              # 2
    assert procs["profilerServer"] == "initializing"     # 3
    assert procs["alertManager"] == "not_monitored"      # -1
    # Codes above the known space (>3), like 7, fold to not_monitored.
    assert procs["identityMapping"] == "not_monitored"   # 7 -> not_monitored


def test_non_process_fields_excluded_from_processes():
    out = SystemSummaryParser().build(_parsed())
    procs = out["vm218"]["processes"]
    for skipped in ("server", "status", "message", "timestamp"):
        assert skipped not in procs


def test_processes_down_lists_only_code_zero():
    out = SystemSummaryParser().build(_parsed())
    assert out["vm218"]["processes_down"] == ["database"]


def test_reported_status_surfaced_verbatim():
    out = SystemSummaryParser().build(_parsed())
    assert out["vm218"]["reported_status"] == "Failed"


def test_metric_aggregation():
    out = SystemSummaryParser().build(_parsed())
    cpu = out["vm218"]["cpu_percent"]
    assert cpu == {"min": 3.0, "max": 4.0, "avg": 3.5, "latest": 3.0}
    lat = out["vm218"]["latency"]
    assert lat["latest"] == 2.0  # latest by timestamp order


def test_missing_series_yields_none_metrics():
    parsed = {"process_statuses": _parsed()["process_statuses"], "status_60min": []}
    out = SystemSummaryParser().build(parsed)
    assert out["vm218"]["cpu_percent"] is None
    assert out["vm218"]["memory_percent"] is None
    assert out["vm218"]["latency"] is None


def test_node_with_only_series_still_appears():
    parsed = {
        "process_statuses": [],
        "status_60min": [
            {"server": "vm9", "timestamp": "2026-07-16 07:38:00",
             "cpuUtilization": "5", "memoryUtilization": "60", "latency": "1"},
        ],
    }
    out = SystemSummaryParser().build(parsed)
    assert "vm9" in out
    assert out["vm9"]["processes"] == {}
    assert out["vm9"]["cpu_percent"]["latest"] == 5.0
