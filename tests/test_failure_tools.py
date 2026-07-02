# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Tests for AAA failure investigation: xml_parser (authStatus, failureReasons),
failure_models, failure_context_resolver, failure_tool_handler."""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


# ---------------------------------------------------------------------------
# Sample XML fixtures
# ---------------------------------------------------------------------------

SAMPLE_AUTH_STATUS_FAILING_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<authStatusOutputList>
    <authStatusList key="78:14:43:88:44:92">
        <authStatusElements>
            <passed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">false</passed>
            <failed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">true</failed>
            <user_name>testUser</user_name>
            <nas_ip_address>1.1.1.1</nas_ip_address>
            <nas_port_type>Ethernet</nas_port_type>
            <failure_reason>22040 Wrong password</failure_reason>
            <calling_station_id>78:14:43:88:44:92</calling_station_id>
            <identity_group></identity_group>
            <network_device_name>DefaultNetworkDevice</network_device_name>
            <acs_server>itwito-1</acs_server>
            <authentication_method>PAP_ASCII</authentication_method>
            <authentication_protocol>PAP_ASCII</authentication_protocol>
            <framed_ip_address>10.1.10.120</framed_ip_address>
            <acs_timestamp>2026-04-29T14:30:29.958+03:00</acs_timestamp>
            <execution_steps>11001,11017,11049,11117,15049,15008,15048,15041,15048,15013,24210,24212,22040,22057,22061,11003</execution_steps>
            <response>{RadiusPacketType=AccessReject; AuthenticationResult=Failed; }</response>
            <audit_session_id></audit_session_id>
            <nas_port_id></nas_port_id>
            <posture_status></posture_status>
            <selected_azn_profiles></selected_azn_profiles>
            <service_type></service_type>
            <message_code>5400</message_code>
            <nas_ipv6_address></nas_ipv6_address>
            <framed_ipv6_address>
                <ipv6_address></ipv6_address>
            </framed_ipv6_address>
            <id>1773668899413394</id>
            <acsview_timestamp>2026-04-29T14:30:29.958+03:00</acsview_timestamp>
            <identity_store>Internal Users</identity_store>
            <response_time>25</response_time>
            <location>All Locations</location>
            <device_type>All Device Types</device_type>
            <cts_security_group></cts_security_group>
            <user_type>User</user_type>
        </authStatusElements>
    </authStatusList>
</authStatusOutputList>"""

SAMPLE_AUTH_STATUS_PASSING_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<authStatusOutputList>
    <authStatusList key="88:14:43:88:44:92">
        <authStatusElements>
            <passed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">true</passed>
            <failed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">false</failed>
            <user_name>iseAiUser</user_name>
            <nas_ip_address>1.1.1.1</nas_ip_address>
            <calling_station_id>88:14:43:88:44:92</calling_station_id>
            <acs_server>itwito-1</acs_server>
            <acs_timestamp>2026-04-29T14:00:00.000+03:00</acs_timestamp>
            <execution_steps>11001,11002</execution_steps>
        </authStatusElements>
    </authStatusList>
</authStatusOutputList>"""

SAMPLE_AUTH_STATUS_MULTIPLE_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<authStatusOutputList>
    <authStatusList key="78:14:43:88:44:92">
        <authStatusElements>
            <passed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">false</passed>
            <failed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">true</failed>
            <user_name>testUser</user_name>
            <failure_reason>22040 Wrong password</failure_reason>
            <acs_timestamp>2026-04-29T14:30:29.958+03:00</acs_timestamp>
            <execution_steps>11001,22040</execution_steps>
        </authStatusElements>
        <authStatusElements>
            <passed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">true</passed>
            <failed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">false</failed>
            <user_name>testUser</user_name>
            <acs_timestamp>2026-04-29T14:35:00.000+03:00</acs_timestamp>
            <execution_steps>11001,11002</execution_steps>
        </authStatusElements>
        <authStatusElements>
            <passed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">false</passed>
            <failed xsi:type="xs:boolean" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">true</failed>
            <user_name>testUser</user_name>
            <failure_reason>22040 Wrong password</failure_reason>
            <acs_timestamp>2026-04-29T14:25:00.000+03:00</acs_timestamp>
            <execution_steps>11001,22040</execution_steps>
        </authStatusElements>
    </authStatusList>
</authStatusOutputList>"""

