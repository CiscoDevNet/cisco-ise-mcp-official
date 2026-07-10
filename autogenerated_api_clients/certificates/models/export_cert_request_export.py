from enum import Enum

class ExportCertRequestExport(str, Enum):
    CERTIFICATE = "CERTIFICATE"
    CERTIFICATE_WITH_PRIVATE_KEY = "CERTIFICATE_WITH_PRIVATE_KEY"

    def __str__(self) -> str:
        return str(self.value)
