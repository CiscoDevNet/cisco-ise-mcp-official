# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for the seven policy MCP tools (PolicyToolHandler).

Coverage per tool: happy path, validator rejection, empty upstream, truncation
+ has_more, upstream API error propagation, and the tool-specific behaviours
(name resolution, fan-out cap, global exception always returned, etc.).
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastmcp.exceptions import ToolError as McpToolError

from models.policy_models import (
    AuthenticationRuleSearchResult,
    AuthorizationProfileSearchResult,
    AuthorizationRuleSearchResult,
    LibraryConditionSearchResult,
    PolicyAuthoringReferencesResult,
    PolicySetDetailsResult,
    PolicySetSearchResult,
)
from tools.policy_tool_handler import PolicyToolHandler


# ---------------------------------------------------------------------------
# Test helpers / fixtures
# ---------------------------------------------------------------------------

def _make_handler() -> PolicyToolHandler:
    """Build a handler whose underlying ISE client factory is never used —
    every test below replaces the granular ``get_*`` methods with AsyncMocks.
    """
    return PolicyToolHandler(MagicMock())


def _wrap_response(payload: list[dict]) -> dict:
    """Wrap a list of raw items in the ISE ``{"version": ..., "response": [...]}`` envelope.

    Used by tests that drive ``execute_api_call`` directly. Tests that
    short-circuit at the granular handler-method level pass the unwrapped
    list directly.
    """
    return {"version": "1.0.0", "response": payload}


def _ps(
    *,
    id_: str,
    name: str,
    rank: int = 0,
    state: str = "enabled",
    is_default: bool = False,
    hit_counts: int = 0,
    service_name: str = "Default Network Access",
    is_proxy: bool = False,
    description: str | None = None,
    condition: dict | None = None,
) -> dict:
    return {
        "id": id_,
        "name": name,
        "description": description,
        "rank": rank,
        "state": state,
        "default": is_default,
        "hitCounts": hit_counts,
        "serviceName": service_name,
        "isProxy": is_proxy,
        "condition": condition,
    }


def _authz_rule(
    *,
    id_: str,
    name: str,
    rank: int = 0,
    state: str = "enabled",
    hit_counts: int = 0,
    profile: list[str] | None = None,
    security_group: str | None = None,
    condition: dict | None = None,
) -> dict:
    return {
        "rule": {
            "id": id_,
            "name": name,
            "rank": rank,
            "state": state,
            "hitCounts": hit_counts,
            "condition": condition,
        },
        "profile": profile or ["PermitAccess"],
        "securityGroup": security_group,
    }


def _authn_rule(
    *,
    id_: str,
    name: str,
    rank: int = 0,
    state: str = "enabled",
    hit_counts: int = 0,
    identity_source_name: str = "Internal Users",
    if_auth_fail: str = "REJECT",
    if_user_not_found: str = "REJECT",
    if_process_fail: str = "DROP",
    condition: dict | None = None,
) -> dict:
    return {
        "rule": {
            "id": id_,
            "name": name,
            "rank": rank,
            "state": state,
            "hitCounts": hit_counts,
            "condition": condition,
        },
        "identitySourceName": identity_source_name,
        "ifAuthFail": if_auth_fail,
        "ifUserNotFound": if_user_not_found,
        "ifProcessFail": if_process_fail,
    }


SAMPLE_PROTOCOL_CONDITION = {
    "conditionType": "ConditionAttributes",
    "isNegate": False,
    "dictionaryName": "Network Access",
    "attributeName": "Protocol",
    "operator": "equals",
    "attributeValue": "RADIUS",
}


# ===========================================================================
# Tool 1 — ise_search_policy_sets
# ===========================================================================


