# ISE Certificate-Based Auth + Server-Cert Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add client-certificate-based authentication to the ISE API clients and enable server-certificate verification by default (with an opt-out), both driven by new settings.

**Architecture:** All HTTP clients funnel their SSL context through `clients/tls.py::build_ssl_context()`. Loading the client cert there gives mTLS to every client for free. Server verification becomes config-driven in the same function. Auth-path selection (send an `Authorization` header or not) is extended in `client_factory.py` and `mnt_client.py`: when a client cert is configured, no `Authorization` header is sent (cert = standalone auth), ranked above the service-account fallback and below the per-user header.

**Tech Stack:** Python 3.12, pydantic 2.12 / pydantic-settings, httpx 0.28.1, stdlib `ssl`, pytest + pytest-asyncio, `uv`.

## Global Constraints

- Python `==3.12.*` — use only stdlib/deps already in `pyproject.toml`; add no new dependencies.
- Run all Python/pytest via `uv run` (never bare `python`/`pytest`).
- Secrets held as `pydantic.SecretStr`; never log secret values.
- Copyright header on every new `.py` file: `# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved`
- Config source of truth is `clients/settings.py`; clients read `settings`, never `os.getenv` directly.
- `check_hostname=True` with `verify_mode=CERT_NONE` raises `ValueError` in stdlib `ssl` — hostname check must be `False` whenever verification is off.
- Fail loud at **startup** (settings load) for bad config, not on first request.

---

### Task 1: New settings fields + cross-field validation

**Files:**
- Modify: `clients/settings.py`
- Test: `tests/test_settings_cert_auth.py` (create)

**Interfaces:**
- Produces on `settings` (module singleton `clients.settings.settings`):
  - `ise_client_cert: Optional[str]` (env `ISE_CLIENT_CERT`)
  - `ise_client_key: Optional[str]` (env `ISE_CLIENT_KEY`)
  - `ise_client_key_password: Optional[SecretStr]` (env `ISE_CLIENT_KEY_PASSWORD`)
  - `ise_verify_server_cert: bool` = `True` (env `ISE_VERIFY_SERVER_CERT`)
  - `ise_verify_hostname: bool` = `True` (env `ISE_VERIFY_HOSTNAME`)
  - `ise_ca_bundle: Optional[str]` (env `ISE_CA_BUNDLE`)
  - `client_cert_configured` — property, `True` iff both `ise_client_cert` and `ise_client_key` are set.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_settings_cert_auth.py`:

```python
# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from clients.settings import ISESettings


def _base(**over):
    """Minimal valid kwargs for ISESettings; override per test.

    Fields use ``validation_alias`` and the model does NOT set
    ``populate_by_name``, so kwargs MUST be keyed by the env-var alias
    (e.g. ``ISE_IP``), not the Python field name.
    """
    kwargs = {"ISE_IP": "10.0.0.1"}
    kwargs.update(over)
    return kwargs


def _cert_files(tmp_path):
    cert = tmp_path / "client.pem"
    key = tmp_path / "client.key"
    cert.write_text("cert")
    key.write_text("key")
    return str(cert), str(key)


