from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.update_system_cert_request import UpdateSystemCertRequest
from ...models.update_system_cert_resp_payload import UpdateSystemCertRespPayload
from typing import cast



def _get_kwargs(
    host_name: str,
    id: str,
    *,
    body: UpdateSystemCertRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/certs/system-certificate/{host_name}/{id}".format(host_name=host_name,id=id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, UpdateSystemCertRespPayload]]:
    if response.status_code == 200:
        response_200 = UpdateSystemCertRespPayload.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, UpdateSystemCertRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateSystemCertRequest,

) -> Response[Union[Any, Error, UpdateSystemCertRespPayload]]:
    r""" Update data for existing system certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a System Certificate.</h3> <b>NOTE: </b>Renewing a
    certificate causes an application server restart on the selected node.<br> <b>NOTE: </b>Request
    parameters accepting True and False as input can be replaced by 1 and 0 respectively.<br>
    <h4>Following parameters are used in the POST body</h4> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"System Certificate\"</td> </tr> <tr>
    <td>description</td> <td>Description of the certificate</td> <td>\"description\": \"Description of
    certificate\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin
    Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols
    that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use
    certificate for RADSec server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use
    certificate for the pxGrid Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td>
    <td>Use certificate for the Cisco ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr>
    <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr> <tr>
    <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Allow
    transfer of roles to certificates with same subject.</td> <td>\"allowRoleTransferForSameSubject\":
    true</td> </tr> <tr> <td>allowPortalTagTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Acquire group tag of the matching certificate.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr>
    <td>renewSelfSignedCertificate</td> <td>Renew Self-signed Certificate</td>
    <td>\"renewSelfSignedCertificate\": false</td> </tr> <tr> <td>expirationTTLPeriod</td>
    <td>Expiration Period</td> <td>\"expirationTTLPeriod\": 365</td> </tr> <tr>
    <td>expirationTTLUnits</td> <td>Expiration Units in one of the below formats <ul> <li>days / weeks /
    months / years</li> </ul> </td> <td>\"expirationTTLUnits\": \"days\"</td> </tr> </tbody> </table>
    <br/> <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead>
    <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling Admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other usage. Enabling SAML unchecks all other usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        host_name (str):
        id (str):
        body (UpdateSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, UpdateSystemCertRespPayload]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
id=id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateSystemCertRequest,

) -> Optional[Union[Any, Error, UpdateSystemCertRespPayload]]:
    r""" Update data for existing system certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a System Certificate.</h3> <b>NOTE: </b>Renewing a
    certificate causes an application server restart on the selected node.<br> <b>NOTE: </b>Request
    parameters accepting True and False as input can be replaced by 1 and 0 respectively.<br>
    <h4>Following parameters are used in the POST body</h4> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"System Certificate\"</td> </tr> <tr>
    <td>description</td> <td>Description of the certificate</td> <td>\"description\": \"Description of
    certificate\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin
    Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols
    that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use
    certificate for RADSec server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use
    certificate for the pxGrid Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td>
    <td>Use certificate for the Cisco ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr>
    <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr> <tr>
    <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Allow
    transfer of roles to certificates with same subject.</td> <td>\"allowRoleTransferForSameSubject\":
    true</td> </tr> <tr> <td>allowPortalTagTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Acquire group tag of the matching certificate.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr>
    <td>renewSelfSignedCertificate</td> <td>Renew Self-signed Certificate</td>
    <td>\"renewSelfSignedCertificate\": false</td> </tr> <tr> <td>expirationTTLPeriod</td>
    <td>Expiration Period</td> <td>\"expirationTTLPeriod\": 365</td> </tr> <tr>
    <td>expirationTTLUnits</td> <td>Expiration Units in one of the below formats <ul> <li>days / weeks /
    months / years</li> </ul> </td> <td>\"expirationTTLUnits\": \"days\"</td> </tr> </tbody> </table>
    <br/> <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead>
    <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling Admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other usage. Enabling SAML unchecks all other usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        host_name (str):
        id (str):
        body (UpdateSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, UpdateSystemCertRespPayload]
     """


    return sync_detailed(
        host_name=host_name,
id=id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateSystemCertRequest,

) -> Response[Union[Any, Error, UpdateSystemCertRespPayload]]:
    r""" Update data for existing system certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a System Certificate.</h3> <b>NOTE: </b>Renewing a
    certificate causes an application server restart on the selected node.<br> <b>NOTE: </b>Request
    parameters accepting True and False as input can be replaced by 1 and 0 respectively.<br>
    <h4>Following parameters are used in the POST body</h4> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"System Certificate\"</td> </tr> <tr>
    <td>description</td> <td>Description of the certificate</td> <td>\"description\": \"Description of
    certificate\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin
    Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols
    that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use
    certificate for RADSec server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use
    certificate for the pxGrid Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td>
    <td>Use certificate for the Cisco ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr>
    <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr> <tr>
    <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Allow
    transfer of roles to certificates with same subject.</td> <td>\"allowRoleTransferForSameSubject\":
    true</td> </tr> <tr> <td>allowPortalTagTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Acquire group tag of the matching certificate.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr>
    <td>renewSelfSignedCertificate</td> <td>Renew Self-signed Certificate</td>
    <td>\"renewSelfSignedCertificate\": false</td> </tr> <tr> <td>expirationTTLPeriod</td>
    <td>Expiration Period</td> <td>\"expirationTTLPeriod\": 365</td> </tr> <tr>
    <td>expirationTTLUnits</td> <td>Expiration Units in one of the below formats <ul> <li>days / weeks /
    months / years</li> </ul> </td> <td>\"expirationTTLUnits\": \"days\"</td> </tr> </tbody> </table>
    <br/> <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead>
    <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling Admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other usage. Enabling SAML unchecks all other usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        host_name (str):
        id (str):
        body (UpdateSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, UpdateSystemCertRespPayload]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
