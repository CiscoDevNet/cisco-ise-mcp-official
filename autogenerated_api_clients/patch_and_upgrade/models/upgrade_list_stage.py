# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.upgrade_stage import UpgradeStage





T = TypeVar("T", bound="UpgradeListStage")



@_attrs_define
class UpgradeListStage:
    

    response: Union[Unset, list['UpgradeStage']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.upgrade_stage import UpgradeStage
        response: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.response, Unset):
            response = []
            for response_item_data in self.response:
                response_item = response_item_data.to_dict()
                response.append(response_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if response is not UNSET:
            field_dict["response"] = response

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.upgrade_stage import UpgradeStage
        d = dict(src_dict)
        response = []
        _response = d.pop("response", UNSET)
        for response_item_data in (_response or []):
            response_item = UpgradeStage.from_dict(response_item_data)



            response.append(response_item)


        upgrade_list_stage = cls(
            response=response,
        )


        upgrade_list_stage.additional_properties = d
        return upgrade_list_stage

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
