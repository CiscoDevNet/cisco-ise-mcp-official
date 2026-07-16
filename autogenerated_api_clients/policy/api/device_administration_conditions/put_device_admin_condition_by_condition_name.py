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

from ...models.condition import Condition
from ...models.error import Error
from ...models.library_condition_response_entity import LibraryConditionResponseEntity
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    condition_name: str,
    *,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/device-admin/condition/condition-by-name/{condition_name}".format(condition_name=quote(str(condition_name), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | LibraryConditionResponseEntity | None:
    if response.status_code == 200:
        response_200 = LibraryConditionResponseEntity.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | LibraryConditionResponseEntity]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    condition_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | LibraryConditionResponseEntity]:
    """ Device Admin - Update library condition by condition name.

     Device Admin - Update library condition using condition name.

    Args:
        condition_name (str):
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | LibraryConditionResponseEntity]
     """


    kwargs = _get_kwargs(
        condition_name=condition_name,
body=body,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    condition_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Error | LibraryConditionResponseEntity | None:
    """ Device Admin - Update library condition by condition name.

     Device Admin - Update library condition using condition name.

    Args:
        condition_name (str):
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | LibraryConditionResponseEntity
     """


    return sync_detailed(
        condition_name=condition_name,
client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    condition_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | LibraryConditionResponseEntity]:
    """ Device Admin - Update library condition by condition name.

     Device Admin - Update library condition using condition name.

    Args:
        condition_name (str):
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | LibraryConditionResponseEntity]
     """


    kwargs = _get_kwargs(
        condition_name=condition_name,
body=body,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    condition_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Error | LibraryConditionResponseEntity | None:
    """ Device Admin - Update library condition by condition name.

     Device Admin - Update library condition using condition name.

    Args:
        condition_name (str):
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | LibraryConditionResponseEntity
     """


    return (await asyncio_detailed(
        condition_name=condition_name,
client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
