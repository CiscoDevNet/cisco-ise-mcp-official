# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

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

    async def _run_no_header_and_capture_log(self, *, client_cert_configured, require_per_user_credential):
        """Run on_request with no header under a given settings posture and
        return the logger.info messages emitted."""
        from utils.ise_credential_middleware import IseCredentialMiddleware

        middleware = IseCredentialMiddleware()

        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_context = MagicMock()

        async def call_next(ctx):
            return "ok"

        mock_settings = MagicMock()
        mock_settings.credential_header_name = "X-ISE-Authorization"
        mock_settings.client_cert_configured = client_cert_configured
        mock_settings.require_per_user_credential = require_per_user_credential

        with patch("utils.ise_credential_middleware.settings", mock_settings), \
                patch("utils.ise_credential_middleware.get_http_request", return_value=mock_request), \
                patch("utils.ise_credential_middleware.logger") as mock_logger:
            await middleware.on_request(mock_context, call_next)

        # Reconstruct the fully-formatted message from the (fmt, *args) call.
        assert mock_logger.info.called
        args, _ = mock_logger.info.call_args
        return args[0] % tuple(args[1:])

    @pytest.mark.asyncio
    async def test_no_header_log_reports_client_certificate(self):
        msg = await self._run_no_header_and_capture_log(
            client_cert_configured=True, require_per_user_credential=True
        )
        # Cert wins over require_per_user_credential; must NOT claim SA
        # fallback or refusal.
        assert "client certificate" in msg
        assert "service-account" not in msg
        assert "refuse" not in msg

    @pytest.mark.asyncio
    async def test_no_header_log_reports_refusal(self):
        msg = await self._run_no_header_and_capture_log(
            client_cert_configured=False, require_per_user_credential=True
        )
        assert "refuse" in msg
        assert "ISE_REQUIRE_PER_USER_CREDENTIAL=true" in msg

    @pytest.mark.asyncio
    async def test_no_header_log_reports_service_account(self):
        msg = await self._run_no_header_and_capture_log(
            client_cert_configured=False, require_per_user_credential=False
        )
        assert "service-account" in msg
