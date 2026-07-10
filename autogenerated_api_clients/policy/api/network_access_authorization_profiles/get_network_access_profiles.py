from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.profile import Profile
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/network-access/authorization-profiles",
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | list[Profile] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = Profile.from_dict(response_200_item_data)



            response_200.append(response_200_item)

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | list[Profile]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | list[Profile]]:
    """ Network Access - Returns list of authorization profiles.

     <p>Network Access - Returns list of authorization profiles.<br> (Other CRUD APIs available throught
    ERS)<br></p>

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[Profile]]
     """


    kwargs = _get_kwargs(
        x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Error | list[Profile] | None:
    """ Network Access - Returns list of authorization profiles.

     <p>Network Access - Returns list of authorization profiles.<br> (Other CRUD APIs available throught
    ERS)<br></p>

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[Profile]
     """


    return sync_detailed(
        client=client,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | list[Profile]]:
    """ Network Access - Returns list of authorization profiles.

     <p>Network Access - Returns list of authorization profiles.<br> (Other CRUD APIs available throught
    ERS)<br></p>

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[Profile]]
     """


    kwargs = _get_kwargs(
        x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Error | list[Profile] | None:
    """ Network Access - Returns list of authorization profiles.

     <p>Network Access - Returns list of authorization profiles.<br> (Other CRUD APIs available throught
    ERS)<br></p>

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[Profile]
     """


    return (await asyncio_detailed(
        client=client,
x_request_id=x_request_id,

    )).parsed
