from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="UpgradeProceedRequest")



@_attrs_define
class UpgradeProceedRequest:
    

    pre_check_report_id: str
    upgrade_type: str
    hostnames: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        pre_check_report_id = self.pre_check_report_id

        upgrade_type = self.upgrade_type

        hostnames: Union[Unset, list[str]] = UNSET
        if not isinstance(self.hostnames, Unset):
            hostnames = self.hostnames




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "preCheckReportID": pre_check_report_id,
            "upgradeType": upgrade_type,
        })
        if hostnames is not UNSET:
            field_dict["hostnames"] = hostnames

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pre_check_report_id = d.pop("preCheckReportID")

        upgrade_type = d.pop("upgradeType")

        hostnames = cast(list[str], d.pop("hostnames", UNSET))


        upgrade_proceed_request = cls(
            pre_check_report_id=pre_check_report_id,
            upgrade_type=upgrade_type,
            hostnames=hostnames,
        )


        upgrade_proceed_request.additional_properties = d
        return upgrade_proceed_request

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
