# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.csr_request import CSRRequest
from ...models.error import Error
from ...models.generate_csr_resp_payload import GenerateCSRRespPayload
from typing import cast



def _get_kwargs(
    *,
    body: CSRRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/certificate-signing-request",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, GenerateCSRRespPayload]]:
    if response.status_code == 200:
        response_200 = GenerateCSRRespPayload.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())



        return response_403
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if response.status_code == 405:
        response_405 = Error.from_dict(response.json())



        return response_405
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, GenerateCSRRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CSRRequest,

) -> Response[Union[Any, Error, GenerateCSRRespPayload]]:
    r""" Generate a Certificate Signing Request (CSR)

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate a certificate signing request for Multi-Use, Admin, EAP
    Authentication, RADIUS DTLS, TACACS,  PxGrid, SAML, Portal and IMS Services.</h3> Following
    parameters are present in the POST request body<br> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>hostnames</td> <td>List of Cisco ISE node hostnames for which CSRs should be generated</td>
    <td>\"hostnames\": [\"ise-host1\", \"ise-host2\"]</td> </tr> <tr> <td>allowWildCardCert</td>
    <td>Allow use of wildCards in certificates</td> <td>\"allowWildCardCert\": false</td> </tr> <tr>
    <td>keyLength<sup><font color=red>*required</font></sup></td> <td>Length of the key used for CSR
    generation.</td> <td>\"keyLength\": \"512\"</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Type of key used for CSR generation either RSA or
    ECDSA.</td> <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>digestType<sup><font
    color=red>*required</font></sup></td> <td>Hash algorithm used for signing CSR.</td>
    <td>\"digestType\": \"SHA-256\"</td> </tr> <tr> <td>usedFor<sup><font
    color=red>*required</font></sup></td> <td>Certificate usage.</td> <td>\"usedFor\": \"MULTI-
    USE\"</td> </tr> <tr> <td>certificatePolicies</td> <td>Certificate policy OID or list of OIDs that
    the certificate should conform to. Use comma or space to separate the OIDs. </td>
    <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr> <tr>
    <td>subjectCommonName<sup><font color=red>*required</font></sup></td> <td>Certificate common name
    (CN).</td> <td>\"subjectCommonName\": \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td>
    <td>Certificate organizational unit (OU).</td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr>
    <tr> <td>subjectOrg</td> <td>Certificate organization (O).</td> <td>\"subjectOrg\": \"Cisco\"</td>
    </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality (L).</td> <td>\"subjectCity\":
    \"San Jose\"</td> </tr> <td>subjectState</td> <td>Certificate state (ST).</td> <td>\"subjectState\":
    \"California\"</td> </tr> <tr> <td>subjectCountry</td> <td>Certificate country (C).</td>
    <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td> <td>Array of SAN (Subject Alternative
    Name) DNS entries (optional).</td> <td>\"sanDNS\": [\"ise.example.com\"]</td> </tr> <td>sanIP</td>
    <td>Array of SAN IP entries (optional).</td> <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr>
    <td>sanURI</td> <td>Array of SAN URI entries (optional).</td> <td>\"sanURI\":
    [\"https://1.1.1.1\"]</td> </tr> <tr> <td>sanDir</td> <td>Array of SAN DIR entries (optional).</td>
    <td>\"sanDir\": [\"CN=AAA,DC=COM,C=IL\"]</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group
    Tag when using certificate for PORTAL service</td> <td>\"portalGroupTag\": \"Default Portal
    Certificate Group\"</td> </tr> </tbody> </table></br> <b>NOTE: </b>For <b>allowWildCardCert</b> to
    be false, the following parameter is mandatory:</br> <b>- hostnames </b></br> <p>When certificate is
    selected to be used for Portal Service, the following parameter is mandatory:</br> <b>-
    portalGroupTag</b></br></p> <hr/>

    Args:
        body (CSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, GenerateCSRRespPayload]]
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
    body: CSRRequest,

) -> Optional[Union[Any, Error, GenerateCSRRespPayload]]:
    r""" Generate a Certificate Signing Request (CSR)

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate a certificate signing request for Multi-Use, Admin, EAP
    Authentication, RADIUS DTLS, TACACS,  PxGrid, SAML, Portal and IMS Services.</h3> Following
    parameters are present in the POST request body<br> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>hostnames</td> <td>List of Cisco ISE node hostnames for which CSRs should be generated</td>
    <td>\"hostnames\": [\"ise-host1\", \"ise-host2\"]</td> </tr> <tr> <td>allowWildCardCert</td>
    <td>Allow use of wildCards in certificates</td> <td>\"allowWildCardCert\": false</td> </tr> <tr>
    <td>keyLength<sup><font color=red>*required</font></sup></td> <td>Length of the key used for CSR
    generation.</td> <td>\"keyLength\": \"512\"</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Type of key used for CSR generation either RSA or
    ECDSA.</td> <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>digestType<sup><font
    color=red>*required</font></sup></td> <td>Hash algorithm used for signing CSR.</td>
    <td>\"digestType\": \"SHA-256\"</td> </tr> <tr> <td>usedFor<sup><font
    color=red>*required</font></sup></td> <td>Certificate usage.</td> <td>\"usedFor\": \"MULTI-
    USE\"</td> </tr> <tr> <td>certificatePolicies</td> <td>Certificate policy OID or list of OIDs that
    the certificate should conform to. Use comma or space to separate the OIDs. </td>
    <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr> <tr>
    <td>subjectCommonName<sup><font color=red>*required</font></sup></td> <td>Certificate common name
    (CN).</td> <td>\"subjectCommonName\": \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td>
    <td>Certificate organizational unit (OU).</td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr>
    <tr> <td>subjectOrg</td> <td>Certificate organization (O).</td> <td>\"subjectOrg\": \"Cisco\"</td>
    </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality (L).</td> <td>\"subjectCity\":
    \"San Jose\"</td> </tr> <td>subjectState</td> <td>Certificate state (ST).</td> <td>\"subjectState\":
    \"California\"</td> </tr> <tr> <td>subjectCountry</td> <td>Certificate country (C).</td>
    <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td> <td>Array of SAN (Subject Alternative
    Name) DNS entries (optional).</td> <td>\"sanDNS\": [\"ise.example.com\"]</td> </tr> <td>sanIP</td>
    <td>Array of SAN IP entries (optional).</td> <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr>
    <td>sanURI</td> <td>Array of SAN URI entries (optional).</td> <td>\"sanURI\":
    [\"https://1.1.1.1\"]</td> </tr> <tr> <td>sanDir</td> <td>Array of SAN DIR entries (optional).</td>
    <td>\"sanDir\": [\"CN=AAA,DC=COM,C=IL\"]</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group
    Tag when using certificate for PORTAL service</td> <td>\"portalGroupTag\": \"Default Portal
    Certificate Group\"</td> </tr> </tbody> </table></br> <b>NOTE: </b>For <b>allowWildCardCert</b> to
    be false, the following parameter is mandatory:</br> <b>- hostnames </b></br> <p>When certificate is
    selected to be used for Portal Service, the following parameter is mandatory:</br> <b>-
    portalGroupTag</b></br></p> <hr/>

    Args:
        body (CSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, GenerateCSRRespPayload]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CSRRequest,

) -> Response[Union[Any, Error, GenerateCSRRespPayload]]:
    r""" Generate a Certificate Signing Request (CSR)

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate a certificate signing request for Multi-Use, Admin, EAP
    Authentication, RADIUS DTLS, TACACS,  PxGrid, SAML, Portal and IMS Services.</h3> Following
    parameters are present in the POST request body<br> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>hostnames</td> <td>List of Cisco ISE node hostnames for which CSRs should be generated</td>
    <td>\"hostnames\": [\"ise-host1\", \"ise-host2\"]</td> </tr> <tr> <td>allowWildCardCert</td>
    <td>Allow use of wildCards in certificates</td> <td>\"allowWildCardCert\": false</td> </tr> <tr>
    <td>keyLength<sup><font color=red>*required</font></sup></td> <td>Length of the key used for CSR
    generation.</td> <td>\"keyLength\": \"512\"</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Type of key used for CSR generation either RSA or
    ECDSA.</td> <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>digestType<sup><font
    color=red>*required</font></sup></td> <td>Hash algorithm used for signing CSR.</td>
    <td>\"digestType\": \"SHA-256\"</td> </tr> <tr> <td>usedFor<sup><font
    color=red>*required</font></sup></td> <td>Certificate usage.</td> <td>\"usedFor\": \"MULTI-
    USE\"</td> </tr> <tr> <td>certificatePolicies</td> <td>Certificate policy OID or list of OIDs that
    the certificate should conform to. Use comma or space to separate the OIDs. </td>
    <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr> <tr>
    <td>subjectCommonName<sup><font color=red>*required</font></sup></td> <td>Certificate common name
    (CN).</td> <td>\"subjectCommonName\": \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td>
    <td>Certificate organizational unit (OU).</td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr>
    <tr> <td>subjectOrg</td> <td>Certificate organization (O).</td> <td>\"subjectOrg\": \"Cisco\"</td>
    </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality (L).</td> <td>\"subjectCity\":
    \"San Jose\"</td> </tr> <td>subjectState</td> <td>Certificate state (ST).</td> <td>\"subjectState\":
    \"California\"</td> </tr> <tr> <td>subjectCountry</td> <td>Certificate country (C).</td>
    <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td> <td>Array of SAN (Subject Alternative
    Name) DNS entries (optional).</td> <td>\"sanDNS\": [\"ise.example.com\"]</td> </tr> <td>sanIP</td>
    <td>Array of SAN IP entries (optional).</td> <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr>
    <td>sanURI</td> <td>Array of SAN URI entries (optional).</td> <td>\"sanURI\":
    [\"https://1.1.1.1\"]</td> </tr> <tr> <td>sanDir</td> <td>Array of SAN DIR entries (optional).</td>
    <td>\"sanDir\": [\"CN=AAA,DC=COM,C=IL\"]</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group
    Tag when using certificate for PORTAL service</td> <td>\"portalGroupTag\": \"Default Portal
    Certificate Group\"</td> </tr> </tbody> </table></br> <b>NOTE: </b>For <b>allowWildCardCert</b> to
    be false, the following parameter is mandatory:</br> <b>- hostnames </b></br> <p>When certificate is
    selected to be used for Portal Service, the following parameter is mandatory:</br> <b>-
    portalGroupTag</b></br></p> <hr/>

    Args:
        body (CSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, GenerateCSRRespPayload]]
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
    body: CSRRequest,

) -> Optional[Union[Any, Error, GenerateCSRRespPayload]]:
    r""" Generate a Certificate Signing Request (CSR)

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate a certificate signing request for Multi-Use, Admin, EAP
    Authentication, RADIUS DTLS, TACACS,  PxGrid, SAML, Portal and IMS Services.</h3> Following
    parameters are present in the POST request body<br> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr>
    <td>hostnames</td> <td>List of Cisco ISE node hostnames for which CSRs should be generated</td>
    <td>\"hostnames\": [\"ise-host1\", \"ise-host2\"]</td> </tr> <tr> <td>allowWildCardCert</td>
    <td>Allow use of wildCards in certificates</td> <td>\"allowWildCardCert\": false</td> </tr> <tr>
    <td>keyLength<sup><font color=red>*required</font></sup></td> <td>Length of the key used for CSR
    generation.</td> <td>\"keyLength\": \"512\"</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Type of key used for CSR generation either RSA or
    ECDSA.</td> <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>digestType<sup><font
    color=red>*required</font></sup></td> <td>Hash algorithm used for signing CSR.</td>
    <td>\"digestType\": \"SHA-256\"</td> </tr> <tr> <td>usedFor<sup><font
    color=red>*required</font></sup></td> <td>Certificate usage.</td> <td>\"usedFor\": \"MULTI-
    USE\"</td> </tr> <tr> <td>certificatePolicies</td> <td>Certificate policy OID or list of OIDs that
    the certificate should conform to. Use comma or space to separate the OIDs. </td>
    <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr> <tr>
    <td>subjectCommonName<sup><font color=red>*required</font></sup></td> <td>Certificate common name
    (CN).</td> <td>\"subjectCommonName\": \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td>
    <td>Certificate organizational unit (OU).</td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr>
    <tr> <td>subjectOrg</td> <td>Certificate organization (O).</td> <td>\"subjectOrg\": \"Cisco\"</td>
    </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality (L).</td> <td>\"subjectCity\":
    \"San Jose\"</td> </tr> <td>subjectState</td> <td>Certificate state (ST).</td> <td>\"subjectState\":
    \"California\"</td> </tr> <tr> <td>subjectCountry</td> <td>Certificate country (C).</td>
    <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td> <td>Array of SAN (Subject Alternative
    Name) DNS entries (optional).</td> <td>\"sanDNS\": [\"ise.example.com\"]</td> </tr> <td>sanIP</td>
    <td>Array of SAN IP entries (optional).</td> <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr>
    <td>sanURI</td> <td>Array of SAN URI entries (optional).</td> <td>\"sanURI\":
    [\"https://1.1.1.1\"]</td> </tr> <tr> <td>sanDir</td> <td>Array of SAN DIR entries (optional).</td>
    <td>\"sanDir\": [\"CN=AAA,DC=COM,C=IL\"]</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group
    Tag when using certificate for PORTAL service</td> <td>\"portalGroupTag\": \"Default Portal
    Certificate Group\"</td> </tr> </tbody> </table></br> <b>NOTE: </b>For <b>allowWildCardCert</b> to
    be false, the following parameter is mandatory:</br> <b>- hostnames </b></br> <p>When certificate is
    selected to be used for Portal Service, the following parameter is mandatory:</br> <b>-
    portalGroupTag</b></br></p> <hr/>

    Args:
        body (CSRRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, GenerateCSRRespPayload]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
