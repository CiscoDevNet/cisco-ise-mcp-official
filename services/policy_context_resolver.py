# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, List

from fastmcp.exceptions import ToolError as McpToolError

from logger import logger
from models.error_models import ErrorCategory, raise_tool_error
from tools.policy_tool_handler import PolicyToolHandler
from models.policy_models import (
    PolicyContext,
    PolicySetSummary,
    AuthenticationRuleSummary,
    AuthorizationRuleSummary,
)
from models.session_models import (
    EnrichedSessionSearchResult,
    PolicyEnrichedSessionSearchResult,
    SessionWithPolicyContext,
)
# Re-export ``condition_to_summary`` from its new home in ``utils`` so existing
# imports (services.policy_context_resolver.condition_to_summary) keep working.
from utils.policy_condition_summary import condition_to_summary  # noqa: F401


class PolicyContextResolver:
    """
    Resolves policy set names and rule names into full policy details
    via the ISE Policy API.

    Generic service: accepts plain strings (not session-specific objects)
    so any tool that has a policy set name can use it.
    """

    def __init__(self, policy_tool_handler: PolicyToolHandler):
        self._policy_handler = policy_tool_handler

    async def enrich_sessions_with_policy_context(
        self, enriched_result: EnrichedSessionSearchResult
    ) -> PolicyEnrichedSessionSearchResult:
        """Resolve policy context for each session in an enriched search result.

        Resolves policy details per unique (policy_set, authn_rule, authz_rule) tuple
        (with caching to avoid duplicate API calls), and returns a typed result.

        Args:
            enriched_result: The enriched session search result from
                ``SessionToolHandler.search_enriched_active_sessions``.

        Returns:
            PolicyEnrichedSessionSearchResult with each session paired with its
            resolved policy context.
        """
        try:
            policy_cache: dict[tuple, PolicyContext] = {}
            results: List[SessionWithPolicyContext] = []

            for session in enriched_result.sessions:
                if not session.ise_policy_set_name:
                    results.append(SessionWithPolicyContext(
                        session=session,
                        policy_context=None,
                        policy_context_note="No policy set name found in session data",
                    ))
                    continue

                cache_key = (
                    session.ise_policy_set_name,
                    session.identity_policy_matched_rule,
                    session.authorization_policy_matched_rule,
                )

                if cache_key not in policy_cache:
                    policy_cache[cache_key] = await self.resolve(
                        policy_set_name=session.ise_policy_set_name,
                        authn_rule_name=session.identity_policy_matched_rule,
                        authz_rule_name=session.authorization_policy_matched_rule,
                    )
                logger.debug("Policy context resolved", policy_context=policy_cache[cache_key])

                results.append(SessionWithPolicyContext(
                    session=session,
                    policy_context=policy_cache[cache_key],
                ))

            return PolicyEnrichedSessionSearchResult(
                search_filters=enriched_result.search_filters,
                total_sessions_found=enriched_result.total_sessions_found,
                actual_sessions_returned=len(results),
                sessions=results,
            )
        except McpToolError:
            raise
        except Exception as e:
            logger.exception("Error enriching sessions with policy context", error=str(e))
            raise_tool_error(
                ErrorCategory.SERVER_ERROR, "POLICY_ENRICHMENT_ERROR",
                "An unexpected error occurred while resolving policy context for sessions.",
            )

    async def resolve(
        self,
        policy_set_name: str,
        authn_rule_name: Optional[str] = None,
        authz_rule_name: Optional[str] = None,
    ) -> PolicyContext:
        """
        Resolve a policy set name (and optionally rule names) into full
        policy details from the ISE Policy API.

        Args:
            policy_set_name: Name of the policy set (e.g. "Default").
            authn_rule_name: Name of the authentication rule to resolve.
            authz_rule_name: Name of the authorization rule to resolve.

        Returns:
            PolicyContext with resolved details. Fields are None when
            resolution fails; errors are collected in resolution_errors.
        """
        errors: List[str] = []
        policy_set_summary: Optional[PolicySetSummary] = None
        authn_rule_summary: Optional[AuthenticationRuleSummary] = None
        authz_rule_summary: Optional[AuthorizationRuleSummary] = None

        policy_set_id, policy_set_summary, ps_errors = await self._resolve_policy_set(
            policy_set_name
        )
        errors.extend(ps_errors)

        if policy_set_id and (authn_rule_name or authz_rule_name):
            authn_rule_summary, authz_rule_summary, rule_errors = (
                await self._resolve_rules(
                    policy_set_id, authn_rule_name, authz_rule_name
                )
            )
            errors.extend(rule_errors)

        return PolicyContext(
            policy_set=policy_set_summary,
            authentication_rule=authn_rule_summary,
            authorization_rule=authz_rule_summary,
            resolution_errors=errors if errors else None,
        )

    async def _resolve_policy_set(
        self, policy_set_name: str
    ) -> tuple[Optional[str], Optional[PolicySetSummary], List[str]]:
        """List all policy sets and find the one matching the given name."""
        errors: List[str] = []
        try:
            policy_set_list = await self._policy_handler.get_network_access_policy_set_list()
        except Exception as e:
            logger.error("Failed to fetch policy set list", error=str(e))
            return None, None, ["Failed to fetch policy set list from ISE"]

        if not isinstance(policy_set_list, list):
            logger.error("Unexpected policy set list format", actual_type=type(policy_set_list).__name__)
            return None, None, ["Unexpected policy set list format from ISE"]

        for policy_set in policy_set_list:
            if policy_set.get("name") == policy_set_name:
                summary = PolicySetSummary(
                    name=policy_set["name"],
                    description=policy_set.get("description"),
                    condition_summary=condition_to_summary(policy_set.get("condition")),
                )
                return policy_set.get("id"), summary, errors

        msg = f"Policy set '{policy_set_name}' not found"
        logger.warning(msg)
        errors.append(msg)
        return None, None, errors

    async def _resolve_rules(
        self,
        policy_set_id: str,
        authn_rule_name: Optional[str],
        authz_rule_name: Optional[str],
    ) -> tuple[
        Optional[AuthenticationRuleSummary],
        Optional[AuthorizationRuleSummary],
        List[str],
    ]:
        """Resolve authentication and authorization rules."""
        authn_summary: Optional[AuthenticationRuleSummary] = None
        authz_summary: Optional[AuthorizationRuleSummary] = None
        errors: List[str] = []

        if authn_rule_name:
            try:
                authn_summary, authn_errors = await self._resolve_authn_rule(
                    policy_set_id, authn_rule_name
                )
                errors.extend(authn_errors)
            except Exception as e:
                logger.error("Error resolving authn rule", rule_name=authn_rule_name, error=str(e))
                errors.append(f"Failed to resolve authentication rule '{authn_rule_name}'")

        if authz_rule_name:
            try:
                authz_summary, authz_errors = await self._resolve_authz_rule(
                    policy_set_id, authz_rule_name
                )
                errors.extend(authz_errors)
            except Exception as e:
                logger.error("Error resolving authz rule", rule_name=authz_rule_name, error=str(e))
                errors.append(f"Failed to resolve authorization rule '{authz_rule_name}'")

        return authn_summary, authz_summary, errors

    async def _resolve_authn_rule(
        self, policy_set_id: str, rule_name: str
    ) -> tuple[Optional[AuthenticationRuleSummary], List[str]]:
        """List authentication rules for a policy set and find by name."""
        errors: List[str] = []
        try:
            authentication_rule_list = await self._policy_handler.get_network_access_authentication_rule_list(policy_id=policy_set_id)
        except Exception as e:
            logger.error("Failed to fetch authentication rules", policy_set_id=policy_set_id, error=str(e))
            return None, ["Failed to fetch authentication rules from ISE"]
        
        if not isinstance(authentication_rule_list, list):
            logger.error("Unexpected authentication rule list format", actual_type=type(authentication_rule_list).__name__)
            return None, ["Unexpected authentication rule list format from ISE"]

        for entry in authentication_rule_list:
            rule = entry.get("rule", {})
            if rule.get("name") == rule_name:
                summary = AuthenticationRuleSummary(
                    name=rule["name"],
                    identity_source_name=entry.get("identitySourceName"),
                    if_auth_fail=entry.get("ifAuthFail"),
                    if_user_not_found=entry.get("ifUserNotFound"),
                    if_process_fail=entry.get("ifProcessFail"),
                    condition_summary=condition_to_summary(rule.get("condition")),
                )
                return summary, errors

        msg = f"Authentication rule '{rule_name}' not found in policy set '{policy_set_id}'"
        logger.warning(msg)
        errors.append(msg)
        return None, errors

    async def _resolve_authz_rule(
        self, policy_set_id: str, rule_name: str
    ) -> tuple[Optional[AuthorizationRuleSummary], List[str]]:
        """List authorization rules for a policy set and find by name."""
        errors: List[str] = []
        try:
            authorization_rule_list = await self._policy_handler.get_network_access_authorization_rule_list(policy_id=policy_set_id)
        except Exception as e:
            logger.error("Failed to fetch authorization rules", policy_set_id=policy_set_id, error=str(e))
            return None, ["Failed to fetch authorization rules from ISE"]

        if not isinstance(authorization_rule_list, list):
            logger.error("Unexpected authorization rule list format", actual_type=type(authorization_rule_list).__name__)
            return None, ["Unexpected authorization rule list format from ISE"]

        for entry in authorization_rule_list:
            rule = entry.get("rule", {})
            if rule.get("name") == rule_name:
                summary = AuthorizationRuleSummary(
                    name=rule["name"],
                    profile=entry.get("profile"),
                    security_group=entry.get("securityGroup"),
                    condition_summary=condition_to_summary(rule.get("condition")),
                )
                return summary, errors

        msg = f"Authorization rule '{rule_name}' not found in policy set '{policy_set_id}'"
        logger.warning(msg)
        errors.append(msg)
        return None, errors
