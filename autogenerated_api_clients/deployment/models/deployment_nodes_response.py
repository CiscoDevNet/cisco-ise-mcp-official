# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_node import DeploymentNode


T = TypeVar("T", bound="DeploymentNodesResponse")


@_attrs_define
class DeploymentNodesResponse:
    response: list[DeploymentNode] | Unset = UNSET
    version: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        response: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.response, Unset):
            response = []
            for response_item_data in self.response:
                response_item = response_item_data.to_dict()
                response.append(response_item)

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if response is not UNSET:
            field_dict["response"] = response
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_node import DeploymentNode

        d = dict(src_dict)
        _response = d.pop("response", UNSET)
        response: list[DeploymentNode] | Unset = UNSET
        if _response is not UNSET:
            response = []
            for response_item_data in _response:
                response_item = DeploymentNode.from_dict(response_item_data)

                response.append(response_item)

        version = d.pop("version", UNSET)

        deployment_nodes_response = cls(
            response=response,
            version=version,
        )

        deployment_nodes_response.additional_properties = d
        return deployment_nodes_response

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
