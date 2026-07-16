# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Literal, List, Dict, Any
from pydantic import Field

from models.base import IseResultModel
from models.policy_models import PolicyContext

_SEARCH_FILTERS_DESC = "Search filters that were used to find sessions"


class ActiveSession(IseResultModel):
    """
    Represents a single active session from the ISE MNT API.
    
    This model validates and structures the data from each <activeSession> element.
    """
    
    user_name: Optional[str] = Field(None, description="Username of the authenticated user")
    calling_station_id: Optional[str] = Field(None, description="MAC address of the endpoint")
    nas_ip_address: Optional[str] = Field(None, description="IP address of the Network Access Server (switch/AP)")
    server: Optional[str] = Field(None, description="ISE node handling the session")
    framed_ip_address: Optional[str] = Field(None, description="IP address assigned to the endpoint")
    framed_ipv6_address: Optional[str] = Field(None, description="IPv6 address assigned to the endpoint")
    audit_session_id: Optional[str] = Field(None, description="Audit session ID for the session")
    acct_session_id: Optional[str] = Field(None, description="Accounting session ID for the session")
    nas_ipv6_address: Optional[str] = Field(None, description="IPv6 address of the Network Access Server")
    


class ActiveSessionList(IseResultModel):
    """
    Represents the complete response from the Session/ActiveList API.
    
    Contains the count of active sessions and the list of sessions.
    """
    
    total_active_sessions: int = Field(..., description="Total number of active sessions", ge=0, alias="noOfActiveSession")
    sessions: List[ActiveSession] = Field(default_factory=list, description="List of active sessions")


class ActiveSessionSearchResult(IseResultModel):
    """
    Represents the filtered search results from active sessions.

    The session list is a bounded SAMPLE of matching sessions, capped by the
    request limit to fit the model context window. Use total_matching_sessions
    for the true count; sampling_note is present only when the list is truncated.
    """

    search_filters: Dict[str, Any] = Field(
        default_factory=dict,
        description=_SEARCH_FILTERS_DESC,
    )
    total_matching_sessions: int = Field(
        ...,
        description=(
            "Total sessions matching the filters in ISE. This is the full count; "
            "the list below may contain fewer."
        ),
        ge=0,
    )
    sample_size: int = Field(
        ...,
        description=(
            "Number of sessions in sample_sessions below. May be smaller than "
            "total_matching_sessions due to the result limit."
        ),
        ge=0,
    )
    sample_sessions: List[ActiveSession] = Field(
        default_factory=list,
        description=(
            "A representative SAMPLE of matching sessions, capped by 'limit' to fit "
            "the model context window. These are real sessions but NOT the complete "
            "set -- do not assume only this many sessions exist; cite "
            "total_matching_sessions for the true count."
        ),
    )
    sampling_note: Optional[str] = Field(
        None,
        description=(
            "Present ONLY when the list is a truncated sample; states how many of "
            "the total matching sessions are shown. Absent when all results are "
            "returned or none matched."
        ),
    )


class StepLatency(IseResultModel):
    """A single step latency entry from the ISE StepLatency string.

    The step_index maps directly to the execution_steps array index
    (e.g. step_index=1 corresponds to execution_steps[1]).
    """

    step_index: int = Field(..., description="Index into the execution_steps array")
    latency_ms: int = Field(..., description="Latency in milliseconds for this step")


