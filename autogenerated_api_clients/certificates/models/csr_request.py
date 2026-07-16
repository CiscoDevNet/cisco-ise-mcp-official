# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.csr_request_digest_type import CSRRequestDigestType
from ..models.csr_request_key_length import CSRRequestKeyLength
from ..models.csr_request_key_type import CSRRequestKeyType
from ..models.csr_request_used_for import CSRRequestUsedFor
from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="CSRRequest")



@_attrs_define
class CSRRequest:
    

    digest_type: CSRRequestDigestType
    key_length: CSRRequestKeyLength
    key_type: CSRRequestKeyType
    used_for: CSRRequestUsedFor
    allow_wild_card_cert: Union[Unset, bool] = UNSET
    certificate_policies: Union[Unset, str] = UNSET
    hostnames: Union[Unset, list[str]] = UNSET
    portal_group_tag: Union[Unset, str] = UNSET
    san_dns: Union[Unset, list[str]] = UNSET
    san_dir: Union[Unset, list[str]] = UNSET
    san_ip: Union[Unset, list[str]] = UNSET
    san_uri: Union[Unset, list[str]] = UNSET
    subject_city: Union[Unset, str] = UNSET
    subject_common_name: Union[Unset, str] = UNSET
    subject_country: Union[Unset, str] = UNSET
    subject_org: Union[Unset, str] = UNSET
    subject_org_unit: Union[Unset, str] = UNSET
    subject_state: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        digest_type = self.digest_type.value

        key_length = self.key_length.value

        key_type = self.key_type.value

        used_for = self.used_for.value

        allow_wild_card_cert = self.allow_wild_card_cert

        certificate_policies = self.certificate_policies

        hostnames: Union[Unset, list[str]] = UNSET
        if not isinstance(self.hostnames, Unset):
            hostnames = self.hostnames



        portal_group_tag = self.portal_group_tag

        san_dns: Union[Unset, list[str]] = UNSET
        if not isinstance(self.san_dns, Unset):
            san_dns = self.san_dns



        san_dir: Union[Unset, list[str]] = UNSET
        if not isinstance(self.san_dir, Unset):
            san_dir = self.san_dir



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


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "digestType": digest_type,
            "keyLength": key_length,
            "keyType": key_type,
            "usedFor": used_for,
        })
        if allow_wild_card_cert is not UNSET:
            field_dict["allowWildCardCert"] = allow_wild_card_cert
        if certificate_policies is not UNSET:
            field_dict["certificatePolicies"] = certificate_policies
        if hostnames is not UNSET:
            field_dict["hostnames"] = hostnames
        if portal_group_tag is not UNSET:
            field_dict["portalGroupTag"] = portal_group_tag
        if san_dns is not UNSET:
            field_dict["sanDNS"] = san_dns
        if san_dir is not UNSET:
            field_dict["sanDir"] = san_dir
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

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        digest_type = CSRRequestDigestType(d.pop("digestType"))




        key_length = CSRRequestKeyLength(d.pop("keyLength"))




        key_type = CSRRequestKeyType(d.pop("keyType"))




        used_for = CSRRequestUsedFor(d.pop("usedFor"))




        allow_wild_card_cert = d.pop("allowWildCardCert", UNSET)

        certificate_policies = d.pop("certificatePolicies", UNSET)

        hostnames = cast(list[str], d.pop("hostnames", UNSET))


        portal_group_tag = d.pop("portalGroupTag", UNSET)

        san_dns = cast(list[str], d.pop("sanDNS", UNSET))


        san_dir = cast(list[str], d.pop("sanDir", UNSET))


        san_ip = cast(list[str], d.pop("sanIP", UNSET))


        san_uri = cast(list[str], d.pop("sanURI", UNSET))


        subject_city = d.pop("subjectCity", UNSET)

        subject_common_name = d.pop("subjectCommonName", UNSET)

        subject_country = d.pop("subjectCountry", UNSET)

        subject_org = d.pop("subjectOrg", UNSET)

        subject_org_unit = d.pop("subjectOrgUnit", UNSET)

        subject_state = d.pop("subjectState", UNSET)

        csr_request = cls(
            digest_type=digest_type,
            key_length=key_length,
            key_type=key_type,
            used_for=used_for,
            allow_wild_card_cert=allow_wild_card_cert,
            certificate_policies=certificate_policies,
            hostnames=hostnames,
            portal_group_tag=portal_group_tag,
            san_dns=san_dns,
            san_dir=san_dir,
            san_ip=san_ip,
            san_uri=san_uri,
            subject_city=subject_city,
            subject_common_name=subject_common_name,
            subject_country=subject_country,
            subject_org=subject_org,
            subject_org_unit=subject_org_unit,
            subject_state=subject_state,
        )


        csr_request.additional_properties = d
        return csr_request

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