class TestCertAuthSettings:
    def test_defaults_verify_on_no_cert(self):
        s = ISESettings(**_base())
        assert s.ise_verify_server_cert is True
        assert s.ise_verify_hostname is True
        assert s.ise_client_cert is None
        assert s.client_cert_configured is False

    def test_cert_and_key_together_ok(self, tmp_path):
        cert, key = _cert_files(tmp_path)
        s = ISESettings(**_base(ISE_CLIENT_CERT=cert, ISE_CLIENT_KEY=key))
        assert s.client_cert_configured is True

    def test_cert_without_key_raises(self, tmp_path):
        cert, _ = _cert_files(tmp_path)
        with pytest.raises(ValidationError, match="ISE_CLIENT_KEY"):
            ISESettings(**_base(ISE_CLIENT_CERT=cert))

    def test_key_without_cert_raises(self, tmp_path):
        _, key = _cert_files(tmp_path)
        with pytest.raises(ValidationError, match="ISE_CLIENT_CERT"):
            ISESettings(**_base(ISE_CLIENT_KEY=key))

    def test_missing_cert_file_raises(self, tmp_path):
        _, key = _cert_files(tmp_path)
        with pytest.raises(ValidationError, match="does not exist"):
            ISESettings(**_base(
                ISE_CLIENT_CERT=str(tmp_path / "nope.pem"), ISE_CLIENT_KEY=key
            ))

    def test_missing_ca_bundle_raises(self):
        with pytest.raises(ValidationError, match="does not exist"):
            ISESettings(**_base(ISE_CA_BUNDLE="/no/such/ca.pem"))

    def test_hostname_true_with_verify_off_raises(self):
        with pytest.raises(ValidationError, match="ISE_VERIFY_HOSTNAME"):
            ISESettings(**_base(
                ISE_VERIFY_SERVER_CERT=False, ISE_VERIFY_HOSTNAME=True
            ))

    def test_hostname_false_with_verify_off_ok(self):
        s = ISESettings(**_base(
            ISE_VERIFY_SERVER_CERT=False, ISE_VERIFY_HOSTNAME=False
        ))
        assert s.ise_verify_server_cert is False
        assert s.ise_verify_hostname is False

    def test_empty_env_strings_treated_as_absent(self):
        s = ISESettings(**_base(ISE_CLIENT_CERT="", ISE_CLIENT_KEY=""))
        assert s.ise_client_cert is None
        assert s.client_cert_configured is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_settings_cert_auth.py -v`
Expected: FAIL (fields/validators/property not defined; `TypeError`/`AttributeError`).

- [ ] **Step 3: Add fields, validators, and property to `clients/settings.py`**

Add these imports near the top (merge with existing pydantic imports):

```python
import os
from pydantic import model_validator
```

Add the new fields inside `ISESettings`, after the `log_cache_dir_prefix` field:

```python
    # --- Certificate-based auth + server verification -----------------
    # Client certificate PEM path. When both cert and key are set, ISE
    # clients present this cert (mTLS) and send NO Authorization header:
    # ISE authenticates the API user from the cert (standalone auth).
    ise_client_cert: Optional[str] = Field(
        default=None, validation_alias="ISE_CLIENT_CERT"
    )
    ise_client_key: Optional[str] = Field(
        default=None, validation_alias="ISE_CLIENT_KEY"
    )
    # Passphrase for an encrypted private key. SecretStr so it never
    # leaks via repr/tracebacks. None => key assumed unencrypted.
    ise_client_key_password: Optional[SecretStr] = Field(
        default=None, validation_alias="ISE_CLIENT_KEY_PASSWORD"
    )
    # Peer certificate verification. Defaults ON (breaking change vs the
    # old always-disabled posture); set false to disable for testing.
    ise_verify_server_cert: bool = Field(
        default=True, validation_alias="ISE_VERIFY_SERVER_CERT"
    )
    # Hostname/SAN matching, independent of chain verification so an
    # operator can verify the chain but skip hostname matching when
    # connecting to a bare IP whose cert has no IP SAN. Must be False
    # whenever ise_verify_server_cert is False (stdlib ssl forbids
    # check_hostname=True with CERT_NONE).
    ise_verify_hostname: bool = Field(
        default=True, validation_alias="ISE_VERIFY_HOSTNAME"
    )
    # Optional CA/self-signed cert to trust (load_verify_locations).
    # When unset and verification is on, the system trust store is used.
    ise_ca_bundle: Optional[str] = Field(
        default=None, validation_alias="ISE_CA_BUNDLE"
    )
```

Extend the existing `_empty_str_to_default` validator's field list to include the new string fields:

```python
    @field_validator(
        "api_port", "api_username", "api_pwd",
        "ise_admin_session_cookie", "log_cache_ttl_s", "log_cache_dir_prefix",
        "ise_client_cert", "ise_client_key", "ise_client_key_password",
        "ise_ca_bundle",
        mode="before",
    )
    @classmethod
    def _empty_str_to_default(cls, v):
        if isinstance(v, str) and v.strip() == "":
            raise PydanticUseDefault
        return v
