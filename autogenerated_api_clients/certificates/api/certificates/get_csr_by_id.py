# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.csr_get_by_id_rsp import CSRGetByIdRsp
from typing import cast



def _get_kwargs(
    host_name: str,
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/certs/certificate-signing-request/{host_name}/{id}".format(host_name=host_name,id=id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, CSRGetByIdRsp]]:
    if response.status_code == 200:
        response_200 = CSRGetByIdRsp.from_dict(response.json())



        return response_200
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, CSRGetByIdRsp]]:
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

) -> Response[Union[Any, CSRGetByIdRsp]]:
    """ Get the certificate signing request for a given ID

     This API displays details of a certificate signing request of a particular node for a given hostname
    and ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CSRGetByIdRsp]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
id=id,

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

) -> Optional[Union[Any, CSRGetByIdRsp]]:
    """ Get the certificate signing request for a given ID

     This API displays details of a certificate signing request of a particular node for a given hostname
    and ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CSRGetByIdRsp]
     """


    return sync_detailed(
        host_name=host_name,
id=id,
client=client,

    ).parsed

async def asyncio_detailed(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, CSRGetByIdRsp]]:
    """ Get the certificate signing request for a given ID

     This API displays details of a certificate signing request of a particular node for a given hostname
    and ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CSRGetByIdRsp]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
id=id,

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

) -> Optional[Union[Any, CSRGetByIdRsp]]:
    """ Get the certificate signing request for a given ID

     This API displays details of a certificate signing request of a particular node for a given hostname
    and ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CSRGetByIdRsp]
     """


    return (await asyncio_detailed(
        host_name=host_name,
id=id,
client=client,

    )).parsed
