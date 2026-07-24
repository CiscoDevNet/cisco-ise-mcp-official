# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Admission control for heavy ISE MnT reads (AuthList downloads, dashboard summary).

Three layers, all configurable via ``clients.settings.settings``:

1. Semaphore (default 1): caps concurrent AuthList downloads and rejects
   immediately when full -- no queue wait.
2. Min-interval floor (default 0.0 = off): rejects a call that starts
   sooner than ``min_interval_s`` after the previous download started,
   to proactively space large downloads off the MnT node.
3. Adaptive circuit breaker: opens on MnT distress (HTTP 502/503/504,
   connect/read timeouts) for a window that doubles per consecutive
   failure (base -> ... -> max, plus jitter). While open, calls reject
   fast; after the window one half-open probe is admitted -- success
   resets the breaker, failure re-opens it (capped at max).

All rejections raise ``ISE_BUSY`` (EXTERNAL_ERROR, retry=True).
"""

import asyncio
import random
import time
from contextlib import asynccontextmanager
from typing import Callable, Optional

import httpx

from logger import logger
from clients.settings import settings
from models.error_models import ErrorCategory, raise_tool_error

# HTTP statuses that indicate the MnT node itself is overloaded/unavailable.
_DISTRESS_STATUSES = frozenset({502, 503, 504})


class MntGate:
    def __init__(
        self,
        max_concurrency: int,
        min_interval_s: float,
        backoff_base_s: float,
        backoff_max_s: float,
        *,
        time_fn: Callable[[], float] = time.monotonic,
        jitter_fn: Optional[Callable[[], float]] = None,
    ) -> None:
        self._sem = asyncio.Semaphore(max_concurrency)
        self._min_interval_s = min_interval_s
        self._backoff_base_s = backoff_base_s
        self._backoff_max_s = backoff_max_s
        self._time_fn = time_fn
        self._jitter_fn = jitter_fn or (lambda: random.uniform(0.0, backoff_base_s * 0.1))

        # State guarded by ``_lock`` (admission decisions are non-blocking).
        self._lock = asyncio.Lock()
        self._last_start: Optional[float] = None
        self._consecutive_failures = 0
        self._breaker_open_until: Optional[float] = None
        self._probing = False  # a half-open probe is currently in flight

    @classmethod
    def from_settings(cls) -> "MntGate":
        return cls(
            max_concurrency=settings.mnt_gate_max_concurrency,
            min_interval_s=settings.mnt_gate_min_interval_s,
            backoff_base_s=settings.mnt_gate_backoff_base_s,
            backoff_max_s=settings.mnt_gate_backoff_max_s,
        )

    def _reject(self, reason: str) -> None:
        logger.warning("AuthList gate rejected call", reason=reason)
        raise_tool_error(
            ErrorCategory.EXTERNAL_ERROR,
            "ISE_BUSY",
            "The ISE MnT node is busy (another large query is in progress or "
            "the node is under load). Retry shortly.",
            retry=True,
        )

    async def _admit(self) -> None:
        """Decide admission under the state lock; raise ISE_BUSY to reject.

        On success, records the start time and acquires the semaphore slot
        (guaranteed non-blocking because we only acquire when not locked).
        """
        async with self._lock:
            now = self._time_fn()

            # Breaker gate.
            if self._breaker_open_until is not None:
                if now < self._breaker_open_until:
                    # Still within the open window -> reject.
                    self._reject("breaker_open")
                elif self._probing:
                    # Another probe is already deciding the breaker's fate.
                    self._reject("breaker_probing")
                else:
                    # Window elapsed: admit exactly one half-open probe.
                    self._probing = True

            # Min-interval floor.
            if (
                self._min_interval_s > 0.0
                and self._last_start is not None
                and (now - self._last_start) < self._min_interval_s
            ):
                # A probe reservation must be undone before rejecting.
                if self._breaker_open_until is not None:
                    self._probing = False
                self._reject("min_interval")

            # Concurrency slot (non-blocking).
            if self._sem.locked():
                if self._breaker_open_until is not None:
                    self._probing = False
                self._reject("at_capacity")
            await self._sem.acquire()
            self._last_start = now

    async def _record_success(self) -> None:
        async with self._lock:
            self._consecutive_failures = 0
            self._breaker_open_until = None
            self._probing = False

    async def _record_failure(self) -> None:
        async with self._lock:
            self._consecutive_failures += 1
            window = self._backoff_base_s * (2 ** (self._consecutive_failures - 1))
            window = min(window, self._backoff_max_s) + self._jitter_fn()
            self._breaker_open_until = self._time_fn() + window
            self._probing = False
            logger.warning(
                "AuthList breaker opened",
                consecutive_failures=self._consecutive_failures,
                open_for_s=round(window, 2),
            )

    @asynccontextmanager
    async def guard(self):
        await self._admit()
        recorded = False
        try:
            yield
        except (httpx.TimeoutException, httpx.ConnectError):
            await self._record_failure()
            recorded = True
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code in _DISTRESS_STATUSES:
                await self._record_failure()
                recorded = True
            raise
        else:
            await self._record_success()
            recorded = True
        finally:
            # If we exited without recording (non-distress exception during probe),
            # clear the probe reservation so the breaker doesn't stay locked.
            if not recorded:
                async with self._lock:
                    self._probing = False
            self._sem.release()


mnt_gate = MntGate.from_settings()
