# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Tests for thin tool handlers that have 0% coverage."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


class TestEndpointsToolHandler:
    def _make_handler(self):
        from tools.endpoints_tool_handler import EndpointsToolHandler
        mock_factory = MagicMock()
        mock_factory.get_client.return_value = MagicMock()
        return EndpointsToolHandler(mock_factory)

    def test_instantiation(self):
        from tools.endpoints_tool_handler import EndpointsToolHandler
        from clients.client_factory import ClientName
        handler = self._make_handler()
        assert handler.client_name == ClientName.ENDPOINTS

    @pytest.mark.asyncio
    async def test_get_rejected_endpoints_returns_list(self):
        handler = self._make_handler()
        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"response": [{"mac": "AA:BB:CC:DD:EE:FF"}]}
            result = await handler.get_rejected_endpoints()
        assert result == [{"mac": "AA:BB:CC:DD:EE:FF"}]

    @pytest.mark.asyncio
    async def test_get_rejected_endpoints_empty(self):
        handler = self._make_handler()
        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {}
            result = await handler.get_rejected_endpoints()
        assert result == []


class TestPatchAndUpgradeToolHandler:
    def test_instantiation(self):
        from tools.patch_and_upgrade_tool_handler import PatchAndUpgradeToolHandler
        from clients.client_factory import ClientName
        mock_factory = MagicMock()
        mock_factory.get_client.return_value = MagicMock()
        handler = PatchAndUpgradeToolHandler(mock_factory)
        assert handler.client_name == ClientName.PATCH_AND_UPGRADE
