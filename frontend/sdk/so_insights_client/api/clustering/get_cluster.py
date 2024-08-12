from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cluster import Cluster
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    workspace_id: str,
    cluster_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/clustering/clusters/{cluster_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Cluster, HTTPValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Cluster.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
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
) -> Response[Union[Cluster, HTTPValidationError]]:
    """Get Cluster

     Get a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Cluster, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        cluster_id=cluster_id,
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
) -> Optional[Union[Cluster, HTTPValidationError]]:
    """Get Cluster

     Get a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):

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
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    cluster_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Cluster, HTTPValidationError]]:
    """Get Cluster

     Get a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Cluster, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        cluster_id=cluster_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    cluster_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Cluster, HTTPValidationError]]:
    """Get Cluster

     Get a specific cluster

    Args:
        workspace_id (str):
        cluster_id (str):

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
        )
    ).parsed
