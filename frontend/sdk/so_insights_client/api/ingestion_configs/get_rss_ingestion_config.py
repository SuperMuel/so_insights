from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rss_ingestion_config import RssIngestionConfig
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/ingestion-configs/rss/{rss_ingestion_config_id}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RssIngestionConfig]]:
    if response.status_code == 200:
        response_200 = RssIngestionConfig.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RssIngestionConfig]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, RssIngestionConfig]]:
    """Get Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RssIngestionConfig]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        rss_ingestion_config_id=rss_ingestion_config_id,
        x_organization_id=x_organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, RssIngestionConfig]]:
    """Get Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RssIngestionConfig]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        rss_ingestion_config_id=rss_ingestion_config_id,
        client=client,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, RssIngestionConfig]]:
    """Get Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RssIngestionConfig]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        rss_ingestion_config_id=rss_ingestion_config_id,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, RssIngestionConfig]]:
    """Get Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RssIngestionConfig]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            rss_ingestion_config_id=rss_ingestion_config_id,
            client=client,
            x_organization_id=x_organization_id,
        )
    ).parsed
