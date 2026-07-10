# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Scan a cleaned ``ise-psc.log`` for certificate/TLS error signals.

Pure and testable (only reads the given file). Filters to the most-recent
2-hour window anchored to the latest parseable timestamp in the log (same
anchoring approach as ``SystemStatsParser``), applies a fixed, case-insensitive
signal set, and returns up to five raw matched lines (newest first) plus the
total number of matching lines seen in the window.

Signal tokens are grouped only for readability; the output returns raw line
text with no category label. Over-broad tokens (bare ``certificate``, ``OCSP``,
``CRL``, ``NotAfter``, ``NotBefore``, ``SHA256withECDSA``, ``private key``) are
deliberately excluded to keep the five returned lines high-signal.
"""

import re
from datetime import timedelta
from pathlib import Path
from typing import Optional

from services.system_stats_parser import _parse_ts  # reuse ISE log ts parsing

_WINDOW_MINUTES = 120
_MAX_LINES_PER_NODE = 5

# RADIUS certificate-related error codes.
_RADIUS_CODES = ["12514", "12516", "12517", "12519", "12520", "12539"]

# Runtime TLS / EAP / validation failures.
_RUNTIME_SIGNALS = [
    "PKIX",
    "Unknown CA",
    "unable to find valid certification path",
    "unable to get issuer certificate",
    "certificate verify failed",
    "certificate has expired",
    "X509 certificate expired",
    "Certificate Expired",
    "SunCertPathBuilderException",
    "SSLHandshake",
    "Ssl_handshake",
    "handshake_failure",
    "tls_alert",
    "Generated Client Alert",
    "x509ExceptionCallback",
    "OCSP Callback",
    "OpenSSLErrorMessage",
    "OpenSSLErrorStack",
    "EVP_DecryptFinal_ex",
    "bad decrypt",
    "EapTlsSessionTicket",
    "Queue Link Error",
]

# Certificate management / config failures.
_MGMT_SIGNALS = [
    "CertMgmtUtils",
    "TrustedCertificatesAction",
    "deleteCertFromStore",
    "Failed to parse certificate",
    "Certificate tag is missing",
    "Certificate hierarchy must terminate",
    "Certificate Replication failed",
    "Portal could not start",
    "NoSuchAlgorithmException",
]

# Numeric codes are matched on a word boundary so "12514" doesn't hit inside a
# longer number; text tokens are matched as literal case-insensitive substrings.
SIGNAL_PATTERNS = (
    [re.compile(rf"\b{code}\b") for code in _RADIUS_CODES]
    + [re.compile(re.escape(tok), re.IGNORECASE) for tok in _RUNTIME_SIGNALS + _MGMT_SIGNALS]
)


def _is_signal(line: str) -> bool:
    return any(p.search(line) for p in SIGNAL_PATTERNS)


class CertificateLogScanner:
    def scan(self, log_path: Path) -> Optional[dict]:
        """Return matched cert/TLS signal lines in the recent 2h window.

        Returns ``{"matches": [...], "total_matches": int}`` with up to
        ``_MAX_LINES_PER_NODE`` raw lines (newest first), or ``None`` when no
        line in the window matches a signal.
        """
        timestamped: list[tuple] = []  # (datetime, raw_line)
        for raw in open(log_path, "r", encoding="utf-8", errors="replace"):
            line = raw.rstrip("\n")
            ts = _parse_ts(line)
            if ts is None:
                continue
            timestamped.append((ts, line))

        if not timestamped:
            return None

        latest_ts = max(ts for ts, _ in timestamped)
        window_start = latest_ts - timedelta(minutes=_WINDOW_MINUTES)
        in_window = [(ts, ln) for ts, ln in timestamped if ts >= window_start]
        in_window.sort(key=lambda pair: pair[0])  # oldest -> newest

        matches = [ln for _, ln in in_window if _is_signal(ln)]
        if not matches:
            return None

        newest_first = list(reversed(matches))
        return {
            "matches": newest_first[:_MAX_LINES_PER_NODE],
            "total_matches": len(matches),
        }
