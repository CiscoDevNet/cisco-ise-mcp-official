# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for session-related tools: xml_parser (sessionParameters), session_models, session_tool_handler."""

import io
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


# Sample sessionParameters XML from ISE MNT Last Session API
SAMPLE_SESSION_PARAMS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sessionParameters>
    <passed xsi:type="xs:string" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">1</passed>
    <failed xsi:type="xs:string" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">0</failed>
    <user_name>iseAiUser</user_name>
    <nas_ip_address>1.1.1.1</nas_ip_address>
    <calling_station_id>88:14:43:88:44:92</calling_station_id>
    <identity_group>Unknown</identity_group>
    <network_device_name>DefaultNetworkDevice</network_device_name>
    <acs_server>itwito-2</acs_server>
    <authentication_method>PAP_ASCII</authentication_method>
    <authentication_protocol>PAP_ASCII</authentication_protocol>
    <framed_ip_address>10.1.10.120</framed_ip_address>
    <auth_acs_timestamp>2026-02-18T15:11:57.723+02:00</auth_acs_timestamp>
    <posture_status></posture_status>
    <selected_azn_profiles>PermitAccess</selected_azn_profiles>
    <identity_store>Internal Users</identity_store>
    <response_time>621</response_time>
    <execution_steps>11001,11017,11049,11117,15049,15008,15048,15041,15048,15013,24210,24212,22037,24715,15036,24209,24211,15016,15016,22081,22080,11002</execution_steps>
    <other_attr_string>AuthenticationStatus=AuthenticationPassed:!:StepLatency=1=0;2=0;3=0;4=1;5=0;6=3;7=5;8=5;9=2;10=0;11=60;12=0;13=0;14=1;15=0;16=2;17=14;18=0;19=0;20=0;21=2;22=0:!:IdentityPolicyMatchedRule=Default:!:Protocol=Radius:!:ISEPolicySetName=Default:!:AuthorizationPolicyMatchedRule=Basic_Authenticated_Access</other_attr_string>
