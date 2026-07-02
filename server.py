# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved
import os
from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastmcp import FastMCP
from pydantic import Field

from clients.client_factory import client_factory
from clients.mnt_client import mnt_client
from tools.certificates_tool_handler import CertificatesToolHandler
from tools.policy_tool_handler import PolicyToolHandler
from tools.session_tool_handler import SessionToolHandler
from tools.failure_tool_handler import FailureToolHandler
from services.policy_context_resolver import PolicyContextResolver
from services.latency_context_resolver import LatencyContextResolver
from services.failure_context_resolver import FailureContextResolver
from resources.ise_glossary import TOOL_GLOSSARIES, DEFAULT_GLOSSARY
from utils.xml_parser import parse_msg_catalog, parse_failure_reasons_xml
from models.session_models import (
    ActiveSessionSearchResult,
    EnrichedSessionSearchResult,
    LatencyEnrichedSessionSearchResult,
    PolicyEnrichedSessionSearchResult,
)
from models.failure_models import AaaFailureInvestigationResult
from models.policy_models import (
    AuthenticationRuleSearchResult,
    AuthorizationRuleSearchResult,
    PolicySetSearchResult,
    PolicySetDetailsResult,
    AuthorizationProfileSearchResult,
    LibraryConditionSearchResult,
    PolicyAuthoringReferencesResult,
)
from logger import logger
from shared_libs import measure_time_async, normalize_docstring
from utils.ise_credential_middleware import IseCredentialMiddleware

MSG_CATALOG_PATH = os.getenv("MSG_CATALOG_PATH", "msg_cat.xml")

latency_context_resolver: Optional[LatencyContextResolver] = None
failure_context_resolver: Optional[FailureContextResolver] = None


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """
    Application lifespan hook for FastMCP server.
    Handles startup and shutdown of async clients.
    """
    # Startup:
    global latency_context_resolver, failure_context_resolver

    logger.info("Starting server lifecycle: initializing clients...")
    await mnt_client.setup()
    logger.info("MNT client ready")

    msg_catalog = parse_msg_catalog(MSG_CATALOG_PATH)
    latency_context_resolver = LatencyContextResolver(msg_catalog)
    logger.info("Latency context resolver ready")

    try:
        failure_reasons_response = await mnt_client.get("FailureReasons")
        failure_reasons_catalog = parse_failure_reasons_xml(failure_reasons_response.text)
        failure_context_resolver = FailureContextResolver(msg_catalog, failure_reasons_catalog)
        logger.info("Failure context resolver ready", count=len(failure_reasons_catalog))
    except Exception as e:
        logger.warning("Failed to load failure reasons catalog — running in degraded mode", error=str(e))
        failure_context_resolver = None

    yield {}
    
    # Shutdown: Close async clients

    logger.info("Shutting down server lifecycle: closing clients...")
    await mnt_client.close()
    logger.info("MNT client closed")


ise_mcp_server = FastMCP("ise-mcp-server", lifespan=app_lifespan)
ise_mcp_server.add_middleware(IseCredentialMiddleware())
PORT = int(os.getenv("PORT", "5000"))
HOST = os.getenv("HOST", "0.0.0.0")

certificates_tool_handler = CertificatesToolHandler(client_factory)
policy_tool_handler = PolicyToolHandler(client_factory)
policy_context_resolver = PolicyContextResolver(policy_tool_handler)
session_tool_handler = SessionToolHandler(mnt_client)
failure_tool_handler = FailureToolHandler(mnt_client)


