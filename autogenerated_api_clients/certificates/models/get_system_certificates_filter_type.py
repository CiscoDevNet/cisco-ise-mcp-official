from enum import Enum

class GetSystemCertificatesFilterType(str, Enum):
    AND = "AND"
    OR = "OR"

    def __str__(self) -> str:
        return str(self.value)
