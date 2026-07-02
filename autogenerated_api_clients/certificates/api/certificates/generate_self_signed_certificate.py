from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.generate_selfsigned_cert_request import GenerateSelfsignedCertRequest
from ...models.generate_selfsigned_cert_resp_payload import GenerateSelfsignedCertRespPayload
from typing import cast



def _get_kwargs(
    *,
    body: GenerateSelfsignedCertRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/system-certificate/generate-selfsigned-certificate",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, GenerateSelfsignedCertRespPayload]]:
    if response.status_code == 200:
        response_200 = GenerateSelfsignedCertRespPayload.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201
    if response.status_code == 400:
        response_400 = GenerateSelfsignedCertRespPayload.from_dict(response.json())



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
    if response.status_code == 406:
        response_406 = GenerateSelfsignedCertRespPayload.from_dict(response.json())



        return response_406
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, GenerateSelfsignedCertRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: GenerateSelfsignedCertRequest,

) -> Response[Union[Any, GenerateSelfsignedCertRespPayload]]:
    r""" Generate self-signed certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate Self-signed Certificate</h3> <p><b>NOTE: </b>The
    certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively. <br> <b>NOTE: </b>Wildcard certificate and SAML certificate can be generated
    only on the primary PAN or a standalone node.<br></p> <br/> <h4>Following parameters are used in the
    POST body</h4> <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Hostname or FQDN of the node in which the certificate
    needs to be created.</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"Self-signed System Certificate\"</td>
    </tr> <tr> <td>subjectCommonName</td> <td> Certificate common name (CN)<br/> <b>NOTE: </b><ul><li>CN
    is Mandatory if SAN not configured.</li><li>>Subject can contain a multi-valued CN. For multi-valued
    RDNs, follow the format \"CN=value1, CN=value2\"</li></ul> </td> <td>\"subjectCommonName\":
    \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td> <td> Certificate organizational unit (OU)<br/>
    <b>NOTE: </b>Subject can contain a multi-valued OU. For multi-valued RDNs, follow the format
    \"OU=value1, OU=value2\" </td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr> <tr>
    <td>subjectOrg</td> <td> Certificate organization (O)<br/> <b>NOTE: </b>Subject can contain multi-
    valued O fields. For multi-valued RDNs, follow the format \"O=value1, O=value2\" </td>
    <td>\"subjectOrg\": \"Cisco\"</td> </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality
    (L)</td> <td>\"subjectCity\": \"San Jose\"</td> </tr> <tr> <td>subjectState</td> <td>Certificate
    state (ST)</td> <td>\"subjectState\": \"California\"</td> </tr> <tr> <td>subjectCountry</td>
    <td>Certificate country (C)</td> <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td>
    <td>Array of SAN (Subject Alternative Name) DNS entries</td> <td>\"sanDNS\":
    [\"ise.example.com\"]</td> </tr> <tr> <td>sanIP</td> <td>Array of SAN IP address entries</td>
    <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr> <td>sanURI</td> <td>Array of SAN URI entries</td>
    <td>\"sanURI\": [\"https://1.1.1.1\"]</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Algorithm to use for certificate public key creation.</td>
    <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>keyLength<sup><font
    color=red>*required</font></sup></td> <td>Bit size of the public key.</td> <td>\"keyLength\":
    \"4096\"</td> </tr> <tr> <td>digestType<sup><font color=red>*required</font></sup></td> <td>Digest
    to sign with.</td> <td>\"digestType\": \"SHA-384\"</td> </tr> <tr> <td>certificatePolicies</td>
    <td>Certificate policy OID or list of OIDs that the certificate should conform to. Use comma or
    space to separate the OIDs. </td> <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr>
    <tr> <td>expirationTTL<sup><font color=red>*required</font></sup></td> <td> Certificate expiration
    value.<br/> <b>NOTE: </b>Expiration TTL should be within Unix time limit </td>
    <td>\"expirationTTL\": 2</td> </tr> <tr> <td>expirationTTLUnit<sup><font
    color=red>*required</font></sup></td> <td>Certificate expiration unit.</td>
    <td>\"expirationTTLUnit\": \"years\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to
    authenticate the Cisco ISE Admin Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td>
    <td>Use certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr>
    <tr> <td>radius</td> <td>Use certificate for RADSec server</td> <td>\"radius\": false</td> </tr>
    <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid controller</td> <td>\"pxgrid\": false</td>
    </tr> <tr> <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr>
    <tr> <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowWildCardCertificates</td> <td>Allow use of WildCards in certificates</td>
    <td>\"allowWildCardCertificates\": false</td> </tr> <tr>
    <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td> <td>Allow
    replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with validity greater than 398 days.</td> <td>\"allowExtendedValidity\":
    true</td> </tr> <tr> <td>allowRoleTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with same
    subject.<br/> If the matching certificate on Cisco ISE has either admin or portal role and if the
    request has admin or portal role selected along with <b>allowRoleTransferForSameSubject</b>
    parameter as true, a self-signed certificate would be generated with both admin and portal role
    enabled.</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Acquire
    the group tag of the matching certificate.</br> If the request portal groug tag is different from
    the group tag of the matching certificate (If matching certificate in Cisco ISE has portal role
    enabled), a self-signed certificate would be generated by acquiring the group tag of the matching
    certificate if the <b>allowPortalTagTransferForSameSubject</b> parameter is true.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>allowSanDnsBadName<sup><font
    color=red>*required</font></sup></td> <td> Allow generation of self-signed certificates with bad
    common name & SAN values such as \"example.org.\",\"invalid.\",\"test.\",\"localhost\" and so
    on.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter <b>allowSanDnsBadName</b> as
    <b>false</b> to avoid generation of certificates with bad Common Name & SAN Values which are not
    secure. </td> <td>\"allowSanDnsBadName\": true</td> </tr> <tr>
    <td>allowSanDnsNonResolvable<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with non resolvable Common Name or SAN Values .</td>
    <td>\"allowSanDnsNonResolvable\": true</td> </tr> </tbody> </table> <br/> <table
    class=\"certTable\"> <thead> <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead>
    <tbody> <tr> <td>Admin</td> <td>False</td> <td>Enabling Admin role for this certificate causes an
    application server restart on the selected node.</td> </tr> <tr> <td>EAP Authentication</td>
    <td>False</td> <td>Only one system certificate can be used for EAP. Assigning EAP to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>RADIUS DTLS</td>
    <td>False</td> <td>Only one system certificate can be used for DTLS. Assigning DTLS to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>SAML</td>
    <td>False</td> <td>SAML cannot be used with other Usage.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.</td> </tr> </tbody> </table>

    Args:
        body (GenerateSelfsignedCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GenerateSelfsignedCertRespPayload]]
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
    body: GenerateSelfsignedCertRequest,

) -> Optional[Union[Any, GenerateSelfsignedCertRespPayload]]:
    r""" Generate self-signed certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate Self-signed Certificate</h3> <p><b>NOTE: </b>The
    certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively. <br> <b>NOTE: </b>Wildcard certificate and SAML certificate can be generated
    only on the primary PAN or a standalone node.<br></p> <br/> <h4>Following parameters are used in the
    POST body</h4> <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Hostname or FQDN of the node in which the certificate
    needs to be created.</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"Self-signed System Certificate\"</td>
    </tr> <tr> <td>subjectCommonName</td> <td> Certificate common name (CN)<br/> <b>NOTE: </b><ul><li>CN
    is Mandatory if SAN not configured.</li><li>>Subject can contain a multi-valued CN. For multi-valued
    RDNs, follow the format \"CN=value1, CN=value2\"</li></ul> </td> <td>\"subjectCommonName\":
    \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td> <td> Certificate organizational unit (OU)<br/>
    <b>NOTE: </b>Subject can contain a multi-valued OU. For multi-valued RDNs, follow the format
    \"OU=value1, OU=value2\" </td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr> <tr>
    <td>subjectOrg</td> <td> Certificate organization (O)<br/> <b>NOTE: </b>Subject can contain multi-
    valued O fields. For multi-valued RDNs, follow the format \"O=value1, O=value2\" </td>
    <td>\"subjectOrg\": \"Cisco\"</td> </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality
    (L)</td> <td>\"subjectCity\": \"San Jose\"</td> </tr> <tr> <td>subjectState</td> <td>Certificate
    state (ST)</td> <td>\"subjectState\": \"California\"</td> </tr> <tr> <td>subjectCountry</td>
    <td>Certificate country (C)</td> <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td>
    <td>Array of SAN (Subject Alternative Name) DNS entries</td> <td>\"sanDNS\":
    [\"ise.example.com\"]</td> </tr> <tr> <td>sanIP</td> <td>Array of SAN IP address entries</td>
    <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr> <td>sanURI</td> <td>Array of SAN URI entries</td>
    <td>\"sanURI\": [\"https://1.1.1.1\"]</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Algorithm to use for certificate public key creation.</td>
    <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>keyLength<sup><font
    color=red>*required</font></sup></td> <td>Bit size of the public key.</td> <td>\"keyLength\":
    \"4096\"</td> </tr> <tr> <td>digestType<sup><font color=red>*required</font></sup></td> <td>Digest
    to sign with.</td> <td>\"digestType\": \"SHA-384\"</td> </tr> <tr> <td>certificatePolicies</td>
    <td>Certificate policy OID or list of OIDs that the certificate should conform to. Use comma or
    space to separate the OIDs. </td> <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr>
    <tr> <td>expirationTTL<sup><font color=red>*required</font></sup></td> <td> Certificate expiration
    value.<br/> <b>NOTE: </b>Expiration TTL should be within Unix time limit </td>
    <td>\"expirationTTL\": 2</td> </tr> <tr> <td>expirationTTLUnit<sup><font
    color=red>*required</font></sup></td> <td>Certificate expiration unit.</td>
    <td>\"expirationTTLUnit\": \"years\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to
    authenticate the Cisco ISE Admin Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td>
    <td>Use certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr>
    <tr> <td>radius</td> <td>Use certificate for RADSec server</td> <td>\"radius\": false</td> </tr>
    <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid controller</td> <td>\"pxgrid\": false</td>
    </tr> <tr> <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr>
    <tr> <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowWildCardCertificates</td> <td>Allow use of WildCards in certificates</td>
    <td>\"allowWildCardCertificates\": false</td> </tr> <tr>
    <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td> <td>Allow
    replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with validity greater than 398 days.</td> <td>\"allowExtendedValidity\":
    true</td> </tr> <tr> <td>allowRoleTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with same
    subject.<br/> If the matching certificate on Cisco ISE has either admin or portal role and if the
    request has admin or portal role selected along with <b>allowRoleTransferForSameSubject</b>
    parameter as true, a self-signed certificate would be generated with both admin and portal role
    enabled.</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Acquire
    the group tag of the matching certificate.</br> If the request portal groug tag is different from
    the group tag of the matching certificate (If matching certificate in Cisco ISE has portal role
    enabled), a self-signed certificate would be generated by acquiring the group tag of the matching
    certificate if the <b>allowPortalTagTransferForSameSubject</b> parameter is true.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>allowSanDnsBadName<sup><font
    color=red>*required</font></sup></td> <td> Allow generation of self-signed certificates with bad
    common name & SAN values such as \"example.org.\",\"invalid.\",\"test.\",\"localhost\" and so
    on.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter <b>allowSanDnsBadName</b> as
    <b>false</b> to avoid generation of certificates with bad Common Name & SAN Values which are not
    secure. </td> <td>\"allowSanDnsBadName\": true</td> </tr> <tr>
    <td>allowSanDnsNonResolvable<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with non resolvable Common Name or SAN Values .</td>
    <td>\"allowSanDnsNonResolvable\": true</td> </tr> </tbody> </table> <br/> <table
    class=\"certTable\"> <thead> <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead>
    <tbody> <tr> <td>Admin</td> <td>False</td> <td>Enabling Admin role for this certificate causes an
    application server restart on the selected node.</td> </tr> <tr> <td>EAP Authentication</td>
    <td>False</td> <td>Only one system certificate can be used for EAP. Assigning EAP to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>RADIUS DTLS</td>
    <td>False</td> <td>Only one system certificate can be used for DTLS. Assigning DTLS to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>SAML</td>
    <td>False</td> <td>SAML cannot be used with other Usage.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.</td> </tr> </tbody> </table>

    Args:
        body (GenerateSelfsignedCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GenerateSelfsignedCertRespPayload]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: GenerateSelfsignedCertRequest,

) -> Response[Union[Any, GenerateSelfsignedCertRespPayload]]:
    r""" Generate self-signed certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate Self-signed Certificate</h3> <p><b>NOTE: </b>The
    certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively. <br> <b>NOTE: </b>Wildcard certificate and SAML certificate can be generated
    only on the primary PAN or a standalone node.<br></p> <br/> <h4>Following parameters are used in the
    POST body</h4> <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Hostname or FQDN of the node in which the certificate
    needs to be created.</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"Self-signed System Certificate\"</td>
    </tr> <tr> <td>subjectCommonName</td> <td> Certificate common name (CN)<br/> <b>NOTE: </b><ul><li>CN
    is Mandatory if SAN not configured.</li><li>>Subject can contain a multi-valued CN. For multi-valued
    RDNs, follow the format \"CN=value1, CN=value2\"</li></ul> </td> <td>\"subjectCommonName\":
    \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td> <td> Certificate organizational unit (OU)<br/>
    <b>NOTE: </b>Subject can contain a multi-valued OU. For multi-valued RDNs, follow the format
    \"OU=value1, OU=value2\" </td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr> <tr>
    <td>subjectOrg</td> <td> Certificate organization (O)<br/> <b>NOTE: </b>Subject can contain multi-
    valued O fields. For multi-valued RDNs, follow the format \"O=value1, O=value2\" </td>
    <td>\"subjectOrg\": \"Cisco\"</td> </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality
    (L)</td> <td>\"subjectCity\": \"San Jose\"</td> </tr> <tr> <td>subjectState</td> <td>Certificate
    state (ST)</td> <td>\"subjectState\": \"California\"</td> </tr> <tr> <td>subjectCountry</td>
    <td>Certificate country (C)</td> <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td>
    <td>Array of SAN (Subject Alternative Name) DNS entries</td> <td>\"sanDNS\":
    [\"ise.example.com\"]</td> </tr> <tr> <td>sanIP</td> <td>Array of SAN IP address entries</td>
    <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr> <td>sanURI</td> <td>Array of SAN URI entries</td>
    <td>\"sanURI\": [\"https://1.1.1.1\"]</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Algorithm to use for certificate public key creation.</td>
    <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>keyLength<sup><font
    color=red>*required</font></sup></td> <td>Bit size of the public key.</td> <td>\"keyLength\":
    \"4096\"</td> </tr> <tr> <td>digestType<sup><font color=red>*required</font></sup></td> <td>Digest
    to sign with.</td> <td>\"digestType\": \"SHA-384\"</td> </tr> <tr> <td>certificatePolicies</td>
    <td>Certificate policy OID or list of OIDs that the certificate should conform to. Use comma or
    space to separate the OIDs. </td> <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr>
    <tr> <td>expirationTTL<sup><font color=red>*required</font></sup></td> <td> Certificate expiration
    value.<br/> <b>NOTE: </b>Expiration TTL should be within Unix time limit </td>
    <td>\"expirationTTL\": 2</td> </tr> <tr> <td>expirationTTLUnit<sup><font
    color=red>*required</font></sup></td> <td>Certificate expiration unit.</td>
    <td>\"expirationTTLUnit\": \"years\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to
    authenticate the Cisco ISE Admin Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td>
    <td>Use certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr>
    <tr> <td>radius</td> <td>Use certificate for RADSec server</td> <td>\"radius\": false</td> </tr>
    <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid controller</td> <td>\"pxgrid\": false</td>
    </tr> <tr> <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr>
    <tr> <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowWildCardCertificates</td> <td>Allow use of WildCards in certificates</td>
    <td>\"allowWildCardCertificates\": false</td> </tr> <tr>
    <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td> <td>Allow
    replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with validity greater than 398 days.</td> <td>\"allowExtendedValidity\":
    true</td> </tr> <tr> <td>allowRoleTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with same
    subject.<br/> If the matching certificate on Cisco ISE has either admin or portal role and if the
    request has admin or portal role selected along with <b>allowRoleTransferForSameSubject</b>
    parameter as true, a self-signed certificate would be generated with both admin and portal role
    enabled.</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Acquire
    the group tag of the matching certificate.</br> If the request portal groug tag is different from
    the group tag of the matching certificate (If matching certificate in Cisco ISE has portal role
    enabled), a self-signed certificate would be generated by acquiring the group tag of the matching
    certificate if the <b>allowPortalTagTransferForSameSubject</b> parameter is true.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>allowSanDnsBadName<sup><font
    color=red>*required</font></sup></td> <td> Allow generation of self-signed certificates with bad
    common name & SAN values such as \"example.org.\",\"invalid.\",\"test.\",\"localhost\" and so
    on.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter <b>allowSanDnsBadName</b> as
    <b>false</b> to avoid generation of certificates with bad Common Name & SAN Values which are not
    secure. </td> <td>\"allowSanDnsBadName\": true</td> </tr> <tr>
    <td>allowSanDnsNonResolvable<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with non resolvable Common Name or SAN Values .</td>
    <td>\"allowSanDnsNonResolvable\": true</td> </tr> </tbody> </table> <br/> <table
    class=\"certTable\"> <thead> <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead>
    <tbody> <tr> <td>Admin</td> <td>False</td> <td>Enabling Admin role for this certificate causes an
    application server restart on the selected node.</td> </tr> <tr> <td>EAP Authentication</td>
    <td>False</td> <td>Only one system certificate can be used for EAP. Assigning EAP to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>RADIUS DTLS</td>
    <td>False</td> <td>Only one system certificate can be used for DTLS. Assigning DTLS to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>SAML</td>
    <td>False</td> <td>SAML cannot be used with other Usage.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.</td> </tr> </tbody> </table>

    Args:
        body (GenerateSelfsignedCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GenerateSelfsignedCertRespPayload]]
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
    body: GenerateSelfsignedCertRequest,

) -> Optional[Union[Any, GenerateSelfsignedCertRespPayload]]:
    r""" Generate self-signed certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Generate Self-signed Certificate</h3> <p><b>NOTE: </b>The
    certificate may have a validity period greater than 398 days. It may be untrusted by many
    browsers.<br> <b>NOTE: </b>Request parameters accepting True and False as input can be replaced by 1
    and 0 respectively. <br> <b>NOTE: </b>Wildcard certificate and SAML certificate can be generated
    only on the primary PAN or a standalone node.<br></p> <br/> <h4>Following parameters are used in the
    POST body</h4> <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Hostname or FQDN of the node in which the certificate
    needs to be created.</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"Self-signed System Certificate\"</td>
    </tr> <tr> <td>subjectCommonName</td> <td> Certificate common name (CN)<br/> <b>NOTE: </b><ul><li>CN
    is Mandatory if SAN not configured.</li><li>>Subject can contain a multi-valued CN. For multi-valued
    RDNs, follow the format \"CN=value1, CN=value2\"</li></ul> </td> <td>\"subjectCommonName\":
    \"$FQDN$\"</td> </tr> <tr> <td>subjectOrgUnit</td> <td> Certificate organizational unit (OU)<br/>
    <b>NOTE: </b>Subject can contain a multi-valued OU. For multi-valued RDNs, follow the format
    \"OU=value1, OU=value2\" </td> <td>\"subjectOrgUnit\": \"Engineering\"</td> </tr> <tr>
    <td>subjectOrg</td> <td> Certificate organization (O)<br/> <b>NOTE: </b>Subject can contain multi-
    valued O fields. For multi-valued RDNs, follow the format \"O=value1, O=value2\" </td>
    <td>\"subjectOrg\": \"Cisco\"</td> </tr> <tr> <td>subjectCity</td> <td>Certificate city or locality
    (L)</td> <td>\"subjectCity\": \"San Jose\"</td> </tr> <tr> <td>subjectState</td> <td>Certificate
    state (ST)</td> <td>\"subjectState\": \"California\"</td> </tr> <tr> <td>subjectCountry</td>
    <td>Certificate country (C)</td> <td>\"subjectCountry\": \"US\"</td> </tr> <tr> <td>sanDNS</td>
    <td>Array of SAN (Subject Alternative Name) DNS entries</td> <td>\"sanDNS\":
    [\"ise.example.com\"]</td> </tr> <tr> <td>sanIP</td> <td>Array of SAN IP address entries</td>
    <td>\"sanIP\": [\"1.1.1.1\"]</td> </tr> <tr> <td>sanURI</td> <td>Array of SAN URI entries</td>
    <td>\"sanURI\": [\"https://1.1.1.1\"]</td> </tr> <tr> <td>keyType<sup><font
    color=red>*required</font></sup></td> <td>Algorithm to use for certificate public key creation.</td>
    <td>\"keyType\": \"RSA\"</td> </tr> <tr> <td>keyLength<sup><font
    color=red>*required</font></sup></td> <td>Bit size of the public key.</td> <td>\"keyLength\":
    \"4096\"</td> </tr> <tr> <td>digestType<sup><font color=red>*required</font></sup></td> <td>Digest
    to sign with.</td> <td>\"digestType\": \"SHA-384\"</td> </tr> <tr> <td>certificatePolicies</td>
    <td>Certificate policy OID or list of OIDs that the certificate should conform to. Use comma or
    space to separate the OIDs. </td> <td>\"certificatePolicies\": \"Certificate Policies\"</td> </tr>
    <tr> <td>expirationTTL<sup><font color=red>*required</font></sup></td> <td> Certificate expiration
    value.<br/> <b>NOTE: </b>Expiration TTL should be within Unix time limit </td>
    <td>\"expirationTTL\": 2</td> </tr> <tr> <td>expirationTTLUnit<sup><font
    color=red>*required</font></sup></td> <td>Certificate expiration unit.</td>
    <td>\"expirationTTLUnit\": \"years\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to
    authenticate the Cisco ISE Admin Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td>
    <td>Use certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr>
    <tr> <td>radius</td> <td>Use certificate for RADSec server</td> <td>\"radius\": false</td> </tr>
    <tr> <td>pxgrid</td> <td>Use certificate for the pxGrid controller</td> <td>\"pxgrid\": false</td>
    </tr> <tr> <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr>
    <tr> <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowWildCardCertificates</td> <td>Allow use of WildCards in certificates</td>
    <td>\"allowWildCardCertificates\": false</td> </tr> <tr>
    <td>allowReplacementOfCertificates<sup><font color=red>*required</font></sup></td> <td>Allow
    replacement of certificates.</td> <td>\"allowReplacementOfCertificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with validity greater than 398 days.</td> <td>\"allowExtendedValidity\":
    true</td> </tr> <tr> <td>allowRoleTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with same
    subject.<br/> If the matching certificate on Cisco ISE has either admin or portal role and if the
    request has admin or portal role selected along with <b>allowRoleTransferForSameSubject</b>
    parameter as true, a self-signed certificate would be generated with both admin and portal role
    enabled.</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Acquire
    the group tag of the matching certificate.</br> If the request portal groug tag is different from
    the group tag of the matching certificate (If matching certificate in Cisco ISE has portal role
    enabled), a self-signed certificate would be generated by acquiring the group tag of the matching
    certificate if the <b>allowPortalTagTransferForSameSubject</b> parameter is true.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>allowSanDnsBadName<sup><font
    color=red>*required</font></sup></td> <td> Allow generation of self-signed certificates with bad
    common name & SAN values such as \"example.org.\",\"invalid.\",\"test.\",\"localhost\" and so
    on.</br> <b>SECURITY ALERT: </b>We recommend to set the parameter <b>allowSanDnsBadName</b> as
    <b>false</b> to avoid generation of certificates with bad Common Name & SAN Values which are not
    secure. </td> <td>\"allowSanDnsBadName\": true</td> </tr> <tr>
    <td>allowSanDnsNonResolvable<sup><font color=red>*required</font></sup></td> <td>Allow generation of
    self-signed certificate with non resolvable Common Name or SAN Values .</td>
    <td>\"allowSanDnsNonResolvable\": true</td> </tr> </tbody> </table> <br/> <table
    class=\"certTable\"> <thead> <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead>
    <tbody> <tr> <td>Admin</td> <td>False</td> <td>Enabling Admin role for this certificate causes an
    application server restart on the selected node.</td> </tr> <tr> <td>EAP Authentication</td>
    <td>False</td> <td>Only one system certificate can be used for EAP. Assigning EAP to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>RADIUS DTLS</td>
    <td>False</td> <td>Only one system certificate can be used for DTLS. Assigning DTLS to this
    certificate removes the assignment from another certificate.</td> </tr> <tr> <td>SAML</td>
    <td>False</td> <td>SAML cannot be used with other Usage.</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.</td> </tr> </tbody> </table>

    Args:
        body (GenerateSelfsignedCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GenerateSelfsignedCertRespPayload]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
