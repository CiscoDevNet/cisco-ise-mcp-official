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

from ...models.condition import Condition
from ...models.error import Error
from ...models.library_condition_response_entity import LibraryConditionResponseEntity
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/network-access/condition",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | LibraryConditionResponseEntity | None:
    if response.status_code == 201:
        response_201 = LibraryConditionResponseEntity.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | LibraryConditionResponseEntity]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | LibraryConditionResponseEntity]:
    """ Network Access - Creates a library condition.

     Network Access - Creates a library condition:
    <ul>
    <li> Library Condition has hierarchical structure which define a set of condition for which
    authentication and authorization policy rules could be match.</li>
    <li> Condition can be composed either from a single dictionary-attribute name and value pair using
    model <b>LibraryConditionAttributes</b>, or from a combination of 2 or more conditions with a
    logical relation (e.g AND/OR) using models: <b>LibraryConditionAndBlock</b> or
    <b>LibraryConditionOrBlock</b>.</li>
    <li> When using AND/OR blocks, the condition will include inner layers inside these blocks, these
    layers should be built using the inner condition models: <b>ConditionAttributes</b>,
    <b>ConditionAndBlock</b>, <b>ConditionOrBlock</b>; these represent dynamically built Conditions
    which do not get stored in the conditions Library, or using <b>ConditionReference</b>, which
    includes an ID of an existing condition which is in the library.</li>
    <li> The LibraryCondition models can only be used in the outer-most layer (root of the condition)
    and must always include the condition name.</li>
    <li> When using one of the 3 inner-layers condition models (<b>ConditionAttributes,
    ConditionAndBlock, ConditionOrBlock</b>), condition name cannot be included in the request, since
    these will not be stored in the conditions library, and used only as inner members of the root
    condition.</li>
    <li> When using <b>ConditionReference</b> model in inner layers, the condition name is not
    required.</li>
    <li> ConditionReference objects can also include a reference ID to a condition of type
    <b>TimeAndDate</b>.</li>
    <li> <b>NOTE:</b> The request body example provided in the Swagger UI is incomplete and cannot be
    used for creating a valid resource. Please refer to the 'Schema' section below, which offers details
    on the properties required to construct a valid request body for each condition model. Please note
    that the 'conditionType' property needs to be set according to the chosen model for each condition;
    In case of condition blocks (AND/OR), it is required for each of the inner-layer conditions as
    well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | LibraryConditionResponseEntity]
     """


    kwargs = _get_kwargs(
        body=body,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Error | LibraryConditionResponseEntity | None:
    """ Network Access - Creates a library condition.

     Network Access - Creates a library condition:
    <ul>
    <li> Library Condition has hierarchical structure which define a set of condition for which
    authentication and authorization policy rules could be match.</li>
    <li> Condition can be composed either from a single dictionary-attribute name and value pair using
    model <b>LibraryConditionAttributes</b>, or from a combination of 2 or more conditions with a
    logical relation (e.g AND/OR) using models: <b>LibraryConditionAndBlock</b> or
    <b>LibraryConditionOrBlock</b>.</li>
    <li> When using AND/OR blocks, the condition will include inner layers inside these blocks, these
    layers should be built using the inner condition models: <b>ConditionAttributes</b>,
    <b>ConditionAndBlock</b>, <b>ConditionOrBlock</b>; these represent dynamically built Conditions
    which do not get stored in the conditions Library, or using <b>ConditionReference</b>, which
    includes an ID of an existing condition which is in the library.</li>
    <li> The LibraryCondition models can only be used in the outer-most layer (root of the condition)
    and must always include the condition name.</li>
    <li> When using one of the 3 inner-layers condition models (<b>ConditionAttributes,
    ConditionAndBlock, ConditionOrBlock</b>), condition name cannot be included in the request, since
    these will not be stored in the conditions library, and used only as inner members of the root
    condition.</li>
    <li> When using <b>ConditionReference</b> model in inner layers, the condition name is not
    required.</li>
    <li> ConditionReference objects can also include a reference ID to a condition of type
    <b>TimeAndDate</b>.</li>
    <li> <b>NOTE:</b> The request body example provided in the Swagger UI is incomplete and cannot be
    used for creating a valid resource. Please refer to the 'Schema' section below, which offers details
    on the properties required to construct a valid request body for each condition model. Please note
    that the 'conditionType' property needs to be set according to the chosen model for each condition;
    In case of condition blocks (AND/OR), it is required for each of the inner-layer conditions as
    well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | LibraryConditionResponseEntity
     """


    return sync_detailed(
        client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | LibraryConditionResponseEntity]:
    """ Network Access - Creates a library condition.

     Network Access - Creates a library condition:
    <ul>
    <li> Library Condition has hierarchical structure which define a set of condition for which
    authentication and authorization policy rules could be match.</li>
    <li> Condition can be composed either from a single dictionary-attribute name and value pair using
    model <b>LibraryConditionAttributes</b>, or from a combination of 2 or more conditions with a
    logical relation (e.g AND/OR) using models: <b>LibraryConditionAndBlock</b> or
    <b>LibraryConditionOrBlock</b>.</li>
    <li> When using AND/OR blocks, the condition will include inner layers inside these blocks, these
    layers should be built using the inner condition models: <b>ConditionAttributes</b>,
    <b>ConditionAndBlock</b>, <b>ConditionOrBlock</b>; these represent dynamically built Conditions
    which do not get stored in the conditions Library, or using <b>ConditionReference</b>, which
    includes an ID of an existing condition which is in the library.</li>
    <li> The LibraryCondition models can only be used in the outer-most layer (root of the condition)
    and must always include the condition name.</li>
    <li> When using one of the 3 inner-layers condition models (<b>ConditionAttributes,
    ConditionAndBlock, ConditionOrBlock</b>), condition name cannot be included in the request, since
    these will not be stored in the conditions library, and used only as inner members of the root
    condition.</li>
    <li> When using <b>ConditionReference</b> model in inner layers, the condition name is not
    required.</li>
    <li> ConditionReference objects can also include a reference ID to a condition of type
    <b>TimeAndDate</b>.</li>
    <li> <b>NOTE:</b> The request body example provided in the Swagger UI is incomplete and cannot be
    used for creating a valid resource. Please refer to the 'Schema' section below, which offers details
    on the properties required to construct a valid request body for each condition model. Please note
    that the 'conditionType' property needs to be set according to the chosen model for each condition;
    In case of condition blocks (AND/OR), it is required for each of the inner-layer conditions as
    well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | LibraryConditionResponseEntity]
     """


    kwargs = _get_kwargs(
        body=body,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: Condition,
    x_request_id: str | Unset = UNSET,

) -> Error | LibraryConditionResponseEntity | None:
    """ Network Access - Creates a library condition.

     Network Access - Creates a library condition:
    <ul>
    <li> Library Condition has hierarchical structure which define a set of condition for which
    authentication and authorization policy rules could be match.</li>
    <li> Condition can be composed either from a single dictionary-attribute name and value pair using
    model <b>LibraryConditionAttributes</b>, or from a combination of 2 or more conditions with a
    logical relation (e.g AND/OR) using models: <b>LibraryConditionAndBlock</b> or
    <b>LibraryConditionOrBlock</b>.</li>
    <li> When using AND/OR blocks, the condition will include inner layers inside these blocks, these
    layers should be built using the inner condition models: <b>ConditionAttributes</b>,
    <b>ConditionAndBlock</b>, <b>ConditionOrBlock</b>; these represent dynamically built Conditions
    which do not get stored in the conditions Library, or using <b>ConditionReference</b>, which
    includes an ID of an existing condition which is in the library.</li>
    <li> The LibraryCondition models can only be used in the outer-most layer (root of the condition)
    and must always include the condition name.</li>
    <li> When using one of the 3 inner-layers condition models (<b>ConditionAttributes,
    ConditionAndBlock, ConditionOrBlock</b>), condition name cannot be included in the request, since
    these will not be stored in the conditions library, and used only as inner members of the root
    condition.</li>
    <li> When using <b>ConditionReference</b> model in inner layers, the condition name is not
    required.</li>
    <li> ConditionReference objects can also include a reference ID to a condition of type
    <b>TimeAndDate</b>.</li>
    <li> <b>NOTE:</b> The request body example provided in the Swagger UI is incomplete and cannot be
    used for creating a valid resource. Please refer to the 'Schema' section below, which offers details
    on the properties required to construct a valid request body for each condition model. Please note
    that the 'conditionType' property needs to be set according to the chosen model for each condition;
    In case of condition blocks (AND/OR), it is required for each of the inner-layer conditions as
    well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (Condition): <ul><li>Hierarchical structure which defines a set of conditions for
            which authentication or authorization policy rules could be matched.</li> <li>Logical
            operations(AND, OR) relationship between conditions are supported</li> <li>Each condition
            can have subconditions with relation to logical operations</li></ul>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | LibraryConditionResponseEntity
     """


    return (await asyncio_detailed(
        client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
