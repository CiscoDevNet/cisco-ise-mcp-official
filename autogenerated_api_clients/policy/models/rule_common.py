from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.rule_common_state import RuleCommonState
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.condition import Condition





T = TypeVar("T", bound="RuleCommon")



@_attrs_define
class RuleCommon:
    """ Common attributes in rule authentication/authorization

     """

    name: str
    """ Rule name, [Valid characters are alphanumerics, underscore, hyphen, space, period, parentheses] """
    id: UUID | Unset = UNSET
    """ The identifier of the rule """
    hit_counts: int | Unset = 0
    """ The amount of times the rule was matched """
    rank: int | Unset = 0
    """ The rank(priority) in relation to other rules. Lower rank is higher priority. """
    state: RuleCommonState | Unset = RuleCommonState.ENABLED
    """ The state that the rule is in. A disabled rule cannot be matched. """
    default: bool | Unset = False
    """ Indicates if this rule is the default one """
    condition: Condition | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.condition import Condition
        name = self.name

        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        hit_counts = self.hit_counts

        rank = self.rank

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value


        default = self.default

        condition: dict[str, Any] | None | Unset
        if isinstance(self.condition, Unset):
            condition = UNSET
        elif isinstance(self.condition, Condition):
            condition = self.condition.to_dict()
        else:
            condition = self.condition


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if hit_counts is not UNSET:
            field_dict["hitCounts"] = hit_counts
        if rank is not UNSET:
            field_dict["rank"] = rank
        if state is not UNSET:
            field_dict["state"] = state
        if default is not UNSET:
            field_dict["default"] = default
        if condition is not UNSET:
            field_dict["condition"] = condition

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.condition import Condition
        d = dict(src_dict)
        name = d.pop("name")

        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = UUID(_id)




        hit_counts = d.pop("hitCounts", UNSET)

        rank = d.pop("rank", UNSET)

        _state = d.pop("state", UNSET)
        state: RuleCommonState | Unset
        if isinstance(_state,  Unset):
            state = UNSET
        else:
            state = RuleCommonState(_state)




        default = d.pop("default", UNSET)

        def _parse_condition(data: object) -> Condition | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                condition_type_1 = Condition.from_dict(data)



                return condition_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Condition | None | Unset, data)

        condition = _parse_condition(d.pop("condition", UNSET))


        rule_common = cls(
            name=name,
            id=id,
            hit_counts=hit_counts,
            rank=rank,
            state=state,
            default=default,
            condition=condition,
        )


        rule_common.additional_properties = d
        return rule_common

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
