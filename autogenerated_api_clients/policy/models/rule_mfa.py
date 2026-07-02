from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.link import Link
  from ..models.rule_common import RuleCommon





T = TypeVar("T", bound="RuleMfa")



@_attrs_define
class RuleMfa:
    """ Rule for MFA in Network Access/Device Admin

     """

    rule: RuleCommon | Unset = UNSET
    """ Common attributes in rule authentication/authorization """
    mfa_connection_name: str | Unset = 'api-XXXXXXXX.duosecurity.com'
    """ MFA Connection name for MFA """
    mfa_fail_action: str | Unset = 'REJECT'
    """ Action to perform when MFA fails """
    mfa_result_action: str | Unset = 'ACCEPT'
    """ Action to perform when MFA is successful """
    link: Link | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_common import RuleCommon
        from ..models.link import Link
        rule: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rule, Unset):
            rule = self.rule.to_dict()

        mfa_connection_name = self.mfa_connection_name

        mfa_fail_action = self.mfa_fail_action

        mfa_result_action = self.mfa_result_action

        link: dict[str, Any] | Unset = UNSET
        if not isinstance(self.link, Unset):
            link = self.link.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if rule is not UNSET:
            field_dict["rule"] = rule
        if mfa_connection_name is not UNSET:
            field_dict["mfaConnectionName"] = mfa_connection_name
        if mfa_fail_action is not UNSET:
            field_dict["mfaFailAction"] = mfa_fail_action
        if mfa_result_action is not UNSET:
            field_dict["mfaResultAction"] = mfa_result_action
        if link is not UNSET:
            field_dict["link"] = link

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        from ..models.rule_common import RuleCommon
        d = dict(src_dict)
        _rule = d.pop("rule", UNSET)
        rule: RuleCommon | Unset
        if isinstance(_rule,  Unset):
            rule = UNSET
        else:
            rule = RuleCommon.from_dict(_rule)




        mfa_connection_name = d.pop("mfaConnectionName", UNSET)

        mfa_fail_action = d.pop("mfaFailAction", UNSET)

        mfa_result_action = d.pop("mfaResultAction", UNSET)

        _link = d.pop("link", UNSET)
        link: Link | Unset
        if isinstance(_link,  Unset):
            link = UNSET
        else:
            link = Link.from_dict(_link)




        rule_mfa = cls(
            rule=rule,
            mfa_connection_name=mfa_connection_name,
            mfa_fail_action=mfa_fail_action,
            mfa_result_action=mfa_result_action,
            link=link,
        )


        rule_mfa.additional_properties = d
        return rule_mfa

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
