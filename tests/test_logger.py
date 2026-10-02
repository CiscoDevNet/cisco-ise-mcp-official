# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent


def _run_logging(code: str, **settings: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for name in ("LOG_FILE", "LOG_FILE_MAX_BYTES", "LOG_FILE_BACKUP_COUNT", "LOG_COLORS"):
        env.pop(name, None)
    env.update(settings)
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_DIR,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_logging_without_file_keeps_console_output():
    result = _run_logging(
        'from logger import logger; logger.info("tool invoked", ise_api="/ers/config")'
    )

    assert result.returncode == 0
    assert "tool invoked" in result.stderr
    assert "/ers/config" in result.stderr
    assert "\x1b[" not in result.stderr


def test_file_contains_json_events_and_stderr_stays_human_readable(tmp_path):
    tracefile = tmp_path / "audit.jsonl"
    result = _run_logging(
        'import logging; from pathlib import Path; from logger import logger; '
        'logger.info("tool invoked", ise_api="/ers/config", path=Path("/tmp")); '
        'logging.getLogger("external").warning("other warning")',
        LOG_FILE=str(tracefile),
    )

    assert result.returncode == 0, result.stderr
    assert "tool invoked" in result.stderr
    assert "\x1b[" not in result.stderr
    assert result.stderr.splitlines()[-1] == "other warning"
    events = [json.loads(line) for line in tracefile.read_text().splitlines()]
    assert len(events) == 2
    assert events[0]["event"] == "tool invoked"
    assert events[0]["ise_api"] == "/ers/config"
    assert events[0]["path"] == "/tmp"
    assert events[0]["level"] == "info"
    assert events[0]["logger"] == "ise-mcp-server"
    assert events[0]["filename"] == "<string>"
    assert isinstance(events[0]["lineno"], int)
    assert events[0]["timestamp"].endswith("Z")
    assert events[1]["event"] == "other warning"
    assert events[1]["logger"] == "external"


def test_file_rotation_honors_backup_count(tmp_path):
    tracefile = tmp_path / "audit.jsonl"
    result = _run_logging(
        'from logger import logger; '
        '[logger.info("tool invoked", index=i) for i in range(30)]',
        LOG_FILE=str(tracefile),
        LOG_FILE_MAX_BYTES="350",
        LOG_FILE_BACKUP_COUNT="2",
    )

    assert result.returncode == 0, result.stderr
    assert tracefile.exists()
    assert (tmp_path / "audit.jsonl.1").exists()
    assert (tmp_path / "audit.jsonl.2").exists()
    assert not (tmp_path / "audit.jsonl.3").exists()
    for path in tmp_path.iterdir():
        for line in path.read_text().splitlines():
            assert json.loads(line)["event"] == "tool invoked"


def test_foreign_exception_keeps_stderr_traceback_and_json_exception(tmp_path):
    tracefile = tmp_path / "audit.jsonl"
    result = _run_logging(
        'import logging; import logger; '
        'error = RuntimeError("boom"); '
        'logging.getLogger("external").error("failed", exc_info=(type(error), error, error.__traceback__))',
        LOG_FILE=str(tracefile),
    )

    assert result.returncode == 0, result.stderr
    assert "failed\nRuntimeError: boom" in result.stderr
    event = json.loads(tracefile.read_text().splitlines()[0])
    assert event["event"] == "failed"
    assert "RuntimeError: boom" in event["exception"]


def test_invalid_rotation_settings_fail_at_startup(tmp_path):
    tracefile = tmp_path / "audit.jsonl"
    result = _run_logging(
        "import logger",
        LOG_FILE=str(tracefile),
        LOG_FILE_BACKUP_COUNT="0",
    )

    assert result.returncode != 0
    assert "LOG_FILE_BACKUP_COUNT must be a positive integer" in result.stderr
    assert not tracefile.exists()
