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
            svc = mod.LogService()
            await svc.setup()
            assert svc._cache_dir is not None and svc._cache_dir.exists()
            d = svc._cache_dir
            await svc.close()
            assert not d.exists()

    @pytest.mark.asyncio
    async def test_download_extract_returns_raw_bytes(self, tmp_path):
        import services.log_service as mod
        from unittest.mock import AsyncMock, MagicMock
        # Extraction is byte-for-byte: CRLF is preserved (no cleaning pass).
        zip_data = self._zip_bytes("iseLocalStore.log", b"hello\r\nworld\r\n")
        resp = MagicMock()
        resp.status_code = 200
        resp.content = zip_data
        resp.headers = {"ETag": 'W/"1-2"', "Last-Modified": "Wed, 01 Jul 2026 07:05:01 GMT"}
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_dir_prefix = "ise-logs-test-"
            sess.get = AsyncMock(return_value=resp)
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

        resp_v1 = MagicMock(); resp_v1.status_code = 200; resp_v1.content = zip_v1
        resp_v1.headers = {"ETag": '"v1"', "Last-Modified": "Wed, 01 Jul 2026 07:00:00 GMT"}
        resp_v1.raise_for_status = MagicMock()

        resp_v2 = MagicMock(); resp_v2.status_code = 200; resp_v2.content = zip_v2
        resp_v2.headers = {"ETag": '"v2"', "Last-Modified": "Wed, 01 Jul 2026 08:00:00 GMT"}
        resp_v2.raise_for_status = MagicMock()

        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            s.log_cache_dir_prefix = "ise-test-"

            call_count = [0]
            async def mock_get(*args, **kwargs):
                call_count[0] += 1
                return resp_v1 if call_count[0] == 1 else resp_v2
            sess.get = AsyncMock(side_effect=mock_get)

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
        from unittest.mock import AsyncMock, MagicMock
        # Two DIFFERENT credentials for the same (hostname, log_name) produce TWO downloads.
        zip_data = self._zip_bytes("app.log", b"data\n")
        resp = MagicMock()
        resp.status_code = 200
        resp.content = zip_data
        resp.headers = {}
        resp.raise_for_status = MagicMock()
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            s.log_cache_dir_prefix = "ise-test-"
            sess.get = AsyncMock(return_value=resp)
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
                assert sess.get.await_count == 2
                assert len(svc._cache) == 2
            finally:
                await svc.close()

    @pytest.mark.asyncio
    async def test_same_credential_reuses_cache_entry(self, tmp_path):
        import services.log_service as mod
        from unittest.mock import AsyncMock, MagicMock
        # The SAME credential across two fetches produces ONE download (reuse).
        zip_data = self._zip_bytes("app.log", b"data\n")
        resp = MagicMock()
        resp.status_code = 200
        resp.content = zip_data
        resp.headers = {}
        resp.raise_for_status = MagicMock()
        with patch("services.log_service.settings") as s, \
             patch("services.log_service.ise_web_session") as sess:
            s.log_cache_ttl_s = 300.0
            s.ise_ip = "h"; s.api_port = 443
            s.log_cache_dir_prefix = "ise-test-"
            sess.get = AsyncMock(return_value=resp)
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
                assert sess.get.await_count == 1
                assert len(svc._cache) == 1
            finally:
                await svc.close()
