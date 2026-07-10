from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.dictionary import Dictionary





T = TypeVar("T", bound="DictionaryResponseEntity")



@_attrs_define
class DictionaryResponseEntity:
    

    version: str
    response: Dictionary
    """ Dictionary POST format """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dictionary import Dictionary
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
        from ..models.dictionary import Dictionary
        d = dict(src_dict)
        version = d.pop("version")

        response = Dictionary.from_dict(d.pop("response"))




        dictionary_response_entity = cls(
            version=version,
            response=response,
        )


        dictionary_response_entity.additional_properties = d
        return dictionary_response_entity

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
