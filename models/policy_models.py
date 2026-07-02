# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


# ===========================================================================
# Building blocks (reused across multiple tools)
# ===========================================================================

class PolicySetSummary(BaseModel):
    """Summary of a network access policy set.

    Used as both:
    - the resolved-by-name container that PolicyContextResolver returns
      (only ``name``, ``description``, ``condition_summary`` are populated)
    - the search-result item returned by ``ise_search_policy_sets`` and the
      ``policy_set`` field of ``ise_get_policy_set_details`` (all fields populated)

    Outputs are name-only by contract — internal ISE UUIDs are stripped before
    serialization.
    """

    name: str = Field(..., description="Policy set name")
    description: Optional[str] = Field(None, description="Policy set description")
    state: Optional[Literal["enabled", "disabled", "monitor"]] = Field(
        None,
        description="Policy set state. A disabled policy set cannot be matched.",
    )
    rank: Optional[int] = Field(
        None,
        description="Rank/priority relative to other policy sets. Lower rank is higher priority (evaluated first).",
    )
    hit_counts: Optional[int] = Field(
        None,
        description="Number of times this policy set was matched.",
    )
    is_default: Optional[bool] = Field(
        None,
        description="True if this is the built-in default policy set.",
    )
    service_name: Optional[str] = Field(
        None,
        description="Allowed-protocols or server-sequence service identifier (e.g. 'Default Network Access').",
    )
    is_proxy: Optional[bool] = Field(
        None,
        description="True if the service identifier is a Proxy Sequence rather than Allowed Protocols.",
    )
    condition_summary: Optional[str] = Field(
        None,
        description="Human-readable summary of the top-level condition that selects this policy set.",
    )


class AuthenticationRuleSummary(BaseModel):
    """Summary of an authentication rule (within a single policy set)."""

    name: str = Field(..., description="Rule name")
    rank: Optional[int] = Field(
        None,
        description="Rank within the policy set. Lower rank evaluates first.",
    )
    state: Optional[Literal["enabled", "disabled", "monitor"]] = Field(
        None,
        description="Rule state. Disabled rules cannot be matched.",
    )
    hit_counts: Optional[int] = Field(
        None,
        description="Number of times this rule was matched.",
    )
    identity_source_name: Optional[str] = Field(
        None,
        description="Identity source the rule queries (e.g. 'Internal Users', AD join name).",
    )
    if_auth_fail: Optional[str] = Field(
        None,
        description="Action on authentication failure: REJECT, CONTINUE, or DROP.",
    )
    if_user_not_found: Optional[str] = Field(
        None,
        description="Action when the user is not found in the identity store.",
    )
    if_process_fail: Optional[str] = Field(
        None,
        description="Action when the identity store is unreachable.",
    )
    condition_summary: Optional[str] = Field(
        None,
        description="Human-readable summary of the rule's matching condition.",
    )


class AuthorizationRuleSummary(BaseModel):
    """Summary of an authorization rule (within a single policy set)."""

    name: str = Field(..., description="Rule name")
    rank: Optional[int] = Field(
        None,
        description="Rank within the policy set. Lower rank evaluates first.",
    )
    state: Optional[Literal["enabled", "disabled", "monitor"]] = Field(
        None,
        description="Rule state. Disabled rules cannot be matched.",
    )
    hit_counts: Optional[int] = Field(
        None,
        description="Number of times this rule was matched.",
    )
    profile: Optional[List[str]] = Field(
        None,
        description="Authorization profile names assigned by this rule.",
    )
    security_group: Optional[str] = Field(
        None,
        description="TrustSec security group (SGT) assigned, if any.",
    )
    condition_summary: Optional[str] = Field(
        None,
        description="Human-readable summary of the rule's matching condition.",
    )


class PolicyContext(BaseModel):
    """Full policy context resolved from the ISE Policy API by name.

    Used by the session-driven flow in PolicyContextResolver. Independent
    of the new policy-config-audit tools.
    """

    policy_set: Optional[PolicySetSummary] = Field(None, description="Resolved policy set details")
    authentication_rule: Optional[AuthenticationRuleSummary] = Field(None, description="Resolved authentication rule details")
    authorization_rule: Optional[AuthorizationRuleSummary] = Field(None, description="Resolved authorization rule details")
    resolution_errors: Optional[List[str]] = Field(None, description="Errors encountered during name-to-ID resolution")


