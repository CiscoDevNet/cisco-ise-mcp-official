from enum import Enum

class ServiceNameServiceType(str, Enum):
    ALLOWEDPROTOCOLS = "allowedProtocols"
    SERVERSEQUENCE = "serverSequence"

    def __str__(self) -> str:
        return str(self.value)
