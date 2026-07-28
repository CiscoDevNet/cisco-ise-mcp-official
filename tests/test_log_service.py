# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import io
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


def _reset():
    import services.log_service as mod
    mod.LogService._instance = None
    mod.LogService._initialized = False


def _fake_stream(chunks, headers=None):
    """Build a fake ``ise_web_session.stream`` async context manager that
    yields a streaming-style response emitting ``chunks`` via aiter_bytes().

    ``chunks`` may be a flat list of bytes (same body every call) or a list
    of per-call chunk-lists (a different body each successive call). A
    ``.calls`` counter is attached to the returned callable.
    """
    import contextlib

    per_call = chunks and isinstance(chunks[0], (list, tuple))

    class _StreamResp:
        def __init__(self, body_chunks):
            self._chunks = body_chunks
            self.status_code = 200
            self.headers = headers or {}

        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            for c in self._chunks:
                yield c

    @contextlib.asynccontextmanager
    async def stream(url, *, headers=None):
        idx = fake_stream.calls
        fake_stream.calls += 1
        body = chunks[idx] if per_call else chunks
        yield _StreamResp(body)

    fake_stream = stream
    fake_stream.calls = 0
    return fake_stream


class TestUrlAndValidation:
    def setup_method(self):
        _reset()

    def test_build_url(self):
        import services.log_service as mod
        with patch("services.log_service.settings") as s:
            s.ise_ip = "10.0.0.1"
            s.api_port = 443
            svc = mod.LogService()
            url = svc._build_url("vm218.marcos.com", "iseLocalStore")
            assert url == "https://10.0.0.1:443/admin/vm218.marcos.com-iseLocalStore.log.zip"

    def test_validate_rejects_traversal(self):
        import services.log_service as mod
        svc = mod.LogService()
        with pytest.raises(ValueError):
            svc._validate_component("../etc", "hostname")

    def test_validate_rejects_slash(self):
        import services.log_service as mod
        svc = mod.LogService()
        with pytest.raises(ValueError):
            svc._validate_component("a/b", "log_name")


class TestMemberSelection:
    def setup_method(self):
        _reset()

    def _zip_bytes(self, members):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, dt, data in members:
                info = zipfile.ZipInfo(name, date_time=dt)
                zf.writestr(info, data)
        buf.seek(0)
        return buf

    def test_single_member(self):
        import services.log_service as mod
        svc = mod.LogService()
        buf = self._zip_bytes([("only.log", (2026, 7, 1, 7, 5, 0), b"x")])
        with zipfile.ZipFile(buf) as zf:
            info = svc._select_latest_member(zf)
            assert info.filename == "only.log"

    def test_latest_of_many(self):
        import services.log_service as mod
        svc = mod.LogService()
        buf = self._zip_bytes([
            ("old.log", (2026, 7, 1, 6, 0, 0), b"x"),
            ("new.log", (2026, 7, 1, 8, 0, 0), b"y"),
            ("mid.log", (2026, 7, 1, 7, 0, 0), b"z"),
        ])
        with zipfile.ZipFile(buf) as zf:
            info = svc._select_latest_member(zf)
            assert info.filename == "new.log"


