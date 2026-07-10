from enum import Enum

class CSRRequestKeyType(str, Enum):
    ECDSA = "ECDSA"
    RSA = "RSA"

    def __str__(self) -> str:
        return str(self.value)
