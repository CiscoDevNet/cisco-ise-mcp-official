# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import os
from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastmcp import FastMCP
from pydantic import Field

from clients.client_factory import client_factory
from clients.mnt_client import mnt_client
from clients.ise_web_session import ise_web_session
from services.log_service import log_service
from services.certificate_diagnostics_resolver import CertificateDiagnosticsResolver
from tools.certificates_tool_handler import CertificatesToolHandler
from tools.policy_tool_handler import PolicyToolHandler
from tools.session_tool_handler import SessionToolHandler
from tools.failure_tool_handler import FailureToolHandler
from tools.deployment_tool_handler import DeploymentToolHandler
from services.policy_context_resolver import PolicyContextResolver
from services.latency_context_resolver import LatencyContextResolver
from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
from resources.ise_glossary import TOOL_GLOSSARIES, DEFAULT_GLOSSARY
from utils.xml_parser import parse_msg_catalog
from models.session_models import (
    ActiveSessionSearchResult,
    EnrichedSessionSearchResult,
    LatencyEnrichedSessionSearchResult,
    PolicyEnrichedSessionSearchResult,
    SessionCountResult,
)
from models.failure_models import AaaFailureInvestigationResult
from models.deployment_models import DeploymentHealthResult
from models.certificate_models import CertificateDiagnosisResult
from models.policy_models import (
    AuthenticationRuleSearchResult,
    AuthorizationRuleSearchResult,
    PolicySetSearchResult,
)
from logger import logger
from shared_libs import measure_time_async, normalize_docstring
from utils.ise_credential_middleware import IseCredentialMiddleware

MSG_CATALOG_PATH = os.getenv("MSG_CATALOG_PATH", "msg_cat.xml")

latency_context_resolver: Optional[LatencyContextResolver] = None


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """
    Application lifespan hook for FastMCP server.
    Handles startup and shutdown of async clients.
    """
    # Startup:
    global latency_context_resolver

    logger.info("Starting server lifecycle: initializing clients...")
    await mnt_client.setup()
    logger.info("MNT client ready")

    await ise_web_session.setup()
    await log_service.setup()
    logger.info("Log service ready")

    msg_catalog = parse_msg_catalog(MSG_CATALOG_PATH)
    latency_context_resolver = LatencyContextResolver(msg_catalog)
    logger.info("Latency context resolver ready")

    # The FailureReasons catalog is NOT fetched here. Doing so at startup
    # issues an MnT GET outside any inbound MCP request, so no per-user
    # X-ISE-Authorization header is in scope and the call can only use the
    # service account (failing loudly in header-only deployments). Instead
    # the FailureContextResolver is built lazily on the first AAA-failure
    # tool call, inside that request's task, so it authenticates with the
    # per-user credential. We only hand the handler the local, network-free
    # message catalog here. See FailureToolHandler._get_failure_resolver.
    failure_tool_handler.attach_msg_catalog(msg_catalog)
    logger.info("Failure tool handler ready (resolver builds lazily on first use)")

    yield {}
    
    # Shutdown: Close async clients

    logger.info("Shutting down server lifecycle: closing clients...")
    await mnt_client.close()
    logger.info("MNT client closed")

    await log_service.close()
    await ise_web_session.close()
    logger.info("Log service closed")


ise_mcp_server = FastMCP("ise-mcp-server", lifespan=app_lifespan)
ise_mcp_server.add_middleware(IseCredentialMiddleware())
PORT = int(os.getenv("PORT", "5000"))
HOST = os.getenv("HOST", "0.0.0.0")

