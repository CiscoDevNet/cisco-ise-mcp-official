# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.bind_csr_request import BindCSRRequest
from ...models.bind_csr_resp_payload import BindCSRRespPayload
from ...models.error import Error
from typing import cast



def _get_kwargs(
    *,
    body: BindCSRRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/signed-certificate/bind",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, BindCSRRespPayload, Error]]:
    if response.status_code == 200:
        response_200 = BindCSRRespPayload.from_dict(response.json())



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
        response_403 = Error.from_dict(response.json())



        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, BindCSRRespPayload, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BindCSRRequest,

) -> Response[Union[Any, BindCSRRespPayload, Error]]:
    r""" Bind CA Signed Certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Bind CA Signed Certificate.</h3> <b>NOTE: </b>This API requires an
    existing certificate signing request, and the root certificate must already be trusted.<br> <b>NOTE:
    </b>The certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively.<br> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\": \"CA
    Signed Certificate\"</td> </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td>
    Plain-text contents of the certificate file. Every space needs to be replaced with a newline escape
    sequence (\n).<br/> Use the command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos;
    &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data from certificate file. </td> <td>\"data\":
    \"Plain-text contents of the certificate file.\"</td> </tr> <tr> <td>allowExtendedValidity<sup><font
    color=red>*required</font></sup></td> <td>Allow the certificates with validity greater than 398
    days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr> <td>allowOutOfDateCert<sup><font
    color=red>*required</font></sup></td> <td> Allow out of date certificates.</br> <b>SECURITY ALERT:
    </b>We recommend to set the parameter the parameter <b>allowOutOfDateCert</b> as <b>false</b> to
    avoid binding of expired certificates (not secure). </td> <td>\"allowOutOfDateCert\": true</td>
    </tr> <tr> <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td>
    <td>Allow Replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr>
    <tr> <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr>
    <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin Portal</td> <td>\"admin\":
    false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols that use SSL/TLS
    tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use certificate for RADSec
    server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid
    Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use certificate for the Cisco
    ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use certificate for TACACS
    server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal Certificate
    Group\"</td> </tr> <tr> <td>validateCertificateExtensions</td> <td>Validate Certificate
    Extensions</td> <td>\"validateCertificateExtensions\": false</td> </tr> </tbody> </table> <br/>
    <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr>
    <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates.</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates.</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other Usage. Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (BindCSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BindCSRRespPayload, Error]]
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
    body: BindCSRRequest,

) -> Optional[Union[Any, BindCSRRespPayload, Error]]:
    r""" Bind CA Signed Certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Bind CA Signed Certificate.</h3> <b>NOTE: </b>This API requires an
    existing certificate signing request, and the root certificate must already be trusted.<br> <b>NOTE:
    </b>The certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively.<br> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\": \"CA
    Signed Certificate\"</td> </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td>
    Plain-text contents of the certificate file. Every space needs to be replaced with a newline escape
    sequence (\n).<br/> Use the command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos;
    &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data from certificate file. </td> <td>\"data\":
    \"Plain-text contents of the certificate file.\"</td> </tr> <tr> <td>allowExtendedValidity<sup><font
    color=red>*required</font></sup></td> <td>Allow the certificates with validity greater than 398
    days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr> <td>allowOutOfDateCert<sup><font
    color=red>*required</font></sup></td> <td> Allow out of date certificates.</br> <b>SECURITY ALERT:
    </b>We recommend to set the parameter the parameter <b>allowOutOfDateCert</b> as <b>false</b> to
    avoid binding of expired certificates (not secure). </td> <td>\"allowOutOfDateCert\": true</td>
    </tr> <tr> <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td>
    <td>Allow Replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr>
    <tr> <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr>
    <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin Portal</td> <td>\"admin\":
    false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols that use SSL/TLS
    tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use certificate for RADSec
    server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid
    Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use certificate for the Cisco
    ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use certificate for TACACS
    server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal Certificate
    Group\"</td> </tr> <tr> <td>validateCertificateExtensions</td> <td>Validate Certificate
    Extensions</td> <td>\"validateCertificateExtensions\": false</td> </tr> </tbody> </table> <br/>
    <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr>
    <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates.</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates.</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other Usage. Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (BindCSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BindCSRRespPayload, Error]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BindCSRRequest,

) -> Response[Union[Any, BindCSRRespPayload, Error]]:
    r""" Bind CA Signed Certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Bind CA Signed Certificate.</h3> <b>NOTE: </b>This API requires an
    existing certificate signing request, and the root certificate must already be trusted.<br> <b>NOTE:
    </b>The certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively.<br> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\": \"CA
    Signed Certificate\"</td> </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td>
    Plain-text contents of the certificate file. Every space needs to be replaced with a newline escape
    sequence (\n).<br/> Use the command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos;
    &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data from certificate file. </td> <td>\"data\":
    \"Plain-text contents of the certificate file.\"</td> </tr> <tr> <td>allowExtendedValidity<sup><font
    color=red>*required</font></sup></td> <td>Allow the certificates with validity greater than 398
    days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr> <td>allowOutOfDateCert<sup><font
    color=red>*required</font></sup></td> <td> Allow out of date certificates.</br> <b>SECURITY ALERT:
    </b>We recommend to set the parameter the parameter <b>allowOutOfDateCert</b> as <b>false</b> to
    avoid binding of expired certificates (not secure). </td> <td>\"allowOutOfDateCert\": true</td>
    </tr> <tr> <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td>
    <td>Allow Replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr>
    <tr> <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr>
    <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin Portal</td> <td>\"admin\":
    false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols that use SSL/TLS
    tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use certificate for RADSec
    server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid
    Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use certificate for the Cisco
    ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use certificate for TACACS
    server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal Certificate
    Group\"</td> </tr> <tr> <td>validateCertificateExtensions</td> <td>Validate Certificate
    Extensions</td> <td>\"validateCertificateExtensions\": false</td> </tr> </tbody> </table> <br/>
    <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr>
    <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates.</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates.</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other Usage. Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (BindCSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BindCSRRespPayload, Error]]
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
    body: BindCSRRequest,

) -> Optional[Union[Any, BindCSRRespPayload, Error]]:
    r""" Bind CA Signed Certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Bind CA Signed Certificate.</h3> <b>NOTE: </b>This API requires an
    existing certificate signing request, and the root certificate must already be trusted.<br> <b>NOTE:
    </b>The certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively.<br> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\": \"CA
    Signed Certificate\"</td> </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td>
    Plain-text contents of the certificate file. Every space needs to be replaced with a newline escape
    sequence (\n).<br/> Use the command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos;
    &lt;&lt;your .pem file&gt;&gt;</cmd> to extract data from certificate file. </td> <td>\"data\":
    \"Plain-text contents of the certificate file.\"</td> </tr> <tr> <td>allowExtendedValidity<sup><font
    color=red>*required</font></sup></td> <td>Allow the certificates with validity greater than 398
    days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr> <td>allowOutOfDateCert<sup><font
    color=red>*required</font></sup></td> <td> Allow out of date certificates.</br> <b>SECURITY ALERT:
    </b>We recommend to set the parameter the parameter <b>allowOutOfDateCert</b> as <b>false</b> to
    avoid binding of expired certificates (not secure). </td> <td>\"allowOutOfDateCert\": true</td>
    </tr> <tr> <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td>
    <td>Allow Replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr>
    <tr> <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr>
    <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin Portal</td> <td>\"admin\":
    false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols that use SSL/TLS
    tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use certificate for RADSec
    server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid
    Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use certificate for the Cisco
    ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use certificate for TACACS
    server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal Certificate
    Group\"</td> </tr> <tr> <td>validateCertificateExtensions</td> <td>Validate Certificate
    Extensions</td> <td>\"validateCertificateExtensions\": false</td> </tr> </tbody> </table> <br/>
    <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr>
    <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates.</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates.</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other Usage. Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (BindCSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BindCSRRespPayload, Error]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
