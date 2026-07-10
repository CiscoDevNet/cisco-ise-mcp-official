from enum import Enum

class SuppressedEndpointState(str, Enum):
    REJECTED = "REJECTED"
    RELEASED = "RELEASED"
    SUPPRESSED = "SUPPRESSED"

    def __str__(self) -> str:
        return str(self.value)
