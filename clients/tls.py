# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""
Shared SSL context for ISE clients.

SECURITY POSTURE
----------------
Peer certificate verification is ON by default (``CERT_REQUIRED``).
Operators may:

* disable verification for testing via ``ISE_VERIFY_SERVER_CERT=false``
  (channel stays TLS 1.2+ encrypted but the server is not authenticated),
* verify the chain but skip hostname matching via
  ``ISE_VERIFY_HOSTNAME=false`` (for bare-IP connections whose cert has
  no matching IP SAN),
* trust an internal-CA / self-signed cert via ``ISE_CA_BUNDLE``.

When a client certificate is configured (``ISE_CLIENT_CERT`` +
``ISE_CLIENT_KEY``) it is loaded here, so every ISE client presents it
(mTLS) automatically.

This file is the single place where the TLS posture is implemented.
"""

import ssl

from clients.settings import settings
from logger import logger

_TLS_POSTURE_LOGGED: bool = False


def build_ssl_context() -> ssl.SSLContext:
    """Build the shared SSL context for ISE clients from settings.

    TLS 1.2 is pinned as the minimum. Peer verification and hostname
    checking follow ``ISE_VERIFY_SERVER_CERT`` / ``ISE_VERIFY_HOSTNAME``.
    A client cert chain is loaded when configured. Posture is logged
    once per process for auditability.

    Note: ``check_hostname`` must be set to ``False`` *before*
    ``verify_mode = CERT_NONE`` to avoid a ``ValueError`` from the stdlib
    ssl module.
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    if settings.ise_verify_server_cert:
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = settings.ise_verify_hostname
        if settings.ise_ca_bundle:
            ctx.load_verify_locations(cafile=settings.ise_ca_bundle)
        else:
            ctx.load_default_certs()
    else:
        # Order matters: hostname off before CERT_NONE.
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    if settings.client_cert_configured:
        password = (
            settings.ise_client_key_password.get_secret_value()
            if settings.ise_client_key_password
            else None
        )
        ctx.load_cert_chain(
            certfile=settings.ise_client_cert,
            keyfile=settings.ise_client_key,
            password=password,
        )

    global _TLS_POSTURE_LOGGED
    if not _TLS_POSTURE_LOGGED:
        logger.info(
            "ISE TLS posture",
            verify_server_cert=settings.ise_verify_server_cert,
            check_hostname=(
                settings.ise_verify_hostname
                if settings.ise_verify_server_cert
                else False
            ),
            ca_bundle=bool(settings.ise_ca_bundle),
            client_cert=settings.client_cert_configured,
            min_tls="1.2",
        )
        _TLS_POSTURE_LOGGED = True

    return ctx
