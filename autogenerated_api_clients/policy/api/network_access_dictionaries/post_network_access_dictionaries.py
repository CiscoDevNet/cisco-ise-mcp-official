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

from ...models.dictionary import Dictionary
from ...models.dictionary_response_entity import DictionaryResponseEntity
from ...models.error import Error
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/network-access/dictionaries",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DictionaryResponseEntity | Error | None:
    if response.status_code == 201:
        response_201 = DictionaryResponseEntity.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400

    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DictionaryResponseEntity | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> Response[DictionaryResponseEntity | Error]:
    """ Network Access - Create a new Dictionary.

     Network Access - Create a new Dictionary.

    Args:
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DictionaryResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        body=body,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> DictionaryResponseEntity | Error | None:
    """ Network Access - Create a new Dictionary.

     Network Access - Create a new Dictionary.

    Args:
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DictionaryResponseEntity | Error
     """


    return sync_detailed(
        client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> Response[DictionaryResponseEntity | Error]:
    """ Network Access - Create a new Dictionary.

     Network Access - Create a new Dictionary.

    Args:
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DictionaryResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        body=body,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> DictionaryResponseEntity | Error | None:
    """ Network Access - Create a new Dictionary.

     Network Access - Create a new Dictionary.

    Args:
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DictionaryResponseEntity | Error
     """


    return (await asyncio_detailed(
        client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
