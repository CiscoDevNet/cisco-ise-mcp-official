from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.service_name_service_type import ServiceNameServiceType
from ..types import UNSET, Unset






T = TypeVar("T", bound="ServiceName")



@_attrs_define
class ServiceName:
    

    name: str
    id: str
    service_type: ServiceNameServiceType
    """ Allowed Protocols OR Server Sequence """
    is_local_authorization: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id = self.id

        service_type = self.service_type.value

        is_local_authorization = self.is_local_authorization


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "id": id,
            "serviceType": service_type,
        })
        if is_local_authorization is not UNSET:
            field_dict["isLocalAuthorization"] = is_local_authorization

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        id = d.pop("id")

        service_type = ServiceNameServiceType(d.pop("serviceType"))




        is_local_authorization = d.pop("isLocalAuthorization", UNSET)

        service_name = cls(
            name=name,
            id=id,
            service_type=service_type,
            is_local_authorization=is_local_authorization,
        )


        service_name.additional_properties = d
        return service_name

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