class TestFetchExtract:
    def setup_method(self):
        _reset()

    def _zip_bytes(self, name, data):
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(zipfile.ZipInfo(name, date_time=(2026, 7, 1, 7, 5, 0)), data)
        return buf.getvalue()

    @pytest.mark.asyncio
    async def test_setup_creates_dir_close_removes(self, tmp_path):
        import services.log_service as mod
        with patch("services.log_service.settings") as s:
            s.log_cache_dir_prefix = "ise-logs-test-"
            s.log_download_max_concurrency = 1
            svc = mod.LogService()
            await svc.setup()
            assert svc._cache_dir is not None and svc._cache_dir.exists()
            d = svc._cache_dir
            await svc.close()
            assert not d.exists()

    @pytest.mark.asyncio
    async def test_download_extract_returns_raw_bytes(self, tmp_path):
        import services.log_service as mod
        # Extraction is byte-for-byte: CRLF is preserved (no cleaning pass).
        zip_data = self._zip_bytes("iseLocalStore.log", b"hello\r\nworld\r\n")
        headers = {"ETag": 'W/"1-2"', "Last-Modified": "Wed, 01 Jul 2026 07:05:01 GMT"}
        # Feed the zip as several small chunks so the streaming write path is
        # exercised end to end.
        chunks = [zip_data[i:i + 4] for i in range(0, len(zip_data), 4)]
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_dir_prefix = "ise-logs-test-"
            s.log_download_max_concurrency = 1
            sess.stream = _fake_stream(chunks, headers=headers)
            svc = mod.LogService()
            await svc.setup()
            try:
                entry = await svc._download_and_extract(
                    "https://h/admin/x.log.zip", "h__iseLocalStore"
                )
                assert entry["path"].exists()
                assert entry["path"].read_bytes() == b"hello\r\nworld\r\n"
                assert entry["etag"] == 'W/"1-2"'
                assert entry["last_modified"].startswith("Wed")
                assert entry["refcount"] == 0
            finally:
                await svc.close()

    @pytest.mark.asyncio
    async def test_download_streams_body_never_reads_content(self, tmp_path):
        """The zip must be assembled from streamed chunks, not a single
        buffered .content read (the OOM root cause)."""
        import services.log_service as mod
        zip_data = self._zip_bytes("app.log", b"streamed-body\n")
        chunks = [zip_data[i:i + 3] for i in range(0, len(zip_data), 3)]
        assert len(chunks) > 1  # sanity: genuinely multiple chunks

        iterated = {"count": 0}

        class TrackingStreamResponse:
            def __init__(self):
                self.status_code = 200
                self.headers = {"ETag": '"x"', "Last-Modified": "LM"}

            def raise_for_status(self):
                return None

            @property
            def content(self):
                raise AssertionError(
                    "streaming download must not touch resp.content"
                )

            async def aiter_bytes(self):
                for c in chunks:
                    iterated["count"] += 1
                    yield c

        import contextlib

        @contextlib.asynccontextmanager
        async def fake_stream(url, *, headers=None):
            yield TrackingStreamResponse()

        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_dir_prefix = "ise-logs-test-"
            s.log_download_max_concurrency = 1
            sess.stream = fake_stream
            svc = mod.LogService()
            await svc.setup()
            try:
                entry = await svc._download_and_extract(
                    "https://h/admin/x.log.zip", "h__app"
                )
                # Body was consumed chunk by chunk (once per chunk), not in one read.
                assert iterated["count"] == len(chunks)
                assert entry["path"].read_bytes() == b"streamed-body\n"
                assert entry["etag"] == '"x"'
            finally:
                await svc.close()


class TestDownloadConcurrencyLimit:
    def setup_method(self):
        _reset()

    def _zip_bytes(self, name, data):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(zipfile.ZipInfo(name, date_time=(2026, 7, 1, 7, 5, 0)), data)
        return buf.getvalue()

    @pytest.mark.asyncio
    async def test_concurrent_downloads_bounded_by_setting(self, tmp_path):
        """Concurrent downloads across distinct keys must not exceed
        settings.log_download_max_concurrency simultaneously."""
        import asyncio
        import contextlib
        import services.log_service as mod

        zip_data = self._zip_bytes("app.log", b"data\n")

        limit = 2
        in_flight = 0
        peak = 0
        entered = 0

        class _StreamResp:
            status_code = 200
            headers = {}
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield zip_data

        @contextlib.asynccontextmanager
        async def slow_stream(url, *, headers=None):
            nonlocal in_flight, peak, entered
            in_flight += 1
            entered += 1
            peak = max(peak, in_flight)
            try:
                # Hold the "download" open long enough that every task that is
                # ALLOWED to run concurrently overlaps here. Without a cap all
                # 5 overlap (peak=5); a semaphore(limit) keeps peak==limit.
                await asyncio.sleep(0.05)
                yield _StreamResp()
            finally:
                in_flight -= 1

        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            s.log_cache_dir_prefix = "ise-test-"
            s.log_download_max_concurrency = limit
            sess.stream = slow_stream

            svc = mod.LogService()
            await svc.setup()
            try:
                # 5 distinct hosts -> 5 distinct keys -> 5 distinct per-key
                # locks, so only the global download semaphore bounds them.
                async def fetch_host(i):
                    async with svc.fetch("app", f"h{i}") as p:
                        assert p.exists()

                await asyncio.gather(*(fetch_host(i) for i in range(5)))
                assert entered == 5
                assert peak <= limit, f"peak downloads {peak} exceeded limit {limit}"
                assert peak == limit, f"expected peak to reach limit {limit}, got {peak}"
            finally:
                await svc.close()


class TestLifespanContract:
    def test_singletons_have_setup_close(self):
        from clients.ise_web_session import ise_web_session
        from services.log_service import log_service
        for obj in (ise_web_session, log_service):
            assert hasattr(obj, "setup") and hasattr(obj, "close")


