# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="TrustCert")



@_attrs_define
class TrustCert:
    

    allow_basic_constraint_ca_false: bool
    """ Allow certificates with Basic Constraints CA Field as False  """
    allow_out_of_date_cert: bool
    """ Allow out of date certificates  """
    allow_sha1_certificates: bool
    """ Allow SHA1 based certificates  """
    data: str
    """ Certificate content  """
    allow_multiple_cn_cert: Union[Unset, bool] = UNSET
    """ Allow certificates with multiple CN """
    description: Union[Unset, str] = UNSET
    """ Description of the certificate """
    name: Union[Unset, str] = UNSET
    """ Name of the certificate """
    trust_for_certificate_based_admin_auth: Union[Unset, bool] = UNSET
    """ Trust for Certificate based Admin authentication """
    trust_for_cisco_services_auth: Union[Unset, bool] = UNSET
    """ Trust for authentication of Cisco Services """
    trust_for_client_auth: Union[Unset, bool] = UNSET
    """ Trust for client authentication and Syslog """
    trust_for_ise_auth: Union[Unset, bool] = UNSET
    """ Trust for Authentication within ISE and Client-Server communication """
    validate_certificate_extensions: Union[Unset, bool] = UNSET
    """ Validate trust certificate extension """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        allow_basic_constraint_ca_false = self.allow_basic_constraint_ca_false

        allow_out_of_date_cert = self.allow_out_of_date_cert

        allow_sha1_certificates = self.allow_sha1_certificates

        data = self.data

        allow_multiple_cn_cert = self.allow_multiple_cn_cert

        description = self.description

        name = self.name

        trust_for_certificate_based_admin_auth = self.trust_for_certificate_based_admin_auth

        trust_for_cisco_services_auth = self.trust_for_cisco_services_auth

        trust_for_client_auth = self.trust_for_client_auth

        trust_for_ise_auth = self.trust_for_ise_auth

        validate_certificate_extensions = self.validate_certificate_extensions


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "allowBasicConstraintCAFalse": allow_basic_constraint_ca_false,
            "allowOutOfDateCert": allow_out_of_date_cert,
            "allowSHA1Certificates": allow_sha1_certificates,
            "data": data,
        })
        if allow_multiple_cn_cert is not UNSET:
            field_dict["allowMultipleCNCert"] = allow_multiple_cn_cert
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if trust_for_certificate_based_admin_auth is not UNSET:
            field_dict["trustForCertificateBasedAdminAuth"] = trust_for_certificate_based_admin_auth
        if trust_for_cisco_services_auth is not UNSET:
            field_dict["trustForCiscoServicesAuth"] = trust_for_cisco_services_auth
        if trust_for_client_auth is not UNSET:
            field_dict["trustForClientAuth"] = trust_for_client_auth
        if trust_for_ise_auth is not UNSET:
            field_dict["trustForIseAuth"] = trust_for_ise_auth
        if validate_certificate_extensions is not UNSET:
            field_dict["validateCertificateExtensions"] = validate_certificate_extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_basic_constraint_ca_false = d.pop("allowBasicConstraintCAFalse")

        allow_out_of_date_cert = d.pop("allowOutOfDateCert")

        allow_sha1_certificates = d.pop("allowSHA1Certificates")

        data = d.pop("data")

        allow_multiple_cn_cert = d.pop("allowMultipleCNCert", UNSET)

        description = d.pop("description", UNSET)

        name = d.pop("name", UNSET)

        trust_for_certificate_based_admin_auth = d.pop("trustForCertificateBasedAdminAuth", UNSET)

        trust_for_cisco_services_auth = d.pop("trustForCiscoServicesAuth", UNSET)

        trust_for_client_auth = d.pop("trustForClientAuth", UNSET)

        trust_for_ise_auth = d.pop("trustForIseAuth", UNSET)

        validate_certificate_extensions = d.pop("validateCertificateExtensions", UNSET)

        trust_cert = cls(
            allow_basic_constraint_ca_false=allow_basic_constraint_ca_false,
            allow_out_of_date_cert=allow_out_of_date_cert,
            allow_sha1_certificates=allow_sha1_certificates,
            data=data,
            allow_multiple_cn_cert=allow_multiple_cn_cert,
            description=description,
            name=name,
            trust_for_certificate_based_admin_auth=trust_for_certificate_based_admin_auth,
            trust_for_cisco_services_auth=trust_for_cisco_services_auth,
            trust_for_client_auth=trust_for_client_auth,
            trust_for_ise_auth=trust_for_ise_auth,
            validate_certificate_extensions=validate_certificate_extensions,
        )


        trust_cert.additional_properties = d
        return trust_cert

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
