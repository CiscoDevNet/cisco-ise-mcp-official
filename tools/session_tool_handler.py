# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncIterator, Awaitable, List, Optional, Tuple
from urllib.parse import quote
import httpx

from logger import logger
from clients.mnt_client import MNTClient
from clients.mnt_gate import mnt_gate
from utils.xml_parser import (
    iter_filter_active_sessions,
    parse_active_session_xml,
    parse_mnt_error_body,
    parse_session_count_xml,
    parse_session_detail_as_active_session,
    parse_session_detail_xml,
)
from utils.sampling import build_sampling_note
from utils.input_validators import (
    normalize_mac_address,
    validate_audit_session_id,
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
    SessionCountResult,
    SessionDetail,
)
from fastmcp.exceptions import ToolError as McpToolError
from models.error_models import ErrorCategory, find_tls_error, raise_tool_error


class SessionToolHandler:
    """Handler for ISE MNT Session APIs."""

    def __init__(self, mnt_client: MNTClient, gate=None):
        """
        Initialize the session tool handler.

        Args:
            mnt_client: The MNT HTTP client instance
            gate: Optional MntGate for concurrency control (defaults to singleton)
        """
        self.mnt_client = mnt_client
        self.gate = gate if gate is not None else mnt_gate

    MAX_MINUTES = 24 * 60

    @asynccontextmanager
    async def _handle_mnt_errors(self, operation: str) -> AsyncIterator[None]:
        """Wrap MNT API calls with consistent error handling."""
        try:
            yield
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            tls = find_tls_error(e)
            if tls is not None:
                logger.error("ISE MNT API TLS verification failed", error=str(tls))
                raise_tool_error(
                    ErrorCategory.EXTERNAL_ERROR, "ISE_TLS_VERIFICATION_FAILED",
                    "TLS verification failed connecting to the ISE MNT API. Check the ISE "
                    "server certificate, the trusted CA bundle, and that the hostname matches "
                    "the certificate SAN.",
                    retry=False,
                )
            logger.exception("ISE MNT API unreachable", error=str(e))
            raise_tool_error(
                ErrorCategory.EXTERNAL_ERROR, "ISE_UNREACHABLE",
                "The ISE MNT API is unreachable or timed out. Try again later.", retry=True,
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.exception("ISE MNT API HTTP error", status_code=status_code)
            # ISE puts the only human-readable cause in <internal-error-info>;
            # without it every backend fault is an indistinguishable "HTTP 500".
            detail = parse_mnt_error_body(e.response.text) if e.response.text else None
            raise_tool_error(
                ErrorCategory.EXTERNAL_ERROR, "ISE_API_ERROR",
                f"ISE MNT API error: {detail}" if detail
                else f"ISE MNT API returned HTTP {status_code}.",
                retry=status_code >= 500,
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
                    # -- essential once ISE_MNT_GATE_MAX_CONCURRENCY > 1, where
                    # multiple parses would otherwise serialize on the loop.
                    retained, total_matched = await asyncio.to_thread(
                        iter_filter_active_sessions, buf, predicate, retention_cap
                    )
        sessions = [ActiveSession(**d) for d in retained]
        logger.info("Streamed authenticated sessions", total_matched=total_matched, retained=len(sessions))
        return sessions, total_matched

    # ISE reports "no session for this identifier" as HTTP 500 with the reason
    # in <internal-error-info>, not as 404 or an empty document. A direct lookup
    # that finds nothing is a normal empty result, not a fault, so this phrase
    # is how we tell the two apart. Matching on the message text is fragile but
    # it is the only signal ISE gives; an unrecognised 500 still propagates.
    _NO_SESSION_MARKER = "is not available"

    @asynccontextmanager
    async def _empty_on_no_session(self, sink: list) -> AsyncIterator[None]:
        """Swallow ISE's "session data is not available" 500, leaving *sink* empty.

        A lookup for an identifier with no session must answer "none found" --
        agents ask `active_sessions_search(username=...)` precisely to check
        whether a session exists, and a tool error there reads as "ISE is
        broken" rather than "no, there isn't one". Any other 500 propagates so
        real faults are not silently reported as an absence.
        """
        try:
            yield
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 500:
                raise
            detail = parse_mnt_error_body(e.response.text) if e.response.text else None
            if not detail or self._NO_SESSION_MARKER not in detail:
                raise
            logger.info("ISE reports no session for this identifier", detail=detail)
            sink.clear()

    async def _fetch_session_as_active(self, endpoint: str, **log_context) -> List[ActiveSession]:
        """GET a single-identifier MnT endpoint, projected to ActiveSession.

        These endpoints return one <sessionParameters> record rather than an
        <activeList>, so the result is a 0- or 1-element list. An absent session
        yields [].
        """
        logger.info("Fetching session via direct MnT lookup", endpoint=endpoint, **log_context)
        sessions: List[ActiveSession] = []
        async with self._empty_on_no_session(sessions):
            response = await self.mnt_client.get(endpoint)
            sessions.append(ActiveSession(**parse_session_detail_as_active_session(response.text)))
        return sessions

    async def _fetch_sessions_by_audit_session_id(self, audit_session_id: str) -> List[ActiveSession]:
        """Fetch active session(s) by audit session ID.

        Unlike the other direct endpoints this one returns an <activeList>, and
        it is genuinely active-scoped (note ``Session/Active/`` in the path).
        """
        endpoint = f"Session/Active/SessionID/{quote(audit_session_id, safe='')}/0"
        logger.info("Fetching session by audit session ID", audit_session_id=audit_session_id)
        sessions: List[ActiveSession] = []
        async with self._empty_on_no_session(sessions):
            response = await self.mnt_client.get(endpoint)
            sessions.extend(ActiveSessionList(**parse_active_session_xml(response.text)).sessions)
        return sessions

    async def _fetch_session_detail(self, endpoint: str) -> List[SessionDetail]:
        """GET a single-identifier MnT endpoint as a full SessionDetail.

        One call replaces the AuthList download plus a follow-up enrichment GET.
        Returns [] when ISE has no session for the identifier.
        """
        logger.info("Fetching session detail via direct MnT lookup", endpoint=endpoint)
        details: List[SessionDetail] = []
        async with self._empty_on_no_session(details):
            response = await self.mnt_client.get(endpoint)
            details.append(SessionDetail(**parse_session_detail_xml(response.text)))
        return details

    @staticmethod
    def _mac_endpoint(mac: str) -> str:
        return f"Session/MACAddress/{quote(mac, safe=':')}"

    @staticmethod
    def _username_endpoint(username: str) -> str:
        return f"Session/UserName/{quote(username, safe='')}"

    def _resolve_direct_lookup(
        self,
        *,
        username: Optional[str],
        calling_station_id: Optional[str],
        nas_ip_address: Optional[str],
        framed_ip_address: Optional[str],
        audit_session_id: Optional[str],
        server: Optional[str],
    ) -> Optional[Tuple[str, str, Awaitable[List[ActiveSession]]]]:
        """Pick a dedicated MnT endpoint when exactly one identifier pins the query.

        ISE offers a point-lookup endpoint per identifier. Using it replaces the
        whole-deployment AuthList download with one GET, and -- because it is not
        time-windowed -- it also finds the session the caller asked about when it
        authenticated outside the default lookback. That default silently losing
        older sessions was the original complaint.

        Requires EXACTLY one identifier and no non-identifier filter: these
        endpoints take a single key and cannot express "this MAC on that ISE
        node", so anything else must fall back to the AuthList scan where
        client-side filtering can compose.

        Returns ``(identifier_name, identifier_value, awaitable)``, or None to
        use the scan.
        """
        candidates = [
            # audit_session_id first: its endpoint is the only active-scoped one.
            ("audit_session_id", audit_session_id,
             lambda: self._fetch_sessions_by_audit_session_id(audit_session_id)),
            ("calling_station_id", calling_station_id,
             lambda: self._fetch_session_as_active(
                 self._mac_endpoint(calling_station_id), mac=calling_station_id)),
            ("username", username,
             lambda: self._fetch_session_as_active(
                 self._username_endpoint(username), username=username)),
            ("nas_ip_address", nas_ip_address,
             lambda: self._fetch_session_as_active(
                 f"Session/IPAddress/{quote(nas_ip_address, safe='.')}", nas_ip=nas_ip_address)),
            ("framed_ip_address", framed_ip_address,
             lambda: self._fetch_session_as_active(
                 f"Session/EndPointIPAddress/{quote(framed_ip_address, safe='.')}",
                 framed_ip=framed_ip_address)),
        ]
        supplied = [(name, value, fetch) for name, value, fetch in candidates if value]
        if len(supplied) != 1 or server:
            return None
        name, value, fetch = supplied[0]
        return name, value, fetch()

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
        audit_session_id: Optional[str] = None,
        server: Optional[str] = None,
        minutes: int = 1440,
        limit: int = 10
    ) -> ActiveSessionSearchResult:
        """
        Search sessions via the most precise ISE MNT endpoint available.

        Routing:
        - Exactly one identifier and no other filter -> that identifier's
          dedicated MnT endpoint, one GET, no time window.
        - Anything else -> the AuthList time-window scan, filtered client-side
          during the streaming parse (the MnT API has no server-side filtering).

        Both paths return the same shape: filters, total count, sample list.
        """
        minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
        limit = validate_limit(limit, max_limit=20)
        if calling_station_id:
            calling_station_id = validate_mac_address(calling_station_id)
        if nas_ip_address:
            nas_ip_address = validate_ip_address(nas_ip_address)
        if framed_ip_address:
            framed_ip_address = validate_ip_address(framed_ip_address)
        if audit_session_id:
            audit_session_id = validate_audit_session_id(audit_session_id)

        async with self._handle_mnt_errors("searching active sessions"):
            filters = {
                "username": username,
                "calling_station_id": calling_station_id,
                "nas_ip_address": nas_ip_address,
                "framed_ip_address": framed_ip_address,
                "server": server,
            }
            direct = self._resolve_direct_lookup(
                username=username,
                calling_station_id=calling_station_id,
                nas_ip_address=nas_ip_address,
                framed_ip_address=framed_ip_address,
                audit_session_id=audit_session_id,
                server=server,
            )

            if direct is not None:
                identifier, identifier_value, fetch = direct
                sessions = await fetch
                # The endpoint already answers exactly the question asked, so no
                # client-side filtering follows. `minutes` is omitted from the
                # reported filters because it genuinely did not apply -- claiming
                # a window we never enforced would misdescribe the result.
                search_filters = {"lookup": "direct", identifier: identifier_value}
                sample_sessions = sessions[:limit]
                total_matching_sessions = len(sessions)
            else:
                sample_sessions, total_matching_sessions = await self._fetch_auth_list_sessions(
                    filters=filters, retention_cap=limit, minutes=minutes,
                )
                search_filters = {"lookup": "authlist_scan", "minutes": minutes}
                for key, value in filters.items():
                    if value:
                        search_filters[key] = value

            sample_size = len(sample_sessions)
            sampling_note = build_sampling_note(
                sample_size=sample_size,
                total_found=total_matching_sessions,
                resource="session",
            )
            logger.info(
                "Session search complete",
                lookup=search_filters["lookup"],
                total_matching=total_matching_sessions,
                sample_size=sample_size,
            )
            return ActiveSessionSearchResult(
                search_filters=search_filters,
                total_matching_active_sessions=total_matching_sessions,
                sample_size=sample_size,
                active_sessions_sample=sample_sessions,
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

    # Max per-session enrichment GETs allowed to run concurrently WITHIN a
    # single search_enriched_active_sessions call. Without this, a latency
    # filter fans out up to ENRICHMENT_CAP (100) GETs at once against one MnT
    # node, and N concurrent tool calls stack N x. This is a per-call width
    # limiter (a local Semaphore), NOT cross-call admission control -- that
    # remains the AuthList gate's job for the heavy download only.
    #
    # COUPLING: this must stay <= MNTClient's httpx max_connections minus a
    # small slack (see clients/mnt_client.py, ~max_connections=20). If this is
    # raised, raise max_connections in lockstep or an enriched call will
    # pool-timeout against the client's own connection limit.
    ENRICHMENT_MAX_CONCURRENCY = 10

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
        Return sessions with full detail from the Get Session Details API.

        Routing:
        - MAC or username supplied -> that identifier's dedicated MnT endpoint,
          a SINGLE GET that returns the full detail directly. No AuthList
          download, no separate enrichment pass, and no time window (so a
          session that authenticated before the lookback is still found).
        - Neither supplied (e.g. a latency-range-only query) -> AuthList scan,
          then a bounded per-session enrichment fan-out.

        limit default 1, max 10.
        """
        minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
        limit = validate_limit(limit, max_limit=10)
        if calling_station_id:
            calling_station_id = validate_mac_address(calling_station_id)
        validate_latency_range(min_latency_ms, max_latency_ms)

        async with self._handle_mnt_errors("searching enriched sessions"):
            has_latency_filter = min_latency_ms is not None or max_latency_ms is not None

            if calling_station_id or username:
                # MAC takes precedence: it identifies the endpoint, whereas one
                # username can span several concurrent sessions.
                if calling_station_id:
                    endpoint = self._mac_endpoint(calling_station_id)
                    filters_applied = {
                        "lookup": "direct", "calling_station_id": calling_station_id,
                    }
                else:
                    endpoint = self._username_endpoint(username)
                    filters_applied = {"lookup": "direct", "username": username}
                enriched_sessions = await self._fetch_session_detail(endpoint)
                total_sessions_found = len(enriched_sessions)
            else:
                cap = self.ENRICHMENT_CAP if has_latency_filter else limit
                filtered_sessions, total_sessions_found = await self._fetch_auth_list_sessions(
                    filters={}, retention_cap=cap, minutes=minutes,
                )
                filters_applied = {"lookup": "authlist_scan", "minutes": minutes}

                sessions_to_enrich = filtered_sessions[:cap]
                # Bound the enrichment fan-out to at most
                # ENRICHMENT_MAX_CONCURRENCY concurrent per-session GETs. A
                # per-call Semaphore keeps this a width limiter for THIS call
                # only (not cross-call admission). gather preserves order, and
                # _enrich_session still returns Optional and handles its own
                # per-session errors, so None-dropping is unchanged.
                enrichment_semaphore = asyncio.Semaphore(self.ENRICHMENT_MAX_CONCURRENCY)

                async def _bounded_enrich(session: ActiveSession) -> Optional[SessionDetail]:
                    async with enrichment_semaphore:
                        return await self._enrich_session(session)

                enrichment_results = await asyncio.gather(
                    *[_bounded_enrich(s) for s in sessions_to_enrich]
                )
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

    async def get_active_session_counts(self) -> SessionCountResult:
        """Fetch the active, posture, and profiler session counts.

        Three independent MnT endpoints, fetched concurrently. gather's default
        return_exceptions=False is what we want here: a partial answer would be
        indistinguishable from a genuine zero, so any failure fails the call.
        """
        async with self._handle_mnt_errors("fetching session counts"):
            active_resp, posture_resp, profiler_resp = await asyncio.gather(
                self.mnt_client.get("Session/ActiveCount"),
                self.mnt_client.get("Session/PostureCount"),
                self.mnt_client.get("Session/ProfilerCount"),
            )
            return SessionCountResult(
                active_count=parse_session_count_xml(active_resp.text),
                posture_count=parse_session_count_xml(posture_resp.text),
                profiler_count=parse_session_count_xml(profiler_resp.text),
            )
