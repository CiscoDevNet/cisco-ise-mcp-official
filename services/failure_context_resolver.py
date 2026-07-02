# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

from typing import Dict, List, Optional

from fastmcp.exceptions import ToolError as McpToolError

from logger import logger
from models.error_models import ErrorCategory, raise_tool_error
from models.session_models import ExecutionStep
from models.failure_models import AaaFailureDetail


class FailureContextResolver:
    """Enriches raw AAA failure dicts with cause/resolution from the FailureReasons
    catalog and resolves execution step codes to human-readable messages via the
    message catalog.

    All lookups are pure in-memory — no additional API calls.
    """

    def __init__(
        self,
        msg_catalog: Dict[str, str],
        failure_reasons_catalog: Dict[str, Dict[str, Optional[str]]],
    ):
        self._msg_catalog = msg_catalog
        self._failure_reasons_catalog = failure_reasons_catalog

    def _parse_failure_reason(self, raw: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """Split a failure_reason string like '22040 Wrong password' into (code, text)."""
        if not raw or not raw.strip():
            return None, None
        parts = raw.strip().split(None, 1)
        code = parts[0]
        text = parts[1] if len(parts) > 1 else None
        return code, text

    def _resolve_execution_steps(self, raw_steps: Optional[List[str]]) -> Optional[List[ExecutionStep]]:
        """Resolve a list of step code strings into ExecutionStep objects."""
        if not raw_steps:
            return None
        steps: List[ExecutionStep] = []
        for code in raw_steps:
            steps.append(ExecutionStep(
                code=code,
                text=self._msg_catalog.get(code),
            ))
        return steps if steps else None

    def enrich_failures(self, raw_failures: List[Dict]) -> List[AaaFailureDetail]:
        """Enrich a list of raw failure dicts with catalog data and resolved steps.

        Args:
            raw_failures: List of dicts from parse_auth_status_xml or
                converted from parse_session_detail_xml.

        Returns:
            List of AaaFailureDetail models with enriched failure context.
        """
        try:
            results: List[AaaFailureDetail] = []

            for raw in raw_failures:
                failure_reason_raw = raw.get("failure_reason")
                code, text = self._parse_failure_reason(failure_reason_raw)

                cause: Optional[str] = None
                resolution: Optional[str] = None
                context_note: Optional[str] = None

                if code and code in self._failure_reasons_catalog:
                    entry = self._failure_reasons_catalog[code]
                    cause = entry.get("cause")
                    resolution = entry.get("resolution")
                elif code:
                    context_note = f"Failure reason code {code} not found in the ISE FailureReasons catalog"
                    logger.debug("Unknown failure reason code", code=code)

                resolved_steps = self._resolve_execution_steps(raw.get("execution_steps"))
                if resolved_steps:
                    unresolved = sum(1 for s in resolved_steps if s.text is None)
                    if unresolved:
                        step_note = f"{unresolved} of {len(resolved_steps)} execution step code(s) could not be resolved"
                        context_note = f"{context_note}; {step_note}" if context_note else step_note

                timestamp = raw.get("acs_timestamp") or raw.get("auth_acs_timestamp")

                results.append(AaaFailureDetail(
                    user_name=raw.get("user_name"),
                    calling_station_id=raw.get("calling_station_id"),
                    nas_ip_address=raw.get("nas_ip_address"),
                    framed_ip_address=raw.get("framed_ip_address"),
                    network_device_name=raw.get("network_device_name"),
                    acs_server=raw.get("acs_server"),
                    authentication_method=raw.get("authentication_method"),
                    authentication_protocol=raw.get("authentication_protocol"),
                    identity_store=raw.get("identity_store"),
                    timestamp=timestamp,
                    failure_reason_code=code,
                    failure_reason_text=text,
                    failure_cause=cause,
                    failure_resolution=resolution,
                    response=raw.get("response"),
                    execution_steps=resolved_steps,
                    failure_context_note=context_note,
                ))

            return results

        except McpToolError:
            raise
        except Exception as e:
            logger.exception("Error enriching failures with context", error=str(e))
            raise_tool_error(
                ErrorCategory.SERVER_ERROR, "FAILURE_ENRICHMENT_ERROR",
                "An unexpected error occurred while enriching failure data.",
            )
