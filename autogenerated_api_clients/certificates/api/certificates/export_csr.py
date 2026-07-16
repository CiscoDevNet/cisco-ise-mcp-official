# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.export_csr_fail_resp_payload import ExportCSRFailRespPayload
from ...types import File, FileTypes
from io import BytesIO
from typing import cast



def _get_kwargs(
    hostname: str,
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/certs/certificate-signing-request/export/{hostname}/{id}".format(hostname=hostname,id=id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ExportCSRFailRespPayload, File]]:
    if response.status_code == 200:
        response_200 = File(
             payload = BytesIO(response.content)
        )



        return response_200
    if response.status_code == 400:
        response_400 = ExportCSRFailRespPayload.from_dict(response.content)



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ExportCSRFailRespPayload, File]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    hostname: str,
    id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, ExportCSRFailRespPayload, File]]:
    """ Export a CSR for a given CSR ID and hostname

     Response of this API carries a CSR corresponding to the requested ID.

    Args:
        hostname (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ExportCSRFailRespPayload, File]]
     """


    kwargs = _get_kwargs(
        hostname=hostname,
id=id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    hostname: str,
    id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, ExportCSRFailRespPayload, File]]:
    """ Export a CSR for a given CSR ID and hostname

     Response of this API carries a CSR corresponding to the requested ID.

    Args:
        hostname (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ExportCSRFailRespPayload, File]
     """


    return sync_detailed(
        hostname=hostname,
id=id,
client=client,

    ).parsed

async def asyncio_detailed(
    hostname: str,
    id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, ExportCSRFailRespPayload, File]]:
    """ Export a CSR for a given CSR ID and hostname

     Response of this API carries a CSR corresponding to the requested ID.

    Args:
        hostname (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ExportCSRFailRespPayload, File]]
     """


    kwargs = _get_kwargs(
        hostname=hostname,
id=id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    hostname: str,
    id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, ExportCSRFailRespPayload, File]]:
    """ Export a CSR for a given CSR ID and hostname

     Response of this API carries a CSR corresponding to the requested ID.

    Args:
        hostname (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ExportCSRFailRespPayload, File]
     """


    return (await asyncio_detailed(
        hostname=hostname,
id=id,
client=client,

    )).parsed
