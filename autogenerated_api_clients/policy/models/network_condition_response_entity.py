from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.network_condition import NetworkCondition





T = TypeVar("T", bound="NetworkConditionResponseEntity")



@_attrs_define
class NetworkConditionResponseEntity:
    """ 
        Example:
            {'version': '1.0.0', 'respose': {'name': 'Endstation condition 1', 'id': 'ad947f38-7063-4da2-8723-652e0ca2ea41',
                'description': 'Optional description', 'conditionType': 'EndstationCondition', 'ipAddrList': ['3.3.3.3',
                '4.4.4.4'], 'macAddrList': None, 'cliDnisList': None, 'link': {'rel': 'self', 'href':
                'https://{{ISE_IP}}/api/v1/policy/{{protocol}}/network-condition/ad947f38-7063-4da2-8723-652e0ca2ea41', 'type':
                'application/json'}}}

     """

    version: str
    response: NetworkCondition
    """ Unique network conditions to restrict access to the network """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.network_condition import NetworkCondition
        version = self.version

        response = self.response.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "version": version,
            "response": response,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.network_condition import NetworkCondition
        d = dict(src_dict)
        version = d.pop("version")

        response = NetworkCondition.from_dict(d.pop("response"))




        network_condition_response_entity = cls(
            version=version,
            response=response,
        )


        network_condition_response_entity.additional_properties = d
        return network_condition_response_entity

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
