# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.rule_mfa import RuleMfa





T = TypeVar("T", bound="MfaRuleResponseEntity")



@_attrs_define
class MfaRuleResponseEntity:
    """ 
        Example:
            {'version': '1.0.0', 'response': {'rule': {'condition': {'conditionType': 'ConditionAttributes', 'isNegate':
                False, 'dictionaryName': 'Network Access', 'attributeName': 'Device IP Address', 'operator': 'ipEquals',
                'attributeValue': '10.0.10.0'}, 'default': False, 'hitCounts': 2, 'id': 'd82952cb-b901-4b09-b363-5ebf39bdbaf9',
                'name': 'MyRuleName_1', 'rank': 1, 'state': 'enabled'}, 'mfaConnectionName': 'Connection Name',
                'mfaResultAction': 'ACCEPT', 'mfaFailAction': 'REJECT', 'link': {'href':
                'https://{{ISE_IP}}/api/v1/policy/{{protocol}}/policy-set/{{policy-
                id}}/mfa/d82952cb-b901-4b09-b363-5ebf39bdbaf9', 'rel': 'self', 'type': 'application/json'}}}

     """

    version: str
    response: RuleMfa
    """ Rule for MFA in Network Access/Device Admin """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_mfa import RuleMfa
        version = self.version

        response = self.response.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "version": version,
            "response": response,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_mfa import RuleMfa
        d = dict(src_dict)
        version = d.pop("version")

        response = RuleMfa.from_dict(d.pop("response"))




        mfa_rule_response_entity = cls(
            version=version,
            response=response,
        )


        mfa_rule_response_entity.additional_properties = d
        return mfa_rule_response_entity

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
