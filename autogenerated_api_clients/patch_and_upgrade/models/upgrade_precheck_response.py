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
  from ..models.precheck_type import PrecheckType





T = TypeVar("T", bound="UpgradePrecheckResponse")



@_attrs_define
class UpgradePrecheckResponse:
    

    is_valid: Union[Unset, bool] = UNSET
    ise_version: Union[Unset, str] = UNSET
    nodecount: Union[Unset, int] = UNSET
    patch_no: Union[Unset, int] = UNSET
    pre_check_report_id: Union[Unset, str] = UNSET
    pre_checks: Union[Unset, list['PrecheckType']] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.precheck_type import PrecheckType
        is_valid = self.is_valid

        ise_version = self.ise_version

        nodecount = self.nodecount

        patch_no = self.patch_no

        pre_check_report_id = self.pre_check_report_id

        pre_checks: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.pre_checks, Unset):
            pre_checks = []
            for pre_checks_item_data in self.pre_checks:
                pre_checks_item = pre_checks_item_data.to_dict()
                pre_checks.append(pre_checks_item)



        status = self.status


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if is_valid is not UNSET:
            field_dict["isValid"] = is_valid
        if ise_version is not UNSET:
            field_dict["iseVersion"] = ise_version
        if nodecount is not UNSET:
            field_dict["nodecount"] = nodecount
        if patch_no is not UNSET:
            field_dict["patchNo"] = patch_no
        if pre_check_report_id is not UNSET:
            field_dict["preCheckReportID"] = pre_check_report_id
        if pre_checks is not UNSET:
            field_dict["preChecks"] = pre_checks
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.precheck_type import PrecheckType
        d = dict(src_dict)
        is_valid = d.pop("isValid", UNSET)

        ise_version = d.pop("iseVersion", UNSET)

        nodecount = d.pop("nodecount", UNSET)

        patch_no = d.pop("patchNo", UNSET)

        pre_check_report_id = d.pop("preCheckReportID", UNSET)

        pre_checks = []
        _pre_checks = d.pop("preChecks", UNSET)
        for pre_checks_item_data in (_pre_checks or []):
            pre_checks_item = PrecheckType.from_dict(pre_checks_item_data)



            pre_checks.append(pre_checks_item)


        status = d.pop("status", UNSET)

        upgrade_precheck_response = cls(
            is_valid=is_valid,
            ise_version=ise_version,
            nodecount=nodecount,
            patch_no=patch_no,
            pre_check_report_id=pre_check_report_id,
            pre_checks=pre_checks,
            status=status,
        )


        upgrade_precheck_response.additional_properties = d
        return upgrade_precheck_response

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
