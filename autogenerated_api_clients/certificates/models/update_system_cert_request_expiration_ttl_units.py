from enum import Enum

class UpdateSystemCertRequestExpirationTTLUnits(str, Enum):
    DAYS = "days"
    MONTHS = "months"
    WEEKS = "weeks"
    YEARS = "years"

    def __str__(self) -> str:
        return str(self.value)
