# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

class GenerateSelfsignedCertRequestKeyType(str, Enum):
    ECDSA = "ECDSA"
    RSA = "RSA"

    def __str__(self) -> str:
        return str(self.value)
