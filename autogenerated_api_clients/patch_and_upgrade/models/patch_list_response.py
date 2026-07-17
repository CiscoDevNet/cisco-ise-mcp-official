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
  from ..models.node_patch_list import NodePatchList





T = TypeVar("T", bound="PatchListResponse")



@_attrs_define
class PatchListResponse:
    

    ise_version: Union[Unset, str] = UNSET
    """ ISE node version. """
    patch_list: Union[Unset, list['NodePatchList']] = UNSET
    """ Array of objects, each object containing  hostname and patch version numbers and installed dates. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.node_patch_list import NodePatchList
        ise_version = self.ise_version

        patch_list: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.patch_list, Unset):
            patch_list = []
            for patch_list_item_data in self.patch_list:
                patch_list_item = patch_list_item_data.to_dict()
                patch_list.append(patch_list_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if ise_version is not UNSET:
            field_dict["iseVersion"] = ise_version
        if patch_list is not UNSET:
            field_dict["patchList"] = patch_list

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.node_patch_list import NodePatchList
        d = dict(src_dict)
        ise_version = d.pop("iseVersion", UNSET)

        patch_list = []
        _patch_list = d.pop("patchList", UNSET)
        for patch_list_item_data in (_patch_list or []):
            patch_list_item = NodePatchList.from_dict(patch_list_item_data)



            patch_list.append(patch_list_item)


        patch_list_response = cls(
            ise_version=ise_version,
            patch_list=patch_list,
        )


        patch_list_response.additional_properties = d
        return patch_list_response

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
