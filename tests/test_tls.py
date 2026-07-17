# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import ssl
from unittest.mock import patch

import pytest


def _reset_flag():
    import clients.tls as tls_mod
    tls_mod._TLS_POSTURE_LOGGED = False


def _fake_settings(**over):
    """A stand-in settings object with cert/verify attributes."""
    from types import SimpleNamespace
    base = dict(
        ise_verify_server_cert=True,
        ise_verify_hostname=True,
        ise_ca_bundle=None,
        client_cert_configured=False,
        ise_client_cert=None,
        ise_client_key=None,
        ise_client_key_password=None,
    )
    base.update(over)
    return SimpleNamespace(**base)


def _write_self_signed(tmp_path, encrypt_password=None):
    """Generate a throwaway self-signed cert + key using stdlib+cryptography.

    cryptography is a transitive dependency already present in the venv
    (via httpx/pydantic stack); import lazily so the test skips cleanly
    if it is ever absent.
    """
    crypto = pytest.importorskip("cryptography")
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2020, 1, 1))
        .not_valid_after(datetime.datetime(2100, 1, 1))
        # Mark as a CA so it is counted by SSLContext.get_ca_certs()
        # (only CA-flagged certs are reported); lets test_ca_bundle_loaded
        # assert the bundle is the sole trust anchor.
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True
        )
        .sign(key, hashes.SHA256())
    )
    cert_path = tmp_path / "c.pem"
    key_path = tmp_path / "k.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    enc = (
        serialization.BestAvailableEncryption(encrypt_password.encode())
        if encrypt_password
        else serialization.NoEncryption()
    )
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            enc,
        )
    )
    return str(cert_path), str(key_path)


class TestBuildSslContext:
    def setup_method(self):
        _reset_flag()

    def test_verify_on_requires_cert_and_hostname(self):
        with patch("clients.tls.settings", _fake_settings()):
            from clients.tls import build_ssl_context
            ctx = build_ssl_context()
        assert ctx.verify_mode == ssl.CERT_REQUIRED
        assert ctx.check_hostname is True
        assert ctx.minimum_version == ssl.TLSVersion.TLSv1_2

    def test_verify_on_hostname_off(self):
        with patch("clients.tls.settings",
                   _fake_settings(ise_verify_hostname=False)):
            from clients.tls import build_ssl_context
            ctx = build_ssl_context()
        assert ctx.verify_mode == ssl.CERT_REQUIRED
        assert ctx.check_hostname is False

    def test_verify_off_disables_everything(self):
        with patch("clients.tls.settings",
                   _fake_settings(ise_verify_server_cert=False,
                                  ise_verify_hostname=False)):
            from clients.tls import build_ssl_context
            ctx = build_ssl_context()
        assert ctx.check_hostname is False
        assert ctx.verify_mode == ssl.CERT_NONE

    def test_ca_bundle_loaded(self, tmp_path):
        cert, _ = _write_self_signed(tmp_path)
        with patch("clients.tls.settings",
                   _fake_settings(ise_ca_bundle=cert)):
            from clients.tls import build_ssl_context
            ctx = build_ssl_context()
        # A custom bundle REPLACES the system store, so exactly the one
        # cert in the bundle is the trust anchor (proves it is not the
        # system store).
        assert len(ctx.get_ca_certs()) == 1

    def test_client_cert_loaded(self, tmp_path):
        cert, key = _write_self_signed(tmp_path)
        with patch("clients.tls.settings",
                   _fake_settings(client_cert_configured=True,
                                  ise_client_cert=cert, ise_client_key=key)):
            from clients.tls import build_ssl_context
            ctx = build_ssl_context()  # must not raise
        assert isinstance(ctx, ssl.SSLContext)

    def test_encrypted_client_key_loaded_with_password(self, tmp_path):
        from types import SimpleNamespace
        cert, key = _write_self_signed(tmp_path, encrypt_password="s3cret")
        pwd = SimpleNamespace(get_secret_value=lambda: "s3cret")
        with patch("clients.tls.settings",
                   _fake_settings(client_cert_configured=True,
                                  ise_client_cert=cert, ise_client_key=key,
                                  ise_client_key_password=pwd)):
            from clients.tls import build_ssl_context
            ctx = build_ssl_context()
        assert isinstance(ctx, ssl.SSLContext)

    def test_posture_logged_once(self):
        import clients.tls as tls_mod
        with patch("clients.tls.settings", _fake_settings()):
            from clients.tls import build_ssl_context
            assert tls_mod._TLS_POSTURE_LOGGED is False
            build_ssl_context()
            assert tls_mod._TLS_POSTURE_LOGGED is True
            build_ssl_context()
            assert tls_mod._TLS_POSTURE_LOGGED is True
