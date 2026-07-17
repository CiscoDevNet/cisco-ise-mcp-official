# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for resources/ise_glossary.py and the get_tool_glossary server resource."""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from resources.ise_glossary import (
    ISE_AUTH_FLOW,
    SESSION_IDENTIFIERS,
    CERTIFICATE_GLOSSARY,
    CERTIFICATE_DIAGNOSIS_GLOSSARY,
    DEFAULT_GLOSSARY,
    FAILURE_GLOSSARY,
    LATENCY_GLOSSARY,
    POLICY_GLOSSARY,
    SESSION_DETAILS_GLOSSARY,
    TOOL_GLOSSARIES,
    _compose,
)

EXPECTED_TOOL_NAMES = {
    "active_sessions_search",
    "sessions_search_with_advanced_details",
    "sessions_search_with_policy_details",
    "sessions_search_with_latency_details",
    "ise_investigate_aaa_failure",
}


# ---------------------------------------------------------------------------
# _compose helper
# ---------------------------------------------------------------------------

class TestComposeHelper:

    def test_two_sections_joined(self):
        assert _compose("A", "B") == "A\n\nB"

    def test_three_sections_joined(self):
        assert _compose("A", "B", "C") == "A\n\nB\n\nC"

    def test_single_section_unchanged(self):
        assert _compose("only") == "only"

    def test_empty_strings_produce_double_newlines(self):
        result = _compose("", "X", "")
        assert result == "\n\nX\n\n"

    def test_multiline_sections_preserved(self):
        s1 = "line1\nline2"
        s2 = "line3\nline4"
        assert _compose(s1, s2) == "line1\nline2\n\nline3\nline4"


# ---------------------------------------------------------------------------
# Glossary constants
# ---------------------------------------------------------------------------

class TestGlossaryConstants:

    def test_auth_flow_type_and_content(self):
        assert isinstance(ISE_AUTH_FLOW, str)
        assert len(ISE_AUTH_FLOW) > 0
        assert "RADIUS" in ISE_AUTH_FLOW
        assert "Policy Set" in ISE_AUTH_FLOW

    def test_session_identifiers_type_and_content(self):
        assert isinstance(SESSION_IDENTIFIERS, str)
        assert len(SESSION_IDENTIFIERS) > 0
        assert "calling_station_id" in SESSION_IDENTIFIERS
        assert "nas_ip_address" in SESSION_IDENTIFIERS
        assert "framed_ip_address" in SESSION_IDENTIFIERS

    def test_session_details_glossary_type_and_content(self):
        assert isinstance(SESSION_DETAILS_GLOSSARY, str)
        assert len(SESSION_DETAILS_GLOSSARY) > 0
        assert "authentication_method" in SESSION_DETAILS_GLOSSARY
        assert "posture_status" in SESSION_DETAILS_GLOSSARY

    def test_policy_glossary_type_and_content(self):
        assert isinstance(POLICY_GLOSSARY, str)
        assert len(POLICY_GLOSSARY) > 0
        assert "Policy Set Selection" in POLICY_GLOSSARY
        assert "authorization_rule" in POLICY_GLOSSARY

    def test_latency_glossary_type_and_content(self):
        assert isinstance(LATENCY_GLOSSARY, str)
        assert len(LATENCY_GLOSSARY) > 0
        assert "execution_steps" in LATENCY_GLOSSARY
        assert "latency_ms" in LATENCY_GLOSSARY

    def test_failure_glossary_type_and_content(self):
        assert isinstance(FAILURE_GLOSSARY, str)
        assert len(FAILURE_GLOSSARY) > 0
        assert "failure_cause" in FAILURE_GLOSSARY
        assert "execution_steps" in FAILURE_GLOSSARY

    def test_glossaries_are_distinct(self):
        all_glossaries = [
            ISE_AUTH_FLOW,
            SESSION_IDENTIFIERS,
            SESSION_DETAILS_GLOSSARY,
            POLICY_GLOSSARY,
            LATENCY_GLOSSARY,
            FAILURE_GLOSSARY,
        ]
        assert len(set(all_glossaries)) == 6


# ---------------------------------------------------------------------------
# TOOL_GLOSSARIES mapping
# ---------------------------------------------------------------------------

