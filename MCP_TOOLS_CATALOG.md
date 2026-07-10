# ISE MCP Server - Tools Catalog

This document provides a comprehensive reference for all MCP tools exposed by the ISE MCP Server.

---

## Table of Contents

- [Active Sessions](#active-sessions)
- [Policy Configuration](#policy-configuration)
- [Deployment Health](#deployment-health)
- [Certificates](#certificates)
- [Tool Selection Guide](#tool-selection-guide)
- [Data Sources](#data-sources)

---

## Active Sessions

Tools for monitoring and searching authenticated network sessions from the past X minutes.

### active_sessions_search

Fast, lightweight session search. Returns basic identifiers only (user, MAC, IPs, ISE node) for sessions authenticated in the past X minutes. Up to 20 results.

Use `sessions_search_with_advanced_details` when you also need authorization profiles, posture, or auth method details.
Use `sessions_search_with_policy_details` when you need full policy rule definitions explaining why sessions were authorized.

**Questions this tool answers:**

- "Is user iseAiUser currently authenticated on the network?"
- "Which users authenticated through switch 1.1.1.1 in the past 6 hours?"
- "What IP address was assigned to MAC 88:14:43:88:44:13?"
- "Which ISE PSN node handled sessions for user testUser?"
- "Show me all sessions on NAS 1.1.1.1 in the last 4 hours"
- "Was MAC address 78:14:43:88:44:92 seen on the network recently?"
- "How many active sessions does user iseAiUser have right now?"
- "Is the same user iseAiUser authenticating from multiple NAS devices?"
- "What is the audit session id for user iseAiUser's session so I can trace it in ISE logs?"
- "Are there any sessions handled by ISE node ise-ai in the past 3 hours?"
- "Does endpoint 88:14:43:88:44:92 have an IPv6 address assigned?"
- "Is endpoint with mac address 48:16:37:18:44:92 currently authenticated, and which NAS handled it in the last 10 min?"
- "Is the same username 'iseAiUser' authenticating from more than one NAS in the last 30 minutes?"


| Parameter            | Type    | Required | Default | Description                                                                                        |
| -------------------- | ------- | -------- | ------- | -------------------------------------------------------------------------------------------------- |
| `username`           | string  | No       | None    | Filter by authenticated username                                                                   |
| `calling_station_id` | string  | No       | None    | Filter by endpoint MAC address (supports XX:XX:XX, XX-XX-XX, XXXXXXXXXXXX, XXXX.XXXX.XXXX formats) |
| `nas_ip_address`     | string  | No       | None    | Filter by network device IP address (exact match)                                                  |
| `framed_ip_address`  | string  | No       | None    | Filter by IP address assigned to the endpoint (exact match)                                        |
| `server`             | string  | No       | None    | Filter by ISE node handling the session                                                            |
| `minutes`            | integer | No       | 60      | Number of minutes to look back for authenticated sessions (default: 60, max: 1440)                 |
| `limit`              | integer | No       | 10      | Maximum results to return (default: 10, max: 20)                                                   |

**Returns:** JSON object with:

- `search_filters`: Search filters that were used to find sessions
- `total_matching_sessions`: Total number of sessions matching the filters in ISE (the true count; the list below may contain fewer)
- `sample_size`: Number of sessions included in `sample_sessions` below (may be smaller than `total_matching_sessions` due to the result limit)
- `sample_sessions`: A representative SAMPLE of matching sessions, capped by `limit` to fit the model context window. These are real sessions but NOT the complete set — cite `total_matching_sessions` for the true count. Each object contains:
  - `user_name`: Username of the authenticated user
  - `calling_station_id`: MAC address of the endpoint device
  - `nas_ip_address`: IP address of the Network Access Server (switch/access point)
  - `server`: ISE node handling the session
  - `framed_ip_address`: IP address assigned to the endpoint (may be null)
  - `framed_ipv6_address`: IPv6 address assigned to the endpoint (may be null)
  - `audit_session_id`: Audit session ID for the session (may be null)
  - `acct_session_id`: Accounting session ID for the session (may be null)
  - `nas_ipv6_address`: IPv6 address of the Network Access Server (may be null)
- `sampling_note`: Present ONLY when the list is a truncated sample; states how many of the total matching sessions are shown. Absent when all results are returned or none matched.

**Example response:**

```json
{
  "search_filters": {
    "minutes": 60,
    "nas_ip_address": "1.1.1.1"
  },
  "total_matching_sessions": 2,
  "sample_size": 2,
  "sample_sessions": [
    {
      "user_name": "iseAiUser",
      "calling_station_id": "88:14:43:88:44:92",
      "nas_ip_address": "1.1.1.1",
      "server": "itwito-2",
      "framed_ip_address": "10.1.10.120",
      "framed_ipv6_address": null,
      "audit_session_id": "0A50963200000000C2E7E7E5",
      "acct_session_id": "00000001",
      "nas_ipv6_address": null
    },
    {
      "user_name": "testUser",
      "calling_station_id": "78:14:43:88:44:92",
      "nas_ip_address": "1.1.1.1",
      "server": "itwito-2",
      "framed_ip_address": "10.1.10.120",
      "framed_ipv6_address": null,
      "audit_session_id": "0A50963200000000C2E7E7E6",
      "acct_session_id": "00000002",
      "nas_ipv6_address": null
    }
  ]
}
```

**Example response (truncated sample):**

```json
{
  "search_filters": {
    "minutes": 60,
    "username": "iseAiUser"
  },
  "total_matching_sessions": 47,
  "sample_size": 10,
  "sample_sessions": [
    {
      "user_name": "iseAiUser",
      "calling_station_id": "88:14:43:88:44:92",
      "nas_ip_address": "1.1.1.1",
      "server": "itwito-2",
      "framed_ip_address": "10.1.10.120"
    }
  ],
  "sampling_note": "This is a SAMPLE of 10 out of 47 matching sessions, capped by the result limit. Treat it as a representative example, not an exhaustive list."
}
```

**Use when:**

- You need to find authenticated sessions from the past X minutes
- Troubleshooting recent connectivity issues for a specific user or device
- Verifying if a user or device authenticated recently (within past 60 minutes by default)
- Checking which ISE node handled sessions in a specific time window
- Finding all sessions on a specific network device (switch/AP) during a time period
- Looking up the IP address assigned to a specific user in recent sessions
- Investigating session patterns over the past few minutes or hours
- Checking current or recent authentication activity

**Do not use when:**

- You need authorization profiles, auth method, posture status, or identity store details (use `sessions_search_with_advanced_details`)
- You need to understand WHY sessions were authorized with full policy rule definitions (use `sessions_search_with_policy_details`)
- You need detailed accounting data with session duration and data transfer (use RADIUS accounting tools instead)
- You want to see failed authentication attempts (use authentication failure tools)
- You need session statistics or aggregated data (use RADIUS accounting summary tools)
- You want to analyze termination causes (use RADIUS accounting tools)

**Best practices:**

- Use specific filters to narrow results and conserve agent context
- Adjust the minutes parameter based on your needs (e.g., minutes=360 for the past 6 hours)
- Combine multiple filters for precise searches (e.g., username + NAS IP + minutes)
- MAC address format is automatically normalized (any format works)
- Exact matching for username
- Use limit parameter to control result size in large deployments
- Default 60-minute (1-hour) window is suitable for most recent activity queries

---

### sessions_search_with_advanced_details

Session search enriched with WHAT happened: authorization profile, auth method, posture status, identity group, network device name, identity store, response time, and matched policy/rule names. Combines the AuthList API (session list) with the Last Session by Attributes API (detail per session). Slower than `active_sessions_search` (extra API call per session). limit default 1, max 10.

Use `active_sessions_search` for fast identifier-only lookups.
Use `sessions_search_with_policy_details` for full policy rule definitions.

**Questions this tool answers:**

- "What authentication method and protocol were used for user iseAiUser?"
- "Did user iseAiUser pass authentication, and what's their posture status?"
- "What authorization profile is currently applied to iseAiUser's session?"
- "Which authorization profile and identity group were applied to testUser's session in the last 2 hours?"
- "What posture status and authorization profile were applied to sessions in the past hour?"
- "What posture status and authorization profile were applied to endpoint 88:14:43:88:44:92's session?"
- "For user iseAiUser, which authorization profile name was applied and was the result a pass or fail?"
- "Which authentication method and authorization profile were applied to testUser's most recent session?"


| Parameter            | Type    | Required | Default | Description                                                  |
| -------------------- | ------- | -------- | ------- | ------------------------------------------------------------ |
| `username`           | string  | No       | None    | Filter by authenticated username                                              |
| `calling_station_id` | string  | No       | None    | Filter by endpoint MAC address (any format)                                   |
| `minutes`            | integer | No       | 60      | Number of minutes to look back (default: 60, max: 1440)                      |
| `limit`              | integer | No       | 1       | Number of sessions to enrich and return (default: 1, max: 10)                |


**Returns:** JSON object with:

- `search_filters`: Search filters that were used to find sessions
- `total_sessions_found`: Total number of sessions that matched the search filters
- `actual_sessions_returned`: Number of enriched sessions included in the sessions list below
- `sessions`: Array of enriched session objects, each containing:
  - `authentication_result`: Authentication result: Passed or Failed
  - `user_name`: Username of the authenticated user
  - `nas_ip_address`: IP address of the Network Access Server
  - `calling_station_id`: Endpoint MAC address
  - `identity_group`: Identity group
  - `network_device_name`: Network device name as defined in ISE
  - `ise_psn_node`: ISE PSN node name that handled the session
  - `authentication_method`: Authentication method used (e.g., PAP_ASCII, MSCHAPV2)
  - `authentication_protocol`: Authentication protocol used (e.g., PAP_ASCII, PEAP)
  - `framed_ip_address`: IP address assigned to the endpoint (may be null)
  - `auth_acs_timestamp`: Authentication timestamp (ISO 8601)
  - `posture_status`: Posture status (may be null)
  - `authorization_profiles`: Authorization profile applied (e.g., PermitAccess)
  - `identity_store`: Identity store used for authentication (e.g., Internal Users, AD)
  - `response_time_ms`: Response time in milliseconds
  - `identity_policy_matched_rule`: Name of the matched authentication rule
  - `protocol`: Protocol used (e.g., Radius, TACACS)
  - `ise_policy_set_name`: Name of the ISE policy set that was applied
  - `authorization_policy_matched_rule`: Name of the matched authorization rule

**Example response:**

```json
{
  "search_filters": {
    "minutes": 60,
    "username": "testUser"
  },
  "total_sessions_found": 1,
  "actual_sessions_returned": 1,
  "sessions": [
    {
      "authentication_result": "Passed",
      "user_name": "testUser",
      "nas_ip_address": "1.1.1.1",
      "calling_station_id": "78:14:43:88:44:92",
      "identity_group": "Unknown",
      "network_device_name": "DefaultNetworkDevice",
      "ise_psn_node": "itwito-2",
      "authentication_method": "PAP_ASCII",
      "authentication_protocol": "PAP_ASCII",
      "framed_ip_address": "10.1.10.120",
      "auth_acs_timestamp": "2026-03-04T15:54:56.921+02:00",
      "posture_status": null,
      "authorization_profiles": "PermitAccess",
      "identity_store": "Internal Users",
      "response_time_ms": 71,
      "identity_policy_matched_rule": "Authentication Rule 1",
      "protocol": "Radius",
      "ise_policy_set_name": "iseAiPolicy",
      "authorization_policy_matched_rule": "Authorization Rule 1"
    }
  ]
}
```

**Use when:**

- You need both "who is on the network" and "what auth profiles / posture / methods" for those sessions
- Troubleshooting across multiple active sessions with full detail in one call
- Checking which identity store or authentication method was used for recent sessions
- Investigating posture status or response times for active sessions

**Do not use when:**

- You only need a quick list of active sessions with basic identifiers (use `active_sessions_search`)
- You need more than 10 sessions (tool caps at 10; use `active_sessions_search` for broader searches with up to 20 results)
- You need to understand WHY sessions were authorized with full policy rule definitions (use `sessions_search_with_policy_details`)

**Best practices:**

- Use filters (username or calling_station_id) to narrow to the relevant sessions before enriching
- limit defaults to 1 (max 10) to balance detail vs. API load; lower it only when you need fewer sessions

---

### sessions_search_with_policy_details

Session search enriched with WHY it was authorized: resolves full policy set, authentication rule, and authorization rule definitions from the ISE Policy API. Combines the AuthList API, the Last Session by Attributes API, and the Policy API. Slowest tool (multiple API calls per session). Caches duplicate policy lookups across sessions. limit default 1, max 10.

Use `active_sessions_search` for fast identifier-only lookups.
Use `sessions_search_with_advanced_details` for auth profiles/posture only.

**Questions this tool answers:**

- "What authorization profile was applied to user iseAiUser's session?"
- "Why was user iseAiUser session authorized with PermitAccess profile? what policy rules led to that decision?"
- "What is the full condition logic of the authorization rule that matched iseAiUser's session?"
- "Which identity source (Internal Users, AD) is configured in the authentication rule for iseAiUser's session?"
- "What security group (TrustSec SGT) is assigned by the authorization rule for iseAiUser's session?"
- "Is the if process fail action set to DROP or CONTINUE for the authentication rule matching iseAiUser's session?"
- "What is the condition summary for the authentication rule that matched user iseAiUser's session?"
- "Why did iseAiUser's session match Authorization Rule 1 with profile PermitAccess — show me the full condition summary of the matched policy set, authn rule, and authz rule."
- "Is session of endpoint with mac address 78:14:43:88:44:92 still hitting the 'Default' policy authorization rule?"


| Parameter            | Type    | Required | Default | Description                                                  |
| -------------------- | ------- | -------- | ------- | ------------------------------------------------------------ |
| `username`           | string  | No       | None    | Filter by authenticated username                                              |
| `calling_station_id` | string  | No       | None    | Filter by endpoint MAC address (any format)                                   |
| `minutes`            | integer | No       | 60      | Number of minutes to look back (default: 60, max: 1440)                      |
| `limit`              | integer | No       | 1       | Number of sessions to enrich and return (default: 1, max: 10)                |


**Returns:** JSON object with:

- `search_filters`: Search filters that were used to find sessions
- `total_sessions_found`: Total number of sessions that matched the search filters
- `actual_sessions_returned`: Number of sessions included in the sessions list below
- `sessions`: Array of objects, each containing:
  - `session`: Detailed session data (same fields as `sessions_search_with_advanced_details`)
  - `policy_context`: Resolved policy configuration:
    - `policy_set`: name, description, condition_summary
    - `authentication_rule`: name, identity_source_name, if_auth_fail, if_user_not_found, if_process_fail, condition_summary
    - `authorization_rule`: name, profile, security_group, condition_summary
    - `resolution_errors`: list of errors if resolution failed (null otherwise)
  - `policy_context_note`: present instead of `policy_context` when no policy set name is found in session data

**Example response:**

```json
{
  "search_filters": {
    "minutes": 60,
    "username": "iseAiUser"
  },
  "total_sessions_found": 2,
  "actual_sessions_returned": 2,
  "sessions": [
    {
      "session": {
        "authentication_result": "Passed",
        "user_name": "iseAiUser",
        "nas_ip_address": "1.1.1.1",
        "calling_station_id": "88:14:43:88:44:92",
        "identity_group": "Unknown",
        "network_device_name": "DefaultNetworkDevice",
        "ise_psn_node": "itwito-2",
        "authentication_method": "PAP_ASCII",
        "authentication_protocol": "PAP_ASCII",
        "framed_ip_address": "10.1.10.120",
        "auth_acs_timestamp": "2026-03-04T15:54:56.921+02:00",
        "posture_status": null,
        "authorization_profiles": "PermitAccess",
        "identity_store": "Internal Users",
        "response_time_ms": 71,
        "identity_policy_matched_rule": "Authentication Rule 1",
        "protocol": "Radius",
        "ise_policy_set_name": "iseAiPolicy",
        "authorization_policy_matched_rule": "Authorization Rule 1"
      },
      "policy_context": {
        "policy_set": {
          "name": "iseAiPolicy",
          "description": null,
          "condition_summary": "Network Access:Protocol equals RADIUS"
        },
        "authentication_rule": {
          "name": "Authentication Rule 1",
          "identity_source_name": "Internal Users",
          "if_auth_fail": "REJECT",
          "if_user_not_found": "REJECT",
          "if_process_fail": "DROP",
          "condition_summary": "Network Access:Protocol equals RADIUS"
        },
        "authorization_rule": {
          "name": "Authorization Rule 1",
          "profile": ["PermitAccess"],
          "security_group": null,
          "condition_summary": "NOT Network Access:Protocol equals TACACS+"
        },
        "resolution_errors": null
      }
    },
    {
      "session": {
        "authentication_result": "Passed",
        "user_name": "testUser",
        "nas_ip_address": "1.1.1.1",
        "calling_station_id": "78:14:43:88:44:92",
        "identity_group": "Unknown",
        "network_device_name": "DefaultNetworkDevice",
        "ise_psn_node": "itwito-2",
        "authentication_method": "PAP_ASCII",
        "authentication_protocol": "PAP_ASCII",
        "framed_ip_address": "10.1.10.120",
        "auth_acs_timestamp": "2026-03-04T15:48:12.105+02:00",
        "authorization_profiles": "PermitAccess",
        "identity_store": "Internal Users",
        "response_time_ms": 65,
        "identity_policy_matched_rule": "Authentication Rule 1",
        "protocol": "Radius",
        "ise_policy_set_name": "iseAiPolicy",
        "authorization_policy_matched_rule": "Authorization Rule 1"
      },
      "policy_context": {
        "policy_set": {
          "name": "iseAiPolicy",
          "description": null,
          "condition_summary": "Network Access:Protocol equals RADIUS"
        },
        "authentication_rule": {
          "name": "Authentication Rule 1",
          "identity_source_name": "Internal Users",
          "if_auth_fail": "REJECT",
          "if_user_not_found": "REJECT",
          "if_process_fail": "DROP",
          "condition_summary": "Network Access:Protocol equals RADIUS"
        },
        "authorization_rule": {
          "name": "Authorization Rule 1",
          "profile": ["PermitAccess"],
          "security_group": null,
          "condition_summary": "NOT Network Access:Protocol equals TACACS+"
        },
        "resolution_errors": null
      }
    }
  ]
}
```

**Use when:**

- You need to understand WHY multiple sessions were authorized the way they were
- Comparing policy decisions across active sessions (e.g., different users on the same NAS)
- Troubleshooting policy-related issues for a group of sessions
- Auditing which policy sets, authentication rules, and authorization rules are being applied

**Do not use when:**

- You only need session details without policy resolution (use `sessions_search_with_advanced_details`)
- You only need a quick list of active sessions with basic identifiers (use `active_sessions_search`)

**Best practices:**

- Use filters (username or calling_station_id) to narrow sessions before enriching to reduce API calls
- Sessions sharing the same policy set and rules reuse cached policy lookups automatically
- limit defaults to 1 (max 10); reduce only if you need fewer sessions

---

### sessions_search_with_latency_details

Session search enriched with per-step latency breakdown: resolves each ISE authentication execution step code into its human-readable message and attaches the latency (ms) for each step. Combines the AuthList API (session list), the Last Session by Attributes API (detail per session), and the ISE message catalog (step code resolution). Supports filtering by total response time range. limit default 1, max 10.

Use `active_sessions_search` for fast identifier-only lookups.
Use `sessions_search_with_advanced_details` for auth profiles/posture only.
Use `sessions_search_with_policy_details` for full policy rules.

**Questions this tool answers:**

- "What is the full latency breakdown for MAC 01:23:49:67:FF:F1's session?"
- "What is the full latency breakdown for KventinClientECDSA's session?"
- "Is there any session for user KventinClientECDSA in the past 6 hours with a total response time exceeding 200ms?"
- "Are there sessions where the total response time is under 100ms (healthy baseline)?"
- "Show me sessions with latency between 200ms and 1000ms in the past 12 hours"
- "Show me last session of iseAiUser broken down by per-step latency"


| Parameter            | Type    | Required | Default | Description                                                    |
| -------------------- | ------- | -------- | ------- | -------------------------------------------------------------- |
| `username`           | string  | No       | None    | Filter by authenticated username                                              |
| `calling_station_id` | string  | No       | None    | Filter by endpoint MAC address (any format)                                   |
| `min_latency_ms`     | integer | No       | None    | Only include sessions with response_time_ms >= this value (ms)                |
| `max_latency_ms`     | integer | No       | None    | Only include sessions with response_time_ms <= this value (ms)                |
| `minutes`            | integer | No       | 60      | Number of minutes to look back (default: 60, max: 1440)                      |
| `limit`              | integer | No       | 1       | Sessions to return (default: 1, max: 10)                                      |


**Returns:** JSON object with:

- `search_filters`: Search filters that were used to find sessions (includes `min_latency_ms` and/or `max_latency_ms` when set)
- `total_sessions_found`: Total number of sessions that matched the search filters
- `actual_sessions_returned`: Number of sessions included in the sessions list below
- `sessions`: Array of objects, each containing:
  - `session`: Detailed session data (same fields as `sessions_search_with_advanced_details`)
  - `execution_steps`: Array of resolved execution steps, each containing:
    - `text`: Human-readable message for the step (e.g., "Received RADIUS Access-Request"). Null if the step code was not found in the message catalog
    - `latency_ms`: Latency in milliseconds for this step (may be null if latency data is unavailable for this step)
  - `latency_context_note`: Present when execution steps could not be resolved or some step codes were missing from the message catalog

**Example response:**

```json
{
  "search_filters": {
    "minutes": 60,
    "username": "iseAiUser",
    "min_latency_ms": 100
  },
  "total_sessions_found": 1,
  "actual_sessions_returned": 1,
  "sessions": [
    {
      "session": {
        "authentication_result": "Passed",
        "user_name": "iseAiUser",
        "nas_ip_address": "1.1.1.1",
        "calling_station_id": "88:14:43:88:44:92",
        "identity_group": "Unknown",
        "network_device_name": "DefaultNetworkDevice",
        "ise_psn_node": "itwito-2",
        "authentication_method": "PAP_ASCII",
        "authentication_protocol": "PAP_ASCII",
        "framed_ip_address": "10.1.10.120",
        "auth_acs_timestamp": "2026-03-04T15:54:56.921+02:00",
        "posture_status": null,
        "authorization_profiles": "PermitAccess",
        "identity_store": "Internal Users",
        "response_time_ms": 621,
        "identity_policy_matched_rule": "Default",
        "protocol": "Radius",
        "ise_policy_set_name": "Default",
        "authorization_policy_matched_rule": "Basic_Authenticated_Access"
      },
      "execution_steps": [
        {"text": "Received RADIUS Access-Request", "latency_ms": 0},
        {"text": "RADIUS created a new session", "latency_ms": 0},
        {"text": "Evaluating Policy Group", "latency_ms": 0},
        {"text": "Evaluating Authentication Policy", "latency_ms": 1},
        {"text": "Evaluating local identity stores", "latency_ms": 0},
        {"text": "Looking up user in Internal Users IDStore", "latency_ms": 3},
        {"text": "Internal Users authentication is successful", "latency_ms": 5},
        {"text": "Evaluating Authorization Policy", "latency_ms": 5},
        {"text": "Internal Users authentication is successful", "latency_ms": 2},
        {"text": "Selected Authorization Profile - PermitAccess", "latency_ms": 0},
        {"text": "Cisco ISE RADIUS is exiting the AAA framework", "latency_ms": 60},
        {"text": "User authentication against Active Directory succeeded", "latency_ms": 0},
        {"text": "Authentication Passed", "latency_ms": 0},
        {"text": "Endpoint conducted several failed authentications", "latency_ms": 1},
        {"text": "Evaluating Post-Authentication Policy", "latency_ms": 0},
        {"text": "ISE has completed the AAA framework processing", "latency_ms": 2},
        {"text": "Starting the AAA framework for MAB request", "latency_ms": 14},
        {"text": "Returned RADIUS Access-Accept", "latency_ms": 0}
      ],
      "latency_context_note": null
    }
  ]
}
```

**Use when:**

- You need to diagnose slow authentication and identify which step is the bottleneck
- Troubleshooting high response_time_ms values reported by `sessions_search_with_advanced_details`
- Investigating whether identity store lookups (AD, LDAP, Internal Users) are causing latency
- Comparing per-step latency across different users or endpoints to find patterns
- Filtering sessions by response time range to find only slow (or fast) authentications
- Understanding the full ISE authentication flow step-by-step for a specific session
- Verifying whether EAP/TLS handshake, policy evaluation, or identity lookup is the slow phase

**Do not use when:**

- You only need session details without latency breakdown (use `sessions_search_with_advanced_details`)
- You only need a quick list of active sessions with basic identifiers (use `active_sessions_search`)
- You need to understand WHY sessions were authorized with full policy rule definitions (use `sessions_search_with_policy_details`)
- You need more than 10 sessions (tool caps at 10; use `active_sessions_search` for broader searches with up to 20 results)

**Best practices:**

- Use `min_latency_ms` to focus on slow sessions (e.g., `min_latency_ms=500` to find sessions taking over 500ms)
- Use both `min_latency_ms` and `max_latency_ms` to define a latency range window
- When latency filters are active, the tool enriches up to 100 sessions internally before filtering, so results are more comprehensive than the result limit suggests
- Use filters (username or calling_station_id) to narrow sessions before enriching to reduce API calls
- Look for steps with high `latency_ms` values to pinpoint the bottleneck in the authentication flow
- Steps with `text: null` indicate step codes not found in the message catalog; check `latency_context_note` for details
- Combine with `sessions_search_with_policy_details` for the same session to get both latency breakdown and policy context

---

### ise_investigate_aaa_failure

Investigate RADIUS AAA authentication failures for a specific endpoint or user. Finds the latest failing authentication(s) and returns a compact failure summary including failure reason, cause, resolution, and the full execution step trace with human-readable messages.

Lookup priority: MAC address (AuthStatus API) is tried first. If no failure is found and a username is also provided, falls back to the Session API. Pass both identifiers when available for best coverage.

Use `active_sessions_search` to check if a user is connected.
Use `sessions_search_with_latency_details` for latency analysis.

**Questions this tool answers:**

- "Why did authentication fail for MAC 18:16:67:18:44:92?"
- "What is the failure reason for endpoint 18:16:67:18:44:92?"
- "Why is user with MAC 18:16:67:18:44:92 getting Access-Reject?"
- "Show me the latest authentication failure for endpoint 18:16:67:18:44:92"
- "Why has session failed for testUser in the past two hours?"


| Parameter     | Type    | Required | Default | Description                                                                              |
| ------------- | ------- | -------- | ------- | ---------------------------------------------------------------------------------------- |
| `mac_address` | string  | No*      | None    | Endpoint MAC address (supports XX:XX:XX, XX-XX-XX, XXXXXXXXXXXX, XXXX.XXXX.XXXX formats) |
| `username`    | string  | No*      | None    | Username to search for failing authentication                                             |
| `minutes`     | integer | No       | 60      | Minutes to look back (default: 60, max: 1440). Only applies to MAC address lookup        |
| `limit`       | integer | No       | 1       | Max failing authentications to return (min 1, max 10). Only applies to MAC address lookup  |


At least one of `mac_address` or `username` is required.

**Returns:** JSON object with:

- `search_filters`: Search filters used for the investigation (includes `source_api` indicating which API found failures)
- `total_failures_found`: Total number of failures matching the search
- `actual_failures_returned`: Number of failures included in this response
- `has_more`: True when more failures exist beyond the returned set
- `failures`: Array of failure detail objects, each containing:
  - `user_name`: Username of the authenticated user
  - `calling_station_id`: Endpoint MAC address
  - `nas_ip_address`: IP of the network device (switch/AP), NOT the endpoint IP
  - `framed_ip_address`: IP assigned to the endpoint (may be null)
  - `network_device_name`: Network device name as defined in ISE
  - `acs_server`: ISE PSN node that processed the authentication
  - `authentication_method`: Authentication method used (e.g. PAP_ASCII)
  - `authentication_protocol`: Authentication protocol used (e.g. PAP_ASCII, PEAP)
  - `identity_store`: Identity store queried (e.g. Internal Users, AD)
  - `timestamp`: Authentication timestamp (ISO 8601)
  - `failure_reason_code`: Numeric failure reason code (e.g. "22040")
  - `failure_reason_text`: Short failure description (e.g. "Wrong password")
  - `failure_cause`: Why it failed, from ISE FailureReasons catalog
  - `failure_resolution`: How to fix it, from ISE FailureReasons catalog
  - `response`: Raw RADIUS response (e.g. "RadiusPacketType=AccessReject")
  - `execution_steps`: Ordered authentication flow steps, each with:
    - `text`: Human-readable step message (null if code not found in catalog)
  - `failure_context_note`: Present when enrichment is partial (e.g. unknown failure code)

**Example response:**

```json
{
  "search_filters": {
    "mac_address": "78:14:43:88:44:92",
    "minutes": 60,
    "source_api": "AuthStatus"
  },
  "total_failures_found": 1,
  "actual_failures_returned": 1,
  "has_more": false,
  "failures": [
    {
      "user_name": "testUser",
      "calling_station_id": "78:14:43:88:44:92",
      "nas_ip_address": "1.1.1.1",
      "framed_ip_address": "10.1.10.120",
      "network_device_name": "DefaultNetworkDevice",
      "acs_server": "itwito-1",
      "authentication_method": "PAP_ASCII",
      "authentication_protocol": "PAP_ASCII",
      "identity_store": "Internal Users",
      "timestamp": "2026-04-29T14:30:29.958+03:00",
      "failure_reason_code": "22040",
      "failure_reason_text": "Wrong password",
      "failure_cause": "The user provided an incorrect password.",
      "failure_resolution": "Verify the user credentials and try again.",
      "response": "{RadiusPacketType=AccessReject; AuthenticationResult=Failed; }",
      "execution_steps": [
        {"text": "Received RADIUS Access-Request"},
        {"text": "RADIUS created a new session"},
        {"text": "Evaluating Policy Group"},
        {"text": "Evaluating Authentication Policy"},
        {"text": "Wrong password"}
      ]
    }
  ]
}
```

**Use when:**

- You need to find out why authentication failed for a specific endpoint or user
- Troubleshooting Access-Reject responses
- Investigating repeated authentication failures
- Understanding the root cause and resolution for AAA failures

**Do not use when:**

- You need to check if a user is currently connected (use `active_sessions_search`)
- You need latency analysis for slow but passing authentications (use `sessions_search_with_latency_details`)
- You need policy rule details for passing sessions (use `sessions_search_with_policy_details`)

**Best practices:**

- Provide both MAC address and username when available for best coverage
- MAC lookup searches a configurable time window (default 60 minutes); username lookup returns only the latest session
- Default `limit=1` returns only the most recent failure — increase to see patterns across multiple failures
- Use the `failure_cause` and `failure_resolution` fields to guide troubleshooting actions
- The `execution_steps` trace shows exactly where in the authentication flow the failure occurred

---

## Policy Configuration

Read-only tools for auditing Cisco ISE Network Access (RADIUS) policy configuration directly — independent of any live session. All tools take and return NAMES only; UUIDs are an internal implementation detail and never appear in tool inputs or outputs. All tools use `GET` endpoints exclusively.

### ise_search_policy_sets

List Network Access policy sets in evaluation order (rank ascending) with their state, hit counts, default flag, condition summary, and associated allowed-protocols / server-sequence service.

Use `ise_search_authorization_rules` to find rules across all policy sets by profile / SGT / state / hit-count.
Use `ise_search_authentication_rules` to find authentication rules across all policy sets by identity store / state / hit-count.

**Questions this tool answers:**

- "What policy sets are configured and in what evaluation order?"
- "Which policy set is the default?"
- "Are there any disabled policy sets?"
- "Are any policy sets in monitor mode?"
- "Which policy sets have never been hit?" / "List all policy sets with 0 hit counts in rank order."
- "Which policy sets are rarely used (<= N hits)?"
- "Find all policy sets with 'Wired' in the name."

| Parameter        | Type    | Required | Default | Description                                                                                                                                                      |
| ---------------- | ------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name_substring` | string  | No       | None    | Case-insensitive substring filter on policy-set name                                                                                                             |
| `state_filter`   | string  | No       | "all"   | One of `all`, `enabled`, `disabled`, `monitor`                                                                                                                   |
| `limit`          | integer | No       | 20      | Max policy sets to return (range 1-100)                                                                                                                          |
| `min_hit_counts` | integer | No       | None    | Keep only policy sets with `hit_counts >= min_hit_counts` (>= 0). Missing hit counts treated as 0.                                                               |
| `max_hit_counts` | integer | No       | None    | Keep only policy sets with `hit_counts <= max_hit_counts` (>= 0). Use `max_hit_counts=0` to find stale / never-hit policy sets. Missing hit counts treated as 0. |


**Returns:** JSON object with `search_filters`, `total_count`, `count`, `has_more`, and `policy_sets[]` sorted by `rank` ASC. Each policy set carries: `name`, `description`, `state`, `rank`, `hit_counts`, `is_default`, `service_name`, `is_proxy`, `condition_summary`. Use `name` to chain into `ise_search_authorization_rules` or `ise_search_authentication_rules`.

---

### ise_search_authorization_rules

Search authorization rules across one or all policy sets, filtered by profile, security group, state, hit count, or rule name. **Always also returns global exception rules** matching the same filters — global exceptions override per-policy-set authz rules across ALL policy sets and are the most common gotcha when troubleshooting "why is my rule not matching?".

Use `ise_search_policy_sets` to discover policy set names to pass via `policy_set_name`.

**Questions this tool answers:**

- "Which authorization rules assign the 'DenyAccess' profile?"
- "Find all authorization rules using 'PermitAccess'."
- "Which authz rules assign the 'Developers' SGT?"
- "Are there any disabled authorization rules?"
- "Which authz rules have zero hits — unused and safe to clean up?"
- "Are there global exception rules overriding my per-policy-set authz rules?"
- "A user is getting 'DenyAccess' even though my policy set rule should permit — are there global exceptions?"
- "Find all authz rules that start with 'Wi-Fi' in their name across all policy sets."
- "A user is getting Block_Wireless_Access profile even though my policy-set rule should permit — are there global exceptions (or rules assigning Block_Wireless_Access elsewhere) overriding my intended authorization?"


| Parameter               | Type    | Required | Default | Description                                                                           |
| ----------------------- | ------- | -------- | ------- | ------------------------------------------------------------------------------------- |
| `policy_set_name`       | string  | No       | None    | Restrict to this policy set (strongly recommended to narrow fan-out)                  |
| `profile_name_filter`   | string  | No       | None    | Case-insensitive substring matched against profile name(s)                            |
| `security_group_filter` | string  | No       | None    | Case-insensitive substring matched against TrustSec SGT name                          |
| `state_filter`          | string  | No       | "all"   | One of `all`, `enabled`, `disabled`                                                   |
| `min_hit_counts`        | integer | No       | None    | Only include rules with hit_counts >= this value (use 0 for unused)                   |
| `name_substring`        | string  | No       | None    | Case-insensitive substring of the rule name                                           |
| `limit`                 | integer | No       | 25      | Max per-policy-set rules (range 1-50). Global exceptions are not subject to this cap. |


**Returns:** JSON object with `search_filters`, `total_count`, `count`, `has_more`, `policy_sets_scanned`, `rules[]` (per-policy-set hits with `policy_set_name`, `name`, `rank`, `state`, `hit_counts`, `profile`, `security_group`, `condition_summary`), `global_exceptions[]` (no `policy_set_name`), and `global_exceptions_note` (steering string).

**Best practices:**

- Always provide `policy_set_name` when known — fan-out across all policy sets scans up to 25 policy sets and is significantly slower.
- Use `min_hit_counts=0` to find unused rules.
- The `global_exceptions` array is always returned; always inspect it when investigating why an unexpected profile was applied.

---

### ise_search_authentication_rules

Search authentication rules across one or all policy sets, filtered by identity store, state, hit count, or rule name. Returns each rule's `identity_source_name` and the `if_auth_fail` / `if_user_not_found` / `if_process_fail` fallback actions so lenient configurations (e.g. `CONTINUE` on user-not-found) are visible.

Use `ise_search_policy_sets` to discover policy set names to pass via `policy_set_name`.

**Questions this tool answers:**

- "Which authentication rules use Active Directory?"
- "Find all authn rules pointing to 'Internal Users'."
- "Which policy sets have authn rules that query 'Guest Users' identity store?"
- "In 'Active Directory Authentication Rule' authn rule, what is the action if user not found?"
- "Are there any disabled authentication rules?"
- "Which authn rules have zero hits?"
- "Which authn rules reference an identity store named 'OldAD_Server' that we are decommissioning?"
- "Which authentication rules reference the identity store named 'Guest Users' — and what are their 'user not found' / auth fail fallback actions?"


| Parameter                | Type    | Required | Default | Description                                        |
| ------------------------ | ------- | -------- | ------- | -------------------------------------------------- |
| `policy_set_name`        | string  | No       | None    | Restrict to this policy set (strongly recommended) |
| `identity_source_filter` | string  | No       | None    | Case-insensitive substring of `identitySourceName` |
| `state_filter`           | string  | No       | "all"   | One of `all`, `enabled`, `disabled`                |
| `min_hit_counts`         | integer | No       | None    | Only include rules with hit_counts >= this value   |
| `name_substring`         | string  | No       | None    | Case-insensitive substring of the rule name        |
| `limit`                  | integer | No       | 25      | Max rules to return (range 1-50)                   |


**Returns:** JSON object with `search_filters`, `total_count`, `count`, `has_more`, `policy_sets_scanned`, and `rules[]` (each: `policy_set_name`, `name`, `rank`, `state`, `hit_counts`, `identity_source_name`, `if_auth_fail`, `if_user_not_found`, `if_process_fail`, `condition_summary`).

---

## Deployment Health

Read-only tool for inspecting the Cisco ISE deployment itself — node inventory, personas/roles, services, node status, PAN redundancy/HA readiness, and an overall health verdict. Sourced from the ISE Deployment API (`GET /api/v1/deployment/node`), with optional log-derived per-node system statistics.

### ise_deployment_health

Returns Cisco ISE deployment topology and node-level deployment health. Use it for questions about the cluster/deployment itself: which nodes exist, which node is Primary/Secondary PAN, which nodes provide MnT, PSN/Session, Profiler, Device Admin, SXP, TC-NAC, PassiveID, or pxGrid services, whether nodes are Connected / Disconnected / out of sync / registration-failed / replication-stopped / not-upgraded, and whether the deployment is healthy, degraded, or critical.

Set `deep_diagnostics=true` only when the user's wording signals a problem or explicitly asks to investigate/diagnose (e.g. "down", "broken", "not syncing", "out of sync", "registration failed", "overloaded", "investigate", "diagnose"). Deep diagnostics is heavier and slower because it reads log-derived system data (CPU, memory, disk, replication/process indicators). For general status, topology, readiness, HA, or plain "is it healthy?" questions, keep it false.

When `hostnames` is set the result describes ONLY the named nodes (`scope: "filtered"`) and cannot support deployment-wide conclusions (PAN redundancy, HA readiness, whether a Secondary PAN exists) — re-run without `hostnames` to assess HA.

**Questions this tool answers:**

- "Is my ISE deployment healthy?"
- "Which ISE nodes are down, disconnected, out of sync, or not upgraded?"
- "Do I have Primary PAN and Secondary PAN redundancy?"
- "Is PAN failover or HA readiness okay?"
- "Which node is PrimaryAdmin, SecondaryAdmin, PrimaryMonitoring, or SecondaryMonitoring?"
- "What roles and services run on each ISE node?"
- "Which nodes are PSNs / provide Session service?"
- "Is replication broken or stopped between deployment nodes?"
- "Show me the ISE cluster topology."
- "Is this a standalone or distributed ISE deployment?"
- "Which nodes are unhealthy before an upgrade or maintenance window?"


| Parameter          | Type            | Required | Default | Description                                                                                                                                                                                     |
| ------------------ | --------------- | -------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hostnames`        | array\[string]  | No       | None    | Exact ISE node hostnames to include (OR-matched). Omit for cluster-wide health, topology, redundancy, or readiness questions. A filtered result describes ONLY the named nodes and cannot support deployment-wide HA/redundancy conclusions. |
| `deep_diagnostics` | boolean         | No       | false   | When true, also gather log-derived per-node system statistics (CPU, memory, disk, replication/process indicators). Set true only when wording signals a problem or asks to investigate/diagnose. |


**Returns:** JSON object with:

- `nodes`: Array of deployed nodes, each containing:
  - `hostname`: Short hostname of the node
  - `fqdn`: Fully qualified domain name (may be null)
  - `ip_address`: Management IP address (may be null)
  - `roles`: Node personas/roles (e.g. `PrimaryAdmin`, `SecondaryMonitoring`)
  - `services`: Enabled services (e.g. `Session`, `Profiler`, `pxGrid`)
  - `node_status`: Deployment status (e.g. `Connected`, `Disconnected`, `NotInSync`)
- `summary`: Derived health summary:
  - `total_nodes`: Number of nodes in scope
  - `status_counts`: Count of nodes by `node_status` value
  - `unhealthy_nodes`: Hostnames whose `node_status` is not `Connected`
  - `scope`: `deployment` (covers every node) or `filtered` (restricted to requested hostnames)
  - `primary_admin_present`: Whether a PrimaryAdmin (Primary PAN) exists (null when scope is `filtered`)
  - `secondary_admin_present`: Whether a SecondaryAdmin (Secondary PAN) exists (null when `filtered`)
  - `ha_ready`: True iff both PrimaryAdmin and SecondaryAdmin exist and every admin/PAN node is Connected (null when `filtered`)
  - `not_found_hostnames`: Requested hostnames matching no node (present only for `filtered` scope when applicable)
  - `scope_note`: Present only for `filtered` scope; explains deployment-wide conclusions cannot be drawn
  - `verdict`: `healthy`, `degraded`, or `critical`
- `diagnostics`: Present only when `deep_diagnostics=true`, otherwise omitted:
  - `observations`: Human-readable derived observations about node health (including replication/process signals)
  - `system_stats`: Log-derived per-node system statistics: top-level `anchor`, `duration_minutes`, and `nodes` (keyed by hostname). Each node is either `{status: "ok", window: {start, end}, sample_count, cpu_percent, memory_percent, disk_percent}` (each metric a `{min, max, avg, latest}` object) or `{status: "unavailable", reason}`.

**Example response:**

```json
{
  "TODO": "Example response to be added."
}
```

**Use when:**

- You need the ISE cluster/deployment topology and node inventory
- Checking PAN redundancy or HA readiness before an upgrade or maintenance window
- Identifying which nodes are unhealthy (not Connected) across the deployment
- Determining which node holds a given persona (PrimaryAdmin, MnT, PSN, etc.)
- Investigating replication or node-status problems (with `deep_diagnostics=true`)

**Do not use when:**

- You need live RADIUS/TACACS events, sessions, Live Logs, or per-endpoint troubleshooting (use the session/authentication tools)
- You need policy configuration lookup or changes (use the policy tools)
- You need certificate expiry, TLS-error diagnosis, licensing, alarms, or backup status (use `ise_diagnose_certificate_issues` for certificates)
- You need root-cause analysis of an individual authentication, profiler, or pxGrid failure

**Best practices:**

- Omit `hostnames` for any deployment-wide HA/redundancy/topology question; only filter when the user asks about specific nodes
- Keep `deep_diagnostics=false` for status/readiness checks; enable it only when a problem is signaled
- A `filtered` result omits `primary_admin_present` / `secondary_admin_present` / `ha_ready` — re-run without `hostnames` to assess HA

---

## Certificates

Read-only tool for diagnosing Cisco ISE certificate health — trusted-certificate expiry combined with PSN `ise-psc.log` scanning for certificate/TLS error signals.

### ise_diagnose_certificate_issues

Diagnose ISE certificate issues from two angles and return a combined verdict. First, list trusted CA certificates that are expired or expiring within `expiry_days` (most-urgent-first). Second, when `scan_logs=true`, scan `ise-psc.log` on PSN nodes for certificate/TLS error signals (EAP-TLS/RADIUS handshake failures, "Unknown CA", PKIX/path-building errors, OCSP/CRL problems, certificate-management failures) over the recent 2-hour window, surfacing up to 5 raw matched lines per node.

Set `scan_logs=false` for a quick "are any certs expiring?" check. Keep it true to investigate suspected live certificate/TLS failures.

**Questions this tool answers:**

- "Are any ISE certificates expired or expiring soon?"
- "Which trusted certificates expire in the next 30 days?"
- "Are there certificate or TLS handshake errors on my PSNs?"
- "Why are endpoints getting 'Unknown CA' / untrusted certificate authority errors?"
- "Are there PKIX path-building or OCSP/CRL validation failures in the logs?"
- "Is a certificate problem causing EAP-TLS/RADIUS authentication failures?"
- "Give me an overall certificate-health verdict for my deployment."


| Parameter       | Type            | Required | Default   | Description                                                                                                                                              |
| --------------- | --------------- | -------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `expiry_days`   | integer         | No       | 30        | Look-ahead window in days for the expiry check (range 1-365)                                                                                              |
| `status_filter` | string          | No       | "enabled" | ISE certificate status to filter the expiry check on: `all`, `enabled`, or `disabled`. Defaults to enabled-only unless the user asks for all or disabled |
| `scan_logs`     | boolean         | No       | true      | When true, also scan `ise-psc.log` on PSN nodes for certificate/TLS error signals in the recent 2-hour window. Set false for a fast expiry-only check    |
| `hostnames`     | array\[string]  | No       | None      | ISE node hostnames to restrict the log scan to (PSN nodes only; non-PSN hosts silently skipped). When omitted, all PSN nodes are scanned (capped at 5). Does not affect the expiry check |
| `limit`         | integer         | No       | 25        | Max certificates to return in the expiry result (range 1-100)                                                                                            |


**Returns:** JSON object with:

- `expiry`: Trusted-certificate expiry check result:
  - `certificates`: Array sorted by expiration date ascending (most urgent first), each containing:
    - `friendly_name`: Human-readable certificate label configured in ISE
    - `expiration_date`: Expiration timestamp (ISO 8601)
    - `valid_from`: Validity start timestamp (ISO 8601, may be null)
    - `days_until_expiry`: Days until expiration; negative means already expired
    - `expiry_status`: `expired` or `warning` (expires within the `expiry_days` window)
    - `ise_status`: Whether the certificate is enabled or disabled in ISE
    - `trusted_for`: ISE services this certificate is trusted for (e.g. Cisco Services)
    - `is_referred_in_policy`: True when actively referenced in an ISE policy (expiry is operationally critical)
  - `summary`: Aggregate counts and metadata:
    - `total_matched`: Total certificates matching the filter across all scanned pages (may exceed the returned count when `limit` applies)
    - `expired_count`: Number of expired certificates in the returned set
    - `warning_count`: Number of certificates expiring within the window in the returned set
    - `earliest_expiration`: ISO 8601 expiration of the most urgently expiring certificate (may be null)
    - `checked_at`: ISO 8601 timestamp of the check (UTC)
    - `expiry_window_days`: Look-ahead window used, in days
- `log_scan`: PSN `ise-psc.log` signal scan; null when `scan_logs=false`:
  - `nodes`: Per-node scan results, each containing:
    - `hostname`: PSN node hostname (or fqdn) scanned
    - `status`: `ok` (log fetched and scanned) or `unavailable` (could not fetch/parse)
    - `matches`: Up to 5 raw matched lines (newest first), each `{ line }`
    - `total_matches`: Total matching lines seen in the window (may exceed the returned matches)
    - `reason`: Generic reason when `status` is `unavailable`; null when `ok`
  - `psn_nodes_total`: PSN nodes discovered as scan candidates
  - `psn_nodes_scanned`: PSN nodes actually attempted (capped)
  - `psn_nodes_succeeded`: PSN nodes whose log was fetched and scanned
  - `coverage_note`: Human-readable "scanned X of Y PSN node(s)" summary
- `verdict`: `critical` (any expired cert OR any log signal), `warning` (expiring certs only, no signals), or `healthy`
- `checked_at`: ISO 8601 timestamp of the diagnosis (UTC)

**Example response:**

```json
{
  "TODO": "Example response to be added."
}
```

**Use when:**

- You need to know whether any trusted certificates are expired or expiring soon
- Investigating certificate/TLS errors on PSNs (Unknown CA, PKIX, OCSP/CRL, handshake failures)
- Correlating EAP-TLS/RADIUS authentication failures with certificate problems
- Getting a single overall certificate-health verdict for the deployment

**Do not use when:**

- You need node/deployment health (use `ise_deployment_health`)
- You need sessions or per-endpoint authentication troubleshooting (use the session/authentication tools)
- You need policy configuration (use the policy tools)
- You need system-identity certificate provisioning or CSR/import operations (out of scope; this tool is read-only diagnosis)

**Best practices:**

- Use `scan_logs=false` for a fast expiry-only check when the user only asks about expiring/expired certs
- The expiry check always covers the whole trusted-certificate store; `hostnames` only narrows the log scan (PSN nodes only)
- Pay attention to `is_referred_in_policy=true` certificates — their expiry is operationally critical
- Check `coverage_note` / `psn_nodes_*` counts to confirm how much of the deployment the log scan actually covered

---

## Tool Selection Guide


| Question                                                | Recommended Tool                            |
| ------------------------------------------------------- | ------------------------------------------- |
| "Why did authentication fail for MAC/user X?"           | `ise_investigate_aaa_failure`               |
| "What is the failure reason for endpoint Y?"            | `ise_investigate_aaa_failure`               |
| "How do I fix the auth failure for user X?"             | `ise_investigate_aaa_failure`               |
| "Why were sessions authorized this way?"                | `sessions_search_with_policy_details`       |
| "Why is authentication slow for user X?"                | `sessions_search_with_latency_details`      |
| "Which authentication step took the longest?"           | `sessions_search_with_latency_details`      |
| "Show sessions with latency above 500ms"                | `sessions_search_with_latency_details`      |
| "What is the step-by-step latency breakdown?"           | `sessions_search_with_latency_details`      |
| "What policy sets exist? In what rank order?"           | `ise_search_policy_sets`                    |
| "Which policy set is the default?"                      | `ise_search_policy_sets`                    |
| "Are there disabled / monitor-mode policy sets?"        | `ise_search_policy_sets`                    |
| "List all policy sets with 0 hit counts in rank order"  | `ise_search_policy_sets` (max_hit_counts=0) |
| "Which policy sets are rarely used (<= N hits)?"        | `ise_search_policy_sets` (max_hit_counts=N) |
| "Which policy sets have been hit at least N times?"     | `ise_search_policy_sets` (min_hit_counts=N) |
| "Which authz rules use profile DenyAccess?"             | `ise_search_authorization_rules`            |
| "Find unused authz rules (hits=0)"                      | `ise_search_authorization_rules`            |
| "Are there global exceptions overriding my authz rule?" | `ise_search_authorization_rules`            |
| "Which authn rules use Active Directory?"               | `ise_search_authentication_rules`           |
| "Find lenient authn rules (if_user_not_found=CONTINUE)" | `ise_search_authentication_rules`           |
| "Is my ISE deployment healthy?"                         | `ise_deployment_health`                     |
| "Do I have Primary/Secondary PAN redundancy (HA)?"      | `ise_deployment_health`                     |
| "Which ISE nodes are down / out of sync / not upgraded?"| `ise_deployment_health`                     |
| "Which node is PrimaryAdmin / MnT / a PSN?"             | `ise_deployment_health`                     |
| "Investigate why a node is disconnected / not syncing"  | `ise_deployment_health` (deep_diagnostics=true) |
| "Are any ISE certificates expired or expiring soon?"    | `ise_diagnose_certificate_issues`           |
| "Are there certificate/TLS (Unknown CA, PKIX) errors?"  | `ise_diagnose_certificate_issues`           |
| "Quick check: any certs expiring in the next N days?"   | `ise_diagnose_certificate_issues` (scan_logs=false) |


---

## Data Sources


| Tool Category                 | Data Source                                                                                                                                                                                                                         |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Active Sessions               | ISE MNT API (AuthList, Last Session by Attributes)                                                                                                                                                                                  |
| Sessions with Policy Context  | ISE MNT API + ISE Policy API (Network Access Policy Sets, Authentication Rules, Authorization Rules)                                                                                                                                |
| Sessions with Latency Details | ISE MNT API (AuthList, Last Session by Attributes) + ISE Message Catalog (execution step code-to-text resolution)                                                                                                                   |
| AAA Failure Investigation     | ISE MNT API (AuthStatus, Last Session by Attributes, FailureReasons) + ISE Message Catalog                                                                                                                                          |
| Policy Configuration          | ISE Policy API (Network Access): policy sets, authentication rules, authorization rules, global exception rules |
| Deployment Health             | ISE Deployment API (`GET /api/v1/deployment/node`) + log-derived per-node system statistics (deep diagnostics)                                                                                                                       |
| Certificates                  | ISE Certificate/Trusted-Certificate API (expiry) + PSN `ise-psc.log` scan (certificate/TLS error signals)                                                                                                                           |


