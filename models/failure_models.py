# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, List, Dict, Any
from pydantic import Field

from models.base import IseResultModel
from models.session_models import ExecutionStep


class FailureReasonEntry(IseResultModel):
    """A single entry from the ISE FailureReasons catalog."""

    code: str = Field(..., description="Full failure reason code text (e.g. '22040 Wrong password')")
    cause: Optional[str] = Field(None, description="Detailed explanation of why the failure occurred")
    resolution: Optional[str] = Field(None, description="Recommended steps to resolve the failure")


class AaaFailureDetail(IseResultModel):
    """A single AAA failure with enriched context."""

    user_name: Optional[str] = Field(None, description="Username of the authenticated user")
    calling_station_id: Optional[str] = Field(None, description="Endpoint MAC address")
    nas_ip_address: Optional[str] = Field(None, description="IP of the Network Access Server (switch/AP), NOT the endpoint IP")
    framed_ip_address: Optional[str] = Field(None, description="IP address assigned to the endpoint")
    network_device_name: Optional[str] = Field(None, description="Network device name as defined in ISE")
    acs_server: Optional[str] = Field(None, description="ISE PSN node that processed the authentication")
    authentication_method: Optional[str] = Field(None, description="Authentication method used (e.g. PAP_ASCII)")
    authentication_protocol: Optional[str] = Field(None, description="Authentication protocol used (e.g. PAP_ASCII, PEAP)")
    identity_store: Optional[str] = Field(None, description="Identity store queried (e.g. Internal Users, AD)")
    timestamp: Optional[str] = Field(None, description="Authentication timestamp (ISO 8601)")
    failure_reason_code: Optional[str] = Field(None, description="Numeric ISE failure reason code (e.g. '22040')")
    failure_reason_text: Optional[str] = Field(None, description="Short failure description (e.g. 'Wrong password')")
    failure_cause: Optional[str] = Field(None, description="Why the failure occurred, from ISE FailureReasons catalog")
    failure_resolution: Optional[str] = Field(None, description="How to fix the failure, from ISE FailureReasons catalog")
    response: Optional[str] = Field(None, description="Raw RADIUS response (e.g. 'RadiusPacketType=AccessReject')")
    execution_steps: Optional[List[ExecutionStep]] = Field(None, description="Ordered authentication flow with human-readable messages")
    failure_context_note: Optional[str] = Field(None, description="Explanation when enrichment is partial or missing")


class AaaFailureInvestigationResult(IseResultModel):
    """Result of ise_investigate_aaa_failure tool."""

    search_filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters used for the investigation")
    total_failures_found: int = Field(..., ge=0, description="Total number of failures matching the search")
    actual_failures_returned: int = Field(..., ge=0, description="Number of failures included in this response")
    has_more: bool = Field(..., description="True when total_failures_found > actual_failures_returned")
    failures: List[AaaFailureDetail] = Field(default_factory=list, description="List of enriched AAA failure details")
