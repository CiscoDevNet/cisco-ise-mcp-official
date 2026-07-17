# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""
Per-request ISE credential context.

The MCP server receives the end-user's pre-built
``Authorization: Basic <b64(user:pass)>`` value on each inbound MCP HTTP
request as a configurable header (default ``X-ISE-Authorization``,
see :class:`clients.settings.ISESettings.credential_header_name`).
FastMCP dispatches each tool call from a Starlette request to a
registered tool coroutine that does NOT receive headers in its
signature, so we make the value reachable from any tool handler via a
:class:`contextvars.ContextVar`.

A Starlette middleware (wired in :mod:`server.py`) sets the var on the
inbound request and resets it on the way out so values cannot leak
across requests in either the asyncio task tree or the worker process.

Logging discipline
------------------
The value held in the ContextVar MUST NEVER be logged. It is a bearer
credential -- anyone who holds it can authenticate to ISE as the
originating user until the user's session expires. Log only the
boolean `has_per_user_credential()`.
"""
from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Optional


# Public name kept deliberately verbose: searching the codebase for
# "ise_credential" should turn up exactly the places that read or write
# the per-request credential.
_ise_credential_header_value: ContextVar[Optional[str]] = ContextVar(
    "ise_credential_header_value", default=None
)


def set_per_user_credential(value: Optional[str]) -> Token:
    """Bind the per-request credential header value to the current task.

    Returns the ContextVar :class:`Token` so the caller (the middleware)
    can pass it to :func:`reset_per_user_credential` in a ``finally``
    block. Always reset what you set -- relying on the var auto-clearing
    when the task ends is fragile under task-group / streaming flows.
    """
    return _ise_credential_header_value.set(value)


def reset_per_user_credential(token: Token) -> None:
    """Restore the ContextVar to its prior value using the returned token."""
    _ise_credential_header_value.reset(token)


def get_per_user_credential() -> Optional[str]:
    """Return the credential header value for the current request, or ``None``.

    Returns the verbatim header value the agent forwarded, including
    the ``Basic `` prefix when present. The caller is responsible for
    enforcing the absence-policy (e.g. service-account fallback or
    401), see :class:`ISESettings.require_per_user_credential`.
    """
    return _ise_credential_header_value.get()


def has_per_user_credential() -> bool:
    """Cheap, log-safe check for "is a per-user credential available?".

    Use this in log lines instead of the value itself so the bearer
    credential never lands on disk.
    """
    return bool(get_per_user_credential())
