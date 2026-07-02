from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.nodes_report import NodesReport
  from ..models.upgrade_proceed import UpgradeProceed
  from ..models.upgrade_precheck_response import UpgradePrecheckResponse





T = TypeVar("T", bound="UpgradeSummaryResponse")



@_attrs_define
class UpgradeSummaryResponse:
    

    nodes_report_summary: Union[Unset, list['NodesReport']] = UNSET
    prechecks_summary: Union[Unset, list['UpgradePrecheckResponse']] = UNSET
    upgrade_summary: Union[Unset, list['UpgradeProceed']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.nodes_report import NodesReport
        from ..models.upgrade_proceed import UpgradeProceed
        from ..models.upgrade_precheck_response import UpgradePrecheckResponse
        nodes_report_summary: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nodes_report_summary, Unset):
            nodes_report_summary = []
            for nodes_report_summary_item_data in self.nodes_report_summary:
                nodes_report_summary_item = nodes_report_summary_item_data.to_dict()
                nodes_report_summary.append(nodes_report_summary_item)



        prechecks_summary: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.prechecks_summary, Unset):
            prechecks_summary = []
            for prechecks_summary_item_data in self.prechecks_summary:
                prechecks_summary_item = prechecks_summary_item_data.to_dict()
                prechecks_summary.append(prechecks_summary_item)



        upgrade_summary: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.upgrade_summary, Unset):
            upgrade_summary = []
            for upgrade_summary_item_data in self.upgrade_summary:
                upgrade_summary_item = upgrade_summary_item_data.to_dict()
                upgrade_summary.append(upgrade_summary_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if nodes_report_summary is not UNSET:
            field_dict["NodesReportSummary"] = nodes_report_summary
        if prechecks_summary is not UNSET:
            field_dict["PrechecksSummary"] = prechecks_summary
        if upgrade_summary is not UNSET:
            field_dict["UpgradeSummary"] = upgrade_summary

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nodes_report import NodesReport
        from ..models.upgrade_proceed import UpgradeProceed
        from ..models.upgrade_precheck_response import UpgradePrecheckResponse
        d = dict(src_dict)
        nodes_report_summary = []
        _nodes_report_summary = d.pop("NodesReportSummary", UNSET)
        for nodes_report_summary_item_data in (_nodes_report_summary or []):
            nodes_report_summary_item = NodesReport.from_dict(nodes_report_summary_item_data)



            nodes_report_summary.append(nodes_report_summary_item)


        prechecks_summary = []
        _prechecks_summary = d.pop("PrechecksSummary", UNSET)
        for prechecks_summary_item_data in (_prechecks_summary or []):
            prechecks_summary_item = UpgradePrecheckResponse.from_dict(prechecks_summary_item_data)



            prechecks_summary.append(prechecks_summary_item)


        upgrade_summary = []
        _upgrade_summary = d.pop("UpgradeSummary", UNSET)
        for upgrade_summary_item_data in (_upgrade_summary or []):
            upgrade_summary_item = UpgradeProceed.from_dict(upgrade_summary_item_data)



            upgrade_summary.append(upgrade_summary_item)


        upgrade_summary_response = cls(
            nodes_report_summary=nodes_report_summary,
            prechecks_summary=prechecks_summary,
            upgrade_summary=upgrade_summary,
        )


        upgrade_summary_response.additional_properties = d
        return upgrade_summary_response

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
