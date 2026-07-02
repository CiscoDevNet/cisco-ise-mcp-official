from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.open_api_endpoint import OpenAPIEndpoint
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    value: str,
    *,
    body: OpenAPIEndpoint | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/endpoint/{value}".format(value=quote(str(value), safe=""),),
    }

    
    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | OpenAPIEndpoint:
    if response.status_code == 200:
        response_200 = OpenAPIEndpoint.from_dict(response.json())



        return response_200

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    response_default = Error.from_dict(response.json())



    return response_default



def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Error | OpenAPIEndpoint]:
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
    body: OpenAPIEndpoint | Unset = UNSET,

) -> Response[Any | Error | OpenAPIEndpoint]:
    """ Update Endpoint by id or mac

    Args:
        value (str):
        body (OpenAPIEndpoint | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | OpenAPIEndpoint]
     """


    kwargs = _get_kwargs(
        value=value,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    value: str,
    *,
    client: AuthenticatedClient | Client,
    body: OpenAPIEndpoint | Unset = UNSET,

) -> Any | Error | OpenAPIEndpoint | None:
    """ Update Endpoint by id or mac

    Args:
        value (str):
        body (OpenAPIEndpoint | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | OpenAPIEndpoint
     """


    return sync_detailed(
        value=value,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    value: str,
    *,
    client: AuthenticatedClient | Client,
    body: OpenAPIEndpoint | Unset = UNSET,

) -> Response[Any | Error | OpenAPIEndpoint]:
    """ Update Endpoint by id or mac

    Args:
        value (str):
        body (OpenAPIEndpoint | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | OpenAPIEndpoint]
     """


    kwargs = _get_kwargs(
        value=value,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    value: str,
    *,
    client: AuthenticatedClient | Client,
    body: OpenAPIEndpoint | Unset = UNSET,

) -> Any | Error | OpenAPIEndpoint | None:
    """ Update Endpoint by id or mac

    Args:
        value (str):
        body (OpenAPIEndpoint | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | OpenAPIEndpoint
     """


    return (await asyncio_detailed(
        value=value,
client=client,
body=body,

    )).parsed
