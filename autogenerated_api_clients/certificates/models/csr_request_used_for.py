# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

class CSRRequestUsedFor(str, Enum):
    ADMIN = "ADMIN"
    DTLS_AUTH = "DTLS-AUTH"
    EAP_AUTH = "EAP-AUTH"
    IMS = "IMS"
    MULTI_USE = "MULTI-USE"
    PORTAL = "PORTAL"
    PXGRID = "PXGRID"
    SAML = "SAML"
    TACACS = "TACACS"

    def __str__(self) -> str:
        return str(self.value)