certificate_diagnostics_resolver = CertificateDiagnosticsResolver(client_factory)
certificates_tool_handler = CertificatesToolHandler(
    client_factory, certificate_diagnostics_resolver
)
policy_tool_handler = PolicyToolHandler(client_factory)
policy_context_resolver = PolicyContextResolver(policy_tool_handler)
session_tool_handler = SessionToolHandler(mnt_client)
failure_tool_handler = FailureToolHandler(mnt_client)
deployment_diagnostics_resolver = DeploymentDiagnosticsResolver(mnt_client)
deployment_tool_handler = DeploymentToolHandler(
    client_factory, deployment_diagnostics_resolver
)


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
    audit_session_id: Annotated[Optional[str], "Audit session ID: a hexadecimal string generated by the network device, e.g. C0A70110000000700019977. NOT the same as acct_session_id."] = None,
    server: Annotated[Optional[str], "ISE node name."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1). Applies ONLY when no single identifier is given — a lookup by one identifier is not time-bounded.")] = 60,
    limit: Annotated[int, Field(ge=1, le=20, description="Max results.")] = 10,
) -> ActiveSessionSearchResult:
    """
    Locate sessions and look up their IDENTIFIERS: username, MAC, IP, IPv6,
    NAS, ISE node, audit_session_id. No profiles, posture, identity store, auth
    method, or policy names.

    Supplying exactly ONE identifier (username, MAC, NAS IP, endpoint IP, or
    audit_session_id) queries ISE directly for that session and ignores
    `minutes`, so the session is found however long ago it authenticated. Adding
    a second filter, or `server`, switches to a time-windowed scan bounded by
    `minutes`. `search_filters.lookup` reports which path answered.

    Returns a bounded SAMPLE of matching active sessions (capped by `limit`);
    cite `total_matching_active_sessions` for the true count, not the number of
    items returned. When it exceeds the returned count, raise `limit` (up to 20).

    USE THIS for:
    - who/what connected; find a session by MAC, username, NAS, or audit_session_id
    - look up a session's IP, IPv6, or audit_session_id
    - check whether a session EXISTS for a known user or MAC (an empty
      active_sessions_sample means there is none)

    DO NOT use this for authentication method, authorization profile, identity
    store, posture, or pass/fail result — use
    sessions_search_with_advanced_details.
    """
    result: ActiveSessionSearchResult = await session_tool_handler.search_active_sessions(
        username=username,
        calling_station_id=calling_station_id,
        nas_ip_address=nas_ip_address,
        framed_ip_address=framed_ip_address,
        audit_session_id=audit_session_id,
        server=server,
        minutes=minutes,
        limit=limit,
    )
    return result


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def sessions_search_with_advanced_details(
    username: Annotated[Optional[str], "Username to match."] = None,
    calling_station_id: Annotated[Optional[str], "Endpoint MAC."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1). Applies ONLY when neither username nor MAC is given — an identifier lookup is not time-bounded.")] = 60,
    limit: Annotated[int, Field(ge=1, le=10, description="Max sessions to enrich and return.")] = 1,
) -> EnrichedSessionSearchResult:
    """
    Show WHAT was applied to a session: auth result (passed/failed), auth
    method/protocol, posture status, identity store, identity group, response
    time, and the authorization profile name. No rule conditions, SGT, or
    failure actions.

    Supplying username or MAC queries ISE for that session directly and ignores
    `minutes`, so the session is found however long ago it authenticated. MAC
    takes precedence when both are given.

    USE THIS for a known user or MAC asking about:
    - authentication method or protocol (dot1x, MAB, PEAP, EAP-TLS, ...)
    - the authorization profile applied
    - identity store, identity group, posture status
    - pass/fail authentication result, or session response time

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
    return result

@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def sessions_search_with_policy_details(
    username: Annotated[Optional[str], "Username to match."] = None,
    calling_station_id: Annotated[Optional[str], "Endpoint MAC."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes (minimum 1). Applies ONLY when neither username nor MAC is given — an identifier lookup is not time-bounded.")] = 60,
    limit: Annotated[int, Field(ge=1, le=10, description="Max sessions to enrich and return.")] = 1,
) -> dict:
    """
    Explain WHY a specific user/endpoint session was authorized: matched policy
    set, authn rule, and authz rule with their CONDITIONS (if/then logic), the
    SGT/security group assigned, the identity source configured, and the
    failure actions (if_auth_fail, if_user_not_found, if_process_fail).

    USE THIS for a SPECIFIC user or MAC asking WHY, or about the matched rule's
    conditions, SGT, configured identity source, or failure actions.

    Supplying username or MAC queries ISE for that session directly and ignores
    `minutes`. MAC takes precedence when both are given.

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
    # Returned as a dict rather than the typed model: this view deliberately
    # projects out the SessionDetail fields already covered by
    # sessions_search_with_advanced_details. Those fields are shared on
    # SessionDetail, so the exclusion must be applied per-call here. FastMCP
    # still emits this dict as structuredContent (None values dropped by the
    # IseResultModel serializer); only the derived outputSchema is skipped.
    return result.model_dump(
        mode="json",
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
) -> LatencyEnrichedSessionSearchResult:
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
    return result


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def get_active_session_counts() -> SessionCountResult:
    """
    Return the CURRENT count of active sessions across the ISE deployment,
    broken down by type: total active, posture, and profiler.

    Takes no filters — this is a deployment-wide total, not a per-user or
    per-device count. For counts matching specific criteria, use
    active_sessions_search and read total_matching_active_sessions.

    USE THIS when asked: how many active sessions are there, how many devices
    are being profiled, how many endpoints have posture, current session count.

    posture_count and profiler_count are SUBSETS of active_count — never add
    them together or add them to active_count.
    """
    result: SessionCountResult = await session_tool_handler.get_active_session_counts()
    return result


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_investigate_aaa_failure(
    calling_station_id: Annotated[Optional[str], "Endpoint MAC."] = None,
    username: Annotated[Optional[str], "Username."] = None,
    minutes: Annotated[int, Field(ge=0, le=1440, description="Lookback minutes for the MAC auth-status search (minimum 1). Defaults to 24h; a narrower window is the usual reason this tool finds nothing.")] = 1440,
    limit: Annotated[int, Field(ge=1, le=10, description="Result cap.")] = 1,
) -> AaaFailureInvestigationResult:
    """
    Investigate the ROOT CAUSE of a RADIUS AAA authentication FAILURE for an
    endpoint or user: failure reason, cause, and resolution. Pass both MAC and
    username for best coverage.

    USE THIS only when authentication FAILED and you need why: access denied,
    failure reason, why rejected, how to fix.

    Coverage, in the order tried: the MAC's auth-status records within `minutes`;
    then the MAC's most recent session (not time-bounded, so it reaches failures
    older than the window); then the username's most recent session.
    `search_filters.source_api` reports which one answered.

    An empty result is NOT proof the authentication never happened: an
    access-reject that never created a session, and is older than `minutes`, is
    outside what MnT exposes here.
    """
    result: AaaFailureInvestigationResult = await failure_tool_handler.investigate_aaa_failure(
        mac_address=calling_station_id,
        username=username,
        minutes=minutes,
        limit=limit,
    )
    return result


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_deployment_health(
    hostnames: Annotated[
        Optional[list[str]],
        "Exact ISE node hostnames to include (OR-matched). Omit for cluster-wide "
        "health, topology, or HA questions. A filtered result describes ONLY the "
        "named nodes and cannot support deployment-wide HA/redundancy conclusions "
        "(whether a Secondary PAN exists, PAN failover readiness) — re-run without "
        "hostnames to assess HA.",
    ] = None,
    diagnostics: Annotated[
        bool,
        "Default false. When true, attach per-node diagnostics "
        "(process health + CPU/memory/latency). Opt-in: the response can be "
        "large in big deployments and the call is gated for MnT-node "
        "backpressure. Set true "
        "ONLY when the user's wording signals a problem or asks to "
        "investigate/diagnose (e.g. 'down', 'not syncing', 'out of sync', "
        "'registration failed', 'overloaded'). Keep false for general status, "
        "topology, readiness, or HA questions.",
    ] = False,
) -> DeploymentHealthResult:
    """
    Cisco ISE deployment topology and node-level health.

    USE THIS for the cluster/deployment itself: node list and topology; PAN/MnT
    roles and PAN redundancy/HA readiness; which nodes are Connected vs
    Disconnected/NotInSync; which nodes run Session/Profiler/DeviceAdmin services.

    Returns:
    - nodes[]: hostname, fqdn, ip_address, roles, services, node_status
      (e.g. Connected, Disconnected, NotInSync).
    - summary: status_counts, unhealthy_nodes, PrimaryAdmin/SecondaryAdmin
      presence, ha_ready, and verdict (healthy | degraded | critical). The
      PAN-redundancy/HA fields are populated only for a full-deployment query;
      with hostnames set the scope is "filtered" and they are null.
    - diagnostics: Present only when diagnostics=true — per-node process health
      plus CPU/memory/latency and derived observations. Nodes with a process
      reporting "down" are flagged.

    Do NOT use for: live authentication/session details (use the session tools);
    certificate expiry or TLS errors (use ise_diagnose_certificate_issues); or
    alarms, licensing, or backups (not returned). With hostnames set, do not draw
    deployment-wide HA/redundancy conclusions.
    """
    result: DeploymentHealthResult = await deployment_tool_handler.get_deployment_health(
        hostnames=hostnames,
        diagnostics=diagnostics,
    )
    return result


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_diagnose_certificate_issues(
    expiry_days: Annotated[
        int,
        Field(ge=1, le=365, description="Look-ahead window in days for the certificate expiry check."),
    ] = 30,
    status_filter: Annotated[
        str,
        "ISE certificate status to filter the expiry check on: 'all', 'enabled', "
        "or 'disabled'. Defaults to 'enabled' — only enabled trusted certificates "
        "are considered unless the user explicitly asks for all or disabled certs.",
    ] = "enabled",
    scan_logs: Annotated[
        bool,
        "Boolean, default true. When true, also scan ise-psc.log on PSN nodes for "
        "certificate/TLS error signals (handshake failures, Unknown CA, PKIX path "
        "errors, OCSP callbacks, RADIUS cert error codes, cert-management failures) "
        "in the most recent 2-hour window. Set false for a fast expiry-only check "
        "when the user only asks whether certificates are expiring/expired.",
    ] = True,
    hostnames: Annotated[
        Optional[list[str]],
        "Optional list of ISE node hostnames to restrict the log scan to. Only PSN "
        "nodes are scanned; a supplied host that is not a PSN is silently skipped. "
        "When omitted, all PSN nodes are scanned (capped at 5). Does not affect the "
        "expiry check, which always covers the whole trusted-certificate store.",
    ] = None,
    limit: Annotated[
        int,
        Field(ge=1, le=100, description="Max certificates to return in the expiry result."),
    ] = 25,
) -> CertificateDiagnosisResult:
    """
    Diagnose Cisco ISE certificate issues from two angles and return a combined
    verdict. First, list trusted CA certificates that are expired or expiring
    within expiry_days (most-urgent-first). Second, when scan_logs is true, scan
    ise-psc.log on PSN nodes for certificate/TLS error signals over the recent
    2-hour window and surface up to 5 raw matched log lines per node.

    USE THIS when the question mentions certificate expiry or renewal, OR
    certificate/TLS errors seen on PSNs: EAP-TLS/RADIUS handshake failures,
    "Unknown CA", untrusted or unknown certificate authority, PKIX/path-building
    errors, OCSP/CRL validation problems, or certificate-management failures.

    Set scan_logs=false for a quick "are any certs expiring?" check. Keep it true
    to investigate suspected live certificate/TLS failures.

    Do NOT use for node/deployment health, sessions, policy, or system identity
    certificate provisioning — use the deployment, session, or policy tools.

    Returns:
    - expiry: expiring/expired trusted certificates and aggregate counts.
    - log_scan: per-PSN-node raw matched log lines plus a "scanned X of Y PSN
      node(s)" coverage note (null when scan_logs=false).
    - verdict: critical (any expired cert or log signal), warning (expiring only),
      or healthy.
    """
    result: CertificateDiagnosisResult = await certificates_tool_handler.diagnose_certificate_issues(
        expiry_days=expiry_days,
        status_filter=status_filter,
        scan_logs=scan_logs,
        hostnames=hostnames,
        limit=limit,
    )
    return result


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
) -> PolicySetSearchResult:
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
    return result



