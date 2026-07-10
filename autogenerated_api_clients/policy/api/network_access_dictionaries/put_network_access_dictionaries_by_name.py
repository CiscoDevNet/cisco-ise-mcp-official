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
    name: str,
    *,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/network-access/dictionaries/{name}".format(name=quote(str(name), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DictionaryResponseEntity | Error | None:
    if response.status_code == 200:
        response_200 = DictionaryResponseEntity.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DictionaryResponseEntity | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> Response[DictionaryResponseEntity | Error]:
    """ Network Access - Update a Dictionary.

     Network Access - Update a Dictionary.

    Args:
        name (str):
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DictionaryResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        name=name,
body=body,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> DictionaryResponseEntity | Error | None:
    """ Network Access - Update a Dictionary.

     Network Access - Update a Dictionary.

    Args:
        name (str):
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DictionaryResponseEntity | Error
     """


    return sync_detailed(
        name=name,
client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> Response[DictionaryResponseEntity | Error]:
    """ Network Access - Update a Dictionary.

     Network Access - Update a Dictionary.

    Args:
        name (str):
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DictionaryResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        name=name,
body=body,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Dictionary,
    x_request_id: str | Unset = UNSET,

) -> DictionaryResponseEntity | Error | None:
    """ Network Access - Update a Dictionary.

     Network Access - Update a Dictionary.

    Args:
        name (str):
        x_request_id (str | Unset):
        body (Dictionary): Dictionary POST format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DictionaryResponseEntity | Error
     """


    return (await asyncio_detailed(
        name=name,
client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
