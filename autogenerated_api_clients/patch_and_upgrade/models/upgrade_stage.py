from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="UpgradeStage")



@_attrs_define
class UpgradeStage:
    

    db_status: Union[Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    node: Union[Unset, str] = UNSET
    percentage: Union[Unset, int] = UNSET
    progress_msg: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        db_status = self.db_status

        message = self.message

        node = self.node

        percentage = self.percentage

        progress_msg = self.progress_msg

        status = self.status


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if db_status is not UNSET:
            field_dict["dbStatus"] = db_status
        if message is not UNSET:
            field_dict["message"] = message
        if node is not UNSET:
            field_dict["node"] = node
        if percentage is not UNSET:
            field_dict["percentage"] = percentage
        if progress_msg is not UNSET:
            field_dict["progressMsg"] = progress_msg
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        db_status = d.pop("dbStatus", UNSET)

        message = d.pop("message", UNSET)

        node = d.pop("node", UNSET)

        percentage = d.pop("percentage", UNSET)

        progress_msg = d.pop("progressMsg", UNSET)

        status = d.pop("status", UNSET)

        upgrade_stage = cls(
            db_status=db_status,
            message=message,
            node=node,
            percentage=percentage,
            progress_msg=progress_msg,
            status=status,
        )


        upgrade_stage.additional_properties = d
        return upgrade_stage

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
