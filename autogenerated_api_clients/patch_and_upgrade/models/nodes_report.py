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
  from ..models.node_report_item import NodeReportItem





T = TypeVar("T", bound="NodesReport")



@_attrs_define
class NodesReport:
    

    nodes_report: Union[Unset, list['NodeReportItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.node_report_item import NodeReportItem
        nodes_report: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nodes_report, Unset):
            nodes_report = []
            for nodes_report_item_data in self.nodes_report:
                nodes_report_item = nodes_report_item_data.to_dict()
                nodes_report.append(nodes_report_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if nodes_report is not UNSET:
            field_dict["nodes-report"] = nodes_report

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.node_report_item import NodeReportItem
        d = dict(src_dict)
        nodes_report = []
        _nodes_report = d.pop("nodes-report", UNSET)
        for nodes_report_item_data in (_nodes_report or []):
            nodes_report_item = NodeReportItem.from_dict(nodes_report_item_data)



            nodes_report.append(nodes_report_item)


        nodes_report = cls(
            nodes_report=nodes_report,
        )


        nodes_report.additional_properties = d
        return nodes_report

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
