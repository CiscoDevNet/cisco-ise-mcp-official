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
from ...models.get_system_certificates_filter_type import GetSystemCertificatesFilterType
from ...models.get_system_certificates_sort import GetSystemCertificatesSort
from ...models.system_cert_get_all_rsp import SystemCertGetAllRsp
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    host_name: str,
    *,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetSystemCertificatesSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetSystemCertificatesFilterType] = UNSET,

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
        "url": "/api/v1/certs/system-certificate/{host_name}".format(host_name=host_name,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error, SystemCertGetAllRsp]]:
    if response.status_code == 200:
        response_200 = SystemCertGetAllRsp.from_dict(response.json())



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
    if response.status_code == 405:
        response_405 = Error.from_dict(response.json())



        return response_405
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error, SystemCertGetAllRsp]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    host_name: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetSystemCertificatesSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetSystemCertificatesFilterType] = UNSET,

) -> Response[Union[Any, Error, SystemCertGetAllRsp]]:
    r""" Get all system certificates of a particular node

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting supported for the following attributes: </p>    <ul
    style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>issuedTo</li>
    <li>issuedBy</li>        <li>validFrom</li>          <ul>            <li>Supported Date Format:
    yyyy-MM-dd HH:mm:ss</li>            <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>
    <li>expirationDate</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        host_name (str):
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetSystemCertificatesSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetSystemCertificatesFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, SystemCertGetAllRsp]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
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
    host_name: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetSystemCertificatesSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetSystemCertificatesFilterType] = UNSET,

) -> Optional[Union[Any, Error, SystemCertGetAllRsp]]:
    r""" Get all system certificates of a particular node

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting supported for the following attributes: </p>    <ul
    style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>issuedTo</li>
    <li>issuedBy</li>        <li>validFrom</li>          <ul>            <li>Supported Date Format:
    yyyy-MM-dd HH:mm:ss</li>            <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>
    <li>expirationDate</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        host_name (str):
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetSystemCertificatesSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetSystemCertificatesFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, SystemCertGetAllRsp]
     """


    return sync_detailed(
        host_name=host_name,
client=client,
page=page,
size=size,
sort=sort,
sort_by=sort_by,
filter_=filter_,
filter_type=filter_type,

    ).parsed

async def asyncio_detailed(
    host_name: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetSystemCertificatesSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetSystemCertificatesFilterType] = UNSET,

) -> Response[Union[Any, Error, SystemCertGetAllRsp]]:
    r""" Get all system certificates of a particular node

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting supported for the following attributes: </p>    <ul
    style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>issuedTo</li>
    <li>issuedBy</li>        <li>validFrom</li>          <ul>            <li>Supported Date Format:
    yyyy-MM-dd HH:mm:ss</li>            <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>
    <li>expirationDate</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        host_name (str):
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetSystemCertificatesSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetSystemCertificatesFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, SystemCertGetAllRsp]]
     """


    kwargs = _get_kwargs(
        host_name=host_name,
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
    host_name: str,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    size: Union[Unset, int] = UNSET,
    sort: Union[Unset, GetSystemCertificatesSort] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    filter_type: Union[Unset, GetSystemCertificatesFilterType] = UNSET,

) -> Optional[Union[Any, Error, SystemCertGetAllRsp]]:
    r""" Get all system certificates of a particular node

     <p style=\"font-size: 15px;\"> This API supports filtering, sorting and pagination. </p><br/> <p
    style=\"font-size: 14px;\">Filtering and sorting supported for the following attributes: </p>    <ul
    style=\"font-size: 14px;\">        <li>friendlyName</li>        <li>issuedTo</li>
    <li>issuedBy</li>        <li>validFrom</li>          <ul>            <li>Supported Date Format:
    yyyy-MM-dd HH:mm:ss</li>            <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>
    <li>expirationDate</li>          <ul>            <li>Supported Date Format: yyyy-MM-dd HH:mm:ss</li>
    <li>Supported Operators: EQ, NEQ, GT and LT</li>          </ul>      </ul>

    Args:
        host_name (str):
        page (Union[Unset, int]):
        size (Union[Unset, int]):
        sort (Union[Unset, GetSystemCertificatesSort]):
        sort_by (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        filter_type (Union[Unset, GetSystemCertificatesFilterType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, SystemCertGetAllRsp]
     """


    return (await asyncio_detailed(
        host_name=host_name,
client=client,
page=page,
size=size,
sort=sort,
sort_by=sort_by,
filter_=filter_,
filter_type=filter_type,

    )).parsed
