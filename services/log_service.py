# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Download, extract, clean, and cache ISE node logs.

See docs/superpowers/specs/2026-07-01-ise-log-reading-service-design.md.
"""

import asyncio
import hashlib
import re
import shutil
import tempfile
import time
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Optional

from logger import logger
from clients.request_context import get_per_user_credential
from clients.settings import settings
from clients.url_safety import assert_url_under_base
from clients.ise_web_session import ise_web_session

__all__ = ["LogService", "log_service"]

_NAME_ALLOWED = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_SERVICE_ACCOUNT_KEY_MATERIAL = "__service_account__"


class LogService:
    _instance: Optional["LogService"] = None
    _initialized: bool = False

    def __new__(cls) -> "LogService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if LogService._initialized:
            return
        self._cache: dict = {}
        self._cache_dir: Optional[Path] = None
        self._locks: dict = {}
        self._fetch_seq = 0
        LogService._initialized = True
        logger.info("LogService initialized")

    @staticmethod
    def _validate_component(value: str, kind: str) -> str:
        if not isinstance(value, str) or not _NAME_ALLOWED.match(value):
            raise ValueError(
                f"invalid {kind}: must match {_NAME_ALLOWED.pattern}"
            )
        return value

    def _build_url(self, hostname: str, log_name: str) -> str:
        self._validate_component(hostname, "hostname")
        self._validate_component(log_name, "log_name")
        base = f"https://{settings.ise_ip}:{settings.api_port}"
        url = f"{base}/admin/{hostname}-{log_name}.log.zip"
        assert_url_under_base(url, f"{base}/admin/")
        return url

    @staticmethod
    def _select_latest_member(zf: zipfile.ZipFile) -> zipfile.ZipInfo:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if not infos:
            raise ValueError("zip archive contains no files")
        return max(infos, key=lambda i: i.date_time)

    def _now(self) -> float:
        return time.monotonic()

    async def setup(self) -> None:
        if self._cache_dir is not None:
            return
        self._cache_dir = Path(tempfile.mkdtemp(prefix=settings.log_cache_dir_prefix))
        logger.info("LogService cache dir created", path=str(self._cache_dir))

    async def close(self) -> None:
        if self._cache_dir and self._cache_dir.exists():
            shutil.rmtree(self._cache_dir, ignore_errors=True)
            logger.debug("LogService cache dir removed", path=str(self._cache_dir))
        self._cache_dir = None
        self._cache.clear()

    async def _download_and_extract(self, url: str, key: str) -> dict:
        if self._cache_dir is None:
            raise RuntimeError("LogService not set up; call await log_service.setup()")
        # Unique token for this fetch version so distinct versions never collide on disk
        self._fetch_seq += 1
        token = self._fetch_seq

        resp = await ise_web_session.get(url)
        resp.raise_for_status()

        zip_path = self._cache_dir / f"{key}.{token}.zip"
        zip_path.write_bytes(resp.content)

        log_path = self._cache_dir / f"{key}.{token}.log"
        with zipfile.ZipFile(zip_path) as zf:
            info = self._select_latest_member(zf)
            with zf.open(info) as src, open(log_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
        zip_path.unlink(missing_ok=True)

        return {
            "path": log_path,
            "etag": resp.headers.get("ETag"),
            "last_modified": resp.headers.get("Last-Modified"),
            "fetched_at": self._now(),
            "refcount": 0,
        }

    @staticmethod
    def _key(hostname: str, log_name: str) -> str:
        # Include an opaque per-credential digest so a log downloaded under one
        # user's ISE session is never served from cache to a different user
        # (the download itself authenticates as the current request's user).
        # The raw credential is NEVER stored or logged; only this sha256 digest
        # is used as part of the key.
        material = get_per_user_credential() or _SERVICE_ACCOUNT_KEY_MATERIAL
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
        return f"{digest}__{hostname}__{log_name}"

    def _lock_for(self, key: str) -> asyncio.Lock:
        # Assumes a single event loop (check-then-set is safe).
        # _locks is intentionally not pruned; key space is bounded by hostname×log-name.
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    async def _get_entry(self, hostname: str, log_name: str) -> dict:
        key = self._key(hostname, log_name)
        url = self._build_url(hostname, log_name)
        async with self._lock_for(key):
            entry = self._cache.get(key)
            if entry is not None:
                age = self._now() - entry["fetched_at"]
                if age < settings.log_cache_ttl_s:
                    # Within TTL: pin and return cached entry.
                    entry["refcount"] = entry.get("refcount", 0) + 1
                    return entry
                # Past TTL: conditional revalidation.
                headers = {}
                if entry.get("etag"):
                    headers["If-None-Match"] = entry["etag"]
                if entry.get("last_modified"):
                    headers["If-Modified-Since"] = entry["last_modified"]
                resp = await ise_web_session.get(url, headers=headers)
                if resp.status_code == 304:
                    # 304 Not Modified: refresh TTL, pin, return cached entry.
                    entry["fetched_at"] = self._now()
                    entry["refcount"] = entry.get("refcount", 0) + 1
                    return entry
                # 200 (or anything else usable) -> supersede below.
            new_entry = await self._download_and_extract(url, key)
            old = self._cache.get(key)
            if old is not None and old.get("refcount", 0) == 0:
                self._unlink_entry_files(old)
            elif old is not None:
                old["stale"] = True
            # Pin the new entry before storing and returning it.
            new_entry["refcount"] = new_entry.get("refcount", 0) + 1
            self._cache[key] = new_entry
            return new_entry

    @staticmethod
    def _unlink_entry_files(entry: dict) -> None:
        p = entry.get("path")
        if isinstance(p, Path):
            p.unlink(missing_ok=True)

    @asynccontextmanager
    async def fetch(
        self, log_name: str, hostname: str
    ) -> AsyncIterator[Path]:
        """Yield a path to the extracted latest log; pins it for the block.

        The returned entry is already pinned (refcount incremented) by
        _get_entry under the per-key lock, so a concurrent supersede cannot
        unlink the file this borrower is about to read. The finally block
        releases the pin under the same lock and lazily evicts a superseded
        (stale) entry once its last borrower leaves.
        """
        key = self._key(hostname, log_name)
        entry = await self._get_entry(hostname, log_name)
        try:
            yield entry["path"]
        finally:
            async with self._lock_for(key):
                entry["refcount"] -= 1
                if entry["refcount"] <= 0 and entry.get("stale"):
                    self._unlink_entry_files(entry)


log_service = LogService()
