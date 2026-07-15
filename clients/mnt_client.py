# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import asyncio
import re
from typing import Optional, Tuple

import httpx

from logger import logger
from clients.exceptions import (
    MissingIseCredentialError,
    MissingServiceAccountError,
)
from clients.request_context import get_per_user_credential
from clients.settings import settings
from clients.tls import build_ssl_context
from clients.url_safety import validate_endpoint, assert_url_under_base


# Path of the ISE OpenAPI endpoint that returns deployment-node metadata
# (hostname / fqdn / ipAddress / roles / services / nodeStatus). We hit
# it once, on the very first MnT call, with a server-side filter that
# returns only the Primary Monitoring node, and pin all subsequent MnT
# traffic at that node's FQDN. See ``MNTClient._discover_mnt_fqdn``.
#
# Reference: ISE Deployment OpenAPI -- "Get all the deployment nodes
# details" (operation id ``getDeploymentNodes``). The ``filter`` query
# param accepts ``<field>.<op>.<value>``; ``roles.EQ.PrimaryMonitoring``
# returns the node currently holding the PrimaryMonitoring persona.
#
# Standalone deployments deliberately return an empty ``response``
# list here -- the lone node holds role ``Standalone``, not
# ``PrimaryMonitoring`` -- which is the intended signal to fall back
# to the PAN IP for MnT calls. See the ``not nodes`` branch of
# ``_discover_mnt_fqdn``.
_DEPLOYMENT_NODE_PATH = "/api/v1/deployment/node"
_PRIMARY_MNT_FILTER = "roles.EQ.PrimaryMonitoring"

# PAN host used for the one-time Deployment-API discovery call AND for
# the PAN-fallback MnT base URL. Sourced from ``settings.ise_ip`` (the
# ``ISE_IP`` .env value), read dynamically at use-time so it reflects
# the configured PAN address for the running environment (native host,
# remote appliance, or container).
#
# In a same-host container deployment where MCP shares the host with
# the ISE PAN, set ``ISE_IP=host.docker.internal`` and publish
# ``host.docker.internal: host-gateway`` in the compose ``extra_hosts``
# so the name resolves to the host running the PAN. In all other
# deployments set ``ISE_IP`` to the PAN's reachable IP or FQDN.
#
# NOTE: the per-user ``X-ISE-Authorization`` credential is only valid on
# the PAN the user authenticated against; ``ISE_IP`` must therefore point
# at that PAN, not at some other node in the deployment.
def _pan_host_for_mnt() -> str:
    """Return the PAN host for MnT/Deployment calls (from ``ISE_IP``)."""
    return settings.ise_ip

# Host-name allow-list applied to the FQDN we pull out of the Deployment
# response before composing the new MnT base URL. Even though the value
# comes from the ISE PAN itself (trusted source), we defend against a
# malformed/spoofed value tipping us into URL-injection on the MnT base
# URL. Letters/digits/hyphens/dots only, 1-253 chars total.
_FQDN_ALLOWED = re.compile(r"^[A-Za-z0-9.-]{1,253}$")


# ``MissingIseCredentialError`` and ``MissingServiceAccountError`` are
# defined once in ``clients.exceptions`` and re-exported here so that
# ``except`` clauses match the same class object regardless of whether
# the failure originated in the MnT path or in
# ``clients.client_factory``. Keeping them importable from this module
# preserves the existing public surface.
__all__ = [
    "MNTClient",
    "mnt_client",
    "MissingIseCredentialError",
    "MissingServiceAccountError",
]


class _NoOpAuth(httpx.Auth):
    """An ``httpx.Auth`` flow that yields the request unmodified.

    Used as a per-call ``auth=`` override on the singleton MNTClient
    when we've already attached an explicit ``Authorization`` header
    that must win over the client-level ``httpx.BasicAuth``. Without
    this override, httpx's auth-flow stage would run AFTER the
    per-call headers are set and overwrite our explicit Authorization
    with the service-account Basic credentials. See
    https://www.python-httpx.org/advanced/authentication/ -- the
    client-level auth applies whenever the request-level auth is left
    at ``httpx._client.UNSET`` (the default), and the only documented
    way to neutralise it for one call is to pass another ``Auth`` flow.
    """

    requires_request_body = False
    requires_response_body = False

    def auth_flow(self, request):  # type: ignore[override]
        yield request


