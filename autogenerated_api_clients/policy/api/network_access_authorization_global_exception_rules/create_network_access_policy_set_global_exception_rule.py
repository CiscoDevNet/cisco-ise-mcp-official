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
from ...models.network_access_authorization_rule_response_entity import NetworkAccessAuthorizationRuleResponseEntity
from ...models.rule_authorization_network_access import RuleAuthorizationNetworkAccess
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: RuleAuthorizationNetworkAccess,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/network-access/policy-set/global-exception",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | NetworkAccessAuthorizationRuleResponseEntity | None:
    if response.status_code == 201:
        response_201 = NetworkAccessAuthorizationRuleResponseEntity.from_dict(response.json())



        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | NetworkAccessAuthorizationRuleResponseEntity]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RuleAuthorizationNetworkAccess,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | NetworkAccessAuthorizationRuleResponseEntity]:
    """ Network Access - Create global exception authorization rule.

     Network Access - Create global exception authorization rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authoriztion
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
     <li> <b>NOTE:</b> The condition property in the request body example provided in the Swagger UI is
    incomplete and cannot be used for creating a valid resource. Please refer to the 'Schema' section
    below, which offers details on the properties required to construct a valid request body for each
    condition model. Please note that the 'conditionType' property needs to be set according to the
    chosen model for each condition; In case of condition blocks (AND/OR), it is required for each of
    the inner-layer conditions as well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (RuleAuthorizationNetworkAccess): Authorization rule for network access

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NetworkAccessAuthorizationRuleResponseEntity]
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
    body: RuleAuthorizationNetworkAccess,
    x_request_id: str | Unset = UNSET,

) -> Error | NetworkAccessAuthorizationRuleResponseEntity | None:
    """ Network Access - Create global exception authorization rule.

     Network Access - Create global exception authorization rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authoriztion
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
     <li> <b>NOTE:</b> The condition property in the request body example provided in the Swagger UI is
    incomplete and cannot be used for creating a valid resource. Please refer to the 'Schema' section
    below, which offers details on the properties required to construct a valid request body for each
    condition model. Please note that the 'conditionType' property needs to be set according to the
    chosen model for each condition; In case of condition blocks (AND/OR), it is required for each of
    the inner-layer conditions as well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (RuleAuthorizationNetworkAccess): Authorization rule for network access

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NetworkAccessAuthorizationRuleResponseEntity
     """


    return sync_detailed(
        client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RuleAuthorizationNetworkAccess,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | NetworkAccessAuthorizationRuleResponseEntity]:
    """ Network Access - Create global exception authorization rule.

     Network Access - Create global exception authorization rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authoriztion
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
     <li> <b>NOTE:</b> The condition property in the request body example provided in the Swagger UI is
    incomplete and cannot be used for creating a valid resource. Please refer to the 'Schema' section
    below, which offers details on the properties required to construct a valid request body for each
    condition model. Please note that the 'conditionType' property needs to be set according to the
    chosen model for each condition; In case of condition blocks (AND/OR), it is required for each of
    the inner-layer conditions as well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (RuleAuthorizationNetworkAccess): Authorization rule for network access

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NetworkAccessAuthorizationRuleResponseEntity]
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
    body: RuleAuthorizationNetworkAccess,
    x_request_id: str | Unset = UNSET,

) -> Error | NetworkAccessAuthorizationRuleResponseEntity | None:
    """ Network Access - Create global exception authorization rule.

     Network Access - Create global exception authorization rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authoriztion
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
     <li> <b>NOTE:</b> The condition property in the request body example provided in the Swagger UI is
    incomplete and cannot be used for creating a valid resource. Please refer to the 'Schema' section
    below, which offers details on the properties required to construct a valid request body for each
    condition model. Please note that the 'conditionType' property needs to be set according to the
    chosen model for each condition; In case of condition blocks (AND/OR), it is required for each of
    the inner-layer conditions as well.</li>
    </ul>

    Args:
        x_request_id (str | Unset):
        body (RuleAuthorizationNetworkAccess): Authorization rule for network access

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NetworkAccessAuthorizationRuleResponseEntity
     """


    return (await asyncio_detailed(
        client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