```

Add the property and the after-validator (place after the field declarations):

```python
    @property
    def client_cert_configured(self) -> bool:
        """True iff both client cert and key paths are set."""
        return bool(self.ise_client_cert and self.ise_client_key)

    @model_validator(mode="after")
    def _validate_cert_and_tls_config(self) -> "ISESettings":
        # Cert and key must be supplied together.
        if bool(self.ise_client_cert) != bool(self.ise_client_key):
            missing = "ISE_CLIENT_KEY" if self.ise_client_cert else "ISE_CLIENT_CERT"
            raise ValueError(
                f"{missing} must be set when the other is set: client "
                "cert and key are required together."
            )
        # Hostname check cannot be on while verification is off.
        if self.ise_verify_hostname and not self.ise_verify_server_cert:
            raise ValueError(
                "ISE_VERIFY_HOSTNAME=true requires ISE_VERIFY_SERVER_CERT=true "
                "(stdlib ssl forbids hostname checking without chain "
                "verification). Set ISE_VERIFY_HOSTNAME=false to connect to "
                "a bare IP without an IP SAN."
            )
        # Referenced files must exist and be readable, checked at startup.
        for label, path in (
            ("ISE_CLIENT_CERT", self.ise_client_cert),
            ("ISE_CLIENT_KEY", self.ise_client_key),
            ("ISE_CA_BUNDLE", self.ise_ca_bundle),
        ):
            if path and not os.path.isfile(path):
                raise ValueError(
                    f"{label} path does not exist or is not a file: {path}"
                )
        return self
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_settings_cert_auth.py -v`
Expected: PASS (9 tests).

- [ ] **Step 5: Run the full suite to check for regressions**

Run: `uv run pytest -q`
Expected: PASS (existing settings/tls/factory/mnt tests still green).

- [ ] **Step 6: Commit**

```bash
git add clients/settings.py tests/test_settings_cert_auth.py
git commit -m "feat(settings): add client-cert + server-verify config fields"
```

---

### Task 2: Config-driven TLS context

**Files:**
- Modify: `clients/tls.py`
- Test: `tests/test_tls.py` (extend)

**Interfaces:**
- Consumes: `clients.settings.settings` fields from Task 1 (`ise_verify_server_cert`, `ise_verify_hostname`, `ise_ca_bundle`, `client_cert_configured`, `ise_client_cert`, `ise_client_key`, `ise_client_key_password`).
- Produces: `build_ssl_context() -> ssl.SSLContext` — same signature; now reads settings. Verification ON → `CERT_REQUIRED` + `check_hostname = ise_verify_hostname`; OFF → `check_hostname=False`, `CERT_NONE`. Loads client cert chain when `client_cert_configured`.

- [ ] **Step 1: Write the failing tests**

Replace the body of `tests/test_tls.py` with this (keeps the reset-flag setup, adds settings patching and new cases). Requires a helper that generates a real self-signed cert/key so `load_cert_chain` exercises real code:

```python
# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

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
        # A loaded CA appears in the context's CA list.
        assert len(ctx.get_ca_certs()) >= 1

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_tls.py -v`
Expected: FAIL — `clients.tls` has no `settings` attribute to patch, and current code always sets `CERT_NONE`.

- [ ] **Step 3: Rewrite `clients/tls.py`**

Replace the entire file with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_tls.py -v`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add clients/tls.py tests/test_tls.py
git commit -m "feat(tls): config-driven verification + client-cert loading"
```

---

### Task 3: OpenAPI factory cert mode (no Authorization header, cached)

**Files:**
- Modify: `clients/client_factory.py`
- Test: `tests/test_client_factory.py` (extend)

**Interfaces:**
- Consumes: `settings.client_cert_configured` (Task 1), `build_ssl_context()` (Task 2), existing `settings.require_per_user_credential`, `get_per_user_credential()`.
- Produces: when cert mode is active, `get_client(name)` returns a client built via `_create_cert_mode_client(client_name)` that carries NO `Authorization` header, cached per `ClientName` in `self._clients` (same cache as the SA path). Per-user header still wins; `require_per_user_credential` still raises.

**Design note:** the autogenerated `AuthenticatedClient` always writes `Authorization: <prefix> <token>` when it lazily builds its own httpx client (`get_async_httpx_client`/`get_httpx_client`). To send NO header, build an `httpx.AsyncClient` ourselves and attach it via `set_async_httpx_client()`, and an `httpx.Client` via `set_httpx_client()`, which bypasses the header-writing branch entirely. The `token`/`prefix` we pass are placeholders that never reach the wire.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_client_factory.py`. The existing `_FakeClient` lacks `set_async_httpx_client`/`set_httpx_client`; add a second fake that records them:

