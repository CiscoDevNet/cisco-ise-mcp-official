from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.id_response_entity import IdResponseEntity
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    condition_id: UUID,
    *,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/device-admin/condition/{condition_id}".format(condition_id=quote(str(condition_id), safe=""),),
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | IdResponseEntity | None:
    if response.status_code == 200:
        response_200 = IdResponseEntity.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | IdResponseEntity]:
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
    x_request_id: str | Unset = UNSET,

) -> Response[Error | IdResponseEntity]:
    """ Device Admin - Delete a library condition.

     Device Admin - Delete a library condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | IdResponseEntity]
     """


    kwargs = _get_kwargs(
        condition_id=condition_id,
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
    x_request_id: str | Unset = UNSET,

) -> Error | IdResponseEntity | None:
    """ Device Admin - Delete a library condition.

     Device Admin - Delete a library condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | IdResponseEntity
     """


    return sync_detailed(
        condition_id=condition_id,
client=client,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    condition_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | IdResponseEntity]:
    """ Device Admin - Delete a library condition.

     Device Admin - Delete a library condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | IdResponseEntity]
     """


    kwargs = _get_kwargs(
        condition_id=condition_id,
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
    x_request_id: str | Unset = UNSET,

) -> Error | IdResponseEntity | None:
    """ Device Admin - Delete a library condition.

     Device Admin - Delete a library condition.

    Args:
        condition_id (UUID):
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | IdResponseEntity
     """


    return (await asyncio_detailed(
        condition_id=condition_id,
client=client,
x_request_id=x_request_id,

    )).parsed
