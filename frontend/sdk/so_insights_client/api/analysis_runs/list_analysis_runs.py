from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.analysis_run import AnalysisRun
from ...models.http_validation_error import HTTPValidationError
from ...models.status import Status
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    *,
    statuses: Union[None, Unset, list[Status]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    params: dict[str, Any] = {}

    json_statuses: Union[None, Unset, list[str]]
    if isinstance(statuses, Unset):
        json_statuses = UNSET
    elif isinstance(statuses, list):
        json_statuses = []
        for statuses_type_0_item_data in statuses:
            statuses_type_0_item = statuses_type_0_item_data.value
            json_statuses.append(statuses_type_0_item)

    else:
        json_statuses = statuses
    params["statuses"] = json_statuses

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/analysis-runs/",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["AnalysisRun"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AnalysisRun.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, list["AnalysisRun"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    statuses: Union[None, Unset, list[Status]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["AnalysisRun"]]]:
    """List Analysis Runs

     List all analysis runs for a workspace

    Args:
        workspace_id (str):
        statuses (Union[None, Unset, list[Status]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['AnalysisRun']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        statuses=statuses,
        x_organization_id=x_organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    statuses: Union[None, Unset, list[Status]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["AnalysisRun"]]]:
    """List Analysis Runs

     List all analysis runs for a workspace

    Args:
        workspace_id (str):
        statuses (Union[None, Unset, list[Status]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['AnalysisRun']]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        client=client,
        statuses=statuses,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    statuses: Union[None, Unset, list[Status]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["AnalysisRun"]]]:
    """List Analysis Runs

     List all analysis runs for a workspace

    Args:
        workspace_id (str):
        statuses (Union[None, Unset, list[Status]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['AnalysisRun']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        statuses=statuses,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    statuses: Union[None, Unset, list[Status]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["AnalysisRun"]]]:
    """List Analysis Runs

     List all analysis runs for a workspace

    Args:
        workspace_id (str):
        statuses (Union[None, Unset, list[Status]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['AnalysisRun']]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            client=client,
            statuses=statuses,
            x_organization_id=x_organization_id,
        )
    ).parsed