id=id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateSystemCertRequest,

) -> Optional[Union[Any, Error, UpdateSystemCertRespPayload]]:
    r""" Update data for existing system certificate

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Update a System Certificate.</h3> <b>NOTE: </b>Renewing a
    certificate causes an application server restart on the selected node.<br> <b>NOTE: </b>Request
    parameters accepting True and False as input can be replaced by 1 and 0 respectively.<br>
    <h4>Following parameters are used in the POST body</h4> <table class=\"certTable\"> <thead> <tr>
    <th>PARAMETER</th> <th>DESCRIPTION</th> <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>name</td>
    <td>Friendly name of the certificate.</td> <td>\"name\": \"System Certificate\"</td> </tr> <tr>
    <td>description</td> <td>Description of the certificate</td> <td>\"description\": \"Description of
    certificate\"</td> </tr> <tr> <td>admin</td> <td>Use certificate to authenticate the Cisco ISE Admin
    Portal</td> <td>\"admin\": false</td> </tr> <tr> <td>eap</td> <td>Use certificate for EAP protocols
    that use SSL/TLS tunneling</td> <td>\"eap\": false</td> </tr> <tr> <td>radius</td> <td>Use
    certificate for RADSec server</td> <td>\"radius\": false</td> </tr> <tr> <td>pxgrid</td> <td>Use
    certificate for the pxGrid Controller</td> <td>\"pxgrid\": false</td> </tr> <tr> <td>ims</td>
    <td>Use certificate for the Cisco ISE Messaging Service</td> <td>\"ims\": false</td> </tr> <tr>
    <td>saml</td> <td>Use certificate for SAML Signing</td> <td>\"saml\": false</td> </tr> <tr>
    <td>portal</td> <td>Use certificate for portal</td> <td>\"portal\": false</td> </tr> <tr>
    <td>tacacs</td> <td>Use certificate for TACACS server</td> <td>\"tacacs\": false</td> </tr> <tr>
    <td>portalGroupTag</td> <td>Portal Group Tag for using certificate with portal role</td>
    <td>\"portalGroupTag\": \"Default Portal Certificate Group\"</td> </tr> <tr>
    <td>allowReplacementOfPortalGroupTag<sup><font color=red>*required</font></sup></td> <td>Allow
    Replacement of Portal Group Tag.</td> <td>\"allowReplacementOfPortalGroupTag\": true</td> </tr> <tr>
    <td>allowRoleTransferForSameSubject<sup><font color=red>*required</font></sup></td> <td>Allow
    transfer of roles to certificates with same subject.</td> <td>\"allowRoleTransferForSameSubject\":
    true</td> </tr> <tr> <td>allowPortalTagTransferForSameSubject<sup><font
    color=red>*required</font></sup></td> <td>Acquire group tag of the matching certificate.</td>
    <td>\"allowPortalTagTransferForSameSubject\": true</td> </tr> <tr>
    <td>renewSelfSignedCertificate</td> <td>Renew Self-signed Certificate</td>
    <td>\"renewSelfSignedCertificate\": false</td> </tr> <tr> <td>expirationTTLPeriod</td>
    <td>Expiration Period</td> <td>\"expirationTTLPeriod\": 365</td> </tr> <tr>
    <td>expirationTTLUnits</td> <td>Expiration Units in one of the below formats <ul> <li>days / weeks /
    months / years</li> </ul> </td> <td>\"expirationTTLUnits\": \"days\"</td> </tr> </tbody> </table>
    <br/> <h4>Following roles can be used in any combinations</h4> <table class=\"certTable\"> <thead>
    <tr> <th>ROLE</th> <th>DEFAULT</th> <th>WARNING</th> </tr> </thead> <tbody> <tr> <td>Admin</td>
    <td>False</td> <td>Enabling Admin role for this certificate causes an application server restart on
    the selected node.<br/><b>Note:</b> Make sure that the required certificate chain is imported under
    Trusted Certificates</td> </tr> <tr> <td>EAP Authentication</td> <td>False</td> <td>Only one system
    certificate can be used for EAP. Assigning EAP to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>RADIUS DTLS</td> <td>False</td> <td>Only one system
    certificate can be used for DTLS. Assigning DTLS to this certificate removes the assignment from
    another certificate.<br/><b>Note:</b> Make sure that the required certificate chain is imported
    under Trusted Certificates</td> </tr> <tr> <td>SAML</td> <td>False</td> <td>SAML cannot be used with
    other usage. Enabling SAML unchecks all other usage.</br><b>Note:</b> Make sure that the required
    certificate chain is imported under Trusted Certificates</td> </tr> <tr> <td>TACACS</td>
    <td>False</td> <td>Only one system certificate can be used for TACACS. Assigning TACACS to this
    certificate removes the assignment from another certificate.<br/><b>Note:</b> Make sure that the
    required certificate chain is imported under Trusted Certificates</td> </tr> </tbody> </table>

    Args:
        host_name (str):
        id (str):
        body (UpdateSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, UpdateSystemCertRespPayload]
     """


    return (await asyncio_detailed(
        host_name=host_name,
id=id,
client=client,
body=body,

    )).parsed