```python
class _CertFakeClient:
    """Fake AuthenticatedClient that records injected httpx clients."""

    def __init__(self, base_url, prefix, token, verify_ssl, timeout, follow_redirects):
        self.base_url = base_url
        self.prefix = prefix
        self.token = token
        self.injected_async = None
        self.injected_sync = None

    def set_async_httpx_client(self, client):
        self.injected_async = client
        return self

    def set_httpx_client(self, client):
        self.injected_sync = client
        return self


class TestClientFactoryCertMode:
    def _make_factory(self):
        from clients.client_factory import ClientFactory, ClientName
        factory = ClientFactory()
        for name in ClientName:
            factory.register_client_class(name, _CertFakeClient, "/fake")
        return factory

    def _cert_settings(self, mock_settings):
        mock_settings.ise_ip = "10.0.0.1"
        mock_settings.api_port = 443
        mock_settings.require_per_user_credential = False
        mock_settings.client_cert_configured = True
        mock_settings.connect_timeout_s = 5.0
        mock_settings.read_timeout_s = 30.0
        mock_settings.write_timeout_s = 10.0
        mock_settings.pool_timeout_s = 5.0

    def test_cert_mode_injects_httpx_clients_no_auth_header(self):
        from clients.client_factory import ClientName
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        factory = self._make_factory()
        token = set_per_user_credential(None)
        try:
            with patch("clients.client_factory.settings") as mock_settings:
                self._cert_settings(mock_settings)
                with patch("clients.client_factory.build_ssl_context", return_value=None):
                    client = factory.get_client(ClientName.ENDPOINTS)
            # An httpx client was injected (bypassing the auth-header branch).
            assert client.injected_async is not None
            assert client.injected_sync is not None
        finally:
            reset_per_user_credential(token)

    def test_cert_mode_client_cached(self):
        from clients.client_factory import ClientName
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        factory = self._make_factory()
        token = set_per_user_credential(None)
        try:
            with patch("clients.client_factory.settings") as mock_settings:
                self._cert_settings(mock_settings)
                with patch("clients.client_factory.build_ssl_context", return_value=None):
                    c1 = factory.get_client(ClientName.ENDPOINTS)
                    c2 = factory.get_client(ClientName.ENDPOINTS)
            assert c1 is c2
        finally:
            reset_per_user_credential(token)

    def test_per_user_header_wins_over_cert_mode(self):
        from clients.client_factory import ClientName
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        factory = self._make_factory()
        token = set_per_user_credential("Basic dXNlcjpwYXNz")
        try:
            with patch("clients.client_factory.settings") as mock_settings:
                self._cert_settings(mock_settings)
                with patch("clients.client_factory.build_ssl_context", return_value=None):
                    client = factory.get_client(ClientName.ENDPOINTS)
            # Per-user path sets prefix/token and does NOT inject an httpx client.
            assert client.prefix == "Basic"
            assert client.token == "dXNlcjpwYXNz"
            assert client.injected_async is None
        finally:
            reset_per_user_credential(token)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_client_factory.py::TestClientFactoryCertMode -v`
Expected: FAIL — `client_cert_configured` branch not implemented; `injected_async` stays `None`.

