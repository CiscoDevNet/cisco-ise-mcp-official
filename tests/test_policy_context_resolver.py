# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Tests for PolicyContextResolver: name-to-ID resolution, not-found handling, concurrent fetch."""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from services.policy_context_resolver import PolicyContextResolver, condition_to_summary
from models.policy_models import PolicyContext
from models.session_models import EnrichedSessionSearchResult, SessionDetail


SAMPLE_POLICY_SET_LIST_RESPONSE = [
    {
        "id": "a1f27026-15c3-4688-8a41-8ac0217d4aaa",
        "name": "Default",
        "description": "Default policy set",
        "state": "enabled",
        "serviceName": "Default Network Access",
        "hitCounts": 42,
        "default": True,
        "condition": {
            "conditionType": "ConditionReference",
            "isNegate": False,
            "name": "Wired_802.1X",
            "id": "19d968b0-ebcb-4cdd-98e3-fe02e5521266",
        },
    },
    {
        "id": "b2e38137-26d4-5799-9b52-9bd1328e5bbb",
        "name": "Wired_MAB",
        "description": "Wired MAB policy set",
        "state": "enabled",
        "serviceName": "MAB",
        "hitCounts": 10,
        "default": False,
        "condition": {
            "conditionType": "ConditionAttributes",
            "isNegate": False,
            "dictionaryName": "Radius",
            "attributeName": "Service-Type",
            "operator": "equals",
            "attributeValue": "Call Check",
        },
    },
]

SAMPLE_AUTHN_RULE_LIST_RESPONSE = [
    {
        "rule": {
            "id": "c3f49248-37e5-6800-ac63-ace2439f6ccc",
            "name": "Default",
            "state": "enabled",
            "hitCounts": 100,
            "default": True,
            "condition": None,
        },
        "identitySourceName": "Internal Users",
        "ifAuthFail": "reject",
        "ifUserNotFound": "reject",
        "ifProcessFail": "drop",
    },
    {
        "rule": {
            "id": "d4059359-48f6-7911-bd74-bdf354a07ddd",
            "name": "MAB_Rule",
            "state": "enabled",
            "hitCounts": 5,
            "default": False,
            "condition": {
                "conditionType": "ConditionAttributes",
                "isNegate": False,
                "dictionaryName": "Network Access",
                "attributeName": "EapAuthentication",
                "operator": "equals",
                "attributeValue": "EAP-TLS",
            },
        },
        "identitySourceName": "Internal Endpoints",
        "ifAuthFail": "reject",
        "ifUserNotFound": "continue",
        "ifProcessFail": "drop",
    },
]

SAMPLE_AUTHZ_RULE_LIST_RESPONSE = [
    {
        "rule": {
            "id": "e5160460-59f7-8022-ce85-cef465b18eee",
            "name": "Basic_Authenticated_Access",
            "state": "enabled",
            "hitCounts": 80,
            "default": False,
            "condition": {
                "conditionType": "ConditionAndBlock",
                "isNegate": False,
                "children": [
                    {
                        "conditionType": "ConditionAttributes",
                        "isNegate": False,
                        "dictionaryName": "Network Access",
                        "attributeName": "Device IP Address",
                        "operator": "ipEquals",
                        "attributeValue": "10.0.10.0",
                    },
                    {
                        "conditionType": "ConditionReference",
                        "isNegate": False,
                        "name": "Wired_802.1X",
                        "id": "19d968b0-ebcb-4cdd-98e3-fe02e5521266",
                    },
                ],
            },
        },
        "profile": ["PermitAccess"],
        "securityGroup": "Employees",
    },
    {
        "rule": {
            "id": "f6271571-60g8-9133-df96-dfg576c29fff",
            "name": "Deny_Access",
            "state": "enabled",
            "hitCounts": 2,
            "default": True,
            "condition": None,
        },
        "profile": ["DenyAccess"],
        "securityGroup": None,
    },
]


