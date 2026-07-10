from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.forbidden_error_message import ForbiddenErrorMessage
from ...models.not_found_error_message import NotFoundErrorMessage
from ...models.patch_list_response import PatchListResponse
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    x_request_id: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/upgrade-patch/patch-install/list-patch",
    }


    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]:
    if response.status_code == 200:
        response_200 = PatchListResponse.from_dict(response.json())



        return response_200
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = ForbiddenErrorMessage.from_dict(response.json())



        return response_403
    if response.status_code == 404:
        response_404 = NotFoundErrorMessage.from_dict(response.json())



        return response_404
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    x_request_id: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]:
    """ List installed patches.

     List all the installed patches in the system with the date of installation.

    Args:
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]
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
    client: AuthenticatedClient,
    x_request_id: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]:
    """ List installed patches.

     List all the installed patches in the system with the date of installation.

    Args:
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]
     """


    return sync_detailed(
        client=client,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    x_request_id: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]:
    """ List installed patches.

     List all the installed patches in the system with the date of installation.

    Args:
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]
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
    client: AuthenticatedClient,
    x_request_id: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]]:
    """ List installed patches.

     List all the installed patches in the system with the date of installation.

    Args:
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, ForbiddenErrorMessage, NotFoundErrorMessage, PatchListResponse]
     """


    return (await asyncio_detailed(
        client=client,
x_request_id=x_request_id,

    )).parsed