- [ ] **Step 3: Implement cert mode in `clients/client_factory.py`**

In `get_client`, insert the cert-mode branch AFTER the per-user check and BEFORE the `require_per_user_credential` check, and route it through the same `self._clients` cache as the SA path:

```python
        per_user_credential = get_per_user_credential()
        if per_user_credential:
            return self._create_client(
                client_name, authorization_value=per_user_credential
            )
        # Cert mode: client cert configured -> standalone auth, no
        # Authorization header. Cached per ClientName like the SA path;
        # the cert is a single process-wide config, so there is no
        # per-user token to leak and no unbounded cache growth.
        if settings.client_cert_configured:
            if client_name not in self._clients:
                self._clients[client_name] = self._create_cert_mode_client(
                    client_name
                )
            return self._clients[client_name]
        if settings.require_per_user_credential:
            raise MissingIseCredentialError(
                "ISE_REQUIRE_PER_USER_CREDENTIAL=true but no "
                f"'{settings.credential_header_name}' header was "
                "forwarded with this request."
            )
        if client_name not in self._clients:
            self._clients[client_name] = self._create_client(client_name)
        return self._clients[client_name]
```

Add the new method (place after `_create_client`):

```python
    def _create_cert_mode_client(self, client_name: ClientName) -> object:
        """Build a client that authenticates via client cert only.

        The autogenerated AuthenticatedClient always emits an
        ``Authorization`` header when it lazily builds its own httpx
        client. To send NO header (cert = standalone auth), we build the
        httpx clients ourselves and inject them via
        ``set_async_httpx_client`` / ``set_httpx_client``, which bypass
        that header-writing branch. ``token``/``prefix`` are placeholders
        that never reach the wire. The shared TLS context already carries
        the client cert (see clients/tls.py).
        """
        if client_name not in self._client_registry:
            raise ValueError(f"Unknown client name: {client_name}")
        entry = self._client_registry[client_name]

        base_url = (
            f"{ISE_PROTOCOL}://{settings.ise_ip}:{settings.api_port}{entry.base_path}"
        )
        timeout = httpx.Timeout(
            connect=settings.connect_timeout_s,
            read=settings.read_timeout_s,
            write=settings.write_timeout_s,
            pool=settings.pool_timeout_s,
        )
        ssl_context = build_ssl_context()

        logger.info(
            "Creating client-certificate ISE client (no Authorization header)",
            client_name=str(client_name),
            base_url=base_url,
        )

        client = entry.client_class(
            base_url=base_url,
            prefix="",
            token="",
            verify_ssl=ssl_context,
            timeout=timeout,
            follow_redirects=False,
        )
        async_httpx = httpx.AsyncClient(
            base_url=base_url,
            verify=ssl_context,
            timeout=timeout,
            follow_redirects=False,
        )
        sync_httpx = httpx.Client(
            base_url=base_url,
            verify=ssl_context,
            timeout=timeout,
            follow_redirects=False,
        )
        client.set_async_httpx_client(async_httpx)
        client.set_httpx_client(sync_httpx)
        return client
```

- [ ] **Step 4: Run the cert-mode tests to verify they pass**

Run: `uv run pytest tests/test_client_factory.py -v`
Expected: PASS (existing 8 tests + 3 new cert-mode tests).

Note: the existing `_FakeClient` in the SA/per-user tests is untouched and never reaches `_create_cert_mode_client` (those tests set no `client_cert_configured`, so the MagicMock attribute is truthy by default — guard by explicitly setting `mock_settings.client_cert_configured = False` in the existing tests if they now fail). If any pre-existing test fails because MagicMock makes `client_cert_configured` truthy, add `mock_settings.client_cert_configured = False` to that test's settings block.

- [ ] **Step 5: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS. If a pre-existing `test_client_factory.py` test fails on the new branch, add `mock_settings.client_cert_configured = False` to its settings block (MagicMock attributes default to truthy).

- [ ] **Step 6: Commit**

