# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

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





T = TypeVar("T", bound="RuleAuthentication")



@_attrs_define
class RuleAuthentication:
    """ Rule for authentication in Network Access/Device Admin

     """

    rule: RuleCommon | Unset = UNSET
    """ Common attributes in rule authentication/authorization """
    identity_source_name: str | Unset = 'Internal Users'
    """ Identity source name from the identity stores """
    if_auth_fail: str | Unset = 'reject'
    """ Action to perform when authentication fails such as Bad credentials, disabled user and so on """
    if_user_not_found: str | Unset = 'reject'
    """ Action to perform when user is not found in any of identity stores """
    if_process_fail: str | Unset = 'drop'
    """ Action to perform when ISE is uanble to access the identity database """
    link: Link | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_common import RuleCommon
        from ..models.link import Link
        rule: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rule, Unset):
            rule = self.rule.to_dict()

        identity_source_name = self.identity_source_name

        if_auth_fail = self.if_auth_fail

        if_user_not_found = self.if_user_not_found

        if_process_fail = self.if_process_fail

        link: dict[str, Any] | Unset = UNSET
        if not isinstance(self.link, Unset):
            link = self.link.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if rule is not UNSET:
            field_dict["rule"] = rule
        if identity_source_name is not UNSET:
            field_dict["identitySourceName"] = identity_source_name
        if if_auth_fail is not UNSET:
            field_dict["ifAuthFail"] = if_auth_fail
        if if_user_not_found is not UNSET:
            field_dict["ifUserNotFound"] = if_user_not_found
        if if_process_fail is not UNSET:
            field_dict["ifProcessFail"] = if_process_fail
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




        identity_source_name = d.pop("identitySourceName", UNSET)

        if_auth_fail = d.pop("ifAuthFail", UNSET)

        if_user_not_found = d.pop("ifUserNotFound", UNSET)

        if_process_fail = d.pop("ifProcessFail", UNSET)

        _link = d.pop("link", UNSET)
        link: Link | Unset
        if isinstance(_link,  Unset):
            link = UNSET
        else:
            link = Link.from_dict(_link)




        rule_authentication = cls(
            rule=rule,
            identity_source_name=identity_source_name,
            if_auth_fail=if_auth_fail,
            if_user_not_found=if_user_not_found,
            if_process_fail=if_process_fail,
            link=link,
        )


        rule_authentication.additional_properties = d
        return rule_authentication

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