SAMPLE_SESSION_FAILING_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sessionParameters>
    <passed xsi:type="xs:string" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">0</passed>
    <failed xsi:type="xs:string" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">1</failed>
    <user_name>testUser</user_name>
    <nas_ip_address>1.1.1.1</nas_ip_address>
    <failure_reason>22040 Wrong password</failure_reason>
    <calling_station_id>78:14:43:88:44:92</calling_station_id>
    <network_device_name>DefaultNetworkDevice</network_device_name>
    <acs_server>itwito-1</acs_server>
    <authentication_method>PAP_ASCII</authentication_method>
    <authentication_protocol>PAP_ASCII</authentication_protocol>
    <framed_ip_address>10.1.10.120</framed_ip_address>
    <auth_acs_timestamp>2026-04-29T11:30:29.958+03:00</auth_acs_timestamp>
    <execution_steps>11001,11017,22040,11003</execution_steps>
    <response>{RadiusPacketType=AccessReject; AuthenticationResult=Failed; }</response>
    <identity_store>Internal Users</identity_store>
    <response_time>25</response_time>
</sessionParameters>"""

SAMPLE_SESSION_PASSING_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sessionParameters>
    <passed xsi:type="xs:string" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">1</passed>
    <failed xsi:type="xs:string" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">0</failed>
    <user_name>iseAiUser</user_name>
    <nas_ip_address>1.1.1.1</nas_ip_address>
    <calling_station_id>88:14:43:88:44:92</calling_station_id>
    <auth_acs_timestamp>2026-04-29T11:00:00.000+03:00</auth_acs_timestamp>
</sessionParameters>"""

SAMPLE_FAILURE_REASONS_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<failureReasonList>
    <failureReason id="100001">
        <code>100001 AUTHMGR-5-FAIL Authorization failed for client</code>
        <cause>This may or may not be indicating a violation</cause>
        <resolution>Please review and resolve according to your organization's policy</resolution>
    </failureReason>
    <failureReason id="22040">
        <code>22040 Wrong password</code>
        <cause>The user provided an incorrect password.</cause>
        <resolution>Verify the user credentials and try again.</resolution>
    </failureReason>
</failureReasonList>"""

SAMPLE_FAILURE_REASONS_EMPTY_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<failureReasonList/>"""


# ===========================================================================
# XML Parser tests
# ===========================================================================


