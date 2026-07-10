from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.suppressed_endpoint_state import SuppressedEndpointState
from ..types import UNSET, Unset






T = TypeVar("T", bound="SuppressedEndpoint")



@_attrs_define
class SuppressedEndpoint:
    """ ISE Suppressed Endpoint

     """

    identifier: str
    state: SuppressedEndpointState | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "identifier": identifier,
        })
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identifier = d.pop("identifier")

        _state = d.pop("state", UNSET)
        state: SuppressedEndpointState | Unset
        if isinstance(_state,  Unset):
            state = UNSET
        else:
            state = SuppressedEndpointState(_state)




        suppressed_endpoint = cls(
            identifier=identifier,
            state=state,
        )


        suppressed_endpoint.additional_properties = d
        return suppressed_endpoint

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
