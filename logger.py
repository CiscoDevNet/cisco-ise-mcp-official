# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys
import warnings

import structlog

APP_LOGGER_NAME = "ise-mcp-server"

_LEVEL_ALIASES: dict[str, str] = {
    "WARN": "WARNING",
    "FATAL": "CRITICAL",
}
_DEFAULT_LEVEL = logging.INFO


def _resolve_log_level(raw: str) -> int:
    """Resolve a log-level name to its ``logging`` integer constant.

    Accepts common aliases (``WARN`` -> ``WARNING``, ``FATAL`` -> ``CRITICAL``)
    and falls back to ``INFO`` with a visible warning for unrecognised values.
    """
    name = _LEVEL_ALIASES.get(raw, raw)
    level = logging.getLevelName(name)
    if isinstance(level, int):
        return level
    warnings.warn(
        f"Unknown log level '{raw}', falling back to INFO",
        stacklevel=2,
    )
    return _DEFAULT_LEVEL


def _resolve_use_colors() -> bool:
    """Decide whether the console renderer should emit ANSI color codes.

    ConsoleRenderer colorizes unconditionally on non-Windows platforms and does
    not check whether the destination is a real terminal. When logs are captured
    to a file or pipe (``docker logs``, ``podman logs``, a systemd journal), that
    leaves raw escape sequences (``^[[2m ...``) in the log. Autodetect the
    stream's TTY status, with an explicit LOG_COLORS override for operators.
    """
    override = os.environ.get("LOG_COLORS")
    if override is not None:
        return override.strip().lower() in {"1", "true", "yes", "on"}
    return sys.stderr.isatty()


def setup_logging() -> None:
    """Configure structured logging for the MCP server.

    Env vars:
        DEBUG_MCP: Set to "true" for DEBUG level. Otherwise defaults to INFO.
        LOG_COLORS: Force ANSI colors on/off. Defaults to autodetecting whether
            stderr is a TTY.
    """
    debug_enabled = os.environ.get("DEBUG_MCP", "").lower() == "true"
    log_level = "DEBUG" if debug_enabled else "INFO"

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ],
            ),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=_resolve_use_colors()),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.WARNING)

    level = _resolve_log_level(log_level)
    for prefix in ("tools", "clients", "services", "utils", "resources", "models", "shared_libs"):
        logging.getLogger(prefix).setLevel(level)
    logging.getLogger(APP_LOGGER_NAME).setLevel(level)


setup_logging()

logger = structlog.get_logger(APP_LOGGER_NAME)
