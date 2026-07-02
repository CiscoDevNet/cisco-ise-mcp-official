from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PatchRollbackVersionResponse")



@_attrs_define
class PatchRollbackVersionResponse:
    

    current_patch_version: Union[Unset, str] = UNSET
    current_release_version: Union[Unset, str] = UNSET
    previous_installed_patch_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        current_patch_version = self.current_patch_version

        current_release_version = self.current_release_version

        previous_installed_patch_version = self.previous_installed_patch_version


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if current_patch_version is not UNSET:
            field_dict["currentPatchVersion"] = current_patch_version
        if current_release_version is not UNSET:
            field_dict["currentReleaseVersion"] = current_release_version
        if previous_installed_patch_version is not UNSET:
            field_dict["previousInstalledPatchVersion"] = previous_installed_patch_version

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_patch_version = d.pop("currentPatchVersion", UNSET)

        current_release_version = d.pop("currentReleaseVersion", UNSET)

        previous_installed_patch_version = d.pop("previousInstalledPatchVersion", UNSET)

        patch_rollback_version_response = cls(
            current_patch_version=current_patch_version,
            current_release_version=current_release_version,
            previous_installed_patch_version=previous_installed_patch_version,
        )


        patch_rollback_version_response.additional_properties = d
        return patch_rollback_version_response

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
