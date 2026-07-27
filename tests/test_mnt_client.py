# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


def _reset_mnt_singleton():
    """Force MNTClient to re-initialise between tests."""
    import clients.mnt_client as mod
    mod.MNTClient._instance = None
    mod.MNTClient._initialized = False


class TestMNTClientSetup:
    def setup_method(self):
        _reset_mnt_singleton()

    @pytest.mark.asyncio
    async def test_setup_creates_client_with_service_account(self):
        import clients.mnt_client as mod
        with patch("clients.mnt_client.settings") as mock_settings, \
             patch("clients.mnt_client.build_ssl_context", return_value=None):
            mock_settings.api_port = 443
            mock_settings.api_username = "admin"
            mock_settings.api_pwd.get_secret_value.return_value = "secret"
            mock_settings.connect_timeout_s = 5.0
            mock_settings.read_timeout_s = 30.0
            mock_settings.write_timeout_s = 10.0
            mock_settings.pool_timeout_s = 5.0
            mock_settings.credential_header_name = "X-ISE-Authorization"
            client = mod.MNTClient()
            await client.setup()
            assert client._client is not None
            await client.close()

    @pytest.mark.asyncio
    async def test_setup_idempotent(self):
        import clients.mnt_client as mod
        with patch("clients.mnt_client.settings") as mock_settings, \
             patch("clients.mnt_client.build_ssl_context", return_value=None):
            mock_settings.api_port = 443
            mock_settings.api_username = "admin"
            mock_settings.api_pwd.get_secret_value.return_value = "secret"
            mock_settings.connect_timeout_s = 5.0
            mock_settings.read_timeout_s = 30.0
            mock_settings.write_timeout_s = 10.0
            mock_settings.pool_timeout_s = 5.0
            mock_settings.credential_header_name = "X-ISE-Authorization"
            client = mod.MNTClient()
            await client.setup()
            first_client = client._client
            await client.setup()  # second call should be no-op
            assert client._client is first_client
            await client.close()

    @pytest.mark.asyncio
    async def test_setup_without_service_account(self):
        import clients.mnt_client as mod
        with patch("clients.mnt_client.settings") as mock_settings, \
             patch("clients.mnt_client.build_ssl_context", return_value=None):
            mock_settings.api_port = 443
            mock_settings.api_username = None
            mock_settings.api_pwd = None
            mock_settings.connect_timeout_s = 5.0
            mock_settings.read_timeout_s = 30.0
            mock_settings.write_timeout_s = 10.0
            mock_settings.pool_timeout_s = 5.0
            mock_settings.credential_header_name = "X-ISE-Authorization"
            client = mod.MNTClient()
            await client.setup()
            assert client._client is not None
            await client.close()