@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_search_authorization_rules(
    policy_set_name: Annotated[Optional[str], "Restrict search to this policy set (by name). Optional — omit to search across ALL policy sets."] = None,
    profile_name_filter: Annotated[Optional[str], "Case-insensitive EXACT match on the rule's authorization profile name (e.g. 'DenyAccess' does NOT match 'DenyAccess_Guest'). Omit the filter first to see the profile names in use."] = None,
    security_group_filter: Annotated[Optional[str], "Case-insensitive EXACT match on the rule's TrustSec SGT name (e.g. 'Developers' does NOT match 'Developers_Contractors')."] = None,
    state_filter: Annotated[str, "Rule state filter: 'all', 'enabled', or 'disabled'."] = "all",
    min_hit_counts: Annotated[Optional[int], Field(ge=0, description="Lower bound: keep rules with hit_counts >= this. Use for 'hit at least N times / most used'.")] = None,
    max_hit_counts: Annotated[Optional[int], Field(ge=0, description="Upper bound: keep rules with hit_counts <= this. Use max_hit_counts=0 for 'never hit / 0 hits / unused / stale / safe to clean up', or N for 'at most N hits'.")] = None,
    name_substring: Annotated[Optional[str], "Case-insensitive substring of the rule name."] = None,
    limit: Annotated[int, Field(ge=1, le=50, description="Max rules to return, after filtering, across all scanned policy sets.")] = 25,
) -> AuthorizationRuleSearchResult:
    """
    Find authorization rules (a.k.a. "authorization policies") across policy
    sets by profile, SGT, state, hit count, or rule name. Includes global
    exception rules.

    USE THIS when: which rules assign profile X, are there global exceptions
    overriding a rule, why is a profile applied unexpectedly, find unused rules
    (max_hit_counts=0), which authorization policy/rule has the most or fewest
    hits, rank authorization rules by hit count, policy configuration questions
    not tied to a specific live session.

    Every policy set is scanned unless one is named. Confirm coverage by
    checking that `policy_sets_scanned` equals `policy_sets_total`.
    """
    result: AuthorizationRuleSearchResult = await policy_tool_handler.search_authorization_rules(
        policy_set_name=policy_set_name,
        profile_name_filter=profile_name_filter,
        security_group_filter=security_group_filter,
        state_filter=state_filter,
        min_hit_counts=min_hit_counts,
        max_hit_counts=max_hit_counts,
        name_substring=name_substring,
        limit=limit,
    )
    return result


