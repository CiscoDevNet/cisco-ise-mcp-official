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

from ...models.dictionary_attribute_response_entity import DictionaryAttributeResponseEntity
from ...models.error import Error
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    dictionary_name: str,
    attribute_name: str,
    *,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/network-access/dictionaries/{dictionary_name}/attribute/{attribute_name}".format(dictionary_name=quote(str(dictionary_name), safe=""),attribute_name=quote(str(attribute_name), safe=""),),
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DictionaryAttributeResponseEntity | Error | None:
    if response.status_code == 200:
        response_200 = DictionaryAttributeResponseEntity.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DictionaryAttributeResponseEntity | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dictionary_name: str,
    attribute_name: str,
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Response[DictionaryAttributeResponseEntity | Error]:
    """ Get a Dictionary Attribute.

     Get a Dictionary Attribute.

    Args:
        dictionary_name (str):
        attribute_name (str):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DictionaryAttributeResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        dictionary_name=dictionary_name,
attribute_name=attribute_name,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dictionary_name: str,
    attribute_name: str,
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> DictionaryAttributeResponseEntity | Error | None:
    """ Get a Dictionary Attribute.

     Get a Dictionary Attribute.

    Args:
        dictionary_name (str):
        attribute_name (str):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DictionaryAttributeResponseEntity | Error
     """


    return sync_detailed(
        dictionary_name=dictionary_name,
attribute_name=attribute_name,
client=client,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    dictionary_name: str,
    attribute_name: str,
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Response[DictionaryAttributeResponseEntity | Error]:
    """ Get a Dictionary Attribute.

     Get a Dictionary Attribute.

    Args:
        dictionary_name (str):
        attribute_name (str):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DictionaryAttributeResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        dictionary_name=dictionary_name,
attribute_name=attribute_name,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dictionary_name: str,
    attribute_name: str,
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> DictionaryAttributeResponseEntity | Error | None:
    """ Get a Dictionary Attribute.

     Get a Dictionary Attribute.

    Args:
        dictionary_name (str):
        attribute_name (str):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DictionaryAttributeResponseEntity | Error
     """


    return (await asyncio_detailed(
        dictionary_name=dictionary_name,
attribute_name=attribute_name,
client=client,
x_request_id=x_request_id,

    )).parsed
