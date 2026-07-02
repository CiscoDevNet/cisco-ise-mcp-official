# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest_plugins = ("pytest_asyncio",)

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class TestIseCredentialMiddleware:
    """Tests for IseCredentialMiddleware.on_request."""

    @pytest.mark.asyncio
    async def test_sets_credential_when_header_present(self):
        from utils.ise_credential_middleware import IseCredentialMiddleware
        from clients.request_context import get_per_user_credential

        middleware = IseCredentialMiddleware()

        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Basic dXNlcjpwYXNz"

        mock_context = MagicMock()
        captured = {}

        async def call_next(ctx):
            captured["credential"] = get_per_user_credential()
            return "result"

        with patch("utils.ise_credential_middleware.get_http_request", return_value=mock_request):
            result = await middleware.on_request(mock_context, call_next)

        assert captured["credential"] == "Basic dXNlcjpwYXNz"
        assert result == "result"

    @pytest.mark.asyncio
    async def test_credential_reset_after_request(self):
        from utils.ise_credential_middleware import IseCredentialMiddleware
        from clients.request_context import get_per_user_credential, set_per_user_credential, reset_per_user_credential

        middleware = IseCredentialMiddleware()

        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Basic dXNlcjpwYXNz"

        mock_context = MagicMock()

        async def call_next(ctx):
            return "ok"

        with patch("utils.ise_credential_middleware.get_http_request", return_value=mock_request):
            await middleware.on_request(mock_context, call_next)

        # After the middleware exits, credential should be back to None
        assert get_per_user_credential() is None

    @pytest.mark.asyncio
    async def test_no_header_sets_none(self):
        from utils.ise_credential_middleware import IseCredentialMiddleware
        from clients.request_context import get_per_user_credential

        middleware = IseCredentialMiddleware()

        mock_request = MagicMock()
        mock_request.headers.get.return_value = None

        mock_context = MagicMock()
        captured = {}

        async def call_next(ctx):
            captured["credential"] = get_per_user_credential()
            return "result"

        with patch("utils.ise_credential_middleware.get_http_request", return_value=mock_request):
            await middleware.on_request(mock_context, call_next)

        assert captured["credential"] is None

    @pytest.mark.asyncio
    async def test_no_http_request_sets_none(self):
        """When get_http_request raises (stdio transport), credential is None."""
        from utils.ise_credential_middleware import IseCredentialMiddleware
        from clients.request_context import get_per_user_credential

        middleware = IseCredentialMiddleware()
        mock_context = MagicMock()
        captured = {}

        async def call_next(ctx):
            captured["credential"] = get_per_user_credential()
            return "ok"

        with patch("utils.ise_credential_middleware.get_http_request", side_effect=RuntimeError("no request")):
            await middleware.on_request(mock_context, call_next)

        assert captured["credential"] is None

    @pytest.mark.asyncio
    async def test_credential_reset_even_if_call_next_raises(self):
        """Credential is cleaned up even when the downstream handler raises."""
        from utils.ise_credential_middleware import IseCredentialMiddleware
        from clients.request_context import get_per_user_credential

        middleware = IseCredentialMiddleware()

        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Basic dXNlcjpwYXNz"
        mock_context = MagicMock()

        async def call_next(ctx):
            raise ValueError("boom")

        with patch("utils.ise_credential_middleware.get_http_request", return_value=mock_request):
            with pytest.raises(ValueError, match="boom"):
                await middleware.on_request(mock_context, call_next)

        assert get_per_user_credential() is None
