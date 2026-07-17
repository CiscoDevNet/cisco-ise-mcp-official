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
from ...models.export_cert_request import ExportCertRequest
from ...models.resource import Resource
from typing import cast



def _get_kwargs(
    *,
    body: ExportCertRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/system-certificate/export",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, Resource]]:
    if response.status_code == 200:
        response_200 = Resource.from_dict(response.content)



        return response_200
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201
    if response.status_code == 400:
        response_400 = Error.from_dict(response.content)



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
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, Resource]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ExportCertRequest,

) -> Response[Union[Any, Error, Resource]]:
    r""" Export a system certificate with a given a certificate ID

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Export System Certificate.</h3> Following parameters are used in the
    POST body <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>id<sup><font color=red>*required</font></sup></td>
    <td>ID of a System Certificate.</td> <td>\"id\": \"CERT-ID\"</td> </tr> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Name of the host for which the system certificate should
    be exported</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>export</td> <td> One of the
    following options is required: <ul> <li><b>\"CERTIFICATE\" :</b>Export only certificate without
    private key<br/></li> <li><b>\"CERTIFICATE_WITH_PRIVATE_KEY\" :</b>Export both certificate and
    private key (<b>\"certificatePassword\"</b> is required).</li> </ul> </td> <td>\"export\":
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</td> </tr> <tr> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Certificate password (required if <b>\"export\" :
    CERTIFICATE_WITH_PRIVATE_KEY</b>).</br> <b>Password constraints:</b> <ul> <li>Alphanumeric</li>
    <li>Minimum of 8 Characters</li> <li>Maximum of 100 Characters</li> </ul> </td> <td>\"password\":
    \"certificate password\"</td> </tr> </tbody> </table> <b>NOTE: </b>The response of this API carries
    a ZIP file containing the certificate and private key if  the request contains <b>\"export\" :
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</b>. If the request body contains <b>\"export\" :
    \"CERTIFICATE\"</b>, the response carries a ZIP file containing only the certificate. <br/><br/>
    <b>WARNING: </b>Exporting a private key is not a secure operation. It could lead to possible
    exposure of the private key. <br/>

    Args:
        body (ExportCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, Resource]]
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
    body: ExportCertRequest,

) -> Optional[Union[Any, Error, Resource]]:
    r""" Export a system certificate with a given a certificate ID

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Export System Certificate.</h3> Following parameters are used in the
    POST body <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>id<sup><font color=red>*required</font></sup></td>
    <td>ID of a System Certificate.</td> <td>\"id\": \"CERT-ID\"</td> </tr> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Name of the host for which the system certificate should
    be exported</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>export</td> <td> One of the
    following options is required: <ul> <li><b>\"CERTIFICATE\" :</b>Export only certificate without
    private key<br/></li> <li><b>\"CERTIFICATE_WITH_PRIVATE_KEY\" :</b>Export both certificate and
    private key (<b>\"certificatePassword\"</b> is required).</li> </ul> </td> <td>\"export\":
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</td> </tr> <tr> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Certificate password (required if <b>\"export\" :
    CERTIFICATE_WITH_PRIVATE_KEY</b>).</br> <b>Password constraints:</b> <ul> <li>Alphanumeric</li>
    <li>Minimum of 8 Characters</li> <li>Maximum of 100 Characters</li> </ul> </td> <td>\"password\":
    \"certificate password\"</td> </tr> </tbody> </table> <b>NOTE: </b>The response of this API carries
    a ZIP file containing the certificate and private key if  the request contains <b>\"export\" :
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</b>. If the request body contains <b>\"export\" :
    \"CERTIFICATE\"</b>, the response carries a ZIP file containing only the certificate. <br/><br/>
    <b>WARNING: </b>Exporting a private key is not a secure operation. It could lead to possible
    exposure of the private key. <br/>

    Args:
        body (ExportCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, Resource]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ExportCertRequest,

) -> Response[Union[Any, Error, Resource]]:
    r""" Export a system certificate with a given a certificate ID

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Export System Certificate.</h3> Following parameters are used in the
    POST body <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>id<sup><font color=red>*required</font></sup></td>
    <td>ID of a System Certificate.</td> <td>\"id\": \"CERT-ID\"</td> </tr> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Name of the host for which the system certificate should
    be exported</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>export</td> <td> One of the
    following options is required: <ul> <li><b>\"CERTIFICATE\" :</b>Export only certificate without
    private key<br/></li> <li><b>\"CERTIFICATE_WITH_PRIVATE_KEY\" :</b>Export both certificate and
    private key (<b>\"certificatePassword\"</b> is required).</li> </ul> </td> <td>\"export\":
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</td> </tr> <tr> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Certificate password (required if <b>\"export\" :
    CERTIFICATE_WITH_PRIVATE_KEY</b>).</br> <b>Password constraints:</b> <ul> <li>Alphanumeric</li>
    <li>Minimum of 8 Characters</li> <li>Maximum of 100 Characters</li> </ul> </td> <td>\"password\":
    \"certificate password\"</td> </tr> </tbody> </table> <b>NOTE: </b>The response of this API carries
    a ZIP file containing the certificate and private key if  the request contains <b>\"export\" :
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</b>. If the request body contains <b>\"export\" :
    \"CERTIFICATE\"</b>, the response carries a ZIP file containing only the certificate. <br/><br/>
    <b>WARNING: </b>Exporting a private key is not a secure operation. It could lead to possible
    exposure of the private key. <br/>

    Args:
        body (ExportCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, Resource]]
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
    body: ExportCertRequest,

) -> Optional[Union[Any, Error, Resource]]:
    r""" Export a system certificate with a given a certificate ID

      <style type=\"text/css\" scoped> .certTable td , .certTable th { padding: 5px 10px !important;
    text-align: left;} </style> <h3>Export System Certificate.</h3> Following parameters are used in the
    POST body <table class=\"certTable\"> <thead> <tr> <th>PARAMETER</th> <th>DESCRIPTION</th>
    <th>EXAMPLE</th> </tr> </thead> <tbody> <tr> <td>id<sup><font color=red>*required</font></sup></td>
    <td>ID of a System Certificate.</td> <td>\"id\": \"CERT-ID\"</td> </tr> <tr> <td>hostName<sup><font
    color=red>*required</font></sup></td> <td>Name of the host for which the system certificate should
    be exported</td> <td>\"hostName\": \"ise-node-001\"</td> </tr> <tr> <td>export</td> <td> One of the
    following options is required: <ul> <li><b>\"CERTIFICATE\" :</b>Export only certificate without
    private key<br/></li> <li><b>\"CERTIFICATE_WITH_PRIVATE_KEY\" :</b>Export both certificate and
    private key (<b>\"certificatePassword\"</b> is required).</li> </ul> </td> <td>\"export\":
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</td> </tr> <tr> <td>password<sup><font
    color=red>*required</font></sup></td> <td>Certificate password (required if <b>\"export\" :
    CERTIFICATE_WITH_PRIVATE_KEY</b>).</br> <b>Password constraints:</b> <ul> <li>Alphanumeric</li>
    <li>Minimum of 8 Characters</li> <li>Maximum of 100 Characters</li> </ul> </td> <td>\"password\":
    \"certificate password\"</td> </tr> </tbody> </table> <b>NOTE: </b>The response of this API carries
    a ZIP file containing the certificate and private key if  the request contains <b>\"export\" :
    \"CERTIFICATE_WITH_PRIVATE_KEY\"</b>. If the request body contains <b>\"export\" :
    \"CERTIFICATE\"</b>, the response carries a ZIP file containing only the certificate. <br/><br/>
    <b>WARNING: </b>Exporting a private key is not a secure operation. It could lead to possible
    exposure of the private key. <br/>

    Args:
        body (ExportCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, Resource]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
