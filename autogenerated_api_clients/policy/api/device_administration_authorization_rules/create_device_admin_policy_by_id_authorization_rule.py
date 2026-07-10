from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.device_admin_authorization_rule_response_entity import DeviceAdminAuthorizationRuleResponseEntity
from ...models.error import Error
from ...models.rule_authorization_device_admin import RuleAuthorizationDeviceAdmin
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    policy_id: UUID,
    *,
    body: RuleAuthorizationDeviceAdmin,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/device-admin/policy-set/{policy_id}/authorization".format(policy_id=quote(str(policy_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DeviceAdminAuthorizationRuleResponseEntity | Error | None:
    if response.status_code == 201:
        response_201 = DeviceAdminAuthorizationRuleResponseEntity.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DeviceAdminAuthorizationRuleResponseEntity | Error]:
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
    body: RuleAuthorizationDeviceAdmin,
    x_request_id: str | Unset = UNSET,

) -> Response[DeviceAdminAuthorizationRuleResponseEntity | Error]:
    """ Device Admin - Create authorization rule.

     Device Admin - Create authorization rule:
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
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthorizationDeviceAdmin): Authorization rule for device admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceAdminAuthorizationRuleResponseEntity | Error]
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
    body: RuleAuthorizationDeviceAdmin,
    x_request_id: str | Unset = UNSET,

) -> DeviceAdminAuthorizationRuleResponseEntity | Error | None:
    """ Device Admin - Create authorization rule.

     Device Admin - Create authorization rule:
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
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthorizationDeviceAdmin): Authorization rule for device admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceAdminAuthorizationRuleResponseEntity | Error
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
    body: RuleAuthorizationDeviceAdmin,
    x_request_id: str | Unset = UNSET,

) -> Response[DeviceAdminAuthorizationRuleResponseEntity | Error]:
    """ Device Admin - Create authorization rule.

     Device Admin - Create authorization rule:
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
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthorizationDeviceAdmin): Authorization rule for device admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceAdminAuthorizationRuleResponseEntity | Error]
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
    body: RuleAuthorizationDeviceAdmin,
    x_request_id: str | Unset = UNSET,

) -> DeviceAdminAuthorizationRuleResponseEntity | Error | None:
    """ Device Admin - Create authorization rule.

     Device Admin - Create authorization rule:
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
        policy_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthorizationDeviceAdmin): Authorization rule for device admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceAdminAuthorizationRuleResponseEntity | Error
     """


    return (await asyncio_detailed(
        policy_id=policy_id,
client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
