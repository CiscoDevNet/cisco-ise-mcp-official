# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Timestamp parsing for ISE log lines.

Formerly also hosted ``SystemStatsParser`` (log-derived CPU/memory/disk stats),
replaced by the MnT ``getSystemSummaryDetails`` API path. The ``_parse_ts``
helper and its regex/format remain because ``services.certificate_log_scanner``
reuses them for ISE log timestamp parsing.
"""

import re
from datetime import datetime, timezone
from typing import Optional

# Leading timestamp, in either shape ISE emits:
#   "2026-07-01 00:02:37.362 +00:00"  (dot millis, explicit offset)
#   "2026-08-17 18:10:45,180"         (comma millis, no offset — ise-psc.log)
# The offset is optional and the millisecond separator may be '.' or ','.
_TS_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[.,](\d{3})(?:\s+([+-]\d{2}:?\d{2}))?"
)
_TS_FMT = "%Y-%m-%d %H:%M:%S.%f %z"
_TS_FMT_NO_TZ = "%Y-%m-%d %H:%M:%S.%f"


def _parse_ts(line: str) -> Optional[datetime]:
    """Parse a leading ISE log timestamp into a timezone-aware datetime.

    Offset-less timestamps are treated as UTC so that every parsed value stays
    mutually comparable — callers sort and window mixed shapes together.
    """
    m = _TS_RE.match(line)
    if not m:
        return None

    stamp = f"{m.group(1)}.{m.group(2)}"
    offset = m.group(3)
    try:
        if offset:
            return datetime.strptime(f"{stamp} {offset}", _TS_FMT)
        return datetime.strptime(stamp, _TS_FMT_NO_TZ).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
