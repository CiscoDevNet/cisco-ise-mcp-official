from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.open_api_endpoint_asset_connected_links_type_0 import OpenAPIEndpointAssetConnectedLinksType0
  from ..models.open_api_endpoint_custom_attributes_type_0 import OpenAPIEndpointCustomAttributesType0
  from ..models.open_api_endpoint_mdm_attributes_type_0 import OpenAPIEndpointMdmAttributesType0





T = TypeVar("T", bound="OpenAPIEndpoint")



@_attrs_define
class OpenAPIEndpoint:
    

    mac: str
    id: str | Unset = UNSET
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    custom_attributes: None | OpenAPIEndpointCustomAttributesType0 | Unset = UNSET
    mdm_attributes: None | OpenAPIEndpointMdmAttributesType0 | Unset = UNSET
    group_id: str | Unset = UNSET
    identity_store: str | Unset = UNSET
    identity_store_id: str | Unset = UNSET
    portal_user: str | Unset = UNSET
    profile_id: str | Unset = UNSET
    ip_address: str | Unset = UNSET
    ipv_6_address: str | Unset = UNSET
    vendor: str | Unset = UNSET
    product_id: str | Unset = UNSET
    serial_number: str | Unset = UNSET
    device_type: str | Unset = UNSET
    software_revision: str | Unset = UNSET
    hardware_revision: str | Unset = UNSET
    protocol: str | Unset = UNSET
    static_group_assignment: bool | Unset = UNSET
    static_profile_assignment: bool | Unset = UNSET
    asset_id: str | Unset = UNSET
    asset_name: str | Unset = UNSET
    asset_ip_address: str | Unset = UNSET
    asset_vendor: str | Unset = UNSET
    asset_product_id: str | Unset = UNSET
    asset_serial_number: str | Unset = UNSET
    asset_device_type: str | Unset = UNSET
    asset_sw_revision: str | Unset = UNSET
    asset_hw_revision: str | Unset = UNSET
    asset_protocol: str | Unset = UNSET
    asset_connected_links: None | OpenAPIEndpointAssetConnectedLinksType0 | Unset = UNSET
    mfc_info_hardware_model: str | Unset = UNSET
    mfc_info_operating_system: str | Unset = UNSET
    mfc_info_endpoint_type: str | Unset = UNSET
    mfc_info_hardware_manufacturer: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.open_api_endpoint_asset_connected_links_type_0 import OpenAPIEndpointAssetConnectedLinksType0
        from ..models.open_api_endpoint_custom_attributes_type_0 import OpenAPIEndpointCustomAttributesType0
        from ..models.open_api_endpoint_mdm_attributes_type_0 import OpenAPIEndpointMdmAttributesType0
        mac = self.mac

        id = self.id

        name = self.name

        description = self.description

        custom_attributes: dict[str, Any] | None | Unset
        if isinstance(self.custom_attributes, Unset):
            custom_attributes = UNSET
        elif isinstance(self.custom_attributes, OpenAPIEndpointCustomAttributesType0):
            custom_attributes = self.custom_attributes.to_dict()
        else:
            custom_attributes = self.custom_attributes

        mdm_attributes: dict[str, Any] | None | Unset
        if isinstance(self.mdm_attributes, Unset):
            mdm_attributes = UNSET
        elif isinstance(self.mdm_attributes, OpenAPIEndpointMdmAttributesType0):
            mdm_attributes = self.mdm_attributes.to_dict()
        else:
            mdm_attributes = self.mdm_attributes

        group_id = self.group_id

        identity_store = self.identity_store

        identity_store_id = self.identity_store_id

        portal_user = self.portal_user

        profile_id = self.profile_id

        ip_address = self.ip_address

        ipv_6_address = self.ipv_6_address

        vendor = self.vendor

        product_id = self.product_id

        serial_number = self.serial_number

        device_type = self.device_type

        software_revision = self.software_revision

        hardware_revision = self.hardware_revision

        protocol = self.protocol

        static_group_assignment = self.static_group_assignment

        static_profile_assignment = self.static_profile_assignment

        asset_id = self.asset_id

        asset_name = self.asset_name

        asset_ip_address = self.asset_ip_address

        asset_vendor = self.asset_vendor

        asset_product_id = self.asset_product_id

        asset_serial_number = self.asset_serial_number

        asset_device_type = self.asset_device_type

        asset_sw_revision = self.asset_sw_revision

        asset_hw_revision = self.asset_hw_revision

        asset_protocol = self.asset_protocol

        asset_connected_links: dict[str, Any] | None | Unset
        if isinstance(self.asset_connected_links, Unset):
            asset_connected_links = UNSET
        elif isinstance(self.asset_connected_links, OpenAPIEndpointAssetConnectedLinksType0):
            asset_connected_links = self.asset_connected_links.to_dict()
        else:
            asset_connected_links = self.asset_connected_links

        mfc_info_hardware_model = self.mfc_info_hardware_model

        mfc_info_operating_system = self.mfc_info_operating_system

        mfc_info_endpoint_type = self.mfc_info_endpoint_type

        mfc_info_hardware_manufacturer = self.mfc_info_hardware_manufacturer


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "mac": mac,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if custom_attributes is not UNSET:
            field_dict["customAttributes"] = custom_attributes
        if mdm_attributes is not UNSET:
            field_dict["mdmAttributes"] = mdm_attributes
        if group_id is not UNSET:
            field_dict["groupId"] = group_id
        if identity_store is not UNSET:
            field_dict["identityStore"] = identity_store
        if identity_store_id is not UNSET:
            field_dict["identityStoreId"] = identity_store_id
        if portal_user is not UNSET:
            field_dict["portalUser"] = portal_user
        if profile_id is not UNSET:
            field_dict["profileId"] = profile_id
        if ip_address is not UNSET:
            field_dict["ipAddress"] = ip_address
        if ipv_6_address is not UNSET:
            field_dict["ipv6Address"] = ipv_6_address
        if vendor is not UNSET:
            field_dict["vendor"] = vendor
        if product_id is not UNSET:
            field_dict["productId"] = product_id
        if serial_number is not UNSET:
            field_dict["serialNumber"] = serial_number
        if device_type is not UNSET:
            field_dict["deviceType"] = device_type
        if software_revision is not UNSET:
            field_dict["softwareRevision"] = software_revision
        if hardware_revision is not UNSET:
            field_dict["hardwareRevision"] = hardware_revision
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if static_group_assignment is not UNSET:
            field_dict["staticGroupAssignment"] = static_group_assignment
        if static_profile_assignment is not UNSET:
            field_dict["staticProfileAssignment"] = static_profile_assignment
        if asset_id is not UNSET:
            field_dict["assetId"] = asset_id
        if asset_name is not UNSET:
            field_dict["assetName"] = asset_name
        if asset_ip_address is not UNSET:
            field_dict["assetIpAddress"] = asset_ip_address
        if asset_vendor is not UNSET:
            field_dict["assetVendor"] = asset_vendor
        if asset_product_id is not UNSET:
            field_dict["assetProductId"] = asset_product_id
        if asset_serial_number is not UNSET:
            field_dict["assetSerialNumber"] = asset_serial_number
        if asset_device_type is not UNSET:
            field_dict["assetDeviceType"] = asset_device_type
        if asset_sw_revision is not UNSET:
            field_dict["assetSwRevision"] = asset_sw_revision
        if asset_hw_revision is not UNSET:
            field_dict["assetHwRevision"] = asset_hw_revision
        if asset_protocol is not UNSET:
            field_dict["assetProtocol"] = asset_protocol
        if asset_connected_links is not UNSET:
            field_dict["assetConnectedLinks"] = asset_connected_links
        if mfc_info_hardware_model is not UNSET:
            field_dict["mfcInfoHardwareModel"] = mfc_info_hardware_model
        if mfc_info_operating_system is not UNSET:
            field_dict["mfcInfoOperatingSystem"] = mfc_info_operating_system
        if mfc_info_endpoint_type is not UNSET:
            field_dict["mfcInfoEndpointType"] = mfc_info_endpoint_type
        if mfc_info_hardware_manufacturer is not UNSET:
            field_dict["mfcInfoHardwareManufacturer"] = mfc_info_hardware_manufacturer

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_api_endpoint_asset_connected_links_type_0 import OpenAPIEndpointAssetConnectedLinksType0
        from ..models.open_api_endpoint_custom_attributes_type_0 import OpenAPIEndpointCustomAttributesType0
        from ..models.open_api_endpoint_mdm_attributes_type_0 import OpenAPIEndpointMdmAttributesType0
        d = dict(src_dict)
        mac = d.pop("mac")

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        def _parse_custom_attributes(data: object) -> None | OpenAPIEndpointCustomAttributesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_attributes_type_0 = OpenAPIEndpointCustomAttributesType0.from_dict(data)



                return custom_attributes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OpenAPIEndpointCustomAttributesType0 | Unset, data)

        custom_attributes = _parse_custom_attributes(d.pop("customAttributes", UNSET))


        def _parse_mdm_attributes(data: object) -> None | OpenAPIEndpointMdmAttributesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                mdm_attributes_type_0 = OpenAPIEndpointMdmAttributesType0.from_dict(data)



                return mdm_attributes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OpenAPIEndpointMdmAttributesType0 | Unset, data)

        mdm_attributes = _parse_mdm_attributes(d.pop("mdmAttributes", UNSET))


        group_id = d.pop("groupId", UNSET)

        identity_store = d.pop("identityStore", UNSET)

        identity_store_id = d.pop("identityStoreId", UNSET)

        portal_user = d.pop("portalUser", UNSET)

        profile_id = d.pop("profileId", UNSET)

        ip_address = d.pop("ipAddress", UNSET)

        ipv_6_address = d.pop("ipv6Address", UNSET)

        vendor = d.pop("vendor", UNSET)

        product_id = d.pop("productId", UNSET)

        serial_number = d.pop("serialNumber", UNSET)

        device_type = d.pop("deviceType", UNSET)

        software_revision = d.pop("softwareRevision", UNSET)

        hardware_revision = d.pop("hardwareRevision", UNSET)

        protocol = d.pop("protocol", UNSET)

        static_group_assignment = d.pop("staticGroupAssignment", UNSET)

        static_profile_assignment = d.pop("staticProfileAssignment", UNSET)

        asset_id = d.pop("assetId", UNSET)

        asset_name = d.pop("assetName", UNSET)

        asset_ip_address = d.pop("assetIpAddress", UNSET)

        asset_vendor = d.pop("assetVendor", UNSET)

        asset_product_id = d.pop("assetProductId", UNSET)

        asset_serial_number = d.pop("assetSerialNumber", UNSET)

        asset_device_type = d.pop("assetDeviceType", UNSET)

        asset_sw_revision = d.pop("assetSwRevision", UNSET)

        asset_hw_revision = d.pop("assetHwRevision", UNSET)

        asset_protocol = d.pop("assetProtocol", UNSET)

        def _parse_asset_connected_links(data: object) -> None | OpenAPIEndpointAssetConnectedLinksType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                asset_connected_links_type_0 = OpenAPIEndpointAssetConnectedLinksType0.from_dict(data)



                return asset_connected_links_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OpenAPIEndpointAssetConnectedLinksType0 | Unset, data)

        asset_connected_links = _parse_asset_connected_links(d.pop("assetConnectedLinks", UNSET))


        mfc_info_hardware_model = d.pop("mfcInfoHardwareModel", UNSET)

        mfc_info_operating_system = d.pop("mfcInfoOperatingSystem", UNSET)

        mfc_info_endpoint_type = d.pop("mfcInfoEndpointType", UNSET)

        mfc_info_hardware_manufacturer = d.pop("mfcInfoHardwareManufacturer", UNSET)

        open_api_endpoint = cls(
            mac=mac,
            id=id,
            name=name,
            description=description,
            custom_attributes=custom_attributes,
            mdm_attributes=mdm_attributes,
            group_id=group_id,
            identity_store=identity_store,
            identity_store_id=identity_store_id,
            portal_user=portal_user,
            profile_id=profile_id,
            ip_address=ip_address,
            ipv_6_address=ipv_6_address,
            vendor=vendor,
            product_id=product_id,
            serial_number=serial_number,
            device_type=device_type,
            software_revision=software_revision,
            hardware_revision=hardware_revision,
            protocol=protocol,
            static_group_assignment=static_group_assignment,
            static_profile_assignment=static_profile_assignment,
            asset_id=asset_id,
            asset_name=asset_name,
            asset_ip_address=asset_ip_address,
            asset_vendor=asset_vendor,
            asset_product_id=asset_product_id,
            asset_serial_number=asset_serial_number,
            asset_device_type=asset_device_type,
            asset_sw_revision=asset_sw_revision,
            asset_hw_revision=asset_hw_revision,
            asset_protocol=asset_protocol,
            asset_connected_links=asset_connected_links,
            mfc_info_hardware_model=mfc_info_hardware_model,
            mfc_info_operating_system=mfc_info_operating_system,
            mfc_info_endpoint_type=mfc_info_endpoint_type,
            mfc_info_hardware_manufacturer=mfc_info_hardware_manufacturer,
        )


        open_api_endpoint.additional_properties = d
        return open_api_endpoint

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
