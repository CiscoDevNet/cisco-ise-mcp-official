# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.update_trust_cert_request import UpdateTrustCertRequest
from ...models.update_trust_cert_resp_payload import UpdateTrustCertRespPayload
from typing import cast



def _get_kwargs(
    id: str,
    *,
    body: UpdateTrustCertRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/certs/trusted-certificate/{id}".format(id=id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, UpdateTrustCertRespPayload]]:
    if response.status_code == 200:
        response_200 = UpdateTrustCertRespPayload.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201
    if response.status_code == 400:
        response_400 = UpdateTrustCertRespPayload.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 422:
        response_422 = UpdateTrustCertRespPayload.from_dict(response.json())



        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, UpdateTrustCertRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateTrustCertRequest,

) -> Response[Union[Any, UpdateTrustCertRespPayload]]:
    r""" Update the trust certificate already present in the Cisco ISE trust store

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a trusted certificate present in Cisco ISE trust store.</h3>
    The following parameters are used in the PUT request body <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name<sup><font color=red>*required</font></sup></td> <td>Friendly name of the certificate.</td>
    <td>\"name\": \"Trust Certificate\"</td> </tr> <tr> <td>status</td> <td>Status of the
    certificate</td> <td>\"status\": \"Enabled\"</td> </tr> <tr> <td>description</td> <td>Description of
    the certificate</td> <td>\"description\": \"Certificate for secure connection to cisco.com\"</td>
    </tr> <tr> <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and Syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based Admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco Services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>enableOCSPValidation</td> <td>Switch to
    enable or disable OCSP Validation</td> <td>\"enableOCSPValidation\": false</td> </tr> <tr>
    <td>selectedOCSPService</td> <td>Name of selected OCSP Service</td> <td>\"selectedOCSPService\":
    \"INTERNAL_OCSP_SERVICE\"</td> </tr> <tr> <td>rejectIfNoStatusFromOCSP</td> <td>Switch to reject
    certificate if there is no status from OCSP</td> <td>\"rejectIfNoStatusFromOCSP\": false</td> </tr>
    <tr> <td>rejectIfUnreachableFromOCSP</td> <td>Switch to reject certificate if unreachable from
    OCSP</td> <td>\"rejectIfUnreachableFromOCSP\": false</td> </tr> <tr> <td>downloadCRL</td> <td>Switch
    to enable or disable download of CRL</td> <td>\"downloadCRL\": false</td> </tr> <tr>
    <td>crlDistributionUrl</td> <td>Certificate Revocation List Distribution URL</td>
    <td>\"crlDistributionUrl\": \"CRL distribution URL\"</td> </tr> <tr> <td>automaticCRLUpdate</td>
    <td>Switch to enable or disable automatic CRL update</td> <td>\"automaticCRLUpdate\": false</td>
    </tr> <tr> <td>automaticCRLUpdatePeriod</td> <td>Automatic CRL update period</td>
    <td>\"automaticCRLUpdatePeriod\": 5</td> </tr> <tr> <td>automaticCRLUpdateUnits</td> <td>Unit of
    time for automatic CRL update</td> <td>\"automaticCRLUpdateUnits\": \"Minutes\"</td> </tr> <tr>
    <td>nonAutomaticCRLUpdatePeriod</td> <td>Non automatic CRL update period</td>
    <td>\"nonAutomaticCRLUpdatePeriod\": 1</td> </tr> <tr> <td>nonAutomaticCRLUpdateUnits</td> <td>Unit
    of time of non automatic CRL update</td> <td>\"nonAutomaticCRLUpdateUnits\": \"Hours\"</td> </tr>
    <tr> <td>crlDownloadFailureRetries</td> <td>If CRL download fails, wait time before retry</td>
    <td>\"crlDownloadFailureRetries\": 10</td> </tr> <tr> <td>crlDownloadFailureRetriesUnits</td>
    <td>Unit of time before retry if CRL download fails</td> <td>\"crlDownloadFailureRetriesUnits\":
    \"Minutes\"</td> </tr> <tr> <td>enableServerIdentityCheck</td> <td>Switch to enable or disable
    verification if HTTPS or LDAP server certificate name fits the configured server URL</td>
    <td>\"enableServerIdentityCheck\": false</td> </tr> <tr> <td>authenticateBeforeCRLReceived</td>
    <td>Switch to enable or disable CRL Verification if CRL is not Received</td>
    <td>\"authenticateBeforeCRLReceived\": false</td> </tr> <tr> <td>ignoreCRLExpiration</td> <td>Switch
    to enable or disable ignore CRL Expiration</td> <td>\"ignoreCRLExpiration\": false</td> </tr>
    </tbody> </table></br> <hr/> <table class=\"certTable\"> <thead> <tr> <th>Trusted For</th>
    <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. Also check this box if
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"trustForClientAuth\" can be set true
    only if \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b> \"trustForCertificateBasedAdminAuth\" can be set true only if \"trustForIseAuth\" and
    \"trustForClientAuth\" are true.</td></td> </tr> <tr> <td>Authentication of Cisco Services</td> <td>
    Use <b>\"trustForCiscoServicesAuth\":true</b> if the certificate is to be used for trusting external
    Cisco services, such as Feed Service.</td> </tr> </tbody> </table> <table class=\"certTable\">
    <thead> <tr> <th>OCSP Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation
    against OCSP service</td> <td>Use <b>\"enableOCSPValidation\":true</b> to validate the certificate
    against OCSP service mentioned in the field <b>selectedOCSPService</b>.</td> </tr> <tr> <td>OCSP
    Service name</td> <td>Use <b>\"selectedOCSPService\":\"Name of OCSP Service\"</b> to mention the
    OCSP service name against which the certificate should be validated.</br> <b>Note:</b>
    <b>selectedOCSPService</b> value is used if <b>enableOCSPValidation</b> has been set true.</td>
    </tr> <tr> <td>Reject the request if OCSP returns UNKNOWN status</td> <td>Use
    <b>\"rejectIfNoStatusFromOCSP\":true</b> to reject the certificate if the OCSP service returns
    UNKNOWN status.</br> <b>Note:</b> <b>\"rejectIfNoStatusFromOCSP\":true</b> can be used only if the
    parameter <b>enableOCSPValidation</b> has been set true.</td> </tr> <tr> <td>Reject the request if
    OCSP Responder is unreachable</td> <td> Use <b>\"rejectIfUnreachableFromOCSP\":true</b> to reject
    the certificate if the OCSP service is unreachable.</br> <b>Note:</b>
    <b>\"rejectIfUnreachableFromOCSP\":true</b> can be used only if <b>enableOCSPValidation</b> has been
    set true.</td> </tr> </tbody> </table> <table class=\"certTable\"> <thead> <tr> <th>Certificate
    Revocation List Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation against
    CRL</td> <td>Use <b>\"downloadCRL\":true</b> to validate the certificate against CRL downloaded from
    URL mentioned in the field <b>crlDistributionUrl</b></td> </tr> <tr> <td>CRL distribution url</td>
    <td>Use <b>\"crlDistributionUrl\"</b> to specify the URL from where the CRL should be
    downloaded</br> <b>Note:</b> \"crlDistributionUrl\" value is used if \"downloadCRL\" has been set
    true.</td> </tr> <tr> <td>Retrieve CRL time</td> <td>Use <b>\"automaticCRLUpdate\":true</b>,
    <b>automaticCRLUpdatePeriod</b>, and <b>automaticCRLUpdatePeriod</b> to set the time before which
    CRL is automatically retrieved prior to expiration</br> Use <b>nonAutomaticCRLUpdatePeriod</b> and
    <b>nonAutomaticCRLUpdateUnits</b> to set the time period for CRL retrieval in loop.<br> <b>Note:</b>
    All the above fields can be used only if <b>\"downloadCRL\"</b> has been set true.</td> </tr> <tr>
    <td>If download fails</td> <td>Use <b>\"crlDownloadFailureRetries\" and
    \"crlDownloadFailureRetriesUnits\"</b> to set retry time period if CRL download fails</br>
    <b>Note:</b><b>crlDownloadFailureRetries</b> and <b>crlDownloadFailureRetriesUnits</b> can be used
    only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Enable Server Identity Check</td>
    <td>Use <b>\"enableServerIdentityCheck\":true</b> to verify that HTTPS or LDAPS server certificate
    name fits the configured server URL</br> <b>Note:</b><b>\"enableServerIdentityCheck\":true</b> can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Bypass CRL Verification if
    CRL is not Received</td> <td>Use <b>\"authenticateBeforeCRLReceived\":true</b> to bypass CRL
    Verification if CRL is not Received</br> <b>Note:</b><b>\"authenticateBeforeCRLReceived\":true can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Ignore that CRL is not yet
    valid or has expired</td> <td> Use <b>\"ignoreCRLExpiration\":true</b> to ignore if CRL is not yet
    valid or expired</br> <b>Note:</b><b>\"ignoreCRLExpiration\":true</b> can be used only if
    <b>downloadCRL</b> has been set true.</td> </tr> </tbody> </table> <br> <b>Note: </b>boolean
    properties accept integers values as well, with 0 considered as false and other values being
    considered as true

    Args:
        id (str):
        body (UpdateTrustCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UpdateTrustCertRespPayload]]
     """


    kwargs = _get_kwargs(
        id=id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateTrustCertRequest,

) -> Optional[Union[Any, UpdateTrustCertRespPayload]]:
    r""" Update the trust certificate already present in the Cisco ISE trust store

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a trusted certificate present in Cisco ISE trust store.</h3>
    The following parameters are used in the PUT request body <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name<sup><font color=red>*required</font></sup></td> <td>Friendly name of the certificate.</td>
    <td>\"name\": \"Trust Certificate\"</td> </tr> <tr> <td>status</td> <td>Status of the
    certificate</td> <td>\"status\": \"Enabled\"</td> </tr> <tr> <td>description</td> <td>Description of
    the certificate</td> <td>\"description\": \"Certificate for secure connection to cisco.com\"</td>
    </tr> <tr> <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and Syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based Admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco Services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>enableOCSPValidation</td> <td>Switch to
    enable or disable OCSP Validation</td> <td>\"enableOCSPValidation\": false</td> </tr> <tr>
    <td>selectedOCSPService</td> <td>Name of selected OCSP Service</td> <td>\"selectedOCSPService\":
    \"INTERNAL_OCSP_SERVICE\"</td> </tr> <tr> <td>rejectIfNoStatusFromOCSP</td> <td>Switch to reject
    certificate if there is no status from OCSP</td> <td>\"rejectIfNoStatusFromOCSP\": false</td> </tr>
    <tr> <td>rejectIfUnreachableFromOCSP</td> <td>Switch to reject certificate if unreachable from
    OCSP</td> <td>\"rejectIfUnreachableFromOCSP\": false</td> </tr> <tr> <td>downloadCRL</td> <td>Switch
    to enable or disable download of CRL</td> <td>\"downloadCRL\": false</td> </tr> <tr>
    <td>crlDistributionUrl</td> <td>Certificate Revocation List Distribution URL</td>
    <td>\"crlDistributionUrl\": \"CRL distribution URL\"</td> </tr> <tr> <td>automaticCRLUpdate</td>
    <td>Switch to enable or disable automatic CRL update</td> <td>\"automaticCRLUpdate\": false</td>
    </tr> <tr> <td>automaticCRLUpdatePeriod</td> <td>Automatic CRL update period</td>
    <td>\"automaticCRLUpdatePeriod\": 5</td> </tr> <tr> <td>automaticCRLUpdateUnits</td> <td>Unit of
    time for automatic CRL update</td> <td>\"automaticCRLUpdateUnits\": \"Minutes\"</td> </tr> <tr>
    <td>nonAutomaticCRLUpdatePeriod</td> <td>Non automatic CRL update period</td>
    <td>\"nonAutomaticCRLUpdatePeriod\": 1</td> </tr> <tr> <td>nonAutomaticCRLUpdateUnits</td> <td>Unit
    of time of non automatic CRL update</td> <td>\"nonAutomaticCRLUpdateUnits\": \"Hours\"</td> </tr>
    <tr> <td>crlDownloadFailureRetries</td> <td>If CRL download fails, wait time before retry</td>
    <td>\"crlDownloadFailureRetries\": 10</td> </tr> <tr> <td>crlDownloadFailureRetriesUnits</td>
    <td>Unit of time before retry if CRL download fails</td> <td>\"crlDownloadFailureRetriesUnits\":
    \"Minutes\"</td> </tr> <tr> <td>enableServerIdentityCheck</td> <td>Switch to enable or disable
    verification if HTTPS or LDAP server certificate name fits the configured server URL</td>
    <td>\"enableServerIdentityCheck\": false</td> </tr> <tr> <td>authenticateBeforeCRLReceived</td>
    <td>Switch to enable or disable CRL Verification if CRL is not Received</td>
    <td>\"authenticateBeforeCRLReceived\": false</td> </tr> <tr> <td>ignoreCRLExpiration</td> <td>Switch
    to enable or disable ignore CRL Expiration</td> <td>\"ignoreCRLExpiration\": false</td> </tr>
    </tbody> </table></br> <hr/> <table class=\"certTable\"> <thead> <tr> <th>Trusted For</th>
    <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. Also check this box if
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"trustForClientAuth\" can be set true
    only if \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b> \"trustForCertificateBasedAdminAuth\" can be set true only if \"trustForIseAuth\" and
    \"trustForClientAuth\" are true.</td></td> </tr> <tr> <td>Authentication of Cisco Services</td> <td>
    Use <b>\"trustForCiscoServicesAuth\":true</b> if the certificate is to be used for trusting external
    Cisco services, such as Feed Service.</td> </tr> </tbody> </table> <table class=\"certTable\">
    <thead> <tr> <th>OCSP Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation
    against OCSP service</td> <td>Use <b>\"enableOCSPValidation\":true</b> to validate the certificate
    against OCSP service mentioned in the field <b>selectedOCSPService</b>.</td> </tr> <tr> <td>OCSP
    Service name</td> <td>Use <b>\"selectedOCSPService\":\"Name of OCSP Service\"</b> to mention the
    OCSP service name against which the certificate should be validated.</br> <b>Note:</b>
    <b>selectedOCSPService</b> value is used if <b>enableOCSPValidation</b> has been set true.</td>
    </tr> <tr> <td>Reject the request if OCSP returns UNKNOWN status</td> <td>Use
    <b>\"rejectIfNoStatusFromOCSP\":true</b> to reject the certificate if the OCSP service returns
    UNKNOWN status.</br> <b>Note:</b> <b>\"rejectIfNoStatusFromOCSP\":true</b> can be used only if the
    parameter <b>enableOCSPValidation</b> has been set true.</td> </tr> <tr> <td>Reject the request if
    OCSP Responder is unreachable</td> <td> Use <b>\"rejectIfUnreachableFromOCSP\":true</b> to reject
    the certificate if the OCSP service is unreachable.</br> <b>Note:</b>
    <b>\"rejectIfUnreachableFromOCSP\":true</b> can be used only if <b>enableOCSPValidation</b> has been
    set true.</td> </tr> </tbody> </table> <table class=\"certTable\"> <thead> <tr> <th>Certificate
    Revocation List Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation against
    CRL</td> <td>Use <b>\"downloadCRL\":true</b> to validate the certificate against CRL downloaded from
    URL mentioned in the field <b>crlDistributionUrl</b></td> </tr> <tr> <td>CRL distribution url</td>
    <td>Use <b>\"crlDistributionUrl\"</b> to specify the URL from where the CRL should be
    downloaded</br> <b>Note:</b> \"crlDistributionUrl\" value is used if \"downloadCRL\" has been set
    true.</td> </tr> <tr> <td>Retrieve CRL time</td> <td>Use <b>\"automaticCRLUpdate\":true</b>,
    <b>automaticCRLUpdatePeriod</b>, and <b>automaticCRLUpdatePeriod</b> to set the time before which
    CRL is automatically retrieved prior to expiration</br> Use <b>nonAutomaticCRLUpdatePeriod</b> and
    <b>nonAutomaticCRLUpdateUnits</b> to set the time period for CRL retrieval in loop.<br> <b>Note:</b>
    All the above fields can be used only if <b>\"downloadCRL\"</b> has been set true.</td> </tr> <tr>
    <td>If download fails</td> <td>Use <b>\"crlDownloadFailureRetries\" and
    \"crlDownloadFailureRetriesUnits\"</b> to set retry time period if CRL download fails</br>
    <b>Note:</b><b>crlDownloadFailureRetries</b> and <b>crlDownloadFailureRetriesUnits</b> can be used
    only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Enable Server Identity Check</td>
    <td>Use <b>\"enableServerIdentityCheck\":true</b> to verify that HTTPS or LDAPS server certificate
    name fits the configured server URL</br> <b>Note:</b><b>\"enableServerIdentityCheck\":true</b> can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Bypass CRL Verification if
    CRL is not Received</td> <td>Use <b>\"authenticateBeforeCRLReceived\":true</b> to bypass CRL
    Verification if CRL is not Received</br> <b>Note:</b><b>\"authenticateBeforeCRLReceived\":true can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Ignore that CRL is not yet
    valid or has expired</td> <td> Use <b>\"ignoreCRLExpiration\":true</b> to ignore if CRL is not yet
    valid or expired</br> <b>Note:</b><b>\"ignoreCRLExpiration\":true</b> can be used only if
    <b>downloadCRL</b> has been set true.</td> </tr> </tbody> </table> <br> <b>Note: </b>boolean
    properties accept integers values as well, with 0 considered as false and other values being
    considered as true

    Args:
        id (str):
        body (UpdateTrustCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UpdateTrustCertRespPayload]
     """


    return sync_detailed(
        id=id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateTrustCertRequest,

) -> Response[Union[Any, UpdateTrustCertRespPayload]]:
    r""" Update the trust certificate already present in the Cisco ISE trust store

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a trusted certificate present in Cisco ISE trust store.</h3>
    The following parameters are used in the PUT request body <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name<sup><font color=red>*required</font></sup></td> <td>Friendly name of the certificate.</td>
    <td>\"name\": \"Trust Certificate\"</td> </tr> <tr> <td>status</td> <td>Status of the
    certificate</td> <td>\"status\": \"Enabled\"</td> </tr> <tr> <td>description</td> <td>Description of
    the certificate</td> <td>\"description\": \"Certificate for secure connection to cisco.com\"</td>
    </tr> <tr> <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and Syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based Admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco Services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>enableOCSPValidation</td> <td>Switch to
    enable or disable OCSP Validation</td> <td>\"enableOCSPValidation\": false</td> </tr> <tr>
    <td>selectedOCSPService</td> <td>Name of selected OCSP Service</td> <td>\"selectedOCSPService\":
    \"INTERNAL_OCSP_SERVICE\"</td> </tr> <tr> <td>rejectIfNoStatusFromOCSP</td> <td>Switch to reject
    certificate if there is no status from OCSP</td> <td>\"rejectIfNoStatusFromOCSP\": false</td> </tr>
    <tr> <td>rejectIfUnreachableFromOCSP</td> <td>Switch to reject certificate if unreachable from
    OCSP</td> <td>\"rejectIfUnreachableFromOCSP\": false</td> </tr> <tr> <td>downloadCRL</td> <td>Switch
    to enable or disable download of CRL</td> <td>\"downloadCRL\": false</td> </tr> <tr>
    <td>crlDistributionUrl</td> <td>Certificate Revocation List Distribution URL</td>
    <td>\"crlDistributionUrl\": \"CRL distribution URL\"</td> </tr> <tr> <td>automaticCRLUpdate</td>
    <td>Switch to enable or disable automatic CRL update</td> <td>\"automaticCRLUpdate\": false</td>
    </tr> <tr> <td>automaticCRLUpdatePeriod</td> <td>Automatic CRL update period</td>
    <td>\"automaticCRLUpdatePeriod\": 5</td> </tr> <tr> <td>automaticCRLUpdateUnits</td> <td>Unit of
    time for automatic CRL update</td> <td>\"automaticCRLUpdateUnits\": \"Minutes\"</td> </tr> <tr>
    <td>nonAutomaticCRLUpdatePeriod</td> <td>Non automatic CRL update period</td>
    <td>\"nonAutomaticCRLUpdatePeriod\": 1</td> </tr> <tr> <td>nonAutomaticCRLUpdateUnits</td> <td>Unit
    of time of non automatic CRL update</td> <td>\"nonAutomaticCRLUpdateUnits\": \"Hours\"</td> </tr>
    <tr> <td>crlDownloadFailureRetries</td> <td>If CRL download fails, wait time before retry</td>
    <td>\"crlDownloadFailureRetries\": 10</td> </tr> <tr> <td>crlDownloadFailureRetriesUnits</td>
    <td>Unit of time before retry if CRL download fails</td> <td>\"crlDownloadFailureRetriesUnits\":
    \"Minutes\"</td> </tr> <tr> <td>enableServerIdentityCheck</td> <td>Switch to enable or disable
    verification if HTTPS or LDAP server certificate name fits the configured server URL</td>
    <td>\"enableServerIdentityCheck\": false</td> </tr> <tr> <td>authenticateBeforeCRLReceived</td>
    <td>Switch to enable or disable CRL Verification if CRL is not Received</td>
    <td>\"authenticateBeforeCRLReceived\": false</td> </tr> <tr> <td>ignoreCRLExpiration</td> <td>Switch
    to enable or disable ignore CRL Expiration</td> <td>\"ignoreCRLExpiration\": false</td> </tr>
    </tbody> </table></br> <hr/> <table class=\"certTable\"> <thead> <tr> <th>Trusted For</th>
    <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. Also check this box if
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"trustForClientAuth\" can be set true
    only if \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b> \"trustForCertificateBasedAdminAuth\" can be set true only if \"trustForIseAuth\" and
    \"trustForClientAuth\" are true.</td></td> </tr> <tr> <td>Authentication of Cisco Services</td> <td>
    Use <b>\"trustForCiscoServicesAuth\":true</b> if the certificate is to be used for trusting external
    Cisco services, such as Feed Service.</td> </tr> </tbody> </table> <table class=\"certTable\">
    <thead> <tr> <th>OCSP Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation
    against OCSP service</td> <td>Use <b>\"enableOCSPValidation\":true</b> to validate the certificate
    against OCSP service mentioned in the field <b>selectedOCSPService</b>.</td> </tr> <tr> <td>OCSP
    Service name</td> <td>Use <b>\"selectedOCSPService\":\"Name of OCSP Service\"</b> to mention the
    OCSP service name against which the certificate should be validated.</br> <b>Note:</b>
    <b>selectedOCSPService</b> value is used if <b>enableOCSPValidation</b> has been set true.</td>
    </tr> <tr> <td>Reject the request if OCSP returns UNKNOWN status</td> <td>Use
    <b>\"rejectIfNoStatusFromOCSP\":true</b> to reject the certificate if the OCSP service returns
    UNKNOWN status.</br> <b>Note:</b> <b>\"rejectIfNoStatusFromOCSP\":true</b> can be used only if the
    parameter <b>enableOCSPValidation</b> has been set true.</td> </tr> <tr> <td>Reject the request if
    OCSP Responder is unreachable</td> <td> Use <b>\"rejectIfUnreachableFromOCSP\":true</b> to reject
    the certificate if the OCSP service is unreachable.</br> <b>Note:</b>
    <b>\"rejectIfUnreachableFromOCSP\":true</b> can be used only if <b>enableOCSPValidation</b> has been
    set true.</td> </tr> </tbody> </table> <table class=\"certTable\"> <thead> <tr> <th>Certificate
    Revocation List Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation against
    CRL</td> <td>Use <b>\"downloadCRL\":true</b> to validate the certificate against CRL downloaded from
    URL mentioned in the field <b>crlDistributionUrl</b></td> </tr> <tr> <td>CRL distribution url</td>
    <td>Use <b>\"crlDistributionUrl\"</b> to specify the URL from where the CRL should be
    downloaded</br> <b>Note:</b> \"crlDistributionUrl\" value is used if \"downloadCRL\" has been set
    true.</td> </tr> <tr> <td>Retrieve CRL time</td> <td>Use <b>\"automaticCRLUpdate\":true</b>,
    <b>automaticCRLUpdatePeriod</b>, and <b>automaticCRLUpdatePeriod</b> to set the time before which
    CRL is automatically retrieved prior to expiration</br> Use <b>nonAutomaticCRLUpdatePeriod</b> and
    <b>nonAutomaticCRLUpdateUnits</b> to set the time period for CRL retrieval in loop.<br> <b>Note:</b>
    All the above fields can be used only if <b>\"downloadCRL\"</b> has been set true.</td> </tr> <tr>
    <td>If download fails</td> <td>Use <b>\"crlDownloadFailureRetries\" and
    \"crlDownloadFailureRetriesUnits\"</b> to set retry time period if CRL download fails</br>
    <b>Note:</b><b>crlDownloadFailureRetries</b> and <b>crlDownloadFailureRetriesUnits</b> can be used
    only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Enable Server Identity Check</td>
    <td>Use <b>\"enableServerIdentityCheck\":true</b> to verify that HTTPS or LDAPS server certificate
    name fits the configured server URL</br> <b>Note:</b><b>\"enableServerIdentityCheck\":true</b> can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Bypass CRL Verification if
    CRL is not Received</td> <td>Use <b>\"authenticateBeforeCRLReceived\":true</b> to bypass CRL
    Verification if CRL is not Received</br> <b>Note:</b><b>\"authenticateBeforeCRLReceived\":true can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Ignore that CRL is not yet
    valid or has expired</td> <td> Use <b>\"ignoreCRLExpiration\":true</b> to ignore if CRL is not yet
    valid or expired</br> <b>Note:</b><b>\"ignoreCRLExpiration\":true</b> can be used only if
    <b>downloadCRL</b> has been set true.</td> </tr> </tbody> </table> <br> <b>Note: </b>boolean
    properties accept integers values as well, with 0 considered as false and other values being
    considered as true

    Args:
        id (str):
        body (UpdateTrustCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UpdateTrustCertRespPayload]]
     """


    kwargs = _get_kwargs(
        id=id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateTrustCertRequest,

) -> Optional[Union[Any, UpdateTrustCertRespPayload]]:
    r""" Update the trust certificate already present in the Cisco ISE trust store

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a trusted certificate present in Cisco ISE trust store.</h3>
    The following parameters are used in the PUT request body <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name<sup><font color=red>*required</font></sup></td> <td>Friendly name of the certificate.</td>
    <td>\"name\": \"Trust Certificate\"</td> </tr> <tr> <td>status</td> <td>Status of the
    certificate</td> <td>\"status\": \"Enabled\"</td> </tr> <tr> <td>description</td> <td>Description of
    the certificate</td> <td>\"description\": \"Certificate for secure connection to cisco.com\"</td>
    </tr> <tr> <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and Syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based Admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco Services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>enableOCSPValidation</td> <td>Switch to
    enable or disable OCSP Validation</td> <td>\"enableOCSPValidation\": false</td> </tr> <tr>
    <td>selectedOCSPService</td> <td>Name of selected OCSP Service</td> <td>\"selectedOCSPService\":
    \"INTERNAL_OCSP_SERVICE\"</td> </tr> <tr> <td>rejectIfNoStatusFromOCSP</td> <td>Switch to reject
    certificate if there is no status from OCSP</td> <td>\"rejectIfNoStatusFromOCSP\": false</td> </tr>
    <tr> <td>rejectIfUnreachableFromOCSP</td> <td>Switch to reject certificate if unreachable from
    OCSP</td> <td>\"rejectIfUnreachableFromOCSP\": false</td> </tr> <tr> <td>downloadCRL</td> <td>Switch
    to enable or disable download of CRL</td> <td>\"downloadCRL\": false</td> </tr> <tr>
    <td>crlDistributionUrl</td> <td>Certificate Revocation List Distribution URL</td>
    <td>\"crlDistributionUrl\": \"CRL distribution URL\"</td> </tr> <tr> <td>automaticCRLUpdate</td>
    <td>Switch to enable or disable automatic CRL update</td> <td>\"automaticCRLUpdate\": false</td>
    </tr> <tr> <td>automaticCRLUpdatePeriod</td> <td>Automatic CRL update period</td>
    <td>\"automaticCRLUpdatePeriod\": 5</td> </tr> <tr> <td>automaticCRLUpdateUnits</td> <td>Unit of
    time for automatic CRL update</td> <td>\"automaticCRLUpdateUnits\": \"Minutes\"</td> </tr> <tr>
    <td>nonAutomaticCRLUpdatePeriod</td> <td>Non automatic CRL update period</td>
    <td>\"nonAutomaticCRLUpdatePeriod\": 1</td> </tr> <tr> <td>nonAutomaticCRLUpdateUnits</td> <td>Unit
    of time of non automatic CRL update</td> <td>\"nonAutomaticCRLUpdateUnits\": \"Hours\"</td> </tr>
    <tr> <td>crlDownloadFailureRetries</td> <td>If CRL download fails, wait time before retry</td>
    <td>\"crlDownloadFailureRetries\": 10</td> </tr> <tr> <td>crlDownloadFailureRetriesUnits</td>
    <td>Unit of time before retry if CRL download fails</td> <td>\"crlDownloadFailureRetriesUnits\":
    \"Minutes\"</td> </tr> <tr> <td>enableServerIdentityCheck</td> <td>Switch to enable or disable
    verification if HTTPS or LDAP server certificate name fits the configured server URL</td>
    <td>\"enableServerIdentityCheck\": false</td> </tr> <tr> <td>authenticateBeforeCRLReceived</td>
    <td>Switch to enable or disable CRL Verification if CRL is not Received</td>
    <td>\"authenticateBeforeCRLReceived\": false</td> </tr> <tr> <td>ignoreCRLExpiration</td> <td>Switch
    to enable or disable ignore CRL Expiration</td> <td>\"ignoreCRLExpiration\": false</td> </tr>
    </tbody> </table></br> <hr/> <table class=\"certTable\"> <thead> <tr> <th>Trusted For</th>
    <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. Also check this box if
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"trustForClientAuth\" can be set true
    only if \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b> \"trustForCertificateBasedAdminAuth\" can be set true only if \"trustForIseAuth\" and
    \"trustForClientAuth\" are true.</td></td> </tr> <tr> <td>Authentication of Cisco Services</td> <td>
    Use <b>\"trustForCiscoServicesAuth\":true</b> if the certificate is to be used for trusting external
    Cisco services, such as Feed Service.</td> </tr> </tbody> </table> <table class=\"certTable\">
    <thead> <tr> <th>OCSP Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation
    against OCSP service</td> <td>Use <b>\"enableOCSPValidation\":true</b> to validate the certificate
    against OCSP service mentioned in the field <b>selectedOCSPService</b>.</td> </tr> <tr> <td>OCSP
    Service name</td> <td>Use <b>\"selectedOCSPService\":\"Name of OCSP Service\"</b> to mention the
    OCSP service name against which the certificate should be validated.</br> <b>Note:</b>
    <b>selectedOCSPService</b> value is used if <b>enableOCSPValidation</b> has been set true.</td>
    </tr> <tr> <td>Reject the request if OCSP returns UNKNOWN status</td> <td>Use
    <b>\"rejectIfNoStatusFromOCSP\":true</b> to reject the certificate if the OCSP service returns
    UNKNOWN status.</br> <b>Note:</b> <b>\"rejectIfNoStatusFromOCSP\":true</b> can be used only if the
    parameter <b>enableOCSPValidation</b> has been set true.</td> </tr> <tr> <td>Reject the request if
    OCSP Responder is unreachable</td> <td> Use <b>\"rejectIfUnreachableFromOCSP\":true</b> to reject
    the certificate if the OCSP service is unreachable.</br> <b>Note:</b>
    <b>\"rejectIfUnreachableFromOCSP\":true</b> can be used only if <b>enableOCSPValidation</b> has been
    set true.</td> </tr> </tbody> </table> <table class=\"certTable\"> <thead> <tr> <th>Certificate
    Revocation List Configuration</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Validation against
    CRL</td> <td>Use <b>\"downloadCRL\":true</b> to validate the certificate against CRL downloaded from
    URL mentioned in the field <b>crlDistributionUrl</b></td> </tr> <tr> <td>CRL distribution url</td>
    <td>Use <b>\"crlDistributionUrl\"</b> to specify the URL from where the CRL should be
    downloaded</br> <b>Note:</b> \"crlDistributionUrl\" value is used if \"downloadCRL\" has been set
    true.</td> </tr> <tr> <td>Retrieve CRL time</td> <td>Use <b>\"automaticCRLUpdate\":true</b>,
    <b>automaticCRLUpdatePeriod</b>, and <b>automaticCRLUpdatePeriod</b> to set the time before which
    CRL is automatically retrieved prior to expiration</br> Use <b>nonAutomaticCRLUpdatePeriod</b> and
    <b>nonAutomaticCRLUpdateUnits</b> to set the time period for CRL retrieval in loop.<br> <b>Note:</b>
    All the above fields can be used only if <b>\"downloadCRL\"</b> has been set true.</td> </tr> <tr>
    <td>If download fails</td> <td>Use <b>\"crlDownloadFailureRetries\" and
    \"crlDownloadFailureRetriesUnits\"</b> to set retry time period if CRL download fails</br>
    <b>Note:</b><b>crlDownloadFailureRetries</b> and <b>crlDownloadFailureRetriesUnits</b> can be used
    only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Enable Server Identity Check</td>
    <td>Use <b>\"enableServerIdentityCheck\":true</b> to verify that HTTPS or LDAPS server certificate
    name fits the configured server URL</br> <b>Note:</b><b>\"enableServerIdentityCheck\":true</b> can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Bypass CRL Verification if
    CRL is not Received</td> <td>Use <b>\"authenticateBeforeCRLReceived\":true</b> to bypass CRL
    Verification if CRL is not Received</br> <b>Note:</b><b>\"authenticateBeforeCRLReceived\":true can
    be used only if <b>downloadCRL</b> has been set true.</td> </tr> <tr> <td>Ignore that CRL is not yet
    valid or has expired</td> <td> Use <b>\"ignoreCRLExpiration\":true</b> to ignore if CRL is not yet
    valid or expired</br> <b>Note:</b><b>\"ignoreCRLExpiration\":true</b> can be used only if
    <b>downloadCRL</b> has been set true.</td> </tr> </tbody> </table> <br> <b>Note: </b>boolean
    properties accept integers values as well, with 0 considered as false and other values being
    considered as true

    Args:
        id (str):
        body (UpdateTrustCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UpdateTrustCertRespPayload]
     """


    return (await asyncio_detailed(
        id=id,
client=client,
body=body,

    )).parsed