class TestParseAuthStatusXml:
    """Tests for parse_auth_status_xml."""

    def test_failing_auth_parsed_correctly(self):
        from utils.xml_parser import parse_auth_status_xml

        results = parse_auth_status_xml(SAMPLE_AUTH_STATUS_FAILING_XML)
        assert len(results) == 1
        entry = results[0]
        assert entry["failed"] is True
        assert entry["passed"] is False
        assert entry["authentication_result"] == "Failed"
        assert entry["user_name"] == "testUser"
        assert entry["nas_ip_address"] == "1.1.1.1"
        assert entry["failure_reason"] == "22040 Wrong password"
        assert entry["calling_station_id"] == "78:14:43:88:44:92"
        assert entry["network_device_name"] == "DefaultNetworkDevice"
        assert entry["acs_server"] == "itwito-1"
        assert entry["authentication_method"] == "PAP_ASCII"
        assert entry["authentication_protocol"] == "PAP_ASCII"
        assert entry["framed_ip_address"] == "10.1.10.120"
        assert entry["acs_timestamp"] == "2026-04-29T14:30:29.958+03:00"
        assert entry["identity_store"] == "Internal Users"
        assert entry["response"] == "{RadiusPacketType=AccessReject; AuthenticationResult=Failed; }"

    def test_execution_steps_parsed_as_list(self):
        from utils.xml_parser import parse_auth_status_xml

        results = parse_auth_status_xml(SAMPLE_AUTH_STATUS_FAILING_XML)
        steps = results[0]["execution_steps"]
        assert isinstance(steps, list)
        assert steps[0] == "11001"
        assert "22040" in steps

    def test_passing_auth_parsed_correctly(self):
        from utils.xml_parser import parse_auth_status_xml

        results = parse_auth_status_xml(SAMPLE_AUTH_STATUS_PASSING_XML)
        assert len(results) == 1
        entry = results[0]
        assert entry["passed"] is True
        assert entry["failed"] is False
        assert entry["authentication_result"] == "Passed"
        assert entry["user_name"] == "iseAiUser"

    def test_multiple_elements_parsed(self):
        from utils.xml_parser import parse_auth_status_xml

        results = parse_auth_status_xml(SAMPLE_AUTH_STATUS_MULTIPLE_XML)
        assert len(results) == 3
        failed_entries = [e for e in results if e["failed"] is True]
        passed_entries = [e for e in results if e["passed"] is True]
        assert len(failed_entries) == 2
        assert len(passed_entries) == 1

    def test_empty_xml_returns_empty_list(self):
        from utils.xml_parser import parse_auth_status_xml

        xml = '<?xml version="1.0"?><authStatusOutputList/>'
        results = parse_auth_status_xml(xml)
        assert results == []

    def test_malformed_xml_raises_parse_error(self):
        import defusedxml.ElementTree as ET
        from utils.xml_parser import parse_auth_status_xml

        with pytest.raises(ET.ParseError):
            parse_auth_status_xml("<not-closed>")

    def test_wrong_root_raises_value_error(self):
        from utils.xml_parser import parse_auth_status_xml

        with pytest.raises(ValueError, match="authStatusOutputList"):
            parse_auth_status_xml("<activeList/>")

    def test_empty_text_elements_become_none(self):
        from utils.xml_parser import parse_auth_status_xml

        results = parse_auth_status_xml(SAMPLE_AUTH_STATUS_FAILING_XML)
        entry = results[0]
        assert entry.get("identity_group") is None
        assert entry.get("audit_session_id") is None

    def test_nested_elements_skipped(self):
        from utils.xml_parser import parse_auth_status_xml

        results = parse_auth_status_xml(SAMPLE_AUTH_STATUS_FAILING_XML)
        entry = results[0]
        assert "framed_ipv6_address" not in entry


class TestParseFailureReasonsXml:
    """Tests for parse_failure_reasons_xml."""

    def test_multiple_reasons_parsed(self):
        from utils.xml_parser import parse_failure_reasons_xml

        catalog = parse_failure_reasons_xml(SAMPLE_FAILURE_REASONS_XML)
        assert len(catalog) == 2
        assert "22040" in catalog
        assert "100001" in catalog

        entry = catalog["22040"]
        assert entry["code"] == "22040 Wrong password"
        assert entry["cause"] == "The user provided an incorrect password."
        assert entry["resolution"] == "Verify the user credentials and try again."

    def test_empty_list_returns_empty_dict(self):
        from utils.xml_parser import parse_failure_reasons_xml

        catalog = parse_failure_reasons_xml(SAMPLE_FAILURE_REASONS_EMPTY_XML)
        assert catalog == {}

    def test_wrong_root_raises_value_error(self):
        from utils.xml_parser import parse_failure_reasons_xml

        with pytest.raises(ValueError, match="failureReasonList"):
            parse_failure_reasons_xml("<authStatusOutputList/>")

    def test_malformed_xml_raises_parse_error(self):
        import defusedxml.ElementTree as ET
        from utils.xml_parser import parse_failure_reasons_xml

        with pytest.raises(ET.ParseError):
            parse_failure_reasons_xml("<unclosed")

    def test_reason_without_id_skipped(self):
        from utils.xml_parser import parse_failure_reasons_xml

        xml = """\
        <failureReasonList>
            <failureReason>
                <code>No ID</code>
            </failureReason>
            <failureReason id="123">
                <code>123 Has ID</code>
            </failureReason>
        </failureReasonList>"""
        catalog = parse_failure_reasons_xml(xml)
        assert len(catalog) == 1
        assert "123" in catalog


# ===========================================================================
# FailureContextResolver tests
# ===========================================================================


