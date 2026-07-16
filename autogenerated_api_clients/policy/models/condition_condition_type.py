# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

class ConditionConditionType(str, Enum):
    CONDITIONANDBLOCK = "ConditionAndBlock"
    CONDITIONATTRIBUTES = "ConditionAttributes"
    CONDITIONORBLOCK = "ConditionOrBlock"
    CONDITIONREFERENCE = "ConditionReference"
    LIBRARYCONDITIONANDBLOCK = "LibraryConditionAndBlock"
    LIBRARYCONDITIONATTRIBUTES = "LibraryConditionAttributes"
    LIBRARYCONDITIONORBLOCK = "LibraryConditionOrBlock"
    TIMEANDDATECONDITION = "TimeAndDateCondition"

    def __str__(self) -> str:
        return str(self.value)
