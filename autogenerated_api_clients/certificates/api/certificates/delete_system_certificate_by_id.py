from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.delete_system_cert_request import DeleteSystemCertRequest
from ...models.delete_system_cert_resp_payload import DeleteSystemCertRespPayload
from typing import cast



def _get_kwargs(
    host_name: str,
    id: str,
    *,
    body: DeleteSystemCertRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/certs/system-certificate/{host_name}/{id}".format(host_name=host_name,id=id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, DeleteSystemCertRespPayload]]:
    if response.status_code == 200:
        response_200 = DeleteSystemCertRespPayload.from_dict(response.json())



        return response_200
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = DeleteSystemCertRespPayload.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, DeleteSystemCertRespPayload]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: DeleteSystemCertRequest,

) -> Response[Union[Any, DeleteSystemCertRespPayload]]:
    """ Delete System Certificate by ID and hostname

     This API deletes a system certificate of a particular node based on the given hostname and ID.

    Args:
        host_name (str):
        id (str):
        body (DeleteSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteSystemCertRespPayload]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
id=id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: DeleteSystemCertRequest,

) -> Optional[Union[Any, DeleteSystemCertRespPayload]]:
    """ Delete System Certificate by ID and hostname

     This API deletes a system certificate of a particular node based on the given hostname and ID.

    Args:
        host_name (str):
        id (str):
        body (DeleteSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteSystemCertRespPayload]
     """


    return sync_detailed(
        host_name=host_name,
id=id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: DeleteSystemCertRequest,

) -> Response[Union[Any, DeleteSystemCertRespPayload]]:
    """ Delete System Certificate by ID and hostname

     This API deletes a system certificate of a particular node based on the given hostname and ID.

    Args:
        host_name (str):
        id (str):
        body (DeleteSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteSystemCertRespPayload]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
id=id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    host_name: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: DeleteSystemCertRequest,

) -> Optional[Union[Any, DeleteSystemCertRespPayload]]:
    """ Delete System Certificate by ID and hostname

     This API deletes a system certificate of a particular node based on the given hostname and ID.

    Args:
        host_name (str):
        id (str):
        body (DeleteSystemCertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteSystemCertRespPayload]
     """


    return (await asyncio_detailed(
        host_name=host_name,
id=id,
client=client,
body=body,

    )).parsed
