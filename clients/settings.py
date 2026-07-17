# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""
Single source of truth for ISE client configuration.

Exposes one module-level ``settings`` singleton. All ISE HTTP clients
(``client_factory``, ``mnt_client``, ``ers_client``) read from it instead of
calling ``os.getenv`` directly. The password is held as ``SecretStr`` so it
is never exposed via ``repr()``, tracebacks, or accidental ``vars()`` dumps.
"""

import os
from typing import Optional

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_core import PydanticUseDefault
from pydantic_settings import BaseSettings, SettingsConfigDict


class ISESettings(BaseSettings):
    """Strongly-typed ISE connection settings loaded from env / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ISE PAN host/IP. Required -- no default; unset/empty fails at startup.
    ise_ip: str = Field(
        min_length=1,
        validation_alias="ISE_IP",
    )
    api_port: int = Field(
        default=443, ge=1, le=65535, validation_alias="API_PORT"
    )
    # Service-account creds: the FALLBACK auth path used when a request
    # carries no per-user `X-ISE-Authorization` header. Optional so a
    # header-only deployment can leave them empty; code paths that need
    # them raise `MissingServiceAccountError` if unset.
    api_username: Optional[str] = Field(
        default=None, max_length=64, validation_alias="API_USERNAME"
    )
    api_pwd: Optional[SecretStr] = Field(
        default=None, validation_alias="API_PWD"
    )

    # `.env` files often ship a slot as `KEY=` (empty string, not
    # absent). Treat empty as absent so the field's default applies.
    # `ise_ip` is excluded on purpose -- it's required, so empty must
    # fail `min_length=1` rather than be silently defaulted.
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

    connect_timeout_s: float = Field(default=5.0, gt=0)
    read_timeout_s: float = Field(default=30.0, gt=0)
    write_timeout_s: float = Field(default=10.0, gt=0)
    pool_timeout_s: float = Field(default=5.0, gt=0)

    # Inbound MCP header carrying the end-user's pre-built
    # `Basic <b64(user:pass)>` credential.
    credential_header_name: str = Field(
        default="X-ISE-Authorization",
        min_length=1,
        max_length=64,
        validation_alias="ISE_CREDENTIAL_HEADER_NAME",
    )
    # When True, reject requests missing the credential header instead
    # of falling back to the service-account creds.
    require_per_user_credential: bool = Field(
        default=False,
        validation_alias="ISE_REQUIRE_PER_USER_CREDENTIAL",
    )

    # Preferred Tier-1 session cookie for the ISE admin web UI
    # (/admin/*) log-download surface. Holds the raw Cookie header
    # value, e.g. "APPSESSIONID=...; MNTLA_JWT_TOKEN=...". When set,
    # IseWebSession uses it directly and fails loud on expiry; when
    # empty/absent, IseWebSession falls back to form login. SecretStr
    # because it is a live credential.
    ise_admin_session_cookie: Optional[SecretStr] = Field(
        default=None, validation_alias="ISE_ADMIN_SESSION_COOKIE"
    )
    # How long a cached, extracted log is served without revalidation.
    log_cache_ttl_s: float = Field(
        default=300.0, gt=0, validation_alias="LOG_CACHE_TTL_S"
    )
    # Prefix for the per-process temp cache directory.
    log_cache_dir_prefix: str = Field(
        default="ise-logs-", min_length=1, validation_alias="LOG_CACHE_DIR_PREFIX"
    )

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


settings = ISESettings()
