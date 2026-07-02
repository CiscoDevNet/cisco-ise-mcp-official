from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.import_system_cert_resp_payload import ImportSystemCertRespPayload
from ...models.system_cert import SystemCert
from typing import cast



def _get_kwargs(
    *,
    body: SystemCert,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/system-certificate/import",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, ImportSystemCertRespPayload]]:
    if response.status_code == 200:
        response_200 = ImportSystemCertRespPayload.from_dict(response.json())



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
    if response.status_code == 406:
        response_406 = Error.from_dict(response.json())



        return response_406
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, ImportSystemCertRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SystemCert,

) -> Response[Union[Any, Error, ImportSystemCertRespPayload]]:
    r""" Import system certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a system certificate.</h3> <b>NOTE:
    </b><br/> <ul> <li>This API is used to import a certificate on a specific node mentioned in the
    server section of the URL. To import a certificate on a secondary node, execute this RESTApi
    directly on a secondary node by specifying the server name of the secondary node in the URL<br/>
    Example: \"&lt;https://secondary-ise-node&gt;/api/v1/certs/system-certificate/import\"</li> <li>The
    certificate may have a validity period of more than 398 days. It may be untrusted by many
    browsers.</li> <li>Request parameters accepting True and False as input can be replaced by 1 and 0
    respectively.</li> </ul> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\":
    \"System certificate\"</td> </tr> <tr> <td>password<sup><font color=red>*required</font></sup></td>
    <td>Password of the certificate to be imported.</td> <td>\"password\": \"certificate password\"</td>
    </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td> Plain-text contents of the
    certificate file. Every space needs to be replaced with a newline escape sequence (\n).<br/> Use the
    command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem
    file&gt;&gt;</cmd> to extract data from the certificate file. </td> <td>\"data\": \"Plain-text
    contents of the certificate file.\"</td> </tr> <tr> <td>privateKeyData<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the private key file. Every space
    needs to be replaced with a newline escape sequence (\n).</br> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract
    privateKeyData from private key file. </td> <td>\"data\": \"Plain-text contents of the private key
    file.\"</td> </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td>
    Allow out of date certificates .</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not Secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses the
    SHA-1 hashing algorithm and is considered less secure .</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1certificates</b>as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1certificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow the certificates
    greater than validity of 398 days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with the same
    subject</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Acquire the group tag of the matching certificate</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>admin</td> <td>Use the
    certificate to authenticate the Cisco ISE admin portal</td> <td>\"admin\": false</td> </tr> <tr>
    <td>eap</td> <td>Use the certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\":
    false</td> </tr> <tr> <td>radius</td> <td>Use the certificate for RADSec server</td> <td>\"radius\":
    false</td> </tr> <tr> <td>pxgrid</td> <td>Use the certificate for the pxGrid Controller</td>
    <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use the certificate for the Cisco ISE
    messaging service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use the certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use the certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use the certificate for TACACS
    Server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal certificate
    Group\"</td> </tr> <tr> <td>allowReplacementOfPortalGroupTag<sup><font
    color=red>*required</font></sup></td> <td>Allow Replacement of Portal Group Tag .</td>
    <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr> <td>allowWildCardcertificates</td>
    <td>Allow use of wildcards in certificates</td> <td>\"allowWildCardcertificates\": false</td> </tr>
    <tr> <td>validatecertificateExtensions</td> <td>Validate certificate extensions</td>
    <td>\"validatecertificateExtensions\": false</td> </tr> </tbody> </table> <br/> <h4>Following roles
    can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr> <th>ROLE</th>
    <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td> <td>False</td>
    <td>Enabling Admin role for this certificate causes an application server restart on the selected
    node.<br/><b>Note:</b> Make sure the required certificate chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system certificate can
    be used for DTLS. Assigning DTLS to this certificate removes the assignment from another
    certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with other Usage.
    Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure the required certificate chain is
    imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td> <td>False</td> <td>Only one
    system certificate can be used for TACACS. Assigning TACACS to this certificate removes the
    assignment from another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is
    imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (SystemCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, ImportSystemCertRespPayload]]
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
    body: SystemCert,

) -> Optional[Union[Any, Error, ImportSystemCertRespPayload]]:
    r""" Import system certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a system certificate.</h3> <b>NOTE:
    </b><br/> <ul> <li>This API is used to import a certificate on a specific node mentioned in the
    server section of the URL. To import a certificate on a secondary node, execute this RESTApi
    directly on a secondary node by specifying the server name of the secondary node in the URL<br/>
    Example: \"&lt;https://secondary-ise-node&gt;/api/v1/certs/system-certificate/import\"</li> <li>The
    certificate may have a validity period of more than 398 days. It may be untrusted by many
    browsers.</li> <li>Request parameters accepting True and False as input can be replaced by 1 and 0
    respectively.</li> </ul> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\":
    \"System certificate\"</td> </tr> <tr> <td>password<sup><font color=red>*required</font></sup></td>
    <td>Password of the certificate to be imported.</td> <td>\"password\": \"certificate password\"</td>
    </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td> Plain-text contents of the
    certificate file. Every space needs to be replaced with a newline escape sequence (\n).<br/> Use the
    command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem
    file&gt;&gt;</cmd> to extract data from the certificate file. </td> <td>\"data\": \"Plain-text
    contents of the certificate file.\"</td> </tr> <tr> <td>privateKeyData<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the private key file. Every space
    needs to be replaced with a newline escape sequence (\n).</br> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract
    privateKeyData from private key file. </td> <td>\"data\": \"Plain-text contents of the private key
    file.\"</td> </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td>
    Allow out of date certificates .</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not Secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses the
    SHA-1 hashing algorithm and is considered less secure .</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1certificates</b>as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1certificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow the certificates
    greater than validity of 398 days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with the same
    subject</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Acquire the group tag of the matching certificate</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>admin</td> <td>Use the
    certificate to authenticate the Cisco ISE admin portal</td> <td>\"admin\": false</td> </tr> <tr>
    <td>eap</td> <td>Use the certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\":
    false</td> </tr> <tr> <td>radius</td> <td>Use the certificate for RADSec server</td> <td>\"radius\":
    false</td> </tr> <tr> <td>pxgrid</td> <td>Use the certificate for the pxGrid Controller</td>
    <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use the certificate for the Cisco ISE
    messaging service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use the certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use the certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use the certificate for TACACS
    Server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal certificate
    Group\"</td> </tr> <tr> <td>allowReplacementOfPortalGroupTag<sup><font
    color=red>*required</font></sup></td> <td>Allow Replacement of Portal Group Tag .</td>
    <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr> <td>allowWildCardcertificates</td>
    <td>Allow use of wildcards in certificates</td> <td>\"allowWildCardcertificates\": false</td> </tr>
    <tr> <td>validatecertificateExtensions</td> <td>Validate certificate extensions</td>
    <td>\"validatecertificateExtensions\": false</td> </tr> </tbody> </table> <br/> <h4>Following roles
    can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr> <th>ROLE</th>
    <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td> <td>False</td>
    <td>Enabling Admin role for this certificate causes an application server restart on the selected
    node.<br/><b>Note:</b> Make sure the required certificate chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system certificate can
    be used for DTLS. Assigning DTLS to this certificate removes the assignment from another
    certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with other Usage.
    Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure the required certificate chain is
    imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td> <td>False</td> <td>Only one
    system certificate can be used for TACACS. Assigning TACACS to this certificate removes the
    assignment from another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is
    imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (SystemCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, ImportSystemCertRespPayload]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SystemCert,

) -> Response[Union[Any, Error, ImportSystemCertRespPayload]]:
    r""" Import system certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a system certificate.</h3> <b>NOTE:
    </b><br/> <ul> <li>This API is used to import a certificate on a specific node mentioned in the
    server section of the URL. To import a certificate on a secondary node, execute this RESTApi
    directly on a secondary node by specifying the server name of the secondary node in the URL<br/>
    Example: \"&lt;https://secondary-ise-node&gt;/api/v1/certs/system-certificate/import\"</li> <li>The
    certificate may have a validity period of more than 398 days. It may be untrusted by many
    browsers.</li> <li>Request parameters accepting True and False as input can be replaced by 1 and 0
    respectively.</li> </ul> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\":
    \"System certificate\"</td> </tr> <tr> <td>password<sup><font color=red>*required</font></sup></td>
    <td>Password of the certificate to be imported.</td> <td>\"password\": \"certificate password\"</td>
    </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td> Plain-text contents of the
    certificate file. Every space needs to be replaced with a newline escape sequence (\n).<br/> Use the
    command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem
    file&gt;&gt;</cmd> to extract data from the certificate file. </td> <td>\"data\": \"Plain-text
    contents of the certificate file.\"</td> </tr> <tr> <td>privateKeyData<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the private key file. Every space
    needs to be replaced with a newline escape sequence (\n).</br> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract
    privateKeyData from private key file. </td> <td>\"data\": \"Plain-text contents of the private key
    file.\"</td> </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td>
    Allow out of date certificates .</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not Secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses the
    SHA-1 hashing algorithm and is considered less secure .</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1certificates</b>as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1certificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow the certificates
    greater than validity of 398 days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with the same
    subject</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Acquire the group tag of the matching certificate</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>admin</td> <td>Use the
    certificate to authenticate the Cisco ISE admin portal</td> <td>\"admin\": false</td> </tr> <tr>
    <td>eap</td> <td>Use the certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\":
    false</td> </tr> <tr> <td>radius</td> <td>Use the certificate for RADSec server</td> <td>\"radius\":
    false</td> </tr> <tr> <td>pxgrid</td> <td>Use the certificate for the pxGrid Controller</td>
    <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use the certificate for the Cisco ISE
    messaging service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use the certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use the certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use the certificate for TACACS
    Server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal certificate
    Group\"</td> </tr> <tr> <td>allowReplacementOfPortalGroupTag<sup><font
    color=red>*required</font></sup></td> <td>Allow Replacement of Portal Group Tag .</td>
    <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr> <td>allowWildCardcertificates</td>
    <td>Allow use of wildcards in certificates</td> <td>\"allowWildCardcertificates\": false</td> </tr>
    <tr> <td>validatecertificateExtensions</td> <td>Validate certificate extensions</td>
    <td>\"validatecertificateExtensions\": false</td> </tr> </tbody> </table> <br/> <h4>Following roles
    can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr> <th>ROLE</th>
    <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td> <td>False</td>
    <td>Enabling Admin role for this certificate causes an application server restart on the selected
    node.<br/><b>Note:</b> Make sure the required certificate chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system certificate can
    be used for DTLS. Assigning DTLS to this certificate removes the assignment from another
    certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with other Usage.
    Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure the required certificate chain is
    imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td> <td>False</td> <td>Only one
    system certificate can be used for TACACS. Assigning TACACS to this certificate removes the
    assignment from another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is
    imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (SystemCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, ImportSystemCertRespPayload]]
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
    body: SystemCert,

) -> Optional[Union[Any, Error, ImportSystemCertRespPayload]]:
    r""" Import system certificate in Cisco ISE

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Import an X509 certificate as a system certificate.</h3> <b>NOTE:
    </b><br/> <ul> <li>This API is used to import a certificate on a specific node mentioned in the
    server section of the URL. To import a certificate on a secondary node, execute this RESTApi
    directly on a secondary node by specifying the server name of the secondary node in the URL<br/>
    Example: \"&lt;https://secondary-ise-node&gt;/api/v1/certs/system-certificate/import\"</li> <li>The
    certificate may have a validity period of more than 398 days. It may be untrusted by many
    browsers.</li> <li>Request parameters accepting True and False as input can be replaced by 1 and 0
    respectively.</li> </ul> <h4>Following parameters are used in the POST body</h4> <table
    class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr>
    </thead> <tbody> <tr> <td>name</td> <td>Friendly name of the certificate.</td> <td>\"name\":
    \"System certificate\"</td> </tr> <tr> <td>password<sup><font color=red>*required</font></sup></td>
    <td>Password of the certificate to be imported.</td> <td>\"password\": \"certificate password\"</td>
    </tr> <tr> <td>data<sup><font color=red>*required</font></sup></td> <td> Plain-text contents of the
    certificate file. Every space needs to be replaced with a newline escape sequence (\n).<br/> Use the
    command <cmd>awk &apos;NF {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem
    file&gt;&gt;</cmd> to extract data from the certificate file. </td> <td>\"data\": \"Plain-text
    contents of the certificate file.\"</td> </tr> <tr> <td>privateKeyData<sup><font
    color=red>*required</font></sup></td> <td> Plain-text contents of the private key file. Every space
    needs to be replaced with a newline escape sequence (\n).</br> Use the command <cmd>awk &apos;NF
    {sub(/\r/, \"\"); printf \"%s\\n\",$0;}&apos; &lt;&lt;your .pem file&gt;&gt;</cmd> to extract
    privateKeyData from private key file. </td> <td>\"data\": \"Plain-text contents of the private key
    file.\"</td> </tr> <tr> <td>allowOutOfDateCert<sup><font color=red>*required</font></sup></td> <td>
    Allow out of date certificates .</br> <b>SECURITY ALERT: </b>We recommend to set the parameter
    <b>allowOutOfDateCert</b> as <b>false</b> to avoid the import of expired certificates (not Secure).
    </td> <td>\"allowOutOfDateCert\": true</td> </tr> <tr> <td>allowSHA1certificates<sup><font
    color=red>*required</font></sup></td> <td> Allow import of certificate with signature that uses the
    SHA-1 hashing algorithm and is considered less secure .</br> <b>SECURITY ALERT: </b>We recommend to
    set the parameter <b>allowSHA1certificates</b>as <b>false</b> to avoid the import of SHA1 based
    certificates (less secure). </td> <td>\"allowSHA1certificates\": true</td> </tr> <tr>
    <td>allowExtendedValidity<sup><font color=red>*required</font></sup></td> <td>Allow the certificates
    greater than validity of 398 days.</td> <td>\"allowExtendedValidity\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Allow the transfer of roles to certificates with the same
    subject</td> <td>\"allowRoleTransferForSameSubject\": true</td> </tr> <tr>
    <td>allowPortalTagTransferForSameSubject</td> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Acquire the group tag of the matching certificate</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr> <td>admin</td> <td>Use the
    certificate to authenticate the Cisco ISE admin portal</td> <td>\"admin\": false</td> </tr> <tr>
    <td>eap</td> <td>Use the certificate for EAP protocols that use SSL/TLS tunneling</td> <td>\"eap\":
    false</td> </tr> <tr> <td>radius</td> <td>Use the certificate for RADSec server</td> <td>\"radius\":
    false</td> </tr> <tr> <td>pxgrid</td> <td>Use the certificate for the pxGrid Controller</td>
    <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td> <td>Use the certificate for the Cisco ISE
    messaging service</td> <td>\"ims\": false</td> </tr> <tr> <td>saml</td> <td>Use the certificate for
    SAML Signing</td> <td>\"saml\": false</td> </tr> <tr> <td>portal</td> <td>Use the certificate for
    portal</td> <td>\"portal\": false</td> </tr> <tr> <td>tacacs</td> <td>Use the certificate for TACACS
    Server</td> <td>\"tacacs\": false</td> </tr> <tr> <td>portalGroupTag</td> <td>Portal Group Tag for
    using certificate with portal role</td> <td>\"portalGroupTag\": \"Default Portal certificate
    Group\"</td> </tr> <tr> <td>allowReplacementOfPortalGroupTag<sup><font
    color=red>*required</font></sup></td> <td>Allow Replacement of Portal Group Tag .</td>
    <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr> <td>allowWildCardcertificates</td>
    <td>Allow use of wildcards in certificates</td> <td>\"allowWildCardcertificates\": false</td> </tr>
    <tr> <td>validatecertificateExtensions</td> <td>Validate certificate extensions</td>
    <td>\"validatecertificateExtensions\": false</td> </tr> </tbody> </table> <br/> <h4>Following roles
    can be used in any combinations</h4> <table class=\"certTable\"> <thead> <tr> <th>ROLE</th>
    <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td> <td>False</td>
    <td>Enabling Admin role for this certificate causes an application server restart on the selected
    node.<br/><b>Note:</b> Make sure the required certificate chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system certificate can
    be used for DTLS. Assigning DTLS to this certificate removes the assignment from another
    certificate.<br/><b>Note:</b> Make sure required Certificate Chain is imported under Trusted
    Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with other Usage.
    Enabling SAML unchecks all other Usage.</br><b>Note:</b> Make sure the required certificate chain is
    imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td> <td>False</td> <td>Only one
    system certificate can be used for TACACS. Assigning TACACS to this certificate removes the
    assignment from another certificate.<br/><b>Note:</b> Make sure required Certificate Chain is
    imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        body (SystemCert):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, ImportSystemCertRespPayload]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
