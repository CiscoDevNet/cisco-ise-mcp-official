# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Tests for utils/input_validators.py."""

import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastmcp.exceptions import ToolError as McpToolError
from utils.input_validators import (
    normalize_mac_address,
    validate_minutes,
    validate_ip_address,
    validate_latency_range,
    validate_limit,
    validate_mac_address,
)


def _error_code(exc_info) -> str:
    return json.loads(str(exc_info.value))["error_code"]


# ---------------------------------------------------------------------------
# normalize_mac_address
# ---------------------------------------------------------------------------

class TestNormalizeMacAddress:

    def test_colon_separated(self):
        assert normalize_mac_address("aa:bb:cc:dd:ee:ff") == "AA:BB:CC:DD:EE:FF"

    def test_dash_separated(self):
        assert normalize_mac_address("aa-bb-cc-dd-ee-ff") == "AA:BB:CC:DD:EE:FF"

    def test_cisco_dot_format(self):
        assert normalize_mac_address("aabb.ccdd.eeff") == "AA:BB:CC:DD:EE:FF"

    def test_bare_format(self):
        assert normalize_mac_address("aabbccddeeff") == "AA:BB:CC:DD:EE:FF"

    def test_already_normalized(self):
        assert normalize_mac_address("AA:BB:CC:DD:EE:FF") == "AA:BB:CC:DD:EE:FF"

    def test_mixed_case(self):
        assert normalize_mac_address("Aa:Bb:Cc:Dd:Ee:Ff") == "AA:BB:CC:DD:EE:FF"

    def test_too_short_returns_uppercased_original(self):
        assert normalize_mac_address("aa:bb") == "AA:BB"

    def test_too_long_returns_uppercased_original(self):
        assert normalize_mac_address("aa:bb:cc:dd:ee:ff:00") == "AA:BB:CC:DD:EE:FF:00"

    def test_empty_string_returns_empty(self):
        assert normalize_mac_address("") == ""


# ---------------------------------------------------------------------------
# validate_mac_address
# ---------------------------------------------------------------------------

