# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import io
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from utils.xml_parser import iter_parse_system_summary

_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<dashboardResult>
  <lstProcessStatuses>
    <timestamp>2026-07-16 08:30:51.488</timestamp>
    <server>vm218</server>
    <applicationServer>1</applicationServer>
    <database>1</database>
    <alertManager>-1</alertManager>
    <sxpEngine>2</sxpEngine>
    <status>Failed</status>
    <message/>
  </lstProcessStatuses>
  <lstSystemStatus60Min>
    <server>vm218</server>
    <timestamp>2026-07-16 07:38:00</timestamp>
    <cpuUtilization>4</cpuUtilization>
    <memoryUtilization>57</memoryUtilization>
    <latency>0</latency>
  </lstSystemStatus60Min>
  <lstSystemStatus24Hr>
    <server>vm218</server>
    <timestamp>2026-07-15 08:00:00</timestamp>
    <cpuUtilization>4</cpuUtilization>
    <memoryUtilization>55</memoryUtilization>
    <latency>0</latency>
  </lstSystemStatus24Hr>
</dashboardResult>
"""


def _src():
    return io.BytesIO(_XML)


def test_parses_process_statuses_and_60min():
    result = iter_parse_system_summary(_src())
    assert len(result["process_statuses"]) == 1
    ps = result["process_statuses"][0]
    assert ps["server"] == "vm218"
    assert ps["applicationServer"] == "1"
    assert ps["sxpEngine"] == "2"
    assert ps["status"] == "Failed"
    assert len(result["status_60min"]) == 1
    row = result["status_60min"][0]
    assert row["server"] == "vm218"
    assert row["cpuUtilization"] == "4"
    assert row["latency"] == "0"


def test_ignores_24hr_series():
    result = iter_parse_system_summary(_src())
    assert "status_24hr" not in result
    # 24hr rows must not leak into the 60-min list.
    assert len(result["status_60min"]) == 1


def test_empty_element_becomes_none():
    result = iter_parse_system_summary(_src())
    assert result["process_statuses"][0]["message"] is None


def test_wrong_root_raises_value_error():
    with pytest.raises(ValueError):
        iter_parse_system_summary(io.BytesIO(b"<notDashboard></notDashboard>"))


def test_malformed_xml_raises_parse_error():
    import defusedxml.ElementTree as ET
    with pytest.raises(ET.ParseError):
        iter_parse_system_summary(io.BytesIO(b"<dashboardResult><unclosed>"))
