# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys
import warnings
from logging.handlers import RotatingFileHandler

import structlog

APP_LOGGER_NAME = "ise-mcp-server"

_LEVEL_ALIASES: dict[str, str] = {
    "WARN": "WARNING",
    "FATAL": "CRITICAL",
}
_DEFAULT_LEVEL = logging.INFO
_FILE_MAX_BYTES = 10 * 1024 * 1024
_FILE_BACKUP_COUNT = 5
_managed_handlers: list[logging.Handler] = []


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


def _positive_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def setup_logging() -> None:
    """Configure structured logging for the MCP server.

    Env vars:
        DEBUG_MCP: Set to "true" for DEBUG level. Otherwise defaults to INFO.
        LOG_COLORS: Force ANSI colors on/off. Defaults to autodetecting whether
            stderr is a TTY.
        LOG_FILE: Optional path for a JSON-lines log alongside stderr.
        LOG_FILE_MAX_BYTES: Rotate the file after this many bytes (default 10 MiB).
        LOG_FILE_BACKUP_COUNT: Number of rotated files to retain (default 5).
    """
    debug_enabled = os.environ.get("DEBUG_MCP", "").lower() == "true"
    log_level = "DEBUG" if debug_enabled else "INFO"

    shared_processors = [
        structlog.contextvars.merge_contextvars,
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
    ]

    console_renderer = structlog.dev.ConsoleRenderer(colors=_resolve_use_colors())

    def render_console(logger, method_name, event_dict):
        from_structlog = event_dict.get("_from_structlog", False)
        event_dict = structlog.stdlib.ProcessorFormatter.remove_processors_meta(
            logger, method_name, event_dict
        )
        if not from_structlog:
            return str(event_dict["event"])
        return console_renderer(logger, method_name, event_dict)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[render_console],
            keep_exc_info=True,
            keep_stack_info=True,
        )
    )
    handlers: list[logging.Handler] = [console_handler]

    log_file = os.environ.get("LOG_FILE", "").strip()
    if log_file:
        max_bytes = _positive_int_env("LOG_FILE_MAX_BYTES", _FILE_MAX_BYTES)
        backup_count = _positive_int_env("LOG_FILE_BACKUP_COUNT", _FILE_BACKUP_COUNT)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                foreign_pre_chain=shared_processors,
                processors=[
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(default=str),
                ],
            )
        )
        handlers.append(file_handler)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    root = logging.getLogger()
    root.handlers.clear()
    for old_handler in _managed_handlers:
        old_handler.close()
    root.handlers.extend(handlers)
    _managed_handlers[:] = handlers
    root.setLevel(logging.WARNING)

    level = _resolve_log_level(log_level)
    for prefix in ("tools", "clients", "services", "utils", "resources", "models", "shared_libs"):
        logging.getLogger(prefix).setLevel(level)
    logging.getLogger(APP_LOGGER_NAME).setLevel(level)


setup_logging()

logger = structlog.get_logger(APP_LOGGER_NAME)
