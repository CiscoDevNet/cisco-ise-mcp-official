# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class TestParseTs:
    """ISE writes two leading-timestamp shapes: ".mmm +HH:MM" and ",mmm" (no offset)."""

    def test_dot_millis_with_offset(self):
        from services.system_stats_parser import _parse_ts
        got = _parse_ts("2026-07-01 00:02:37.362 +00:00 INFO something")
        assert got == datetime(2026, 7, 1, 0, 2, 37, 362000, tzinfo=timezone.utc)

    def test_non_utc_offset_is_preserved(self):
        from services.system_stats_parser import _parse_ts
        got = _parse_ts("2026-07-01 00:02:37.362 +05:30 INFO something")
        assert got.utcoffset() == timedelta(hours=5, minutes=30)

    def test_comma_millis_without_offset_is_treated_as_utc(self):
        from services.system_stats_parser import _parse_ts
        got = _parse_ts("2026-08-17 18:10:45,180 INFO  [admin-http-pool32] something")
        assert got == datetime(2026, 8, 17, 18, 10, 45, 180000, tzinfo=timezone.utc)

    def test_dot_millis_without_offset(self):
        from services.system_stats_parser import _parse_ts
        got = _parse_ts("2026-08-17 18:10:45.180 INFO something")
        assert got == datetime(2026, 8, 17, 18, 10, 45, 180000, tzinfo=timezone.utc)

    def test_result_is_always_timezone_aware(self):
        from services.system_stats_parser import _parse_ts
        with_off = _parse_ts("2026-08-17 18:00:00.000 +00:00 line")
        without = _parse_ts("2026-08-17 18:10:45,180 line")
        # Must be mutually comparable — the scanner sorts both shapes together.
        assert without > with_off

    def test_line_without_leading_timestamp_returns_none(self):
        from services.system_stats_parser import _parse_ts
        assert _parse_ts("        at java.base/sun.security.ssl.Alert.createSSLException") is None
        assert _parse_ts("") is None

    def test_timestamp_must_be_at_line_start(self):
        from services.system_stats_parser import _parse_ts
        assert _parse_ts("prefix 2026-08-17 18:10:45,180 INFO something") is None

    def test_malformed_date_returns_none(self):
        from services.system_stats_parser import _parse_ts
        assert _parse_ts("2026-13-45 99:99:99,180 INFO impossible date") is None
