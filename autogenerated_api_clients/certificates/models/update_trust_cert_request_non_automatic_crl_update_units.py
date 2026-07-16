# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

class UpdateTrustCertRequestNonAutomaticCRLUpdateUnits(str, Enum):
    DAYS = "Days"
    HOURS = "Hours"
    MINUTES = "Minutes"
    WEEKS = "Weeks"

    def __str__(self) -> str:
        return str(self.value)
