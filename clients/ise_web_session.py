# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Authenticated session for the ISE admin web UI (/admin/*).

This surface uses a session cookie (APPSESSIONID + MNTLA_JWT_TOKEN),
NOT the Basic auth MnT uses. Cookie acquisition is tiered:

* Tier 1 (preferred): a cookie configured in settings
  (``ise_admin_session_cookie``). Used directly; on expiry we FAIL
  LOUD (no fallback) so an operator-supplied cookie is honored as a
  deliberate choice.
* Tier 2 (fallback): form login against /admin/LoginAction.do, used
  only when no env cookie is configured. Fully self-contained here and
  intended to be removable without touching callers.

All 302/re-auth handling lives inside ``get()``. Callers receive a
ready response or an ``IseSessionAuthError``.
"""

import asyncio
import base64
import binascii
import hashlib
import re
from typing import Optional

import httpx

from logger import logger
from clients.request_context import get_per_user_credential
from clients.settings import settings
from clients.tls import build_ssl_context

__all__ = ["IseWebSession", "ise_web_session", "IseSessionAuthError"]

_CSRF_RE = re.compile(r"value=(OWASP_CSRFTOKEN=[A-Za-z0-9-]+)")
_LOGIN_PAGE_PATH = "/admin/login.jsp"
_LOGIN_ACTION_PATH = "/admin/LoginAction.do"
_SERVICE_ACCOUNT_KEY_MATERIAL = "__service_account__"


class IseSessionAuthError(Exception):
    """Unrecoverable authentication failure against the ISE admin UI."""


class IseWebSession:
    _instance: Optional["IseWebSession"] = None
    _initialized: bool = False

    def __new__(cls) -> "IseWebSession":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if IseWebSession._initialized:
            return
        self._client: Optional[httpx.AsyncClient] = None
        # Per-credential authenticated cookie jars and single-flight locks,
        # keyed by _credential_cache_key(). Isolates concurrent distinct
        # users so one user's admin session is never reused for another.
        self._sessions: dict[str, httpx.Cookies] = {}
        self._session_locks: dict[str, asyncio.Lock] = {}
        IseWebSession._initialized = True
        logger.info("IseWebSession initialized")

    @property
    def base_url(self) -> str:
        return f"https://{settings.ise_ip}:{settings.api_port}"

    async def setup(self) -> None:
        if self._client is not None:
            return
        timeout = httpx.Timeout(
            connect=settings.connect_timeout_s,
            read=settings.read_timeout_s,
            write=settings.write_timeout_s,
            pool=settings.pool_timeout_s,
        )
        # follow_redirects=False so we can detect the 302->login flow.
        self._client = httpx.AsyncClient(
            verify=build_ssl_context(),
            timeout=timeout,
            follow_redirects=False,
        )
        logger.info("IseWebSession setup complete")

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            raise RuntimeError(
                "IseWebSession not initialized. Call await ise_web_session.setup()."
            )
        return self._client

    def _has_env_cookie(self) -> bool:
        c = settings.ise_admin_session_cookie
        return bool(c and c.get_secret_value().strip())

    def _credential_cache_key(self) -> str:
        """Opaque per-credential cache key for the current request.

        Returns a sha256 hex digest of the per-user header value when one is
        present, else of a fixed service-account sentinel. The raw credential
        is NEVER stored or logged; only this digest is used as a dict key so
        concurrent distinct users get isolated cookie jars.
        """
        material = get_per_user_credential() or _SERVICE_ACCOUNT_KEY_MATERIAL
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def _lock_for_key(self, key: str) -> asyncio.Lock:
        # Single event loop assumed (check-then-set is safe). Bounded key
        # space (one per distinct credential), so not pruned.
        lock = self._session_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._session_locks[key] = lock
        return lock

    def _clear_shared_jar(self) -> None:
        # The per-request `cookies=jar` we pass is the source of truth for
        # auth state; the singleton client's own jar must stay empty so one
        # user's Set-Cookie can never be replayed on another user's request.
        if self._client is not None:
            self._client.cookies.clear()

    def _resolve_login_credentials(self) -> tuple[str, str]:
        """Resolve (username, password) for Tier-2 form login.

        Prefers the per-request X-ISE-Authorization credential (a
        ``Basic <b64(user:pass)>`` value), decoding it to user/pass. Falls
        back to the configured service account when no header is present.

        Never logs the value or the decoded username/password.
        """
        cred = get_per_user_credential()
        if cred:
            token = cred[6:].strip() if cred[:6].lower() == "basic " else cred
            try:
                decoded = base64.b64decode(token, validate=True).decode("utf-8")
            except (binascii.Error, ValueError, UnicodeDecodeError):
                raise IseSessionAuthError(
                    "Per-user credential header is not valid Base64; cannot "
                    "authenticate to the ISE admin UI."
                )
            if ":" not in decoded:
                raise IseSessionAuthError(
                    "Per-user credential header did not decode to user:password."
                )
            username, password = decoded.split(":", 1)
            return username, password

        if settings.api_username and settings.api_pwd:
            return settings.api_username, settings.api_pwd.get_secret_value()

        raise IseSessionAuthError(
            "Form login requires a per-user credential or API_USERNAME / "
            "API_PWD, but none are available, and no ISE_ADMIN_SESSION_COOKIE "
            "is configured."
        )

    @staticmethod
    def _is_login_redirect(resp: httpx.Response) -> bool:
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("location", "")
            return "/login.jsp" in loc or loc.endswith("login.jsp")
        return resp.status_code == 401

    async def get(self, url: str, *, headers: Optional[dict] = None) -> httpx.Response:
        """Make an authenticated GET against the ISE admin UI.

        Returns a ready response (200/304) or raises IseSessionAuthError.
        All re-auth/retry logic is encapsulated here.
        """
        client = await self._get_client()
        req_headers = dict(headers or {})

        if self._has_env_cookie():
            req_headers["Cookie"] = settings.ise_admin_session_cookie.get_secret_value()
            resp = await client.get(url, headers=req_headers)
            if self._is_login_redirect(resp):
                raise IseSessionAuthError(
                    "Configured ISE_ADMIN_SESSION_COOKIE has expired or is "
                    "invalid (redirected to login). Refresh the cookie value."
                )
            return resp

        # Tier 2: form login (implemented in Task 4).
        return await self._get_with_form_login(url, req_headers)

    @staticmethod
    def _scrape_csrf(html: str) -> str:
        m = _CSRF_RE.search(html)
        if not m:
            raise IseSessionAuthError(
                "Could not find CSRF token on ISE login page."
            )
        return m.group(1)

    async def _form_login(self) -> httpx.Cookies:
        """GET login.jsp, scrape CSRF, POST credentials. Assert 302.

        Uses the current request's resolved credentials (per-user header
        when present, else service account). Returns a fresh authenticated
        cookie jar. Passes cookies per-call so the singleton client's shared
        jar never mixes sessions across users.
        """
        username, password = self._resolve_login_credentials()
        client = await self._get_client()
        jar = httpx.Cookies()
        page = await client.get(f"{self.base_url}{_LOGIN_PAGE_PATH}", cookies=jar)
        self._clear_shared_jar()
        jar.update(page.cookies)
        csrf = self._scrape_csrf(page.text)
        data = {
            "name": username,
            "password": password,
            "authType": "Internal",
            "newPassword": "",
            "destinationURL": "",
            "CSRFTokenNameValue": csrf,
            "OWASP_CSRFTOKEN": csrf.split("=", 1)[1],
            "locale": "en",
            "hasSelectedLocale": "false",
        }
        resp = await client.post(
            f"{self.base_url}{_LOGIN_ACTION_PATH}", data=data, cookies=jar
        )
        self._clear_shared_jar()
        if resp.status_code != 302:
            raise IseSessionAuthError(
                "ISE form login failed (expected 302, got "
                f"{resp.status_code}). Check the credential and that the admin "
                "identity source is Internal."
            )
        jar.update(resp.cookies)
        logger.info("IseWebSession form login succeeded")
        return jar

    async def _get_with_form_login(self, url: str, headers: dict) -> httpx.Response:
        key = self._credential_cache_key()
        # Single-flight per credential: one login in flight per distinct user.
        async with self._lock_for_key(key):
            jar = self._sessions.get(key)
            if jar is None:
                jar = await self._form_login()
                self._sessions[key] = jar
        client = await self._get_client()
        resp = await client.get(url, headers=headers, cookies=jar)
        self._clear_shared_jar()
        if self._is_login_redirect(resp):
            # Session expired mid-use: re-auth once for this credential, retry.
            async with self._lock_for_key(key):
                jar = await self._form_login()
                self._sessions[key] = jar
            resp = await client.get(url, headers=headers, cookies=jar)
            self._clear_shared_jar()
            if self._is_login_redirect(resp):
                raise IseSessionAuthError(
                    "ISE session still unauthorized after re-login."
                )
        return resp

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("IseWebSession closed")


ise_web_session = IseWebSession()
