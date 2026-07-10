from enum import Enum

class CSRRequestKeyLength(str, Enum):
    VALUE_0 = "1024"
    VALUE_1 = "2048"
    VALUE_2 = "256"
    VALUE_3 = "384"
    VALUE_4 = "4096"
    VALUE_5 = "512"

    def __str__(self) -> str:
        return str(self.value)