class TestFailureContextResolver:
    """Tests for FailureContextResolver."""

    def _make_resolver(self, msg_catalog=None, failure_catalog=None):
        from services.failure_context_resolver import FailureContextResolver

        if msg_catalog is None:
            msg_catalog = {
                "11001": "Received RADIUS Access-Request",
                "11017": "RADIUS created a new session",
                "22040": "Wrong password or invalid shared secret",
                "11003": "Returned RADIUS Access-Reject",
            }
        if failure_catalog is None:
            failure_catalog = {
                "22040": {
                    "code": "22040 Wrong password",
                    "cause": "The user provided an incorrect password.",
                    "resolution": "Verify the user credentials and try again.",
                },
            }
        return FailureContextResolver(msg_catalog, failure_catalog)

    def test_enrichment_with_matching_failure_code(self):
        resolver = self._make_resolver()
        raw = [{
            "user_name": "testUser",
            "calling_station_id": "78:14:43:88:44:92",
            "failure_reason": "22040 Wrong password",
            "acs_timestamp": "2026-04-29T14:30:29.958+03:00",
            "execution_steps": ["11001", "22040", "11003"],
        }]
        results = resolver.enrich_failures(raw)
        assert len(results) == 1
        detail = results[0]
        assert detail.failure_reason_code == "22040"
        assert detail.failure_reason_text == "Wrong password"
        assert detail.failure_cause == "The user provided an incorrect password."
        assert detail.failure_resolution == "Verify the user credentials and try again."
        assert detail.timestamp == "2026-04-29T14:30:29.958+03:00"

    def test_enrichment_with_unknown_failure_code(self):
        resolver = self._make_resolver()
        raw = [{
            "user_name": "testUser",
            "failure_reason": "99999 Unknown failure",
            "execution_steps": ["11001"],
        }]
        results = resolver.enrich_failures(raw)
        detail = results[0]
        assert detail.failure_reason_code == "99999"
        assert detail.failure_reason_text == "Unknown failure"
        assert detail.failure_cause is None
        assert detail.failure_resolution is None
        assert detail.failure_context_note is not None
        assert "99999" in detail.failure_context_note

    def test_execution_steps_resolved(self):
        resolver = self._make_resolver()
        raw = [{
            "failure_reason": "22040 Wrong password",
            "execution_steps": ["11001", "11017", "22040", "11003"],
        }]
        results = resolver.enrich_failures(raw)
        steps = results[0].execution_steps
        assert steps is not None
        assert len(steps) == 4
        assert steps[0].text == "Received RADIUS Access-Request"
        assert steps[1].text == "RADIUS created a new session"
        assert steps[2].text == "Wrong password or invalid shared secret"
        assert steps[3].text == "Returned RADIUS Access-Reject"

    def test_execution_steps_with_missing_codes(self):
        resolver = self._make_resolver()
        raw = [{
            "failure_reason": "22040 Wrong password",
            "execution_steps": ["11001", "99999"],
        }]
        results = resolver.enrich_failures(raw)
        steps = results[0].execution_steps
        assert steps is not None
        assert steps[0].text == "Received RADIUS Access-Request"
        assert steps[1].text is None
        assert "1 of 2" in results[0].failure_context_note

    def test_no_failure_reason_returns_none_fields(self):
        resolver = self._make_resolver()
        raw = [{"user_name": "testUser"}]
        results = resolver.enrich_failures(raw)
        detail = results[0]
        assert detail.failure_reason_code is None
        assert detail.failure_reason_text is None
        assert detail.failure_cause is None

    def test_no_execution_steps_returns_none(self):
        resolver = self._make_resolver()
        raw = [{"failure_reason": "22040 Wrong password"}]
        results = resolver.enrich_failures(raw)
        assert results[0].execution_steps is None

    def test_timestamp_fallback_to_auth_acs_timestamp(self):
        resolver = self._make_resolver()
        raw = [{"auth_acs_timestamp": "2026-04-29T11:30:29.958+03:00"}]
        results = resolver.enrich_failures(raw)
        assert results[0].timestamp == "2026-04-29T11:30:29.958+03:00"


# ===========================================================================
# FailureToolHandler tests
# ===========================================================================