# ===========================================================================
# Tool 1 — ise_search_policy_sets
# ===========================================================================

class PolicySetSearchResult(BaseModel):
    """Result envelope for ``ise_search_policy_sets``."""

    search_filters: Dict[str, Any] = Field(
        ...,
        description="Filters that were applied to the search (echoed for the agent).",
    )
    total_count: int = Field(
        ...,
        description="Total policy sets matching the filters before truncation by `limit`.",
    )
    count: int = Field(
        ...,
        description="Number of policy sets in `policy_sets` (after truncation).",
    )
    has_more: bool = Field(
        ...,
        description="True when `total_count > count` (more matching policy sets exist than were returned).",
    )
    policy_sets: List[PolicySetSummary] = Field(
        ...,
        description="Matching policy sets sorted by `rank` ascending (evaluation order).",
    )


# ===========================================================================
# Tool 2 — ise_get_policy_set_details
# ===========================================================================

class AuthenticationRulesSection(BaseModel):
    total_count: int = Field(..., description="Total authentication rules in this policy set.")
    count: int = Field(..., description="Number of rules included in `rules` after truncation.")
    has_more: bool = Field(..., description="True when more rules exist beyond the returned set.")
    rules: List[AuthenticationRuleSummary] = Field(
        ...,
        description="Authentication rules sorted by `rank` ascending (evaluation order).",
    )


class AuthorizationRulesSection(BaseModel):
    total_count: int = Field(..., description="Total authorization rules in this policy set.")
    count: int = Field(..., description="Number of rules included in `rules` after truncation.")
    has_more: bool = Field(..., description="True when more rules exist beyond the returned set.")
    rules: List[AuthorizationRuleSummary] = Field(
        ...,
        description="Authorization rules sorted by `rank` ascending (evaluation order).",
    )


class LocalExceptionRulesSection(BaseModel):
    total_count: int = Field(..., description="Total local exception rules in this policy set.")
    count: int = Field(..., description="Number of rules included in `rules` after truncation.")
    has_more: bool = Field(..., description="True when more rules exist beyond the returned set.")
    rules: List[AuthorizationRuleSummary] = Field(
        ...,
        description="Local exception rules sorted by `rank` ascending. Evaluated BEFORE regular authorization rules within the same policy set.",
    )
    note: str = Field(
        "Local exception rules are evaluated BEFORE regular authorization rules within this policy set.",
        description="Steering note for the agent.",
    )


class PolicySetDetailsResult(BaseModel):
    """Result envelope for ``ise_get_policy_set_details``.

    Returns the full decision tree of a single policy set (looked up by name).
    """

    policy_set: PolicySetSummary = Field(..., description="The resolved policy set.")
    authentication_rules: AuthenticationRulesSection = Field(
        ...,
        description="Authentication rules in evaluation order.",
    )
    authorization_rules: AuthorizationRulesSection = Field(
        ...,
        description="Authorization rules in evaluation order.",
    )
    local_exception_rules: LocalExceptionRulesSection = Field(
        ...,
        description="Local exception rules — evaluated BEFORE regular authorization rules.",
    )


# ===========================================================================
# Tool 3 — ise_search_authorization_rules
# ===========================================================================

class AuthorizationRuleHit(BaseModel):
    """Authorization rule hit returned by ``ise_search_authorization_rules``.

    ``policy_set_name`` is omitted for global exception rules (they apply
    across ALL policy sets).
    """

    policy_set_name: Optional[str] = Field(
        None,
        description="Name of the policy set containing the rule. Omitted for global exception rules.",
    )
    name: str = Field(..., description="Rule name")
    rank: Optional[int] = Field(None, description="Rank within the policy set (or globally for global exceptions). Lower evaluates first.")
    state: Optional[Literal["enabled", "disabled", "monitor"]] = Field(None, description="Rule state.")
    hit_counts: Optional[int] = Field(None, description="Number of times this rule was matched.")
    profile: Optional[List[str]] = Field(None, description="Authorization profile names assigned by this rule.")
    security_group: Optional[str] = Field(None, description="TrustSec security group (SGT) assigned, if any.")
    condition_summary: Optional[str] = Field(None, description="Human-readable summary of the rule's matching condition.")


