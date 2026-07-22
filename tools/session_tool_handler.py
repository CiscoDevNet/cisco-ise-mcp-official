# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncIterator, List, Optional, Tuple
from urllib.parse import quote
import httpx

from logger import logger
from clients.mnt_client import MNTClient
from utils.xml_parser import parse_active_session_xml, parse_session_detail_xml
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
    ActiveSessionList,
    ActiveSessionSearchResult,
    EnrichedSessionSearchResult,
    SessionDetail,
)
from fastmcp.exceptions import ToolError as McpToolError
from models.error_models import ErrorCategory, raise_tool_error


class SessionToolHandler:
    """Handler for ISE MNT Session APIs."""
    
    def __init__(self, mnt_client: MNTClient):
        """
        Initialize the session tool handler.
        
        Args:
            mnt_client: The MNT HTTP client instance
        """
        self.mnt_client = mnt_client

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

    async def _fetch_auth_list_sessions(self, minutes: int = 1440) -> List[ActiveSession]:
        """Fetch authenticated sessions from the past *minutes* via Session/AuthList API.

        Callers must validate *minutes* before invoking this method.
        """
        minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
        start_time = datetime.now() - timedelta(minutes=minutes)
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        encoded_start_time = quote(start_time_str, safe=":")
        encoded_end_time = "null"
        endpoint = f"Session/AuthList/{encoded_start_time}/{encoded_end_time}"
        logger.debug("MNT endpoint", endpoint=endpoint)
        logger.info("Fetching authenticated sessions via AuthList API", minutes=minutes)
        response = await self.mnt_client.get(endpoint)
        parsed_data = parse_active_session_xml(response.text)
        active_session_list = ActiveSessionList(**parsed_data)
        logger.info("Fetched authenticated sessions", count=len(active_session_list.sessions), minutes=minutes)
        return active_session_list.sessions

    @staticmethod
    def _build_session_predicate(
        username: Optional[str] = None,
        calling_station_id: Optional[str] = None,
        nas_ip_address: Optional[str] = None,
        framed_ip_address: Optional[str] = None,
        server: Optional[str] = None,
    ):
        """Build a per-session predicate mirroring _filter_sessions.

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

    @staticmethod
    def _filter_sessions(
        sessions: List[ActiveSession],
        username: Optional[str] = None,
        calling_station_id: Optional[str] = None,
        nas_ip_address: Optional[str] = None,
        framed_ip_address: Optional[str] = None,
        server: Optional[str] = None,
        minutes: int = 1440,
    ) -> Tuple[List[ActiveSession], dict]:
        """Apply client-side filters on a list of active sessions.

        All filter values must be pre-validated and normalized by the caller.
        Returns (filtered_sessions, filters_applied). No I/O.
        """
        filters_applied: dict = {"minutes": minutes}
        filtered = sessions
        if username:
            filtered = [s for s in filtered if s.user_name and username == s.user_name]
            filters_applied["username"] = username
        if calling_station_id:
            filtered = [
                s for s in filtered
                if s.calling_station_id
                and normalize_mac_address(s.calling_station_id) == calling_station_id
            ]
            filters_applied["calling_station_id"] = calling_station_id
        if nas_ip_address:
            filtered = [s for s in filtered if s.nas_ip_address and s.nas_ip_address == nas_ip_address]
            filters_applied["nas_ip_address"] = nas_ip_address
        if framed_ip_address:
            filtered = [
                s for s in filtered
                if s.framed_ip_address and s.framed_ip_address == framed_ip_address
            ]
            filters_applied["framed_ip_address"] = framed_ip_address
        if server:
            filtered = [s for s in filtered if s.server and server == s.server]
            filters_applied["server"] = server
        return (filtered, filters_applied)

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
            all_sessions = await self._fetch_auth_list_sessions(minutes=minutes)

            filtered_sessions, search_filters = self._filter_sessions(
                all_sessions,
                username=username,
                calling_station_id=calling_station_id,
                nas_ip_address=nas_ip_address,
                framed_ip_address=framed_ip_address,
                server=server,
                minutes=minutes,
            )
            total_matching_sessions: int = len(filtered_sessions)
            filtered_sessions_with_limit: List[ActiveSession] = (
                filtered_sessions[:limit] if limit < total_matching_sessions else filtered_sessions
            )
            sample_size: int = len(filtered_sessions_with_limit)
            sampling_note: Optional[str] = build_sampling_note(
                sample_size=sample_size,
                total_found=total_matching_sessions,
                resource="session",
            )

            logger.info(
                "Session search complete",
                total_matching=total_matching_sessions,
                sample_size=sample_size,
            )
            return ActiveSessionSearchResult(
                search_filters=search_filters,
                total_matching_sessions=total_matching_sessions,
                sample_size=sample_size,
                sample_sessions=filtered_sessions_with_limit,
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
            all_sessions = await self._fetch_auth_list_sessions(minutes=minutes)

            filtered_sessions, filters_applied = self._filter_sessions(
                all_sessions,
                username=username,
                calling_station_id=calling_station_id,
                minutes=minutes,
            )
            total_sessions_found: int = len(filtered_sessions)
            sessions_to_enrich: List[ActiveSession] = filtered_sessions[:cap]
            enrichment_results: List[Optional[SessionDetail]] = await asyncio.gather(*[self._enrich_session(s) for s in sessions_to_enrich])
            enriched_sessions: List[SessionDetail] = [s for s in enrichment_results if s is not None]

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
