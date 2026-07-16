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
  from ..models.list_node_proceed import ListNodeProceed





T = TypeVar("T", bound="UpgradeProceed")



@_attrs_define
class UpgradeProceed:
    

    nodes: Union[Unset, list['ListNodeProceed']] = UNSET
    percentage: Union[Unset, int] = UNSET
    remaining_upgrade_time: Union[Unset, int] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.list_node_proceed import ListNodeProceed
        nodes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nodes, Unset):
            nodes = []
            for nodes_item_data in self.nodes:
                nodes_item = nodes_item_data.to_dict()
                nodes.append(nodes_item)



        percentage = self.percentage

        remaining_upgrade_time = self.remaining_upgrade_time

        status = self.status


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if nodes is not UNSET:
            field_dict["nodes"] = nodes
        if percentage is not UNSET:
            field_dict["percentage"] = percentage
        if remaining_upgrade_time is not UNSET:
            field_dict["remainingUpgradeTime"] = remaining_upgrade_time
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_node_proceed import ListNodeProceed
        d = dict(src_dict)
        nodes = []
        _nodes = d.pop("nodes", UNSET)
        for nodes_item_data in (_nodes or []):
            nodes_item = ListNodeProceed.from_dict(nodes_item_data)



            nodes.append(nodes_item)


        percentage = d.pop("percentage", UNSET)

        remaining_upgrade_time = d.pop("remainingUpgradeTime", UNSET)

        status = d.pop("status", UNSET)

        upgrade_proceed = cls(
            nodes=nodes,
            percentage=percentage,
            remaining_upgrade_time=remaining_upgrade_time,
            status=status,
        )


        upgrade_proceed.additional_properties = d
        return upgrade_proceed

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
