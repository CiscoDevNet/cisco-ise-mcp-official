# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""
Single source of truth for ISE client configuration.

Exposes one module-level ``settings`` singleton. All ISE HTTP clients
(``client_factory``, ``mnt_client``, ``ers_client``) read from it instead of
calling ``os.getenv`` directly. The password is held as ``SecretStr`` so it
is never exposed via ``repr()``, tracebacks, or accidental ``vars()`` dumps.
"""

from typing import Optional

from pydantic import Field, SecretStr, field_validator
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
        "api_port", "api_username", "api_pwd", mode="before"
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


settings = ISESettings()