class TestFailureToolHandlerValidation:
    """Validation and error-handling tests for FailureToolHandler."""

    def _make_handler(self):
        from tools.failure_tool_handler import FailureToolHandler

        mock_client = AsyncMock()
        return FailureToolHandler(mock_client)

    @pytest.mark.asyncio
    async def test_no_identifiers_raises_client_error(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure()
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "MISSING_IDENTIFIER"
        assert data["error_category"] == "client_error"

    @pytest.mark.asyncio
    async def test_invalid_mac_raises_client_error(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(mac_address="NOT-A-MAC")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MAC_ADDRESS"

    @pytest.mark.asyncio
    async def test_minutes_above_max_raises_client_error(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(mac_address="78:14:43:88:44:92", minutes=9999)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MINUTES"

    @pytest.mark.asyncio
    async def test_limit_above_max_raises_client_error(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(mac_address="78:14:43:88:44:92", limit=11)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_LIMIT"

    @pytest.mark.asyncio
    async def test_limit_at_max_accepted(self):
        """Test that limit=10 (the new MAX_LIMIT) is accepted by the handler."""
        from tools.failure_tool_handler import FailureToolHandler
        from services.failure_context_resolver import FailureContextResolver

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = SAMPLE_AUTH_STATUS_FAILING_XML
        mock_client.get = AsyncMock(return_value=resp)

        handler = FailureToolHandler(mock_client)
        handler._failure_context_resolver = FailureContextResolver(
            msg_catalog={}, failure_reasons_catalog={}
        )

        # Should not raise - limit=10 is at the cap
        result = await handler.investigate_aaa_failure(
            mac_address="78:14:43:88:44:92",
            limit=10,
        )
        assert result.total_failures_found >= 0  # Just verify it completed


class TestFailureToolHandlerMacLookup:
    """Tests for MAC-based failure investigation."""

    @pytest.mark.asyncio
    async def test_mac_finds_failure_returns_enriched(self):
        from tools.failure_tool_handler import FailureToolHandler
        from services.failure_context_resolver import FailureContextResolver

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = SAMPLE_AUTH_STATUS_FAILING_XML
        mock_client.get = AsyncMock(return_value=resp)

        handler = FailureToolHandler(mock_client)
        resolver = FailureContextResolver(
            msg_catalog={"11001": "Received RADIUS Access-Request"},
            failure_reasons_catalog={
                "22040": {
                    "code": "22040 Wrong password",
                    "cause": "The user provided an incorrect password.",
                    "resolution": "Verify the user credentials and try again.",
                },
            },
        )
        handler._failure_context_resolver = resolver

        result = await handler.investigate_aaa_failure(
            mac_address="78:14:43:88:44:92",
            minutes=480,
            limit=1,
        )
        assert result.total_failures_found == 1
        assert result.actual_failures_returned == 1
        assert result.has_more is False
        assert len(result.failures) == 1
        assert result.failures[0].failure_reason_code == "22040"
        assert result.failures[0].failure_cause == "The user provided an incorrect password."
        assert result.search_filters["source_api"] == "AuthStatus"

    @pytest.mark.asyncio
    async def test_mac_finds_failure_skips_username(self):
        from tools.failure_tool_handler import FailureToolHandler
        from services.failure_context_resolver import FailureContextResolver

        mock_client = AsyncMock()
        call_count = 0

        async def mock_get(endpoint):
            nonlocal call_count
            call_count += 1
            r = Mock()
            r.text = SAMPLE_AUTH_STATUS_FAILING_XML
            return r

        mock_client.get = mock_get
        handler = FailureToolHandler(mock_client)
        handler._failure_context_resolver = FailureContextResolver(
            msg_catalog={}, failure_reasons_catalog={}
        )

        result = await handler.investigate_aaa_failure(
            mac_address="78:14:43:88:44:92",
            username="testUser",
        )
        assert result.total_failures_found == 1
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_mac_no_failure_falls_back_to_username(self):
        from tools.failure_tool_handler import FailureToolHandler

        mock_client = AsyncMock()

        async def mock_get(endpoint):
            r = Mock()
            if "AuthStatus" in endpoint:
                r.text = SAMPLE_AUTH_STATUS_PASSING_XML
            elif "Session/UserName" in endpoint:
                r.text = SAMPLE_SESSION_FAILING_XML
            else:
                raise ValueError(f"Unexpected endpoint: {endpoint}")
            return r

        mock_client.get = mock_get
        handler = FailureToolHandler(mock_client)

        result = await handler.investigate_aaa_failure(
            mac_address="88:14:43:88:44:92",
            username="testUser",
        )
        assert result.total_failures_found == 1
        assert result.search_filters.get("source_api") == "Session"

    @pytest.mark.asyncio
    async def test_mac_no_failure_no_username_returns_empty(self):
        from tools.failure_tool_handler import FailureToolHandler

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = SAMPLE_AUTH_STATUS_PASSING_XML
        mock_client.get = AsyncMock(return_value=resp)

        handler = FailureToolHandler(mock_client)
        result = await handler.investigate_aaa_failure(mac_address="88:14:43:88:44:92")
        assert result.total_failures_found == 0
        assert result.failures == []
        assert result.has_more is False


class TestFailureToolHandlerUsernameLookup:
    """Tests for username-only failure investigation."""

    @pytest.mark.asyncio
    async def test_username_only_calls_session_api(self):
        from tools.failure_tool_handler import FailureToolHandler
        from services.failure_context_resolver import FailureContextResolver

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = SAMPLE_SESSION_FAILING_XML
        mock_client.get = AsyncMock(return_value=resp)

        handler = FailureToolHandler(mock_client)
        handler._failure_context_resolver = FailureContextResolver(
            msg_catalog={}, failure_reasons_catalog={}
        )
        result = await handler.investigate_aaa_failure(username="testUser")
        assert result.total_failures_found == 1
        assert result.search_filters.get("source_api") == "Session"
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args[0][0]
        assert "Session/UserName/testUser" in call_args

    @pytest.mark.asyncio
    async def test_username_passing_session_returns_empty(self):
        from tools.failure_tool_handler import FailureToolHandler

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = SAMPLE_SESSION_PASSING_XML
        mock_client.get = AsyncMock(return_value=resp)

        handler = FailureToolHandler(mock_client)
        result = await handler.investigate_aaa_failure(username="iseAiUser")
        assert result.total_failures_found == 0
        assert result.failures == []

    @pytest.mark.asyncio
    async def test_username_500_not_available_returns_empty(self):
        """ISE returns HTTP 500 when no session data exists for a user -- treat as empty."""
        from tools.failure_tool_handler import FailureToolHandler
        import httpx

        mock_client = AsyncMock()
        ise_error_body = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            "<mnt-rest-result><http-code>500</http-code>"
            "<internal-error-info>Error in generating XML output. "
            "Error message = Session data is not available for iseAiUser."
            "</internal-error-info></mnt-rest-result>"
        )
        response = httpx.Response(
            500,
            request=httpx.Request("GET", "http://test"),
            text=ise_error_body,
        )
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("", request=response.request, response=response)
        )
        handler = FailureToolHandler(mock_client)

        result = await handler.investigate_aaa_failure(username="iseAiUser")
        assert result.total_failures_found == 0
        assert result.failures == []
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_username_500_other_error_still_propagates(self):
        """A generic 500 from ISE (not 'not available') should still raise."""
        from tools.failure_tool_handler import FailureToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        mock_client = AsyncMock()
        response = httpx.Response(
            500,
            request=httpx.Request("GET", "http://test"),
            text="Internal Server Error",
        )
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("", request=response.request, response=response)
        )
        handler = FailureToolHandler(mock_client)

        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(username="testUser")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "ISE_API_ERROR"
        assert data["retry"] is True


class TestFailureToolHandlerErrors:
    """Tests for MNT API error handling."""

    @pytest.mark.asyncio
    async def test_ise_unreachable_returns_external_error(self):
        from tools.failure_tool_handler import FailureToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
        handler = FailureToolHandler(mock_client)

        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(mac_address="78:14:43:88:44:92")
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "external_error"
        assert data["error_code"] == "ISE_UNREACHABLE"
        assert data["retry"] is True

    @pytest.mark.asyncio
    async def test_ise_timeout_returns_external_error(self):
        from tools.failure_tool_handler import FailureToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        handler = FailureToolHandler(mock_client)

        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(username="testUser")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "ISE_UNREACHABLE"
        assert data["retry"] is True

    @pytest.mark.asyncio
    async def test_ise_500_returns_api_error(self):
        from tools.failure_tool_handler import FailureToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        mock_client = AsyncMock()
        response = httpx.Response(500, request=httpx.Request("GET", "http://test"))
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("", request=response.request, response=response)
        )
        handler = FailureToolHandler(mock_client)

        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(mac_address="78:14:43:88:44:92")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "ISE_API_ERROR"
        assert "500" in data["message"]
        assert data["retry"] is True

    @pytest.mark.asyncio
    async def test_ise_404_returns_api_error_no_retry(self):
        from tools.failure_tool_handler import FailureToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        mock_client = AsyncMock()
        response = httpx.Response(404, request=httpx.Request("GET", "http://test"))
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("", request=response.request, response=response)
        )
        handler = FailureToolHandler(mock_client)

        with pytest.raises(McpToolError) as exc_info:
            await handler.investigate_aaa_failure(username="testUser")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "ISE_API_ERROR"
        assert data["retry"] is False


