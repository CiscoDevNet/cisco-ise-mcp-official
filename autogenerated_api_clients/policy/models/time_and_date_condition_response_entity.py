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
  from ..models.time_and_date_condition import TimeAndDateCondition





T = TypeVar("T", bound="TimeAndDateConditionResponseEntity")



@_attrs_define
class TimeAndDateConditionResponseEntity:
    """ 
        Example:
            {'version': '1.0.0', 'response': {'conditionType': 'TimeAndDateCondition', 'id':
                '1059b637-f0f4-4bdd-a25f-203da9f96e2a', 'isNegate': False, 'name': 'Time Condition 1', 'description': 'TimeDate
                description', 'hoursRange': {'startTime': '08:00', 'endTime': '10:00'}, 'weekDays': ['Sunday', 'Wednesday'],
                'link': {'rel': 'self', 'href': 'https://{{ISE_IP}}/api/v1/policy/{{protocol}}/time-
                condition/1059b637-f0f4-4bdd-a25f-203da9f96e2a', 'type': 'application/json'}}}

     """

    version: str
    response: TimeAndDateCondition
    """ Condition based on time and date. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.time_and_date_condition import TimeAndDateCondition
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
        from ..models.time_and_date_condition import TimeAndDateCondition
        d = dict(src_dict)
        version = d.pop("version")

        response = TimeAndDateCondition.from_dict(d.pop("response"))




        time_and_date_condition_response_entity = cls(
            version=version,
            response=response,
        )


        time_and_date_condition_response_entity.additional_properties = d
        return time_and_date_condition_response_entity

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
