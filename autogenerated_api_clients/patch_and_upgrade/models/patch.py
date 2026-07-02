from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="Patch")



@_attrs_define
class Patch:
    

    install_date: Union[Unset, str] = UNSET
    """ Date of patch installation. """
    patch_number: Union[Unset, int] = UNSET
    """ Patch version number. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        install_date = self.install_date

        patch_number = self.patch_number


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if install_date is not UNSET:
            field_dict["installDate"] = install_date
        if patch_number is not UNSET:
            field_dict["patchNumber"] = patch_number

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        install_date = d.pop("installDate", UNSET)

        patch_number = d.pop("patchNumber", UNSET)

        patch = cls(
            install_date=install_date,
            patch_number=patch_number,
        )


        patch.additional_properties = d
        return patch

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
