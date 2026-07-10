from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.condition import Condition





T = TypeVar("T", bound="LibraryConditionListResponseEntity")



@_attrs_define
class LibraryConditionListResponseEntity:
    

    version: str
    response: list[Condition]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.condition import Condition
        version = self.version

        response = []
        for response_item_data in self.response:
            response_item = response_item_data.to_dict()
            response.append(response_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "version": version,
            "response": response,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.condition import Condition
        d = dict(src_dict)
        version = d.pop("version")

        response = []
        _response = d.pop("response")
        for response_item_data in (_response):
            response_item = Condition.from_dict(response_item_data)



            response.append(response_item)


        library_condition_list_response_entity = cls(
            version=version,
            response=response,
        )


        library_condition_list_response_entity.additional_properties = d
        return library_condition_list_response_entity

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
