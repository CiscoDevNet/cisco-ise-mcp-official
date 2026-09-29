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
        # Cert authenticates the OpenAPI path (wins over
        # require_per_user_credential); MnT is the documented exception
        # (no cert auth -> SA fallback). Must not claim a refusal.
        assert "client certificate" in msg
        assert "certificate auth" in msg
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


class TestValidationErrorTranslation:
    """FastMCP lets pydantic's ValidationError escape tool-argument validation.

    Unwrapped, its repr reads like an internal crash, so agents retry the same
    bad call instead of correcting it. The middleware must convert it into a
    CLIENT_ERROR that names the offending fields.
    """

    @staticmethod
    def _validation_error(func, **kwargs):
        """Produce a real ValidationError the way FastMCP does.

        FastMCP validates tool arguments against the handler's signature, so
        ``validate_call`` reproduces the exact error `type` values the
        middleware branches on -- notably ``unexpected_keyword_argument``,
        which a plain BaseModel never emits.
        """
        from pydantic import ValidationError, validate_call

        try:
            validate_call(func)(**kwargs)
        except ValidationError as exc:
            return exc
        raise AssertionError("expected validate_call to reject these kwargs")

    async def _run(self, exc, tool_name):
        from fastmcp.exceptions import ToolError
        from utils.ise_credential_middleware import IseCredentialMiddleware

        mock_context = MagicMock()
        mock_context.message.name = tool_name

        async def call_next(ctx):
            raise exc

        with patch("utils.ise_credential_middleware.get_http_request", return_value=None):
            with pytest.raises(ToolError) as excinfo:
                await IseCredentialMiddleware().on_request(mock_context, call_next)
        return str(excinfo.value)

    @pytest.mark.asyncio
    async def test_unexpected_keyword_names_the_offending_params(self):
        def ise_investigate_aaa_failure(mac_address: str = None, username: str = None):
            ...

        exc = self._validation_error(
            ise_investigate_aaa_failure, nas_ip_address="10.0.0.1"
        )
        msg = await self._run(exc, "ise_investigate_aaa_failure")

        assert "Unsupported parameter(s)" in msg
        assert "nas_ip_address" in msg
        # Bespoke hint for this tool's narrow parameter surface.
        assert "mac_address and username" in msg

    @pytest.mark.asyncio
    async def test_unexpected_keyword_without_hint_omits_tool_advice(self):
        def active_sessions_search(username: str = None):
            ...

        exc = self._validation_error(active_sessions_search, bogus=1)
        msg = await self._run(exc, "active_sessions_search")

        assert "Unsupported parameter(s): bogus." in msg
        assert "mac_address and username" not in msg

    @pytest.mark.asyncio
    async def test_type_error_reports_field_reason_and_value(self):
        def active_sessions_search(limit: int = 10):
            ...

        exc = self._validation_error(active_sessions_search, limit="not-a-number")
        msg = await self._run(exc, "active_sessions_search")

        assert "Invalid tool input" in msg
        assert "limit" in msg
        assert "not-a-number" in msg

    @pytest.mark.asyncio
    async def test_credential_still_reset_when_validation_fails(self):
        from clients.request_context import get_per_user_credential

        def active_sessions_search(limit: int = 10):
            ...

        exc = self._validation_error(active_sessions_search, limit="x")
        await self._run(exc, "active_sessions_search")

        assert get_per_user_credential() is None
