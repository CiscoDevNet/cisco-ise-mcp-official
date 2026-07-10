# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from services.system_stats_parser import SystemStatsParser


def _util_line(ts, cpu, mem, disks):
    # disks: list of (pct, mount)
    disk_str = ", ".join(f"SysStatsUtilizationDiskSpace={p}% {m}" for p, m in disks)
    return (
        f"{ts} 0000010615 70000 NOTICE System-Stats: ISE Utilization, "
        f"ConfigVersionId=892, SysStatsUtilizationCpu={cpu}%, "
        f"SysStatsUtilizationMemory={mem}%, SysStatsUtilizationDiskIO=0.06%, "
        f"{disk_str}, SysStatsCpuCount=12, ActiveSessionCount=0, \n"
    )


def _write(tmp_path, lines):
    p = tmp_path / "iseLocalStore.log"
    p.write_text("".join(lines), encoding="utf-8")
    return p


class TestSystemStatsParser:
    def test_returns_none_when_no_samples(self, tmp_path):
        p = tmp_path / "x.log"
        p.write_text("2026-07-01 00:00:00.000 +00:00 nothing relevant here\n")
        assert SystemStatsParser().parse(p) is None

    def test_aggregates_cpu_memory(self, tmp_path):
        lines = [
            _util_line("2026-07-01 00:00:00.000 +00:00", "2.00", "50.0", [("21", "/"), ("31", "/opt")]),
            _util_line("2026-07-01 00:30:00.000 +00:00", "4.00", "52.0", [("21", "/"), ("31", "/opt")]),
            _util_line("2026-07-01 01:00:00.000 +00:00", "3.00", "54.0", [("22", "/"), ("32", "/opt")]),
        ]
        p = _write(tmp_path, lines)
        out = SystemStatsParser().parse(p)
        assert out["sample_count"] == 3
        assert out["cpu_percent"] == {"min": 2.0, "max": 4.0, "avg": 3.0, "latest": 3.0}
        assert out["memory_percent"]["latest"] == 54.0
        assert out["memory_percent"]["min"] == 50.0

    def test_window_anchored_to_latest_timestamp(self, tmp_path):
        # First sample is >1h before the latest -> excluded from the window.
        lines = [
            _util_line("2026-07-01 00:00:00.000 +00:00", "99.0", "99.0", [("99", "/")]),
            _util_line("2026-07-01 01:10:00.000 +00:00", "3.00", "50.0", [("21", "/"), ("31", "/opt")]),
            _util_line("2026-07-01 02:00:00.000 +00:00", "5.00", "60.0", [("22", "/"), ("33", "/opt")]),
        ]
        p = _write(tmp_path, lines)
        out = SystemStatsParser().parse(p)
        # Only the 01:10 and 02:00 samples are within [02:00 - 60m, 02:00]
        assert out["sample_count"] == 2
        assert out["cpu_percent"]["max"] == 5.0  # the 99.0 sample was excluded
        assert out["window"]["end"].startswith("2026-07-01T02:00:00")

    def test_disk_limited_to_kept_mounts(self, tmp_path):
        lines = [
            _util_line(
                "2026-07-01 01:00:00.000 +00:00", "3.0", "50.0",
                [("21", "/"), ("1", "/boot"), ("31", "/opt"), ("1", "/tmp")],
            ),
        ]
        p = _write(tmp_path, lines)
        out = SystemStatsParser().parse(p)
        assert set(out["disk_percent"].keys()) == {"/", "/opt"}
        assert out["disk_percent"]["/"]["latest"] == 21
        assert out["disk_percent"]["/opt"]["latest"] == 31

    def test_skips_unparseable_timestamps(self, tmp_path):
        lines = [
            "BADTS System-Stats: ISE Utilization, SysStatsUtilizationCpu=9.0%, SysStatsUtilizationMemory=9.0%, SysStatsUtilizationDiskSpace=9% /, \n",
            _util_line("2026-07-01 01:00:00.000 +00:00", "3.0", "50.0", [("21", "/"), ("31", "/opt")]),
        ]
        p = _write(tmp_path, lines)
        out = SystemStatsParser().parse(p)
        assert out["sample_count"] == 1
        assert out["cpu_percent"]["latest"] == 3.0

    def test_metric_absent_in_some_samples_is_tolerated(self, tmp_path):
        # A sample line with no memory field: memory aggregates over the others.
        good = _util_line("2026-07-01 01:00:00.000 +00:00", "3.0", "50.0", [("21", "/"), ("31", "/opt")])
        no_mem = (
            "2026-07-01 01:05:00.000 +00:00 0000010615 70000 NOTICE System-Stats: "
            "ISE Utilization, SysStatsUtilizationCpu=4.0%, "
            "SysStatsUtilizationDiskSpace=21% /, SysStatsUtilizationDiskSpace=31% /opt, \n"
        )
        p = _write(tmp_path, [good, no_mem])
        out = SystemStatsParser().parse(p)
        assert out["sample_count"] == 2
        assert out["cpu_percent"]["max"] == 4.0
        # memory present in only one sample
        assert out["memory_percent"]["latest"] == 50.0
