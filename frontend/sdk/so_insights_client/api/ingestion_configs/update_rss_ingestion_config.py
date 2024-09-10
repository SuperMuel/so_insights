from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rss_ingestion_config import RssIngestionConfig
from ...models.rss_ingestion_config_update import RssIngestionConfigUpdate
from ...types import Response


def _get_kwargs(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    body: RssIngestionConfigUpdate,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/workspaces/{workspace_id}/ingestion-configs/rss/{rss_ingestion_config_id}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RssIngestionConfig]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = RssIngestionConfig.from_dict(response.json())

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
    body: RssIngestionConfigUpdate,
) -> Response[Union[HTTPValidationError, RssIngestionConfig]]:
    """Update Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        body (RssIngestionConfigUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RssIngestionConfig]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        rss_ingestion_config_id=rss_ingestion_config_id,
        body=body,
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
    body: RssIngestionConfigUpdate,
) -> Optional[Union[HTTPValidationError, RssIngestionConfig]]:
    """Update Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        body (RssIngestionConfigUpdate):

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
        body=body,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RssIngestionConfigUpdate,
) -> Response[Union[HTTPValidationError, RssIngestionConfig]]:
    """Update Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        body (RssIngestionConfigUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RssIngestionConfig]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        rss_ingestion_config_id=rss_ingestion_config_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    rss_ingestion_config_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RssIngestionConfigUpdate,
) -> Optional[Union[HTTPValidationError, RssIngestionConfig]]:
    """Update Rss Ingestion Config

    Args:
        workspace_id (str):
        rss_ingestion_config_id (str):
        body (RssIngestionConfigUpdate):

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
            body=body,
        )
    ).parsed
