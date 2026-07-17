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





T = TypeVar("T", bound="CSRResponse")



@_attrs_define
class CSRResponse:
    

    friendly_name: Union[Unset, str] = UNSET
    """ Friendly name of the certificate. """
    group_tag: Union[Unset, str] = UNSET
    """ GroupTag of the certificate. """
    host_name: Union[Unset, str] = UNSET
    """ Hostname or IP address of the Cisco ISE node. """
    id: Union[Unset, str] = UNSET
    """ ID of the certificate. """
    key_size: Union[Unset, str] = UNSET
    """ Size of the cryptographic key used. """
    link: Union['Link', None, Unset] = UNSET
    san_names: Union[Unset, str] = UNSET
    """ String representation of subject alternative names. """
    signature_algorithm: Union[Unset, str] = UNSET
    """ Algorithm used for encrypting CSR """
    subject: Union[Unset, str] = UNSET
    """ Subject of the certificate. Includes Common Name (CN), Organizational Unit (OU), etc. """
    time_stamp: Union[Unset, str] = UNSET
    """ Timestamp of the certificate generation. """
    used_for: Union[Unset, str] = UNSET
    """ Services for which the certificate is used for (for eg- MGMT, GENERIC). """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        friendly_name = self.friendly_name

        group_tag = self.group_tag

        host_name = self.host_name

        id = self.id

        key_size = self.key_size

        link: Union[None, Unset, dict[str, Any]]
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, Link):
            link = self.link.to_dict()
        else:
            link = self.link

        san_names = self.san_names

        signature_algorithm = self.signature_algorithm

        subject = self.subject

        time_stamp = self.time_stamp

        used_for = self.used_for


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if group_tag is not UNSET:
            field_dict["groupTag"] = group_tag
        if host_name is not UNSET:
            field_dict["hostName"] = host_name
        if id is not UNSET:
            field_dict["id"] = id
        if key_size is not UNSET:
            field_dict["keySize"] = key_size
        if link is not UNSET:
            field_dict["link"] = link
        if san_names is not UNSET:
            field_dict["sanNames"] = san_names
        if signature_algorithm is not UNSET:
            field_dict["signatureAlgorithm"] = signature_algorithm
        if subject is not UNSET:
            field_dict["subject"] = subject
        if time_stamp is not UNSET:
            field_dict["timeStamp"] = time_stamp
        if used_for is not UNSET:
            field_dict["usedFor"] = used_for

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        d = dict(src_dict)
        friendly_name = d.pop("friendlyName", UNSET)

        group_tag = d.pop("groupTag", UNSET)

        host_name = d.pop("hostName", UNSET)

        id = d.pop("id", UNSET)

        key_size = d.pop("keySize", UNSET)

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


        san_names = d.pop("sanNames", UNSET)

        signature_algorithm = d.pop("signatureAlgorithm", UNSET)

        subject = d.pop("subject", UNSET)

        time_stamp = d.pop("timeStamp", UNSET)

        used_for = d.pop("usedFor", UNSET)

        csr_response = cls(
            friendly_name=friendly_name,
            group_tag=group_tag,
            host_name=host_name,
            id=id,
            key_size=key_size,
            link=link,
            san_names=san_names,
            signature_algorithm=signature_algorithm,
            subject=subject,
            time_stamp=time_stamp,
            used_for=used_for,
        )


        csr_response.additional_properties = d
        return csr_response

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
