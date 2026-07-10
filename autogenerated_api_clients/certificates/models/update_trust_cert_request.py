from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.update_trust_cert_request_automatic_crl_update_units import UpdateTrustCertRequestAutomaticCRLUpdateUnits
from ..models.update_trust_cert_request_crl_download_failure_retries_units import UpdateTrustCertRequestCrlDownloadFailureRetriesUnits
from ..models.update_trust_cert_request_non_automatic_crl_update_units import UpdateTrustCertRequestNonAutomaticCRLUpdateUnits
from ..models.update_trust_cert_request_status import UpdateTrustCertRequestStatus
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="UpdateTrustCertRequest")



@_attrs_define
class UpdateTrustCertRequest:
    

    name: str
    """ Friendly name of the certificate """
    authenticate_before_crl_received: Union[Unset, bool] = UNSET
    """ Switch to enable or disable CRL verification if CRL is not received """
    automatic_crl_update: Union[Unset, bool] = UNSET
    """ Switch to enable or disable automatic CRL update """
    automatic_crl_update_period: Union[Unset, int] = UNSET
    """ Automatic CRL update period """
    automatic_crl_update_units: Union[Unset, UpdateTrustCertRequestAutomaticCRLUpdateUnits] = UNSET
    """ Unit of time for automatic CRL update """
    crl_distribution_url: Union[Unset, str] = UNSET
    """ CRL Distribution URL """
    crl_download_failure_retries: Union[Unset, int] = UNSET
    """ If CRL download fails, wait time before retry """
    crl_download_failure_retries_units: Union[Unset, UpdateTrustCertRequestCrlDownloadFailureRetriesUnits] = UNSET
    """ Unit of time before retry if CRL download fails """
    description: Union[Unset, str] = UNSET
    """ Description for trust certificate """
    download_crl: Union[Unset, bool] = UNSET
    """ Switch to enable or disable download of CRL """
    enable_ocsp_validation: Union[Unset, bool] = UNSET
    """ Switch to enable or disable OCSP Validation """
    enable_server_identity_check: Union[Unset, bool] = UNSET
    """ Switch to enable or disable verification if HTTPS or LDAP server certificate name fits the configured server
    URL """
    ignore_crl_expiration: Union[Unset, bool] = UNSET
    """ Switch to enable or disable ignore CRL expiration """
    non_automatic_crl_update_period: Union[Unset, int] = UNSET
    """ Non automatic CRL update period """
    non_automatic_crl_update_units: Union[Unset, UpdateTrustCertRequestNonAutomaticCRLUpdateUnits] = UNSET
    """ Unit of time of non automatic CRL update """
    reject_if_no_status_from_ocsp: Union[Unset, bool] = UNSET
    """ Switch to reject certificate if there is no status from OCSP """
    reject_if_unreachable_from_ocsp: Union[Unset, bool] = UNSET
    """ Switch to reject certificate if unreachable from OCSP """
    selected_ocsp_service: Union[Unset, str] = UNSET
    """ Name of selected OCSP Service """
    status: Union[Unset, UpdateTrustCertRequestStatus] = UNSET
    trust_for_certificate_based_admin_auth: Union[Unset, bool] = UNSET
    """ Trust for Certificate based Admin authentication """
    trust_for_cisco_services_auth: Union[Unset, bool] = UNSET
    """ Trust for authentication of Cisco Services """
    trust_for_client_auth: Union[Unset, bool] = UNSET
    """ Trust for client authentication and Syslog """
    trust_for_ise_auth: Union[Unset, bool] = UNSET
    """ Trust for Authentication within ISE and Client-Server communication """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        authenticate_before_crl_received = self.authenticate_before_crl_received

        automatic_crl_update = self.automatic_crl_update

        automatic_crl_update_period = self.automatic_crl_update_period

        automatic_crl_update_units: Union[Unset, str] = UNSET
        if not isinstance(self.automatic_crl_update_units, Unset):
            automatic_crl_update_units = self.automatic_crl_update_units.value


        crl_distribution_url = self.crl_distribution_url

        crl_download_failure_retries = self.crl_download_failure_retries

        crl_download_failure_retries_units: Union[Unset, str] = UNSET
        if not isinstance(self.crl_download_failure_retries_units, Unset):
            crl_download_failure_retries_units = self.crl_download_failure_retries_units.value


        description = self.description

        download_crl = self.download_crl

        enable_ocsp_validation = self.enable_ocsp_validation

        enable_server_identity_check = self.enable_server_identity_check

        ignore_crl_expiration = self.ignore_crl_expiration

        non_automatic_crl_update_period = self.non_automatic_crl_update_period

        non_automatic_crl_update_units: Union[Unset, str] = UNSET
        if not isinstance(self.non_automatic_crl_update_units, Unset):
            non_automatic_crl_update_units = self.non_automatic_crl_update_units.value


        reject_if_no_status_from_ocsp = self.reject_if_no_status_from_ocsp

        reject_if_unreachable_from_ocsp = self.reject_if_unreachable_from_ocsp

        selected_ocsp_service = self.selected_ocsp_service

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        trust_for_certificate_based_admin_auth = self.trust_for_certificate_based_admin_auth

        trust_for_cisco_services_auth = self.trust_for_cisco_services_auth

        trust_for_client_auth = self.trust_for_client_auth

        trust_for_ise_auth = self.trust_for_ise_auth


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
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
        if ignore_crl_expiration is not UNSET:
            field_dict["ignoreCRLExpiration"] = ignore_crl_expiration
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
        if status is not UNSET:
            field_dict["status"] = status
        if trust_for_certificate_based_admin_auth is not UNSET:
            field_dict["trustForCertificateBasedAdminAuth"] = trust_for_certificate_based_admin_auth
        if trust_for_cisco_services_auth is not UNSET:
            field_dict["trustForCiscoServicesAuth"] = trust_for_cisco_services_auth
        if trust_for_client_auth is not UNSET:
            field_dict["trustForClientAuth"] = trust_for_client_auth
        if trust_for_ise_auth is not UNSET:
            field_dict["trustForIseAuth"] = trust_for_ise_auth

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        authenticate_before_crl_received = d.pop("authenticateBeforeCRLReceived", UNSET)

        automatic_crl_update = d.pop("automaticCRLUpdate", UNSET)

        automatic_crl_update_period = d.pop("automaticCRLUpdatePeriod", UNSET)

        _automatic_crl_update_units = d.pop("automaticCRLUpdateUnits", UNSET)
        automatic_crl_update_units: Union[Unset, UpdateTrustCertRequestAutomaticCRLUpdateUnits]
        if isinstance(_automatic_crl_update_units,  Unset):
            automatic_crl_update_units = UNSET
        else:
            automatic_crl_update_units = UpdateTrustCertRequestAutomaticCRLUpdateUnits(_automatic_crl_update_units)




        crl_distribution_url = d.pop("crlDistributionUrl", UNSET)

        crl_download_failure_retries = d.pop("crlDownloadFailureRetries", UNSET)

        _crl_download_failure_retries_units = d.pop("crlDownloadFailureRetriesUnits", UNSET)
        crl_download_failure_retries_units: Union[Unset, UpdateTrustCertRequestCrlDownloadFailureRetriesUnits]
        if isinstance(_crl_download_failure_retries_units,  Unset):
            crl_download_failure_retries_units = UNSET
        else:
            crl_download_failure_retries_units = UpdateTrustCertRequestCrlDownloadFailureRetriesUnits(_crl_download_failure_retries_units)




        description = d.pop("description", UNSET)

        download_crl = d.pop("downloadCRL", UNSET)

        enable_ocsp_validation = d.pop("enableOCSPValidation", UNSET)

        enable_server_identity_check = d.pop("enableServerIdentityCheck", UNSET)

        ignore_crl_expiration = d.pop("ignoreCRLExpiration", UNSET)

        non_automatic_crl_update_period = d.pop("nonAutomaticCRLUpdatePeriod", UNSET)

        _non_automatic_crl_update_units = d.pop("nonAutomaticCRLUpdateUnits", UNSET)
        non_automatic_crl_update_units: Union[Unset, UpdateTrustCertRequestNonAutomaticCRLUpdateUnits]
        if isinstance(_non_automatic_crl_update_units,  Unset):
            non_automatic_crl_update_units = UNSET
        else:
            non_automatic_crl_update_units = UpdateTrustCertRequestNonAutomaticCRLUpdateUnits(_non_automatic_crl_update_units)




        reject_if_no_status_from_ocsp = d.pop("rejectIfNoStatusFromOCSP", UNSET)

        reject_if_unreachable_from_ocsp = d.pop("rejectIfUnreachableFromOCSP", UNSET)

        selected_ocsp_service = d.pop("selectedOCSPService", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, UpdateTrustCertRequestStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = UpdateTrustCertRequestStatus(_status)




        trust_for_certificate_based_admin_auth = d.pop("trustForCertificateBasedAdminAuth", UNSET)

        trust_for_cisco_services_auth = d.pop("trustForCiscoServicesAuth", UNSET)

        trust_for_client_auth = d.pop("trustForClientAuth", UNSET)

        trust_for_ise_auth = d.pop("trustForIseAuth", UNSET)

        update_trust_cert_request = cls(
            name=name,
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
            ignore_crl_expiration=ignore_crl_expiration,
            non_automatic_crl_update_period=non_automatic_crl_update_period,
            non_automatic_crl_update_units=non_automatic_crl_update_units,
            reject_if_no_status_from_ocsp=reject_if_no_status_from_ocsp,
            reject_if_unreachable_from_ocsp=reject_if_unreachable_from_ocsp,
            selected_ocsp_service=selected_ocsp_service,
            status=status,
            trust_for_certificate_based_admin_auth=trust_for_certificate_based_admin_auth,
            trust_for_cisco_services_auth=trust_for_cisco_services_auth,
            trust_for_client_auth=trust_for_client_auth,
            trust_for_ise_auth=trust_for_ise_auth,
        )


        update_trust_cert_request.additional_properties = d
        return update_trust_cert_request

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