class SessionDetail(IseResultModel):
    """
    Curated session details from the ISE MNT Last Session by Attributes API (sessionParameters XML).
    Contains 16 direct XML elements plus 6 key-value pairs extracted from other_attr_string.
    """
    authentication_result: Optional[Literal["Passed", "Failed"]] = Field(None, description="Authentication result: Passed or Failed")
    user_name: Optional[str] = Field(None, description="Username of the authenticated user")
    nas_ip_address: Optional[str] = Field(None, description="IP address of the Network Access Server")
    calling_station_id: Optional[str] = Field(None, description="Endpoint MAC address")
    identity_group: Optional[str] = Field(None, description="Identity group")
    network_device_name: Optional[str] = Field(None, description="Network device name as defined in ISE")
    ise_psn_node: Optional[str] = Field(None, description="ISE PSN node name that handled the session", alias="acs_server")
    authentication_method: Optional[str] = Field(None, description="Authentication method used")
    authentication_protocol: Optional[str] = Field(None, description="Authentication protocol used")
    framed_ip_address: Optional[str] = Field(None, description="IP address assigned to the endpoint")
    auth_acs_timestamp: Optional[str] = Field(None, description="Authentication timestamp (ISO 8601)")
    posture_status: Optional[str] = Field(None, description="Posture status; may be empty")
    authorization_profiles: Optional[str] = Field(None, description="Authorization profile applied", alias="selected_azn_profiles")
    identity_store: Optional[str] = Field(None, description="Identity store used for authentication")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds", alias="response_time")
    authentication_status: Optional[str] = Field(None, description="From other_attr_string: AuthenticationStatus", exclude=True)
    identity_policy_matched_rule: Optional[str] = Field(None, description="From other_attr_string: IdentityPolicyMatchedRule")
    protocol: Optional[str] = Field(None, description="From other_attr_string: Protocol")
    ise_policy_set_name: Optional[str] = Field(None, description="From other_attr_string: ISEPolicySetName")
    authorization_policy_matched_rule: Optional[str] = Field(None, description="From other_attr_string: AuthorizationPolicyMatchedRule")
    execution_steps: Optional[List[str]] = Field(None, description="Parsed list of execution step codes", exclude=True)
    steps_latencies: Optional[List[StepLatency]] = Field(None, description="Per-step latency with 1-based step index", exclude=True)


class SessionDetailResult(IseResultModel):
    """
    Result of get_session_details: wraps a single SessionDetail.
    """
    session: SessionDetail = Field(..., description="Detailed session data from the ISE MNT API")


class EnrichedSessionSearchResult(IseResultModel):
    """
    Result of search_enriched_active_sessions: filters, counts, and list of enriched sessions.
    """
    search_filters: Dict[str, Any] = Field(default_factory=dict, description=_SEARCH_FILTERS_DESC)
    total_sessions_found: int = Field(..., description="Total number of sessions that matched the search filters", ge=0)
    actual_sessions_returned: int = Field(..., description="Number of enriched sessions included in the sessions list below", ge=0)
    sessions: List[SessionDetail] = Field(default_factory=list, description="List of sessions with detailed enrichment data")


class SessionWithPolicyContext(IseResultModel):
    """A single session paired with its resolved policy context."""

    session: SessionDetail = Field(..., description="Enriched session details")
    policy_context: Optional[PolicyContext] = Field(None, description="Resolved policy set, authentication rule, and authorization rule")
    policy_context_note: Optional[str] = Field(None, description="Explanation when policy context could not be resolved")


class PolicyEnrichedSessionSearchResult(IseResultModel):
    """
    Result of sessions_search_with_policy_details:
    sessions enriched with both session details and full policy context.
    """
    search_filters: Dict[str, Any] = Field(default_factory=dict, description=_SEARCH_FILTERS_DESC)
    total_sessions_found: int = Field(..., description="Total number of sessions that matched the search filters", ge=0)
    actual_sessions_returned: int = Field(..., description="Number of sessions included in the sessions list below", ge=0)
    sessions: List[SessionWithPolicyContext] = Field(default_factory=list, description="Sessions with detailed enrichment and policy context")


class ExecutionStep(IseResultModel):
    """A single resolved execution step from the ISE authentication flow."""

    code: str = Field(..., description="Numeric message code from ISE execution steps", exclude=True)
    text: Optional[str] = Field(None, description="Human-readable message text (None if code not found in catalog)")
    latency_ms: Optional[int] = Field(None, description="Latency in milliseconds for this step")


class SessionWithLatencyContext(IseResultModel):
    """A single session paired with its resolved execution steps."""

    session: SessionDetail = Field(..., description="Enriched session details")
    execution_steps: Optional[List[ExecutionStep]] = Field(None, description="Resolved execution steps with message texts")
    latency_context_note: Optional[str] = Field(None, description="Explanation when execution steps could not be resolved")


class LatencyEnrichedSessionSearchResult(IseResultModel):
    """
    Result of sessions_search_with_latency_details:
    sessions enriched with resolved execution step messages.
    """
    search_filters: Dict[str, Any] = Field(default_factory=dict, description=_SEARCH_FILTERS_DESC)
    total_sessions_found: int = Field(..., description="Total number of sessions that matched the search filters", ge=0)
    actual_sessions_returned: int = Field(..., description="Number of sessions included in the sessions list below", ge=0)
    sessions: List[SessionWithLatencyContext] = Field(default_factory=list, description="Sessions with resolved execution step details")

