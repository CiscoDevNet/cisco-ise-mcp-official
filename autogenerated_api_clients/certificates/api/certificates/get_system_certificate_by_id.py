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
from ...models.system_cert_get_by_id_rsp import SystemCertGetByIdRsp
from typing import cast



def _get_kwargs(
    host_name: str,
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/certs/system-certificate/{host_name}/{id}".format(host_name=host_name,id=id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, SystemCertGetByIdRsp]]:
    if response.status_code == 200:
        response_200 = SystemCertGetByIdRsp.from_dict(response.json())



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
    if response.status_code == 405:
        response_405 = Error.from_dict(response.json())



        return response_405
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, SystemCertGetByIdRsp]]:
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

) -> Response[Union[Any, Error, SystemCertGetByIdRsp]]:
    """ Get system certificate of a particular node by ID

     This API provides details of a system certificate of a particular node based on given hostname and
    ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, SystemCertGetByIdRsp]]
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

) -> Optional[Union[Any, Error, SystemCertGetByIdRsp]]:
    """ Get system certificate of a particular node by ID

     This API provides details of a system certificate of a particular node based on given hostname and
    ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, SystemCertGetByIdRsp]
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

) -> Response[Union[Any, Error, SystemCertGetByIdRsp]]:
    """ Get system certificate of a particular node by ID

     This API provides details of a system certificate of a particular node based on given hostname and
    ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, SystemCertGetByIdRsp]]
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

) -> Optional[Union[Any, Error, SystemCertGetByIdRsp]]:
    """ Get system certificate of a particular node by ID

     This API provides details of a system certificate of a particular node based on given hostname and
    ID.

    Args:
        host_name (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, SystemCertGetByIdRsp]
     """


    return (await asyncio_detailed(
        host_name=host_name,
id=id,
client=client,

    )).parsed
