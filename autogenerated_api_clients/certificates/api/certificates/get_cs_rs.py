from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.csr_get_all_rsp import CSRGetAllRsp
from ...models.get_cs_rs_filter_type import GetCSRsFilterType
from ...models.get_cs_rs_sort import GetCSRsSort
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    *,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetCSRsSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetCSRsFilterType] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["page"] = page

    params["size"] = size

    json_sort: Union[Unset, str] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params["sortBy"] = sort_by

    params["filter"] = filter_

    json_filter_type: Union[Unset, str] = UNSET
    if not isinstance(filter_type, Unset):
        json_filter_type = filter_type.value

    params["filterType"] = json_filter_type


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/certs/certificate-signing-request",
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, CSRGetAllRsp]]:
    if response.status_code == 200:
        response_200 = CSRGetAllRsp.from_dict(response.json())



        return response_200
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, CSRGetAllRsp]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetCSRsSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetCSRsFilterType] = UNSET,

) -> Response[Union[Any, CSRGetAllRsp]]:
    r""" Get all Certificate Signing Requests from PAN

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting are supported for the following attributes: </p>
    <ul style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>subject</li>
    <li>timeStamp</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss.SSS</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetCSRsSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetCSRsFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CSRGetAllRsp]]
     """


    kwargs = _get_kwargs(
        page=page,
size=size,
sort=sort,
sort_by=sort_by,
filter_=filter_,
filter_type=filter_type,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetCSRsSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetCSRsFilterType] = UNSET,

) -> Optional[Union[Any, CSRGetAllRsp]]:
    r""" Get all Certificate Signing Requests from PAN

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting are supported for the following attributes: </p>
    <ul style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>subject</li>
    <li>timeStamp</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss.SSS</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetCSRsSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetCSRsFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CSRGetAllRsp]
     """


    return sync_detailed(
        client=client,
page=page,
size=size,
sort=sort,
sort_by=sort_by,
filter_=filter_,
filter_type=filter_type,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetCSRsSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetCSRsFilterType] = UNSET,

) -> Response[Union[Any, CSRGetAllRsp]]:
    r""" Get all Certificate Signing Requests from PAN

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting are supported for the following attributes: </p>
    <ul style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>subject</li>
    <li>timeStamp</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss.SSS</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetCSRsSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetCSRsFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CSRGetAllRsp]]
     """


    kwargs = _get_kwargs(
        page=page,
size=size,
sort=sort,
sort_by=sort_by,
filter_=filter_,
filter_type=filter_type,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetCSRsSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetCSRsFilterType] = UNSET,

) -> Optional[Union[Any, CSRGetAllRsp]]:
    r""" Get all Certificate Signing Requests from PAN

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting are supported for the following attributes: </p>
    <ul style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>subject</li>
    <li>timeStamp</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss.SSS</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetCSRsSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetCSRsFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CSRGetAllRsp]
     """


    return (await asyncio_detailed(
        client=client,
page=page,
size=size,
sort=sort,
sort_by=sort_by,
filter_=filter_,
filter_type=filter_type,

    )).parsed
