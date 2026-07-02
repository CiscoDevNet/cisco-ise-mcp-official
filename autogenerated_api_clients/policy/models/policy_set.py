from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.policy_set_state import PolicySetState
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.condition import Condition
  from ..models.link import Link





T = TypeVar("T", bound="PolicySet")



@_attrs_define
class PolicySet:
    """ Policy set structure

     """

    name: str
    """ Given name for the policy set, [Valid characters are alphanumerics, underscore, hyphen, space, period,
    parentheses] """
    service_name: str
    """ Policy set service identifier - Allowed Protocols,Server Sequence.. """
    id: UUID | Unset = UNSET
    """ Identifier for the policy set """
    description: str | Unset = UNSET
    """ The description for the policy set """
    hit_counts: int | Unset = 0
    """ The amount of times the policy was matched """
    rank: int | Unset = 0
    """ The rank(priority) in relation to other policy set. Lower rank is higher priority. """
    state: PolicySetState | Unset = PolicySetState.ENABLED
    """ The state that the policy set is in. A disabled policy set cannot be matched. """
    default: bool | Unset = False
    """ Flag which indicates if this policy set is the default one """
    condition: Condition | None | Unset = UNSET
    is_proxy: bool | Unset = False
    """ Flag which indicates if the policy set service is of type 'Proxy Sequence' or 'Allowed Protocols' """
    link: Link | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.condition import Condition
        from ..models.link import Link
        name = self.name

        service_name = self.service_name

        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        description = self.description

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

        is_proxy = self.is_proxy

        link: dict[str, Any] | Unset = UNSET
        if not isinstance(self.link, Unset):
            link = self.link.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "serviceName": service_name,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
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
        if is_proxy is not UNSET:
            field_dict["isProxy"] = is_proxy
        if link is not UNSET:
            field_dict["link"] = link

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.condition import Condition
        from ..models.link import Link
        d = dict(src_dict)
        name = d.pop("name")

        service_name = d.pop("serviceName")

        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = UUID(_id)




        description = d.pop("description", UNSET)

        hit_counts = d.pop("hitCounts", UNSET)

        rank = d.pop("rank", UNSET)

        _state = d.pop("state", UNSET)
        state: PolicySetState | Unset
        if isinstance(_state,  Unset):
            state = UNSET
        else:
            state = PolicySetState(_state)




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


        is_proxy = d.pop("isProxy", UNSET)

        _link = d.pop("link", UNSET)
        link: Link | Unset
        if isinstance(_link,  Unset):
            link = UNSET
        else:
            link = Link.from_dict(_link)




        policy_set = cls(
            name=name,
            service_name=service_name,
            id=id,
            description=description,
            hit_counts=hit_counts,
            rank=rank,
            state=state,
            default=default,
            condition=condition,
            is_proxy=is_proxy,
            link=link,
        )


        policy_set.additional_properties = d
        return policy_set

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
