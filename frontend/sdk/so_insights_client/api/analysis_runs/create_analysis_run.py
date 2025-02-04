from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.analysis_run import AnalysisRun
from ...models.analysis_run_create import AnalysisRunCreate
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    *,
    body: AnalysisRunCreate,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/workspaces/{workspace_id}/analysis-runs/",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AnalysisRun, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = AnalysisRun.from_dict(response.json())

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
) -> Response[Union[AnalysisRun, HTTPValidationError]]:
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
    body: AnalysisRunCreate,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[AnalysisRun, HTTPValidationError]]:
    """Create Analysis Run

     Create a new pending analysis run

    Args:
        workspace_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (AnalysisRunCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AnalysisRun, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        body=body,
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
    body: AnalysisRunCreate,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[AnalysisRun, HTTPValidationError]]:
    """Create Analysis Run

     Create a new pending analysis run

    Args:
        workspace_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (AnalysisRunCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AnalysisRun, HTTPValidationError]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        client=client,
        body=body,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AnalysisRunCreate,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[AnalysisRun, HTTPValidationError]]:
    """Create Analysis Run

     Create a new pending analysis run

    Args:
        workspace_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (AnalysisRunCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AnalysisRun, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        body=body,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AnalysisRunCreate,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[AnalysisRun, HTTPValidationError]]:
    """Create Analysis Run

     Create a new pending analysis run

    Args:
        workspace_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (AnalysisRunCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AnalysisRun, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            client=client,
            body=body,
            x_organization_id=x_organization_id,
        )
    ).parsed
