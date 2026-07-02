# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import ssl
import importlib

import pytest


class TestBuildSslContext:
    def setup_method(self):
        # Reset the module-level flag before each test so logging fires fresh
        import clients.tls as tls_mod
        tls_mod._TLS_POSTURE_LOGGED = False

    def test_returns_ssl_context(self):
        from clients.tls import build_ssl_context
        ctx = build_ssl_context()
        assert isinstance(ctx, ssl.SSLContext)

    def test_peer_verification_disabled(self):
        from clients.tls import build_ssl_context
        ctx = build_ssl_context()
        assert ctx.verify_mode == ssl.CERT_NONE

    def test_hostname_check_disabled(self):
        from clients.tls import build_ssl_context
        ctx = build_ssl_context()
        assert ctx.check_hostname is False

    def test_minimum_tls_version(self):
        from clients.tls import build_ssl_context
        ctx = build_ssl_context()
        assert ctx.minimum_version == ssl.TLSVersion.TLSv1_2

    def test_posture_logged_once(self):
        import clients.tls as tls_mod
        from clients.tls import build_ssl_context
        assert tls_mod._TLS_POSTURE_LOGGED is False
        build_ssl_context()
        assert tls_mod._TLS_POSTURE_LOGGED is True
        # Second call must not re-log (flag stays True)
        build_ssl_context()
        assert tls_mod._TLS_POSTURE_LOGGED is True
