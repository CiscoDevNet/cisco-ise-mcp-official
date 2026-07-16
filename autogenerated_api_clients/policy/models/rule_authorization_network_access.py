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





T = TypeVar("T", bound="RuleAuthorizationNetworkAccess")



@_attrs_define
class RuleAuthorizationNetworkAccess:
    """ Authorization rule for network access

     """

    rule: RuleCommon
    """ Common attributes in rule authentication/authorization """
    profile: list[str] | Unset = UNSET
    """ The authorization profile/s """
    security_group: str | Unset = UNSET
    """ Security group used in authorization policies """
    link: Link | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_common import RuleCommon
        from ..models.link import Link
        rule = self.rule.to_dict()

        profile: list[str] | Unset = UNSET
        if not isinstance(self.profile, Unset):
            profile = self.profile



        security_group = self.security_group

        link: dict[str, Any] | Unset = UNSET
        if not isinstance(self.link, Unset):
            link = self.link.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "rule": rule,
        })
        if profile is not UNSET:
            field_dict["profile"] = profile
        if security_group is not UNSET:
            field_dict["securityGroup"] = security_group
        if link is not UNSET:
            field_dict["link"] = link

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        from ..models.rule_common import RuleCommon
        d = dict(src_dict)
        rule = RuleCommon.from_dict(d.pop("rule"))




        profile = cast(list[str], d.pop("profile", UNSET))


        security_group = d.pop("securityGroup", UNSET)

        _link = d.pop("link", UNSET)
        link: Link | Unset
        if isinstance(_link,  Unset):
            link = UNSET
        else:
            link = Link.from_dict(_link)




        rule_authorization_network_access = cls(
            rule=rule,
            profile=profile,
            security_group=security_group,
            link=link,
        )


        rule_authorization_network_access.additional_properties = d
        return rule_authorization_network_access

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
