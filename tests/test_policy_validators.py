# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Tests for the policy-tool input validators in utils/input_validators.py."""

import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastmcp.exceptions import ToolError as McpToolError
from utils.input_validators import (
    validate_condition_scope_filter,
    validate_hit_counts_range,
    validate_max_hit_counts,
    validate_min_hit_counts,
    validate_name_substring,
    validate_policy_set_name,
    validate_policy_set_state_filter,
    validate_rule_state_filter,
)


def _error_code(exc_info) -> str:
    return json.loads(str(exc_info.value))["error_code"]


# ---------------------------------------------------------------------------
# validate_policy_set_name
# ---------------------------------------------------------------------------

class TestValidatePolicySetName:
    def test_alphanumeric_passes(self):
        assert validate_policy_set_name("Default") == "Default"

    def test_with_underscores_and_hyphens(self):
        assert validate_policy_set_name("Employee_Wired-Access") == "Employee_Wired-Access"

    def test_with_periods_and_parentheses(self):
        assert validate_policy_set_name("Site.A (Branch)") == "Site.A (Branch)"

    def test_with_spaces(self):
        assert validate_policy_set_name("Default Network Access") == "Default Network Access"

    def test_strips_outer_whitespace(self):
        assert validate_policy_set_name("   Default   ") == "Default"

    def test_rejects_empty(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_policy_set_name("")
        assert _error_code(exc_info) == "INVALID_POLICY_SET_NAME"

    def test_rejects_whitespace_only(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_policy_set_name("   ")
        assert _error_code(exc_info) == "INVALID_POLICY_SET_NAME"

    def test_rejects_too_long(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_policy_set_name("a" * 257)
        assert _error_code(exc_info) == "INVALID_POLICY_SET_NAME"

    def test_rejects_disallowed_characters(self):
        # Colon, slash, ampersand, etc. are not in the policy-set name alphabet.
        for value in ("AD:corp.example.com", "Bad/Name", "A&B", "<script>"):
            with pytest.raises(McpToolError) as exc_info:
                validate_policy_set_name(value)
            assert _error_code(exc_info) == "INVALID_POLICY_SET_NAME"


# ---------------------------------------------------------------------------
# validate_name_substring
# ---------------------------------------------------------------------------

class TestValidateNameSubstring:
    def test_basic_substring(self):
        assert validate_name_substring("Permit") == "Permit"

    def test_allows_colon_for_ad_paths(self):
        assert validate_name_substring("AD:corp.example.com") == "AD:corp.example.com"

    def test_allows_slash_plus_comma_ampersand(self):
        assert validate_name_substring("a/b+c,d&e") == "a/b+c,d&e"

    def test_strips_whitespace(self):
        assert validate_name_substring("  Permit  ") == "Permit"

    def test_rejects_empty(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_name_substring("")
        assert _error_code(exc_info) == "INVALID_NAME_SUBSTRING"

    def test_rejects_too_long(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_name_substring("a" * 257)
        assert _error_code(exc_info) == "INVALID_NAME_SUBSTRING"

    def test_rejects_control_characters(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_name_substring("bad\x00value")
        assert _error_code(exc_info) == "INVALID_NAME_SUBSTRING"

    def test_rejects_quotes_and_html(self):
        for value in ("\"quoted\"", "<script>", "name';--"):
            with pytest.raises(McpToolError) as exc_info:
                validate_name_substring(value)
            assert _error_code(exc_info) == "INVALID_NAME_SUBSTRING"

    def test_field_name_in_error_message(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_name_substring("", field_name="profile_name_filter")
        data = json.loads(str(exc_info.value))
        assert "profile_name_filter" in data["message"]


# ---------------------------------------------------------------------------
# validate_policy_set_state_filter
# ---------------------------------------------------------------------------

class TestValidatePolicySetStateFilter:
    @pytest.mark.parametrize("value", ["all", "enabled", "disabled", "monitor"])
    def test_valid_values(self, value):
        assert validate_policy_set_state_filter(value) == value

    def test_case_insensitive(self):
        assert validate_policy_set_state_filter("ENABLED") == "enabled"
        assert validate_policy_set_state_filter("Disabled") == "disabled"

    def test_strips_whitespace(self):
        assert validate_policy_set_state_filter("  monitor  ") == "monitor"

    def test_rejects_unknown_value(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_policy_set_state_filter("active")
        assert _error_code(exc_info) == "INVALID_STATE_FILTER"

    def test_rejects_empty(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_policy_set_state_filter("")
        assert _error_code(exc_info) == "INVALID_STATE_FILTER"


# ---------------------------------------------------------------------------
# validate_rule_state_filter
# ---------------------------------------------------------------------------

class TestValidateRuleStateFilter:
    @pytest.mark.parametrize("value", ["all", "enabled", "disabled"])
    def test_valid_values(self, value):
        assert validate_rule_state_filter(value) == value

    def test_rejects_monitor(self):
        # Monitor is valid for policy sets but not for individual rules per the plan.
        with pytest.raises(McpToolError) as exc_info:
            validate_rule_state_filter("monitor")
        assert _error_code(exc_info) == "INVALID_STATE_FILTER"

    def test_rejects_unknown(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_rule_state_filter("active")
        assert _error_code(exc_info) == "INVALID_STATE_FILTER"


# ---------------------------------------------------------------------------
# validate_condition_scope_filter
# ---------------------------------------------------------------------------

class TestValidateConditionScopeFilter:
    @pytest.mark.parametrize("value", ["all", "policyset", "authentication", "authorization"])
    def test_valid_values(self, value):
        assert validate_condition_scope_filter(value) == value

    def test_case_insensitive(self):
        assert validate_condition_scope_filter("Authorization") == "authorization"

    def test_rejects_unknown(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_condition_scope_filter("rule")
        assert _error_code(exc_info) == "INVALID_SCOPE_FILTER"


# ---------------------------------------------------------------------------
# validate_min_hit_counts
# ---------------------------------------------------------------------------

class TestValidateMinHitCounts:
    def test_none_returns_none(self):
        assert validate_min_hit_counts(None) is None

    def test_zero_passes(self):
        assert validate_min_hit_counts(0) == 0

    def test_positive_passes(self):
        assert validate_min_hit_counts(42) == 42

    def test_rejects_negative(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_min_hit_counts(-1)
        assert _error_code(exc_info) == "INVALID_MIN_HIT_COUNTS"


# ---------------------------------------------------------------------------
# validate_max_hit_counts
# ---------------------------------------------------------------------------

class TestValidateMaxHitCounts:
    def test_none_returns_none(self):
        assert validate_max_hit_counts(None) is None

    def test_zero_passes(self):
        assert validate_max_hit_counts(0) == 0

    def test_positive_passes(self):
        assert validate_max_hit_counts(99) == 99

    def test_rejects_negative(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_max_hit_counts(-5)
        assert _error_code(exc_info) == "INVALID_MAX_HIT_COUNTS"


# ---------------------------------------------------------------------------
# validate_hit_counts_range
# ---------------------------------------------------------------------------

class TestValidateHitCountsRange:
    def test_both_none_passes(self):
        validate_hit_counts_range(None, None)

    def test_only_min_set_passes(self):
        validate_hit_counts_range(5, None)

    def test_only_max_set_passes(self):
        validate_hit_counts_range(None, 5)

    def test_min_equals_max_passes(self):
        validate_hit_counts_range(3, 3)

    def test_min_less_than_max_passes(self):
        validate_hit_counts_range(1, 10)

    def test_rejects_min_greater_than_max(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_hit_counts_range(10, 5)
        assert _error_code(exc_info) == "INVALID_HIT_COUNT_RANGE"


# ---------------------------------------------------------------------------
# Error payload structure
# ---------------------------------------------------------------------------

class TestErrorPayloadStructure:
    def test_policy_set_name_error_includes_value(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_policy_set_name("AD:corp.example.com")
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "client_error"
        assert data["error_code"] == "INVALID_POLICY_SET_NAME"
        assert "AD:corp.example.com" in data["message"]
        assert data["retry"] is False

    def test_state_filter_error_includes_allowed_values(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_rule_state_filter("active")
        data = json.loads(str(exc_info.value))
        assert "all" in data["message"]
        assert "enabled" in data["message"]
        assert "disabled" in data["message"]

    def test_scope_filter_error_includes_allowed_values(self):
        with pytest.raises(McpToolError) as exc_info:
            validate_condition_scope_filter("rule")
        data = json.loads(str(exc_info.value))
        assert "policyset" in data["message"]
        assert "authentication" in data["message"]
        assert "authorization" in data["message"]
