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
from ...models.mfa_rule_response_entity import MfaRuleResponseEntity
from ...models.rule_mfa import RuleMfa
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    policy_id: UUID,
    *,
    body: RuleMfa,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/device-admin/policy-set/{policy_id}/mfa".format(policy_id=quote(str(policy_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | MfaRuleResponseEntity | None:
    if response.status_code == 201:
        response_201 = MfaRuleResponseEntity.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | MfaRuleResponseEntity]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleMfa,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | MfaRuleResponseEntity]:
    """ Device Admin - Create MFA rule.

     Device Admin - Create MFA rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authentication
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
    </ul>

    Args:
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleMfa): Rule for MFA in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MfaRuleResponseEntity]
     """


    kwargs = _get_kwargs(
        policy_id=policy_id,
body=body,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    policy_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleMfa,
    x_request_id: str | Unset = UNSET,

) -> Error | MfaRuleResponseEntity | None:
    """ Device Admin - Create MFA rule.

     Device Admin - Create MFA rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authentication
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
    </ul>

    Args:
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleMfa): Rule for MFA in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MfaRuleResponseEntity
     """


    return sync_detailed(
        policy_id=policy_id,
client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    policy_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleMfa,
    x_request_id: str | Unset = UNSET,

) -> Response[Error | MfaRuleResponseEntity]:
    """ Device Admin - Create MFA rule.

     Device Admin - Create MFA rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authentication
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
    </ul>

    Args:
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleMfa): Rule for MFA in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MfaRuleResponseEntity]
     """


    kwargs = _get_kwargs(
        policy_id=policy_id,
body=body,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    policy_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleMfa,
    x_request_id: str | Unset = UNSET,

) -> Error | MfaRuleResponseEntity | None:
    """ Device Admin - Create MFA rule.

     Device Admin - Create MFA rule:
    <ul>
    <li> Rule must include name and condition. </li>
    <li> Condition has hierarchical structure which define a set of conditions for which authentication
    policy rule could be match. </li>
    <li> Condition can be either reference to a stored Library condition, using model
    <b>ConditionReference</b> </li>
    or dynamically built conditions which are not stored in the conditions Library, using models
    <b>ConditionAttributes, ConditionAndBlock, ConditionOrBlock</b>. </li>
    </ul>

    Args:
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleMfa): Rule for MFA in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MfaRuleResponseEntity
     """


    return (await asyncio_detailed(
        policy_id=policy_id,
client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
