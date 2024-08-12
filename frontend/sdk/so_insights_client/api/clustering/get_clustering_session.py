from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.clustering_session import ClusteringSession
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    workspace_id: str,
    session_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/clustering/sessions/{session_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ClusteringSession, HTTPValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ClusteringSession.from_dict(response.json())

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
) -> Response[Union[ClusteringSession, HTTPValidationError]]:
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
) -> Response[Union[ClusteringSession, HTTPValidationError]]:
    """Get Clustering Session

     Get a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClusteringSession, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
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
) -> Optional[Union[ClusteringSession, HTTPValidationError]]:
    """Get Clustering Session

     Get a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClusteringSession, HTTPValidationError]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        session_id=session_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[ClusteringSession, HTTPValidationError]]:
    """Get Clustering Session

     Get a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClusteringSession, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[ClusteringSession, HTTPValidationError]]:
    """Get Clustering Session

     Get a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClusteringSession, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            session_id=session_id,
            client=client,
        )
    ).parsed
