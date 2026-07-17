# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.forbidden_error_message import ForbiddenErrorMessage
from ...models.invalid_error_message import InvalidErrorMessage
from ...models.not_found_error_message import NotFoundErrorMessage
from ...models.server_error_message import ServerErrorMessage
from ...models.upgrade_precheck_response import UpgradePrecheckResponse
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    pre_check_report_id: Union[Unset, str] = UNSET,
    precheck_name: Union[Unset, str] = UNSET,
    x_request_id: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    params: dict[str, Any] = {}

    params["preCheckReportID"] = pre_check_report_id

    params["precheckName"] = precheck_name


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/upgrade-patch/patch-install/pre-checks-status",
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]:
    if response.status_code == 200:
        response_200 = UpgradePrecheckResponse.from_dict(response.json())



        return response_200
    if response.status_code == 400:
        response_400 = InvalidErrorMessage.from_dict(response.json())



        return response_400
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
        response_500 = ServerErrorMessage.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    pre_check_report_id: Union[Unset, str] = UNSET,
    precheck_name: Union[Unset, str] = UNSET,
    x_request_id: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]:
    """ Gets status of prechecks for the given precheck report id.

     Get the latest precheck report. User can get status of an individual check by passing check's name.

    Args:
        pre_check_report_id (Union[Unset, str]):
        precheck_name (Union[Unset, str]):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]
     """


    kwargs = _get_kwargs(
        pre_check_report_id=pre_check_report_id,
precheck_name=precheck_name,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    pre_check_report_id: Union[Unset, str] = UNSET,
    precheck_name: Union[Unset, str] = UNSET,
    x_request_id: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]:
    """ Gets status of prechecks for the given precheck report id.

     Get the latest precheck report. User can get status of an individual check by passing check's name.

    Args:
        pre_check_report_id (Union[Unset, str]):
        precheck_name (Union[Unset, str]):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]
     """


    return sync_detailed(
        client=client,
pre_check_report_id=pre_check_report_id,
precheck_name=precheck_name,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    pre_check_report_id: Union[Unset, str] = UNSET,
    precheck_name: Union[Unset, str] = UNSET,
    x_request_id: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]:
    """ Gets status of prechecks for the given precheck report id.

     Get the latest precheck report. User can get status of an individual check by passing check's name.

    Args:
        pre_check_report_id (Union[Unset, str]):
        precheck_name (Union[Unset, str]):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]
     """


    kwargs = _get_kwargs(
        pre_check_report_id=pre_check_report_id,
precheck_name=precheck_name,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    pre_check_report_id: Union[Unset, str] = UNSET,
    precheck_name: Union[Unset, str] = UNSET,
    x_request_id: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]]:
    """ Gets status of prechecks for the given precheck report id.

     Get the latest precheck report. User can get status of an individual check by passing check's name.

    Args:
        pre_check_report_id (Union[Unset, str]):
        precheck_name (Union[Unset, str]):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ForbiddenErrorMessage, InvalidErrorMessage, NotFoundErrorMessage, ServerErrorMessage, UpgradePrecheckResponse]
     """


    return (await asyncio_detailed(
        client=client,
pre_check_report_id=pre_check_report_id,
precheck_name=precheck_name,
x_request_id=x_request_id,

    )).parsed