class TestBorrowAndCache:
    def setup_method(self):
        _reset()

    def _entry(self, tmp_path, ttl_ok=True):
        p = tmp_path / "c.log"
        p.write_text("data\n")
        return {
            "path": p,
            "etag": 'W/"1-2"', "last_modified": "LM",
            "fetched_at": 1000.0, "refcount": 0,
        }

    @pytest.mark.asyncio
    async def test_cache_hit_within_ttl_no_http(self, tmp_path):
        import services.log_service as mod
        from unittest.mock import AsyncMock, patch as p2
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            sess.get = AsyncMock()
            svc = mod.LogService()
            svc._cache_dir = tmp_path
            key = svc._key("h", "app")
            svc._cache[key] = self._entry(tmp_path)
            svc._now = lambda: 1100.0  # 100s < ttl
            async with svc.fetch("app", "h") as path:
                assert path.read_text() == "data\n"
            sess.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_304_refreshes_ttl(self, tmp_path):
        import services.log_service as mod
        from unittest.mock import AsyncMock, MagicMock
        resp = MagicMock(); resp.status_code = 304; resp.headers = {}
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            sess.get = AsyncMock(return_value=resp)
            svc = mod.LogService()
            svc._cache_dir = tmp_path
            key = svc._key("h", "app")
            svc._cache[key] = self._entry(tmp_path)
            svc._now = lambda: 2000.0  # past ttl -> revalidate
            async with svc.fetch("app", "h") as path:
                assert path.read_text() == "data\n"
            # conditional headers were sent
            _, kwargs = sess.get.call_args
            assert kwargs["headers"]["If-None-Match"] == 'W/"1-2"'
            assert svc._cache[key]["fetched_at"] == 2000.0

    @pytest.mark.asyncio
    async def test_borrow_pins_refcount(self, tmp_path):
        import services.log_service as mod
        with patch("services.log_service.settings") as s:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            svc = mod.LogService()
            svc._cache_dir = tmp_path
            key = svc._key("h", "app")
            svc._cache[key] = self._entry(tmp_path)
            svc._now = lambda: 1100.0
            async with svc.fetch("app", "h"):
                assert svc._cache[key]["refcount"] == 1
            assert svc._cache[key]["refcount"] == 0

    @pytest.mark.asyncio
    async def test_supersede_cannot_overwrite_active_borrow_files(self, tmp_path):
        """Regression: each fetched version must have unique on-disk file paths.

        Without unique paths, when a past-TTL borrow triggers a supersede (200 OK),
        the new version's extraction overwrites the same paths that the old version's
        borrower is still reading. This test verifies that a supersede creates new
        files with a unique version token, so the first borrower's path_v1 stays
        readable while path_v2 is being written. After both borrowers exit, the
        superseded v1 files are lazily evicted, and v2 remains.
        """
        import services.log_service as mod
        from unittest.mock import AsyncMock, MagicMock

        # Build two different zip contents
        def _zip_bytes(name, data):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                zf.writestr(zipfile.ZipInfo(name, date_time=(2026, 7, 1, 7, 5, 0)), data)
            return buf.getvalue()

        zip_v1 = _zip_bytes("app.log", b"version1\r\n")
        zip_v2 = _zip_bytes("app.log", b"version2\r\n")

        # Two successive DOWNLOADS stream distinct bodies (v1 then v2).
        v1_chunks = [zip_v1[i:i + 8] for i in range(0, len(zip_v1), 8)]
        v2_chunks = [zip_v2[i:i + 8] for i in range(0, len(zip_v2), 8)]

        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            s.log_cache_dir_prefix = "ise-test-"
            s.log_download_max_concurrency = 1

            # v1 download carries v1 headers; v2 download carries v2 headers.
            stream_v1 = _fake_stream(
                v1_chunks,
                headers={"ETag": '"v1"', "Last-Modified": "Wed, 01 Jul 2026 07:00:00 GMT"},
            )
            stream_v2 = _fake_stream(
                v2_chunks,
                headers={"ETag": '"v2"', "Last-Modified": "Wed, 01 Jul 2026 08:00:00 GMT"},
            )
            stream_calls = [0]
            import contextlib as _c

            @_c.asynccontextmanager
            async def mock_stream(url, *, headers=None):
                stream_calls[0] += 1
                use = stream_v1 if stream_calls[0] == 1 else stream_v2
                async with use(url, headers=headers) as resp:
                    yield resp
            sess.stream = mock_stream

            # Past-TTL conditional revalidation hits get(); return 200 so the
            # handler proceeds to a (streaming) supersede download.
            reval = MagicMock(); reval.status_code = 200; reval.headers = {}
            sess.get = AsyncMock(return_value=reval)

            svc = mod.LogService()
            await svc.setup()
            try:
                now = [1000.0]
                svc._now = lambda: now[0]
                key = svc._key("h", "app")

                # First borrow: cache miss -> fetch v1
                async with svc.fetch("app", "h") as path_v1:
                    # Capture v1's concrete path
                    assert path_v1.exists()
                    v1_content = path_v1.read_text()
                    assert "version1" in v1_content

                    # Advance past TTL to force supersede
                    now[0] = 1500.0

                    # Second borrow while first is active: forces 200 supersede
                    async with svc.fetch("app", "h") as path_v2:
                        # Verify v2 was fetched and is live
                        assert path_v2.exists()
                        v2_content = path_v2.read_text()
                        assert "version2" in v2_content

                        # CRITICAL: v1's path must STILL exist on disk while its
                        # pin is held, even though v2 has superseded it.
                        # This fails without unique paths: v2 overwrites v1's path.
                        assert path_v1.exists(), \
                            f"path_v1 ({path_v1}) was clobbered by supersede; should have unique path"
                        # And v1's original content should still be readable
                        assert path_v1.read_text() == v1_content

                    # After second borrow exits, v2 entry has refcount=0 but is not stale

                # First borrow exits: v1 entry (now stale) is lazily evicted
                # v1 files should be cleaned up
                assert not path_v1.exists(), "v1 files should be evicted after last pin dropped"

                # v2 is the live cached entry and its files should still exist
                current_entry = svc._cache[key]
                path_v2_live = current_entry["path"]
                assert path_v2_live.exists(), "live v2 entry's files should not be deleted"
            finally:
                await svc.close()


