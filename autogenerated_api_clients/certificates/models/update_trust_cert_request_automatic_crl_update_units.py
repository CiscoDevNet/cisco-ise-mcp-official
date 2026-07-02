from enum import Enum

class UpdateTrustCertRequestAutomaticCRLUpdateUnits(str, Enum):
    DAYS = "Days"
    HOURS = "Hours"
    MINUTES = "Minutes"
    WEEKS = "Weeks"

    def __str__(self) -> str:
        return str(self.value)
