# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class NodeStatus(str, Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    INPROGRESS = "InProgress"
    NOTAPPLICABLE = "NotApplicable"
    NOTINSYNC = "NotInSync"
    NOTUPGRADED = "NotUpgraded"
    REGISTRATIONFAILED = "RegistrationFailed"
    REPLICATIONSTOPPED = "ReplicationStopped"

    def __str__(self) -> str:
        return str(self.value)
