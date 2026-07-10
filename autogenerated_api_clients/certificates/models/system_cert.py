from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="SystemCert")



@_attrs_define
class SystemCert:
    

    allow_extended_validity: bool
    """ Allow import of certificates with validity greater than 398 days  """
    allow_out_of_date_cert: bool
    """ Allow out of date certificates  """
    allow_portal_tag_transfer_for_same_subject: bool
    """ Allow overwriting the portal tag from matching certificate of same subject """
    allow_replacement_of_certificates: bool
    """ Allow Replacement of certificates  """
    allow_replacement_of_portal_group_tag: bool
    """ Allow Replacement of Portal Group Tag  """
    allow_role_transfer_for_same_subject: bool
    """ Allow transfer of roles for certificate with matching subject  """
    allow_sha1_certificates: bool
    """ Allow SHA1 based certificates  """
    data: str
    """ Certificate Content  """
    private_key_data: str
    """ Private Key data  """
    admin: Union[Unset, bool] = UNSET
    """ Use certificate to authenticate the Cisco ISE Admin Portal """
    allow_wild_card_certificates: Union[Unset, bool] = UNSET
    """ Allow Wildcard certificates """
    eap: Union[Unset, bool] = UNSET
    """ Use certificate for EAP protocols that use SSL/TLS tunneling """
    ims: Union[Unset, bool] = UNSET
    """ Use certificate for the Cisco ISE Messaging Service """
    name: Union[Unset, str] = UNSET
    """ Name of the certificate """
    password: Union[Unset, str] = UNSET
    """ Certificate Password . """
    portal: Union[Unset, bool] = UNSET
    """ Use for portal """
    portal_group_tag: Union[Unset, str] = UNSET
    """ Set Group tag """
    pxgrid: Union[Unset, bool] = UNSET
    """ Use certificate for the pxGrid Controller """
    radius: Union[Unset, bool] = UNSET
    """ Use certificate for the RADSec server """
    saml: Union[Unset, bool] = UNSET
    """ Use certificate for SAML Signing """
    tacacs: Union[Unset, bool] = UNSET
    """ Use certificate for TACACS Server """
    validate_certificate_extensions: Union[Unset, bool] = UNSET
    """ Validate certificate extensions """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        allow_extended_validity = self.allow_extended_validity

        allow_out_of_date_cert = self.allow_out_of_date_cert

        allow_portal_tag_transfer_for_same_subject = self.allow_portal_tag_transfer_for_same_subject

        allow_replacement_of_certificates = self.allow_replacement_of_certificates

        allow_replacement_of_portal_group_tag = self.allow_replacement_of_portal_group_tag

        allow_role_transfer_for_same_subject = self.allow_role_transfer_for_same_subject

        allow_sha1_certificates = self.allow_sha1_certificates

        data = self.data

        private_key_data = self.private_key_data

        admin = self.admin

        allow_wild_card_certificates = self.allow_wild_card_certificates

        eap = self.eap

        ims = self.ims

        name = self.name

        password = self.password

        portal = self.portal

        portal_group_tag = self.portal_group_tag

        pxgrid = self.pxgrid

        radius = self.radius

        saml = self.saml

        tacacs = self.tacacs

        validate_certificate_extensions = self.validate_certificate_extensions


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "allowExtendedValidity": allow_extended_validity,
            "allowOutOfDateCert": allow_out_of_date_cert,
            "allowPortalTagTransferForSameSubject": allow_portal_tag_transfer_for_same_subject,
            "allowReplacementOfCertificates": allow_replacement_of_certificates,
            "allowReplacementOfPortalGroupTag": allow_replacement_of_portal_group_tag,
            "allowRoleTransferForSameSubject": allow_role_transfer_for_same_subject,
            "allowSHA1Certificates": allow_sha1_certificates,
            "data": data,
            "privateKeyData": private_key_data,
        })
        if admin is not UNSET:
            field_dict["admin"] = admin
        if allow_wild_card_certificates is not UNSET:
            field_dict["allowWildCardCertificates"] = allow_wild_card_certificates
        if eap is not UNSET:
            field_dict["eap"] = eap
        if ims is not UNSET:
            field_dict["ims"] = ims
        if name is not UNSET:
            field_dict["name"] = name
        if password is not UNSET:
            field_dict["password"] = password
        if portal is not UNSET:
            field_dict["portal"] = portal
        if portal_group_tag is not UNSET:
            field_dict["portalGroupTag"] = portal_group_tag
        if pxgrid is not UNSET:
            field_dict["pxgrid"] = pxgrid
        if radius is not UNSET:
            field_dict["radius"] = radius
        if saml is not UNSET:
            field_dict["saml"] = saml
        if tacacs is not UNSET:
            field_dict["tacacs"] = tacacs
        if validate_certificate_extensions is not UNSET:
            field_dict["validateCertificateExtensions"] = validate_certificate_extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_extended_validity = d.pop("allowExtendedValidity")

        allow_out_of_date_cert = d.pop("allowOutOfDateCert")

        allow_portal_tag_transfer_for_same_subject = d.pop("allowPortalTagTransferForSameSubject")

        allow_replacement_of_certificates = d.pop("allowReplacementOfCertificates")

        allow_replacement_of_portal_group_tag = d.pop("allowReplacementOfPortalGroupTag")

        allow_role_transfer_for_same_subject = d.pop("allowRoleTransferForSameSubject")

        allow_sha1_certificates = d.pop("allowSHA1Certificates")

        data = d.pop("data")

        private_key_data = d.pop("privateKeyData")

        admin = d.pop("admin", UNSET)

        allow_wild_card_certificates = d.pop("allowWildCardCertificates", UNSET)

        eap = d.pop("eap", UNSET)

        ims = d.pop("ims", UNSET)

        name = d.pop("name", UNSET)

        password = d.pop("password", UNSET)

        portal = d.pop("portal", UNSET)

        portal_group_tag = d.pop("portalGroupTag", UNSET)

        pxgrid = d.pop("pxgrid", UNSET)

        radius = d.pop("radius", UNSET)

        saml = d.pop("saml", UNSET)

        tacacs = d.pop("tacacs", UNSET)

        validate_certificate_extensions = d.pop("validateCertificateExtensions", UNSET)

        system_cert = cls(
            allow_extended_validity=allow_extended_validity,
            allow_out_of_date_cert=allow_out_of_date_cert,
            allow_portal_tag_transfer_for_same_subject=allow_portal_tag_transfer_for_same_subject,
            allow_replacement_of_certificates=allow_replacement_of_certificates,
            allow_replacement_of_portal_group_tag=allow_replacement_of_portal_group_tag,
            allow_role_transfer_for_same_subject=allow_role_transfer_for_same_subject,
            allow_sha1_certificates=allow_sha1_certificates,
            data=data,
            private_key_data=private_key_data,
            admin=admin,
            allow_wild_card_certificates=allow_wild_card_certificates,
            eap=eap,
            ims=ims,
            name=name,
            password=password,
            portal=portal,
            portal_group_tag=portal_group_tag,
            pxgrid=pxgrid,
            radius=radius,
            saml=saml,
            tacacs=tacacs,
            validate_certificate_extensions=validate_certificate_extensions,
        )


        system_cert.additional_properties = d
        return system_cert

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
