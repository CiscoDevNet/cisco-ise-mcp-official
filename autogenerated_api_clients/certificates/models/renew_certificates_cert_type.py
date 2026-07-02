from enum import Enum

class RenewCertificatesCertType(str, Enum):
    DATAGRID = "DATAGRID"
    IMS = "IMS"
    OCSP = "OCSP"

    def __str__(self) -> str:
        return str(self.value)
