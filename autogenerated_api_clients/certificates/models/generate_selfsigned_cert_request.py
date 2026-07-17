# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.generate_selfsigned_cert_request_digest_type import GenerateSelfsignedCertRequestDigestType
from ..models.generate_selfsigned_cert_request_expiration_ttl_unit import GenerateSelfsignedCertRequestExpirationTTLUnit
from ..models.generate_selfsigned_cert_request_key_length import GenerateSelfsignedCertRequestKeyLength
from ..models.generate_selfsigned_cert_request_key_type import GenerateSelfsignedCertRequestKeyType
from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="GenerateSelfsignedCertRequest")



@_attrs_define
class GenerateSelfsignedCertRequest:
    

    allow_extended_validity: bool
    """ Allow generation of self-signed certificate with validity greater than 398 days """
    allow_portal_tag_transfer_for_same_subject: bool
    """ Allow overwriting the portal tag from matching certificate of same subject """
    allow_replacement_of_certificates: bool
    """ Allow Replacement of certificates """
    allow_replacement_of_portal_group_tag: bool
    """ Allow Replacement of Portal Group Tag """
    allow_role_transfer_for_same_subject: bool
    """ Allow transfer of roles for certificate with matching subject """
    allow_san_dns_bad_name: bool
    """ Allow usage of SAN DNS Bad name """
    allow_san_dns_non_resolvable: bool
    """ Allow use of non resolvable Common Name or SAN Values """
    digest_type: GenerateSelfsignedCertRequestDigestType
    """ Digest to sign with """
    expiration_ttl: int
    """ Certificate expiration value """
    expiration_ttl_unit: GenerateSelfsignedCertRequestExpirationTTLUnit
    """ Certificate expiration unit """
    host_name: str
    """ Hostname of the Cisco ISE node in which self-signed certificate should be generated. """
    key_length: GenerateSelfsignedCertRequestKeyLength
    """ Bit size of public key """
    key_type: GenerateSelfsignedCertRequestKeyType
    """ Algorithm to use for certificate public key creation """
    admin: Union[Unset, bool] = UNSET
    """ Use certificate to authenticate the Cisco ISE Admin Portal """
    allow_wild_card_certificates: Union[Unset, bool] = UNSET
    """ Allow Wildcard Certificates """
    certificate_policies: Union[Unset, str] = UNSET
    """ Certificate Policies """
    eap: Union[Unset, bool] = UNSET
    """ Use certificate for EAP protocols that use SSL/TLS tunneling """
    name: Union[Unset, str] = UNSET
    """ Friendly name of the certificate. """
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
    san_dns: Union[Unset, list[str]] = UNSET
    """ Array of SAN (Subject Alternative Name) DNS entries """
    san_ip: Union[Unset, list[str]] = UNSET
    """ Array of SAN IP entries """
    san_uri: Union[Unset, list[str]] = UNSET
    """ Array of SAN URI entries """
    subject_city: Union[Unset, str] = UNSET
    """ Certificate city or locality (L) """
    subject_common_name: Union[Unset, str] = UNSET
    """ Certificate common name (CN) """
    subject_country: Union[Unset, str] = UNSET
    """ Certificate country (C) """
    subject_org: Union[Unset, str] = UNSET
    """ Certificate organization (O) """
    subject_org_unit: Union[Unset, str] = UNSET
    """ Certificate organizational unit (OU) """
    subject_state: Union[Unset, str] = UNSET
    """ Certificate state (ST) """
    tacacs: Union[Unset, bool] = UNSET
    """ Use certificate for TACACS Server """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        allow_extended_validity = self.allow_extended_validity

        allow_portal_tag_transfer_for_same_subject = self.allow_portal_tag_transfer_for_same_subject

        allow_replacement_of_certificates = self.allow_replacement_of_certificates

        allow_replacement_of_portal_group_tag = self.allow_replacement_of_portal_group_tag

        allow_role_transfer_for_same_subject = self.allow_role_transfer_for_same_subject

        allow_san_dns_bad_name = self.allow_san_dns_bad_name

        allow_san_dns_non_resolvable = self.allow_san_dns_non_resolvable

        digest_type = self.digest_type.value

        expiration_ttl = self.expiration_ttl

        expiration_ttl_unit = self.expiration_ttl_unit.value

        host_name = self.host_name

        key_length = self.key_length.value

        key_type = self.key_type.value

        admin = self.admin

        allow_wild_card_certificates = self.allow_wild_card_certificates

        certificate_policies = self.certificate_policies

        eap = self.eap

        name = self.name

        portal = self.portal

        portal_group_tag = self.portal_group_tag

        pxgrid = self.pxgrid

        radius = self.radius

        saml = self.saml

        san_dns: Union[Unset, list[str]] = UNSET
        if not isinstance(self.san_dns, Unset):
            san_dns = self.san_dns



        san_ip: Union[Unset, list[str]] = UNSET
        if not isinstance(self.san_ip, Unset):
            san_ip = self.san_ip



        san_uri: Union[Unset, list[str]] = UNSET
        if not isinstance(self.san_uri, Unset):
            san_uri = self.san_uri



        subject_city = self.subject_city

        subject_common_name = self.subject_common_name

        subject_country = self.subject_country

        subject_org = self.subject_org

        subject_org_unit = self.subject_org_unit

        subject_state = self.subject_state

        tacacs = self.tacacs


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "allowExtendedValidity": allow_extended_validity,
            "allowPortalTagTransferForSameSubject": allow_portal_tag_transfer_for_same_subject,
            "allowReplacementOfCertificates": allow_replacement_of_certificates,
            "allowReplacementOfPortalGroupTag": allow_replacement_of_portal_group_tag,
            "allowRoleTransferForSameSubject": allow_role_transfer_for_same_subject,
            "allowSanDnsBadName": allow_san_dns_bad_name,
            "allowSanDnsNonResolvable": allow_san_dns_non_resolvable,
            "digestType": digest_type,
            "expirationTTL": expiration_ttl,
            "expirationTTLUnit": expiration_ttl_unit,
            "hostName": host_name,
            "keyLength": key_length,
            "keyType": key_type,
        })
        if admin is not UNSET:
            field_dict["admin"] = admin
        if allow_wild_card_certificates is not UNSET:
            field_dict["allowWildCardCertificates"] = allow_wild_card_certificates
        if certificate_policies is not UNSET:
            field_dict["certificatePolicies"] = certificate_policies
        if eap is not UNSET:
            field_dict["eap"] = eap
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
        if saml is not UNSET:
            field_dict["saml"] = saml
        if san_dns is not UNSET:
            field_dict["sanDNS"] = san_dns
        if san_ip is not UNSET:
            field_dict["sanIP"] = san_ip
        if san_uri is not UNSET:
            field_dict["sanURI"] = san_uri
        if subject_city is not UNSET:
            field_dict["subjectCity"] = subject_city
        if subject_common_name is not UNSET:
            field_dict["subjectCommonName"] = subject_common_name
        if subject_country is not UNSET:
            field_dict["subjectCountry"] = subject_country
        if subject_org is not UNSET:
            field_dict["subjectOrg"] = subject_org
        if subject_org_unit is not UNSET:
            field_dict["subjectOrgUnit"] = subject_org_unit
        if subject_state is not UNSET:
            field_dict["subjectState"] = subject_state
        if tacacs is not UNSET:
            field_dict["tacacs"] = tacacs

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_extended_validity = d.pop("allowExtendedValidity")

        allow_portal_tag_transfer_for_same_subject = d.pop("allowPortalTagTransferForSameSubject")

        allow_replacement_of_certificates = d.pop("allowReplacementOfCertificates")

        allow_replacement_of_portal_group_tag = d.pop("allowReplacementOfPortalGroupTag")

        allow_role_transfer_for_same_subject = d.pop("allowRoleTransferForSameSubject")

        allow_san_dns_bad_name = d.pop("allowSanDnsBadName")

        allow_san_dns_non_resolvable = d.pop("allowSanDnsNonResolvable")

        digest_type = GenerateSelfsignedCertRequestDigestType(d.pop("digestType"))




        expiration_ttl = d.pop("expirationTTL")

        expiration_ttl_unit = GenerateSelfsignedCertRequestExpirationTTLUnit(d.pop("expirationTTLUnit"))




        host_name = d.pop("hostName")

        key_length = GenerateSelfsignedCertRequestKeyLength(d.pop("keyLength"))




        key_type = GenerateSelfsignedCertRequestKeyType(d.pop("keyType"))




        admin = d.pop("admin", UNSET)

        allow_wild_card_certificates = d.pop("allowWildCardCertificates", UNSET)

        certificate_policies = d.pop("certificatePolicies", UNSET)

        eap = d.pop("eap", UNSET)

        name = d.pop("name", UNSET)

        portal = d.pop("portal", UNSET)

        portal_group_tag = d.pop("portalGroupTag", UNSET)

        pxgrid = d.pop("pxgrid", UNSET)

        radius = d.pop("radius", UNSET)

        saml = d.pop("saml", UNSET)

        san_dns = cast(list[str], d.pop("sanDNS", UNSET))


        san_ip = cast(list[str], d.pop("sanIP", UNSET))


        san_uri = cast(list[str], d.pop("sanURI", UNSET))


        subject_city = d.pop("subjectCity", UNSET)

        subject_common_name = d.pop("subjectCommonName", UNSET)

        subject_country = d.pop("subjectCountry", UNSET)

        subject_org = d.pop("subjectOrg", UNSET)

        subject_org_unit = d.pop("subjectOrgUnit", UNSET)

        subject_state = d.pop("subjectState", UNSET)

        tacacs = d.pop("tacacs", UNSET)

        generate_selfsigned_cert_request = cls(
            allow_extended_validity=allow_extended_validity,
            allow_portal_tag_transfer_for_same_subject=allow_portal_tag_transfer_for_same_subject,
            allow_replacement_of_certificates=allow_replacement_of_certificates,
            allow_replacement_of_portal_group_tag=allow_replacement_of_portal_group_tag,
            allow_role_transfer_for_same_subject=allow_role_transfer_for_same_subject,
            allow_san_dns_bad_name=allow_san_dns_bad_name,
            allow_san_dns_non_resolvable=allow_san_dns_non_resolvable,
            digest_type=digest_type,
            expiration_ttl=expiration_ttl,
            expiration_ttl_unit=expiration_ttl_unit,
            host_name=host_name,
            key_length=key_length,
            key_type=key_type,
            admin=admin,
            allow_wild_card_certificates=allow_wild_card_certificates,
            certificate_policies=certificate_policies,
            eap=eap,
            name=name,
            portal=portal,
            portal_group_tag=portal_group_tag,
            pxgrid=pxgrid,
            radius=radius,
            saml=saml,
            san_dns=san_dns,
            san_ip=san_ip,
            san_uri=san_uri,
            subject_city=subject_city,
            subject_common_name=subject_common_name,
            subject_country=subject_country,
            subject_org=subject_org,
            subject_org_unit=subject_org_unit,
            subject_state=subject_state,
            tacacs=tacacs,
        )


        generate_selfsigned_cert_request.additional_properties = d
        return generate_selfsigned_cert_request

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
