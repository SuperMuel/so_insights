from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cluster import Cluster
from ...models.http_validation_error import HTTPValidationError
from ...models.list_clusters_for_session_relevance_levels_type_0_item import (
    ListClustersForSessionRelevanceLevelsType0Item,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    session_id: str,
    *,
    relevance_levels: Union[None, Unset, list[ListClustersForSessionRelevanceLevelsType0Item]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    params: dict[str, Any] = {}

    json_relevance_levels: Union[None, Unset, list[str]]
    if isinstance(relevance_levels, Unset):
        json_relevance_levels = UNSET
    elif isinstance(relevance_levels, list):
        json_relevance_levels = []
        for relevance_levels_type_0_item_data in relevance_levels:
            relevance_levels_type_0_item = relevance_levels_type_0_item_data.value
            json_relevance_levels.append(relevance_levels_type_0_item)

    else:
        json_relevance_levels = relevance_levels
    params["relevance_levels"] = json_relevance_levels

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/clustering/sessions/{session_id}/clusters",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["Cluster"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Cluster.from_dict(response_200_item_data)

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
) -> Response[Union[HTTPValidationError, list["Cluster"]]]:
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
    relevance_levels: Union[None, Unset, list[ListClustersForSessionRelevanceLevelsType0Item]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["Cluster"]]]:
    """List Clusters

     List all clusters for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevance_levels (Union[None, Unset,
            list[ListClustersForSessionRelevanceLevelsType0Item]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['Cluster']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        relevance_levels=relevance_levels,
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
    relevance_levels: Union[None, Unset, list[ListClustersForSessionRelevanceLevelsType0Item]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["Cluster"]]]:
    """List Clusters

     List all clusters for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevance_levels (Union[None, Unset,
            list[ListClustersForSessionRelevanceLevelsType0Item]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['Cluster']]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        session_id=session_id,
        client=client,
        relevance_levels=relevance_levels,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    relevance_levels: Union[None, Unset, list[ListClustersForSessionRelevanceLevelsType0Item]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["Cluster"]]]:
    """List Clusters

     List all clusters for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevance_levels (Union[None, Unset,
            list[ListClustersForSessionRelevanceLevelsType0Item]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['Cluster']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        relevance_levels=relevance_levels,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    relevance_levels: Union[None, Unset, list[ListClustersForSessionRelevanceLevelsType0Item]] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["Cluster"]]]:
    """List Clusters

     List all clusters for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        relevance_levels (Union[None, Unset,
            list[ListClustersForSessionRelevanceLevelsType0Item]]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['Cluster']]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            session_id=session_id,
            client=client,
            relevance_levels=relevance_levels,
            x_organization_id=x_organization_id,
        )
    ).parsed
