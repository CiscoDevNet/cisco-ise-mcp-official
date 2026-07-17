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






T = TypeVar("T", bound="RollbackPrecheckRequest")



@_attrs_define
class RollbackPrecheckRequest:
    

    upgrade_type: str
    pre_check_report_id: Union[Unset, str] = UNSET
    pre_checks: Union[Unset, list[str]] = UNSET
    """ Array of prechecks that needs to be executed. """
    re_trigger: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        upgrade_type = self.upgrade_type

        pre_check_report_id = self.pre_check_report_id

        pre_checks: Union[Unset, list[str]] = UNSET
        if not isinstance(self.pre_checks, Unset):
            pre_checks = self.pre_checks



        re_trigger = self.re_trigger


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "upgradeType": upgrade_type,
        })
        if pre_check_report_id is not UNSET:
            field_dict["preCheckReportID"] = pre_check_report_id
        if pre_checks is not UNSET:
            field_dict["preChecks"] = pre_checks
        if re_trigger is not UNSET:
            field_dict["reTrigger"] = re_trigger

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        upgrade_type = d.pop("upgradeType")

        pre_check_report_id = d.pop("preCheckReportID", UNSET)

        pre_checks = cast(list[str], d.pop("preChecks", UNSET))


        re_trigger = d.pop("reTrigger", UNSET)

        rollback_precheck_request = cls(
            upgrade_type=upgrade_type,
            pre_check_report_id=pre_check_report_id,
            pre_checks=pre_checks,
            re_trigger=re_trigger,
        )


        rollback_precheck_request.additional_properties = d
        return rollback_precheck_request

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
