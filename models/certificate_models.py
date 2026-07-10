# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

from typing import Literal, Optional

from pydantic import Field

from models.base import IseResultModel


class ExpiringCertificateSummary(IseResultModel):
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


class CertExpirationSummary(IseResultModel):
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


class ExpiringTrustedCertificatesResponse(IseResultModel):
    """Full response for the check_expiring_trusted_certificates tool."""

    certificates: list[ExpiringCertificateSummary] = Field(
        ...,
        description="Certificates sorted by expiration date ascending (most urgent first)",
    )
    summary: CertExpirationSummary = Field(..., description="Aggregate expiration counts and check metadata")


class CertLogMatch(IseResultModel):
    """A single raw matched line from an ise-psc.log scan."""

    line: str = Field(..., description="Raw log line that matched a certificate/TLS error signal")


class CertLogNodeResult(IseResultModel):
    """Per-PSN-node result of the ise-psc.log signal scan."""

    hostname: str = Field(..., description="PSN node hostname (or fqdn) scanned")
    status: Literal["ok", "unavailable"] = Field(
        ...,
        description="'ok' when the log was fetched and scanned; 'unavailable' when it could not be fetched/parsed",
    )
    matches: list[CertLogMatch] = Field(
        default_factory=list,
        description="Up to 5 raw matched lines (newest first) from the recent 2-hour window",
    )
    total_matches: int = Field(
        0, ge=0, description="Total matching lines seen in the window (may exceed the returned matches)"
    )
    reason: Optional[str] = Field(
        None, description="Generic reason when status is 'unavailable'; null when 'ok'"
    )


class CertLogScanResult(IseResultModel):
    """Aggregate result of scanning ise-psc.log across PSN nodes."""

    nodes: list[CertLogNodeResult] = Field(..., description="Per-node scan results")
    psn_nodes_total: int = Field(..., ge=0, description="PSN nodes discovered as scan candidates")
    psn_nodes_scanned: int = Field(..., ge=0, description="PSN nodes actually attempted (capped)")
    psn_nodes_succeeded: int = Field(..., ge=0, description="PSN nodes whose log was fetched and scanned")
    coverage_note: str = Field(..., description="Human-readable 'scanned X of Y PSN node(s)' summary")


class CertificateDiagnosisResult(IseResultModel):
    """Full response for the ise_diagnose_certificate_issues tool."""

    expiry: ExpiringTrustedCertificatesResponse = Field(
        ..., description="Trusted-certificate expiry check result"
    )
    log_scan: Optional[CertLogScanResult] = Field(
        None, description="PSN ise-psc.log signal scan; null when scan_logs=false"
    )
    verdict: Literal["healthy", "warning", "critical"] = Field(
        ..., description="Derived overall certificate-health verdict"
    )
    checked_at: str = Field(..., description="ISO 8601 timestamp of the diagnosis (UTC)")
