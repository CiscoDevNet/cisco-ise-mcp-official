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
from ...models.time_and_date_condition import TimeAndDateCondition
from ...models.time_and_date_condition_response_entity import TimeAndDateConditionResponseEntity
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    condition_id: UUID,
    *,
    body: TimeAndDateCondition,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/device-admin/time-condition/{condition_id}".format(condition_id=quote(str(condition_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | TimeAndDateConditionResponseEntity | None:
    if response.status_code == 200:
        response_200 = TimeAndDateConditionResponseEntity.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | TimeAndDateConditionResponseEntity]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    condition_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: TimeAndDateCondition,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | TimeAndDateConditionResponseEntity]:
    """ Device Admin - Update network condition.

     Device Admin - Update network condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):
        body (TimeAndDateCondition): Condition based on time and date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | TimeAndDateConditionResponseEntity]
     """


    kwargs = _get_kwargs(
        condition_id=condition_id,
body=body,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    condition_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: TimeAndDateCondition,
    x_request_id: str | Unset = UNSET,

) -> Error | TimeAndDateConditionResponseEntity | None:
    """ Device Admin - Update network condition.

     Device Admin - Update network condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):
        body (TimeAndDateCondition): Condition based on time and date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | TimeAndDateConditionResponseEntity
     """


    return sync_detailed(
        condition_id=condition_id,
client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    condition_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: TimeAndDateCondition,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | TimeAndDateConditionResponseEntity]:
    """ Device Admin - Update network condition.

     Device Admin - Update network condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):
        body (TimeAndDateCondition): Condition based on time and date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | TimeAndDateConditionResponseEntity]
     """


    kwargs = _get_kwargs(
        condition_id=condition_id,
body=body,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    condition_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: TimeAndDateCondition,
    x_request_id: str | Unset = UNSET,

) -> Error | TimeAndDateConditionResponseEntity | None:
    """ Device Admin - Update network condition.

     Device Admin - Update network condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):
        body (TimeAndDateCondition): Condition based on time and date.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | TimeAndDateConditionResponseEntity
     """


    return (await asyncio_detailed(
        condition_id=condition_id,
client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
