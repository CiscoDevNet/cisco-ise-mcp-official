from enum import Enum

class GenerateSelfsignedCertRequestExpirationTTLUnit(str, Enum):
    DAYS = "days"
    MONTHS = "months"
    WEEKS = "weeks"
    YEARS = "years"

    def __str__(self) -> str:
        return str(self.value)
