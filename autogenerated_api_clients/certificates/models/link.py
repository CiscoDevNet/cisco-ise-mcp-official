from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.link_rel import LinkRel
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="Link")



@_attrs_define
class Link:
    

    href: Union[Unset, str] = UNSET
    rel: Union[Unset, LinkRel] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        href = self.href

        rel: Union[Unset, str] = UNSET
        if not isinstance(self.rel, Unset):
            rel = self.rel.value


        type_ = self.type_


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if href is not UNSET:
            field_dict["href"] = href
        if rel is not UNSET:
            field_dict["rel"] = rel
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        href = d.pop("href", UNSET)

        _rel = d.pop("rel", UNSET)
        rel: Union[Unset, LinkRel]
        if isinstance(_rel,  Unset):
            rel = UNSET
        else:
            rel = LinkRel(_rel)




        type_ = d.pop("type", UNSET)

        link = cls(
            href=href,
            rel=rel,
            type_=type_,
        )


        link.additional_properties = d
        return link

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