def _build_resolver(
    policy_set_list_response=SAMPLE_POLICY_SET_LIST_RESPONSE,
    authn_rule_list_response=SAMPLE_AUTHN_RULE_LIST_RESPONSE,
    authz_rule_list_response=SAMPLE_AUTHZ_RULE_LIST_RESPONSE,
):
    """Build a PolicyContextResolver with a mocked PolicyToolHandler."""
    mock_handler = AsyncMock()
    mock_handler.get_network_access_policy_set_list = AsyncMock(
        return_value=policy_set_list_response
    )
    mock_handler.get_network_access_authentication_rule_list = AsyncMock(
        return_value=authn_rule_list_response
    )
    mock_handler.get_network_access_authorization_rule_list = AsyncMock(
        return_value=authz_rule_list_response
    )
    return PolicyContextResolver(mock_handler), mock_handler


class TestPolicyContextResolverResolve:
    """Tests for the full resolve() flow."""

    @pytest.mark.asyncio
    async def test_resolve_full_context(self):
        resolver, handler = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authn_rule_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        assert isinstance(result, PolicyContext)
        assert result.policy_set is not None
        assert result.policy_set.name == "Default"
        assert result.policy_set.condition_summary == "Wired_802.1X"

        assert result.authentication_rule is not None
        assert result.authentication_rule.name == "Default"
        assert result.authentication_rule.identity_source_name == "Internal Users"
        assert result.authentication_rule.if_auth_fail == "reject"
        assert result.authentication_rule.condition_summary is None

        assert result.authorization_rule is not None
        assert result.authorization_rule.name == "Basic_Authenticated_Access"
        assert result.authorization_rule.profile == ["PermitAccess"]
        assert result.authorization_rule.security_group == "Employees"
        assert result.authorization_rule.condition_summary == "Network Access:Device IP Address ipEquals 10.0.10.0 AND Wired_802.1X"

        assert result.resolution_errors is None

    @pytest.mark.asyncio
    async def test_resolve_policy_set_only(self):
        resolver, handler = _build_resolver()

        result = await resolver.resolve(policy_set_name="Default")

        assert result.policy_set is not None
        assert result.policy_set.name == "Default"
        assert result.authentication_rule is None
        assert result.authorization_rule is None
        assert result.resolution_errors is None
        handler.get_network_access_authentication_rule_list.assert_not_called()
        handler.get_network_access_authorization_rule_list.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolve_with_authn_only(self):
        resolver, handler = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authn_rule_name="Default",
        )

        assert result.policy_set is not None
        assert result.authentication_rule is not None
        assert result.authorization_rule is None
        handler.get_network_access_authentication_rule_list.assert_called_once()
        handler.get_network_access_authorization_rule_list.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolve_with_authz_only(self):
        resolver, handler = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        assert result.policy_set is not None
        assert result.authentication_rule is None
        assert result.authorization_rule is not None
        handler.get_network_access_authentication_rule_list.assert_not_called()
        handler.get_network_access_authorization_rule_list.assert_called_once()


class TestPolicyContextResolverNotFound:
    """Tests for name resolution failures."""

    @pytest.mark.asyncio
    async def test_policy_set_not_found(self):
        resolver, _ = _build_resolver()

        result = await resolver.resolve(policy_set_name="NonExistent")

        assert result.policy_set is None
        assert result.authentication_rule is None
        assert result.authorization_rule is None
        assert result.resolution_errors is not None
        assert any("NonExistent" in e and "not found" in e for e in result.resolution_errors)

    @pytest.mark.asyncio
    async def test_authn_rule_not_found(self):
        resolver, _ = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authn_rule_name="NonExistentRule",
        )

        assert result.policy_set is not None
        assert result.authentication_rule is None
        assert result.resolution_errors is not None
        assert any("NonExistentRule" in e for e in result.resolution_errors)

    @pytest.mark.asyncio
    async def test_authz_rule_not_found(self):
        resolver, _ = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authz_rule_name="NonExistentRule",
        )

        assert result.policy_set is not None
        assert result.authorization_rule is None
        assert result.resolution_errors is not None
        assert any("NonExistentRule" in e for e in result.resolution_errors)

    @pytest.mark.asyncio
    async def test_policy_set_not_found_skips_rule_resolution(self):
        resolver, handler = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="NonExistent",
            authn_rule_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        assert result.policy_set is None
        assert result.authentication_rule is None
        assert result.authorization_rule is None
        handler.get_network_access_authentication_rule_list.assert_not_called()
        handler.get_network_access_authorization_rule_list.assert_not_called()


