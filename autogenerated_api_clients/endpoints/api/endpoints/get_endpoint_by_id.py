# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.open_api_endpoint import OpenAPIEndpoint
from typing import cast



def _get_kwargs(
    value: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/endpoint/{value}".format(value=quote(str(value), safe=""),),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | OpenAPIEndpoint:
    if response.status_code == 200:
        response_200 = OpenAPIEndpoint.from_dict(response.json())



        return response_200

    response_default = Error.from_dict(response.json())



    return response_default



def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | OpenAPIEndpoint]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    value: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Error | OpenAPIEndpoint]:
    """ Get endpoint by id or MAC

    Args:
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OpenAPIEndpoint]
     """


    kwargs = _get_kwargs(
        value=value,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    value: str,
    *,
    client: AuthenticatedClient | Client,

) -> Error | OpenAPIEndpoint | None:
    """ Get endpoint by id or MAC

    Args:
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OpenAPIEndpoint
     """


    return sync_detailed(
        value=value,
client=client,

    ).parsed

async def asyncio_detailed(
    value: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[Error | OpenAPIEndpoint]:
    """ Get endpoint by id or MAC

    Args:
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OpenAPIEndpoint]
     """


    kwargs = _get_kwargs(
        value=value,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    value: str,
    *,
    client: AuthenticatedClient | Client,

) -> Error | OpenAPIEndpoint | None:
    """ Get endpoint by id or MAC

    Args:
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OpenAPIEndpoint
     """


    return (await asyncio_detailed(
        value=value,
client=client,

    )).parsed
