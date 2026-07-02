# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

ISE_AUTH_FLOW: str = """\
## ISE Authentication Flow
1. Endpoint (user device) connects to a network device (switch or access point).
2. The network device (NAS) sends a RADIUS Access-Request to the ISE PSN node.
3. ISE selects a Policy Set whose top-level condition matches the request.
4. The Authentication Rule inside that policy set determines HOW to verify identity (which identity store to query).
5. The Authorization Rule determines WHAT access to grant (which authorization profile to apply).
6. ISE returns RADIUS Access-Accept (with the authorization profile) or Access-Reject to the NAS."""

SESSION_IDENTIFIERS: str = """\
## Session Identifiers
- calling_station_id: MAC address of the endpoint device connecting to the network.
- nas_ip_address: IP of the network device (switch/AP) that forwarded the RADIUS request. This is NOT the endpoint's IP.
- framed_ip_address: IP address of the endpoint as reported by the network device. May be absent if not yet assigned.
- network_device_name: Friendly name of the NAS as configured in ISE device administration.
- ise_psn_node: The ISE Policy Service Node that processed this authentication request."""

SESSION_DETAILS_GLOSSARY: str = """\
## Authentication Fields
- authentication_method: How the user proved their identity.
- authentication_protocol: The outer protocol wrapping authentication.
- identity_store: Where ISE looked up the user.
- identity_group: Logical group the endpoint belongs to in ISE, used for policy matching.
- protocol: "Radius" for network access or "TACACS" for device administration.
- posture_status: Whether the endpoint passed compliance checks.
- response_time_ms: Total time ISE took to process this authentication request, in milliseconds.
- ise_policy_set_name: The top-level policy container ISE selected for this session.
- identity_policy_matched_rule: The authentication rule that matched.
- authorization_policy_matched_rule: The authorization rule that matched.
- authorization_profiles: The result of authorization -- what network access was granted."""

POLICY_GLOSSARY: str = """\
## ISE Policy Evaluation Flow
ISE evaluates policies in three steps. Each step uses top-down, first-match logic: the first rule whose condition is TRUE is selected.

### Step 1 -- Policy Set Selection
- ISE compares the incoming request against each Policy Set's top-level condition. First match wins.
- If no condition matches, the built-in "Default" Policy Set is used.

### Step 2 -- Authentication Policy (inside the selected Policy Set)
- Determines HOW to verify identity. The first matching authentication_rule determines which identity store to query and what to do on failure.
- Fallback actions (if_auth_fail, if_user_not_found, if_process_fail): REJECT = deny access, CONTINUE = try next rule, DROP = silently drop the request.

### Step 3 -- Authorization Policy (inside the selected Policy Set)
- Determines WHAT access to grant. The first matching authorization_rule determines the authorization profile and optional security group (TrustSec SGT).
- If no rule matches, ISE applies the implicit default (typically DenyAccess)."""

LATENCY_GLOSSARY: str = """\
## Latency Fields
- execution_steps: Ordered list of steps ISE performed during authentication. Each step has a human-readable message and optional latency.
- latency_ms: Time in milliseconds that a specific execution step took. High values indicate bottlenecks.
- response_time_ms: Total time ISE took to process this authentication request. Compare with per-step latency to find the bottleneck."""


FAILURE_GLOSSARY: str = """\
## AAA Failure Interpretation
- failure_cause and failure_resolution come from the ISE failure reasons catalog and explain why the failure occurred and how to fix it.
- execution_steps: Ordered list of steps ISE performed during the failing authentication, showing the flow up to the point of failure. Use these to trace where the authentication broke down."""

