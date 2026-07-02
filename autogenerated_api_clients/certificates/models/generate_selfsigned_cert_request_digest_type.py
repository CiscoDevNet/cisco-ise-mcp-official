from enum import Enum

class GenerateSelfsignedCertRequestDigestType(str, Enum):
    SHA_256 = "SHA-256"
    SHA_384 = "SHA-384"
    SHA_512 = "SHA-512"

    def __str__(self) -> str:
        return str(self.value)