class TestMNTClientResolveAuth:
    def setup_method(self):
        _reset_mnt_singleton()

    def test_per_user_credential_used(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            token = set_per_user_credential("Basic dXNlcjpwYXNz")
            try:
                client = mod.MNTClient()
                kwargs, label = client._resolve_per_call_auth()
                assert label == "per_user_credential"
                assert kwargs["headers"]["Authorization"] == "Basic dXNlcjpwYXNz"
            finally:
                reset_per_user_credential(token)

    def test_service_account_fallback(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.client_cert_configured = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                kwargs, label = client._resolve_per_call_auth()
                assert label == "service_account"
                assert kwargs == {}
            finally:
                reset_per_user_credential(token)

    def test_require_per_user_raises_when_absent(self):
        import clients.mnt_client as mod
        from clients.exceptions import MissingIseCredentialError
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = True
            mock_settings.client_cert_configured = False
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                with pytest.raises(MissingIseCredentialError):
                    client._resolve_per_call_auth()
            finally:
                reset_per_user_credential(token)

    def test_no_sa_creds_raises(self):
        import clients.mnt_client as mod
        from clients.exceptions import MissingServiceAccountError
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.client_cert_configured = False
            mock_settings.api_username = None
            mock_settings.api_pwd = None
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                with pytest.raises(MissingServiceAccountError):
                    client._resolve_per_call_auth()
            finally:
                reset_per_user_credential(token)

    def test_client_cert_mode_no_auth_header(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.client_cert_configured = True
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                kwargs, label = client._resolve_per_call_auth()
                assert label == "client_certificate"
                assert "headers" not in kwargs or "Authorization" not in kwargs.get("headers", {})
                # A no-op auth flow neutralises client-level BasicAuth.
                assert isinstance(kwargs["auth"], mod._NoOpAuth)
            finally:
                reset_per_user_credential(token)

    def test_per_user_wins_over_client_cert(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.client_cert_configured = True
            token = set_per_user_credential("Basic dXNlcjpwYXNz")
            try:
                client = mod.MNTClient()
                kwargs, label = client._resolve_per_call_auth()
                assert label == "per_user_credential"
                assert kwargs["headers"]["Authorization"] == "Basic dXNlcjpwYXNz"
            finally:
                reset_per_user_credential(token)


class TestMNTClientGet:
    def setup_method(self):
        _reset_mnt_singleton()

    def _make_async_client_mock(self, status_code=200, text="<ok/>"):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.text = text
        mock_response.raise_for_status = MagicMock()
        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(return_value=mock_response)
        return mock_httpx, mock_response

    @pytest.mark.asyncio
    async def test_invalid_endpoint_raises(self):
        import clients.mnt_client as mod
        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            client = mod.MNTClient()
            with pytest.raises(ValueError):
                await client.get("/bad/endpoint")

    @pytest.mark.asyncio
    async def test_get_returns_response(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_httpx, mock_response = self._make_async_client_mock()

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                client._discovery_succeeded = True  # skip discovery
                result = await client.get("Session/ActiveList")
                assert result is mock_response
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_http_status_error_propagated(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_request = MagicMock()
        mock_error_response = MagicMock()
        mock_error_response.status_code = 401
        mock_error_response.text = "Unauthorized"

        http_error = httpx.HTTPStatusError("401", request=mock_request, response=mock_error_response)

        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(side_effect=http_error)

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                client._discovery_succeeded = True
                with pytest.raises(httpx.HTTPStatusError):
                    await client.get("Session/ActiveList")
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_request_error_propagated(self):
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                client._discovery_succeeded = True
                with pytest.raises(httpx.ConnectError):
                    await client.get("Session/ActiveList")
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_get_client_raises_when_not_setup(self):
        import clients.mnt_client as mod
        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            client = mod.MNTClient()
            client._client = None
            with pytest.raises(RuntimeError, match="not initialized"):
                await client._get_client()

    @pytest.mark.asyncio
    async def test_close_closes_client(self):
        import clients.mnt_client as mod
        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            client = mod.MNTClient()
            mock_httpx = MagicMock(spec=httpx.AsyncClient)
            mock_httpx.is_closed = False
            mock_httpx.aclose = AsyncMock()
            client._client = mock_httpx
            await client.close()
            mock_httpx.aclose.assert_called_once()


class TestMNTClientDiscovery:
    def setup_method(self):
        _reset_mnt_singleton()

    @pytest.mark.asyncio
    async def test_discovery_standalone_latches_pan_url(self):
        """Empty 'response' list means standalone: keep PAN URL and latch success."""
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"response": []}

        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(return_value=mock_response)

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                await client._discover_mnt_fqdn()
                assert client._discovery_succeeded is True
                assert client._mnt_fqdn is None
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_discovery_pins_fqdn(self):
        """A valid FQDN in the deployment response pins base_url to that host."""
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "response": [{"fqdn": "mnt-node.example.com"}]
        }

        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(return_value=mock_response)

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                await client._discover_mnt_fqdn()
                assert client._discovery_succeeded is True
                assert client._mnt_fqdn == "mnt-node.example.com"
                assert "mnt-node.example.com" in client.base_url
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_discovery_network_error_does_not_latch(self):
        """Network error: discovery flag stays False so next call retries."""
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(side_effect=httpx.ConnectError("timeout"))

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                await client._discover_mnt_fqdn()
                assert client._discovery_succeeded is False
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_discovery_invalid_fqdn_does_not_latch(self):
        """A dangerous FQDN fails allow-list: flag stays False."""
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "response": [{"fqdn": "../../etc/passwd"}]
        }

        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(return_value=mock_response)

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                await client._discover_mnt_fqdn()
                assert client._discovery_succeeded is False
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_discovery_missing_fqdn_field(self):
        """Node dict with no 'fqdn': flag stays False."""
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"response": [{"hostname": "node1"}]}

        mock_httpx = MagicMock(spec=httpx.AsyncClient)
        mock_httpx.is_closed = False
        mock_httpx.get = AsyncMock(return_value=mock_response)

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            mock_settings.require_per_user_credential = False
            mock_settings.api_username = "admin"
            mock_settings.api_pwd = MagicMock()
            mock_settings.credential_header_name = "X-ISE-Authorization"
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._client = mock_httpx
                await client._discover_mnt_fqdn()
                assert client._discovery_succeeded is False
            finally:
                reset_per_user_credential(token)

    @pytest.mark.asyncio
    async def test_ensure_mnt_target_skips_after_success(self):
        """After discovery is latched, _ensure_mnt_target is a no-op."""
        import clients.mnt_client as mod
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            token = set_per_user_credential(None)
            try:
                client = mod.MNTClient()
                client._discovery_succeeded = True
                discover_called = []

                async def fake_discover():
                    discover_called.append(True)

                client._discover_mnt_fqdn = fake_discover
                await client._ensure_mnt_target()
                assert discover_called == []
            finally:
                reset_per_user_credential(token)


class TestMNTClientGetStream:
    def setup_method(self):
        _reset_mnt_singleton()

    @pytest.mark.asyncio
    async def test_get_stream_yields_streaming_response(self, monkeypatch):
        import contextlib
        from clients.mnt_client import MNTClient
        from clients.request_context import set_per_user_credential, reset_per_user_credential

        with patch("clients.mnt_client.settings") as mock_settings:
            mock_settings.api_port = 443
            token = set_per_user_credential(None)
            try:
                client = MNTClient()

                # Skip discovery so the test targets streaming only.
                async def _no_discovery():
                    client._discovery_succeeded = True
                monkeypatch.setattr(client, "_ensure_mnt_target", _no_discovery)

                chunks = [b"<activeList>", b"</activeList>"]

                class FakeResponse:
                    status_code = 200
                    def raise_for_status(self):
                        return None
                    async def aiter_bytes(self):
                        for c in chunks:
                            yield c

                @contextlib.asynccontextmanager
                async def fake_stream(method, url, **kwargs):
                    assert method == "GET"
                    yield FakeResponse()

                fake_client = type("C", (), {})()
                fake_client.is_closed = False
                fake_client.stream = fake_stream
                monkeypatch.setattr(client, "_get_client", AsyncMock(return_value=fake_client))
                monkeypatch.setattr(client, "_resolve_per_call_auth", lambda: ({}, "service_account"))

                got = []
                async with client.get_stream("Session/AuthList/x/null") as resp:
                    async for c in resp.aiter_bytes():
                        got.append(c)
                assert got == chunks
            finally:
                reset_per_user_credential(token)
