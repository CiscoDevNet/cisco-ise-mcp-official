from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.get_endpoints_filter_type import GetEndpointsFilterType
from ...models.get_endpoints_sort import GetEndpointsSort
from ...models.open_api_endpoint import OpenAPIEndpoint
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    page: int | Unset = 1,
    size: int | Unset = 100,
    sort: GetEndpointsSort | Unset = GetEndpointsSort.ASC,
    sort_by: str | Unset = UNSET,
    filter_: list[str] | Unset = UNSET,
    filter_type: GetEndpointsFilterType | Unset = GetEndpointsFilterType.AND,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["page"] = page

    params["size"] = size

    json_sort: str | Unset = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params["sort"] = json_sort

    params["sortBy"] = sort_by

    json_filter_: list[str] | Unset = UNSET
    if not isinstance(filter_, Unset):
        json_filter_ = filter_


    params["filter"] = json_filter_

    json_filter_type: str | Unset = UNSET
    if not isinstance(filter_type, Unset):
        json_filter_type = filter_type.value

    params["filterType"] = json_filter_type


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/endpoint",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | list[OpenAPIEndpoint]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_endpoints_item_data in (_response_200):
            componentsschemas_endpoints_item = OpenAPIEndpoint.from_dict(componentsschemas_endpoints_item_data)



            response_200.append(componentsschemas_endpoints_item)

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400

    response_default = Error.from_dict(response.json())



    return response_default



def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | list[OpenAPIEndpoint]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    size: int | Unset = 100,
    sort: GetEndpointsSort | Unset = GetEndpointsSort.ASC,
    sort_by: str | Unset = UNSET,
    filter_: list[str] | Unset = UNSET,
    filter_type: GetEndpointsFilterType | Unset = GetEndpointsFilterType.AND,

) -> Response[Error | list[OpenAPIEndpoint]]:
    """ Get all endpoints

    Args:
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 100.
        sort (GetEndpointsSort | Unset):  Default: GetEndpointsSort.ASC.
        sort_by (str | Unset):
        filter_ (list[str] | Unset):
        filter_type (GetEndpointsFilterType | Unset):  Default: GetEndpointsFilterType.AND.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[OpenAPIEndpoint]]
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
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    size: int | Unset = 100,
    sort: GetEndpointsSort | Unset = GetEndpointsSort.ASC,
    sort_by: str | Unset = UNSET,
    filter_: list[str] | Unset = UNSET,
    filter_type: GetEndpointsFilterType | Unset = GetEndpointsFilterType.AND,

) -> Error | list[OpenAPIEndpoint] | None:
    """ Get all endpoints

    Args:
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 100.
        sort (GetEndpointsSort | Unset):  Default: GetEndpointsSort.ASC.
        sort_by (str | Unset):
        filter_ (list[str] | Unset):
        filter_type (GetEndpointsFilterType | Unset):  Default: GetEndpointsFilterType.AND.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[OpenAPIEndpoint]
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
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    size: int | Unset = 100,
    sort: GetEndpointsSort | Unset = GetEndpointsSort.ASC,
    sort_by: str | Unset = UNSET,
    filter_: list[str] | Unset = UNSET,
    filter_type: GetEndpointsFilterType | Unset = GetEndpointsFilterType.AND,

) -> Response[Error | list[OpenAPIEndpoint]]:
    """ Get all endpoints

    Args:
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 100.
        sort (GetEndpointsSort | Unset):  Default: GetEndpointsSort.ASC.
        sort_by (str | Unset):
        filter_ (list[str] | Unset):
        filter_type (GetEndpointsFilterType | Unset):  Default: GetEndpointsFilterType.AND.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[OpenAPIEndpoint]]
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
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    size: int | Unset = 100,
    sort: GetEndpointsSort | Unset = GetEndpointsSort.ASC,
    sort_by: str | Unset = UNSET,
    filter_: list[str] | Unset = UNSET,
    filter_type: GetEndpointsFilterType | Unset = GetEndpointsFilterType.AND,

) -> Error | list[OpenAPIEndpoint] | None:
    """ Get all endpoints

    Args:
        page (int | Unset):  Default: 1.
        size (int | Unset):  Default: 100.
        sort (GetEndpointsSort | Unset):  Default: GetEndpointsSort.ASC.
        sort_by (str | Unset):
        filter_ (list[str] | Unset):
        filter_type (GetEndpointsFilterType | Unset):  Default: GetEndpointsFilterType.AND.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[OpenAPIEndpoint]
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
