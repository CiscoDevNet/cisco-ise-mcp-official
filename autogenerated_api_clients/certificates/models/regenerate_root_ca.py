# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="RegenerateRootCA")



@_attrs_define
class RegenerateRootCA:
    

    remove_existing_ise_intermediate_csr: bool
    """ Setting this attribute to true removes existing Cisco ISE Intermediate CSR """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        remove_existing_ise_intermediate_csr = self.remove_existing_ise_intermediate_csr


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "removeExistingISEIntermediateCSR": remove_existing_ise_intermediate_csr,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        remove_existing_ise_intermediate_csr = d.pop("removeExistingISEIntermediateCSR")

        regenerate_root_ca = cls(
            remove_existing_ise_intermediate_csr=remove_existing_ise_intermediate_csr,
        )


        regenerate_root_ca.additional_properties = d
        return regenerate_root_ca

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