```bash
git add clients/client_factory.py tests/test_client_factory.py
git commit -m "feat(factory): client-cert auth mode for OpenAPI clients"
```

---

### Task 4: MnT cert mode (no Authorization header)

**Files:**
- Modify: `clients/mnt_client.py`
- Test: `tests/test_mnt_client.py` (extend)

**Interfaces:**
- Consumes: `settings.client_cert_configured` (Task 1), existing `_NoOpAuth`, `get_per_user_credential()`.
- Produces: `_resolve_per_call_auth()` returns `({"auth": _NoOpAuth()}, "client_certificate")` when cert mode is active — no `Authorization` header, and `_NoOpAuth` neutralises any client-level BasicAuth. Precedence: per-user header first, then cert mode, then `require_per_user_credential` raise, then SA fallback.

- [ ] **Step 1: Write the failing tests**

Add to `TestMNTClientResolveAuth` in `tests/test_mnt_client.py`:

```python
    def test_client_cert_mode_no_auth_header(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.client_cert_configured = True
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                kwargs, label = client._resolve_per_call_auth()
                assert label == "client_certificate"
                assert "headers" not in kwargs or "Authorization" not in kwargs.get("headers", {})
                # A no-op auth flow neutralises client-level BasicAuth.
                assert isinstance(kwargs["auth"], mod._NoOpAuth)
            finally:
                reset_per_user_credential(token)

    def test_per_user_wins_over_client_cert(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.client_cert_configured = True
            token = set_per_user_credential("Basic dXNlcjpwYXNz")
            try:
                client = mod.MNTClient()
                kwargs, label = client._resolve_per_call_auth()
                assert label == "per_user_credential"
                assert kwargs["headers"]["Authorization"] == "Basic dXNlcjpwYXNz"
            finally:
                reset_per_user_credential(token)
```

Also guard the existing `TestMNTClientResolveAuth` tests that don't set `client_cert_configured`: add `mock_settings.client_cert_configured = False` to the settings block in `test_service_account_fallback`, `test_require_per_user_raises_when_absent`, and `test_no_sa_creds_raises` (MagicMock attributes default truthy, which would otherwise divert them into cert mode).

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_mnt_client.py::TestMNTClientResolveAuth -v`
Expected: FAIL — no `client_certificate` branch; new tests error / mislabel.

- [ ] **Step 3: Implement cert mode in `_resolve_per_call_auth`**

In `clients/mnt_client.py`, insert the cert-mode branch after the per-user check and before the `require_per_user_credential` check:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_mnt_client.py -v`
Expected: PASS (existing tests + 2 new).

- [ ] **Step 5: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add clients/mnt_client.py tests/test_mnt_client.py
git commit -m "feat(mnt): client-cert auth mode (no Authorization header)"
```

---

### Task 5: Documentation (.env.example + README)

**Files:**
- Modify: `.env.example`
- Modify: `README.md`

**Interfaces:** none (docs only). Reflects the env vars from Task 1 and posture from Task 2.

- [ ] **Step 1: Update `.env.example`**

Replace the file contents with:

```
# ISE API Configuration
# Note: These environment variables are used by both ERS API and MNT API clients
ISE_IP= # The IP address or hostname of your ISE server (used for API base URL)

# --- Authentication (choose ONE approach) ---------------------------------
# 1) Service-account Basic auth (fallback when no per-user header is sent):
API_USERNAME= # Admin username for API authentication
API_PWD=      # Admin password for API authentication

# 2) Client-certificate auth (standalone: when set, NO Authorization header
#    is sent and ISE authenticates the API user from the cert). Cert and key
#    must be provided together. Supply the passphrase only if the key is
#    encrypted.
ISE_CLIENT_CERT=          # Path to client certificate PEM
ISE_CLIENT_KEY=           # Path to client private-key PEM
ISE_CLIENT_KEY_PASSWORD=  # Passphrase for an encrypted key (leave blank if none)

