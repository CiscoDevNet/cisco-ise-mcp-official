# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.regenerate_root_ca import RegenerateRootCA
from ...models.regenerate_root_ca_resp_payload import RegenerateRootCaRespPayload
from typing import cast



def _get_kwargs(
    *,
    body: RegenerateRootCA,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/ise-root-ca/regenerate",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, RegenerateRootCaRespPayload]]:
    if response.status_code == 200:
        response_200 = Error.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201
    if response.status_code == 202:
        response_202 = RegenerateRootCaRespPayload.from_dict(response.json())



        return response_202
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 405:
        response_405 = Error.from_dict(response.json())



        return response_405
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, RegenerateRootCaRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: RegenerateRootCA,

) -> Response[Union[Any, Error, RegenerateRootCaRespPayload]]:
    r""" Regenerate entire internal CA certificate chain including root CA on the primary PAN and subordinate
    CAs on the PSNs (Applicable only for internal CA service)

     This API initiates regeneration of Cisco ISE root CA certificate chain. The response contains an ID
    which can be used to track the status. <br>  Setting \"removeExistingISEIntermediateCSR\" to true
    removes existing Cisco ISE Intermediate CSR.

    Args:
        body (RegenerateRootCA):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, RegenerateRootCaRespPayload]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: RegenerateRootCA,

) -> Optional[Union[Any, Error, RegenerateRootCaRespPayload]]:
    r""" Regenerate entire internal CA certificate chain including root CA on the primary PAN and subordinate
    CAs on the PSNs (Applicable only for internal CA service)

     This API initiates regeneration of Cisco ISE root CA certificate chain. The response contains an ID
    which can be used to track the status. <br>  Setting \"removeExistingISEIntermediateCSR\" to true
    removes existing Cisco ISE Intermediate CSR.

    Args:
        body (RegenerateRootCA):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, RegenerateRootCaRespPayload]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: RegenerateRootCA,

) -> Response[Union[Any, Error, RegenerateRootCaRespPayload]]:
    r""" Regenerate entire internal CA certificate chain including root CA on the primary PAN and subordinate
    CAs on the PSNs (Applicable only for internal CA service)

     This API initiates regeneration of Cisco ISE root CA certificate chain. The response contains an ID
    which can be used to track the status. <br>  Setting \"removeExistingISEIntermediateCSR\" to true
    removes existing Cisco ISE Intermediate CSR.

    Args:
        body (RegenerateRootCA):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, RegenerateRootCaRespPayload]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: RegenerateRootCA,

) -> Optional[Union[Any, Error, RegenerateRootCaRespPayload]]:
    r""" Regenerate entire internal CA certificate chain including root CA on the primary PAN and subordinate
    CAs on the PSNs (Applicable only for internal CA service)

     This API initiates regeneration of Cisco ISE root CA certificate chain. The response contains an ID
    which can be used to track the status. <br>  Setting \"removeExistingISEIntermediateCSR\" to true
    removes existing Cisco ISE Intermediate CSR.

    Args:
        body (RegenerateRootCA):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, RegenerateRootCaRespPayload]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