class AuthorizationRuleSearchResult(BaseModel):
    """Result envelope for ``ise_search_authorization_rules``.

    Always returns BOTH per-policy-set rules and global exception rules,
    because global exceptions override per-policy-set authorization rules
    across ALL policy sets and are the most common gotcha when troubleshooting
    "why is my rule not matching?".
    """

    search_filters: Dict[str, Any] = Field(..., description="Filters applied to the search (echoed for the agent).")
    total_count: int = Field(..., description="Total per-policy-set rules matching the filters before truncation by `limit`.")
    count: int = Field(..., description="Number of per-policy-set rules in `rules` (after truncation).")
    has_more: bool = Field(..., description="True when `total_count > count` for the per-policy-set rules.")
    policy_sets_scanned: int = Field(
        ...,
        description="Number of policy sets that were scanned during the fan-out. Compare with the total policy-set count if `has_more` is True — narrowing via `policy_set_name` may speed up the next call.",
    )
    rules: List[AuthorizationRuleHit] = Field(
        ...,
        description="Per-policy-set authorization rules matching the filters.",
    )
    global_exceptions: List[AuthorizationRuleHit] = Field(
        ...,
        description="Global exception rules matching the same filters. Override per-policy-set authz rules across ALL policy sets.",
    )
    global_exceptions_note: str = Field(
        "Global exception rules override per-policy-set authorization rules across ALL policy sets. Check these first when an unexpected profile is being applied.",
        description="Steering note for the agent.",
    )


# ===========================================================================
# Tool 4 — ise_search_authentication_rules
# ===========================================================================

class AuthenticationRuleHit(BaseModel):
    """Authentication rule hit returned by ``ise_search_authentication_rules``."""

    policy_set_name: str = Field(..., description="Name of the policy set containing the rule.")
    name: str = Field(..., description="Rule name")
    rank: Optional[int] = Field(None, description="Rank within the policy set. Lower evaluates first.")
    state: Optional[Literal["enabled", "disabled", "monitor"]] = Field(None, description="Rule state.")
    hit_counts: Optional[int] = Field(None, description="Number of times this rule was matched.")
    identity_source_name: Optional[str] = Field(None, description="Identity source the rule queries.")
    if_auth_fail: Optional[str] = Field(None, description="Action on authentication failure: REJECT, CONTINUE, or DROP.")
    if_user_not_found: Optional[str] = Field(None, description="Action when the user is not found in the identity store.")
    if_process_fail: Optional[str] = Field(None, description="Action when the identity store is unreachable.")
    condition_summary: Optional[str] = Field(None, description="Human-readable summary of the rule's matching condition.")


class AuthenticationRuleSearchResult(BaseModel):
    """Result envelope for ``ise_search_authentication_rules``."""

    search_filters: Dict[str, Any] = Field(..., description="Filters applied to the search.")
    total_count: int = Field(..., description="Total rules matching the filters before truncation by `limit`.")
    count: int = Field(..., description="Number of rules in `rules` (after truncation).")
    has_more: bool = Field(..., description="True when `total_count > count`.")
    policy_sets_scanned: int = Field(
        ...,
        description="Number of policy sets scanned during the fan-out.",
    )
    rules: List[AuthenticationRuleHit] = Field(
        ...,
        description="Authentication rules matching the filters.",
    )


# ===========================================================================
# Tool 5 — ise_search_authorization_profiles
# ===========================================================================

class AuthorizationProfileSummary(BaseModel):
    name: str = Field(..., description="Authorization profile name.")
    description: Optional[str] = Field(None, description="Profile description, when provided by ISE.")