# --- Server certificate verification --------------------------------------
# Verification is ON by default. This is a change from earlier builds where
# it was disabled. If you connect by IP to a self-signed / internal-CA ISE,
# either point ISE_CA_BUNDLE at the trusted cert, disable hostname matching,
# or (testing only) disable verification entirely.
ISE_VERIFY_SERVER_CERT=true  # false disables verification (testing only)
ISE_VERIFY_HOSTNAME=true     # false verifies the chain but skips hostname/SAN
                             # matching (must be false if VERIFY_SERVER_CERT=false)
ISE_CA_BUNDLE=               # Path to a CA/self-signed cert to trust

# Server Settings
HOST=0.0.0.0
PORT=5000
```

- [ ] **Step 2: Add a "Certificate-based authentication" section to `README.md`**

Read `README.md` first to find the existing authentication/configuration section, then add this subsection near it (adjust heading level to match surrounding headings):

````markdown
### Certificate-based authentication

Instead of a username/password, the server can authenticate to ISE with a
client certificate. When `ISE_CLIENT_CERT` and `ISE_CLIENT_KEY` are set, the
certificate is presented on the TLS connection and **no `Authorization`
header is sent** — ISE identifies the API user from the certificate. This is
the programmatic equivalent of:

```bash
curl -X GET https://<ISE_IP>/ers/config/op/systemconfig/iseversion \
  --cert client.pem --key client.key -H "Accept: application/json"
```

Configuration (`.env`):

| Variable | Purpose |
|---|---|
| `ISE_CLIENT_CERT` | Path to the client certificate PEM |
| `ISE_CLIENT_KEY` | Path to the client private-key PEM |
| `ISE_CLIENT_KEY_PASSWORD` | Passphrase, only if the key is encrypted |

Cert and key must be supplied together. A forwarded per-user
`X-ISE-Authorization` header still takes precedence over certificate auth.

### Server certificate verification

Server-certificate verification is **enabled by default**. Earlier builds
disabled it; upgrading enforces it, which may break connections to ISE nodes
presenting self-signed or internal-CA certificates until you configure trust.

| Variable | Default | Purpose |
|---|---|---|
| `ISE_VERIFY_SERVER_CERT` | `true` | Set `false` to disable verification (testing only) |
| `ISE_VERIFY_HOSTNAME` | `true` | Set `false` to verify the chain but skip hostname/SAN matching (useful for bare-IP connections). Must be `false` when `ISE_VERIFY_SERVER_CERT=false` |
| `ISE_CA_BUNDLE` | _(unset)_ | Path to a CA / self-signed certificate to trust; when unset the system trust store is used |
````

- [ ] **Step 3: Commit**

```bash
git add .env.example README.md
git commit -m "docs: document client-cert auth and server verification config"
```

---

## Self-Review

**Spec coverage:**
- Section 1 (Settings — six fields, cross-field validation, startup file checks, `client_cert_configured`) → Task 1. ✓
- Section 2 (config-driven TLS, CA bundle, hostname toggle, client-cert load, once-per-process log) → Task 2. ✓
- Section 3 (cert = standalone; precedence; OpenAPI injects httpx client + cached; MnT `_NoOpAuth`; web session out of scope) → Tasks 3 & 4. ✓ Web session correctly untouched — it still picks up the cert via the shared TLS context.
- Section 4 (docs, tests, error handling) → Tests fold into Tasks 1–4; docs in Task 5; startup error handling in Task 1's validator. ✓

**Placeholder scan:** No TBD/TODO; all steps carry real code and exact `uv run pytest` commands with expected outcomes.

**Type consistency:** `client_cert_configured` (property), `_create_cert_mode_client(client_name)`, `_resolve_per_call_auth()` returning label `"client_certificate"`, and `build_ssl_context()` signature are used consistently across tasks. Env var names match Task 1 exactly in Tasks 2–5.

**MagicMock caveat** (Tasks 3 & 4): pre-existing tests patch `settings` with a `MagicMock`, whose `client_cert_configured` attribute defaults truthy and would wrongly divert into cert mode. Both tasks explicitly instruct adding `client_cert_configured = False` to the affected existing tests. This is called out rather than left to discovery.
