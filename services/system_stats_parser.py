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
from datetime import datetime
from typing import Optional

# Leading timestamp: "2026-07-01 00:02:37.362 +00:00"
_TS_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2})"
)
_TS_FMT = "%Y-%m-%d %H:%M:%S.%f %z"


def _parse_ts(line: str) -> Optional[datetime]:
    m = _TS_RE.match(line)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), _TS_FMT)
    except ValueError:
        return None
