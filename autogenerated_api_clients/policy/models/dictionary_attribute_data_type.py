# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

class DictionaryAttributeDataType(str, Enum):
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    FLOAT = "FLOAT"
    INT = "INT"
    IP = "IP"
    IPV4 = "IPV4"
    IPV6 = "IPV6"
    IPV6INTERFACE = "IPV6INTERFACE"
    IPV6PREFIX = "IPV6PREFIX"
    LONG = "LONG"
    OCTET_STRING = "OCTET_STRING"
    STRING = "STRING"
    UINT64 = "UINT64"
    UNIT32 = "UNIT32"

    def __str__(self) -> str:
        return str(self.value)
