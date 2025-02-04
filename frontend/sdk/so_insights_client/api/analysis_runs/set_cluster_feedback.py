from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cluster import Cluster
from ...models.cluster_feedback import ClusterFeedback
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    cluster_id: str,
    *,
    body: ClusterFeedback,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/workspaces/{workspace_id}/analysis-runs/clusters/{cluster_id}/feedback",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Cluster, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = Cluster.from_dict(response.json())

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
) -> Response[Union[Cluster, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    cluster_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ClusterFeedback,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[Cluster, HTTPValidationError]]:
    """Set Cluster Feedback

     Set or update feedback for a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (ClusterFeedback): Captures user feedback on the relevance or usefulness of a
            cluster.

            This simple model allows users to indicate whether they find a particular
            cluster of articles relevant or not. It's a way to incorporate human judgment
            into the system's organization of content, which can help improve the
            cluster evaluation process over time.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Cluster, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        cluster_id=cluster_id,
        body=body,
        x_organization_id=x_organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    cluster_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ClusterFeedback,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Cluster, HTTPValidationError]]:
    """Set Cluster Feedback

     Set or update feedback for a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (ClusterFeedback): Captures user feedback on the relevance or usefulness of a
            cluster.

            This simple model allows users to indicate whether they find a particular
            cluster of articles relevant or not. It's a way to incorporate human judgment
            into the system's organization of content, which can help improve the
            cluster evaluation process over time.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Cluster, HTTPValidationError]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        cluster_id=cluster_id,
        client=client,
        body=body,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    cluster_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ClusterFeedback,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[Cluster, HTTPValidationError]]:
    """Set Cluster Feedback

     Set or update feedback for a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (ClusterFeedback): Captures user feedback on the relevance or usefulness of a
            cluster.

            This simple model allows users to indicate whether they find a particular
            cluster of articles relevant or not. It's a way to incorporate human judgment
            into the system's organization of content, which can help improve the
            cluster evaluation process over time.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Cluster, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        cluster_id=cluster_id,
        body=body,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    cluster_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ClusterFeedback,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Cluster, HTTPValidationError]]:
    """Set Cluster Feedback

     Set or update feedback for a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):
        x_organization_id (Union[None, Unset, str]):
        body (ClusterFeedback): Captures user feedback on the relevance or usefulness of a
            cluster.

            This simple model allows users to indicate whether they find a particular
            cluster of articles relevant or not. It's a way to incorporate human judgment
            into the system's organization of content, which can help improve the
            cluster evaluation process over time.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Cluster, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            cluster_id=cluster_id,
            client=client,
            body=body,
            x_organization_id=x_organization_id,
        )
    ).parsed
