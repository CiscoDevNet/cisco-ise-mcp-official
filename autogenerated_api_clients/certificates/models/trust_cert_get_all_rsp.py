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
  from ..models.trust_certificate_response import TrustCertificateResponse





T = TypeVar("T", bound="TrustCertGetAllRsp")



@_attrs_define
class TrustCertGetAllRsp:
    

    next_page: Union['Link', None, Unset] = UNSET
    previous_page: Union['Link', None, Unset] = UNSET
    response: Union[Unset, list['TrustCertificateResponse']] = UNSET
    version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        from ..models.trust_certificate_response import TrustCertificateResponse
        next_page: Union[None, Unset, dict[str, Any]]
        if isinstance(self.next_page, Unset):
            next_page = UNSET
        elif isinstance(self.next_page, Link):
            next_page = self.next_page.to_dict()
        else:
            next_page = self.next_page

        previous_page: Union[None, Unset, dict[str, Any]]
        if isinstance(self.previous_page, Unset):
            previous_page = UNSET
        elif isinstance(self.previous_page, Link):
            previous_page = self.previous_page.to_dict()
        else:
            previous_page = self.previous_page

        response: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.response, Unset):
            response = []
            for response_item_data in self.response:
                response_item = response_item_data.to_dict()
                response.append(response_item)



        version = self.version


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if next_page is not UNSET:
            field_dict["nextPage"] = next_page
        if previous_page is not UNSET:
            field_dict["previousPage"] = previous_page
        if response is not UNSET:
            field_dict["response"] = response
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        from ..models.trust_certificate_response import TrustCertificateResponse
        d = dict(src_dict)
        def _parse_next_page(data: object) -> Union['Link', None, Unset]:
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

        next_page = _parse_next_page(d.pop("nextPage", UNSET))


        def _parse_previous_page(data: object) -> Union['Link', None, Unset]:
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

        previous_page = _parse_previous_page(d.pop("previousPage", UNSET))


        response = []
        _response = d.pop("response", UNSET)
        for response_item_data in (_response or []):
            response_item = TrustCertificateResponse.from_dict(response_item_data)



            response.append(response_item)


        version = d.pop("version", UNSET)

        trust_cert_get_all_rsp = cls(
            next_page=next_page,
            previous_page=previous_page,
            response=response,
            version=version,
        )


        trust_cert_get_all_rsp.additional_properties = d
        return trust_cert_get_all_rsp

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
