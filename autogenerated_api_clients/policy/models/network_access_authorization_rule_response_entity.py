from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.rule_authorization_network_access import RuleAuthorizationNetworkAccess





T = TypeVar("T", bound="NetworkAccessAuthorizationRuleResponseEntity")



@_attrs_define
class NetworkAccessAuthorizationRuleResponseEntity:
    """ 
        Example:
            {'version': '1.0.0', 'response': {'rule': {'default': False, 'id': 'c841b537-45fb-4c3a-a1ae-baeb3e4c427a',
                'name': 'Authorization Rule 1', 'hitCounts': 0, 'rank': 0, 'state': 'enabled', 'condition': {'conditionType':
                'ConditionAttributes', 'isNegate': False, 'dictionaryName': 'Network Access', 'attributeName': 'Device IP
                Address', 'operator': 'ipEquals', 'attributeValue': '10.0.10.0'}}, 'profile': ['PermitAccess'], 'securityGroup':
                'BYOD', 'link': {'rel': 'self', 'href': 'https://{{ISE_IP}}/api/v1/policy/network-access/policy-set/{{policy-
                id}}/authorization/c841b537-45fb-4c3a-a1ae-baeb3e4c427a', 'type': 'application/json'}}}

     """

    version: str
    response: RuleAuthorizationNetworkAccess
    """ Authorization rule for network access """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_authorization_network_access import RuleAuthorizationNetworkAccess
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
        from ..models.rule_authorization_network_access import RuleAuthorizationNetworkAccess
        d = dict(src_dict)
        version = d.pop("version")

        response = RuleAuthorizationNetworkAccess.from_dict(d.pop("response"))




        network_access_authorization_rule_response_entity = cls(
            version=version,
            response=response,
        )


        network_access_authorization_rule_response_entity.additional_properties = d
        return network_access_authorization_rule_response_entity

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
