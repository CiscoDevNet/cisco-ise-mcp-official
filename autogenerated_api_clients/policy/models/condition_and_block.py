from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.condition_condition_type import ConditionConditionType
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.condition import Condition
  from ..models.link import Link





T = TypeVar("T", bound="ConditionAndBlock")



@_attrs_define
class ConditionAndBlock:
    

    condition_type: ConditionConditionType
    """ <ul><li>Inidicates whether the record is the condition itself(data) or a logical(or,and) aggregation</li>
    <li>Data type enum(reference,single) indicates than "conditonId" OR "ConditionAttrs" fields should contain
    condition data but not both</li> <li>Logical aggreation(and,or) enum indicates that additional conditions are
    present under the children field</li></ul> """
    children: list[Condition]
    """ In case type is andBlock or orBlock addtional conditions will be aggregated under this logical (OR/AND)
    condition """
    link: Link | None | Unset = UNSET
    is_negate: bool | Unset = False
    """ Indicates whereas this condition is in negate mode """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.condition import Condition
        from ..models.link import Link
        condition_type = self.condition_type.value

        children = []
        for children_item_data in self.children:
            children_item = children_item_data.to_dict()
            children.append(children_item)



        link: dict[str, Any] | None | Unset
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, Link):
            link = self.link.to_dict()
        else:
            link = self.link

        is_negate = self.is_negate


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "conditionType": condition_type,
            "children": children,
        })
        if link is not UNSET:
            field_dict["link"] = link
        if is_negate is not UNSET:
            field_dict["isNegate"] = is_negate

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.condition import Condition
        from ..models.link import Link
        d = dict(src_dict)
        condition_type = ConditionConditionType(d.pop("conditionType"))




        children = []
        _children = d.pop("children")
        for children_item_data in (_children):
            children_item = Condition.from_dict(children_item_data)



            children.append(children_item)


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

        condition_and_block = cls(
            condition_type=condition_type,
            children=children,
            link=link,
            is_negate=is_negate,
        )


        condition_and_block.additional_properties = d
        return condition_and_block

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
