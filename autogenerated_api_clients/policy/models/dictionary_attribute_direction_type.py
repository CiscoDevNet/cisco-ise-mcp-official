# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

class DictionaryAttributeDirectionType(str, Enum):
    BOTH = "BOTH"
    IN = "IN"
    NONE = "NONE"
    OUT = "OUT"

    def __str__(self) -> str:
        return str(self.value)
