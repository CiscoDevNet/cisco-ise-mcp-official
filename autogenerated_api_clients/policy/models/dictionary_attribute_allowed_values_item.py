from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="DictionaryAttributeAllowedValuesItem")



@_attrs_define
class DictionaryAttributeAllowedValuesItem:
    

    key: str
    value: str
    is_default: bool | Unset = False
    """ true if this key value is the default between the allowed values of the dictionary attribute """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        key = self.key

        value = self.value

        is_default = self.is_default


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "key": key,
            "value": value,
        })
        if is_default is not UNSET:
            field_dict["isDefault"] = is_default

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key = d.pop("key")

        value = d.pop("value")

        is_default = d.pop("isDefault", UNSET)

        dictionary_attribute_allowed_values_item = cls(
            key=key,
            value=value,
            is_default=is_default,
        )


        dictionary_attribute_allowed_values_item.additional_properties = d
        return dictionary_attribute_allowed_values_item

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
