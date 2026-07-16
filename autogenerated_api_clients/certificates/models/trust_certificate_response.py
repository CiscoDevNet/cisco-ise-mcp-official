# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.link import Link





T = TypeVar("T", bound="TrustCertificateResponse")



@_attrs_define
class TrustCertificateResponse:
    

    authenticate_before_crl_received: Union[Unset, str] = UNSET
    """ Switch to enable or disable authentication before receiving CRL """
    automatic_crl_update: Union[Unset, str] = UNSET
    """ Switch to enable or disable automatic CRL update """
    automatic_crl_update_period: Union[Unset, str] = UNSET
    """ Automatic CRL update period """
    automatic_crl_update_units: Union[Unset, str] = UNSET
    """ Unit of time of automatic CRL update """
    crl_distribution_url: Union[Unset, str] = UNSET
    """ CRL Distribution URL """
    crl_download_failure_retries: Union[Unset, str] = UNSET
    """ If CRL download fails, wait time before retry """
    crl_download_failure_retries_units: Union[Unset, str] = UNSET
    """ Unit of time before retry if CRL download fails """
    description: Union[Unset, str] = UNSET
    """ Description of trust certificate """
    download_crl: Union[Unset, str] = UNSET
    """ Switch to enable or disable download of CRL """
    enable_ocsp_validation: Union[Unset, str] = UNSET
    """ Switch to enable or disable OCSP Validation """
    enable_server_identity_check: Union[Unset, str] = UNSET
    """ Switch to enable or disable Server Identity Check """
    expiration_date: Union[Unset, str] = UNSET
    """ The time and date past which the certificate is no longer valid """
    friendly_name: Union[Unset, str] = UNSET
    """ Friendly name of trust certificate """
    id: Union[Unset, str] = UNSET
    """ ID of trust certificate """
    ignore_crl_expiration: Union[Unset, str] = UNSET
    """ Switch to enable or disable ignore CRL Expiration """
    internal_ca: Union[Unset, bool] = UNSET
    issued_by: Union[Unset, str] = UNSET
    """ The entity that verified the information and signed the certificate """
    issued_to: Union[Unset, str] = UNSET
    """ Entity to which trust certificate is issued """
    key_size: Union[Unset, str] = UNSET
    """ Length of the key used for encrypting trust certificate """
    link: Union['Link', None, Unset] = UNSET
    non_automatic_crl_update_period: Union[Unset, str] = UNSET
    """ Non automatic CRL update period """
    non_automatic_crl_update_units: Union[Unset, str] = UNSET
    """ Unit of time of non automatic CRL update """
    reject_if_no_status_from_ocsp: Union[Unset, str] = UNSET
    """ Switch to reject certificate if there is no status from OCSP """
    reject_if_unreachable_from_ocsp: Union[Unset, str] = UNSET
    """ Switch to reject certificate if unreachable from OCSP """
    selected_ocsp_service: Union[Unset, str] = UNSET
    """ Name of selected OCSP Service """
    serial_number_decimal_format: Union[Unset, str] = UNSET
    """ Used to uniquely identify the certificate within a CA's systems """
    sha_256_fingerprint: Union[Unset, str] = UNSET
    signature_algorithm: Union[Unset, str] = UNSET
    """ Algorithm used for encrypting trust certificate """
    status: Union[Unset, str] = UNSET
    subject: Union[Unset, str] = UNSET
    """ The Subject or entity with which public key of trust certificate is associated """
    trusted_for: Union[Unset, str] = UNSET
    """ Different services for which the certificated is trusted """
    valid_from: Union[Unset, str] = UNSET
    """ The earliest time and date on which the certificate is valid """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.link import Link
        authenticate_before_crl_received = self.authenticate_before_crl_received

        automatic_crl_update = self.automatic_crl_update

        automatic_crl_update_period = self.automatic_crl_update_period

        automatic_crl_update_units = self.automatic_crl_update_units

        crl_distribution_url = self.crl_distribution_url

        crl_download_failure_retries = self.crl_download_failure_retries

        crl_download_failure_retries_units = self.crl_download_failure_retries_units

        description = self.description

        download_crl = self.download_crl

        enable_ocsp_validation = self.enable_ocsp_validation

        enable_server_identity_check = self.enable_server_identity_check

        expiration_date = self.expiration_date

        friendly_name = self.friendly_name

        id = self.id

        ignore_crl_expiration = self.ignore_crl_expiration

        internal_ca = self.internal_ca

        issued_by = self.issued_by

        issued_to = self.issued_to

        key_size = self.key_size

        link: Union[None, Unset, dict[str, Any]]
        if isinstance(self.link, Unset):
            link = UNSET
        elif isinstance(self.link, Link):
            link = self.link.to_dict()
        else:
            link = self.link

        non_automatic_crl_update_period = self.non_automatic_crl_update_period

        non_automatic_crl_update_units = self.non_automatic_crl_update_units

        reject_if_no_status_from_ocsp = self.reject_if_no_status_from_ocsp

        reject_if_unreachable_from_ocsp = self.reject_if_unreachable_from_ocsp

        selected_ocsp_service = self.selected_ocsp_service

        serial_number_decimal_format = self.serial_number_decimal_format

        sha_256_fingerprint = self.sha_256_fingerprint

        signature_algorithm = self.signature_algorithm

        status = self.status

        subject = self.subject

        trusted_for = self.trusted_for

        valid_from = self.valid_from


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if authenticate_before_crl_received is not UNSET:
            field_dict["authenticateBeforeCRLReceived"] = authenticate_before_crl_received
        if automatic_crl_update is not UNSET:
            field_dict["automaticCRLUpdate"] = automatic_crl_update
        if automatic_crl_update_period is not UNSET:
            field_dict["automaticCRLUpdatePeriod"] = automatic_crl_update_period
        if automatic_crl_update_units is not UNSET:
            field_dict["automaticCRLUpdateUnits"] = automatic_crl_update_units
        if crl_distribution_url is not UNSET:
            field_dict["crlDistributionUrl"] = crl_distribution_url
        if crl_download_failure_retries is not UNSET:
            field_dict["crlDownloadFailureRetries"] = crl_download_failure_retries
        if crl_download_failure_retries_units is not UNSET:
            field_dict["crlDownloadFailureRetriesUnits"] = crl_download_failure_retries_units
        if description is not UNSET:
            field_dict["description"] = description
        if download_crl is not UNSET:
            field_dict["downloadCRL"] = download_crl
        if enable_ocsp_validation is not UNSET:
            field_dict["enableOCSPValidation"] = enable_ocsp_validation
        if enable_server_identity_check is not UNSET:
            field_dict["enableServerIdentityCheck"] = enable_server_identity_check
        if expiration_date is not UNSET:
            field_dict["expirationDate"] = expiration_date
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if id is not UNSET:
            field_dict["id"] = id
        if ignore_crl_expiration is not UNSET:
            field_dict["ignoreCRLExpiration"] = ignore_crl_expiration
        if internal_ca is not UNSET:
            field_dict["internalCA"] = internal_ca
        if issued_by is not UNSET:
            field_dict["issuedBy"] = issued_by
        if issued_to is not UNSET:
            field_dict["issuedTo"] = issued_to
        if key_size is not UNSET:
            field_dict["keySize"] = key_size
        if link is not UNSET:
            field_dict["link"] = link
        if non_automatic_crl_update_period is not UNSET:
            field_dict["nonAutomaticCRLUpdatePeriod"] = non_automatic_crl_update_period
        if non_automatic_crl_update_units is not UNSET:
            field_dict["nonAutomaticCRLUpdateUnits"] = non_automatic_crl_update_units
        if reject_if_no_status_from_ocsp is not UNSET:
            field_dict["rejectIfNoStatusFromOCSP"] = reject_if_no_status_from_ocsp
        if reject_if_unreachable_from_ocsp is not UNSET:
            field_dict["rejectIfUnreachableFromOCSP"] = reject_if_unreachable_from_ocsp
        if selected_ocsp_service is not UNSET:
            field_dict["selectedOCSPService"] = selected_ocsp_service
        if serial_number_decimal_format is not UNSET:
            field_dict["serialNumberDecimalFormat"] = serial_number_decimal_format
        if sha_256_fingerprint is not UNSET:
            field_dict["sha256Fingerprint"] = sha_256_fingerprint
        if signature_algorithm is not UNSET:
            field_dict["signatureAlgorithm"] = signature_algorithm
        if status is not UNSET:
            field_dict["status"] = status
        if subject is not UNSET:
            field_dict["subject"] = subject
        if trusted_for is not UNSET:
            field_dict["trustedFor"] = trusted_for
        if valid_from is not UNSET:
            field_dict["validFrom"] = valid_from

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.link import Link
        d = dict(src_dict)
        authenticate_before_crl_received = d.pop("authenticateBeforeCRLReceived", UNSET)

        automatic_crl_update = d.pop("automaticCRLUpdate", UNSET)

        automatic_crl_update_period = d.pop("automaticCRLUpdatePeriod", UNSET)

        automatic_crl_update_units = d.pop("automaticCRLUpdateUnits", UNSET)

        crl_distribution_url = d.pop("crlDistributionUrl", UNSET)

        crl_download_failure_retries = d.pop("crlDownloadFailureRetries", UNSET)

        crl_download_failure_retries_units = d.pop("crlDownloadFailureRetriesUnits", UNSET)

        description = d.pop("description", UNSET)

        download_crl = d.pop("downloadCRL", UNSET)

        enable_ocsp_validation = d.pop("enableOCSPValidation", UNSET)

        enable_server_identity_check = d.pop("enableServerIdentityCheck", UNSET)

        expiration_date = d.pop("expirationDate", UNSET)

        friendly_name = d.pop("friendlyName", UNSET)

        id = d.pop("id", UNSET)

        ignore_crl_expiration = d.pop("ignoreCRLExpiration", UNSET)

        internal_ca = d.pop("internalCA", UNSET)

        issued_by = d.pop("issuedBy", UNSET)

        issued_to = d.pop("issuedTo", UNSET)

        key_size = d.pop("keySize", UNSET)

        def _parse_link(data: object) -> Union['Link', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_link_type_0 = Link.from_dict(data)



                return componentsschemas_link_type_0
            except: # noqa: E722
                pass
            return cast(Union['Link', None, Unset], data)

        link = _parse_link(d.pop("link", UNSET))


        non_automatic_crl_update_period = d.pop("nonAutomaticCRLUpdatePeriod", UNSET)

        non_automatic_crl_update_units = d.pop("nonAutomaticCRLUpdateUnits", UNSET)

        reject_if_no_status_from_ocsp = d.pop("rejectIfNoStatusFromOCSP", UNSET)

        reject_if_unreachable_from_ocsp = d.pop("rejectIfUnreachableFromOCSP", UNSET)

        selected_ocsp_service = d.pop("selectedOCSPService", UNSET)

        serial_number_decimal_format = d.pop("serialNumberDecimalFormat", UNSET)

        sha_256_fingerprint = d.pop("sha256Fingerprint", UNSET)

        signature_algorithm = d.pop("signatureAlgorithm", UNSET)

        status = d.pop("status", UNSET)

        subject = d.pop("subject", UNSET)

        trusted_for = d.pop("trustedFor", UNSET)

        valid_from = d.pop("validFrom", UNSET)

        trust_certificate_response = cls(
            authenticate_before_crl_received=authenticate_before_crl_received,
            automatic_crl_update=automatic_crl_update,
            automatic_crl_update_period=automatic_crl_update_period,
            automatic_crl_update_units=automatic_crl_update_units,
            crl_distribution_url=crl_distribution_url,
            crl_download_failure_retries=crl_download_failure_retries,
            crl_download_failure_retries_units=crl_download_failure_retries_units,
            description=description,
            download_crl=download_crl,
            enable_ocsp_validation=enable_ocsp_validation,
            enable_server_identity_check=enable_server_identity_check,
            expiration_date=expiration_date,
            friendly_name=friendly_name,
            id=id,
            ignore_crl_expiration=ignore_crl_expiration,
            internal_ca=internal_ca,
            issued_by=issued_by,
            issued_to=issued_to,
            key_size=key_size,
            link=link,
            non_automatic_crl_update_period=non_automatic_crl_update_period,
            non_automatic_crl_update_units=non_automatic_crl_update_units,
            reject_if_no_status_from_ocsp=reject_if_no_status_from_ocsp,
            reject_if_unreachable_from_ocsp=reject_if_unreachable_from_ocsp,
            selected_ocsp_service=selected_ocsp_service,
            serial_number_decimal_format=serial_number_decimal_format,
            sha_256_fingerprint=sha_256_fingerprint,
            signature_algorithm=signature_algorithm,
            status=status,
            subject=subject,
            trusted_for=trusted_for,
            valid_from=valid_from,
        )


        trust_certificate_response.additional_properties = d
        return trust_certificate_response

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