class TestPolicyContextResolverErrors:
    """Tests for API failure handling."""

    @pytest.mark.asyncio
    async def test_policy_set_list_api_failure(self):
        resolver, handler = _build_resolver()
        handler.get_network_access_policy_set_list = AsyncMock(
            side_effect=Exception("connection refused")
        )

        result = await resolver.resolve(policy_set_name="Default")

        assert result.policy_set is None
        assert result.resolution_errors is not None
        assert any("Failed to fetch policy set list" in e for e in result.resolution_errors)

    @pytest.mark.asyncio
    async def test_authn_rule_list_api_failure(self):
        resolver, handler = _build_resolver()
        handler.get_network_access_authentication_rule_list = AsyncMock(
            side_effect=Exception("timeout")
        )

        result = await resolver.resolve(
            policy_set_name="Default",
            authn_rule_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        assert result.policy_set is not None
        assert result.authentication_rule is None
        assert result.authorization_rule is not None
        assert result.resolution_errors is not None
        assert any("Failed to fetch authentication rules from ISE" in e for e in result.resolution_errors)

    @pytest.mark.asyncio
    async def test_authz_rule_list_api_failure(self):
        resolver, handler = _build_resolver()
        handler.get_network_access_authorization_rule_list = AsyncMock(
            side_effect=Exception("500 internal server error")
        )

        result = await resolver.resolve(
            policy_set_name="Default",
            authn_rule_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        assert result.policy_set is not None
        assert result.authentication_rule is not None
        assert result.authorization_rule is None
        assert result.resolution_errors is not None
        assert any("Failed to fetch authorization rules from ISE" in e for e in result.resolution_errors)

    @pytest.mark.asyncio
    async def test_invalid_response_format(self):
        resolver, handler = _build_resolver(
            policy_set_list_response="not a list"
        )

        result = await resolver.resolve(policy_set_name="Default")

        assert result.policy_set is None
        assert result.resolution_errors is not None
        assert len(result.resolution_errors) >= 1


class TestPolicyContextResolverConcurrency:
    """Tests that authn and authz rule resolution runs concurrently."""

    @pytest.mark.asyncio
    async def test_both_rules_resolved_concurrently(self):
        resolver, handler = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authn_rule_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        assert result.authentication_rule is not None
        assert result.authorization_rule is not None
        handler.get_network_access_authentication_rule_list.assert_called_once_with(
            policy_id="a1f27026-15c3-4688-8a41-8ac0217d4aaa"
        )
        handler.get_network_access_authorization_rule_list.assert_called_once_with(
            policy_id="a1f27026-15c3-4688-8a41-8ac0217d4aaa"
        )


class TestPolicyContextResolverSerialization:
    """Tests that PolicyContext serializes correctly for MCP tool responses."""

    @pytest.mark.asyncio
    async def test_model_dump_omits_none_fields(self):
        resolver, _ = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        # IseResultModel drops None fields on serialization, matching the
        # exclude_none wire contract the policy tools have always emitted.
        dumped = result.model_dump(mode="json")
        assert "policy_set" in dumped
        assert "authorization_rule" in dumped
        assert "authentication_rule" not in dumped
        assert "resolution_errors" not in dumped

    @pytest.mark.asyncio
    async def test_full_context_json_roundtrip(self):
        resolver, _ = _build_resolver()

        result = await resolver.resolve(
            policy_set_name="Default",
            authn_rule_name="Default",
            authz_rule_name="Basic_Authenticated_Access",
        )

        json_str = json.dumps(result.model_dump(mode="json"))
        parsed = json.loads(json_str)
        assert parsed["policy_set"]["name"] == "Default"
        assert parsed["policy_set"]["condition_summary"] == "Wired_802.1X"
        assert parsed["authentication_rule"]["identity_source_name"] == "Internal Users"
        # condition_summary is None here, so it is omitted (exclude_none contract).
        assert "condition_summary" not in parsed["authentication_rule"]
        assert parsed["authorization_rule"]["profile"] == ["PermitAccess"]
        assert "condition_summary" in parsed["authorization_rule"]


class TestEnrichSessionsWithPolicyContext:
    """Tests for enrich_sessions_with_policy_context() orchestration."""

    ENRICHED_TWO_SESSIONS = EnrichedSessionSearchResult(
        search_filters={"minutes": 1440},
        total_sessions_found=2,
        actual_sessions_returned=2,
        sessions=[
            SessionDetail(
                user_name="testUser",
                ise_policy_set_name="Default",
                identity_policy_matched_rule="Default",
                authorization_policy_matched_rule="Basic_Authenticated_Access",
            ),
            SessionDetail(
                user_name="iseAiUser",
                ise_policy_set_name="Default",
                identity_policy_matched_rule="Default",
                authorization_policy_matched_rule="Basic_Authenticated_Access",
            ),
        ],
    )

    @pytest.mark.asyncio
    async def test_returns_sessions_with_policy_context(self):
        resolver, _ = _build_resolver()

        result = await resolver.enrich_sessions_with_policy_context(self.ENRICHED_TWO_SESSIONS)

        assert result.total_sessions_found == 2
        assert result.actual_sessions_returned == 2
        assert len(result.sessions) == 2
        for entry in result.sessions:
            assert entry.session is not None
            assert entry.policy_context is not None
            assert entry.policy_context.policy_set.name == "Default"

    @pytest.mark.asyncio
    async def test_policy_cache_avoids_duplicate_resolve_calls(self):
        """Two sessions with identical policy triple should trigger only one set of API calls."""
        resolver, handler = _build_resolver()

        await resolver.enrich_sessions_with_policy_context(self.ENRICHED_TWO_SESSIONS)

        handler.get_network_access_policy_set_list.assert_called_once()
        handler.get_network_access_authentication_rule_list.assert_called_once()
        handler.get_network_access_authorization_rule_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_without_policy_set_name_gets_note(self):
        enriched_no_policy = EnrichedSessionSearchResult(
            search_filters={},
            total_sessions_found=1,
            actual_sessions_returned=1,
            sessions=[
                SessionDetail(
                    user_name="noPolicy",
                    ise_policy_set_name=None,
                    identity_policy_matched_rule=None,
                    authorization_policy_matched_rule=None,
                ),
            ],
        )
        resolver, handler = _build_resolver()

        result = await resolver.enrich_sessions_with_policy_context(enriched_no_policy)

        assert result.actual_sessions_returned == 1
        entry = result.sessions[0]
        assert entry.policy_context is None
        assert entry.policy_context_note is not None
        handler.get_network_access_policy_set_list.assert_not_called()

    @pytest.mark.asyncio
    async def test_mixed_sessions_some_with_some_without_policy(self):
        enriched_mixed = EnrichedSessionSearchResult(
            search_filters={},
            total_sessions_found=2,
            actual_sessions_returned=2,
            sessions=[
                SessionDetail(
                    user_name="withPolicy",
                    ise_policy_set_name="Default",
                    identity_policy_matched_rule="Default",
                    authorization_policy_matched_rule="Basic_Authenticated_Access",
                ),
                SessionDetail(
                    user_name="noPolicy",
                    ise_policy_set_name=None,
                    identity_policy_matched_rule=None,
                    authorization_policy_matched_rule=None,
                ),
            ],
        )
        resolver, handler = _build_resolver()

        result = await resolver.enrich_sessions_with_policy_context(enriched_mixed)

        assert result.actual_sessions_returned == 2
        assert result.sessions[0].policy_context is not None
        assert result.sessions[0].policy_context.policy_set.name == "Default"
        assert result.sessions[1].policy_context is None
        assert result.sessions[1].policy_context_note is not None

    @pytest.mark.asyncio
    async def test_different_policy_triples_resolve_separately(self):
        enriched_different = EnrichedSessionSearchResult(
            search_filters={},
            total_sessions_found=2,
            actual_sessions_returned=2,
            sessions=[
                SessionDetail(
                    user_name="user1",
                    ise_policy_set_name="Default",
                    identity_policy_matched_rule="Default",
                    authorization_policy_matched_rule="Basic_Authenticated_Access",
                ),
                SessionDetail(
                    user_name="user2",
                    ise_policy_set_name="Wired_MAB",
                    identity_policy_matched_rule="MAB_Rule",
                    authorization_policy_matched_rule="Deny_Access",
                ),
            ],
        )
        resolver, handler = _build_resolver()

        result = await resolver.enrich_sessions_with_policy_context(enriched_different)

        assert result.actual_sessions_returned == 2
        assert result.sessions[0].policy_context.policy_set.name == "Default"
        assert result.sessions[1].policy_context.policy_set.name == "Wired_MAB"
        assert handler.get_network_access_policy_set_list.call_count == 2

    @pytest.mark.asyncio
    async def test_empty_sessions_list(self):
        enriched_empty = EnrichedSessionSearchResult(
            search_filters={"minutes": 1440},
            total_sessions_found=0,
            actual_sessions_returned=0,
            sessions=[],
        )
        resolver, _ = _build_resolver()

        result = await resolver.enrich_sessions_with_policy_context(enriched_empty)

        assert result.total_sessions_found == 0
        assert result.actual_sessions_returned == 0
        assert result.sessions == []


class TestConditionToSummary:
    """Unit tests for the condition_to_summary() helper."""

    def test_none_returns_none(self):
        assert condition_to_summary(None) is None

    def test_empty_dict_returns_none(self):
        assert condition_to_summary({}) is None

    def test_simple_attribute_condition(self):
        cond = {
            "conditionType": "ConditionAttributes",
            "isNegate": False,
            "dictionaryName": "Network Access",
            "attributeName": "Device IP Address",
            "operator": "ipEquals",
            "attributeValue": "10.0.10.0",
        }
        assert condition_to_summary(cond) == "Network Access:Device IP Address ipEquals 10.0.10.0"

    def test_library_attribute_condition(self):
        cond = {
            "conditionType": "LibraryConditionAttributes",
            "isNegate": False,
            "dictionaryName": "Radius",
            "attributeName": "Service-Type",
            "operator": "equals",
            "attributeValue": "Call Check",
        }
        assert condition_to_summary(cond) == "Radius:Service-Type equals Call Check"

    def test_condition_reference_by_name(self):
        cond = {
            "conditionType": "ConditionReference",
            "isNegate": False,
            "name": "Wired_802.1X",
            "id": "19d968b0-ebcb-4cdd-98e3-fe02e5521266",
        }
        assert condition_to_summary(cond) == "Wired_802.1X"

    def test_condition_reference_falls_back_to_id(self):
        cond = {
            "conditionType": "ConditionReference",
            "isNegate": False,
            "id": "19d968b0-ebcb-4cdd-98e3-fe02e5521266",
        }
        assert condition_to_summary(cond) == "19d968b0-ebcb-4cdd-98e3-fe02e5521266"

    def test_dictionary_value_prefixed_to_attribute_value(self):
        cond = {
            "conditionType": "ConditionAttributes",
            "isNegate": False,
            "dictionaryName": "Radius",
            "attributeName": "Service-Type",
            "operator": "equals",
            "attributeValue": "2",
            "dictionaryValue": "Framed",
        }
        assert condition_to_summary(cond) == "Radius:Service-Type equals Framed:2"

    def test_dictionary_value_absent_uses_attribute_value_only(self):
        cond = {
            "conditionType": "ConditionAttributes",
            "isNegate": False,
            "dictionaryName": "Network Access",
            "attributeName": "Device IP Address",
            "operator": "ipEquals",
            "attributeValue": "10.0.10.0",
        }
        assert condition_to_summary(cond) == "Network Access:Device IP Address ipEquals 10.0.10.0"

    def test_negated_attribute(self):
        cond = {
            "conditionType": "ConditionAttributes",
            "isNegate": True,
            "dictionaryName": "Network Access",
            "attributeName": "EapAuthentication",
            "operator": "equals",
            "attributeValue": "EAP-TLS",
        }
        assert condition_to_summary(cond) == "NOT Network Access:EapAuthentication equals EAP-TLS"

    def test_negated_reference(self):
        cond = {
            "conditionType": "ConditionReference",
            "isNegate": True,
            "name": "Wired_MAB",
            "id": "abc-123",
        }
        assert condition_to_summary(cond) == "NOT Wired_MAB"

    def test_and_block(self):
        cond = {
            "conditionType": "ConditionAndBlock",
            "isNegate": False,
            "children": [
                {
                    "conditionType": "ConditionAttributes",
                    "isNegate": False,
                    "dictionaryName": "Network Access",
                    "attributeName": "Device IP Address",
                    "operator": "ipEquals",
                    "attributeValue": "10.0.10.0",
                },
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "Wired_802.1X",
                    "id": "19d968b0-ebcb-4cdd-98e3-fe02e5521266",
                },
            ],
        }
        result = condition_to_summary(cond)
        assert result == "Network Access:Device IP Address ipEquals 10.0.10.0 AND Wired_802.1X"

    def test_or_block(self):
        cond = {
            "conditionType": "ConditionOrBlock",
            "isNegate": False,
            "children": [
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "Wired_802.1X",
                    "id": "aaa",
                },
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "Wireless_802.1X",
                    "id": "bbb",
                },
            ],
        }
        assert condition_to_summary(cond) == "Wired_802.1X OR Wireless_802.1X"

    def test_nested_blocks_get_parenthesized(self):
        cond = {
            "conditionType": "ConditionOrBlock",
            "isNegate": False,
            "children": [
                {
                    "conditionType": "ConditionAndBlock",
                    "isNegate": False,
                    "children": [
                        {
                            "conditionType": "ConditionReference",
                            "isNegate": False,
                            "name": "A",
                            "id": "1",
                        },
                        {
                            "conditionType": "ConditionReference",
                            "isNegate": False,
                            "name": "B",
                            "id": "2",
                        },
                    ],
                },
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "C",
                    "id": "3",
                },
            ],
        }
        assert condition_to_summary(cond) == "(A AND B) OR C"

    def test_negated_and_block(self):
        cond = {
            "conditionType": "ConditionAndBlock",
            "isNegate": True,
            "children": [
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "A",
                    "id": "1",
                },
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "B",
                    "id": "2",
                },
            ],
        }
        assert condition_to_summary(cond) == "NOT (A AND B)"

    def test_time_and_date_condition(self):
        cond = {
            "conditionType": "TimeAndDateCondition",
            "isNegate": False,
        }
        assert condition_to_summary(cond) == "TimeAndDate condition"

    def test_empty_children_returns_none(self):
        cond = {
            "conditionType": "ConditionAndBlock",
            "isNegate": False,
            "children": [],
        }
        assert condition_to_summary(cond) is None

    def test_library_and_block(self):
        cond = {
            "conditionType": "LibraryConditionAndBlock",
            "isNegate": False,
            "children": [
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "X",
                    "id": "1",
                },
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "Y",
                    "id": "2",
                },
            ],
        }
        assert condition_to_summary(cond) == "X AND Y"

    def test_library_or_block(self):
        cond = {
            "conditionType": "LibraryConditionOrBlock",
            "isNegate": False,
            "children": [
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "X",
                    "id": "1",
                },
                {
                    "conditionType": "ConditionReference",
                    "isNegate": False,
                    "name": "Y",
                    "id": "2",
                },
            ],
        }
        assert condition_to_summary(cond) == "X OR Y"
