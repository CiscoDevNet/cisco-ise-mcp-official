# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""
Shared exception types for the ISE client layer.

Both ``clients.client_factory`` and ``clients.mnt_client`` need to
signal the same two credential-routing failures:

  * ``MissingIseCredentialError`` -- the operator requires a per-user
    credential and none was forwarded with the request.
  * ``MissingServiceAccountError`` -- the SA fallback path was taken
    but ``API_USERNAME`` / ``API_PWD`` are unset.

These classes live here (rather than being defined twice, once in each
module) so that callers anywhere in the codebase can write a single
``except MissingIseCredentialError`` clause and have it match
regardless of which client raised it. Defining identically-named
classes in two modules would produce two distinct types and silently
defeat that intent. Both client modules re-export these names so the
public import surface (``from clients.client_factory import
MissingIseCredentialError`` and ``from clients.mnt_client import
MissingIseCredentialError``) keeps working and resolves to the *same*
class object.
"""


class MissingIseCredentialError(RuntimeError):
    """Raised when per-user-credential is required but absent.

    The MCP server is configured with
    ``ISE_REQUIRE_PER_USER_CREDENTIAL=true``, the inbound request
    carried no credential header (or it was empty), and there is no
    legitimate service-account fallback to use. Tool handlers should
    let this propagate so FastMCP surfaces a clear error instead of
    silently calling ISE as the service account.
    """


class MissingServiceAccountError(RuntimeError):
    """Raised when SA fallback is attempted with no SA creds configured.

    Distinct from ``MissingIseCredentialError`` so the operator can
    tell apart "user didn't forward their cred" from "operator never
    configured the SA fallback either". The fix in each case is
    different: the former is a routing/NVA problem, the latter is a
    deployment problem (set ``API_USERNAME`` / ``API_PWD`` in .env, or
    flip ``ISE_REQUIRE_PER_USER_CREDENTIAL=true`` to disable fallback
    entirely).
    """


__all__ = [
    "MissingIseCredentialError",
    "MissingServiceAccountError",
]
