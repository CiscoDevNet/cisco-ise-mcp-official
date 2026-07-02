from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.network_condition_condition_type import NetworkConditionConditionType
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.link import Link





T = TypeVar("T", bound="DeviceCondition")



@_attrs_define
class DeviceCondition:
    

    name: str
    """ Network Condition name """
    condition_type: NetworkConditionConditionType
    """ This field determines the content of the conditions field """
    link: Link | Unset = UNSET
    id: UUID | Unset = UNSET
    description: str | Unset = UNSET
    ip_addr_list: list[str] | Unset = UNSET
    """ <p>This field should contain IP address or subnet.<br> IP address can be IPV4 format (n.n.n.n) or IPV6
    format (n:n:n:n:n:n:n:n).<br> IP subnet can be IPV4 format (n.n.n.n/m) or IPV6 format (n:n:n:n:n:n:n:n/m).<br>
    Line format - IP Address or subnet</p> """
    device_list: list[str] | Unset = UNSET
    """ <p>This field should contain Device Name. The device name must be the same as the name field in a Network
    Device object. Line format - Device Name</p> """
    device_group_list: list[str] | Unset = UNSET
    """ <p>This field should contain a tuple with NDG Root, comma, and an NDG (that it under the root).<br> Line
    format - NDG Root Name, NDG, Port</p> """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        name = self.name

        condition_type = self.condition_type.value

        link: dict[str, Any] | Unset = UNSET
        if not isinstance(self.link, Unset):
            link = self.link.to_dict()

        id: str | Unset = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        description = self.description

        ip_addr_list: list[str] | Unset = UNSET
        if not isinstance(self.ip_addr_list, Unset):
            ip_addr_list = self.ip_addr_list



        device_list: list[str] | Unset = UNSET
        if not isinstance(self.device_list, Unset):
            device_list = self.device_list



        device_group_list: list[str] | Unset = UNSET
        if not isinstance(self.device_group_list, Unset):
            device_group_list = self.device_group_list




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "conditionType": condition_type,
        })
        if link is not UNSET:
            field_dict["link"] = link
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if ip_addr_list is not UNSET:
            field_dict["ipAddrList"] = ip_addr_list
        if device_list is not UNSET:
            field_dict["deviceList"] = device_list
        if device_group_list is not UNSET:
            field_dict["deviceGroupList"] = device_group_list

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        d = dict(src_dict)
        name = d.pop("name")

        condition_type = NetworkConditionConditionType(d.pop("conditionType"))




        _link = d.pop("link", UNSET)
        link: Link | Unset
        if isinstance(_link,  Unset):
            link = UNSET
        else:
            link = Link.from_dict(_link)




        _id = d.pop("id", UNSET)
        id: UUID | Unset
        if isinstance(_id,  Unset):
            id = UNSET
        else:
            id = UUID(_id)




        description = d.pop("description", UNSET)

        ip_addr_list = cast(list[str], d.pop("ipAddrList", UNSET))


        device_list = cast(list[str], d.pop("deviceList", UNSET))


        device_group_list = cast(list[str], d.pop("deviceGroupList", UNSET))


        device_condition = cls(
            name=name,
            condition_type=condition_type,
            link=link,
            id=id,
            description=description,
            ip_addr_list=ip_addr_list,
            device_list=device_list,
            device_group_list=device_group_list,
        )


        device_condition.additional_properties = d
        return device_condition

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
