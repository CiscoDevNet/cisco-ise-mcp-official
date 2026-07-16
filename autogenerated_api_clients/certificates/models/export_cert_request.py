# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.export_cert_request_export import ExportCertRequestExport
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="ExportCertRequest")



@_attrs_define
class ExportCertRequest:
    

    export: ExportCertRequestExport
    id: str
    host_name: Union[Unset, str] = UNSET
    """ Hostname of the Cisco ISE node in which self-signed certificate should be generated. """
    password: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        export = self.export.value

        id = self.id

        host_name = self.host_name

        password = self.password


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "export": export,
            "id": id,
        })
        if host_name is not UNSET:
            field_dict["hostName"] = host_name
        if password is not UNSET:
            field_dict["password"] = password

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        export = ExportCertRequestExport(d.pop("export"))




        id = d.pop("id")

        host_name = d.pop("hostName", UNSET)

        password = d.pop("password", UNSET)

        export_cert_request = cls(
            export=export,
            id=id,
            host_name=host_name,
            password=password,
        )


        export_cert_request.additional_properties = d
        return export_cert_request

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
