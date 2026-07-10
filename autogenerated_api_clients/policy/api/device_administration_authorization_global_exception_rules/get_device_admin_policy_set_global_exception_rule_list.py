from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.device_admin_authorization_rule_list_response_entity import DeviceAdminAuthorizationRuleListResponseEntity
from ...models.error import Error
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
        "url": "/device-admin/policy-set/global-exception",
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DeviceAdminAuthorizationRuleListResponseEntity | Error | None:
    if response.status_code == 200:
        response_200 = DeviceAdminAuthorizationRuleListResponseEntity.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DeviceAdminAuthorizationRuleListResponseEntity | Error]:
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

) -> Response[DeviceAdminAuthorizationRuleListResponseEntity | Error]:
    """ Device Admin - Get global execption rules.

     Device Admin - Get global execption rules.

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceAdminAuthorizationRuleListResponseEntity | Error]
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

) -> DeviceAdminAuthorizationRuleListResponseEntity | Error | None:
    """ Device Admin - Get global execption rules.

     Device Admin - Get global execption rules.

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceAdminAuthorizationRuleListResponseEntity | Error
     """


    return sync_detailed(
        client=client,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    x_request_id: str | Unset = UNSET,

) -> Response[DeviceAdminAuthorizationRuleListResponseEntity | Error]:
    """ Device Admin - Get global execption rules.

     Device Admin - Get global execption rules.

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceAdminAuthorizationRuleListResponseEntity | Error]
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

) -> DeviceAdminAuthorizationRuleListResponseEntity | Error | None:
    """ Device Admin - Get global execption rules.

     Device Admin - Get global execption rules.

    Args:
        x_request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceAdminAuthorizationRuleListResponseEntity | Error
     """


    return (await asyncio_detailed(
        client=client,
x_request_id=x_request_id,

    )).parsed
