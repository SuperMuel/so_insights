from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.search_query_set import SearchQuerySet
from ...models.search_query_set_update import SearchQuerySetUpdate
from ...types import Response


def _get_kwargs(
    workspace_id: str,
    search_query_set_id: str,
    *,
    body: SearchQuerySetUpdate,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/workspaces/{workspace_id}/search-query-sets/{search_query_set_id}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, SearchQuerySet]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SearchQuerySet.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, SearchQuerySet]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    search_query_set_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchQuerySetUpdate,
) -> Response[Union[HTTPValidationError, SearchQuerySet]]:
    """Update Search Query Set

    Args:
        workspace_id (str):
        search_query_set_id (str):
        body (SearchQuerySetUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SearchQuerySet]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        search_query_set_id=search_query_set_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    search_query_set_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchQuerySetUpdate,
) -> Optional[Union[HTTPValidationError, SearchQuerySet]]:
    """Update Search Query Set

    Args:
        workspace_id (str):
        search_query_set_id (str):
        body (SearchQuerySetUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SearchQuerySet]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        search_query_set_id=search_query_set_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    search_query_set_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchQuerySetUpdate,
) -> Response[Union[HTTPValidationError, SearchQuerySet]]:
    """Update Search Query Set

    Args:
        workspace_id (str):
        search_query_set_id (str):
        body (SearchQuerySetUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SearchQuerySet]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        search_query_set_id=search_query_set_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    search_query_set_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SearchQuerySetUpdate,
) -> Optional[Union[HTTPValidationError, SearchQuerySet]]:
    """Update Search Query Set

    Args:
        workspace_id (str):
        search_query_set_id (str):
        body (SearchQuerySetUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SearchQuerySet]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            search_query_set_id=search_query_set_id,
            client=client,
            body=body,
        )
    ).parsed
