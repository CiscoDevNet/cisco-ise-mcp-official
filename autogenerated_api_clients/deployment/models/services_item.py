# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class ServicesItem(str, Enum):
    DEVICEADMIN = "DeviceAdmin"
    PASSIVEIDENTITY = "PassiveIdentity"
    PROFILER = "Profiler"
    PXGRID = "pxGrid"
    PXGRIDCLOUD = "pxGridCloud"
    SESSION = "Session"
    SXP = "SXP"
    TC_NAC = "TC-NAC"

    def __str__(self) -> str:
        return str(self.value)
