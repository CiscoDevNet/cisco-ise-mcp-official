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


def test_only_processes_down_surfaced():
    out = SystemSummaryParser().build(_parsed())
    node = out["vm218"]
    # Only down processes (code 0) are surfaced; there is no full per-process
    # state map. Every other state — running (1), disabled (2), initializing
    # (3), and not_monitored (-1 / unknown code) — is not reported.
    assert node["processes_down"] == ["Database Server"]  # only the code-0 one
    assert "processes" not in node


def test_processes_down_uses_human_readable_names():
    parsed = {
        "process_statuses": [
            {"server": "vm1", "applicationServer": "0", "sxpEngine": "0",
             "identityMapping": "0"},
        ],
        "status_60min": [],
    }
    out = SystemSummaryParser().build(parsed)
    assert out["vm1"]["processes_down"] == [
        "Application Server", "SXP Engine Service", "PassiveID WMI Service",
    ]


def test_down_process_unmapped_field_falls_back_to_raw_name():
    parsed = {
        "process_statuses": [{"server": "vm1", "someNewService": "0"}],
        "status_60min": [],
    }
    out = SystemSummaryParser().build(parsed)
    # An unmapped bean field falls back to the raw name verbatim.
    assert out["vm1"]["processes_down"] == ["someNewService"]


def test_non_process_fields_never_reported_as_down():
    parsed = {
        "process_statuses": [
            {"server": "vm1", "status": "Failed", "message": None,
             "timestamp": "2026-07-16 08:30:51.488", "applicationServer": "1"},
        ],
        "status_60min": [],
    }
    out = SystemSummaryParser().build(parsed)
    assert out["vm1"]["processes_down"] == []


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
    assert out["vm9"]["processes_down"] == []
    assert out["vm9"]["cpu_percent"]["latest"] == 5.0