@ise_mcp_server.resource(
    "ise://glossary/tool/{tool_name}",
    name="ise_tool_glossary",
    description="Cisco ISE domain glossary composed for a specific tool. Returns field definitions relevant to the tool's output.",
    mime_type="text/plain",
    annotations={"readOnlyHint": True},
)
def get_tool_glossary(tool_name: str) -> str:
    return TOOL_GLOSSARIES.get(tool_name, DEFAULT_GLOSSARY)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def active_sessions_search(
    username: Annotated[Optional[str], "Username to match."] = None,
    calling_station_id: Annotated[Optional[str], "Endpoint MAC."] = None,
    nas_ip_address: Annotated[Optional[str], "NAS IP (network device)."] = None,
    framed_ip_address: Annotated[Optional[str], "Endpoint IP."] = None,
    server: Annotated[Optional[str], "ISE node name."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1).")] = 60,
    limit: Annotated[int, Field(ge=1, le=20, description="Max results.")] = 10,
) -> str:
    """
    Locate sessions and look up their IDENTIFIERS: username, MAC, IP, IPv6,
    NAS, ISE node, audit_session_id. No profiles, posture, identity store, auth
    method, or policy names.

    Returns a bounded SAMPLE of matching sessions (capped by `limit`); cite
    `total_matching_sessions` for the true count, not the number of items returned.

    When total_matching_sessions exceeds the returned count, raise `limit`
    (up to 20) to retrieve more; cite total_matching_sessions as the true count.

    USE THIS for: who/what connected, find a session by MAC/username/NAS, look up a session's IP, IPv6, or audit_session_id.
    """
    result: ActiveSessionSearchResult = await session_tool_handler.search_active_sessions(
        username=username,
        calling_station_id=calling_station_id,
        nas_ip_address=nas_ip_address,
        framed_ip_address=framed_ip_address,
        server=server,
        minutes=minutes,
        limit=limit,
    )
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def sessions_search_with_advanced_details(
    username: Annotated[Optional[str], "Username to match."] = None,
    calling_station_id: Annotated[Optional[str], "Endpoint MAC."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1).")] = 60,
    limit: Annotated[int, Field(ge=1, le=10, description="Max sessions to enrich and return.")] = 1,
) -> str:
    """
    Show WHAT was applied to a session: auth result (passed/failed), auth
    method/protocol, posture status, identity store, identity group, response
    time, and the authorization profile name. No rule conditions, SGT, or
    failure actions.

    USE THIS for a known user or MAC asking which profile, identity store,
    identity group, posture, auth method, pass/fail, or response time applied
    to their session.

    For per-step timing use sessions_search_with_latency_details. For matched
    rule conditions, SGT, and failure actions use sessions_search_with_policy_details.
    For failure root cause, use ise_investigate_aaa_failure.
    """
    result: EnrichedSessionSearchResult = await session_tool_handler.search_enriched_active_sessions(
        username=username,
        calling_station_id=calling_station_id,
        minutes=minutes,
        limit=limit,
    )
    return result.model_dump_json(exclude_none=True)

@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def sessions_search_with_policy_details(
    username: Annotated[Optional[str], "Username to match."] = None,
    calling_station_id: Annotated[Optional[str], "Endpoint MAC."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1).")] = 60,
    limit: Annotated[int, Field(ge=1, le=10, description="Max sessions to enrich and return.")] = 1,
) -> str:
    """
    Explain WHY a specific user/endpoint session was authorized: matched policy
    set, authn rule, and authz rule with their CONDITIONS (if/then logic), the
    SGT/security group assigned, the identity source configured, and the
    failure actions (if_auth_fail, if_user_not_found, if_process_fail).

    USE THIS for a SPECIFIC user or MAC asking WHY, or about the matched rule's
    conditions, SGT, configured identity source, or failure actions.

    For just the profile/identity-store applied (no conditions), use
    sessions_search_with_advanced_details. For policy config with no live session,
    use ise_search_authorization_rules / ise_search_authentication_rules.
    """
    enriched_result = await session_tool_handler.search_enriched_active_sessions(
        username=username,
        calling_station_id=calling_station_id,
        minutes=minutes,
        limit=limit,
    )
    result: PolicyEnrichedSessionSearchResult = await policy_context_resolver.enrich_sessions_with_policy_context(enriched_result)
    return result.model_dump_json(
        exclude_none=True,
        exclude={
            "sessions": {
                "__all__": {
                    "session": {
                        "authentication_method",
                        "authentication_protocol",
                        "framed_ip_address",
                        "ise_psn_node",
                        "response_time_ms",
                        "auth_acs_timestamp",
                        "posture_status",
                        "protocol",
                    }
                }
            }
        },
    )

# # TODO: take for ise CSCOcpm/db/sql/msg_cat.xml
@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def sessions_search_with_latency_details(
    username: Annotated[Optional[str], "Username to match."] = None,
    calling_station_id: Annotated[Optional[str], "Endpoint MAC."] = None,
    min_latency_ms: Annotated[Optional[int], Field(ge=0, description="Min response_time_ms.")] = None,
    max_latency_ms: Annotated[Optional[int], Field(ge=0, description="Max response_time_ms.")] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1).")] = 60,
    limit: Annotated[int, Field(ge=1, le=10, description="Max sessions to enrich and return.")] = 1,
) -> str:
    """
    Break down HOW LONG each ISE authentication STEP took: per-step latency
    (step name, message, milliseconds), with optional min/max filtering.

    USE THIS for per-step timing or filtering sessions by latency: which step
    is slow, where is the bottleneck, sessions above/below N ms.
    """
    enriched_result = await session_tool_handler.search_enriched_active_sessions(
        username=username,
        calling_station_id=calling_station_id,
        minutes=minutes,
        limit=limit,
        min_latency_ms=min_latency_ms,
        max_latency_ms=max_latency_ms,
    )
    result: LatencyEnrichedSessionSearchResult = latency_context_resolver.enrich_sessions_with_latency_context(enriched_result)
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_investigate_aaa_failure(
    mac_address: Annotated[Optional[str], "Endpoint MAC."] = None,
    username: Annotated[Optional[str], "Username."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1).")] = 60,
    limit: Annotated[int, Field(ge=1, le=10, description="Result cap.")] = 1,
) -> str:
    """
    Investigate the ROOT CAUSE of a RADIUS AAA authentication FAILURE for an
    endpoint or user: failure reason, cause, and resolution. Pass both MAC and
    username for best coverage.

    USE THIS only when authentication FAILED and you need why: access denied,
    failure reason, why rejected, how to fix.
    """
    result: AaaFailureInvestigationResult = await failure_tool_handler.investigate_aaa_failure(
        mac_address=mac_address,
        username=username,
        minutes=minutes,
        limit=limit,
        failure_context_resolver=failure_context_resolver,
    )
    return result.model_dump_json(exclude_none=True)




