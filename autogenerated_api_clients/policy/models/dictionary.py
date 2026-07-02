from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.dictionary_dictionary_attr_type import DictionaryDictionaryAttrType
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.link import Link





T = TypeVar("T", bound="Dictionary")



@_attrs_define
class Dictionary:
    """ Dictionary POST format

     """

    name: str
    """ The dictionary name """
    version: str
    """ The dictionary version """
    dictionary_attr_type: DictionaryDictionaryAttrType
    """ The dictionary attribute type """
    id: UUID | Unset = UNSET
    """ Identifier for the dictionary """
    description: str | Unset = UNSET
    """ The description of the Dictionary """
    link: Link | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        name = self.name

        version = self.version

        dictionary_attr_type = self.dictionary_attr_type.value

        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        description = self.description

        link: dict[str, Any] | Unset = UNSET
        if not isinstance(self.link, Unset):
            link = self.link.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "version": version,
            "dictionaryAttrType": dictionary_attr_type,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if link is not UNSET:
            field_dict["link"] = link

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        d = dict(src_dict)
        name = d.pop("name")

        version = d.pop("version")

        dictionary_attr_type = DictionaryDictionaryAttrType(d.pop("dictionaryAttrType"))




        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = UUID(_id)




        description = d.pop("description", UNSET)

        _link = d.pop("link", UNSET)
        link: Link | Unset
        if isinstance(_link,  Unset):
            link = UNSET
        else:
            link = Link.from_dict(_link)




        dictionary = cls(
            name=name,
            version=version,
            dictionary_attr_type=dictionary_attr_type,
            id=id,
            description=description,
            link=link,
        )


        dictionary.additional_properties = d
        return dictionary

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