POLICY_CONFIG_GLOSSARY: str = """\
## Policy Configuration Glossary
- policy_set: top-level evaluation container. ISE picks the first policy set whose top-level condition is TRUE; rank determines order (lower rank evaluates first).
- policy_set.condition_summary: human-readable form of the condition that selects this policy set.
- policy_set.service_name: the allowed-protocols definition (e.g. "Default Network Access") or server sequence used by this policy set.
- policy_set.is_proxy: True if `service_name` is a Proxy Sequence rather than Allowed Protocols.
- policy_set.state: enabled = active, disabled = ignored entirely, monitor = evaluated but not enforced.
- policy_set.is_default: True for the built-in catch-all policy set used when no other policy set's condition matches.
- rank: priority of a policy set or rule. Lower rank evaluates first.
- hit_counts: how many times the policy set / rule has matched. 0 commonly indicates a stale or misconfigured rule.
- state (rule): same enabled/disabled/monitor semantics as policy sets.

## Authentication Rule Fields
- identity_source_name: the identity store the rule queries (e.g. "Internal Users", "AD:corp.example.com").
- if_auth_fail / if_user_not_found / if_process_fail: action codes — REJECT (deny), CONTINUE (try next rule), DROP (silent drop). CONTINUE on user-not-found is lenient and often a misconfiguration risk.
- condition_summary: the rule's matching condition, flattened to text.

## Authorization Rule Fields
- profile: list of authorization profile names assigned by the rule (e.g. ["PermitAccess"], ["DenyAccess"], ["Guest_Redirect"]).
- security_group: TrustSec SGT name assigned by the rule, if any.
- condition_summary: the rule's matching condition, flattened to text.

## Global Exception Rules
- Global exception rules override per-policy-set authorization rules across ALL policy sets. They are the single most common cause of "my authz rule should match but doesn't" — always check them when an unexpected profile is being applied.

## Local Exception Rules
- Per-policy-set exception rules. Evaluated BEFORE the regular authorization rules of the same policy set.

## Library Conditions
- Reusable conditions defined in the ISE conditions library. Authorization, authentication, and policy-set rules can reference them by name. The `condition_summary` flattens the condition tree to text (e.g. "Network Access:Protocol equals RADIUS").

## Policy Authoring References
- identity_stores: identity sources you can reference in authentication rules (AD joins, LDAP, Internal Users, ODBC, etc.).
- security_groups: TrustSec SGTs you can assign in authorization rules.
- service_names: Allowed Protocols definitions (service_type=allowed_protocols) or Server Sequences (service_type=server_sequence) you can attach to a policy set."""


CERTIFICATE_GLOSSARY: str = """\
## Trusted Certificate Fields
- friendly_name: Human-readable label for the certificate as configured in ISE (Administration > System > Certificates > Trusted Certificates).
- expiration_date: ISO 8601 date/time after which the certificate is no longer valid. ISE will reject it.
- valid_from: ISO 8601 date/time from which the certificate is valid.
- days_until_expiry: Whole days from now until expiration. Negative values mean the cert has already expired.
- expiry_status: expired = already past expiration date; warning = expires within the look-ahead window.
- ise_status: whether the certificate is enabled or disabled in ISE — enabled means ISE actively uses this cert for trust validation.
- trusted_for: ISE services this certificate is trusted for.
- is_referred_in_policy: True when the certificate is actively referenced in an ISE policy. Expiry of a policy-referenced cert is operationally critical and may cause authentication failures.

## Summary Fields
- total_matched: Total certificates matching the filter criteria across all scanned pages. If this exceeds the number of certificates in the returned list, there are more matching certs — increase limit or narrow the expiry_days window to see them all.
- expired_count: Number of already-expired certificates among the returned certificates.
- warning_count: Number of certificates expiring within the look-ahead window among the returned certificates.
- earliest_expiration: Expiration date of the most urgent certificate in the returned set."""


def _compose(*sections: str) -> str:
    return "\n\n".join(sections)


TOOL_GLOSSARIES: dict[str, str] = {
    "active_sessions_search": SESSION_IDENTIFIERS,
    "sessions_search_with_advanced_details": _compose(ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY),
    "sessions_search_with_policy_details": _compose(ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY, POLICY_GLOSSARY),
    "sessions_search_with_latency_details": _compose(ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY, LATENCY_GLOSSARY),
    "ise_investigate_aaa_failure": _compose(ISE_AUTH_FLOW, SESSION_IDENTIFIERS, SESSION_DETAILS_GLOSSARY, FAILURE_GLOSSARY),
    "check_expiring_trusted_certificates": CERTIFICATE_GLOSSARY,
    "ise_search_policy_sets": _compose(POLICY_GLOSSARY, POLICY_CONFIG_GLOSSARY),
    "ise_get_policy_set_details": _compose(POLICY_GLOSSARY, POLICY_CONFIG_GLOSSARY),
    "ise_search_authorization_rules": _compose(POLICY_GLOSSARY, POLICY_CONFIG_GLOSSARY),
    "ise_search_authentication_rules": _compose(POLICY_GLOSSARY, POLICY_CONFIG_GLOSSARY),
    "ise_search_authorization_profiles": POLICY_CONFIG_GLOSSARY,
    "ise_search_library_conditions": POLICY_CONFIG_GLOSSARY,
    "ise_list_policy_authoring_references": POLICY_CONFIG_GLOSSARY,
}

DEFAULT_GLOSSARY: str = ""
