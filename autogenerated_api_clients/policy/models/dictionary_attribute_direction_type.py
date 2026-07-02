from enum import Enum

class DictionaryAttributeDirectionType(str, Enum):
    BOTH = "BOTH"
    IN = "IN"
    NONE = "NONE"
    OUT = "OUT"

    def __str__(self) -> str:
        return str(self.value)
