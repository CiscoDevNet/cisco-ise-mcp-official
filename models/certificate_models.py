# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExpiringCertificateSummary(BaseModel):
    """Summary of a single trusted certificate approaching or past expiration."""

    friendly_name: str = Field(..., description="Human-readable certificate label configured in ISE")
    expiration_date: str = Field(..., description="Expiration timestamp in ISO 8601 format")
    valid_from: Optional[str] = Field(None, description="Validity start timestamp in ISO 8601 format, when available")
    days_until_expiry: int = Field(
        ...,
        description="Days until expiration from now. Negative values mean the cert is already expired",
    )
    expiry_status: Literal["expired", "warning"] = Field(
        ...,
        description=(
            "expired = already past expiration; "
            "warning = expires within the requested expiry_days window"
        ),
    )
    ise_status: str = Field(..., description="Whether the certificate is enabled or disabled in ISE")
    trusted_for: str = Field(..., description="ISE services this certificate is trusted for (e.g. Cisco Services)")
    is_referred_in_policy: bool = Field(
        ...,
        description="True when this certificate is actively referenced in an ISE policy — expiry is operationally critical",
    )


class CertExpirationSummary(BaseModel):
    """Aggregate counts and metadata for the expiration check."""

    total_matched: int = Field(
        ...,
        description=(
            "Total certificates matching the filter criteria across all scanned pages. "
            "May exceed the number of returned certificates when limit is applied."
        ),
        ge=0,
    )
    expired_count: int = Field(..., description="Number of expired certificates in the returned set", ge=0)
    warning_count: int = Field(
        ...,
        description="Number of certificates expiring within the expiry_days window in the returned set",
        ge=0,
    )
    earliest_expiration: Optional[str] = Field(
        None,
        description="ISO 8601 expiration date of the most urgently expiring certificate in the result set",
    )
    checked_at: str = Field(..., description="ISO 8601 timestamp of when this check was performed (UTC)")
    expiry_window_days: int = Field(..., description="Look-ahead window used for this check, in days")


class ExpiringTrustedCertificatesResponse(BaseModel):
    """Full response for the check_expiring_trusted_certificates tool."""

    certificates: list[ExpiringCertificateSummary] = Field(
        ...,
        description="Certificates sorted by expiration date ascending (most urgent first)",
    )
    summary: CertExpirationSummary = Field(..., description="Aggregate expiration counts and check metadata")
