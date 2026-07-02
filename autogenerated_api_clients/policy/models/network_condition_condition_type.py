from enum import Enum

class NetworkConditionConditionType(str, Enum):
    DEVICECONDITION = "DeviceCondition"
    DEVICEPORTCONDITION = "DevicePortCondition"
    ENDSTATIONCONDITION = "EndstationCondition"

    def __str__(self) -> str:
        return str(self.value)