</sessionParameters>"""


class TestParseSessionDetailXml:
    """Tests for parse_session_detail_xml and other_attr_string parsing."""

    def test_parse_session_detail_xml_full(self):
        from utils.xml_parser import parse_session_detail_xml

        parsed = parse_session_detail_xml(SAMPLE_SESSION_PARAMS_XML)
        assert parsed["authentication_result"] == "Passed"
        assert parsed["user_name"] == "iseAiUser"
        assert parsed["nas_ip_address"] == "1.1.1.1"
        assert parsed["calling_station_id"] == "88:14:43:88:44:92"
        assert parsed["identity_group"] == "Unknown"
        assert parsed["network_device_name"] == "DefaultNetworkDevice"
        assert parsed["acs_server"] == "itwito-2"
        assert parsed["authentication_method"] == "PAP_ASCII"
        assert parsed["authentication_protocol"] == "PAP_ASCII"
        assert parsed["framed_ip_address"] == "10.1.10.120"
        assert parsed["auth_acs_timestamp"] == "2026-02-18T15:11:57.723+02:00"
        assert parsed["posture_status"] is None
        assert parsed["selected_azn_profiles"] == "PermitAccess"
        assert parsed["identity_store"] == "Internal Users"
        assert parsed["response_time"] == 621
        assert parsed["authentication_status"] == "AuthenticationPassed"
        assert parsed["identity_policy_matched_rule"] == "Default"
        assert parsed["protocol"] == "Radius"
        assert parsed["ise_policy_set_name"] == "Default"
        assert parsed["authorization_policy_matched_rule"] == "Basic_Authenticated_Access"

    def test_parse_session_detail_xml_wrong_root_raises(self):
        from utils.xml_parser import parse_session_detail_xml

        with pytest.raises(ValueError, match="sessionParameters"):
            parse_session_detail_xml("<activeList><activeSession/></activeList>")

    def test_parse_session_detail_xml_empty_posture_becomes_none(self):
        from utils.xml_parser import parse_session_detail_xml

        parsed = parse_session_detail_xml(SAMPLE_SESSION_PARAMS_XML)
        assert parsed.get("posture_status") is None

    def test_parse_session_detail_xml_other_attr_optional_keys(self):
        from utils.xml_parser import parse_session_detail_xml

        xml_minimal = """<?xml version="1.0"?>
        <sessionParameters>
            <user_name>u</user_name>
            <other_attr_string>Foo=Bar:!:AuthenticationStatus=Passed:!:Baz=Qux</other_attr_string>
        </sessionParameters>"""
        parsed = parse_session_detail_xml(xml_minimal)
        assert parsed["authentication_status"] == "Passed"
        assert "Foo" not in parsed
        assert "Baz" not in parsed


class TestSessionDetailModel:
    """Tests for SessionDetail and EnrichedSessionSearchResult Pydantic models."""

    def test_session_detail_from_parsed(self):
        from utils.xml_parser import parse_session_detail_xml
        from models.session_models import SessionDetail

        parsed = parse_session_detail_xml(SAMPLE_SESSION_PARAMS_XML)
        detail = SessionDetail(**parsed)
        assert detail.authentication_result == "Passed"
        assert detail.authorization_profiles == "PermitAccess"
        assert detail.authorization_policy_matched_rule == "Basic_Authenticated_Access"

    def test_enriched_session_search_result(self):
        from models.session_models import SessionDetail, EnrichedSessionSearchResult

        sessions = [
            SessionDetail(
                user_name="u1",
                calling_station_id="AA:BB:CC:DD:EE:01",
                nas_ip_address="1.1.1.1",
                selected_azn_profiles="PermitAccess",
            ),
        ]
        result = EnrichedSessionSearchResult(
            search_filters={"minutes": 1440},
            total_sessions_found=10,
            actual_sessions_returned=1,
            sessions=sessions,
        )
        assert result.total_sessions_found == 10
        assert result.actual_sessions_returned == 1
        assert result.sessions[0].authorization_profiles == "PermitAccess"


class TestSessionToolHandlerGetEnrichmentEndpoints:
    """Tests for _get_enrichment_endpoints."""


    def test_get_enrichment_endpoints_calling_station_id_first_then_username(self):
        from tools.session_tool_handler import SessionToolHandler
        from models.session_models import ActiveSession

        handler = SessionToolHandler(Mock())
        session = ActiveSession(
            user_name="u",
            calling_station_id="AA:BB:CC:DD:EE:FF",
            nas_ip_address="1.1.1.1",
            server="ise-1",
        )
        api_endpoints = handler._get_enrichment_endpoints(session)
        assert len(api_endpoints) == 2
        path0, desc0 = api_endpoints[0]
        path1, desc1 = api_endpoints[1]
        assert desc0 == "calling_station_id"
        assert "Session/MACAddress" in path0
        assert "AA:BB:CC:DD:EE:FF" in path0
        assert desc1 == "user_name"
        assert "Session/UserName" in path1
        assert "u" in path1

    def test_get_enrichment_endpoints_mac_only(self):
        from tools.session_tool_handler import SessionToolHandler
        from models.session_models import ActiveSession

        handler = SessionToolHandler(Mock())
        session = ActiveSession(
            user_name="u",
            calling_station_id="88:14:43:88:44:92",
            nas_ip_address="1.1.1.1",
            server="ise-1",
        )
        api_endpoints = handler._get_enrichment_endpoints(session)
        assert len(api_endpoints) >= 1
        path, desc = api_endpoints[0]
        assert desc == "calling_station_id"
        assert "Session/MACAddress" in path
        assert "88:14:43:88:44:92" in path

class TestFetchAuthListSessions:
    """Direct unit tests for SessionToolHandler._fetch_auth_list_sessions.

    This private helper validates *minutes*, builds the Session/AuthList
    endpoint (start time derived from now-minutes, end time literal 'null'),
    fetches, parses, and returns the list of ActiveSession objects.
    """

    ACTIVE_LIST_XML = """<?xml version="1.0"?>
    <activeList noOfActiveSession="2">
        <activeSession>
            <user_name>alice</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:01</calling_station_id>
            <nas_ip_address>10.0.0.1</nas_ip_address>
            <server>ise-1</server>
        </activeSession>
        <activeSession>
            <user_name>bob</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:02</calling_station_id>
            <nas_ip_address>10.0.0.2</nas_ip_address>
            <server>ise-2</server>
        </activeSession>
    </activeList>"""

    EMPTY_LIST_XML = '<?xml version="1.0"?><activeList noOfActiveSession="0"></activeList>'

    # Real ISE sessions do not always populate every field. This session is
    # missing <nas_ip_address> and <calling_station_id> entirely.
    PARTIAL_SESSION_XML = """<?xml version="1.0"?>
    <activeList noOfActiveSession="1">
        <activeSession>
            <user_name>test19</user_name>
            <framed_ip_address>10.1.2.3</framed_ip_address>
            <framed_ipv6_address/>
        </activeSession>
    </activeList>"""

    def _make_handler(self, xml_text):
        import contextlib
        from unittest.mock import AsyncMock
        from tools.session_tool_handler import SessionToolHandler

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            self._last_endpoint = endpoint
            yield FakeResponse(xml_text.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        # A pass-through gate so tests exercise the handler, not admission.
        import contextlib as _c
        class _PassGate:
            @_c.asynccontextmanager
            async def guard(self):
                yield
        return SessionToolHandler(mock_client, gate=_PassGate()), mock_client

    @pytest.mark.asyncio
    async def test_returns_parsed_sessions(self):
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert total == 2
        assert len(sessions) == 2
        assert sessions[0].user_name == "alice"
        assert sessions[1].user_name == "bob"

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty(self):
        handler, _ = self._make_handler(self.EMPTY_LIST_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert sessions == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_session_missing_optional_fields_does_not_raise(self):
        handler, _ = self._make_handler(self.PARTIAL_SESSION_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert len(sessions) == 1
        assert sessions[0].user_name == "test19"
        assert sessions[0].nas_ip_address is None
        assert sessions[0].calling_station_id is None
        assert sessions[0].framed_ip_address == "10.1.2.3"

    @pytest.mark.asyncio
    async def test_endpoint_uses_authlist_with_null_end_time(self):
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert self._last_endpoint.startswith("Session/AuthList/")
        assert self._last_endpoint.endswith("/null")

    @pytest.mark.asyncio
    async def test_invalid_minutes_raises_before_io(self):
        from fastmcp.exceptions import ToolError as McpToolError
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        with pytest.raises(McpToolError):
            await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=0)

    @pytest.mark.asyncio
    async def test_retention_cap_bounds_sample_but_not_total(self):
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=1, minutes=60)
        assert total == 2
        assert len(sessions) == 1


class TestSessionToolHandlerSearchActiveSessions:
    """Edge-case and boundary tests for search_active_sessions."""

    ACTIVE_LIST_XML = """<?xml version="1.0"?>
    <activeList noOfActiveSession="2">
        <activeSession>
            <user_name>alice</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:01</calling_station_id>
            <nas_ip_address>10.0.0.1</nas_ip_address>
            <server>ise-1</server>
            <framed_ip_address>192.168.1.10</framed_ip_address>
        </activeSession>
        <activeSession>
            <user_name>bob</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:02</calling_station_id>
            <nas_ip_address>10.0.0.2</nas_ip_address>
            <server>ise-2</server>
            <framed_ip_address>192.168.1.20</framed_ip_address>
        </activeSession>
    </activeList>"""

    def _make_handler(self):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(self.ACTIVE_LIST_XML.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        # A pass-through gate so tests exercise the handler, not admission.
        import contextlib as _c
        class _PassGate:
            @_c.asynccontextmanager
            async def guard(self):
                yield
        return SessionToolHandler(mock_client, gate=_PassGate())

    @pytest.mark.asyncio
    async def test_minutes_above_max_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(minutes=9999)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MINUTES"

    @pytest.mark.asyncio
    async def test_minutes_below_min_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(minutes=-5)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MINUTES"

    @pytest.mark.asyncio
    async def test_sub_minute_window_returns_user_ready_message(self):
        """minutes=0 is what the routing LLM floors a 'last 10 sec' request to.
        The error must be a clear, actionable message (minimum 1 minute), not a
        raw range dump, and must not call the MNT API."""
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(minutes=0)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MINUTES"
        assert "1 minute" in data["message"]

    @pytest.mark.asyncio
    async def test_limit_above_200_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(limit=999)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_LIMIT"

    @pytest.mark.asyncio
    async def test_limit_below_1_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(limit=0)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_LIMIT"

    @pytest.mark.asyncio
    async def test_no_filters_returns_all(self):
        handler = self._make_handler()
        result = await handler.search_active_sessions()
        assert result.total_matching_sessions == 2
        assert result.sample_size == 2
        assert result.sampling_note is None

    @pytest.mark.asyncio
    async def test_invalid_mac_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(calling_station_id="NOT-A-MAC")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MAC_ADDRESS"

    @pytest.mark.asyncio
    async def test_invalid_nas_ip_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(nas_ip_address="abc.def")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_IP_ADDRESS"

    @pytest.mark.asyncio
    async def test_invalid_framed_ip_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions(framed_ip_address="999.999.999.999")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_IP_ADDRESS"

    @pytest.mark.asyncio
    async def test_valid_filter_applied(self):
        handler = self._make_handler()
        result = await handler.search_active_sessions(username="alice")
        assert result.search_filters["username"] == "alice"
        assert result.total_matching_sessions == 1
        assert result.sample_sessions[0].user_name == "alice"

    @pytest.mark.asyncio
    async def test_filter_no_match_returns_empty(self):
        handler = self._make_handler()
        result = await handler.search_active_sessions(username="nobody")
        assert result.total_matching_sessions == 0
        assert result.sample_sessions == []
        assert result.sampling_note is None

    @pytest.mark.asyncio
    async def test_limit_truncates_to_sample_with_note(self):
        """When limit < total matching sessions the result is a SAMPLE; the
        sampling_note must clearly state the N-of-M counts so the SLM does not
        misread the list as the complete set."""
        handler = self._make_handler()
        result = await handler.search_active_sessions(limit=1)
        assert result.total_matching_sessions == 2
        assert result.sample_size == 1
        assert len(result.sample_sessions) == 1
        assert "sample" in result.sampling_note.lower()
        assert "1 out of 2" in result.sampling_note

    @pytest.mark.asyncio
    async def test_ise_api_timeout_returns_structured_error(self):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            raise httpx.ConnectError("connection refused")
            yield  # unreachable but required for generator

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        # A pass-through gate
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions()
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "external_error"
        assert data["error_code"] == "ISE_UNREACHABLE"
        assert data["retry"] is True

    @pytest.mark.asyncio
    async def test_ise_api_500_returns_structured_error(self):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            response = httpx.Response(500, request=httpx.Request("GET", "http://test"))
            raise httpx.HTTPStatusError("", request=response.request, response=response)
            yield  # unreachable but required for generator

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        # A pass-through gate
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        with pytest.raises(McpToolError) as exc_info:
            await handler.search_active_sessions()
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "external_error"
        assert data["error_code"] == "ISE_API_ERROR"
        assert "500" in data["message"]
        assert data["retry"] is True


class TestSessionToolHandlerSearchEnriched:
    """Tests for search_enriched_active_sessions with mocked MNT client."""

    @pytest.mark.asyncio
    async def test_search_enriched_calls_authlist_then_enriches(self):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        # API 1 response: one active session
        active_list_xml = """<?xml version="1.0"?>
        <activeList noOfActiveSession="1">
            <activeSession>
                <user_name>iseAiUser</user_name>
                <calling_station_id>88:14:43:88:44:92</calling_station_id>
                <nas_ip_address>1.1.1.1</nas_ip_address>
                <server>itwito-2</server>
                <framed_ip_address>10.1.10.120</framed_ip_address>
                <audit_session_id>0A50963200000000C2E7E7E5</audit_session_id>
            </activeSession>
        </activeList>"""

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(active_list_xml.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream
        call_count = 0

        async def mock_get(endpoint):
            nonlocal call_count
            call_count += 1
            if "SessionID" in endpoint or "MACAddress" in endpoint:
                r = Mock()
                r.text = SAMPLE_SESSION_PARAMS_XML
                return r
            raise ValueError(f"Unexpected endpoint: {endpoint}")

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        result = await handler.search_enriched_active_sessions(minutes=1440, limit=2)
        assert result.total_sessions_found == 1
        assert result.actual_sessions_returned == 1
        assert len(result.sessions) == 1
        assert result.sessions[0].user_name == "iseAiUser"
        assert result.sessions[0].authorization_profiles == "PermitAccess"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_search_enriched_limit_above_10_rejected(self):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler
        from fastmcp.exceptions import ToolError as McpToolError

        # A pass-through gate
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(AsyncMock(), gate=_PassGate())
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions(minutes=1440, limit=11)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_LIMIT"

    ACTIVE_LIST_2_XML = """<?xml version="1.0"?>
    <activeList noOfActiveSession="2">
        <activeSession>
            <user_name>alice</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:01</calling_station_id>
            <nas_ip_address>10.0.0.1</nas_ip_address>
            <server>ise-1</server>
            <framed_ip_address>192.168.1.10</framed_ip_address>
        </activeSession>
        <activeSession>
            <user_name>bob</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:02</calling_station_id>
            <nas_ip_address>10.0.0.2</nas_ip_address>
            <server>ise-2</server>
            <framed_ip_address>192.168.1.20</framed_ip_address>
        </activeSession>
    </activeList>"""

    def _make_enriched_handler(self):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(self.ACTIVE_LIST_2_XML.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            r = Mock()
            r.text = SAMPLE_SESSION_PARAMS_XML
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        return SessionToolHandler(mock_client, gate=_PassGate())

    @pytest.mark.asyncio
    async def test_enriched_minutes_above_max_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_enriched_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions(minutes=9999)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MINUTES"

    @pytest.mark.asyncio
    async def test_enriched_minutes_below_min_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_enriched_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions(minutes=-1)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MINUTES"

    @pytest.mark.asyncio
    async def test_enriched_invalid_mac_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_enriched_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions(calling_station_id="BADMAC")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MAC_ADDRESS"

    @pytest.mark.asyncio
    async def test_enriched_api_timeout_returns_structured_error(self):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler
        from fastmcp.exceptions import ToolError as McpToolError
        import httpx

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            raise httpx.ConnectError("refused")
            yield  # unreachable but required for generator

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        # A pass-through gate
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions()
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "external_error"
        assert data["error_code"] == "ISE_UNREACHABLE"
        assert data["retry"] is True

    @pytest.mark.asyncio
    async def test_enriched_partial_enrichment_failure(self):
        """If enrichment fails for one session (all fallbacks), it is omitted."""
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(self.ACTIVE_LIST_2_XML.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            if "AA:BB:CC:DD:EE:01" in endpoint or "alice" in endpoint:
                raise ConnectionError("enrichment failed")
            r = Mock()
            r.text = SAMPLE_SESSION_PARAMS_XML
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        result = await handler.search_enriched_active_sessions(limit=2)
        assert result.total_sessions_found == 2
        assert result.actual_sessions_returned == 1


class TestEnrichedLatencyFiltering:
    """Tests for latency range validation, post-enrichment filtering, and ENRICHMENT_CAP."""

    @staticmethod
    def _session_detail_xml(response_time: int) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            "<sessionParameters>"
            "<user_name>u</user_name>"
            "<nas_ip_address>1.1.1.1</nas_ip_address>"
            "<calling_station_id>AA:BB:CC:DD:EE:FF</calling_station_id>"
            f"<response_time>{response_time}</response_time>"
            "</sessionParameters>"
        )

    @staticmethod
    def _session_detail_xml_no_response_time() -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            "<sessionParameters>"
            "<user_name>u</user_name>"
            "<nas_ip_address>1.1.1.1</nas_ip_address>"
            "<calling_station_id>AA:BB:CC:DD:EE:FF</calling_station_id>"
            "</sessionParameters>"
        )

    @staticmethod
    def _active_list_xml(n: int) -> str:
        sessions = ""
        for i in range(n):
            mac = f"AA:BB:CC:DD:{i // 256:02X}:{i % 256:02X}"
            sessions += (
                "<activeSession>"
                f"<user_name>user{i}</user_name>"
                f"<calling_station_id>{mac}</calling_station_id>"
                "<nas_ip_address>10.0.0.1</nas_ip_address>"
                "<server>ise-1</server>"
                "</activeSession>"
            )
        return (
            '<?xml version="1.0"?>'
            f'<activeList noOfActiveSession="{n}">'
            f"{sessions}"
            "</activeList>"
        )

    def _make_handler(self, n_sessions, response_time=100):
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        active_xml = self._active_list_xml(n_sessions)
        detail_xml = self._session_detail_xml(response_time)

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(active_xml.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            r = Mock()
            r.text = detail_xml
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        return SessionToolHandler(mock_client, gate=_PassGate())

    # ---- (1) Latency range validation errors ----

    @pytest.mark.asyncio
    async def test_negative_min_latency_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler(1)
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions(min_latency_ms=-1)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MIN_LATENCY"

    @pytest.mark.asyncio
    async def test_negative_max_latency_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler(1)
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions(max_latency_ms=-5)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MAX_LATENCY"

    @pytest.mark.asyncio
    async def test_min_greater_than_max_rejected(self):
        from fastmcp.exceptions import ToolError as McpToolError

        handler = self._make_handler(1)
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_enriched_active_sessions(
                min_latency_ms=500, max_latency_ms=100,
            )
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_LATENCY_RANGE"

    @pytest.mark.asyncio
    async def test_zero_latency_bounds_accepted(self):
        handler = self._make_handler(1, response_time=0)
        result = await handler.search_enriched_active_sessions(
            min_latency_ms=0, max_latency_ms=0,
        )
        assert result.actual_sessions_returned == 1

    # ---- (2) Sessions included/excluded based on response_time_ms ----

    @pytest.mark.asyncio
    async def test_min_latency_excludes_fast_sessions(self):
        handler = self._make_handler(1, response_time=50)
        result = await handler.search_enriched_active_sessions(min_latency_ms=100)
        assert result.actual_sessions_returned == 0

    @pytest.mark.asyncio
    async def test_min_latency_includes_slow_sessions(self):
        handler = self._make_handler(1, response_time=200)
        result = await handler.search_enriched_active_sessions(min_latency_ms=100)
        assert result.actual_sessions_returned == 1

    @pytest.mark.asyncio
    async def test_max_latency_excludes_slow_sessions(self):
        handler = self._make_handler(1, response_time=500)
        result = await handler.search_enriched_active_sessions(max_latency_ms=200)
        assert result.actual_sessions_returned == 0

    @pytest.mark.asyncio
    async def test_max_latency_includes_fast_sessions(self):
        handler = self._make_handler(1, response_time=50)
        result = await handler.search_enriched_active_sessions(max_latency_ms=200)
        assert result.actual_sessions_returned == 1

    @pytest.mark.asyncio
    async def test_both_bounds_include_matching_session(self):
        handler = self._make_handler(1, response_time=150)
        result = await handler.search_enriched_active_sessions(
            min_latency_ms=100, max_latency_ms=200,
        )
        assert result.actual_sessions_returned == 1

    @pytest.mark.asyncio
    async def test_both_bounds_exclude_out_of_range_session(self):
        handler = self._make_handler(1, response_time=300)
        result = await handler.search_enriched_active_sessions(
            min_latency_ms=100, max_latency_ms=200,
        )
        assert result.actual_sessions_returned == 0

    @pytest.mark.asyncio
    async def test_none_response_time_excluded_when_latency_filter_active(self):
        """Sessions with response_time_ms=None are dropped when any latency filter is set."""
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        active_xml = self._active_list_xml(1)
        detail_xml = self._session_detail_xml_no_response_time()

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(active_xml.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            r = Mock()
            r.text = detail_xml
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        result = await handler.search_enriched_active_sessions(min_latency_ms=0)
        assert result.actual_sessions_returned == 0

    @pytest.mark.asyncio
    async def test_latency_filters_appear_in_search_filters(self):
        handler = self._make_handler(1, response_time=100)
        result = await handler.search_enriched_active_sessions(
            min_latency_ms=50, max_latency_ms=200,
        )
        assert result.search_filters["min_latency_ms"] == 50
        assert result.search_filters["max_latency_ms"] == 200

    @pytest.mark.asyncio
    async def test_total_sessions_found_reflects_post_filter_count(self):
        """With latency filters, total_sessions_found should equal the post-filter count."""
        handler = self._make_handler(2, response_time=50)
        result = await handler.search_enriched_active_sessions(min_latency_ms=100)
        assert result.total_sessions_found == 0

    # ---- (3) ENRICHMENT_CAP behavior ----

    @pytest.mark.asyncio
    async def test_without_latency_filter_enriches_only_limit(self):
        """Without latency filters, only ``limit`` sessions are enriched."""
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        active_xml = self._active_list_xml(10)
        enrich_call_count = 0
        detail_xml = self._session_detail_xml(100)

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(active_xml.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            nonlocal enrich_call_count
            enrich_call_count += 1
            r = Mock()
            r.text = detail_xml
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        result = await handler.search_enriched_active_sessions(limit=2)
        assert result.actual_sessions_returned == 2
        assert enrich_call_count == 2

    @pytest.mark.asyncio
    async def test_with_latency_filter_enriches_up_to_cap(self):
        """With a latency filter, up to ENRICHMENT_CAP sessions are enriched, not just ``limit``."""
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        n_sessions = 120
        active_xml = self._active_list_xml(n_sessions)
        enrich_call_count = 0
        detail_xml = self._session_detail_xml(100)

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(active_xml.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            nonlocal enrich_call_count
            enrich_call_count += 1
            r = Mock()
            r.text = detail_xml
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        result = await handler.search_enriched_active_sessions(
            limit=2, min_latency_ms=0,
        )
        assert enrich_call_count == SessionToolHandler.ENRICHMENT_CAP
        assert result.actual_sessions_returned == 2

    @pytest.mark.asyncio
    async def test_cap_not_exceeded_when_fewer_candidates(self):
        """When candidate sessions < ENRICHMENT_CAP, all candidates are enriched."""
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        n_sessions = 5
        active_xml = self._active_list_xml(n_sessions)
        enrich_call_count = 0
        detail_xml = self._session_detail_xml(100)

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(active_xml.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            nonlocal enrich_call_count
            enrich_call_count += 1
            r = Mock()
            r.text = detail_xml
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        result = await handler.search_enriched_active_sessions(
            limit=2, min_latency_ms=0,
        )
        assert enrich_call_count == n_sessions
        assert result.actual_sessions_returned == 2

    @pytest.mark.asyncio
    async def test_cap_filters_then_truncates_to_limit(self):
        """After enriching ENRICHMENT_CAP sessions and filtering, result is truncated to limit."""
        import contextlib
        from tools.session_tool_handler import SessionToolHandler

        n_sessions = 120
        active_xml = self._active_list_xml(n_sessions)
        detail_xml = self._session_detail_xml(500)

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            yield FakeResponse(active_xml.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        async def mock_get(endpoint):
            r = Mock()
            r.text = detail_xml
            return r

        mock_client.get = mock_get

        # A pass-through gate so tests exercise the handler, not admission.
        class _PassGate:
            @contextlib.asynccontextmanager
            async def guard(self):
                yield
        handler = SessionToolHandler(mock_client, gate=_PassGate())

        result = await handler.search_enriched_active_sessions(
            limit=2, min_latency_ms=100, max_latency_ms=1000,
        )
        assert result.actual_sessions_returned == 2
        assert result.total_sessions_found == SessionToolHandler.ENRICHMENT_CAP


class TestParseSessionDetailXmlExecutionSteps:
    """Tests for execution_steps extraction in parse_session_detail_xml."""

    def test_execution_steps_present_in_parsed_output(self):
        from utils.xml_parser import parse_session_detail_xml

        parsed = parse_session_detail_xml(SAMPLE_SESSION_PARAMS_XML)
        assert "execution_steps" in parsed
        assert parsed["execution_steps"] == [
            "11001", "11017", "11049", "11117", "15049", "15008", "15048", "15041",
            "15048", "15013", "24210", "24212", "22037", "24715", "15036", "24209",
            "24211", "15016", "15016", "22081", "22080", "11002",
        ]

    def test_execution_steps_missing_returns_none(self):
        from utils.xml_parser import parse_session_detail_xml

        xml_no_steps = """<?xml version="1.0"?>
        <sessionParameters>
            <user_name>u</user_name>
        </sessionParameters>"""
        parsed = parse_session_detail_xml(xml_no_steps)
        assert parsed.get("execution_steps") is None

    def test_session_detail_model_excludes_execution_steps_from_json(self):
        from utils.xml_parser import parse_session_detail_xml
        from models.session_models import SessionDetail

        parsed = parse_session_detail_xml(SAMPLE_SESSION_PARAMS_XML)
        detail = SessionDetail(**parsed)
        assert detail.execution_steps is not None
        dumped = detail.model_dump()
        assert "execution_steps" not in dumped

    def test_steps_latencies_parsed_with_step_index(self):
        from utils.xml_parser import parse_session_detail_xml

        parsed = parse_session_detail_xml(SAMPLE_SESSION_PARAMS_XML)
        assert "steps_latencies" in parsed
        latencies = parsed["steps_latencies"]
        assert len(latencies) == 22
        assert latencies[0] == {"step_index": 1, "latency_ms": 0}
        assert latencies[3] == {"step_index": 4, "latency_ms": 1}
        assert latencies[10] == {"step_index": 11, "latency_ms": 60}
        assert latencies[16] == {"step_index": 17, "latency_ms": 14}
        assert latencies[21] == {"step_index": 22, "latency_ms": 0}

    def test_steps_latencies_missing_returns_none(self):
        from utils.xml_parser import parse_session_detail_xml

        xml_no_latency = """<?xml version="1.0"?>
        <sessionParameters>
            <user_name>u</user_name>
            <execution_steps>11001,11002</execution_steps>
            <other_attr_string>AuthenticationStatus=Passed</other_attr_string>
        </sessionParameters>"""
        parsed = parse_session_detail_xml(xml_no_latency)
        assert parsed.get("steps_latencies") is None

    def test_steps_latencies_malformed_returns_none(self):
        from utils.xml_parser import parse_session_detail_xml

        xml_bad = """<?xml version="1.0"?>
        <sessionParameters>
            <user_name>u</user_name>
            <other_attr_string>StepLatency=not;valid;data</other_attr_string>
        </sessionParameters>"""
        parsed = parse_session_detail_xml(xml_bad)
        assert parsed.get("steps_latencies") is None

    def test_session_detail_model_excludes_steps_latencies_from_dump(self):
        from utils.xml_parser import parse_session_detail_xml
        from models.session_models import SessionDetail

        parsed = parse_session_detail_xml(SAMPLE_SESSION_PARAMS_XML)
        detail = SessionDetail(**parsed)
        assert detail.steps_latencies is not None
        dumped = detail.model_dump()
        assert "steps_latencies" not in dumped


class TestParseMsgCatalog:
    """Tests for parse_msg_catalog."""

    def test_parses_valid_catalog(self, tmp_path):
        from utils.xml_parser import parse_msg_catalog

        xml_content = """<?xml version="1.0"?>
        <messageCatalog>
            <scopes><scope><messages>
                <message code="11001">
                    <text lang="en" country="US">Received RADIUS Access-Request</text>
                </message>
                <message code="11002">
                    <text lang="en" country="US">Returned RADIUS Access-Accept</text>
                </message>
            </messages></scope></scopes>
        </messageCatalog>"""
        catalog_file = tmp_path / "test_catalog.xml"
        catalog_file.write_text(xml_content)

        catalog = parse_msg_catalog(str(catalog_file))
        assert catalog == {
            "11001": "Received RADIUS Access-Request",
            "11002": "Returned RADIUS Access-Accept",
        }

    def test_missing_file_returns_empty_dict(self, tmp_path):
        from utils.xml_parser import parse_msg_catalog

        catalog = parse_msg_catalog(str(tmp_path / "nonexistent.xml"))
        assert catalog == {}

    def test_malformed_xml_returns_empty_dict(self, tmp_path):
        from utils.xml_parser import parse_msg_catalog

        bad_file = tmp_path / "bad.xml"
        bad_file.write_text("<not-closed>")

        catalog = parse_msg_catalog(str(bad_file))
        assert catalog == {}

    def test_message_without_text_skipped(self, tmp_path):
        from utils.xml_parser import parse_msg_catalog

        xml_content = """<?xml version="1.0"?>
        <messageCatalog>
            <scopes><scope><messages>
                <message code="99999">
                    <label>NO_TEXT_ELEMENT</label>
                </message>
                <message code="11001">
                    <text lang="en" country="US">Valid message</text>
                </message>
            </messages></scope></scopes>
        </messageCatalog>"""
        catalog_file = tmp_path / "partial.xml"
        catalog_file.write_text(xml_content)

        catalog = parse_msg_catalog(str(catalog_file))
        assert "99999" not in catalog
        assert catalog["11001"] == "Valid message"

    def test_message_without_code_skipped(self, tmp_path):
        from utils.xml_parser import parse_msg_catalog

        xml_content = """<?xml version="1.0"?>
        <messageCatalog>
            <scopes><scope><messages>
                <message>
                    <text lang="en" country="US">No code attr</text>
                </message>
                <message code="11001">
                    <text lang="en" country="US">Has code</text>
                </message>
            </messages></scope></scopes>
        </messageCatalog>"""
        catalog_file = tmp_path / "no_code.xml"
        catalog_file.write_text(xml_content)

        catalog = parse_msg_catalog(str(catalog_file))
        assert len(catalog) == 1
        assert catalog["11001"] == "Has code"


class TestLatencyContextResolver:
    """Tests for LatencyContextResolver."""

    def _make_resolver(self, catalog=None):
        from services.latency_context_resolver import LatencyContextResolver

        if catalog is None:
            catalog = {
                "11001": "Received RADIUS Access-Request",
                "11002": "Returned RADIUS Access-Accept",
                "11017": "RADIUS created a new session",
            }
        return LatencyContextResolver(catalog)

    def _make_enriched_result(self, execution_steps=None, steps_latencies=None):
        from models.session_models import SessionDetail, EnrichedSessionSearchResult

        session = SessionDetail(
            user_name="testuser",
            calling_station_id="AA:BB:CC:DD:EE:FF",
            nas_ip_address="1.1.1.1",
            execution_steps=execution_steps,
            steps_latencies=steps_latencies,
        )
        return EnrichedSessionSearchResult(
            search_filters={"minutes": 1440},
            total_sessions_found=1,
            actual_sessions_returned=1,
            sessions=[session],
        )

    def test_resolves_known_codes(self):
        resolver = self._make_resolver()
        enriched = self._make_enriched_result(["11001", "11017", "11002"])
        result = resolver.enrich_sessions_with_latency_context(enriched)

        assert result.actual_sessions_returned == 1
        steps = result.sessions[0].execution_steps
        assert steps is not None
        assert len(steps) == 3
        assert steps[0].code == "11001"
        assert steps[0].text == "Received RADIUS Access-Request"
        assert steps[1].code == "11017"
        assert steps[1].text == "RADIUS created a new session"
        assert steps[2].code == "11002"
        assert steps[2].text == "Returned RADIUS Access-Accept"
        assert result.sessions[0].latency_context_note is None

    def test_unknown_codes_have_none_text(self):
        resolver = self._make_resolver()
        enriched = self._make_enriched_result(["11001", "99999"])
        result = resolver.enrich_sessions_with_latency_context(enriched)

        steps = result.sessions[0].execution_steps
        assert steps is not None
        assert len(steps) == 2
        assert steps[0].text == "Received RADIUS Access-Request"
        assert steps[1].code == "99999"
        assert steps[1].text is None
        assert result.sessions[0].latency_context_note is not None
        assert "1 of 2" in result.sessions[0].latency_context_note

    def test_empty_execution_steps_returns_none(self):
        resolver = self._make_resolver()
        enriched = self._make_enriched_result(None)
        result = resolver.enrich_sessions_with_latency_context(enriched)

        assert result.sessions[0].execution_steps is None
        assert result.sessions[0].latency_context_note is not None
        assert "No execution steps" in result.sessions[0].latency_context_note

    def test_blank_execution_steps_returns_none(self):
        resolver = self._make_resolver()
        enriched = self._make_enriched_result([])
        result = resolver.enrich_sessions_with_latency_context(enriched)

        assert result.sessions[0].execution_steps is None

    def test_empty_catalog_all_codes_unresolved(self):
        resolver = self._make_resolver(catalog={})
        enriched = self._make_enriched_result(["11001", "11002"])
        result = resolver.enrich_sessions_with_latency_context(enriched)

        steps = result.sessions[0].execution_steps
        assert steps is not None
        assert all(s.text is None for s in steps)
        assert "2 of 2" in result.sessions[0].latency_context_note

    def test_preserves_search_metadata(self):
        resolver = self._make_resolver()
        enriched = self._make_enriched_result(["11001"])
        result = resolver.enrich_sessions_with_latency_context(enriched)

        assert result.search_filters == {"minutes": 1440}
        assert result.total_sessions_found == 1

    def test_latency_ms_attached_to_steps(self):
        from models.session_models import StepLatency

        resolver = self._make_resolver()
        latencies = [
            StepLatency(step_index=0, latency_ms=5),
            StepLatency(step_index=1, latency_ms=10),
            StepLatency(step_index=2, latency_ms=2),
        ]
        enriched = self._make_enriched_result(["11001", "11017", "11002"], steps_latencies=latencies)
        result = resolver.enrich_sessions_with_latency_context(enriched)

        steps = result.sessions[0].execution_steps
        assert steps is not None
        assert steps[0].latency_ms == 5
        assert steps[1].latency_ms == 10
        assert steps[2].latency_ms == 2

    def test_latency_ms_none_when_steps_latencies_missing(self):
        resolver = self._make_resolver()
        enriched = self._make_enriched_result(["11001", "11002"], steps_latencies=None)
        result = resolver.enrich_sessions_with_latency_context(enriched)

        steps = result.sessions[0].execution_steps
        assert steps is not None
        assert all(s.latency_ms is None for s in steps)

    def test_first_step_has_no_latency_when_indices_start_at_1(self):
        """ISE StepLatency indices start at 1, so execution_steps[0] has no latency."""
        from models.session_models import StepLatency

        resolver = self._make_resolver()
        latencies = [
            StepLatency(step_index=1, latency_ms=0),
            StepLatency(step_index=2, latency_ms=3),
            StepLatency(step_index=3, latency_ms=7),
        ]
        enriched = self._make_enriched_result(
            ["11001", "11017", "11002", "11001"], steps_latencies=latencies,
        )
        result = resolver.enrich_sessions_with_latency_context(enriched)

        steps = result.sessions[0].execution_steps
        assert steps is not None
        assert len(steps) == 4
        assert steps[0].latency_ms is None
        assert steps[1].latency_ms == 0
        assert steps[2].latency_ms == 3
        assert steps[3].latency_ms == 7

    def test_latency_ms_none_for_extra_steps_beyond_latencies(self):
        from models.session_models import StepLatency

        resolver = self._make_resolver()
        latencies = [StepLatency(step_index=1, latency_ms=5)]
        enriched = self._make_enriched_result(["11001", "11017", "11002"], steps_latencies=latencies)
        result = resolver.enrich_sessions_with_latency_context(enriched)

        steps = result.sessions[0].execution_steps
        assert steps is not None
        assert steps[0].latency_ms is None
        assert steps[1].latency_ms == 5
        assert steps[2].latency_ms is None


def test_enriched_limit_allows_up_to_10():
    # New LLM-era cap: 10 is valid.
    from utils.input_validators import validate_limit

    assert validate_limit(10, max_limit=10) == 10


def test_enriched_limit_rejects_above_10():
    import pytest
    from utils.input_validators import validate_limit
    from fastmcp.exceptions import ToolError as McpToolError

    with pytest.raises(McpToolError):
        validate_limit(11, max_limit=10)


class TestIterFilterActiveSessions:
    """Streaming, memory-bounded AuthList parse + filter."""

    XML = """<?xml version="1.0"?>
    <activeList noOfActiveSession="3">
        <activeSession>
            <user_name>alice</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:01</calling_station_id>
            <nas_ip_address>10.0.0.1</nas_ip_address>
            <server>ise-1</server>
        </activeSession>
        <activeSession>
            <user_name>bob</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:02</calling_station_id>
            <nas_ip_address>10.0.0.1</nas_ip_address>
            <server>ise-2</server>
        </activeSession>
        <activeSession>
            <user_name>alice</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:03</calling_station_id>
            <nas_ip_address>10.0.0.2</nas_ip_address>
            <server>ise-1</server>
        </activeSession>
    </activeList>"""

    def _src(self):
        return io.BytesIO(self.XML.encode("utf-8"))

    def test_no_filter_retains_up_to_cap_and_counts_all(self):
        from utils.xml_parser import iter_filter_active_sessions

        retained, total = iter_filter_active_sessions(self._src(), lambda s: True, retention_cap=2)
        assert total == 3
        assert len(retained) == 2
        assert retained[0]["user_name"] == "alice"

    def test_predicate_filters_and_counts_matches(self):
        from utils.xml_parser import iter_filter_active_sessions

        pred = lambda s: s.get("user_name") == "alice"
        retained, total = iter_filter_active_sessions(self._src(), pred, retention_cap=10)
        assert total == 2
        assert len(retained) == 2
        assert all(s["user_name"] == "alice" for s in retained)

    def test_cap_zero_counts_but_retains_nothing(self):
        from utils.xml_parser import iter_filter_active_sessions

        retained, total = iter_filter_active_sessions(self._src(), lambda s: True, retention_cap=0)
        assert total == 3
        assert retained == []

    def test_empty_list(self):
        from utils.xml_parser import iter_filter_active_sessions

        src = io.BytesIO(b'<?xml version="1.0"?><activeList noOfActiveSession="0"></activeList>')
        retained, total = iter_filter_active_sessions(src, lambda s: True, retention_cap=5)
        assert total == 0
        assert retained == []

    def test_empty_child_text_becomes_none(self):
        from utils.xml_parser import iter_filter_active_sessions

        src = io.BytesIO(
            b'<?xml version="1.0"?><activeList noOfActiveSession="1">'
            b"<activeSession><user_name>x</user_name><framed_ipv6_address/></activeSession>"
            b"</activeList>"
        )
        retained, total = iter_filter_active_sessions(src, lambda s: True, retention_cap=5)
        assert total == 1
        assert retained[0]["user_name"] == "x"
        assert retained[0]["framed_ipv6_address"] is None


class TestBuildSessionPredicate:
    """Parity between the streaming predicate and legacy _filter_sessions."""

    def _handler(self):
        from unittest.mock import AsyncMock
        from tools.session_tool_handler import SessionToolHandler
        return SessionToolHandler(AsyncMock())

    def test_no_filters_matches_all(self):
        pred = self._handler()._build_session_predicate(None, None, None, None, None)
        assert pred({"user_name": "anyone"}) is True

    def test_username_exact_match(self):
        pred = self._handler()._build_session_predicate("alice", None, None, None, None)
        assert pred({"user_name": "alice"}) is True
        assert pred({"user_name": "alicia"}) is False
        assert pred({"user_name": None}) is False

    def test_mac_normalized_match(self):
        # Predicate receives an already-normalized filter value; session MAC
        # comes raw from XML and must be normalized before comparison.
        pred = self._handler()._build_session_predicate(None, "AA:BB:CC:DD:EE:01", None, None, None)
        assert pred({"calling_station_id": "aa-bb-cc-dd-ee-01"}) is True
        assert pred({"calling_station_id": "AA:BB:CC:DD:EE:99"}) is False

    def test_multiple_filters_are_anded(self):
        pred = self._handler()._build_session_predicate("alice", None, "10.0.0.2", None, "ise-1")
        assert pred({"user_name": "alice", "nas_ip_address": "10.0.0.2", "server": "ise-1"}) is True
        assert pred({"user_name": "alice", "nas_ip_address": "10.0.0.1", "server": "ise-1"}) is False


class TestIterFilterActiveSessionsMemoryRegression:
    """Regression test: ensure start+end iterparse idiom keeps peak memory bounded."""

    def test_large_document_memory_remains_bounded(self):
        """Parse 4000 sessions with root.clear(); peak memory stays far below raw document size.

        This test FAILS on the buggy end-only event code (peak ~= document size) and
        PASSES on the correct start+end event code (peak << document size).
        """
        import tracemalloc
        from utils.xml_parser import iter_filter_active_sessions

        # Build a 4000-session document (~3.2 MB raw bytes)
        n_sessions = 4000
        sessions_xml = "".join([
            "<activeSession>"
            f"<user_name>user{i}</user_name>"
            f"<calling_station_id>AA:BB:CC:DD:{i // 256:02X}:{i % 256:02X}</calling_station_id>"
            "<nas_ip_address>10.0.0.1</nas_ip_address>"
            "<server>ise-1</server>"
            "<framed_ip_address>192.168.1.10</framed_ip_address>"
            "<audit_session_id>SESSION-ID-000000000000</audit_session_id>"
            "<acct_session_id>00000001</acct_session_id>"
            "<framed_ipv6_address/>"
            "<nas_ipv6_address/>"
            "</activeSession>"
            for i in range(n_sessions)
        ])
        doc_xml = (
            '<?xml version="1.0"?>'
            f'<activeList noOfActiveSession="{n_sessions}">'
            f'{sessions_xml}'
            '</activeList>'
        )
        raw_bytes = doc_xml.encode("utf-8")
        raw_size_mb = len(raw_bytes) / (1024 * 1024)

        src = io.BytesIO(raw_bytes)

        tracemalloc.start()
        retained, total = iter_filter_active_sessions(src, lambda s: True, retention_cap=10)
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak_mem / (1024 * 1024)
        # With the correct start+end idiom + root.clear(), peak should be ~0.5 MB or less
        # (proportional to a few retained sessions, NOT the entire 3+ MB document).
        # With the buggy end-only code, peak will be ~3+ MB (entire document stays in memory).
        # We assert peak < 1.5 MB; buggy code peaks ~3.2 MB, correct code peaks ~0.3 MB.
        assert peak_mb < 1.5, (
            f"Memory regression: peak {peak_mb:.2f} MB >= 1.5 MB threshold "
            f"(document size {raw_size_mb:.2f} MB). "
            "The streaming parser is NOT clearing the document tree."
        )

        # Verify functional correctness is unchanged
        assert total == n_sessions
        assert len(retained) == 10
