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
from typing import Union

if TYPE_CHECKING:
  from ..models.generate_csr_response import GenerateCSRResponse





T = TypeVar("T", bound="GenerateCSRRespPayload")



@_attrs_define
class GenerateCSRRespPayload:
    

    response: Union[Unset, list['GenerateCSRResponse']] = UNSET
    version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.generate_csr_response import GenerateCSRResponse
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
        if response is not UNSET:
            field_dict["response"] = response
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.generate_csr_response import GenerateCSRResponse
        d = dict(src_dict)
        response = []
        _response = d.pop("response", UNSET)
        for response_item_data in (_response or []):
            response_item = GenerateCSRResponse.from_dict(response_item_data)



            response.append(response_item)


        version = d.pop("version", UNSET)

        generate_csr_resp_payload = cls(
            response=response,
            version=version,
        )


        generate_csr_resp_payload.additional_properties = d
        return generate_csr_resp_payload

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
