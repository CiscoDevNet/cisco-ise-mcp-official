# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Optional
from urllib.parse import quote

import httpx
from fastmcp.exceptions import ToolError as McpToolError

from logger import logger
from clients.mnt_client import MNTClient
from utils.xml_parser import (
    parse_auth_status_xml,
    parse_failure_reasons_xml,
    parse_session_detail_xml,
)
from utils.input_validators import validate_minutes, validate_limit, validate_mac_address, validate_username
from models.error_models import ErrorCategory, find_tls_error, raise_tool_error
from models.failure_models import AaaFailureDetail, AaaFailureInvestigationResult
from services.failure_context_resolver import FailureContextResolver


class FailureToolHandler:
    """Handler for ISE MNT AAA failure investigation APIs.

    The ``FailureContextResolver`` it uses for enrichment depends on the
    ISE ``FailureReasons`` MnT catalog, which can only be fetched from
    ISE with valid credentials. To keep the MCP server's startup
    network-free (and to ensure that the catalog is fetched with the
    per-user credential from the inbound MCP request, not with the
    service account at startup), the resolver is built lazily on the
    first AAA-failure tool call. See :meth:`_get_failure_resolver`.
    """

    MAX_MINUTES = 24 * 60
    MAX_LIMIT = 10

    def __init__(self, mnt_client: MNTClient):
        self.mnt_client = mnt_client
        # Local in-memory ISE message catalog. Attached at startup via
        # :meth:`attach_msg_catalog`. Used by the
        # ``FailureContextResolver`` to translate execution-step codes
        # to human-readable text. Loaded from a packaged XML file --
        # NO network access.
        self._msg_catalog: Dict[str, str] = {}
        # Lazily-built resolver. ``None`` until the first successful
        # ``FailureReasons`` fetch. We do NOT latch a failed attempt --
        # the next AAA-failure tool call retries, so the system
        # self-heals once ISE becomes reachable / the user supplies a
        # working credential header.
        self._failure_context_resolver: Optional[FailureContextResolver] = None
        # Serialise concurrent first-time resolver builds so the first
        # burst of AAA-failure tool calls doesn't fan out into N
        # FailureReasons GETs.
        self._resolver_lock = asyncio.Lock()

    def attach_msg_catalog(self, msg_catalog: Dict[str, str]) -> None:
        """Attach the locally-parsed ISE message catalog.

        Called from the FastMCP lifespan hook after the catalog has
        been parsed from disk. The catalog is consumed lazily by the
        ``FailureContextResolver`` when it's first built.
        """
        self._msg_catalog = msg_catalog

    async def _get_failure_resolver(self) -> Optional[FailureContextResolver]:
        """Return a ready ``FailureContextResolver`` or ``None`` on failure.

        Lazy build: the FailureReasons MnT GET is issued on the first
        call (and on retries after a previous failure), inside the
        current MCP request's task -- so the per-user
        ``X-ISE-Authorization`` set by ``IseCredentialMiddleware`` is
        in scope and ``mnt_client.get`` will authenticate with the
        end user's credential rather than the service account.

        Failure mode: if FailureReasons cannot be fetched/parsed, the
        method returns ``None``. Callers must degrade gracefully (see
        ``investigate_aaa_failure`` / ``_build_fallback_details``).
        We deliberately do NOT cache the failure: the next AAA-failure
        tool call retries, so transient ISE/network outages don't
        permanently disable enrichment for the lifetime of the process.
        """
        if self._failure_context_resolver is not None:
            return self._failure_context_resolver
        async with self._resolver_lock:
            # Re-check under the lock: another task may have completed
            # the build while we were waiting to acquire it.
            if self._failure_context_resolver is not None:
                return self._failure_context_resolver
            try:
                response = await self.mnt_client.get("FailureReasons")
                failure_reasons_catalog = parse_failure_reasons_xml(response.text)
            except Exception as exc:  # noqa: BLE001
                # Don't latch -- next call will retry. Log the *type*
                # of failure but never the raw response body, which
                # may quote the request URL and the value of the
                # Authorization header in some ISE error pages.
                logger.warning(
                    "Lazy FailureReasons load failed -- AAA failure "
                    "enrichment will run in degraded mode for this "
                    "call and retry on the next call",
                    error=str(exc),
                )
                return None
            self._failure_context_resolver = FailureContextResolver(
                self._msg_catalog, failure_reasons_catalog
            )
            logger.info(
                "Failure context resolver ready (lazy, per-user-credential path)",
                count=len(failure_reasons_catalog),
            )
            return self._failure_context_resolver

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
                "The ISE MNT API is unreachable or timed out. Try again later.",
                retry=True,
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

    async def _fetch_failures_by_mac(
        self, mac_address: str, minutes: int, limit: int,
    ) -> tuple[List[Dict], int]:
        """Fetch auth status by MAC and return (failed_entries, total_failed_count).

        Fetches ``limit * 2`` records (capped at 10) to allow for filtering
        out passing authentications, then returns only failures sorted by
        timestamp descending, truncated to ``limit``.
        """
        seconds = minutes * 60
        fetch_records = min(limit * 2, 10)
        endpoint = f"AuthStatus/MACAddress/{quote(mac_address, safe=':')}/{seconds}/{fetch_records}/All"

        logger.info("Fetching auth status by MAC", mac_address=mac_address, seconds=seconds, records=fetch_records)
        response = await self.mnt_client.get(endpoint)
        all_entries = parse_auth_status_xml(response.text)

        failures = [e for e in all_entries if e.get("failed") is True]
        total_failed = len(failures)
        return failures[:limit], total_failed

    async def _fetch_failure_by_username(self, username: str) -> tuple[List[Dict], int]:
        """Fetch latest session by username and return it as a failure if auth failed.

        Returns (failures_list, total_count) where total_count is 0 or 1.
        The ISE Session/UserName API returns HTTP 500 with body containing
        "is not available" when no session exists -- treated as empty result.
        """
        endpoint = f"Session/UserName/{quote(username, safe='')}"

        logger.info("Fetching session by username for failure check", username=username)
        try:
            response = await self.mnt_client.get(endpoint)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500 and "is not available" in e.response.text:
                logger.info("No session data available for user", username=username)
                return [], 0
            raise
        parsed = parse_session_detail_xml(response.text)

        if parsed.get("authentication_result") != "Failed":
            return [], 0

        return [parsed], 1

    def _build_fallback_details(self, raw_failures: List[Dict]) -> List[AaaFailureDetail]:
        """Build AaaFailureDetail objects without the FailureReasons catalog (degraded mode).

        Performs timestamp mapping and failure_reason splitting but cannot
        provide cause/resolution or resolve execution step codes.
        """
        results: List[AaaFailureDetail] = []
        for raw in raw_failures:
            timestamp = raw.get("acs_timestamp") or raw.get("auth_acs_timestamp")

            failure_reason_raw = raw.get("failure_reason")
            code: Optional[str] = None
            text: Optional[str] = None
            if failure_reason_raw and failure_reason_raw.strip():
                parts = failure_reason_raw.strip().split(None, 1)
                code = parts[0]
                text = parts[1] if len(parts) > 1 else None

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
                response=raw.get("response"),
                failure_context_note="Failure reasons catalog unavailable — cause/resolution not enriched",
            ))
        return results

    async def investigate_aaa_failure(
        self,
        mac_address: Optional[str] = None,
        username: Optional[str] = None,
        minutes: int = 1440,
        limit: int = 1,
    ) -> AaaFailureInvestigationResult:
        """Investigate AAA failures by MAC and/or username.

        Lookup priority: MAC (AuthStatus API) first.  If MAC finds failures,
        username lookup is skipped.  Falls back to username (Session API) only
        when MAC found no failures or was not provided.

        The ``FailureContextResolver`` used for enrichment is built
        lazily by :meth:`_get_failure_resolver` on the first call, so
        the ``FailureReasons`` MnT GET runs inside this request's
        task (and therefore with the per-user
        ``X-ISE-Authorization`` header in scope), not at server
        startup.

        Args:
            mac_address: Endpoint MAC address (any format).
            username: Username to search.
            minutes: Minutes to look back (1-1440, default 1440, MAC only).
            limit: Max failures to return (1-10, default 1, MAC only).

        Returns:
            AaaFailureInvestigationResult with enriched failure details.
        """
        if not mac_address and not username:
            raise_tool_error(
                ErrorCategory.CLIENT_ERROR, "MISSING_IDENTIFIER",
                "At least one of mac_address or username is required. "
                "Provide the endpoint MAC address, username, or both.",
            )

        if mac_address:
            mac_address = validate_mac_address(mac_address)
            minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
            limit = validate_limit(limit, max_limit=self.MAX_LIMIT)
        if username:
            username = validate_username(username)

        search_filters: Dict = {}
        if mac_address:
            search_filters["mac_address"] = mac_address
            search_filters["minutes"] = minutes
        if username:
            search_filters["username"] = username

        raw_failures: List[Dict] = []
        total_failures: int = 0
        source: Optional[str] = None

        async with self._handle_mnt_errors("investigating AAA failures"):
            if mac_address:
                raw_failures, total_failures = await self._fetch_failures_by_mac(
                    mac_address, minutes, limit,
                )
                if raw_failures:
                    source = "AuthStatus"
                    logger.info("Found failures via MAC lookup",
                                mac_address=mac_address, count=len(raw_failures))

            if not raw_failures and username:
                raw_failures, total_failures = await self._fetch_failure_by_username(username)
                if raw_failures:
                    source = "Session"
                    logger.info("Found failure via username fallback", username=username)

            if not raw_failures:
                logger.info("No AAA failures found", mac_address=mac_address, username=username)
                return AaaFailureInvestigationResult(
                    search_filters=search_filters,
                    total_failures_found=0,
                    actual_failures_returned=0,
                    has_more=False,
                    failures=[],
                )

            if source:
                search_filters["source_api"] = source

            # Resolve the resolver lazily, INSIDE the same task as the
            # MnT GETs above so the per-user X-ISE-Authorization
            # ContextVar set by IseCredentialMiddleware is visible to
            # ``mnt_client.get('FailureReasons')``. A ``None`` return
            # means the FailureReasons fetch failed; we degrade to
            # un-enriched details rather than failing the whole call.
            failure_context_resolver = await self._get_failure_resolver()
            if failure_context_resolver:
                enriched = failure_context_resolver.enrich_failures(raw_failures)
            else:
                enriched = self._build_fallback_details(raw_failures)

            return AaaFailureInvestigationResult(
                search_filters=search_filters,
                total_failures_found=total_failures,
                actual_failures_returned=len(enriched),
                has_more=total_failures > len(enriched),
                failures=enriched,
            )
