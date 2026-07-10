from enum import Enum

class PolicySetState(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    MONITOR = "monitor"

    def __str__(self) -> str:
        return str(self.value)
