from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.dictionary_attribute_data_type import DictionaryAttributeDataType
from ..models.dictionary_attribute_direction_type import DictionaryAttributeDirectionType
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.dictionary_attribute_allowed_values_item import DictionaryAttributeAllowedValuesItem





T = TypeVar("T", bound="DictionaryAttribute")



@_attrs_define
class DictionaryAttribute:
    """ Dictionary Attribute format

     """

    name: str
    """ The dictionary attribute's name """
    internal_name: str
    """ the internal name of the dictionary attribute """
    data_type: DictionaryAttributeDataType
    """ the data type for the dictionary attribute """
    id: UUID | Unset = UNSET
    """ Identifier for the dictionary attribute """
    direction_type: DictionaryAttributeDirectionType | Unset = UNSET
    """ the direction for the useage of the dictionary attribute """
    description: str | Unset = UNSET
    """ The description of the Dictionary attribute """
    dictionary_name: str | Unset = UNSET
    """ the name of the dictionary which the dictionary attribute belongs to """
    allowed_values: list[DictionaryAttributeAllowedValuesItem] | Unset = UNSET
    """ all of the allowed values for the dictionary attribute """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dictionary_attribute_allowed_values_item import DictionaryAttributeAllowedValuesItem
        name = self.name

        internal_name = self.internal_name

        data_type = self.data_type.value

        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        direction_type: str | Unset = UNSET
        if not isinstance(self.direction_type, Unset):
            direction_type = self.direction_type.value


        description = self.description

        dictionary_name = self.dictionary_name

        allowed_values: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.allowed_values, Unset):
            allowed_values = []
            for allowed_values_item_data in self.allowed_values:
                allowed_values_item = allowed_values_item_data.to_dict()
                allowed_values.append(allowed_values_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "internalName": internal_name,
            "dataType": data_type,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if direction_type is not UNSET:
            field_dict["directionType"] = direction_type
        if description is not UNSET:
            field_dict["description"] = description
        if dictionary_name is not UNSET:
            field_dict["dictionaryName"] = dictionary_name
        if allowed_values is not UNSET:
            field_dict["allowedValues"] = allowed_values

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dictionary_attribute_allowed_values_item import DictionaryAttributeAllowedValuesItem
        d = dict(src_dict)
        name = d.pop("name")

        internal_name = d.pop("internalName")

        data_type = DictionaryAttributeDataType(d.pop("dataType"))




        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = UUID(_id)




        _direction_type = d.pop("directionType", UNSET)
        direction_type: DictionaryAttributeDirectionType | Unset
        if isinstance(_direction_type,  Unset):
            direction_type = UNSET
        else:
            direction_type = DictionaryAttributeDirectionType(_direction_type)




        description = d.pop("description", UNSET)

        dictionary_name = d.pop("dictionaryName", UNSET)

        _allowed_values = d.pop("allowedValues", UNSET)
        allowed_values: list[DictionaryAttributeAllowedValuesItem] | Unset = UNSET
        if _allowed_values is not UNSET:
            allowed_values = []
            for allowed_values_item_data in _allowed_values:
                allowed_values_item = DictionaryAttributeAllowedValuesItem.from_dict(allowed_values_item_data)



                allowed_values.append(allowed_values_item)


        dictionary_attribute = cls(
            name=name,
            internal_name=internal_name,
            data_type=data_type,
            id=id,
            direction_type=direction_type,
            description=description,
            dictionary_name=dictionary_name,
            allowed_values=allowed_values,
        )


        dictionary_attribute.additional_properties = d
        return dictionary_attribute

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
