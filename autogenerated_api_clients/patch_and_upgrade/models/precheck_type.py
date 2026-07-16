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
  from ..models.list_node import ListNode





T = TypeVar("T", bound="PrecheckType")



@_attrs_define
class PrecheckType:
    

    check_type: Union[Unset, str] = UNSET
    displayname: Union[Unset, str] = UNSET
    execution_time: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    nodes: Union[Unset, list['ListNode']] = UNSET
    on_failure: Union[Unset, str] = UNSET
    percentage: Union[Unset, int] = UNSET
    remediation_msg: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    success_msg: Union[Unset, str] = UNSET
    success_nodes: Union[Unset, int] = UNSET
    update_time: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.list_node import ListNode
        check_type = self.check_type

        displayname = self.displayname

        execution_time = self.execution_time

        message = self.message

        name = self.name

        nodes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nodes, Unset):
            nodes = []
            for nodes_item_data in self.nodes:
                nodes_item = nodes_item_data.to_dict()
                nodes.append(nodes_item)



        on_failure = self.on_failure

        percentage = self.percentage

        remediation_msg = self.remediation_msg

        status = self.status

        success_msg = self.success_msg

        success_nodes = self.success_nodes

        update_time = self.update_time


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if check_type is not UNSET:
            field_dict["checkType"] = check_type
        if displayname is not UNSET:
            field_dict["displayname"] = displayname
        if execution_time is not UNSET:
            field_dict["executionTime"] = execution_time
        if message is not UNSET:
            field_dict["message"] = message
        if name is not UNSET:
            field_dict["name"] = name
        if nodes is not UNSET:
            field_dict["nodes"] = nodes
        if on_failure is not UNSET:
            field_dict["onFailure"] = on_failure
        if percentage is not UNSET:
            field_dict["percentage"] = percentage
        if remediation_msg is not UNSET:
            field_dict["remediationMsg"] = remediation_msg
        if status is not UNSET:
            field_dict["status"] = status
        if success_msg is not UNSET:
            field_dict["successMsg"] = success_msg
        if success_nodes is not UNSET:
            field_dict["successNodes"] = success_nodes
        if update_time is not UNSET:
            field_dict["updateTime"] = update_time

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_node import ListNode
        d = dict(src_dict)
        check_type = d.pop("checkType", UNSET)

        displayname = d.pop("displayname", UNSET)

        execution_time = d.pop("executionTime", UNSET)

        message = d.pop("message", UNSET)

        name = d.pop("name", UNSET)

        nodes = []
        _nodes = d.pop("nodes", UNSET)
        for nodes_item_data in (_nodes or []):
            nodes_item = ListNode.from_dict(nodes_item_data)



            nodes.append(nodes_item)


        on_failure = d.pop("onFailure", UNSET)

        percentage = d.pop("percentage", UNSET)

        remediation_msg = d.pop("remediationMsg", UNSET)

        status = d.pop("status", UNSET)

        success_msg = d.pop("successMsg", UNSET)

        success_nodes = d.pop("successNodes", UNSET)

        update_time = d.pop("updateTime", UNSET)

        precheck_type = cls(
            check_type=check_type,
            displayname=displayname,
            execution_time=execution_time,
            message=message,
            name=name,
            nodes=nodes,
            on_failure=on_failure,
            percentage=percentage,
            remediation_msg=remediation_msg,
            status=status,
            success_msg=success_msg,
            success_nodes=success_nodes,
            update_time=update_time,
        )


        precheck_type.additional_properties = d
        return precheck_type

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
