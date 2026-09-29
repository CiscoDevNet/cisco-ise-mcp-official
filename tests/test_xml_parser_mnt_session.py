# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Parsers for the single-identifier MnT session endpoints and error bodies."""

import sys
from pathlib import Path

import defusedxml.ElementTree as ET
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from utils.xml_parser import (
    parse_mnt_error_body,
    parse_session_count_xml,
    parse_session_detail_as_active_session,
)


class TestParseSessionCountXml:
    def test_parses_count(self):
        assert parse_session_count_xml(
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<sessionCount><count>42</count></sessionCount>"
        ) == 42

    def test_parses_zero(self):
        assert parse_session_count_xml("<sessionCount><count>0</count></sessionCount>") == 0

    def test_tolerates_whitespace(self):
        assert parse_session_count_xml("<sessionCount><count>  7\n</count></sessionCount>") == 7

    def test_strips_namespace_from_root(self):
        assert parse_session_count_xml(
            '<sessionCount xmlns="http://www.cisco.com/ise"><count>3</count></sessionCount>'
        ) == 3

    def test_rejects_wrong_root(self):
        with pytest.raises(ValueError, match="sessionCount"):
            parse_session_count_xml("<activeList><count>1</count></activeList>")

    def test_rejects_missing_count(self):
        with pytest.raises(ValueError, match="Missing <count>"):
            parse_session_count_xml("<sessionCount/>")

    def test_rejects_blank_count(self):
        with pytest.raises(ValueError, match="Missing <count>"):
            parse_session_count_xml("<sessionCount><count>   </count></sessionCount>")

    def test_rejects_non_integer_count(self):
        with pytest.raises(ValueError):
            parse_session_count_xml("<sessionCount><count>many</count></sessionCount>")

    def test_raises_on_malformed_xml(self):
        with pytest.raises(ET.ParseError):
            parse_session_count_xml("<sessionCount><count>1")


class TestParseMntErrorBody:
    _BODY = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<mnt-rest-result>
  <http-code>500</http-code>
  <internal-error-info>Session data is not available for 4.4.4.1.</internal-error-info>
  <link/>
</mnt-rest-result>"""

    def test_extracts_internal_error_info(self):
        assert parse_mnt_error_body(self._BODY) == "Session data is not available for 4.4.4.1."

    def test_returns_none_for_other_root(self):
        assert parse_mnt_error_body("<sessionParameters><user_name>bob</user_name></sessionParameters>") is None

    def test_returns_none_when_element_absent(self):
        assert parse_mnt_error_body("<mnt-rest-result><http-code>500</http-code></mnt-rest-result>") is None

    def test_returns_none_when_element_blank(self):
        assert parse_mnt_error_body(
            "<mnt-rest-result><internal-error-info>  </internal-error-info></mnt-rest-result>"
        ) is None

    def test_never_raises_on_malformed_body(self):
        # This runs inside an `except HTTPStatusError` handler; a raise here
        # would replace the real HTTP error with a parse error.
        assert parse_mnt_error_body("<mnt-rest-result><internal") is None

    def test_never_raises_on_html_error_page(self):
        assert parse_mnt_error_body("<html><body>502 Bad Gateway</body></html>") is None

    def test_never_raises_on_empty_body(self):
        assert parse_mnt_error_body("") is None


class TestParseSessionDetailAsActiveSession:
    _BODY = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sessionParameters>
  <passed>true</passed>
  <user_name>alice</user_name>
  <calling_station_id>AA:BB:CC:00:00:14</calling_station_id>
  <nas_ip_address>10.80.60.150</nas_ip_address>
  <framed_ip_address>10.251.204.55</framed_ip_address>
  <audit_session_id>0A50963200000000C2E7E7E5</audit_session_id>
  <acct_session_id>00000001</acct_session_id>
  <nas_ipv6_address/>
  <acs_server>ise-psn-1</acs_server>
  <authentication_method>dot1x</authentication_method>
</sessionParameters>"""

    def test_projects_onto_active_session_fields(self):
        assert parse_session_detail_as_active_session(self._BODY) == {
            "user_name": "alice",
            "calling_station_id": "AA:BB:CC:00:00:14",
            "nas_ip_address": "10.80.60.150",
            "framed_ip_address": "10.251.204.55",
            "audit_session_id": "0A50963200000000C2E7E7E5",
            "acct_session_id": "00000001",
            "nas_ipv6_address": None,
            # MnT names this acs_server here but server in <activeList>.
            "server": "ise-psn-1",
        }

    def test_result_constructs_an_active_session(self):
        from models.session_models import ActiveSession

        session = ActiveSession(**parse_session_detail_as_active_session(self._BODY))
        assert session.user_name == "alice"
        assert session.server == "ise-psn-1"

    def test_absent_elements_become_none(self):
        result = parse_session_detail_as_active_session(
            "<sessionParameters><user_name>bob</user_name></sessionParameters>"
        )
        assert result["user_name"] == "bob"
        assert result["calling_station_id"] is None
        assert result["server"] is None

    def test_ignores_unmapped_elements(self):
        result = parse_session_detail_as_active_session(self._BODY)
        assert "authentication_method" not in result
        assert "passed" not in result

    def test_strips_namespaces(self):
        result = parse_session_detail_as_active_session(
            '<sessionParameters xmlns="http://www.cisco.com/ise">'
            "<user_name>carol</user_name></sessionParameters>"
        )
        assert result["user_name"] == "carol"

    def test_rejects_wrong_root(self):
        with pytest.raises(ValueError, match="sessionParameters"):
            parse_session_detail_as_active_session("<mnt-rest-result/>")

    def test_raises_on_malformed_xml(self):
        with pytest.raises(ET.ParseError):
            parse_session_detail_as_active_session("<sessionParameters><user_name>")
