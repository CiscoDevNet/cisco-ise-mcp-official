from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="DatesRange")



@_attrs_define
class DatesRange:
    """ <p>Defines for which date/s TimeAndDate condition will be matched<br> Options are - Date range, for specific date,
    the same date should be used for start/end date <br> Default - no specific dates<br> In order to reset the dates to
    have no specific dates Date format - yyyy-mm-dd (MM = month, dd = day, yyyy = year)</p>

     """

    start_date: str
    end_date: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        start_date = self.start_date

        end_date = self.end_date


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "startDate": start_date,
            "endDate": end_date,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_date = d.pop("startDate")

        end_date = d.pop("endDate")

        dates_range = cls(
            start_date=start_date,
            end_date=end_date,
        )


        dates_range.additional_properties = d
        return dates_range

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
