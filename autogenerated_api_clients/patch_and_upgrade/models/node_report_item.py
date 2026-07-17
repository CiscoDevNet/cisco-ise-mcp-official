# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="NodeReportItem")



@_attrs_define
class NodeReportItem:
    

    hostname: str
    new_personas: str
    old_personas: str
    role: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        hostname = self.hostname

        new_personas = self.new_personas

        old_personas = self.old_personas

        role = self.role


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "Hostname": hostname,
            "New Personas": new_personas,
            "Old Personas": old_personas,
            "Role": role,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hostname = d.pop("Hostname")

        new_personas = d.pop("New Personas")

        old_personas = d.pop("Old Personas")

        role = d.pop("Role")

        node_report_item = cls(
            hostname=hostname,
            new_personas=new_personas,
            old_personas=old_personas,
            role=role,
        )


        node_report_item.additional_properties = d
        return node_report_item

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
