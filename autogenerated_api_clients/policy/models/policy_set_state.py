# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

class PolicySetState(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    MONITOR = "monitor"

    def __str__(self) -> str:
        return str(self.value)
