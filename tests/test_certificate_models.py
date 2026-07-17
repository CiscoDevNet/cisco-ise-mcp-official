# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def test_log_scan_result_shape():
    from models.certificate_models import (
        CertLogMatch,
        CertLogNodeResult,
        CertLogScanResult,
    )
    node = CertLogNodeResult(
        hostname="vm218",
        status="ok",
        matches=[CertLogMatch(line="PKIX path building failed")],
        total_matches=1,
    )
    scan = CertLogScanResult(
        nodes=[node],
        psn_nodes_total=2,
        psn_nodes_scanned=1,
        psn_nodes_succeeded=1,
        coverage_note="Scanned 1 of 2 PSN node(s).",
    )
    assert scan.nodes[0].matches[0].line.startswith("PKIX")
    assert scan.psn_nodes_total == 2


def test_diagnosis_result_allows_null_log_scan():
    from models.certificate_models import (
        CertExpirationSummary,
        CertificateDiagnosisResult,
        ExpiringTrustedCertificatesResponse,
    )
    expiry = ExpiringTrustedCertificatesResponse(
        certificates=[],
        summary=CertExpirationSummary(
            total_matched=0, expired_count=0, warning_count=0,
            earliest_expiration=None, checked_at="2026-07-03T00:00:00+00:00",
            expiry_window_days=30,
        ),
    )
    result = CertificateDiagnosisResult(
        expiry=expiry, log_scan=None, verdict="healthy",
        checked_at="2026-07-03T00:00:00+00:00",
    )
    assert result.log_scan is None
    assert result.verdict == "healthy"
