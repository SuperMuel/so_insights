from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cluster_with_articles import ClusterWithArticles
from ...models.http_validation_error import HTTPValidationError
from ...models.relevancy_filter import RelevancyFilter
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    session_id: str,
    *,
    relevancy_filter: Union[Unset, RelevancyFilter] = RelevancyFilter.ALL,
    n_articles: Union[Unset, int] = 5,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    params: dict[str, Any] = {}

    json_relevancy_filter: Union[Unset, str] = UNSET
    if not isinstance(relevancy_filter, Unset):
        json_relevancy_filter = relevancy_filter.value

    params["relevancy_filter"] = json_relevancy_filter

    params["n_articles"] = n_articles

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/clustering/sessions/{session_id}/clusters-with-articles",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["ClusterWithArticles"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ClusterWithArticles.from_dict(response_200_item_data)

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
) -> Response[Union[HTTPValidationError, list["ClusterWithArticles"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    relevancy_filter: Union[Unset, RelevancyFilter] = RelevancyFilter.ALL,
    n_articles: Union[Unset, int] = 5,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevancy_filter (Union[Unset, RelevancyFilter]):  Default: RelevancyFilter.ALL.
        n_articles (Union[Unset, int]):  Default: 5.
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ClusterWithArticles']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        relevancy_filter=relevancy_filter,
        n_articles=n_articles,
        x_organization_id=x_organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    relevancy_filter: Union[Unset, RelevancyFilter] = RelevancyFilter.ALL,
    n_articles: Union[Unset, int] = 5,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevancy_filter (Union[Unset, RelevancyFilter]):  Default: RelevancyFilter.ALL.
        n_articles (Union[Unset, int]):  Default: 5.
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ClusterWithArticles']]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        session_id=session_id,
        client=client,
        relevancy_filter=relevancy_filter,
        n_articles=n_articles,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    relevancy_filter: Union[Unset, RelevancyFilter] = RelevancyFilter.ALL,
    n_articles: Union[Unset, int] = 5,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevancy_filter (Union[Unset, RelevancyFilter]):  Default: RelevancyFilter.ALL.
        n_articles (Union[Unset, int]):  Default: 5.
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ClusterWithArticles']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        relevancy_filter=relevancy_filter,
        n_articles=n_articles,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    relevancy_filter: Union[Unset, RelevancyFilter] = RelevancyFilter.ALL,
    n_articles: Union[Unset, int] = 5,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevancy_filter (Union[Unset, RelevancyFilter]):  Default: RelevancyFilter.ALL.
        n_articles (Union[Unset, int]):  Default: 5.
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ClusterWithArticles']]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            session_id=session_id,
            client=client,
            relevancy_filter=relevancy_filter,
            n_articles=n_articles,
            x_organization_id=x_organization_id,
        )
    ).parsed