class TestSearchPolicySets:

    @pytest.mark.asyncio
    async def test_happy_path_returns_sorted_by_rank(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="b", name="WiredMAB", rank=2),
            _ps(id_="a", name="Default", rank=0, is_default=True, condition=SAMPLE_PROTOCOL_CONDITION),
            _ps(id_="c", name="GuestAccess", rank=1, state="disabled"),
        ])

        result = await handler.search_policy_sets()

        assert isinstance(result, PolicySetSearchResult)
        assert result.total_count == 3
        assert result.count == 3
        assert result.has_more is False
        names = [p.name for p in result.policy_sets]
        assert names == ["Default", "GuestAccess", "WiredMAB"]
        # condition_summary populated for the one with a condition
        assert result.policy_sets[0].condition_summary is not None
        # Default flag and state populated
        assert result.policy_sets[0].is_default is True
        assert result.policy_sets[1].state == "disabled"

    @pytest.mark.asyncio
    async def test_state_filter_excludes_other_states(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="a", name="A", state="enabled"),
            _ps(id_="b", name="B", state="disabled"),
            _ps(id_="c", name="C", state="monitor"),
        ])

        result = await handler.search_policy_sets(state_filter="enabled")

        assert [p.name for p in result.policy_sets] == ["A"]
        assert result.search_filters["state_filter"] == "enabled"

    @pytest.mark.asyncio
    async def test_name_substring_is_case_insensitive(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="a", name="Wired_802.1X"),
            _ps(id_="b", name="WIRELESS"),
            _ps(id_="c", name="VpnAccess"),
        ])

        result = await handler.search_policy_sets(name_substring="wir")

        assert sorted(p.name for p in result.policy_sets) == ["WIRELESS", "Wired_802.1X"]

    @pytest.mark.asyncio
    async def test_truncation_sets_has_more(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_=str(i), name=f"PS{i}", rank=i) for i in range(5)
        ])

        result = await handler.search_policy_sets(limit=2)

        assert result.total_count == 5
        assert result.count == 2
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_empty_upstream_returns_zero_results(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[])

        result = await handler.search_policy_sets()

        assert result.total_count == 0
        assert result.count == 0
        assert result.has_more is False
        assert result.policy_sets == []

    @pytest.mark.asyncio
    async def test_invalid_state_filter_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_policy_sets(state_filter="active")
        assert "INVALID_STATE_FILTER" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_limit_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.search_policy_sets(limit=0)
        with pytest.raises(McpToolError):
            await handler.search_policy_sets(limit=101)

    @pytest.mark.asyncio
    async def test_invalid_name_substring_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.search_policy_sets(name_substring="<bad>")

    @pytest.mark.asyncio
    async def test_max_hit_counts_zero_returns_only_zero_hit_sets(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="a", name="StaleA", rank=2, hit_counts=0),
            _ps(id_="b", name="Hot", rank=0, hit_counts=42),
            _ps(id_="c", name="StaleB", rank=1, hit_counts=0),
        ])

        result = await handler.search_policy_sets(max_hit_counts=0)

        # Sorted by rank ascending, only zero-hit sets retained.
        assert [p.name for p in result.policy_sets] == ["StaleB", "StaleA"]
        assert result.total_count == 2
        assert result.search_filters["max_hit_counts"] == 0
        assert "min_hit_counts" not in result.search_filters

    @pytest.mark.asyncio
    async def test_min_hit_counts_excludes_zero_hit_sets(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="a", name="Stale", rank=0, hit_counts=0),
            _ps(id_="b", name="Used", rank=1, hit_counts=5),
        ])

        result = await handler.search_policy_sets(min_hit_counts=1)

        assert [p.name for p in result.policy_sets] == ["Used"]
        assert result.search_filters["min_hit_counts"] == 1

    @pytest.mark.asyncio
    async def test_min_and_max_hit_counts_combined(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="a", name="Zero", rank=0, hit_counts=0),
            _ps(id_="b", name="One", rank=1, hit_counts=1),
            _ps(id_="c", name="Two", rank=2, hit_counts=2),
            _ps(id_="d", name="Ten", rank=3, hit_counts=10),
        ])

        result = await handler.search_policy_sets(min_hit_counts=1, max_hit_counts=2)

        assert [p.name for p in result.policy_sets] == ["One", "Two"]
        assert result.search_filters["min_hit_counts"] == 1
        assert result.search_filters["max_hit_counts"] == 2

    @pytest.mark.asyncio
    async def test_missing_hit_counts_treated_as_zero(self):
        handler = _make_handler()
        raw = _ps(id_="a", name="NoHits", rank=0)
        raw["hitCounts"] = None
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[raw])

        result = await handler.search_policy_sets(max_hit_counts=0)
        assert [p.name for p in result.policy_sets] == ["NoHits"]

        result_excluded = await handler.search_policy_sets(min_hit_counts=1)
        assert result_excluded.policy_sets == []

    @pytest.mark.asyncio
    async def test_negative_min_hit_counts_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_policy_sets(min_hit_counts=-1)
        assert "INVALID_MIN_HIT_COUNTS" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_negative_max_hit_counts_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_policy_sets(max_hit_counts=-1)
        assert "INVALID_MAX_HIT_COUNTS" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_min_greater_than_max_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_policy_sets(min_hit_counts=5, max_hit_counts=2)
        assert "INVALID_HIT_COUNT_RANGE" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upstream_api_error_propagates(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(
            side_effect=McpToolError('{"error_code": "ISE_API_ERROR"}')
        )
        with pytest.raises(McpToolError):
            await handler.search_policy_sets()


# ===========================================================================
# Tool 2 — ise_get_policy_set_details
# ===========================================================================


class TestGetPolicySetDetails:

    def _setup_handler(
        self,
        *,
        policy_sets: list[dict],
        ps_detail: dict | None = None,
        authn_rules: list[dict] | None = None,
        authz_rules: list[dict] | None = None,
        local_exc_rules: list[dict] | None = None,
    ) -> PolicyToolHandler:
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=policy_sets)
        # The by-id endpoint may or may not wrap under "response"; the handler
        # falls back to the resolved list entry if the by-id response is empty.
        handler.get_network_access_policy_set_by_id = AsyncMock(
            return_value=ps_detail if ps_detail is not None else (policy_sets[0] if policy_sets else {})
        )
        handler.get_network_access_authentication_rule_list = AsyncMock(return_value=authn_rules or [])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=authz_rules or [])
        handler.get_network_access_local_exception_rule_list = AsyncMock(return_value=local_exc_rules or [])
        return handler

    @pytest.mark.asyncio
    async def test_happy_path_resolves_by_name_and_returns_full_tree(self):
        ps = _ps(id_="ps-1", name="Default", is_default=True, condition=SAMPLE_PROTOCOL_CONDITION)
        handler = self._setup_handler(
            policy_sets=[ps],
            authn_rules=[
                _authn_rule(id_="r2", name="MAB_Rule", rank=2),
                _authn_rule(id_="r1", name="Default", rank=1),
            ],
            authz_rules=[
                _authz_rule(id_="r1", name="Default", rank=10, profile=["DenyAccess"]),
            ],
            local_exc_rules=[
                _authz_rule(id_="le1", name="Local_Override", rank=0, profile=["PermitAccess"]),
            ],
        )

        result = await handler.get_policy_set_details(policy_set_name="Default")

        assert isinstance(result, PolicySetDetailsResult)
        assert result.policy_set.name == "Default"
        assert result.policy_set.is_default is True
        # Authn rules sorted by rank ascending
        assert [r.name for r in result.authentication_rules.rules] == ["Default", "MAB_Rule"]
        assert result.authentication_rules.total_count == 2
        assert result.authentication_rules.has_more is False
        assert result.authorization_rules.rules[0].profile == ["DenyAccess"]
        assert result.local_exception_rules.rules[0].name == "Local_Override"
        # Steering note present
        assert "BEFORE" in result.local_exception_rules.note

    @pytest.mark.asyncio
    async def test_unknown_policy_set_raises_not_found(self):
        handler = self._setup_handler(policy_sets=[_ps(id_="ps-1", name="OtherName")])
        with pytest.raises(McpToolError) as exc_info:
            await handler.get_policy_set_details(policy_set_name="MissingName")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "POLICY_SET_NOT_FOUND"
        assert "ise_search_policy_sets" in data["message"]
        assert data["retry"] is False

    @pytest.mark.asyncio
    async def test_section_truncation_sets_has_more(self):
        ps = _ps(id_="ps-1", name="Default")
        many_authz = [
            _authz_rule(id_=f"r{i}", name=f"Rule_{i}", rank=i) for i in range(15)
        ]
        handler = self._setup_handler(policy_sets=[ps], authz_rules=many_authz)

        result = await handler.get_policy_set_details(policy_set_name="Default", rules_per_section_limit=5)

        assert result.authorization_rules.total_count == 15
        assert result.authorization_rules.count == 5
        assert result.authorization_rules.has_more is True

    @pytest.mark.asyncio
    async def test_invalid_policy_set_name_raises_validator_error(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.get_policy_set_details(policy_set_name="bad:name")

    @pytest.mark.asyncio
    async def test_invalid_section_limit_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.get_policy_set_details(policy_set_name="Default", rules_per_section_limit=26)

    @pytest.mark.asyncio
    async def test_parallel_detail_fetch_invoked(self):
        """The four detail endpoints should all be invoked exactly once."""
        ps = _ps(id_="ps-1", name="Default")
        handler = self._setup_handler(policy_sets=[ps])

        await handler.get_policy_set_details(policy_set_name="Default")

        handler.get_network_access_policy_set_by_id.assert_awaited_once()
        handler.get_network_access_authentication_rule_list.assert_awaited_once()
        handler.get_network_access_authorization_rule_list.assert_awaited_once()
        handler.get_network_access_local_exception_rule_list.assert_awaited_once()


# ===========================================================================
# Tool 3 — ise_search_authorization_rules
# ===========================================================================


class TestSearchAuthorizationRules:

    @pytest.mark.asyncio
    async def test_global_exceptions_always_returned(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="ps-1", name="Default"),
        ])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="r1", name="Default", profile=["PermitAccess"]),
        ])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="g1", name="GlobalDeny", profile=["DenyAccess"]),
        ])

        result = await handler.search_authorization_rules()

        assert isinstance(result, AuthorizationRuleSearchResult)
        assert len(result.rules) == 1
        assert result.rules[0].policy_set_name == "Default"
        assert len(result.global_exceptions) == 1
        assert result.global_exceptions[0].policy_set_name is None
        assert result.global_exceptions[0].name == "GlobalDeny"
        assert "override" in result.global_exceptions_note.lower()

    @pytest.mark.asyncio
    async def test_profile_filter_applied_to_both_lists(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="ps-1", name="Default"),
        ])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="r1", name="PermitRule", profile=["PermitAccess"]),
            _authz_rule(id_="r2", name="DenyRule", profile=["DenyAccess"]),
        ])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="g1", name="GlobalDeny", profile=["DenyAccess"]),
            _authz_rule(id_="g2", name="GlobalPermit", profile=["PermitAccess"]),
        ])

        result = await handler.search_authorization_rules(profile_name_filter="Deny")

        assert {r.name for r in result.rules} == {"DenyRule"}
        assert {r.name for r in result.global_exceptions} == {"GlobalDeny"}

    @pytest.mark.asyncio
    async def test_state_and_min_hit_counts_filters(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="ps-1", name="Default"),
        ])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="r1", name="ActiveRule", state="enabled", hit_counts=10),
            _authz_rule(id_="r2", name="DisabledRule", state="disabled", hit_counts=10),
            _authz_rule(id_="r3", name="UnusedRule", state="enabled", hit_counts=0),
        ])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[])

        # Find unused rules across all states
        result = await handler.search_authorization_rules(min_hit_counts=0, state_filter="all")
        assert {r.name for r in result.rules} == {"ActiveRule", "DisabledRule", "UnusedRule"}

        # Only enabled rules with at least one hit
        result = await handler.search_authorization_rules(min_hit_counts=1, state_filter="enabled")
        assert {r.name for r in result.rules} == {"ActiveRule"}

    @pytest.mark.asyncio
    async def test_security_group_filter(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[_ps(id_="ps-1", name="Default")])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="r1", name="EmpRule", security_group="Employee"),
            _authz_rule(id_="r2", name="GuestRule", security_group="Guest"),
        ])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[])

        result = await handler.search_authorization_rules(security_group_filter="emp")

        assert [r.name for r in result.rules] == ["EmpRule"]

    @pytest.mark.asyncio
    async def test_policy_set_name_scopes_search(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="ps-1", name="Default"),
            _ps(id_="ps-2", name="Wireless"),
        ])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="r1", name="OnlyRule"),
        ])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[])

        await handler.search_authorization_rules(policy_set_name="Default")

        # Should be called only once (for the resolved Default policy set)
        assert handler.get_network_access_authorization_rule_list.await_count == 1

    @pytest.mark.asyncio
    async def test_unknown_policy_set_name_raises(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="ps-1", name="Default"),
        ])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[])

        with pytest.raises(McpToolError) as exc_info:
            await handler.search_authorization_rules(policy_set_name="Missing")
        assert "POLICY_SET_NOT_FOUND" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_truncation_sets_has_more(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[_ps(id_="ps-1", name="Default")])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[
            _authz_rule(id_=f"r{i}", name=f"Rule_{i}") for i in range(30)
        ])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[])

        result = await handler.search_authorization_rules(limit=10)

        assert result.total_count == 30
        assert result.count == 10
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_empty_upstream_returns_zero(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[])

        result = await handler.search_authorization_rules()

        assert result.total_count == 0
        assert result.policy_sets_scanned == 0
        assert result.rules == []
        assert result.global_exceptions == []

    @pytest.mark.asyncio
    async def test_invalid_filter_raises(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.search_authorization_rules(state_filter="bogus")
        with pytest.raises(McpToolError):
            await handler.search_authorization_rules(min_hit_counts=-1)


# ===========================================================================
# Tool 4 — ise_search_authentication_rules
# ===========================================================================


class TestSearchAuthenticationRules:

    @pytest.mark.asyncio
    async def test_identity_source_filter(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="ps-1", name="Default"),
        ])
        handler.get_network_access_authentication_rule_list = AsyncMock(return_value=[
            _authn_rule(id_="r1", name="ADRule", identity_source_name="AD:corp.example.com"),
            _authn_rule(id_="r2", name="InternalRule", identity_source_name="Internal Users"),
        ])

        result = await handler.search_authentication_rules(identity_source_filter="ad")

        assert isinstance(result, AuthenticationRuleSearchResult)
        assert [r.name for r in result.rules] == ["ADRule"]
        assert result.rules[0].if_user_not_found == "REJECT"
        assert result.rules[0].policy_set_name == "Default"

    @pytest.mark.asyncio
    async def test_lenient_rule_fields_returned(self):
        """The if_* fields are surfaced raw so the SLM can identify CONTINUE-on-not-found."""
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[_ps(id_="ps-1", name="Default")])
        handler.get_network_access_authentication_rule_list = AsyncMock(return_value=[
            _authn_rule(id_="r1", name="LenientRule", if_user_not_found="CONTINUE"),
        ])

        result = await handler.search_authentication_rules()

        assert result.rules[0].if_user_not_found == "CONTINUE"

    @pytest.mark.asyncio
    async def test_truncation_sets_has_more(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[_ps(id_="ps-1", name="Default")])
        handler.get_network_access_authentication_rule_list = AsyncMock(return_value=[
            _authn_rule(id_=f"r{i}", name=f"R{i}") for i in range(8)
        ])

        result = await handler.search_authentication_rules(limit=3)

        assert result.total_count == 8
        assert result.count == 3
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_empty_upstream(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[])
        result = await handler.search_authentication_rules()
        assert result.total_count == 0

    @pytest.mark.asyncio
    async def test_invalid_state_filter(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.search_authentication_rules(state_filter="monitor")


# ===========================================================================
# Tool 5 — ise_search_authorization_profiles
# ===========================================================================


class TestSearchAuthorizationProfiles:

    @pytest.mark.asyncio
    async def test_happy_path_sorted_by_name(self):
        handler = _make_handler()
        handler.get_network_access_authorization_profiles = AsyncMock(return_value=[
            {"id": "p1", "name": "PermitAccess"},
            {"id": "p2", "name": "DenyAccess", "description": "Block"},
            {"id": "p3", "name": "Guest_Redirect"},
        ])

        result = await handler.search_authorization_profiles()

        assert isinstance(result, AuthorizationProfileSearchResult)
        assert [p.name for p in result.profiles] == ["DenyAccess", "Guest_Redirect", "PermitAccess"]
        # IDs are not exposed
        assert all(not hasattr(p, "id") or getattr(p, "id", None) is None for p in result.profiles)
        # Description present when provided
        assert result.profiles[0].description == "Block"

    @pytest.mark.asyncio
    async def test_name_substring_filter(self):
        handler = _make_handler()
        handler.get_network_access_authorization_profiles = AsyncMock(return_value=[
            {"name": "PermitAccess"},
            {"name": "DenyAccess"},
            {"name": "Guest_Redirect"},
        ])

        result = await handler.search_authorization_profiles(name_substring="guest")

        assert [p.name for p in result.profiles] == ["Guest_Redirect"]

    @pytest.mark.asyncio
    async def test_truncation(self):
        handler = _make_handler()
        handler.get_network_access_authorization_profiles = AsyncMock(return_value=[
            {"name": f"Profile_{i:02d}"} for i in range(10)
        ])

        result = await handler.search_authorization_profiles(limit=4)

        assert result.total_count == 10
        assert result.count == 4
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_empty_upstream(self):
        handler = _make_handler()
        handler.get_network_access_authorization_profiles = AsyncMock(return_value=[])

        result = await handler.search_authorization_profiles()

        assert result.total_count == 0
        assert result.profiles == []

    @pytest.mark.asyncio
    async def test_invalid_limit(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.search_authorization_profiles(limit=201)


# ===========================================================================
# Tool 6 — ise_search_library_conditions
# ===========================================================================


class TestSearchLibraryConditions:

    @pytest.mark.asyncio
    async def test_happy_path_resolves_summary(self):
        handler = _make_handler()
        handler.get_network_access_library_conditions = AsyncMock(return_value=[
            {
                "id": "c1",
                "name": "Wired_802.1X",
                "description": "802.1X over wired",
                "conditionType": "ConditionAttributes",
                "isNegate": False,
                "dictionaryName": "Network Access",
                "attributeName": "Protocol",
                "operator": "equals",
                "attributeValue": "RADIUS",
            },
        ])

        result = await handler.search_library_conditions()

        assert isinstance(result, LibraryConditionSearchResult)
        assert result.conditions[0].name == "Wired_802.1X"
        assert result.conditions[0].condition_summary == "Network Access:Protocol equals RADIUS"

    @pytest.mark.asyncio
    async def test_scope_filter_passes_through(self):
        handler = _make_handler()
        handler.get_network_access_library_conditions = AsyncMock(return_value=[])

        await handler.search_library_conditions(scope_filter="authentication")

        handler.get_network_access_library_conditions.assert_awaited_once_with(scope="authentication")

    @pytest.mark.asyncio
    async def test_invalid_scope_filter(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.search_library_conditions(scope_filter="rule")

    @pytest.mark.asyncio
    async def test_truncation(self):
        handler = _make_handler()
        handler.get_network_access_library_conditions = AsyncMock(return_value=[
            {"name": f"Cond_{i:02d}", "conditionType": "ConditionReference"} for i in range(8)
        ])

        result = await handler.search_library_conditions(limit=3)

        assert result.total_count == 8
        assert result.count == 3
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_empty_upstream(self):
        handler = _make_handler()
        handler.get_network_access_library_conditions = AsyncMock(return_value=[])
        result = await handler.search_library_conditions()
        assert result.total_count == 0


# ===========================================================================
# Tool 7 — ise_list_policy_authoring_references
# ===========================================================================


class TestListPolicyAuthoringReferences:

    @pytest.mark.asyncio
    async def test_happy_path_returns_three_sections(self):
        handler = _make_handler()
        handler.get_network_access_identity_stores = AsyncMock(return_value=[
            {"id": "i1", "name": "Internal Users"},
            {"id": "i2", "name": "AD:corp.example.com"},
        ])
        handler.get_network_access_security_groups = AsyncMock(return_value=[
            {"id": "s1", "name": "Employee"},
            {"id": "s2", "name": "Guest"},
        ])
        handler.get_network_access_service_names = AsyncMock(return_value=[
            {"id": "sv1", "name": "Default Network Access", "serviceType": "Allowed Protocols"},
            {"id": "sv2", "name": "MAB_Sequence", "serviceType": "Server Sequence", "isLocalAuthorization": True},
        ])

        result = await handler.list_policy_authoring_references()

        assert isinstance(result, PolicyAuthoringReferencesResult)
        assert {i.name for i in result.identity_stores.items} == {"Internal Users", "AD:corp.example.com"}
        assert {g.name for g in result.security_groups.items} == {"Employee", "Guest"}
        names_to_type = {s.name: s.service_type for s in result.service_names.items}
        assert names_to_type == {
            "Default Network Access": "allowed_protocols",
            "MAB_Sequence": "server_sequence",
        }
        # is_local_authorization is preserved when present
        for s in result.service_names.items:
            if s.name == "MAB_Sequence":
                assert s.is_local_authorization is True

    @pytest.mark.asyncio
    async def test_substring_filter_applies_to_all_sections(self):
        handler = _make_handler()
        handler.get_network_access_identity_stores = AsyncMock(return_value=[
            {"name": "Internal Users"},
            {"name": "AD:corp"},
        ])
        handler.get_network_access_security_groups = AsyncMock(return_value=[
            {"name": "Employee"},
            {"name": "Internal_Group"},
        ])
        handler.get_network_access_service_names = AsyncMock(return_value=[
            {"name": "Internal_Sequence", "serviceType": "Server Sequence"},
            {"name": "Default Network Access", "serviceType": "Allowed Protocols"},
        ])

        result = await handler.list_policy_authoring_references(name_substring="internal")

        assert [i.name for i in result.identity_stores.items] == ["Internal Users"]
        assert [g.name for g in result.security_groups.items] == ["Internal_Group"]
        assert [s.name for s in result.service_names.items] == ["Internal_Sequence"]

    @pytest.mark.asyncio
    async def test_section_truncation(self):
        handler = _make_handler()
        handler.get_network_access_identity_stores = AsyncMock(return_value=[
            {"name": f"Store_{i:02d}"} for i in range(8)
        ])
        handler.get_network_access_security_groups = AsyncMock(return_value=[])
        handler.get_network_access_service_names = AsyncMock(return_value=[])

        result = await handler.list_policy_authoring_references(limit_per_section=3)

        assert result.identity_stores.total_count == 8
        assert result.identity_stores.count == 3
        assert result.identity_stores.has_more is True
        assert result.security_groups.total_count == 0
        assert result.security_groups.has_more is False

    @pytest.mark.asyncio
    async def test_empty_upstream_all_sections(self):
        handler = _make_handler()
        handler.get_network_access_identity_stores = AsyncMock(return_value=[])
        handler.get_network_access_security_groups = AsyncMock(return_value=[])
        handler.get_network_access_service_names = AsyncMock(return_value=[])

        result = await handler.list_policy_authoring_references()

        for section in (result.identity_stores, result.security_groups, result.service_names):
            assert section.total_count == 0
            assert section.has_more is False
            assert section.items == []

    @pytest.mark.asyncio
    async def test_invalid_limit(self):
        handler = _make_handler()
        with pytest.raises(McpToolError):
            await handler.list_policy_authoring_references(limit_per_section=0)


# ===========================================================================
# Cross-cutting: name-only output contract
# ===========================================================================


class TestNameOnlyOutputContract:
    """Verify that no Pydantic output model exposes any *_id field. UUIDs from
    upstream ISE must never reach the SLM."""

    @pytest.mark.asyncio
    async def test_search_policy_sets_has_no_id_field(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[
            _ps(id_="should-not-leak", name="Default"),
        ])
        result = await handler.search_policy_sets()
        dumped = json.loads(result.model_dump_json(exclude_none=True))
        assert "should-not-leak" not in json.dumps(dumped)
        assert "id" not in dumped["policy_sets"][0]
        assert "policy_set_id" not in dumped["policy_sets"][0]

    @pytest.mark.asyncio
    async def test_authz_search_has_no_id_fields(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[_ps(id_="ps-1", name="Default")])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[
            _authz_rule(id_="rule-uuid", name="Rule1"),
        ])
        handler.get_network_access_global_exception_rule_list = AsyncMock(return_value=[])

        result = await handler.search_authorization_rules()
        dumped = json.loads(result.model_dump_json(exclude_none=True))
        text = json.dumps(dumped)
        assert "rule-uuid" not in text
        assert "ps-1" not in text
        assert "rule_id" not in text
        assert "policy_set_id" not in text

    @pytest.mark.asyncio
    async def test_profiles_have_no_id(self):
        handler = _make_handler()
        handler.get_network_access_authorization_profiles = AsyncMock(return_value=[
            {"id": "should-not-leak", "name": "PermitAccess"},
        ])
        result = await handler.search_authorization_profiles()
        dumped = json.loads(result.model_dump_json(exclude_none=True))
        assert "should-not-leak" not in json.dumps(dumped)
        assert "id" not in dumped["profiles"][0]
        assert "profile_id" not in dumped["profiles"][0]

    @pytest.mark.asyncio
    async def test_conditions_have_no_id(self):
        handler = _make_handler()
        handler.get_network_access_library_conditions = AsyncMock(return_value=[
            {"id": "cond-uuid", "name": "Wired", "conditionType": "ConditionReference"},
        ])
        result = await handler.search_library_conditions()
        dumped = json.loads(result.model_dump_json(exclude_none=True))
        assert "cond-uuid" not in json.dumps(dumped)
        assert "id" not in dumped["conditions"][0]
        assert "condition_id" not in dumped["conditions"][0]

    @pytest.mark.asyncio
    async def test_authoring_references_have_no_ids(self):
        handler = _make_handler()
        handler.get_network_access_identity_stores = AsyncMock(return_value=[{"id": "i1", "name": "Internal Users"}])
        handler.get_network_access_security_groups = AsyncMock(return_value=[{"id": "s1", "name": "Employee"}])
        handler.get_network_access_service_names = AsyncMock(return_value=[
            {"id": "sv1", "name": "Default Network Access", "serviceType": "Allowed Protocols"},
        ])
        result = await handler.list_policy_authoring_references()
        text = result.model_dump_json(exclude_none=True)
        assert "i1" not in text
        assert "s1" not in text
        assert "sv1" not in text


# ===========================================================================
# API error propagation
# ===========================================================================


class TestApiErrorPropagation:

    @pytest.mark.asyncio
    async def test_5xx_propagates_from_search_policy_sets(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(
            side_effect=McpToolError(json.dumps({
                "error_category": "external_error",
                "error_code": "ISE_API_ERROR",
                "message": "ISE API returned HTTP 500",
                "retry": True,
            }))
        )
        with pytest.raises(McpToolError) as exc_info:
            await handler.search_policy_sets()
        data = json.loads(str(exc_info.value))
        assert data["error_category"] == "external_error"
        assert data["retry"] is True

    @pytest.mark.asyncio
    async def test_timeout_propagates_from_get_details(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(
            side_effect=McpToolError(json.dumps({
                "error_category": "external_error",
                "error_code": "ISE_UNREACHABLE",
                "message": "ISE API timed out",
                "retry": True,
            }))
        )
        with pytest.raises(McpToolError) as exc_info:
            await handler.get_policy_set_details(policy_set_name="Default")
        data = json.loads(str(exc_info.value))
        assert data["error_code"] == "ISE_UNREACHABLE"

    @pytest.mark.asyncio
    async def test_authorization_rules_propagates_global_exception_failure(self):
        handler = _make_handler()
        handler.get_network_access_policy_set_list = AsyncMock(return_value=[_ps(id_="ps-1", name="Default")])
        handler.get_network_access_authorization_rule_list = AsyncMock(return_value=[])
        handler.get_network_access_global_exception_rule_list = AsyncMock(
            side_effect=McpToolError('{"error_code": "ISE_API_ERROR"}')
        )
        with pytest.raises(McpToolError):
            await handler.search_authorization_rules()
