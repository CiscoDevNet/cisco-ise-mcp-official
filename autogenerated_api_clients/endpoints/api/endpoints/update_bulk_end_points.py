# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.open_api_endpoint import OpenAPIEndpoint
from ...models.task_response import TaskResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: list[OpenAPIEndpoint] | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/endpoint/bulk",
    }

    
    if not isinstance(body, Unset):
        _kwargs["json"] = []
        for componentsschemas_endpoints_item_data in body:
            componentsschemas_endpoints_item = componentsschemas_endpoints_item_data.to_dict()
            _kwargs["json"].append(componentsschemas_endpoints_item)




    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | TaskResponse:
    if response.status_code == 200:
        response_200 = TaskResponse.from_dict(response.json())



        return response_200

    response_default = Error.from_dict(response.json())



    return response_default



def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | TaskResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[OpenAPIEndpoint] | Unset = UNSET,

) -> Response[Error | TaskResponse]:
    """ Update Endpoint in bulk

     We recommend that you update endpoint custom attribute data through this bulk update operation using
    OpenAPI instead of the pxGrid Context-In asset topic or the endpoint ERS API. (Use bulk create
    operation if endpoint does not already exist in Cisco ISE database.)
    <ul>
    __Limitations to using the pxGrid Context-In asset topic or the Endpoint ERS API__
    </ul>
    <ul>
    pxGrid Context-In Asset topic
    <ul>
    <li>When Endpoint custom attribute updates come through pxGrid Context-In asset topic, the endpoints
    are reprofiled. But the custom attribute updates remain in the current PSN's cache and persist in
    the database only after 12 hours. Only changes to significant endpoint attributes results in
    immediate persistence to database. As a result, the authorization policies that use the revised
    custom attributes are not honored until the updates are persistent 12 hours later.</li>
    </ul>
    </ul>
    <ul>
    Endpoint ERS API
    <ul>
    <li>Updating endpoint custom attributes through ERS API does not trigger endpoint reprofiling. As a
    result, the profiler policies that contain the revised custom attributes are not honored.</li>

    <li>Endpoint ERS APIs provide a 2-step update for endpoints: use the GET operation to fetch the
    endpoint ID, and update the endpoint using the ID. These steps make the bulk update of endpoint data
    cumbersome.</li>
    </ul>
    <ul>
    <li>In earlier releases of Cisco ISE you could not programmatically create or update custom
    attributes. These tasks required manual effort through the admin portal UI. Cisco ISE could then
    ingest the data through either Endpoint ERS API or the pxGrid Context-In asset topic.</li>

    </ul>
    </ul>
    <ul>
     __Solution__
    </ul>
    <ul>
    To address these limitations, Cisco ISE now provides -

    <ul>
    <li>Endpoint CRUD operations with bulk create and update capabilities through Open API model which
    has a more efficient infrastructure for bulk operations compared to ERS API.</li>

    <li>Cisco ISE triggers endpoint reprofiling after an endpoint custom attribute is updated if
    __Custom Attribute for Profiling Enforcement__ is enabled in the admin portal UI in the __Work
    Centers > Profiler Settings__ page.</li>

    <li> You can programmatically create, read, update, and delete the custom attributes through Open
    APIs provided for Custom Attributes.</li>
    </ul>
    </ul>

    Args:
        body (list[OpenAPIEndpoint] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | TaskResponse]
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
    client: AuthenticatedClient | Client,
    body: list[OpenAPIEndpoint] | Unset = UNSET,

) -> Error | TaskResponse | None:
    """ Update Endpoint in bulk

     We recommend that you update endpoint custom attribute data through this bulk update operation using
    OpenAPI instead of the pxGrid Context-In asset topic or the endpoint ERS API. (Use bulk create
    operation if endpoint does not already exist in Cisco ISE database.)
    <ul>
    __Limitations to using the pxGrid Context-In asset topic or the Endpoint ERS API__
    </ul>
    <ul>
    pxGrid Context-In Asset topic
    <ul>
    <li>When Endpoint custom attribute updates come through pxGrid Context-In asset topic, the endpoints
    are reprofiled. But the custom attribute updates remain in the current PSN's cache and persist in
    the database only after 12 hours. Only changes to significant endpoint attributes results in
    immediate persistence to database. As a result, the authorization policies that use the revised
    custom attributes are not honored until the updates are persistent 12 hours later.</li>
    </ul>
    </ul>
    <ul>
    Endpoint ERS API
    <ul>
    <li>Updating endpoint custom attributes through ERS API does not trigger endpoint reprofiling. As a
    result, the profiler policies that contain the revised custom attributes are not honored.</li>

    <li>Endpoint ERS APIs provide a 2-step update for endpoints: use the GET operation to fetch the
    endpoint ID, and update the endpoint using the ID. These steps make the bulk update of endpoint data
    cumbersome.</li>
    </ul>
    <ul>
    <li>In earlier releases of Cisco ISE you could not programmatically create or update custom
    attributes. These tasks required manual effort through the admin portal UI. Cisco ISE could then
    ingest the data through either Endpoint ERS API or the pxGrid Context-In asset topic.</li>

    </ul>
    </ul>
    <ul>
     __Solution__
    </ul>
    <ul>
    To address these limitations, Cisco ISE now provides -

    <ul>
    <li>Endpoint CRUD operations with bulk create and update capabilities through Open API model which
    has a more efficient infrastructure for bulk operations compared to ERS API.</li>

    <li>Cisco ISE triggers endpoint reprofiling after an endpoint custom attribute is updated if
    __Custom Attribute for Profiling Enforcement__ is enabled in the admin portal UI in the __Work
    Centers > Profiler Settings__ page.</li>

    <li> You can programmatically create, read, update, and delete the custom attributes through Open
    APIs provided for Custom Attributes.</li>
    </ul>
    </ul>

    Args:
        body (list[OpenAPIEndpoint] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | TaskResponse
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[OpenAPIEndpoint] | Unset = UNSET,

) -> Response[Error | TaskResponse]:
    """ Update Endpoint in bulk

     We recommend that you update endpoint custom attribute data through this bulk update operation using
    OpenAPI instead of the pxGrid Context-In asset topic or the endpoint ERS API. (Use bulk create
    operation if endpoint does not already exist in Cisco ISE database.)
    <ul>
    __Limitations to using the pxGrid Context-In asset topic or the Endpoint ERS API__
    </ul>
    <ul>
    pxGrid Context-In Asset topic
    <ul>
    <li>When Endpoint custom attribute updates come through pxGrid Context-In asset topic, the endpoints
    are reprofiled. But the custom attribute updates remain in the current PSN's cache and persist in
    the database only after 12 hours. Only changes to significant endpoint attributes results in
    immediate persistence to database. As a result, the authorization policies that use the revised
    custom attributes are not honored until the updates are persistent 12 hours later.</li>
    </ul>
    </ul>
    <ul>
    Endpoint ERS API
    <ul>
    <li>Updating endpoint custom attributes through ERS API does not trigger endpoint reprofiling. As a
    result, the profiler policies that contain the revised custom attributes are not honored.</li>

    <li>Endpoint ERS APIs provide a 2-step update for endpoints: use the GET operation to fetch the
    endpoint ID, and update the endpoint using the ID. These steps make the bulk update of endpoint data
    cumbersome.</li>
    </ul>
    <ul>
    <li>In earlier releases of Cisco ISE you could not programmatically create or update custom
    attributes. These tasks required manual effort through the admin portal UI. Cisco ISE could then
    ingest the data through either Endpoint ERS API or the pxGrid Context-In asset topic.</li>

    </ul>
    </ul>
    <ul>
     __Solution__
    </ul>
    <ul>
    To address these limitations, Cisco ISE now provides -

    <ul>
    <li>Endpoint CRUD operations with bulk create and update capabilities through Open API model which
    has a more efficient infrastructure for bulk operations compared to ERS API.</li>

    <li>Cisco ISE triggers endpoint reprofiling after an endpoint custom attribute is updated if
    __Custom Attribute for Profiling Enforcement__ is enabled in the admin portal UI in the __Work
    Centers > Profiler Settings__ page.</li>

    <li> You can programmatically create, read, update, and delete the custom attributes through Open
    APIs provided for Custom Attributes.</li>
    </ul>
    </ul>

    Args:
        body (list[OpenAPIEndpoint] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | TaskResponse]
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
    client: AuthenticatedClient | Client,
    body: list[OpenAPIEndpoint] | Unset = UNSET,

) -> Error | TaskResponse | None:
    """ Update Endpoint in bulk

     We recommend that you update endpoint custom attribute data through this bulk update operation using
    OpenAPI instead of the pxGrid Context-In asset topic or the endpoint ERS API. (Use bulk create
    operation if endpoint does not already exist in Cisco ISE database.)
    <ul>
    __Limitations to using the pxGrid Context-In asset topic or the Endpoint ERS API__
    </ul>
    <ul>
    pxGrid Context-In Asset topic
    <ul>
    <li>When Endpoint custom attribute updates come through pxGrid Context-In asset topic, the endpoints
    are reprofiled. But the custom attribute updates remain in the current PSN's cache and persist in
    the database only after 12 hours. Only changes to significant endpoint attributes results in
    immediate persistence to database. As a result, the authorization policies that use the revised
    custom attributes are not honored until the updates are persistent 12 hours later.</li>
    </ul>
    </ul>
    <ul>
    Endpoint ERS API
    <ul>
    <li>Updating endpoint custom attributes through ERS API does not trigger endpoint reprofiling. As a
    result, the profiler policies that contain the revised custom attributes are not honored.</li>

    <li>Endpoint ERS APIs provide a 2-step update for endpoints: use the GET operation to fetch the
    endpoint ID, and update the endpoint using the ID. These steps make the bulk update of endpoint data
    cumbersome.</li>
    </ul>
    <ul>
    <li>In earlier releases of Cisco ISE you could not programmatically create or update custom
    attributes. These tasks required manual effort through the admin portal UI. Cisco ISE could then
    ingest the data through either Endpoint ERS API or the pxGrid Context-In asset topic.</li>

    </ul>
    </ul>
    <ul>
     __Solution__
    </ul>
    <ul>
    To address these limitations, Cisco ISE now provides -

    <ul>
    <li>Endpoint CRUD operations with bulk create and update capabilities through Open API model which
    has a more efficient infrastructure for bulk operations compared to ERS API.</li>

    <li>Cisco ISE triggers endpoint reprofiling after an endpoint custom attribute is updated if
    __Custom Attribute for Profiling Enforcement__ is enabled in the admin portal UI in the __Work
    Centers > Profiler Settings__ page.</li>

    <li> You can programmatically create, read, update, and delete the custom attributes through Open
    APIs provided for Custom Attributes.</li>
    </ul>
    </ul>

    Args:
        body (list[OpenAPIEndpoint] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | TaskResponse
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
