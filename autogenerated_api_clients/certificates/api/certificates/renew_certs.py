from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.renew_cert_resp_payload import RenewCertRespPayload
from ...models.renew_certificates import RenewCertificates
from typing import cast



def _get_kwargs(
    *,
    body: RenewCertificates,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certs/renew-certificate",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, RenewCertRespPayload]]:
    if response.status_code == 200:
        response_200 = Error.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = cast(Any, None)
        return response_201
    if response.status_code == 202:
        response_202 = RenewCertRespPayload.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, RenewCertRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: RenewCertificates,

) -> Response[Union[Any, Error, RenewCertRespPayload]]:
    """ Renew certificates of OCSP responder, Cisco ISE Messaging Service, and Datagrid Service

     This API initiates regeneration of certificates. The response contains an ID which can be used to
    track the status.

    Args:
        body (RenewCertificates):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, RenewCertRespPayload]]
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
    body: RenewCertificates,

) -> Optional[Union[Any, Error, RenewCertRespPayload]]:
    """ Renew certificates of OCSP responder, Cisco ISE Messaging Service, and Datagrid Service

     This API initiates regeneration of certificates. The response contains an ID which can be used to
    track the status.

    Args:
        body (RenewCertificates):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, RenewCertRespPayload]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: RenewCertificates,

) -> Response[Union[Any, Error, RenewCertRespPayload]]:
    """ Renew certificates of OCSP responder, Cisco ISE Messaging Service, and Datagrid Service

     This API initiates regeneration of certificates. The response contains an ID which can be used to
    track the status.

    Args:
        body (RenewCertificates):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, RenewCertRespPayload]]
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
    body: RenewCertificates,

) -> Optional[Union[Any, Error, RenewCertRespPayload]]:
    """ Renew certificates of OCSP responder, Cisco ISE Messaging Service, and Datagrid Service

     This API initiates regeneration of certificates. The response contains an ID which can be used to
    track the status.

    Args:
        body (RenewCertificates):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, RenewCertRespPayload]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