class AuthorizationProfileSearchResult(BaseModel):
    """Result envelope for ``ise_search_authorization_profiles``."""

    search_filters: Dict[str, Any] = Field(..., description="Filters applied to the search.")
    total_count: int = Field(..., description="Total profiles matching the filters before truncation by `limit`.")
    count: int = Field(..., description="Number of profiles in `profiles` (after truncation).")
    has_more: bool = Field(..., description="True when `total_count > count`.")
    profiles: List[AuthorizationProfileSummary] = Field(
        ...,
        description="Matching authorization profiles, sorted by name ascending.",
    )


# ===========================================================================
# Tool 6 — ise_search_library_conditions
# ===========================================================================

class LibraryConditionSummary(BaseModel):
    name: str = Field(..., description="Library condition name.")
    description: Optional[str] = Field(None, description="Condition description, when provided by ISE.")
    condition_summary: Optional[str] = Field(
        None,
        description="Human-readable expression of the condition tree (e.g. 'Network Access:Protocol equals RADIUS').",
    )


class LibraryConditionSearchResult(BaseModel):
    """Result envelope for ``ise_search_library_conditions``."""

    search_filters: Dict[str, Any] = Field(..., description="Filters applied to the search.")
    total_count: int = Field(..., description="Total conditions matching the filters before truncation by `limit`.")
    count: int = Field(..., description="Number of conditions in `conditions` (after truncation).")
    has_more: bool = Field(..., description="True when `total_count > count`.")
    conditions: List[LibraryConditionSummary] = Field(
        ...,
        description="Matching library conditions, sorted by name ascending.",
    )


# ===========================================================================
# Tool 7 — ise_list_policy_authoring_references
# ===========================================================================

class IdentityStoreSummary(BaseModel):
    name: str = Field(..., description="Identity store name (referenced by authentication rules).")


class SecurityGroupSummary(BaseModel):
    name: str = Field(..., description="TrustSec security group name (referenced by authorization rules).")


class ServiceNameSummary(BaseModel):
    name: str = Field(..., description="Service name (referenced as a policy-set service identifier).")
    service_type: Optional[Literal["allowed_protocols", "server_sequence"]] = Field(
        None,
        description="Whether this service is an Allowed Protocols definition or a Server Sequence.",
    )
    is_local_authorization: Optional[bool] = Field(
        None,
        description="For server-sequence services, True when local authorization is enabled.",
    )


class IdentityStoresSection(BaseModel):
    total_count: int = Field(..., description="Total identity stores matching the filter.")
    count: int = Field(..., description="Number of items in `items` (after truncation).")
    has_more: bool = Field(..., description="True when `total_count > count`.")
    items: List[IdentityStoreSummary] = Field(..., description="Identity stores.")


class SecurityGroupsSection(BaseModel):
    total_count: int = Field(..., description="Total security groups matching the filter.")
    count: int = Field(..., description="Number of items in `items` (after truncation).")
    has_more: bool = Field(..., description="True when `total_count > count`.")
    items: List[SecurityGroupSummary] = Field(..., description="TrustSec security groups (SGTs).")


class ServiceNamesSection(BaseModel):
    total_count: int = Field(..., description="Total service names matching the filter.")
    count: int = Field(..., description="Number of items in `items` (after truncation).")
    has_more: bool = Field(..., description="True when `total_count > count`.")
    items: List[ServiceNameSummary] = Field(..., description="Allowed-protocols and server-sequence services.")


class PolicyAuthoringReferencesResult(BaseModel):
    """Result envelope for ``ise_list_policy_authoring_references``.

    Returns the three reference catalogs needed when authoring or auditing
    policy rules: identity stores (used in authentication rules), security
    groups (used in authorization rules), and service names (used by policy
    sets as the allowed-protocols or server-sequence identifier).
    """

    search_filters: Dict[str, Any] = Field(..., description="Filters applied to the search (e.g. `name_substring`).")
    identity_stores: IdentityStoresSection = Field(
        ...,
        description="Identity stores referenced by authentication rules.",
    )
    security_groups: SecurityGroupsSection = Field(
        ...,
        description="TrustSec security groups referenced by authorization rules.",
    )
    service_names: ServiceNamesSection = Field(
        ...,
        description="Allowed-protocols / server-sequence services referenced by policy sets.",
    )
