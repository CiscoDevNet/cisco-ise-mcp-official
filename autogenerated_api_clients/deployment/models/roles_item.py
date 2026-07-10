from enum import Enum


class RolesItem(str, Enum):
    PRIMARYADMIN = "PrimaryAdmin"
    PRIMARYDEDICATEDMONITORING = "PrimaryDedicatedMonitoring"
    PRIMARYMONITORING = "PrimaryMonitoring"
    SECONDARYADMIN = "SecondaryAdmin"
    SECONDARYDEDICATEDMONITORING = "SecondaryDedicatedMonitoring"
    SECONDARYMONITORING = "SecondaryMonitoring"
    STANDALONE = "Standalone"

    def __str__(self) -> str:
        return str(self.value)
