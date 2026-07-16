# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.node_status import NodeStatus
from ..models.roles_item import RolesItem
from ..models.services_item import ServicesItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentNode")


@_attrs_define
class DeploymentNode:
    """
    Example:
        TBD

    """

    hostname: str
    fqdn: str
    ip_address: str
    services: list[ServicesItem]
    roles: list[RolesItem] | Unset = UNSET
    node_status: NodeStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hostname = self.hostname

        fqdn = self.fqdn

        ip_address = self.ip_address

        services = []
        for componentsschemas_services_item_data in self.services:
            componentsschemas_services_item = componentsschemas_services_item_data.value
            services.append(componentsschemas_services_item)

        roles: list[str] | Unset = UNSET
        if not isinstance(self.roles, Unset):
            roles = []
            for componentsschemas_roles_item_data in self.roles:
                componentsschemas_roles_item = componentsschemas_roles_item_data.value
                roles.append(componentsschemas_roles_item)

        node_status: str | Unset = UNSET
        if not isinstance(self.node_status, Unset):
            node_status = self.node_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hostname": hostname,
                "fqdn": fqdn,
                "ipAddress": ip_address,
                "services": services,
            }
        )
        if roles is not UNSET:
            field_dict["roles"] = roles
        if node_status is not UNSET:
            field_dict["nodeStatus"] = node_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hostname = d.pop("hostname")

        fqdn = d.pop("fqdn")

        ip_address = d.pop("ipAddress")

        services = []
        _services = d.pop("services")
        for componentsschemas_services_item_data in _services:
            componentsschemas_services_item = ServicesItem(componentsschemas_services_item_data)

            services.append(componentsschemas_services_item)

        _roles = d.pop("roles", UNSET)
        roles: list[RolesItem] | Unset = UNSET
        if _roles is not UNSET:
            roles = []
            for componentsschemas_roles_item_data in _roles:
                componentsschemas_roles_item = RolesItem(componentsschemas_roles_item_data)

                roles.append(componentsschemas_roles_item)

        _node_status = d.pop("nodeStatus", UNSET)
        node_status: NodeStatus | Unset
        if isinstance(_node_status, Unset):
            node_status = UNSET
        else:
            node_status = NodeStatus(_node_status)

        deployment_node = cls(
            hostname=hostname,
            fqdn=fqdn,
            ip_address=ip_address,
            services=services,
            roles=roles,
            node_status=node_status,
        )

        deployment_node.additional_properties = d
        return deployment_node

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