# ---------------------------------------------------------------------------
# Policy Configuration Tools (Network Access)
# ---------------------------------------------------------------------------

@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_search_policy_sets(
    name_substring: Annotated[Optional[str], "Case-insensitive substring filter on policy-set name."] = None,
    state_filter: Annotated[str, "Policy-set state filter: 'all', 'enabled', 'disabled', or 'monitor'."] = "all",
    limit: Annotated[int, Field(ge=1, le=100, description="Max policy sets to return.")] = 20,
    min_hit_counts: Annotated[Optional[int], Field(ge=0, description="Lower bound: keep policy sets with hit_counts >= this. Use for 'hit at least N times / busiest / most used'.")] = None,
    max_hit_counts: Annotated[Optional[int], Field(ge=0, description="Upper bound: keep policy sets with hit_counts <= this. Use max_hit_counts=0 for 'never hit / 0 hit counts / stale / unused', or N for 'rarely used / at most N hits'.")] = None,
) -> str:
    """
    List ALL policy sets: name, rank, state, hit counts, condition, service.
    No internal rule details.

    USE THIS when: list policy sets, find a policy set by name, find disabled/stale sets.
    """
    result: PolicySetSearchResult = await policy_tool_handler.search_policy_sets(
        name_substring=name_substring,
        state_filter=state_filter,
        limit=limit,
        min_hit_counts=min_hit_counts,
        max_hit_counts=max_hit_counts,
    )
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_get_policy_set_details(
    policy_set_name: Annotated[str, "Exact policy-set name (the human-readable label shown in the ISE UI)."],
    rules_per_section_limit: Annotated[int, Field(ge=1, le=25, description="Max rules to return per section (authn / authz / local exceptions).")] = 10,
) -> str:
    """
    [REQUIRES a policy-set name] Return the full rule tree INSIDE a single
    policy set: authentication rules, authorization rules, and local exception
    rules — with their identity stores, state, hit counts, conditions, and
    evaluation order (rank).

    USE THIS when the question asks about anything INSIDE a named policy set:
    'show me everything inside X', 'what is the evaluation order in X',
    'which identity store does each authn rule use in X', 'are there disabled
    rules in X', 'what authz profiles are assigned by rules in X', 'does X
    have local exception rules'.

    Do NOT use to discover what policy sets exist (use ise_search_policy_sets).

    Do NOT use for cross-policy-set reverse lookups by profile or identity
    store (use ise_search_authorization_rules / ise_search_authentication_rules).
    """
    result: PolicySetDetailsResult = await policy_tool_handler.get_policy_set_details(
        policy_set_name=policy_set_name,
        rules_per_section_limit=rules_per_section_limit,
    )
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_search_authorization_rules(
    policy_set_name: Annotated[Optional[str], "Restrict search to this policy set (by name). Strongly recommended to narrow fan-out."] = None,
    profile_name_filter: Annotated[Optional[str], "Case-insensitive substring matched against the rule's authorization profile name(s)."] = None,
    security_group_filter: Annotated[Optional[str], "Case-insensitive substring matched against the rule's TrustSec SGT name."] = None,
    state_filter: Annotated[str, "Rule state filter: 'all', 'enabled', or 'disabled'."] = "all",
    min_hit_counts: Annotated[Optional[int], Field(ge=0, description="Only include rules with hit_counts >= this value. Use 0 to find unused rules.")] = None,
    name_substring: Annotated[Optional[str], "Case-insensitive substring of the rule name."] = None,
    limit: Annotated[int, Field(ge=1, le=50, description="Max per-policy-set rules to return.")] = 25,
) -> str:
    """
    Find authorization rules (a.k.a. "authorization policies") across policy
    sets by profile, SGT, state, hit count, or rule name. Includes global
    exception rules.

    USE THIS when: which rules assign profile X, are there global exceptions
    overriding a rule, why is a profile applied unexpectedly, find unused rules,
    which authorization policy/rule has the most or fewest hits, rank
    authorization rules by hit count, policy configuration questions not tied
    to a specific live session.
    """
    result: AuthorizationRuleSearchResult = await policy_tool_handler.search_authorization_rules(
        policy_set_name=policy_set_name,
        profile_name_filter=profile_name_filter,
        security_group_filter=security_group_filter,
        state_filter=state_filter,
        min_hit_counts=min_hit_counts,
        name_substring=name_substring,
        limit=limit,
    )
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_search_authentication_rules(
    policy_set_name: Annotated[Optional[str], "Restrict search to this policy set (by name). Strongly recommended to narrow fan-out."] = None,
    identity_source_filter: Annotated[Optional[str], "Case-insensitive substring matched against the rule's identitySourceName (identity store)."] = None,
    state_filter: Annotated[str, "Rule state filter: 'all', 'enabled', or 'disabled'."] = "all",
    min_hit_counts: Annotated[Optional[int], Field(ge=0, description="Only include rules with hit_counts >= this value. Use 0 to find unused rules.")] = None,
    name_substring: Annotated[Optional[str], "Case-insensitive substring of the rule name."] = None,
    limit: Annotated[int, Field(ge=1, le=50, description="Max rules to return.")] = 25,
) -> str:
    """
    Find authentication rules in the policy CONFIGURATION across policy sets by
    identity store, state, hit count, or rule name. Returns identity_source_name
    and failure actions. Not tied to any live session.

    USE THIS when: which authn rules use AD, find unused authn rules, lenient
    failure actions.
    """
    result: AuthenticationRuleSearchResult = await policy_tool_handler.search_authentication_rules(
        policy_set_name=policy_set_name,
        identity_source_filter=identity_source_filter,
        state_filter=state_filter,
        min_hit_counts=min_hit_counts,
        name_substring=name_substring,
        limit=limit,
    )
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_search_authorization_profiles(
    name_substring: Annotated[Optional[str], "Case-insensitive substring of the profile name."] = None,
    limit: Annotated[int, Field(ge=1, le=200, description="Max profiles to return.")] = 50,
) -> str:
    """
    [CATALOG lookup] List available authorization profile NAMES (not which
    rules use them). Returns name + description only.

    USE THIS to: verify a profile exists, find profiles matching a substring,
    or audit the authorization profile catalog.

    Do NOT use to find which rules USE a profile (use
    ise_search_authorization_rules with profile_name_filter).
    """
    result: AuthorizationProfileSearchResult = await policy_tool_handler.search_authorization_profiles(
        name_substring=name_substring,
        limit=limit,
    )
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_search_library_conditions(
    name_substring: Annotated[Optional[str], "Case-insensitive substring of the condition name."] = None,
    scope_filter: Annotated[str, "Scope filter: 'all', 'policyset', 'authentication', or 'authorization'."] = "all",
    limit: Annotated[int, Field(ge=1, le=50, description="Max conditions to return.")] = 25,
) -> str:
    """
    [CATALOG lookup] Look up reusable library conditions and return what each
    one actually evaluates (e.g. 'Network Access:Protocol equals RADIUS').

    USE THIS for: 'what does library condition X evaluate?', 'find conditions
    usable in authentication rules', 'is there a condition named Y?'.

    Do NOT use for inline conditions on rules (those appear as
    condition_summary in ise_get_policy_set_details output).
    """
    result: LibraryConditionSearchResult = await policy_tool_handler.search_library_conditions(
        name_substring=name_substring,
        scope_filter=scope_filter,
        limit=limit,
    )
    return result.model_dump_json(exclude_none=True)


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_list_policy_authoring_references(
    name_substring: Annotated[Optional[str], "Case-insensitive substring applied to all three sections (identity stores, security groups, service names)."] = None,
    limit_per_section: Annotated[int, Field(ge=1, le=200, description="Max items returned per section (identity stores / security groups / service names).")] = 50,
) -> str:
    """
    [CATALOG lookup] List reference catalogs: identity stores, TrustSec
    security groups (SGTs), and service names (Allowed Protocols / Server
    Sequences). Returns NAMES only.

    USE THIS for: 'what identity stores can I reference?', 'what SGTs are
    available?', 'what allowed-protocols services exist?', 'what can I use
    when creating a new policy set?'.

    Do NOT use for authorization profiles (use
    ise_search_authorization_profiles).

    Do NOT use for library conditions (use ise_search_library_conditions).
    """
    result: PolicyAuthoringReferencesResult = await policy_tool_handler.list_policy_authoring_references(
        name_substring=name_substring,
        limit_per_section=limit_per_section,
    )
    return result.model_dump_json(exclude_none=True)


def main():
    try:
        logger.info("Starting ISE MCP Server...")
        ise_mcp_server.run(transport="streamable-http", host=HOST, port=PORT)
    except Exception as e:
        logger.exception("Error starting ISE MCP Server", error=str(e))
        return 1
    return 0

if __name__ == "__main__":
    main()
