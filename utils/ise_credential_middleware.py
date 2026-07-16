# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""FastMCP middleware that lifts the per-request ISE credential
header into a ContextVar visible to downstream tool handlers."""

from typing import Optional

from fastmcp.server.dependencies import get_http_request
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

from clients.request_context import (
    reset_per_user_credential,
    set_per_user_credential,
)
from clients.settings import settings
from logger import logger


class IseCredentialMiddleware(Middleware):
    """
    Lift the per-request ISE credential header into a ContextVar.

    Implemented as a FastMCP middleware (NOT a Starlette ASGI or
    BaseHTTPMiddleware) on purpose. The streamable-HTTP transport
    dispatches the JSON-RPC tool call from the ASGI request task
    into an MCP session worker task; ``contextvars.ContextVar``
    values are bound per asyncio task and do NOT cross task
    boundaries. We confirmed this with two earlier attempts:

      1. BaseHTTPMiddleware -- documented Starlette limitation.
      2. Pure ASGI middleware -- worked in a Starlette-only smoke
         test, but the streamable-HTTP session worker still ran the
         tool handler in a different task, so the ContextVar set in
         the request task was invisible at ``get_client()`` time.

    FastMCP's own ``Middleware`` runs in the SAME task that executes
    the tool, so a ContextVar set in ``on_request`` is visible to
    every downstream ISE-client lookup
    (``client_factory.get_client()``, ``mnt_client.get()``).

    We reach into the original HTTP request via
    ``get_http_request()`` -- the supported FastMCP API for this --
    to read the configured header (default ``X-ISE-Authorization``).
    Its value is a fully-formed ``Basic <b64(user:pass)>`` string
    captured by NVA at user login. The ContextVar is reset in
    ``finally`` so nothing can leak across requests sharing this
    worker task.

    Logging discipline: we MUST NEVER log the value. Log only
    presence (a boolean), and never any prefix/suffix of the value.
    """

    async def on_request(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> object:
        # `on_request` covers every client->server request
        # (tools/call, resources/read, prompts/get, tools/list, ...),
        # so every ISE-touching code path sees the credential. For
        # stdio transport (no HTTP request) `get_http_request()`
        # raises -- treat as "no per-user creds, fall back".
        header_value: Optional[str] = None
        try:
            request = get_http_request()
        except Exception:
            request = None

        if request is not None:
            header_value = request.headers.get(settings.credential_header_name)

        if header_value:
            # Log PRESENCE only -- never the value. The header carries a
            # bearer credential (Base64 of ``user:password``) and must
            # not reach any logfile.
            logger.info(
                f"MCP middleware: received {settings.credential_header_name}"
            )
        else:
            # Loud INFO so the missing-header case is unmistakable in
            # the MCP server logs. If you see this on a tools/call you
            # expected to carry a per-user credential, the header was
            # either never attached by the agent (fix upstream) or
            # stripped by an intermediate proxy (none in the default
            # topology). Describe the ACTUAL next auth step, which
            # depends on how the server is configured (see the auth
            # precedence in client_factory / mnt_client).
            if settings.client_cert_configured:
                # A configured client cert authenticates the request on
                # its own -- no Authorization header is sent, and this
                # holds even under ISE_REQUIRE_PER_USER_CREDENTIAL=true.
                next_step = (
                    "client_factory / mnt_client will authenticate with "
                    "the configured client certificate"
                )
            elif settings.require_per_user_credential:
                next_step = (
                    "client_factory / mnt_client will refuse the request "
                    "(ISE_REQUIRE_PER_USER_CREDENTIAL=true)"
                )
            else:
                next_step = (
                    "client_factory / mnt_client will use the "
                    "service-account credentials"
                )
            logger.info(
                f"MCP middleware: NO {settings.credential_header_name} on "
                f"this request -- {next_step}"
            )

        token = set_per_user_credential(header_value)
        try:
            return await call_next(context)
        finally:
            reset_per_user_credential(token)