class TestFailureToolHandlerHasMore:
    """Tests for pagination metadata (has_more)."""

    @pytest.mark.asyncio
    async def test_has_more_true_when_truncated(self):
        from tools.failure_tool_handler import FailureToolHandler

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = SAMPLE_AUTH_STATUS_MULTIPLE_XML
        mock_client.get = AsyncMock(return_value=resp)

        handler = FailureToolHandler(mock_client)
        result = await handler.investigate_aaa_failure(
            mac_address="78:14:43:88:44:92", limit=1,
        )
        assert result.total_failures_found == 2
        assert result.actual_failures_returned == 1
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_has_more_false_when_all_returned(self):
        from tools.failure_tool_handler import FailureToolHandler

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = SAMPLE_AUTH_STATUS_MULTIPLE_XML
        mock_client.get = AsyncMock(return_value=resp)

        handler = FailureToolHandler(mock_client)
        result = await handler.investigate_aaa_failure(
            mac_address="78:14:43:88:44:92", limit=2,
        )
        assert result.total_failures_found == 2
        assert result.actual_failures_returned == 2
        assert result.has_more is False


class TestFetchFailuresByMac:
    """Direct unit tests for FailureToolHandler._fetch_failures_by_mac.

    This private helper builds the AuthStatus endpoint, fetches
    ``min(limit * 2, 10)`` records, filters to failures only, and returns
    ``(failures[:limit], total_failed_count)``.
    """

    def _make_handler(self, xml_text):
        from tools.failure_tool_handler import FailureToolHandler

        mock_client = AsyncMock()
        resp = Mock()
        resp.text = xml_text
        mock_client.get = AsyncMock(return_value=resp)
        return FailureToolHandler(mock_client), mock_client

    @pytest.mark.asyncio
    async def test_endpoint_encodes_seconds_records_and_mac(self):
        handler, mock_client = self._make_handler(SAMPLE_AUTH_STATUS_FAILING_XML)

        await handler._fetch_failures_by_mac("78:14:43:88:44:92", minutes=10, limit=1)

        endpoint = mock_client.get.call_args[0][0]
        # minutes * 60 -> seconds; limit * 2 -> fetch_records (capped at 10)
        assert endpoint == "AuthStatus/MACAddress/78:14:43:88:44:92/600/2/All"

    @pytest.mark.asyncio
    async def test_fetch_records_is_double_the_limit(self):
        handler, mock_client = self._make_handler(SAMPLE_AUTH_STATUS_FAILING_XML)

        await handler._fetch_failures_by_mac("78:14:43:88:44:92", minutes=60, limit=3)

        endpoint = mock_client.get.call_args[0][0]
        # 3 * 2 = 6 records, 60 * 60 = 3600 seconds
        assert "/3600/6/All" in endpoint

    @pytest.mark.asyncio
    async def test_fetch_records_capped_at_ten(self):
        handler, mock_client = self._make_handler(SAMPLE_AUTH_STATUS_FAILING_XML)

        await handler._fetch_failures_by_mac("78:14:43:88:44:92", minutes=1, limit=8)

        endpoint = mock_client.get.call_args[0][0]
        # 8 * 2 = 16, capped to 10
        assert "/10/All" in endpoint

    @pytest.mark.asyncio
    async def test_mac_with_colons_is_not_percent_encoded(self):
        """Colons are declared safe in quote(), so the MAC stays human-readable."""
        handler, mock_client = self._make_handler(SAMPLE_AUTH_STATUS_FAILING_XML)

        await handler._fetch_failures_by_mac("AA:BB:CC:DD:EE:FF", minutes=1, limit=1)

        endpoint = mock_client.get.call_args[0][0]
        assert "AA:BB:CC:DD:EE:FF" in endpoint
        assert "%3A" not in endpoint

    @pytest.mark.asyncio
    async def test_returns_only_failures(self):
        handler, _ = self._make_handler(SAMPLE_AUTH_STATUS_FAILING_XML)

        failures, total = await handler._fetch_failures_by_mac(
            "78:14:43:88:44:92", minutes=60, limit=1,
        )
        assert total == 1
        assert len(failures) == 1
        assert failures[0]["failed"] is True
        assert failures[0]["user_name"] == "testUser"

    @pytest.mark.asyncio
    async def test_passing_entries_filtered_out(self):
        handler, _ = self._make_handler(SAMPLE_AUTH_STATUS_PASSING_XML)

        failures, total = await handler._fetch_failures_by_mac(
            "88:14:43:88:44:92", minutes=60, limit=1,
        )
        assert total == 0
        assert failures == []

    @pytest.mark.asyncio
    async def test_mixed_entries_total_counts_all_failures(self):
        """SAMPLE_AUTH_STATUS_MULTIPLE_XML has 2 failed + 1 passed entry."""
        handler, _ = self._make_handler(SAMPLE_AUTH_STATUS_MULTIPLE_XML)

        failures, total = await handler._fetch_failures_by_mac(
            "78:14:43:88:44:92", minutes=60, limit=3,
        )
        assert total == 2
        assert len(failures) == 2
        assert all(f["failed"] is True for f in failures)

    @pytest.mark.asyncio
    async def test_truncates_to_limit_but_total_reflects_all(self):
        """With 2 failures and limit=1, return 1 entry but report total=2."""
        handler, _ = self._make_handler(SAMPLE_AUTH_STATUS_MULTIPLE_XML)

        failures, total = await handler._fetch_failures_by_mac(
            "78:14:43:88:44:92", minutes=60, limit=1,
        )
        assert total == 2
        assert len(failures) == 1

    @pytest.mark.asyncio
    async def test_empty_xml_returns_empty(self):
        handler, _ = self._make_handler(
            '<?xml version="1.0"?><authStatusOutputList/>'
        )
        failures, total = await handler._fetch_failures_by_mac(
            "78:14:43:88:44:92", minutes=60, limit=1,
        )
        assert failures == []
        assert total == 0


class TestFailureModels:
    """Tests for failure Pydantic models."""

    def test_aaa_failure_detail_exclude_none(self):
        from models.failure_models import AaaFailureDetail

        detail = AaaFailureDetail(
            user_name="testUser",
            failure_reason_code="22040",
            failure_reason_text="Wrong password",
        )
        dumped = json.loads(detail.model_dump_json(exclude_none=True))
        assert "user_name" in dumped
        assert "failure_reason_code" in dumped
        assert "nas_ip_address" not in dumped
        assert "execution_steps" not in dumped

    def test_investigation_result_serialization(self):
        from models.failure_models import AaaFailureInvestigationResult, AaaFailureDetail

        result = AaaFailureInvestigationResult(
            search_filters={"mac_address": "78:14:43:88:44:92", "minutes": 480},
            total_failures_found=1,
            actual_failures_returned=1,
            has_more=False,
            failures=[
                AaaFailureDetail(
                    user_name="testUser",
                    failure_reason_code="22040",
                ),
            ],
        )
        dumped = json.loads(result.model_dump_json(exclude_none=True))
        assert dumped["total_failures_found"] == 1
        assert dumped["has_more"] is False
        assert len(dumped["failures"]) == 1
