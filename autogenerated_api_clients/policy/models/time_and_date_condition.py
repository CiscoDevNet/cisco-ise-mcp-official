from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.condition_condition_type import ConditionConditionType
from ..models.week_day_enum import WeekDayEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.dates_range import DatesRange
  from ..models.hours_range import HoursRange
  from ..models.link import Link





T = TypeVar("T", bound="TimeAndDateCondition")



@_attrs_define
class TimeAndDateCondition:
    """ Condition based on time and date.

     """

    condition_type: ConditionConditionType
    """ <ul><li>Inidicates whether the record is the condition itself(data) or a logical(or,and) aggregation</li>
    <li>Data type enum(reference,single) indicates than "conditonId" OR "ConditionAttrs" fields should contain
    condition data but not both</li> <li>Logical aggreation(and,or) enum indicates that additional conditions are
    present under the children field</li></ul> """
    name: str
    """ Condition name """
    link: Link | None | Unset = UNSET
    is_negate: bool | Unset = False
    """ Indicates whereas this condition is in negate mode """
    id: UUID | Unset = UNSET
    description: str | Unset = ''
    """ Condition description """
    hours_range: HoursRange | Unset = UNSET
    """ <p>Defines for which hours a TimeAndDate condition will be matched<br> Time foramt - hh:mm  ( h = hour , mm
    = minutes ) <br> Default - All Day </p> """
    hours_range_exception: HoursRange | Unset = UNSET
    """ <p>Defines for which hours a TimeAndDate condition will be matched<br> Time foramt - hh:mm  ( h = hour , mm
    = minutes ) <br> Default - All Day </p> """
    week_days: list[WeekDayEnum] | Unset = UNSET
    """ <p>Defines for which days this condition will be matched<br> Days format - Arrays of WeekDay enums <br>
    Default - List of All week days</p> """
    week_days_exception: list[WeekDayEnum] | Unset = UNSET
    """ <p>Defines for which days this condition will NOT be matched<br> Days format - Arrays of WeekDay enums <br>
    Default - Not enabled</p> """
    dates_range: DatesRange | Unset = UNSET
    """ <p>Defines for which date/s TimeAndDate condition will be matched<br> Options are - Date range, for specific
    date, the same date should be used for start/end date <br> Default - no specific dates<br> In order to reset the
    dates to have no specific dates Date format - yyyy-mm-dd (MM = month, dd = day, yyyy = year)</p> """
    dates_range_exception: DatesRange | Unset = UNSET
    """ <p>Defines for which date/s TimeAndDate condition will be matched<br> Options are - Date range, for specific
    date, the same date should be used for start/end date <br> Default - no specific dates<br> In order to reset the
    dates to have no specific dates Date format - yyyy-mm-dd (MM = month, dd = day, yyyy = year)</p> """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dates_range import DatesRange
        from ..models.link import Link
        from ..models.hours_range import HoursRange
        condition_type = self.condition_type.value

        name = self.name

        link: dict[str, Any] | None | Unset
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, Link):
            link = self.link.to_dict()
        else:
            link = self.link

        is_negate = self.is_negate

        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        description = self.description

        hours_range: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hours_range, Unset):
            hours_range = self.hours_range.to_dict()

        hours_range_exception: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hours_range_exception, Unset):
            hours_range_exception = self.hours_range_exception.to_dict()

        week_days: list[str] | Unset = UNSET
        if not isinstance(self.week_days, Unset):
            week_days = []
            for week_days_item_data in self.week_days:
                week_days_item = week_days_item_data.value
                week_days.append(week_days_item)



        week_days_exception: list[str] | Unset = UNSET
        if not isinstance(self.week_days_exception, Unset):
            week_days_exception = []
            for week_days_exception_item_data in self.week_days_exception:
                week_days_exception_item = week_days_exception_item_data.value
                week_days_exception.append(week_days_exception_item)



        dates_range: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dates_range, Unset):
            dates_range = self.dates_range.to_dict()

        dates_range_exception: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dates_range_exception, Unset):
            dates_range_exception = self.dates_range_exception.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "conditionType": condition_type,
            "name": name,
        })
        if link is not UNSET:
            field_dict["link"] = link
        if is_negate is not UNSET:
            field_dict["isNegate"] = is_negate
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if hours_range is not UNSET:
            field_dict["hoursRange"] = hours_range
        if hours_range_exception is not UNSET:
            field_dict["hoursRangeException"] = hours_range_exception
        if week_days is not UNSET:
            field_dict["weekDays"] = week_days
        if week_days_exception is not UNSET:
            field_dict["weekDaysException"] = week_days_exception
        if dates_range is not UNSET:
            field_dict["datesRange"] = dates_range
        if dates_range_exception is not UNSET:
            field_dict["datesRangeException"] = dates_range_exception

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dates_range import DatesRange
        from ..models.hours_range import HoursRange
        from ..models.link import Link
        d = dict(src_dict)
        condition_type = ConditionConditionType(d.pop("conditionType"))




        name = d.pop("name")

        def _parse_link(data: object) -> Link | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                link_type_1 = Link.from_dict(data)



                return link_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Link | None | Unset, data)

        link = _parse_link(d.pop("link", UNSET))


        is_negate = d.pop("isNegate", UNSET)

        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = UUID(_id)




        description = d.pop("description", UNSET)

        _hours_range = d.pop("hoursRange", UNSET)
        hours_range: HoursRange | Unset
        if isinstance(_hours_range,  Unset):
            hours_range = UNSET
        else:
            hours_range = HoursRange.from_dict(_hours_range)




        _hours_range_exception = d.pop("hoursRangeException", UNSET)
        hours_range_exception: HoursRange | Unset
        if isinstance(_hours_range_exception,  Unset):
            hours_range_exception = UNSET
        else:
            hours_range_exception = HoursRange.from_dict(_hours_range_exception)




        _week_days = d.pop("weekDays", UNSET)
        week_days: list[WeekDayEnum] | Unset = UNSET
        if _week_days is not UNSET:
            week_days = []
            for week_days_item_data in _week_days:
                week_days_item = WeekDayEnum(week_days_item_data)



                week_days.append(week_days_item)


        _week_days_exception = d.pop("weekDaysException", UNSET)
        week_days_exception: list[WeekDayEnum] | Unset = UNSET
        if _week_days_exception is not UNSET:
            week_days_exception = []
            for week_days_exception_item_data in _week_days_exception:
                week_days_exception_item = WeekDayEnum(week_days_exception_item_data)



                week_days_exception.append(week_days_exception_item)


        _dates_range = d.pop("datesRange", UNSET)
        dates_range: DatesRange | Unset
        if isinstance(_dates_range,  Unset):
            dates_range = UNSET
        else:
            dates_range = DatesRange.from_dict(_dates_range)




        _dates_range_exception = d.pop("datesRangeException", UNSET)
        dates_range_exception: DatesRange | Unset
        if isinstance(_dates_range_exception,  Unset):
            dates_range_exception = UNSET
        else:
            dates_range_exception = DatesRange.from_dict(_dates_range_exception)




        time_and_date_condition = cls(
            condition_type=condition_type,
            name=name,
            link=link,
            is_negate=is_negate,
            id=id,
            description=description,
            hours_range=hours_range,
            hours_range_exception=hours_range_exception,
            week_days=week_days,
            week_days_exception=week_days_exception,
            dates_range=dates_range,
            dates_range_exception=dates_range_exception,
        )


        time_and_date_condition.additional_properties = d
        return time_and_date_condition

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
