from enum import Enum

class UpdateTrustCertRequestCrlDownloadFailureRetriesUnits(str, Enum):
    DAYS = "Days"
    HOURS = "Hours"
    MINUTES = "Minutes"
    WEEKS = "Weeks"

    def __str__(self) -> str:
        return str(self.value)
