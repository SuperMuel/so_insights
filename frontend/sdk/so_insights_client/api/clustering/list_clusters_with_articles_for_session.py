from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cluster_with_articles import ClusterWithArticles
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    session_id: str,
    *,
    n_articles: Union[Unset, int] = 5,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["n_articles"] = n_articles

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/clustering/sessions/{session_id}/clusters-with-articles",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, List["ClusterWithArticles"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ClusterWithArticles.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[HTTPValidationError, List["ClusterWithArticles"]]]:
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
    n_articles: Union[Unset, int] = 5,
) -> Response[Union[HTTPValidationError, List["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        n_articles (Union[Unset, int]):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, List['ClusterWithArticles']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        n_articles=n_articles,
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
    n_articles: Union[Unset, int] = 5,
) -> Optional[Union[HTTPValidationError, List["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        n_articles (Union[Unset, int]):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, List['ClusterWithArticles']]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        session_id=session_id,
        client=client,
        n_articles=n_articles,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    n_articles: Union[Unset, int] = 5,
) -> Response[Union[HTTPValidationError, List["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        n_articles (Union[Unset, int]):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, List['ClusterWithArticles']]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        n_articles=n_articles,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    session_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    n_articles: Union[Unset, int] = 5,
) -> Optional[Union[HTTPValidationError, List["ClusterWithArticles"]]]:
    """List Clusters With Articles

     List all clusters with their top N articles for a specific clustering session

    Args:
        workspace_id (str):
        session_id (str):
        n_articles (Union[Unset, int]):  Default: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, List['ClusterWithArticles']]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            session_id=session_id,
            client=client,
            n_articles=n_articles,
        )
    ).parsed
