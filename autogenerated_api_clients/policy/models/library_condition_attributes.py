from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.condition_attributes_operator import ConditionAttributesOperator
from ..models.condition_condition_type import ConditionConditionType
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.link import Link





T = TypeVar("T", bound="LibraryConditionAttributes")



@_attrs_define
class LibraryConditionAttributes:
    

    condition_type: ConditionConditionType
    """ <ul><li>Inidicates whether the record is the condition itself(data) or a logical(or,and) aggregation</li>
    <li>Data type enum(reference,single) indicates than "conditonId" OR "ConditionAttrs" fields should contain
    condition data but not both</li> <li>Logical aggreation(and,or) enum indicates that additional conditions are
    present under the children field</li></ul> """
    dictionary_name: str
    """ Dictionary name """
    attribute_name: str
    """ Dictionary attribute name """
    operator: ConditionAttributesOperator
    """ Equality operator """
    attribute_value: str
    """ <ul><li>Attribute value for condition</li> <li>Value type is specified in dictionary object</li> <li>if
    multiple values allowed is specified in dictionary object</li></ul> """
    name: str
    """ Condition name, [Valid characters are alphanumerics, underscore, hyphen, space] """
    link: Link | None | Unset = UNSET
    is_negate: bool | Unset = False
    """ Indicates whereas this condition is in negate mode """
    dictionary_value: str | Unset = UNSET
    """ Dictionary value """
    id: UUID | Unset = UNSET
    """ condition ID """
    description: str | Unset = ''
    """ Conditiopn description """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        condition_type = self.condition_type.value

        dictionary_name = self.dictionary_name

        attribute_name = self.attribute_name

        operator = self.operator.value

        attribute_value = self.attribute_value

        name = self.name

        link: dict[str, Any] | None | Unset
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, Link):
            link = self.link.to_dict()
        else:
            link = self.link

        is_negate = self.is_negate

        dictionary_value = self.dictionary_value

        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        description = self.description


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "conditionType": condition_type,
            "dictionaryName": dictionary_name,
            "attributeName": attribute_name,
            "operator": operator,
            "attributeValue": attribute_value,
            "name": name,
        })
        if link is not UNSET:
            field_dict["link"] = link
        if is_negate is not UNSET:
            field_dict["isNegate"] = is_negate
        if dictionary_value is not UNSET:
            field_dict["dictionaryValue"] = dictionary_value
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        d = dict(src_dict)
        condition_type = ConditionConditionType(d.pop("conditionType"))




        dictionary_name = d.pop("dictionaryName")

        attribute_name = d.pop("attributeName")

        operator = ConditionAttributesOperator(d.pop("operator"))




        attribute_value = d.pop("attributeValue")

        name = d.pop("name")

        def _parse_link(data: object) -> Link | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                link_type_1 = Link.from_dict(data)



                return link_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Link | None | Unset, data)

        link = _parse_link(d.pop("link", UNSET))


        is_negate = d.pop("isNegate", UNSET)

        dictionary_value = d.pop("dictionaryValue", UNSET)

        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = UUID(_id)




        description = d.pop("description", UNSET)

        library_condition_attributes = cls(
            condition_type=condition_type,
            dictionary_name=dictionary_name,
            attribute_name=attribute_name,
            operator=operator,
            attribute_value=attribute_value,
            name=name,
            link=link,
            is_negate=is_negate,
            dictionary_value=dictionary_value,
            id=id,
            description=description,
        )


        library_condition_attributes.additional_properties = d
        return library_condition_attributes

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