class TestValidateMacAddress:

    def test_valid_colon_format(self):
        assert validate_mac_address("aa:bb:cc:dd:ee:ff") == "AA:BB:CC:DD:EE:FF"

    def test_valid_dash_format(self):
        assert validate_mac_address("AA-BB-CC-DD-EE-FF") == "AA:BB:CC:DD:EE:FF"

    def test_valid_cisco_format(self):
        assert validate_mac_address("aabb.ccdd.eeff") == "AA:BB:CC:DD:EE:FF"

    def test_valid_bare_format(self):
        assert validate_mac_address("AABBCCDDEEFF") == "AA:BB:CC:DD:EE:FF"

    def test_strips_whitespace(self):
        assert validate_mac_address("  aa:bb:cc:dd:ee:ff  ") == "AA:BB:CC:DD:EE:FF"

    def test_rejects_too_short(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("AA:BB:CC")
        assert _error_code(exc_info) == "INVALID_MAC_ADDRESS"

    def test_rejects_too_long(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("AA:BB:CC:DD:EE:FF:00")
        assert _error_code(exc_info) == "INVALID_MAC_ADDRESS"

    def test_rejects_non_hex_characters(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("GG:HH:II:JJ:KK:LL")
        assert _error_code(exc_info) == "INVALID_MAC_ADDRESS"

    def test_rejects_empty_string(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("")
        assert _error_code(exc_info) == "INVALID_MAC_ADDRESS"

    def test_rejects_whitespace_only(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("   ")
        assert _error_code(exc_info) == "INVALID_MAC_ADDRESS"

    def test_rejects_random_text(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("not-a-mac-address")
        assert _error_code(exc_info) == "INVALID_MAC_ADDRESS"

    def test_rejects_correct_length_non_hex(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("ZZZZZZZZZZZZ")
        assert _error_code(exc_info) == "INVALID_MAC_ADDRESS"


# ---------------------------------------------------------------------------
# validate_ip_address
# ---------------------------------------------------------------------------

class TestValidateIpAddress:

    def test_valid_ipv4(self):
        assert validate_ip_address("10.0.0.1") == "10.0.0.1"

    def test_valid_ipv4_loopback(self):
        assert validate_ip_address("127.0.0.1") == "127.0.0.1"

    def test_valid_ipv6(self):
        assert validate_ip_address("::1") == "::1"

    def test_valid_ipv6_full(self):
        assert validate_ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def test_strips_whitespace(self):
        assert validate_ip_address("  10.0.0.1  ") == "10.0.0.1"

    def test_rejects_out_of_range_octet(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_ip_address("999.999.999.999")
        assert _error_code(exc_info) == "INVALID_IP_ADDRESS"

    def test_rejects_hostname(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_ip_address("example.com")
        assert _error_code(exc_info) == "INVALID_IP_ADDRESS"

    def test_rejects_empty_string(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_ip_address("")
        assert _error_code(exc_info) == "INVALID_IP_ADDRESS"

    def test_rejects_partial_ip(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_ip_address("10.0.0")
        assert _error_code(exc_info) == "INVALID_IP_ADDRESS"

    def test_rejects_ip_with_port(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_ip_address("10.0.0.1:8080")
        assert _error_code(exc_info) == "INVALID_IP_ADDRESS"

    def test_rejects_cidr_notation(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_ip_address("10.0.0.0/24")
        assert _error_code(exc_info) == "INVALID_IP_ADDRESS"


# ---------------------------------------------------------------------------
# validate_minutes
# ---------------------------------------------------------------------------

class TestValidateMinutes:

    def test_valid_boundary_min(self):
        assert validate_minutes(1, max_minutes=1440) == 1

    def test_valid_boundary_max(self):
        assert validate_minutes(1440, max_minutes=1440) == 1440

    def test_valid_mid_range(self):
        assert validate_minutes(60, max_minutes=1440) == 60

    def test_rejects_zero(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(0, max_minutes=1440)
        assert _error_code(exc_info) == "INVALID_MINUTES"

    def test_rejects_negative(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(-5, max_minutes=1440)
        assert _error_code(exc_info) == "INVALID_MINUTES"

    def test_rejects_above_max(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(1441, max_minutes=1440)
        assert _error_code(exc_info) == "INVALID_MINUTES"

    def test_rejects_large_value(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(99999, max_minutes=1440)
        assert _error_code(exc_info) == "INVALID_MINUTES"

    def test_custom_max_minutes(self):
        assert validate_minutes(720, max_minutes=720) == 720
        with pytest.raises(McpToolError):
            validate_minutes(721, max_minutes=720)

    def test_below_min_message_mentions_one_minute_window(self):
        """The sub-1-minute path returns a user-ready 'at least 1 minute' hint,
        not a raw range dump."""
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(0, max_minutes=1440)
        message = json.loads(str(exc_info.value))["message"]
        assert "1 minute" in message

    def test_above_max_message_mentions_hours_and_got_value(self):
        """The above-max path reports the max in both minutes and hours and
        echoes back the offending value."""
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(5000, max_minutes=1440)
        message = json.loads(str(exc_info.value))["message"]
        assert "1440 minutes" in message
        assert "24 hours" in message
        assert "5000" in message

    def test_below_min_and_above_max_share_error_code(self):
        """Both out-of-range directions surface the same INVALID_MINUTES code."""
        with pytest.raises(McpToolError) as below:
            validate_minutes(0, max_minutes=1440)
        with pytest.raises(McpToolError) as above:
            validate_minutes(1441, max_minutes=1440)
        assert _error_code(below) == _error_code(above) == "INVALID_MINUTES"

    def test_below_min_does_not_leak_max(self):
        """The sub-1-minute message focuses on the lower bound and must not
        mention the configured maximum."""
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(-100, max_minutes=1440)
        message = json.loads(str(exc_info.value))["message"]
        assert "1440" not in message

    def test_hours_derived_from_custom_max(self):
        """The hours figure in the above-max message is derived from
        max_minutes via integer division (90 minutes -> 1 hour)."""
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(200, max_minutes=90)
        message = json.loads(str(exc_info.value))["message"]
        assert "90 minutes" in message
        assert "1 hours" in message


# ---------------------------------------------------------------------------
# validate_limit
# ---------------------------------------------------------------------------

class TestValidateLimit:

    def test_valid_boundary_min(self):
        assert validate_limit(1, max_limit=200) == 1

    def test_valid_boundary_max(self):
        assert validate_limit(200, max_limit=200) == 200

    def test_valid_mid_range(self):
        assert validate_limit(50, max_limit=200) == 50

    def test_rejects_zero(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_limit(0, max_limit=200)
        assert _error_code(exc_info) == "INVALID_LIMIT"

    def test_rejects_negative(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_limit(-1, max_limit=200)
        assert _error_code(exc_info) == "INVALID_LIMIT"

    def test_rejects_above_max(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_limit(201, max_limit=200)
        assert _error_code(exc_info) == "INVALID_LIMIT"

    def test_custom_max_limit(self):
        assert validate_limit(3, max_limit=3) == 3
        with pytest.raises(McpToolError):
            validate_limit(4, max_limit=3)


# ---------------------------------------------------------------------------
# validate_latency_range
# ---------------------------------------------------------------------------

class TestValidateLatencyRange:

    def test_both_none_passes(self):
        validate_latency_range(None, None)

    def test_only_min_set_passes(self):
        validate_latency_range(100, None)

    def test_only_max_set_passes(self):
        validate_latency_range(None, 500)

    def test_valid_range_passes(self):
        validate_latency_range(100, 500)

    def test_equal_min_max_passes(self):
        validate_latency_range(200, 200)

    def test_zero_min_passes(self):
        validate_latency_range(0, 100)

    def test_zero_max_passes(self):
        validate_latency_range(0, 0)

    def test_rejects_negative_min(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_latency_range(-1, 100)
        assert _error_code(exc_info) == "INVALID_MIN_LATENCY"

    def test_rejects_negative_max(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_latency_range(None, -1)
        assert _error_code(exc_info) == "INVALID_MAX_LATENCY"

    def test_rejects_both_negative(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_latency_range(-10, -5)
        assert _error_code(exc_info) == "INVALID_MIN_LATENCY"

    def test_rejects_inverted_range(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_latency_range(500, 100)
        assert _error_code(exc_info) == "INVALID_LATENCY_RANGE"

    def test_rejects_inverted_by_one(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_latency_range(101, 100)
        assert _error_code(exc_info) == "INVALID_LATENCY_RANGE"


# ---------------------------------------------------------------------------
# Error payload structure
# ---------------------------------------------------------------------------

class TestErrorPayloadStructure:
    """Verify that all validators produce well-formed structured error payloads."""

    def test_mac_error_has_full_payload(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_mac_address("bad")
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "client_error"
        assert data["error_code"] == "INVALID_MAC_ADDRESS"
        assert "bad" in data["message"]
        assert data["retry"] is False

    def test_ip_error_has_full_payload(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_ip_address("not.an.ip")
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "client_error"
        assert data["error_code"] == "INVALID_IP_ADDRESS"
        assert "not.an.ip" in data["message"]
        assert data["retry"] is False

    def test_sub_minute_error_message_is_user_ready(self):
        """A sub-1-minute window (e.g. user asked for 'last 10 sec') must
        produce a clear, actionable message telling the user the minimum
        supported window, not a raw range dump."""
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(0, max_minutes=1440)
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "INVALID_MINUTES"
        assert data["error_category"] == "client_error"
        assert data["retry"] is False
        assert "1 minute" in data["message"]

    def test_above_max_error_message_mentions_limit(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_minutes(2000, max_minutes=1440)
        data = json.loads(str(exc_info.value))
        assert "1440" in data["message"]

    def test_limit_error_includes_value_in_message(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_limit(999, max_limit=200)
        data = json.loads(str(exc_info.value))
        assert "999" in data["message"]
        assert "200" in data["message"]

    def test_latency_range_error_includes_both_values(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_latency_range(500, 100)
        data = json.loads(str(exc_info.value))
        assert "500" in data["message"]
        assert "100" in data["message"]


class TestValidateHostname:
    def test_valid_hostname_returned(self):
        from utils.input_validators import validate_hostname
        assert validate_hostname("vm218") == "vm218"

    def test_valid_with_hyphen_and_digits(self):
        from utils.input_validators import validate_hostname
        assert validate_hostname("ise-node-01") == "ise-node-01"

    def test_strips_whitespace(self):
        from utils.input_validators import validate_hostname
        assert validate_hostname("  vm218  ") == "vm218"

    def test_must_start_with_letter(self):
        from utils.input_validators import validate_hostname
        import pytest
        from fastmcp.exceptions import ToolError
        with pytest.raises(ToolError):
            validate_hostname("1node")

    def test_rejects_dot(self):
        # FQDN-style input is rejected; hostname only.
        from utils.input_validators import validate_hostname
        import pytest
        from fastmcp.exceptions import ToolError
        with pytest.raises(ToolError):
            validate_hostname("vm218.marcos.com")

    def test_rejects_filter_injection_chars(self):
        from utils.input_validators import validate_hostname
        import pytest
        from fastmcp.exceptions import ToolError
        with pytest.raises(ToolError):
            validate_hostname("vm218.EQ.x&filter=y")

    def test_rejects_too_long(self):
        from utils.input_validators import validate_hostname
        import pytest
        from fastmcp.exceptions import ToolError
        with pytest.raises(ToolError):
            validate_hostname("a" * 65)

    def test_rejects_empty(self):
        from utils.input_validators import validate_hostname
        import pytest
        from fastmcp.exceptions import ToolError
        with pytest.raises(ToolError):
            validate_hostname("")
