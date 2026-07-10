from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.delete_trusted_cert_resp_payload import DeleteTrustedCertRespPayload
from ...models.error import Error
from typing import cast



def _get_kwargs(
    id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/certs/trusted-certificate/{id}".format(id=id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, DeleteTrustedCertRespPayload, Error]]:
    if response.status_code == 200:
        response_200 = DeleteTrustedCertRespPayload.from_dict(response.json())



        return response_200
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, DeleteTrustedCertRespPayload, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, DeleteTrustedCertRespPayload, Error]]:
    """ Delete a trusted certificate based on a given ID

     This API deletes a Trust Certificate from Trusted Certificate Store based on a given ID.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteTrustedCertRespPayload, Error]]
     """


    kwargs = _get_kwargs(
        id=id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, DeleteTrustedCertRespPayload, Error]]:
    """ Delete a trusted certificate based on a given ID

     This API deletes a Trust Certificate from Trusted Certificate Store based on a given ID.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteTrustedCertRespPayload, Error]
     """


    return sync_detailed(
        id=id,
client=client,

    ).parsed

async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, DeleteTrustedCertRespPayload, Error]]:
    """ Delete a trusted certificate based on a given ID

     This API deletes a Trust Certificate from Trusted Certificate Store based on a given ID.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteTrustedCertRespPayload, Error]]
     """


    kwargs = _get_kwargs(
        id=id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, DeleteTrustedCertRespPayload, Error]]:
    """ Delete a trusted certificate based on a given ID

     This API deletes a Trust Certificate from Trusted Certificate Store based on a given ID.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteTrustedCertRespPayload, Error]
     """


    return (await asyncio_detailed(
        id=id,
client=client,

    )).parsed
