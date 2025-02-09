from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.topic_with_articles import TopicWithArticles
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    analysis_run_id: str,
    *,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/analysis-runs/{analysis_run_id}/topics-with-articles",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["TopicWithArticles"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = TopicWithArticles.from_dict(response_200_item_data)

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
) -> Response[Union[HTTPValidationError, list["TopicWithArticles"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    analysis_run_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["TopicWithArticles"]]]:
    """List Topics With Articles

     List all topics with their articles for a specific agentic analysis run.

    Only works for analysis runs of type AGENTIC.
    Raises HTTPException if the run is not an agentic analysis or has no result.

    Args:
        workspace_id (str):
        analysis_run_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['TopicWithArticles']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        analysis_run_id=analysis_run_id,
        x_organization_id=x_organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    analysis_run_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["TopicWithArticles"]]]:
    """List Topics With Articles

     List all topics with their articles for a specific agentic analysis run.

    Only works for analysis runs of type AGENTIC.
    Raises HTTPException if the run is not an agentic analysis or has no result.

    Args:
        workspace_id (str):
        analysis_run_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['TopicWithArticles']]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        analysis_run_id=analysis_run_id,
        client=client,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    analysis_run_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["TopicWithArticles"]]]:
    """List Topics With Articles

     List all topics with their articles for a specific agentic analysis run.

    Only works for analysis runs of type AGENTIC.
    Raises HTTPException if the run is not an agentic analysis or has no result.

    Args:
        workspace_id (str):
        analysis_run_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['TopicWithArticles']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        analysis_run_id=analysis_run_id,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    analysis_run_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["TopicWithArticles"]]]:
    """List Topics With Articles

     List all topics with their articles for a specific agentic analysis run.

    Only works for analysis runs of type AGENTIC.
    Raises HTTPException if the run is not an agentic analysis or has no result.

    Args:
        workspace_id (str):
        analysis_run_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['TopicWithArticles']]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            analysis_run_id=analysis_run_id,
            client=client,
            x_organization_id=x_organization_id,
        )
    ).parsed
