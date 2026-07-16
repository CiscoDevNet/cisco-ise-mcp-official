# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.link import Link





T = TypeVar("T", bound="RegenerateRootCaResponse")



@_attrs_define
class RegenerateRootCaResponse:
    

    id: Union[Unset, str] = UNSET
    """ ID which can be used to track the status of Cisco ISE root CA chain regeneration """
    link: Union['Link', None, Unset] = UNSET
    message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        id = self.id

        link: Union[None, Unset, dict[str, Any]]
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, Link):
            link = self.link.to_dict()
        else:
            link = self.link

        message = self.message


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if link is not UNSET:
            field_dict["link"] = link
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        def _parse_link(data: object) -> Union['Link', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_link_type_0 = Link.from_dict(data)



                return componentsschemas_link_type_0
            except: # noqa: E722
                pass
            return cast(Union['Link', None, Unset], data)

        link = _parse_link(d.pop("link", UNSET))


        message = d.pop("message", UNSET)

        regenerate_root_ca_response = cls(
            id=id,
            link=link,
            message=message,
        )


        regenerate_root_ca_response.additional_properties = d
        return regenerate_root_ca_response

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