@ise_mcp_server.tool(annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
@measure_time_async
@normalize_docstring
async def ise_search_authentication_rules(
    policy_set_name: Annotated[Optional[str], "Restrict search to this policy set (by name). Optional — omit to search across ALL policy sets."] = None,
    identity_source_filter: Annotated[Optional[str], "Case-insensitive EXACT match on the rule's identitySourceName (identity store / AD join point), e.g. 'Internal Users' or 'All_AD_Join_Points'. A substring like 'AD' or 'Guest' will NOT match."] = None,
    state_filter: Annotated[str, "Rule state filter: 'all', 'enabled', or 'disabled'."] = "all",
    min_hit_counts: Annotated[Optional[int], Field(ge=0, description="Lower bound: keep rules with hit_counts >= this. Use for 'hit at least N times / most used'.")] = None,
    max_hit_counts: Annotated[Optional[int], Field(ge=0, description="Upper bound: keep rules with hit_counts <= this. Use max_hit_counts=0 for 'never hit / 0 hits / unused / stale / safe to clean up', or N for 'at most N hits'.")] = None,
    name_substring: Annotated[Optional[str], "Case-insensitive substring of the rule name."] = None,
    limit: Annotated[int, Field(ge=1, le=50, description="Max rules to return.")] = 25,
) -> AuthenticationRuleSearchResult:
    """
    Find authentication rules in the policy CONFIGURATION across policy sets by
    identity store, state, hit count, or rule name. Returns identity_source_name
    and failure actions. Not tied to any live session.

    USE THIS when: which authn rules use identity store X (pass its exact name;
    identity_source_name in the returned rules shows the names in use), find
    unused/zero-hit authn rules (max_hit_counts=0), disabled authn rules,
    lenient failure actions.

    Every policy set is scanned unless one is named. Confirm coverage by
    checking that `policy_sets_scanned` equals `policy_sets_total`.
    """
    result: AuthenticationRuleSearchResult = await policy_tool_handler.search_authentication_rules(
        policy_set_name=policy_set_name,
        identity_source_filter=identity_source_filter,
        state_filter=state_filter,
        min_hit_counts=min_hit_counts,
        max_hit_counts=max_hit_counts,
        name_substring=name_substring,
        limit=limit,
    )
    return result




def main():
    try:
        logger.info("Starting ISE MCP Server...")
        ise_mcp_server.run(transport="streamable-http", host=HOST, port=PORT, show_banner=False)
    except Exception as e:
        logger.exception("Error starting ISE MCP Server", error=str(e))
        return 1
    return 0

if __name__ == "__main__":
    main()
