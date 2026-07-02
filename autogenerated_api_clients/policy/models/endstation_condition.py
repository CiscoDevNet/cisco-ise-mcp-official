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





T = TypeVar("T", bound="EndstationCondition")



@_attrs_define
class EndstationCondition:
    

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
    mac_addr_list: list[str] | Unset = UNSET
    """ <p>This field should contain Endstation MAC address, comma, and Destination MAC addresses.<br> Each Max
    address must include twelve hexadecimal digits using formats nn:nn:nn:nn:nn:nn or nn-nn-nn-nn-nn-nn or
    nnnn.nnnn.nnnn or nnnnnnnnnnnn.<br> Line format - Endstation MAC,Destination MAC </p> """
    cli_dnis_list: list[str] | Unset = UNSET
    """ <p>This field should contain a Caller ID (CLI), comma, and Called ID (DNIS).<br> Line format -  Caller ID
    (CLI), Called ID (DNIS)</p> """
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



        mac_addr_list: list[str] | Unset = UNSET
        if not isinstance(self.mac_addr_list, Unset):
            mac_addr_list = self.mac_addr_list



        cli_dnis_list: list[str] | Unset = UNSET
        if not isinstance(self.cli_dnis_list, Unset):
            cli_dnis_list = self.cli_dnis_list




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
        if mac_addr_list is not UNSET:
            field_dict["macAddrList"] = mac_addr_list
        if cli_dnis_list is not UNSET:
            field_dict["cliDnisList"] = cli_dnis_list

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


        mac_addr_list = cast(list[str], d.pop("macAddrList", UNSET))


        cli_dnis_list = cast(list[str], d.pop("cliDnisList", UNSET))


        endstation_condition = cls(
            name=name,
            condition_type=condition_type,
            link=link,
            id=id,
            description=description,
            ip_addr_list=ip_addr_list,
            mac_addr_list=mac_addr_list,
            cli_dnis_list=cli_dnis_list,
        )


        endstation_condition.additional_properties = d
        return endstation_condition

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
