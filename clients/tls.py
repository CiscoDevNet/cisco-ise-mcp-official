# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""
Shared SSL context for ISE clients.

SECURITY POSTURE (beta)
-----------------------
Per accepted residual-risk decision (recorded with the tech lead),
peer certificate verification is intentionally DISABLED. The channel is
encrypted with TLS 1.2 or higher, but does NOT authenticate the ISE
server. An active on-path attacker can MITM and capture the ISE
service-account credential.

This file is the single place where that decision is implemented; do
NOT change it without revisiting the residual-risk acceptance.

TODO(<owner>, <date>): revisit this posture at GA. Replace ``CERT_NONE``
with ``CERT_REQUIRED`` and ``check_hostname=True``, optionally loading a
custom CA bundle via a settings field (e.g. ``ISE_CA_BUNDLE``).
"""

import ssl

from logger import logger

_TLS_POSTURE_LOGGED: bool = False


def build_ssl_context() -> ssl.SSLContext:
    """Build the shared SSL context for ISE clients.

    Pins TLS 1.2 as the minimum protocol version (prevents legacy
    downgrade) but explicitly disables peer verification. Logs the
    posture once per process so operators can audit it from logs.

    Note: ``check_hostname`` must be set to ``False`` *before*
    ``verify_mode = CERT_NONE`` to avoid a ``ValueError`` from the
    stdlib ssl module.
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    global _TLS_POSTURE_LOGGED
    if not _TLS_POSTURE_LOGGED:
        logger.info(
            "ISE TLS posture: peer verification disabled, hostname check off, "
            "TLS 1.2+ enforced (accepted residual risk per tech-lead decision)"
        )
        _TLS_POSTURE_LOGGED = True

    return ctx
