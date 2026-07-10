# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Parse and aggregate ISE ``System-Stats: ISE Utilization`` samples.

Pure, testable, no I/O beyond reading the given cleaned log file. Extracts
scalar metrics (CPU, memory) and per-mount disk utilization, keeps only the
most-recent-hour window anchored to the latest timestamp in the log, and
aggregates each metric to min/max/avg/latest.

Extending with more scalar metrics is a one-line addition to
``_SCALAR_METRICS``.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

_UTILIZATION_MARKER = "System-Stats: ISE Utilization"
_WINDOW_MINUTES = 60
_DISK_MOUNTS_KEPT = ("/", "/opt")

# Leading timestamp: "2026-07-01 00:02:37.362 +00:00"
_TS_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2})"
)
_TS_FMT = "%Y-%m-%d %H:%M:%S.%f %z"

# name -> regex capturing one numeric group. Add entries here to extend.
_SCALAR_METRICS = {
    "cpu_percent": re.compile(r"SysStatsUtilizationCpu=([\d.]+)%"),
    "memory_percent": re.compile(r"SysStatsUtilizationMemory=([\d.]+)%"),
}
# Disk: "SysStatsUtilizationDiskSpace=21% /" (mount is the token after the %).
_DISK_RE = re.compile(r"SysStatsUtilizationDiskSpace=(\d+)%\s+(\S+)")


def _parse_ts(line: str) -> Optional[datetime]:
    m = _TS_RE.match(line)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), _TS_FMT)
    except ValueError:
        return None


def _aggregate(values: list[float]) -> dict:
    return {
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 2),
        "latest": values[-1],
    }


class SystemStatsParser:
    def parse(self, log_path: Path) -> Optional[dict]:
        """Parse ISE Utilization samples from ``log_path``.

        Returns aggregated stats over the most-recent-hour window (anchored to
        the latest sample timestamp), or ``None`` if there are no parseable
        samples.
        """
        samples: list[tuple[datetime, str]] = []
        with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if _UTILIZATION_MARKER not in line:
                    continue
                ts = _parse_ts(line)
                if ts is None:
                    continue
                samples.append((ts, line))

        if not samples:
            return None

        latest_ts = max(ts for ts, _ in samples)
        window_start = latest_ts - timedelta(minutes=_WINDOW_MINUTES)
        in_window = [(ts, ln) for ts, ln in samples if ts >= window_start]
        if not in_window:
            return None
        in_window.sort(key=lambda pair: pair[0])  # oldest -> newest

        result: dict = {
            "window": {
                "start": in_window[0][0].isoformat(),
                "end": in_window[-1][0].isoformat(),
            },
            "sample_count": len(in_window),
        }

        # Scalar metrics (registry-driven).
        for name, pattern in _SCALAR_METRICS.items():
            values: list[float] = []
            for _, line in in_window:
                m = pattern.search(line)
                if m:
                    values.append(float(m.group(1)))
            if values:
                result[name] = _aggregate(values)

        # Disk per kept mount.
        disk: dict[str, list[float]] = {mount: [] for mount in _DISK_MOUNTS_KEPT}
        for _, line in in_window:
            for pct, mount in _DISK_RE.findall(line):
                mount = mount.rstrip(',')
                if mount in disk:
                    disk[mount].append(float(pct))
        disk_out = {
            mount: _aggregate(vals) for mount, vals in disk.items() if vals
        }
        if disk_out:
            result["disk_percent"] = disk_out

        return result
