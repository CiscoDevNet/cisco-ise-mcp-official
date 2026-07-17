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






T = TypeVar("T", bound="PrecheckRequest")



@_attrs_define
class PrecheckRequest:
    

    bundle_name: Union[Unset, str] = UNSET
    hostnames: Union[Unset, list[str]] = UNSET
    patch_bundle_name: Union[Unset, str] = UNSET
    pre_check_report_id: Union[Unset, str] = UNSET
    pre_checks: Union[Unset, list[str]] = UNSET
    re_trigger: Union[Unset, bool] = UNSET
    repo_name: Union[Unset, str] = UNSET
    upgrade_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        bundle_name = self.bundle_name

        hostnames: Union[Unset, list[str]] = UNSET
        if not isinstance(self.hostnames, Unset):
            hostnames = self.hostnames



        patch_bundle_name = self.patch_bundle_name

        pre_check_report_id = self.pre_check_report_id

        pre_checks: Union[Unset, list[str]] = UNSET
        if not isinstance(self.pre_checks, Unset):
            pre_checks = self.pre_checks



        re_trigger = self.re_trigger

        repo_name = self.repo_name

        upgrade_type = self.upgrade_type


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if bundle_name is not UNSET:
            field_dict["bundleName"] = bundle_name
        if hostnames is not UNSET:
            field_dict["hostnames"] = hostnames
        if patch_bundle_name is not UNSET:
            field_dict["patchBundleName"] = patch_bundle_name
        if pre_check_report_id is not UNSET:
            field_dict["preCheckReportID"] = pre_check_report_id
        if pre_checks is not UNSET:
            field_dict["preChecks"] = pre_checks
        if re_trigger is not UNSET:
            field_dict["reTrigger"] = re_trigger
        if repo_name is not UNSET:
            field_dict["repoName"] = repo_name
        if upgrade_type is not UNSET:
            field_dict["upgradeType"] = upgrade_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bundle_name = d.pop("bundleName", UNSET)

        hostnames = cast(list[str], d.pop("hostnames", UNSET))


        patch_bundle_name = d.pop("patchBundleName", UNSET)

        pre_check_report_id = d.pop("preCheckReportID", UNSET)

        pre_checks = cast(list[str], d.pop("preChecks", UNSET))


        re_trigger = d.pop("reTrigger", UNSET)

        repo_name = d.pop("repoName", UNSET)

        upgrade_type = d.pop("upgradeType", UNSET)

        precheck_request = cls(
            bundle_name=bundle_name,
            hostnames=hostnames,
            patch_bundle_name=patch_bundle_name,
            pre_check_report_id=pre_check_report_id,
            pre_checks=pre_checks,
            re_trigger=re_trigger,
            repo_name=repo_name,
            upgrade_type=upgrade_type,
        )


        precheck_request.additional_properties = d
        return precheck_request

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
