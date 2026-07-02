from tools.base_tool_handler import BaseToolHandler
from clients.client_factory import ClientFactory, ClientName

class PatchAndUpgradeToolHandler(BaseToolHandler):
    """Handler for patch and upgrade-related tools"""

    def __init__(self, client_factory: ClientFactory):
        super().__init__(ClientName.PATCH_AND_UPGRADE, client_factory)



    