class TestCredentialKeyedCache:
    def setup_method(self):
        _reset()

    def _zip_bytes(self, name, data):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(zipfile.ZipInfo(name, date_time=(2026, 7, 1, 7, 5, 0)), data)
        return buf.getvalue()

    @pytest.mark.asyncio
    async def test_different_credentials_produce_separate_cache_entries(self, tmp_path):
        import services.log_service as mod
        # Two DIFFERENT credentials for the same (hostname, log_name) produce TWO downloads.
        zip_data = self._zip_bytes("app.log", b"data\n")
        chunks = [zip_data[i:i + 8] for i in range(0, len(zip_data), 8)]
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            s.log_cache_dir_prefix = "ise-test-"
            s.log_download_max_concurrency = 1
            sess.stream = _fake_stream(chunks)
            svc = mod.LogService()
            await svc.setup()
            try:
                # User A
                with patch("services.log_service.get_per_user_credential", return_value="Basic QWxpY2U6c2VjcmV0"):
                    async with svc.fetch("app", "h") as path_a:
                        assert path_a.exists()
                # User B (different credential)
                with patch("services.log_service.get_per_user_credential", return_value="Basic Qm9iOmh1bnRlcjI="):
                    async with svc.fetch("app", "h") as path_b:
                        assert path_b.exists()
                # Two distinct credentials → two downloads (two cache entries)
                assert sess.stream.calls == 2
                assert len(svc._cache) == 2
            finally:
                await svc.close()

    @pytest.mark.asyncio
    async def test_same_credential_reuses_cache_entry(self, tmp_path):
        import services.log_service as mod
        # The SAME credential across two fetches produces ONE download (reuse).
        zip_data = self._zip_bytes("app.log", b"data\n")
        chunks = [zip_data[i:i + 8] for i in range(0, len(zip_data), 8)]
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            s.log_cache_dir_prefix = "ise-test-"
            s.log_download_max_concurrency = 1
            sess.stream = _fake_stream(chunks)
            svc = mod.LogService()
            await svc.setup()
            try:
                cred = "Basic QWxpY2U6c2VjcmV0"
                with patch("services.log_service.get_per_user_credential", return_value=cred):
                    async with svc.fetch("app", "h") as path_1:
                        assert path_1.exists()
                    async with svc.fetch("app", "h") as path_2:
                        assert path_2.exists()
                # Same credential → reuse → single download
                assert sess.stream.calls == 1
                assert len(svc._cache) == 1
            finally:
                await svc.close()
