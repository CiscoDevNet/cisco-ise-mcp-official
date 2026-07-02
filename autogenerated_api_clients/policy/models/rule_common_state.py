from enum import Enum

class RuleCommonState(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    MONITOR = "monitor"

    def __str__(self) -> str:
        return str(self.value)
