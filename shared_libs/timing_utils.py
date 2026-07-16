# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import time
import inspect
import functools
from typing import Callable, Coroutine, Any, TypeVar
from collections.abc import Awaitable

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar('T')


def normalize_docstring(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Collapse a PEP-257-style multi-line docstring into a single normalized
    string suitable for SLM-facing MCP tool descriptions.

    Why: FastMCP serializes ``func.__doc__`` verbatim into the MCP tool
    descriptor's ``description`` field. PEP-257 docstrings carry leading
    indentation and embedded newlines that waste tokens and visually
    fragment routing instructions for small models. ``inspect.cleandoc``
    strips common leading whitespace and trims blank edges; we then join
    on single spaces so the SLM sees one continuous prose paragraph
    while the source stays human-readable.

    Apply BEFORE the framework decorator that reads the docstring (e.g.
    place it closer to the function than ``@ise_mcp_server.tool(...)``).
    """
    if func.__doc__:
        cleaned = inspect.cleandoc(func.__doc__)
        func.__doc__ = " ".join(cleaned.split())
    return func


def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure and log execution time of a sync function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            duration = time.perf_counter() - start_time
            logger.info("Node executed", node=func.__name__, duration_ms=round(duration * 1000, 2))
    return wrapper


def measure_time_async(func: Callable[..., Awaitable[T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    """Decorator to measure and log execution time of an async function."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        start_time = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            duration = time.perf_counter() - start_time
            logger.info("Node executed", node=func.__name__, duration_ms=round(duration * 1000, 2))
    return wrapper
