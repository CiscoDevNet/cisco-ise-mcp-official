from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.identifier_list import IdentifierList





T = TypeVar("T", bound="IdentifierListResponseEntity")



@_attrs_define
class IdentifierListResponseEntity:
    

    response: IdentifierList
    """ Array of mac identifiers. Each identifier represents an endpoint. """
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.identifier_list import IdentifierList
        response = self.response.to_dict()

        version = self.version


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "response": response,
            "version": version,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identifier_list import IdentifierList
        d = dict(src_dict)
        response = IdentifierList.from_dict(d.pop("response"))




        version = d.pop("version")

        identifier_list_response_entity = cls(
            response=response,
            version=version,
        )


        identifier_list_response_entity.additional_properties = d
        return identifier_list_response_entity

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