class MNTClient:
    """
    Singleton HTTP client for Cisco ISE Monitoring and Troubleshooting (MNT) APIs.

    The MNT API uses Basic Authentication and returns XML responses.
    Configuration is sourced from ``clients.settings.settings`` (Pydantic
    Settings, ``SecretStr``-backed password). The async HTTP client is
    created during ``setup()`` (call during server startup).

    Security posture: TLS peer verification is on by default (configurable
    via ISE_VERIFY_SERVER_CERT, see ``clients/tls.py``); TLS 1.2+ is enforced.
    Redirects are not followed.
    """

    _instance: Optional["MNTClient"] = None
    _initialized: bool = False

    def __new__(cls) -> "MNTClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if MNTClient._initialized:
            return

        # PAN-pointing fallback URL. Used until lazy discovery succeeds
        # (or for the lifetime of the process if discovery determines
        # that the deployment is standalone, i.e. no node holds the
        # PrimaryMonitoring role).
        #
        # Built from ``settings.ise_ip`` (the ``ISE_IP`` .env value) via
        # ``_pan_host_for_mnt()``: see that function's docstring for the
        # rationale (the per-user credential is only valid on the PAN
        # the user logged into, which ``ISE_IP`` must point at).
        self._pan_base_url: str = self._compose_mnt_base_url(_pan_host_for_mnt())
        # Effective base URL the next ``get()`` will use. Swapped to the
        # MnT-FQDN URL after a successful discovery; otherwise stays at
        # the PAN URL.
        self.base_url: str = self._pan_base_url

        self._client: Optional[httpx.AsyncClient] = None

        # --- one-time MnT-FQDN discovery state ----------------------
        # ``_mnt_fqdn`` is the FQDN we extracted from the Deployment API
        # response (e.g. ``piyukum3-79.sn.test``), or ``None`` if we
        # never discovered one. ``_discovery_succeeded`` flips to True
        # the first time we either (a) got a valid FQDN, OR (b) got an
        # empty ``response`` array from the Deployment API (standalone
        # deployments are the textbook case: a lone node holds role
        # ``Standalone``, not ``PrimaryMonitoring``, so the filter
        # returns 0 hits and we keep using the PAN URL forever). Once
        # this flag is True, no further discovery calls are made for
        # the lifetime of the process; operators move the MnT role by
        # restarting the MCP container, which clears this state.
        #
        # Network/HTTP errors and malformed JSON do NOT set this flag
        # to True, so the very next ``get()`` will retry discovery.
        self._mnt_fqdn: Optional[str] = None
        self._discovery_succeeded: bool = False
        # Serialise concurrent first-time discovery attempts so 50
        # simultaneous tool calls don't all fire 50 Deployment GETs.
        self._discovery_lock: asyncio.Lock = asyncio.Lock()

        MNTClient._initialized = True
        logger.info("MNTClient initialized (config validated)")

    @staticmethod
    def _compose_mnt_base_url(host: str) -> str:
        """Build the MnT base URL for ``host`` (PAN IP or MnT FQDN).

        Keeps the existing path/port contract intact; only the host
        component varies between the PAN-fallback URL and the
        discovered-FQDN URL.
        """
        return f"https://{host}:{settings.api_port}/admin/API/mnt/"

    async def setup(self) -> None:
        """Create the async HTTP client. Call during server startup (lifespan hook).

        Service-account Basic-auth is wired in as the client-level
        default only when ``API_USERNAME`` and ``API_PWD`` are both
        present. When absent, the client is built without an auth
        flow; per-request flows that carry an
        ``X-ISE-Authorization`` header inject their own Authorization
        header per-call, and client-certificate auth authenticates via
        the shared TLS context -- both are unaffected. Only requests
        that would need the SA fallback (no header, no client cert)
        fail loud in that configuration (see ``get()``).
        """
        if self._client is not None:
            logger.debug("MNT client already set up")
            return

        auth: Optional[httpx.Auth]
        if settings.api_username and settings.api_pwd:
            auth = httpx.BasicAuth(
                settings.api_username, settings.api_pwd.get_secret_value()
            )
            logger.info(
                "MNT client: service-account fallback configured "
                "(per-user X-ISE-Authorization still takes precedence "
                "when forwarded)"
            )
        else:
            auth = None
            if settings.client_cert_configured:
                logger.info(
                    "MNT client: no service-account credentials in .env -- "
                    "MNT calls authenticate with the configured client "
                    f"certificate (or a forwarded "
                    f"'{settings.credential_header_name}' when present)"
                )
            else:
                logger.info(
                    "MNT client: no service-account credentials in .env -- "
                    "all MNT calls MUST carry "
                    f"'{settings.credential_header_name}'"
                )

        headers = {"Accept": "application/xml"}

        timeout = httpx.Timeout(
            connect=settings.connect_timeout_s,
            read=settings.read_timeout_s,
            write=settings.write_timeout_s,
            pool=settings.pool_timeout_s,
        )

        self._client = httpx.AsyncClient(
            auth=auth,
            headers=headers,
            verify=build_ssl_context(),
            timeout=timeout,
            follow_redirects=False,
        )

        logger.info("MNT client setup complete")

    async def _get_client(self) -> httpx.AsyncClient:
        """Return the live async HTTP client or raise if ``setup()`` hasn't run."""
        if self._client is None or self._client.is_closed:
            raise RuntimeError(
                "MNT client not initialized. Call await mnt_client.setup() during server startup."
            )
        return self._client

    def _resolve_per_call_auth(self) -> Tuple[dict, str]:
        """Pick the auth flow for the current request and report it.

        Returns ``(per_call_kwargs, auth_path_label)`` where
        ``per_call_kwargs`` is spread into ``httpx.AsyncClient.get(...)``
        and ``auth_path_label`` is a stable string for logs
        (``"per_user_credential"``, ``"client_certificate"``, or
        ``"service_account"``).

        Selection order (precedence, highest first):
          1. If the inbound MCP request carried an
             ``X-ISE-Authorization`` header, attach it verbatim plus a
             no-op ``auth=`` flow so httpx's client-level BasicAuth
             cannot overwrite us.
          2. Else, if a client certificate is configured, send no
             ``Authorization`` header plus a no-op ``auth=`` flow (so
             the client-level BasicAuth can't inject SA creds); the
             cert authenticates the request via the shared TLS context.
          3. Else, if ``require_per_user_credential`` is True, refuse.
          4. Else, if no SA creds are configured, refuse loudly.
          5. Otherwise, return empty kwargs (client-level BasicAuth
             does the work) and label it as SA fallback.
        """
        per_user_credential = get_per_user_credential()
        if per_user_credential:
            return (
                {
                    "headers": {"Authorization": per_user_credential},
                    "auth": _NoOpAuth(),
                },
                "per_user_credential",
            )
        # Cert mode: client cert configured -> standalone auth. Send no
        # Authorization header; _NoOpAuth neutralises the client-level
        # BasicAuth so it can't inject SA creds. The cert itself (loaded
        # in the shared TLS context) authenticates the request.
        if settings.client_cert_configured:
            return ({"auth": _NoOpAuth()}, "client_certificate")
        if settings.require_per_user_credential:
            raise MissingIseCredentialError(
                "ISE_REQUIRE_PER_USER_CREDENTIAL=true but no "
                f"'{settings.credential_header_name}' header was "
                "forwarded with this request."
            )
        if not (settings.api_username and settings.api_pwd):
            raise MissingServiceAccountError(
                "MNT service-account fallback unavailable: "
                "API_USERNAME / API_PWD are not configured and this "
                "request did not carry "
                f"'{settings.credential_header_name}'. Either configure "
                "SA creds in .env or ensure NVA forwards the header."
            )
        return ({}, "service_account")

    async def _ensure_mnt_target(self) -> None:
        """Run one-time MnT-FQDN discovery if it hasn't succeeded yet.

        Called at the top of every ``get()``. After a successful
        discovery this method is a no-op (``_discovery_succeeded`` is
        latched True for the lifetime of the process). After a FAILED
        discovery (network/HTTP/parse error) the flag stays False and
        the next ``get()`` re-tries, so the system self-heals once ISE
        becomes reachable.

        Discovery is serialised through ``_discovery_lock`` so the
        first burst of concurrent MnT calls doesn't fan out into N
        Deployment GETs.
        """
        if self._discovery_succeeded:
            return
        async with self._discovery_lock:
            # Re-check under the lock: another task may have completed
            # discovery while we were waiting to acquire it.
            if self._discovery_succeeded:
                return
            await self._discover_mnt_fqdn()

    async def _discover_mnt_fqdn(self) -> None:
        """Discover the Primary Monitoring node's FQDN and pin MnT to it.

        Hits ``GET {PAN}/api/v1/deployment/node?filter=roles.EQ.PrimaryMonitoring``
        with the same auth flow ``get()`` would use, parses the first
        ``response[].fqdn``, validates it, and swaps ``self.base_url``
        from the PAN URL to the FQDN URL.

        Outcomes:

        * Valid FQDN found -> pin MnT base URL to it, latch
          ``_discovery_succeeded=True``.
        * Deployment API returned an empty ``response[]`` (the standard
          standalone-deployment case -- the lone node holds role
          ``Standalone``, not ``PrimaryMonitoring``, so the filter
          returns zero hits and the PAN IP IS the MnT node) -> keep
          PAN base URL, latch ``_discovery_succeeded=True`` so we
          don't retry forever.
        * Anything else (network, HTTP, JSON parse, missing/blank/bad
          FQDN) -> log WARNING, leave the flag False; the next
          ``get()`` will retry. We never propagate the discovery error
          out of here because falling back to the PAN URL is strictly
          better than failing every MnT call until ISE is fully
          available again.
        """
        try:
            per_call_kwargs, auth_path = self._resolve_per_call_auth()
        except (MissingIseCredentialError, MissingServiceAccountError) as exc:
            # No auth path is available for THIS request, so we can't
            # discover. Don't latch -- the next request may have a
            # per-user credential and succeed. Log at debug because the
            # caller's own auth check will surface the same condition
            # as a hard error in a moment.
            logger.debug(
                "MnT FQDN discovery skipped (no usable auth flow on this "
                "request); will retry on the next MnT call",
                error=str(exc),
            )
            return

        client = await self._get_client()
        # Deployment-API discovery target. ``_pan_host_for_mnt()`` returns
        # the configured PAN host (``ISE_IP``), which must point at the PAN
        # that minted the user's credential. See the function's docstring.
        url = (
            f"https://{_pan_host_for_mnt()}:{settings.api_port}"
            f"{_DEPLOYMENT_NODE_PATH}"
        )
        # The Deployment API returns JSON. The MnT singleton client
        # carries ``Accept: application/xml`` as its default header, so
        # we override per-call. Likewise authority must match the PAN,
        # not whatever ``self.base_url`` happens to be.
        per_call_kwargs.setdefault("headers", {})
        per_call_kwargs["headers"] = {
            **per_call_kwargs["headers"],
            "Accept": "application/json",
        }
        logger.info(
            "MnT FQDN discovery: GET %s?filter=%s (auth=%s)",
            url,
            _PRIMARY_MNT_FILTER,
            auth_path,
        )
        try:
            response = await client.get(
                url,
                params={"filter": _PRIMARY_MNT_FILTER},
                **per_call_kwargs,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning(
                "MnT FQDN discovery failed; falling back to PAN for this "
                "call and will retry on the next MnT call",
                error=str(exc),
                pan_base_url=self._pan_base_url,
            )
            return

        if not isinstance(payload, dict):
            logger.warning(
                "MnT FQDN discovery: unexpected payload type; falling back "
                "to PAN and will retry",
                payload_type=type(payload).__name__,
            )
            return

        nodes = payload.get("response")
        if not isinstance(nodes, list):
            logger.warning(
                "MnT FQDN discovery: 'response' field missing or not a "
                "list; falling back to PAN and will retry",
            )
            return

        if not nodes:
            # Standalone deployment: no node holds the PrimaryMonitoring
            # role (the lone node holds 'Standalone' instead). PAN IS
            # the MnT node, so we keep ``self.base_url`` pointed at the
            # PAN and latch success so we never retry.
            self._discovery_succeeded = True
            logger.info(
                "MnT FQDN discovery: no PrimaryMonitoring node in this "
                "deployment (standalone). Keeping MnT base URL pointed "
                "at the PAN: %s",
                self._pan_base_url,
            )
            return

        first = nodes[0]
        fqdn = first.get("fqdn") if isinstance(first, dict) else None
        if not isinstance(fqdn, str) or not fqdn.strip():
            logger.warning(
                "MnT FQDN discovery: first node has no usable 'fqdn'; "
                "falling back to PAN and will retry",
                node_keys=list(first.keys()) if isinstance(first, dict) else None,
            )
            return

        fqdn = fqdn.strip()
        if not _FQDN_ALLOWED.match(fqdn):
            # Defence-in-depth against a malformed/spoofed value tipping
            # us into URL-injection on the MnT base URL. The Deployment
            # response is from the ISE PAN itself so this should never
            # happen, but a typo'd or attacker-controlled value would.
            logger.warning(
                "MnT FQDN discovery: 'fqdn' failed allow-list "
                "validation; falling back to PAN and will retry",
                fqdn_chars=len(fqdn),
            )
            return

        self._mnt_fqdn = fqdn
        self.base_url = self._compose_mnt_base_url(fqdn)
        self._discovery_succeeded = True
        logger.info(
            "MnT FQDN discovery: pinning MnT base URL to discovered "
            "PrimaryMonitoring node",
            mnt_fqdn=fqdn,
            mnt_base_url=self.base_url,
            pan_base_url=self._pan_base_url,
        )

    async def get(self, endpoint: str) -> httpx.Response:
        """
        Make a GET request to the MNT API.

        Args:
            endpoint: The API endpoint path (e.g., "Session/ActiveList").
                Must be a relative path; absolute URLs, traversal, and
                control characters are rejected by ``validate_endpoint``.

        Returns:
            httpx.Response object with the XML response.

        Raises:
            ValueError: For unsafe endpoint inputs.
            httpx.HTTPError: For network or HTTP errors.
            MissingIseCredentialError: When the operator requires a
                per-user credential and the request did not carry one.
        """
        validate_endpoint(endpoint)
        client = await self._get_client()

        # Lazily discover the Primary Monitoring node's FQDN on the
        # first call (and re-attempt on every call until discovery
        # latches success). Discovery runs under a per-singleton lock
        # so concurrent first-time MnT calls don't fan out into N
        # Deployment GETs. After the first successful discovery this
        # is a cheap flag-check no-op.
        await self._ensure_mnt_target()

        # ``self.base_url`` is whatever ``_ensure_mnt_target`` left in
        # place: the discovered MnT-FQDN URL if discovery succeeded,
        # otherwise the PAN URL (either as a temporary fallback while
        # we retry, or permanently for standalone deployments).
        url = f"{self.base_url}{endpoint}"
        assert_url_under_base(url, self.base_url)

        # Per-call auth selection. When the current MCP request carried
        # an X-ISE-Authorization header, swap the service-account
        # Basic-auth out for the user's value on THIS call only. We
        # override at request scope rather than mutating the shared
        # AsyncClient because the client is a singleton shared across
        # concurrent calls -- a global swap would create a cross-user
        # credential race.
        per_call_kwargs, auth_path = self._resolve_per_call_auth()
        logger.info(
            "MNT API GET",
            url=url,
            auth_path=auth_path,
            mnt_fqdn_pinned=bool(self._mnt_fqdn),
        )

        try:
            response = await client.get(url, **per_call_kwargs)
            response.raise_for_status()
            logger.info(
                "MNT API response",
                status_code=response.status_code,
                url=url,
            )
            return response
        except httpx.HTTPStatusError as e:
            logger.error(
                "MNT HTTP error",
                status_code=e.response.status_code,
                response_text=e.response.text[:200],
            )
            raise
        except httpx.RequestError as e:
            logger.error("MNT request error", error=str(e))
            raise

    async def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("MNT client connection closed")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(base_url={self.base_url!r})"


mnt_client = MNTClient()
