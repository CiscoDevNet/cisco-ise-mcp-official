# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def _write(tmp_path, lines):
    p = tmp_path / "ise-psc.log"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _ts(minute):
    # All within the same hour so they fall in a 120-minute window.
    return f"2026-07-03 10:{minute:02d}:00.000 +00:00"


class TestCertificateLogScanner:
    def test_matches_runtime_signal(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            f"{_ts(1)} INFO normal startup line",
            f"{_ts(2)} ERROR PKIX path building failed: unable to find valid certification path",
        ])
        result = CertificateLogScanner().scan(p)
        assert result is not None
        assert result["total_matches"] == 1
        assert any("PKIX" in line for line in result["matches"])

    def test_matches_radius_code_and_mgmt_signal(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            f"{_ts(1)} 12514 EAP-TLS failed SSL/TLS handshake",
            f"{_ts(2)} CertMgmtUtils Failed to parse certificate",
        ])
        result = CertificateLogScanner().scan(p)
        assert result["total_matches"] == 2

    def test_no_match_returns_none(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            f"{_ts(1)} INFO healthy line",
            f"{_ts(2)} INFO another benign line about a certificate being loaded",
        ])
        # bare "certificate" is NOT a signal, so this benign line must not match.
        assert CertificateLogScanner().scan(p) is None

    def test_dropped_broad_tokens_do_not_match(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            f"{_ts(1)} INFO OCSP responder status OK",
            f"{_ts(2)} INFO CRL downloaded; NotAfter far in future",
            f"{_ts(3)} INFO cert uses SHA256withECDSA",
        ])
        assert CertificateLogScanner().scan(p) is None

    def test_caps_at_five_and_counts_total(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        lines = [f"{_ts(i)} ERROR Unknown CA hit number {i}" for i in range(1, 9)]
        p = _write(tmp_path, lines)
        result = CertificateLogScanner().scan(p)
        assert result["total_matches"] == 8
        assert len(result["matches"]) == 5

    def test_window_excludes_old_lines(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            "2026-07-03 05:00:00.000 +00:00 ERROR Unknown CA old, out of window",
            "2026-07-03 10:00:00.000 +00:00 ERROR Unknown CA recent, in window",
        ])
        result = CertificateLogScanner().scan(p)
        # Window is 120 min anchored to the latest ts (10:00), so 05:00 is excluded.
        assert result["total_matches"] == 1
        assert "recent" in result["matches"][0]

    def test_matches_real_ise_psc_timestamp_format(self, tmp_path):
        """ise-psc.log uses "2026-08-17 18:10:45,180" — comma millis, no UTC offset.

        The scanner previously parsed zero such lines, so every node reported
        0 matches regardless of content.
        """
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            "2026-08-17 12:32:52,664 INFO  [main][[]] epm.auth.encryptor.crypt.TPMUtil -:::::- decrypting key...",
            "2026-08-17 18:10:45,180 INFO  [admin-http-pool32][[]] cpm.restidstore.eventmanager.notifications."
            "TrustCertificateNotificationHandler -::admin::deleteCertFromStore:- Pushing delete notification "
            "for TrustCertificate apiuser#48cc5e31",
        ])
        result = CertificateLogScanner().scan(p)
        assert result is not None
        assert result["total_matches"] == 1
        assert "deleteCertFromStore" in result["matches"][0]

    def test_cert_delete_matches_only_originating_notification(self, tmp_path):
        """One admin deletion fans out to several listener lines that also carry
        "deleteCertFromStore"; only the originating notification should match."""
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            "2026-08-17 18:10:45,180 INFO  [admin-http-pool32][[]] cpm.restidstore.eventmanager.notifications."
            "TrustCertificateNotificationHandler -::admin::deleteCertFromStore:- Pushing delete notification "
            "for TrustCertificate apiuser#48cc5e31",
            "2026-08-17 18:10:45,187 INFO  [admin-http-pool32][[]] cisco.cpm.posture.token.PostureTokenFactory "
            "-::admin::deleteCertFromStore:- SwissListener - Listened to TrustCertificate delete",
            "2026-08-17 18:10:45,190 INFO  [admin-http-pool32][[]] cisco.cpm.nsf.notifications.CertChangeHandler "
            "-::admin::deleteCertFromStore:- handling cert change",
        ])
        result = CertificateLogScanner().scan(p)
        assert result["total_matches"] == 1
        assert "Pushing delete notification" in result["matches"][0]

    def test_window_applies_to_comma_millis_format(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            "2026-08-17 12:00:00,000 ERROR Unknown CA old, out of window",
            "2026-08-17 18:10:45,180 ERROR Unknown CA recent, in window",
        ])
        result = CertificateLogScanner().scan(p)
        assert result["total_matches"] == 1
        assert "recent" in result["matches"][0]

    def test_mixed_timestamp_formats_do_not_error(self, tmp_path):
        """Offset-bearing and offset-less lines must stay mutually comparable."""
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            "2026-08-17 18:00:00.000 +00:00 ERROR Unknown CA with offset",
            "2026-08-17 18:10:45,180 ERROR Unknown CA without offset",
        ])
        result = CertificateLogScanner().scan(p)
        assert result["total_matches"] == 2

    def test_lines_without_timestamp_are_ignored_for_window(self, tmp_path):
        from services.certificate_log_scanner import CertificateLogScanner
        p = _write(tmp_path, [
            "no-timestamp Unknown CA stray continuation line",
            f"{_ts(1)} ERROR Unknown CA proper line",
        ])
        result = CertificateLogScanner().scan(p)
        assert result["total_matches"] == 1
