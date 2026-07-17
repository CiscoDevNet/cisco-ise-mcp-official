# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.import_trust_cert_resp_payload import ImportTrustCertRespPayload
from ...models.trust_cert import TrustCert
from typing import cast



def _get_kwargs(
    *,
    body: TrustCert,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/trusted-certificate/import",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, ImportTrustCertRespPayload]]:
    if response.status_code == 200:
        response_200 = ImportTrustCertRespPayload.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



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
    if response.status_code == 405:
        response_405 = Error.from_dict(response.json())



        return response_405
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409
    if response.status_code == 417:
        response_417 = Error.from_dict(response.json())



        return response_417
    if response.status_code == 422:
        response_422 = Error.from_dict(response.json())



        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, ImportTrustCertRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: TrustCert,

) -> Response[Union[Any, Error, ImportTrustCertRespPayload]]:
    r""" Add root certificate to the Cisco ISE truststore

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a trust certificate</h3><br>
    <p><b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1< and 0<
    respectively.<br> Following parameters are used in the POST body:</p> <table class=\"certTable\">
    <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name</td> <td>Friendly name of the certificate</td> <td>\"name\": \"Trust Certificate\"</td>
    </tr> <tr> <td>description</td> <td>Description of the certificate</td> <td>\"description\":
    \"Imported Trust Certificate\"</td> </tr> <tr> <td>data<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the certificate file. Every space
    needs to be replaced with a newline escape sequence (\n).<br/> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data
    from the certificate file. </td> <td>\"data\": \"Plain-text contents of the certificate file.\"</td>
    </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td> Allow out of
    date certificates.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1Certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses
    SHA-1 hashing algorithm and is considered less secure.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1Certificates</b> as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1Certificates\": true</td> </tr> <tr>
    <td>allowBasicConstraintCAFalse<sup><font color=red>*required</font></sup></td> <td> Allow
    certificates with Basic Constraints CA Field as False.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowBasicConstraintCAFalse</b> as <b>false</b> to avoid the import of
    certificates with <b>Basic Constraints CA Field</b> set as <b>False</b> (not Secure). </td>
    <td>\"allowBasicConstraintCAFalse\": true</td> </tr> <tr> <td>allowMultipleCNCert</td> <td> Allow
    import of certificates with Multiple CN</br> <b>SECURITY ALERT: </b>We recommend to set the
    parameter <b>allowMultipleCNCert</b> as <b>false</b> to avoid the import of certificates with
    multiple CN as such certificates are not RFC recommended and might impact ISE functionalities like
    PxGrid certificate generation. </td> <td>\"allowMultipleCNCert\": false</td> </tr> <tr>
    <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>validateCertificateExtensions</td>
    <td>Validate extensions for trust certificate</td> <td>\"validateCertificateExtensions\": false</td>
    </tr> </tbody> </table></br> <p><b>NOTE</b>: If <b>name</b> is not set, a default name with the
    following format is used where <b>nnnnn</b> is a unique number: </br> <b>- common-
    name#issuer#nnnnn</b></br> You can always change the friendly name later by editing the
    certificate.</p> <hr/> <p>You must choose how this certificate is trusted in Cisco ISE. The
    objective here is to distinguish between certificates that are used for trust within a Cisco ISE
    deployment and public certificates that are used to trust Cisco services. We recommend not using a
    given certificate for both purposes.</p> <table class=\"certTable\"> <thead> <tr> <th>Trusted
    For</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. This is also used if the
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"\" can be set true only if the
    \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b><b>trustForCertificateBasedAdminAuth</b> can be set true only if both
    <b>trustForIseAuth</b> and <b>trustForClientAuth</b> are true.</td></td> </tr> <tr>
    <td>Authentication of Cisco Services</td> <td> Use <b>\"trustForCiscoServicesAuth\":true</b> if the
    certificate is to be used for trusting external Cisco services, such as Feed Service.</td> </tr>
    </tbody> </table>

    Args:
        body (TrustCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, ImportTrustCertRespPayload]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: TrustCert,

) -> Optional[Union[Any, Error, ImportTrustCertRespPayload]]:
    r""" Add root certificate to the Cisco ISE truststore

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a trust certificate</h3><br>
    <p><b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1< and 0<
    respectively.<br> Following parameters are used in the POST body:</p> <table class=\"certTable\">
    <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name</td> <td>Friendly name of the certificate</td> <td>\"name\": \"Trust Certificate\"</td>
    </tr> <tr> <td>description</td> <td>Description of the certificate</td> <td>\"description\":
    \"Imported Trust Certificate\"</td> </tr> <tr> <td>data<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the certificate file. Every space
    needs to be replaced with a newline escape sequence (\n).<br/> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data
    from the certificate file. </td> <td>\"data\": \"Plain-text contents of the certificate file.\"</td>
    </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td> Allow out of
    date certificates.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1Certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses
    SHA-1 hashing algorithm and is considered less secure.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1Certificates</b> as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1Certificates\": true</td> </tr> <tr>
    <td>allowBasicConstraintCAFalse<sup><font color=red>*required</font></sup></td> <td> Allow
    certificates with Basic Constraints CA Field as False.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowBasicConstraintCAFalse</b> as <b>false</b> to avoid the import of
    certificates with <b>Basic Constraints CA Field</b> set as <b>False</b> (not Secure). </td>
    <td>\"allowBasicConstraintCAFalse\": true</td> </tr> <tr> <td>allowMultipleCNCert</td> <td> Allow
    import of certificates with Multiple CN</br> <b>SECURITY ALERT: </b>We recommend to set the
    parameter <b>allowMultipleCNCert</b> as <b>false</b> to avoid the import of certificates with
    multiple CN as such certificates are not RFC recommended and might impact ISE functionalities like
    PxGrid certificate generation. </td> <td>\"allowMultipleCNCert\": false</td> </tr> <tr>
    <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>validateCertificateExtensions</td>
    <td>Validate extensions for trust certificate</td> <td>\"validateCertificateExtensions\": false</td>
    </tr> </tbody> </table></br> <p><b>NOTE</b>: If <b>name</b> is not set, a default name with the
    following format is used where <b>nnnnn</b> is a unique number: </br> <b>- common-
    name#issuer#nnnnn</b></br> You can always change the friendly name later by editing the
    certificate.</p> <hr/> <p>You must choose how this certificate is trusted in Cisco ISE. The
    objective here is to distinguish between certificates that are used for trust within a Cisco ISE
    deployment and public certificates that are used to trust Cisco services. We recommend not using a
    given certificate for both purposes.</p> <table class=\"certTable\"> <thead> <tr> <th>Trusted
    For</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. This is also used if the
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"\" can be set true only if the
    \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b><b>trustForCertificateBasedAdminAuth</b> can be set true only if both
    <b>trustForIseAuth</b> and <b>trustForClientAuth</b> are true.</td></td> </tr> <tr>
    <td>Authentication of Cisco Services</td> <td> Use <b>\"trustForCiscoServicesAuth\":true</b> if the
    certificate is to be used for trusting external Cisco services, such as Feed Service.</td> </tr>
    </tbody> </table>

    Args:
        body (TrustCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, ImportTrustCertRespPayload]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: TrustCert,

) -> Response[Union[Any, Error, ImportTrustCertRespPayload]]:
    r""" Add root certificate to the Cisco ISE truststore

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a trust certificate</h3><br>
    <p><b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1< and 0<
    respectively.<br> Following parameters are used in the POST body:</p> <table class=\"certTable\">
    <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name</td> <td>Friendly name of the certificate</td> <td>\"name\": \"Trust Certificate\"</td>
    </tr> <tr> <td>description</td> <td>Description of the certificate</td> <td>\"description\":
    \"Imported Trust Certificate\"</td> </tr> <tr> <td>data<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the certificate file. Every space
    needs to be replaced with a newline escape sequence (\n).<br/> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data
    from the certificate file. </td> <td>\"data\": \"Plain-text contents of the certificate file.\"</td>
    </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td> Allow out of
    date certificates.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1Certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses
    SHA-1 hashing algorithm and is considered less secure.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1Certificates</b> as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1Certificates\": true</td> </tr> <tr>
    <td>allowBasicConstraintCAFalse<sup><font color=red>*required</font></sup></td> <td> Allow
    certificates with Basic Constraints CA Field as False.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowBasicConstraintCAFalse</b> as <b>false</b> to avoid the import of
    certificates with <b>Basic Constraints CA Field</b> set as <b>False</b> (not Secure). </td>
    <td>\"allowBasicConstraintCAFalse\": true</td> </tr> <tr> <td>allowMultipleCNCert</td> <td> Allow
    import of certificates with Multiple CN</br> <b>SECURITY ALERT: </b>We recommend to set the
    parameter <b>allowMultipleCNCert</b> as <b>false</b> to avoid the import of certificates with
    multiple CN as such certificates are not RFC recommended and might impact ISE functionalities like
    PxGrid certificate generation. </td> <td>\"allowMultipleCNCert\": false</td> </tr> <tr>
    <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>validateCertificateExtensions</td>
    <td>Validate extensions for trust certificate</td> <td>\"validateCertificateExtensions\": false</td>
    </tr> </tbody> </table></br> <p><b>NOTE</b>: If <b>name</b> is not set, a default name with the
    following format is used where <b>nnnnn</b> is a unique number: </br> <b>- common-
    name#issuer#nnnnn</b></br> You can always change the friendly name later by editing the
    certificate.</p> <hr/> <p>You must choose how this certificate is trusted in Cisco ISE. The
    objective here is to distinguish between certificates that are used for trust within a Cisco ISE
    deployment and public certificates that are used to trust Cisco services. We recommend not using a
    given certificate for both purposes.</p> <table class=\"certTable\"> <thead> <tr> <th>Trusted
    For</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. This is also used if the
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"\" can be set true only if the
    \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b><b>trustForCertificateBasedAdminAuth</b> can be set true only if both
    <b>trustForIseAuth</b> and <b>trustForClientAuth</b> are true.</td></td> </tr> <tr>
    <td>Authentication of Cisco Services</td> <td> Use <b>\"trustForCiscoServicesAuth\":true</b> if the
    certificate is to be used for trusting external Cisco services, such as Feed Service.</td> </tr>
    </tbody> </table>

    Args:
        body (TrustCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, ImportTrustCertRespPayload]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: TrustCert,

) -> Optional[Union[Any, Error, ImportTrustCertRespPayload]]:
    r""" Add root certificate to the Cisco ISE truststore

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a trust certificate</h3><br>
    <p><b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1< and 0<
    respectively.<br> Following parameters are used in the POST body:</p> <table class=\"certTable\">
    <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>name</td> <td>Friendly name of the certificate</td> <td>\"name\": \"Trust Certificate\"</td>
    </tr> <tr> <td>description</td> <td>Description of the certificate</td> <td>\"description\":
    \"Imported Trust Certificate\"</td> </tr> <tr> <td>data<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the certificate file. Every space
    needs to be replaced with a newline escape sequence (\n).<br/> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data
    from the certificate file. </td> <td>\"data\": \"Plain-text contents of the certificate file.\"</td>
    </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td> Allow out of
    date certificates.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1Certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses
    SHA-1 hashing algorithm and is considered less secure.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1Certificates</b> as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1Certificates\": true</td> </tr> <tr>
    <td>allowBasicConstraintCAFalse<sup><font color=red>*required</font></sup></td> <td> Allow
    certificates with Basic Constraints CA Field as False.</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowBasicConstraintCAFalse</b> as <b>false</b> to avoid the import of
    certificates with <b>Basic Constraints CA Field</b> set as <b>False</b> (not Secure). </td>
    <td>\"allowBasicConstraintCAFalse\": true</td> </tr> <tr> <td>allowMultipleCNCert</td> <td> Allow
    import of certificates with Multiple CN</br> <b>SECURITY ALERT: </b>We recommend to set the
    parameter <b>allowMultipleCNCert</b> as <b>false</b> to avoid the import of certificates with
    multiple CN as such certificates are not RFC recommended and might impact ISE functionalities like
    PxGrid certificate generation. </td> <td>\"allowMultipleCNCert\": false</td> </tr> <tr>
    <td>trustForIseAuth</td> <td>Trust for Authentication within ISE and Client-Server
    communication</td> <td>\"trustForIseAuth\": false</td> </tr> <tr> <td>trustForClientAuth</td>
    <td>Trust for client authentication and syslog</td> <td>\"trustForClientAuth\": false</td> </tr>
    <tr> <td>trustForCertificateBasedAdminAuth</td> <td>Trust for certificate based admin
    authentication</td> <td>\"trustForCertificateBasedAdminAuth\": false</td> </tr> <tr>
    <td>trustForCiscoServicesAuth</td> <td>Trust for authentication of Cisco services</td>
    <td>\"trustForCiscoServicesAuth\": false</td> </tr> <tr> <td>validateCertificateExtensions</td>
    <td>Validate extensions for trust certificate</td> <td>\"validateCertificateExtensions\": false</td>
    </tr> </tbody> </table></br> <p><b>NOTE</b>: If <b>name</b> is not set, a default name with the
    following format is used where <b>nnnnn</b> is a unique number: </br> <b>- common-
    name#issuer#nnnnn</b></br> You can always change the friendly name later by editing the
    certificate.</p> <hr/> <p>You must choose how this certificate is trusted in Cisco ISE. The
    objective here is to distinguish between certificates that are used for trust within a Cisco ISE
    deployment and public certificates that are used to trust Cisco services. We recommend not using a
    given certificate for both purposes.</p> <table class=\"certTable\"> <thead> <tr> <th>Trusted
    For</th> <th>Usage</th> </tr> </thead> <tbody> <tr> <td>Authentication within Cisco ISE</td> <td>Use
    <b>\"trustForIseAuth\":true</b> if the certificate is used for trust within Cisco ISE, such as for
    secure communication between Cisco ISE nodes</td> </tr> <tr> <td>Client authentication and
    Syslog</td> <td>Use <b>\"trustForClientAuth\":true</b> if the certificate is to be used for
    authentication of endpoints that contact Cisco ISE over the EAP protocol. This is also used if the
    certificate is used to trust a Syslog server. Make sure to have keyCertSign bit asserted under
    KeyUsage extension for this certificate.</br> <b>Note:</b> \"\" can be set true only if the
    \"trustForIseAuth\" has been set true.</td> </tr> <tr> <td>Certificate based admin
    authentication</td> <td>Use <b>\"trustForCertificateBasedAdminAuth\":true</b> if the certificate is
    used for trust within Cisco ISE, such as for secure communication between Cisco ISE nodes</br>
    <b>Note:</b><b>trustForCertificateBasedAdminAuth</b> can be set true only if both
    <b>trustForIseAuth</b> and <b>trustForClientAuth</b> are true.</td></td> </tr> <tr>
    <td>Authentication of Cisco Services</td> <td> Use <b>\"trustForCiscoServicesAuth\":true</b> if the
    certificate is to be used for trusting external Cisco services, such as Feed Service.</td> </tr>
    </tbody> </table>

    Args:
        body (TrustCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, ImportTrustCertRespPayload]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
