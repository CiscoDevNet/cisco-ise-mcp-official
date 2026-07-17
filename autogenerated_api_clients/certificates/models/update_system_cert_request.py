# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.update_system_cert_request_expiration_ttl_units import UpdateSystemCertRequestExpirationTTLUnits
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="UpdateSystemCertRequest")



@_attrs_define
class UpdateSystemCertRequest:
    

    allow_portal_tag_transfer_for_same_subject: bool
    """ Allow overwriting the portal tag from matching certificate of same subject """
    allow_replacement_of_portal_group_tag: bool
    """ Allow Replacement of Portal Group Tag  """
    allow_role_transfer_for_same_subject: bool
    """ Allow transfer of roles for certificate with matching subject  """
    admin: Union[Unset, bool] = UNSET
    """ Use certificate to authenticate the Cisco ISE Admin Portal """
    description: Union[Unset, str] = UNSET
    """ Description of System Certificate """
    eap: Union[Unset, bool] = UNSET
    """ Use certificate for EAP protocols that use SSL/TLS tunneling """
    expiration_ttl_period: Union[Unset, int] = UNSET
    expiration_ttl_units: Union[Unset, UpdateSystemCertRequestExpirationTTLUnits] = UNSET
    ims: Union[Unset, bool] = UNSET
    """ Use certificate for the Cisco ISE Messaging Service """
    name: Union[Unset, str] = UNSET
    """ Name of the certificate """
    portal: Union[Unset, bool] = UNSET
    """ Use for portal """
    portal_group_tag: Union[Unset, str] = UNSET
    """ Set Group tag """
    pxgrid: Union[Unset, bool] = UNSET
    """ Use certificate for the pxGrid Controller """
    radius: Union[Unset, bool] = UNSET
    """ Use certificate for the RADSec server """
    renew_self_signed_certificate: Union[Unset, bool] = UNSET
    """ Renew Self-signed Certificate """
    saml: Union[Unset, bool] = UNSET
    """ Use certificate for SAML Signing """
    tacacs: Union[Unset, bool] = UNSET
    """ Use for TACACS Server """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        allow_portal_tag_transfer_for_same_subject = self.allow_portal_tag_transfer_for_same_subject

        allow_replacement_of_portal_group_tag = self.allow_replacement_of_portal_group_tag

        allow_role_transfer_for_same_subject = self.allow_role_transfer_for_same_subject

        admin = self.admin

        description = self.description

        eap = self.eap

        expiration_ttl_period = self.expiration_ttl_period

        expiration_ttl_units: Union[Unset, str] = UNSET
        if not isinstance(self.expiration_ttl_units, Unset):
            expiration_ttl_units = self.expiration_ttl_units.value


        ims = self.ims

        name = self.name

        portal = self.portal

        portal_group_tag = self.portal_group_tag

        pxgrid = self.pxgrid

        radius = self.radius

        renew_self_signed_certificate = self.renew_self_signed_certificate

        saml = self.saml

        tacacs = self.tacacs


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "allowPortalTagTransferForSameSubject": allow_portal_tag_transfer_for_same_subject,
            "allowReplacementOfPortalGroupTag": allow_replacement_of_portal_group_tag,
            "allowRoleTransferForSameSubject": allow_role_transfer_for_same_subject,
        })
        if admin is not UNSET:
            field_dict["admin"] = admin
        if description is not UNSET:
            field_dict["description"] = description
        if eap is not UNSET:
            field_dict["eap"] = eap
        if expiration_ttl_period is not UNSET:
            field_dict["expirationTTLPeriod"] = expiration_ttl_period
        if expiration_ttl_units is not UNSET:
            field_dict["expirationTTLUnits"] = expiration_ttl_units
        if ims is not UNSET:
            field_dict["ims"] = ims
        if name is not UNSET:
            field_dict["name"] = name
        if portal is not UNSET:
            field_dict["portal"] = portal
        if portal_group_tag is not UNSET:
            field_dict["portalGroupTag"] = portal_group_tag
        if pxgrid is not UNSET:
            field_dict["pxgrid"] = pxgrid
        if radius is not UNSET:
            field_dict["radius"] = radius
        if renew_self_signed_certificate is not UNSET:
            field_dict["renewSelfSignedCertificate"] = renew_self_signed_certificate
        if saml is not UNSET:
            field_dict["saml"] = saml
        if tacacs is not UNSET:
            field_dict["tacacs"] = tacacs

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_portal_tag_transfer_for_same_subject = d.pop("allowPortalTagTransferForSameSubject")

        allow_replacement_of_portal_group_tag = d.pop("allowReplacementOfPortalGroupTag")

        allow_role_transfer_for_same_subject = d.pop("allowRoleTransferForSameSubject")

        admin = d.pop("admin", UNSET)

        description = d.pop("description", UNSET)

        eap = d.pop("eap", UNSET)

        expiration_ttl_period = d.pop("expirationTTLPeriod", UNSET)

        _expiration_ttl_units = d.pop("expirationTTLUnits", UNSET)
        expiration_ttl_units: Union[Unset, UpdateSystemCertRequestExpirationTTLUnits]
        if isinstance(_expiration_ttl_units,  Unset):
            expiration_ttl_units = UNSET
        else:
            expiration_ttl_units = UpdateSystemCertRequestExpirationTTLUnits(_expiration_ttl_units)




        ims = d.pop("ims", UNSET)

        name = d.pop("name", UNSET)

        portal = d.pop("portal", UNSET)

        portal_group_tag = d.pop("portalGroupTag", UNSET)

        pxgrid = d.pop("pxgrid", UNSET)

        radius = d.pop("radius", UNSET)

        renew_self_signed_certificate = d.pop("renewSelfSignedCertificate", UNSET)

        saml = d.pop("saml", UNSET)

        tacacs = d.pop("tacacs", UNSET)

        update_system_cert_request = cls(
            allow_portal_tag_transfer_for_same_subject=allow_portal_tag_transfer_for_same_subject,
            allow_replacement_of_portal_group_tag=allow_replacement_of_portal_group_tag,
            allow_role_transfer_for_same_subject=allow_role_transfer_for_same_subject,
            admin=admin,
            description=description,
            eap=eap,
            expiration_ttl_period=expiration_ttl_period,
            expiration_ttl_units=expiration_ttl_units,
            ims=ims,
            name=name,
            portal=portal,
            portal_group_tag=portal_group_tag,
            pxgrid=pxgrid,
            radius=radius,
            renew_self_signed_certificate=renew_self_signed_certificate,
            saml=saml,
            tacacs=tacacs,
        )


        update_system_cert_request.additional_properties = d
        return update_system_cert_request

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
