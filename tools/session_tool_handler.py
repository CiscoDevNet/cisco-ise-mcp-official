# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncIterator, List, Optional, Tuple
from urllib.parse import quote
import httpx

from logger import logger
from clients.mnt_client import MNTClient
from clients.auth_list_gate import auth_list_gate
from utils.xml_parser import parse_session_detail_xml, iter_filter_active_sessions
from utils.sampling import build_sampling_note
from utils.input_validators import (
    normalize_mac_address,
    validate_minutes,
    validate_ip_address,
    validate_latency_range,
    validate_limit,
    validate_mac_address,
)
from models.session_models import (
    ActiveSession,
    ActiveSessionSearchResult,
    EnrichedSessionSearchResult,
    SessionDetail,
)
from fastmcp.exceptions import ToolError as McpToolError
from models.error_models import ErrorCategory, raise_tool_error


class SessionToolHandler:
    """Handler for ISE MNT Session APIs."""

    def __init__(self, mnt_client: MNTClient, gate=None):
        """
        Initialize the session tool handler.

        Args:
            mnt_client: The MNT HTTP client instance
            gate: Optional AuthListGate for concurrency control (defaults to singleton)
        """
        self.mnt_client = mnt_client
        self.gate = gate if gate is not None else auth_list_gate

    MAX_MINUTES = 24 * 60

    @asynccontextmanager
    async def _handle_mnt_errors(self, operation: str) -> AsyncIterator[None]:
        """Wrap MNT API calls with consistent error handling."""
        try:
            yield
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.exception("ISE MNT API unreachable", error=str(e))
            raise_tool_error(
                ErrorCategory.EXTERNAL_ERROR, "ISE_UNREACHABLE",
                "The ISE MNT API is unreachable or timed out. Try again later.", retry=True,
            )
        except httpx.HTTPStatusError as e:
            logger.exception("ISE MNT API HTTP error", status_code=e.response.status_code)
            raise_tool_error(
                ErrorCategory.EXTERNAL_ERROR, "ISE_API_ERROR",
                f"ISE MNT API returned HTTP {e.response.status_code}.",
                retry=e.response.status_code >= 500,
            )
        except McpToolError:
            raise
        except Exception as e:
            logger.exception("Unexpected error in operation", operation=operation, error=str(e))
            raise_tool_error(
                ErrorCategory.SERVER_ERROR, "INTERNAL_ERROR",
                f"An unexpected error occurred while {operation}.",
            )

    async def _fetch_auth_list_sessions(
        self,
        filters: dict,
        retention_cap: int,
        minutes: int = 1440,
    ) -> Tuple[List[ActiveSession], int]:
        """Stream authenticated sessions from the past *minutes*, filtering
        during the parse and retaining only up to *retention_cap* matches.

        Returns (sessions, total_matched). Runs inside the AuthList gate so
        concurrency and MnT load are bounded. Callers must validate *minutes*
        and normalize all *filters* values beforehand.
        """
        minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
        start_time = datetime.now() - timedelta(minutes=minutes)
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        encoded_start_time = quote(start_time_str, safe=":")
        endpoint = f"Session/AuthList/{encoded_start_time}/null"
        predicate = self._build_session_predicate(**filters)

        logger.info("Streaming authenticated sessions via AuthList API", minutes=minutes)
        async with self.gate.guard():
            async with self.mnt_client.get_stream(endpoint) as response:
                with tempfile.SpooledTemporaryFile(max_size=64 * 1024 * 1024) as buf:
                    async for chunk in response.aiter_bytes():
                        buf.write(chunk)
                    buf.seek(0)
                    # The iterparse walk is synchronous and CPU-bound (and may
                    # read from a spilled-to-disk temp file). Run it off the
                    # event loop so a large parse cannot stall unrelated calls
                    # -- essential once ISE_AUTHLIST_MAX_CONCURRENCY > 1, where
                    # multiple parses would otherwise serialize on the loop.
                    retained, total_matched = await asyncio.to_thread(
                        iter_filter_active_sessions, buf, predicate, retention_cap
                    )
        sessions = [ActiveSession(**d) for d in retained]
        logger.info("Streamed authenticated sessions", total_matched=total_matched, retained=len(sessions))
        return sessions, total_matched

    @staticmethod
    def _build_session_predicate(
        username: Optional[str] = None,
        calling_station_id: Optional[str] = None,
        nas_ip_address: Optional[str] = None,
        framed_ip_address: Optional[str] = None,
        server: Optional[str] = None,
    ):
        """Build a per-session predicate for streaming filter.

        Filter values must be pre-validated and normalized by the caller
        (calling_station_id already normalized via validate_mac_address).
        The session's own MAC is normalized here before comparison.
        """
        def predicate(s: dict) -> bool:
            if username and s.get("user_name") != username:
                return False
            if calling_station_id:
                raw = s.get("calling_station_id")
                if not raw or normalize_mac_address(raw) != calling_station_id:
                    return False
            if nas_ip_address and s.get("nas_ip_address") != nas_ip_address:
                return False
            if framed_ip_address and s.get("framed_ip_address") != framed_ip_address:
                return False
            if server and s.get("server") != server:
                return False
            return True

        return predicate


    async def search_active_sessions(
        self,
        username: Optional[str] = None,
        calling_station_id: Optional[str] = None,
        nas_ip_address: Optional[str] = None,
        framed_ip_address: Optional[str] = None,
        server: Optional[str] = None,
        minutes: int = 1440,
        limit: int = 10
    ) -> ActiveSessionSearchResult:
        """
        Search authenticated sessions from the past X minutes with optional filters.
        
        Uses the ISE MNT AuthList API to query sessions authenticated within a time window.
        Since the MNT API doesn't support server-side filtering, this method:
        1. Validates and normalizes all inputs
        2. Fetches authenticated sessions from the past X minutes using AuthList API
        3. Applies client-side filtering based on provided parameters
        4. Returns filtered results with metadata
        """
        minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
        limit = validate_limit(limit, max_limit=20)
        if calling_station_id:
            calling_station_id = validate_mac_address(calling_station_id)
        if nas_ip_address:
            nas_ip_address = validate_ip_address(nas_ip_address)
        if framed_ip_address:
            framed_ip_address = validate_ip_address(framed_ip_address)

        async with self._handle_mnt_errors("searching active sessions"):
            filters = {
                "username": username,
                "calling_station_id": calling_station_id,
                "nas_ip_address": nas_ip_address,
                "framed_ip_address": framed_ip_address,
                "server": server,
            }
            sample_sessions, total_matching_sessions = await self._fetch_auth_list_sessions(
                filters=filters, retention_cap=limit, minutes=minutes,
            )
            search_filters = {"minutes": minutes}
            for key, value in filters.items():
                if value:
                    search_filters[key] = value
            sample_size = len(sample_sessions)
            sampling_note = build_sampling_note(
                sample_size=sample_size,
                total_found=total_matching_sessions,
                resource="session",
            )
            logger.info("Session search complete", total_matching=total_matching_sessions, sample_size=sample_size)
            return ActiveSessionSearchResult(
                search_filters=search_filters,
                total_matching_sessions=total_matching_sessions,
                sample_size=sample_size,
                sample_sessions=sample_sessions,
                sampling_note=sampling_note,
            )

    @staticmethod
    def _get_enrichment_endpoints(session: ActiveSession) -> List[Tuple[str, str]]:
        """
        Return MNT API (Get Session Details) lookup keys in priority order.
        First calling_station_id (MACAddress), then user_name (UserName).
        """
        keys: List[Tuple[str, str]] = []
        if session.calling_station_id:
            mac = normalize_mac_address(session.calling_station_id)
            keys.append((f"Session/MACAddress/{quote(mac, safe=':')}", "calling_station_id"))
        if session.user_name:
            keys.append((f"Session/UserName/{quote(session.user_name, safe='')}", "user_name"))
        return keys

    async def _enrich_session(self, session: ActiveSession) -> Optional[SessionDetail]:
        """
        Call Get Session Details API for one session; try calling_station_id first, fall back to user_name on error.
        Returns None if all enrichment attempts fail or no keys are available.
        """
        api_endpoints = self._get_enrichment_endpoints(session)
        if not api_endpoints:
            logger.warning("No enrichment keys found for session")
            return None
        for endpoint_path, desc in api_endpoints:
            try:
                response = await self.mnt_client.get(endpoint_path)
                parsed_data = parse_session_detail_xml(response.text)
                return SessionDetail(**parsed_data)
            except Exception as e:
                logger.warning("Enrichment failed for session", error=str(e))
                continue
        return None

    ENRICHMENT_CAP = 100

    @staticmethod
    def _filter_sessions_by_latency(
        sessions: List[SessionDetail],
        min_latency_ms: Optional[int],
        max_latency_ms: Optional[int],
    ) -> List[SessionDetail]:
        """Filter enriched sessions by response_time_ms range.

        Sessions with ``response_time_ms is None`` are excluded when any
        latency filter is active.
        """
        filtered: List[SessionDetail] = []
        for s in sessions:
            response_time_ms = s.response_time_ms
            if response_time_ms is None:
                continue
            if min_latency_ms is not None and response_time_ms < min_latency_ms:
                continue
            if max_latency_ms is not None and response_time_ms > max_latency_ms:
                continue
            filtered.append(s)
        return filtered

    async def search_enriched_active_sessions(
        self,
        username: Optional[str] = None,
        calling_station_id: Optional[str] = None,
        minutes: int = 1440,
        limit: int = 1,
        min_latency_ms: Optional[int] = None,
        max_latency_ms: Optional[int] = None,
    ) -> EnrichedSessionSearchResult:
        """
        Search active sessions (AuthList API) and enrich each with detailed data from Get Session Details API.
        limit default 1, max 10. Enrichment uses calling_station_id first.

        Pipeline:
            1. Validate and normalize all inputs
            2. Fetch sessions from ISE
            3. Filter by username / calling_station_id (cheap, pre-enrichment)
            4. Enrich up to ENRICHMENT_CAP sessions when latency filters are
               active, otherwise up to ``limit``
            5. Apply latency range filter on enriched SessionDetail objects
            6. Truncate to ``limit``
        """
        minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
        limit = validate_limit(limit, max_limit=10)
        if calling_station_id:
            calling_station_id = validate_mac_address(calling_station_id)
        validate_latency_range(min_latency_ms, max_latency_ms)

        async with self._handle_mnt_errors("searching enriched sessions"):
            has_latency_filter = min_latency_ms is not None or max_latency_ms is not None
            cap = self.ENRICHMENT_CAP if has_latency_filter else limit
            filters = {"username": username, "calling_station_id": calling_station_id}
            filtered_sessions, total_sessions_found = await self._fetch_auth_list_sessions(
                filters=filters, retention_cap=cap, minutes=minutes,
            )
            filters_applied = {"minutes": minutes}
            if username:
                filters_applied["username"] = username
            if calling_station_id:
                filters_applied["calling_station_id"] = calling_station_id

            sessions_to_enrich = filtered_sessions[:cap]
            enrichment_results = await asyncio.gather(*[self._enrich_session(s) for s in sessions_to_enrich])
            enriched_sessions = [s for s in enrichment_results if s is not None]

            if has_latency_filter:
                enriched_sessions = self._filter_sessions_by_latency(
                    enriched_sessions, min_latency_ms, max_latency_ms,
                )
                if min_latency_ms is not None:
                    filters_applied["min_latency_ms"] = min_latency_ms
                if max_latency_ms is not None:
                    filters_applied["max_latency_ms"] = max_latency_ms
                total_sessions_found = len(enriched_sessions)

            enriched_sessions = enriched_sessions[:limit]
            return EnrichedSessionSearchResult(
                search_filters=filters_applied,
                total_sessions_found=total_sessions_found,
                actual_sessions_returned=len(enriched_sessions),
                sessions=enriched_sessions,
            )
