from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.patch import Patch





T = TypeVar("T", bound="NodePatchList")



@_attrs_define
class NodePatchList:
    

    node: Union[Unset, str] = UNSET
    """ ISE node name. """
    patch_versions: Union[Unset, list['Patch']] = UNSET
    """ Array of objects, each object containing patch version and installed date. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.patch import Patch
        node = self.node

        patch_versions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.patch_versions, Unset):
            patch_versions = []
            for patch_versions_item_data in self.patch_versions:
                patch_versions_item = patch_versions_item_data.to_dict()
                patch_versions.append(patch_versions_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if node is not UNSET:
            field_dict["node"] = node
        if patch_versions is not UNSET:
            field_dict["patchVersions"] = patch_versions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch import Patch
        d = dict(src_dict)
        node = d.pop("node", UNSET)

        patch_versions = []
        _patch_versions = d.pop("patchVersions", UNSET)
        for patch_versions_item_data in (_patch_versions or []):
            patch_versions_item = Patch.from_dict(patch_versions_item_data)



            patch_versions.append(patch_versions_item)


        node_patch_list = cls(
            node=node,
            patch_versions=patch_versions,
        )


        node_patch_list.additional_properties = d
        return node_patch_list

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
