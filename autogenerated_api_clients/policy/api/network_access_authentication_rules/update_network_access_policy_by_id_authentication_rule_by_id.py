from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.authentication_rule_response_entity import AuthenticationRuleResponseEntity
from ...models.error import Error
from ...models.rule_authentication import RuleAuthentication
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    policy_id: UUID,
    rule_id: UUID,
    *,
    body: RuleAuthentication,
    x_request_id: str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["X-Request-ID"] = x_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/network-access/policy-set/{policy_id}/authentication/{rule_id}".format(policy_id=quote(str(policy_id), safe=""),rule_id=quote(str(rule_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | AuthenticationRuleResponseEntity | Error | None:
    if response.status_code == 200:
        response_200 = AuthenticationRuleResponseEntity.from_dict(response.json())



        return response_200

    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | AuthenticationRuleResponseEntity | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy_id: UUID,
    rule_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleAuthentication,
    x_request_id: str | Unset = UNSET,

) -> Response[Any | AuthenticationRuleResponseEntity | Error]:
    """ Network Access - Update rule.

     Network Access - Update rule.

    Args:
        policy_id (UUID):
        rule_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthentication): Rule for authentication in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AuthenticationRuleResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        policy_id=policy_id,
rule_id=rule_id,
body=body,
x_request_id=x_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    policy_id: UUID,
    rule_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleAuthentication,
    x_request_id: str | Unset = UNSET,

) -> Any | AuthenticationRuleResponseEntity | Error | None:
    """ Network Access - Update rule.

     Network Access - Update rule.

    Args:
        policy_id (UUID):
        rule_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthentication): Rule for authentication in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | AuthenticationRuleResponseEntity | Error
     """


    return sync_detailed(
        policy_id=policy_id,
rule_id=rule_id,
client=client,
body=body,
x_request_id=x_request_id,

    ).parsed

async def asyncio_detailed(
    policy_id: UUID,
    rule_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleAuthentication,
    x_request_id: str | Unset = UNSET,

) -> Response[Any | AuthenticationRuleResponseEntity | Error]:
    """ Network Access - Update rule.

     Network Access - Update rule.

    Args:
        policy_id (UUID):
        rule_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthentication): Rule for authentication in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AuthenticationRuleResponseEntity | Error]
     """


    kwargs = _get_kwargs(
        policy_id=policy_id,
rule_id=rule_id,
body=body,
x_request_id=x_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    policy_id: UUID,
    rule_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RuleAuthentication,
    x_request_id: str | Unset = UNSET,

) -> Any | AuthenticationRuleResponseEntity | Error | None:
    """ Network Access - Update rule.

     Network Access - Update rule.

    Args:
        policy_id (UUID):
        rule_id (UUID):
        x_request_id (str | Unset):
        body (RuleAuthentication): Rule for authentication in Network Access/Device Admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | AuthenticationRuleResponseEntity | Error
     """


    return (await asyncio_detailed(
        policy_id=policy_id,
rule_id=rule_id,
client=client,
body=body,
x_request_id=x_request_id,

    )).parsed