class TestToolGlossaries:

    def test_contains_at_least_expected_keys(self):
        assert EXPECTED_TOOL_NAMES.issubset(set(TOOL_GLOSSARIES.keys()))

    def test_active_sessions_is_identifiers_only(self):
        assert TOOL_GLOSSARIES["active_sessions_search"] == SESSION_IDENTIFIERS

    def test_active_sessions_has_no_auth_flow(self):
        assert ISE_AUTH_FLOW not in TOOL_GLOSSARIES["active_sessions_search"]

    def test_basic_details_composition(self):
        value = TOOL_GLOSSARIES["sessions_search_with_advanced_details"]
        assert ISE_AUTH_FLOW in value
        assert SESSION_IDENTIFIERS in value
        assert SESSION_DETAILS_GLOSSARY in value
        assert value == _compose(ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY)

    def test_policy_details_composition(self):
        value = TOOL_GLOSSARIES["sessions_search_with_policy_details"]
        assert ISE_AUTH_FLOW in value
        assert SESSION_IDENTIFIERS in value
        assert SESSION_DETAILS_GLOSSARY in value
        assert POLICY_GLOSSARY in value
        assert value == _compose(
            ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY, POLICY_GLOSSARY
        )

    def test_latency_details_composition(self):
        value = TOOL_GLOSSARIES["sessions_search_with_latency_details"]
        assert ISE_AUTH_FLOW in value
        assert SESSION_IDENTIFIERS in value
        assert SESSION_DETAILS_GLOSSARY in value
        assert LATENCY_GLOSSARY in value
        assert value == _compose(
            ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY, LATENCY_GLOSSARY
        )

    def test_failure_investigation_composition(self):
        value = TOOL_GLOSSARIES["ise_investigate_aaa_failure"]
        assert ISE_AUTH_FLOW in value
        assert SESSION_IDENTIFIERS in value
        assert SESSION_DETAILS_GLOSSARY in value
        assert FAILURE_GLOSSARY in value
        assert value == _compose(
            ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY, FAILURE_GLOSSARY
        )

    def test_diagnose_certificate_issues_composition(self):
        value = TOOL_GLOSSARIES["ise_diagnose_certificate_issues"]
        assert CERTIFICATE_GLOSSARY in value
        assert CERTIFICATE_DIAGNOSIS_GLOSSARY in value
        assert value == _compose(CERTIFICATE_GLOSSARY, CERTIFICATE_DIAGNOSIS_GLOSSARY)
        # The diagnosis-specific fields the base cert glossary does not cover.
        assert "verdict:" in value
        assert "coverage_note:" in value
        assert "total_matches:" in value

    def test_values_use_double_newline_separator(self):
        for key in EXPECTED_TOOL_NAMES:
            value = TOOL_GLOSSARIES[key]
            assert isinstance(value, str)
            if "\n\n" not in value:
                assert value == SESSION_IDENTIFIERS, (
                    f"{key} should be SESSION_IDENTIFIERS if it has no separator"
                )

    def test_active_sessions_does_not_contain_session_details(self):
        assert SESSION_DETAILS_GLOSSARY not in TOOL_GLOSSARIES["active_sessions_search"]

    def test_policy_details_does_not_contain_latency(self):
        assert LATENCY_GLOSSARY not in TOOL_GLOSSARIES["sessions_search_with_policy_details"]

    def test_latency_details_does_not_contain_policy(self):
        assert POLICY_GLOSSARY not in TOOL_GLOSSARIES["sessions_search_with_latency_details"]

    def test_failure_does_not_contain_latency_or_policy(self):
        value = TOOL_GLOSSARIES["ise_investigate_aaa_failure"]
        assert LATENCY_GLOSSARY not in value
        assert POLICY_GLOSSARY not in value


# ---------------------------------------------------------------------------
# DEFAULT_GLOSSARY
# ---------------------------------------------------------------------------

class TestDefaultGlossary:

    def test_default_is_empty_string(self):
        assert DEFAULT_GLOSSARY == ""

    def test_unknown_tool_returns_empty(self):
        assert TOOL_GLOSSARIES.get("nonexistent_tool", DEFAULT_GLOSSARY) == ""


# ---------------------------------------------------------------------------
# get_tool_glossary (server resource lookup logic)
# ---------------------------------------------------------------------------

def _get_tool_glossary(tool_name: str) -> str:
    """Mirrors the server resource: TOOL_GLOSSARIES.get(tool_name, DEFAULT_GLOSSARY)."""
    return TOOL_GLOSSARIES.get(tool_name, DEFAULT_GLOSSARY)


class TestGetToolGlossary:

    def test_known_tool_active_sessions(self):
        assert _get_tool_glossary("active_sessions_search") == TOOL_GLOSSARIES["active_sessions_search"]

    def test_known_tool_basic_details(self):
        assert _get_tool_glossary("sessions_search_with_advanced_details") == TOOL_GLOSSARIES["sessions_search_with_advanced_details"]

    def test_known_tool_policy_details(self):
        assert _get_tool_glossary("sessions_search_with_policy_details") == TOOL_GLOSSARIES["sessions_search_with_policy_details"]

    def test_known_tool_latency_details(self):
        assert _get_tool_glossary("sessions_search_with_latency_details") == TOOL_GLOSSARIES["sessions_search_with_latency_details"]

    def test_unknown_tool_returns_default(self):
        assert _get_tool_glossary("nonexistent_tool") == DEFAULT_GLOSSARY

    def test_empty_string_returns_default(self):
        assert _get_tool_glossary("") == DEFAULT_GLOSSARY

    def test_wrong_casing_returns_default(self):
        assert _get_tool_glossary("Active_Sessions_Search") == DEFAULT_GLOSSARY

    def test_leading_trailing_whitespace_returns_default(self):
        assert _get_tool_glossary("  active_sessions_search  ") == DEFAULT_GLOSSARY

    def test_special_characters_returns_default(self):
        assert _get_tool_glossary("active_sessions_search!@#") == DEFAULT_GLOSSARY

    def test_partial_tool_name_returns_default(self):
        assert _get_tool_glossary("active_sessions") == DEFAULT_GLOSSARY

    def test_all_known_tools_return_non_default_or_match(self):
        for tool_name in EXPECTED_TOOL_NAMES:
            result = _get_tool_glossary(tool_name)
            assert result == TOOL_GLOSSARIES[tool_name]
            assert isinstance(result, str)
            assert len(result) > 0


# ---------------------------------------------------------------------------
# Re-enabled tools glossary verification (Task 5)
# ---------------------------------------------------------------------------

def test_reenabled_tools_have_glossaries():
    for name in (
        "ise_get_policy_set_details",
        "ise_search_authorization_profiles",
        "ise_search_library_conditions",
        "ise_list_policy_authoring_references",
    ):
        assert name in TOOL_GLOSSARIES
        assert TOOL_GLOSSARIES[name]  # non-empty
