# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from tools.base_tool_handler import BaseToolHandler
from clients.client_factory import ClientFactory, ClientName

class PatchAndUpgradeToolHandler(BaseToolHandler):
    """Handler for patch and upgrade-related tools"""

    def __init__(self, client_factory: ClientFactory):
        super().__init__(ClientName.PATCH_AND_UPGRADE, client_factory)



    