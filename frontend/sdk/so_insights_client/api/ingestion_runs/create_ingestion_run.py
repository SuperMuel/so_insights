from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.ingestion_run import IngestionRun
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    *,
    ingestion_config_id: str,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    params: Dict[str, Any] = {}

    json_ingestion_config_id: str
    json_ingestion_config_id = ingestion_config_id
    params["ingestion_config_id"] = json_ingestion_config_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/workspaces/{workspace_id}/ingestion-runs/",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, IngestionRun]]:
    if response.status_code == 200:
        response_200 = IngestionRun.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, IngestionRun]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    ingestion_config_id: str,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, IngestionRun]]:
    """Create Ingestion Run

    Args:
        workspace_id (str):
        ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, IngestionRun]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        ingestion_config_id=ingestion_config_id,
        x_organization_id=x_organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    ingestion_config_id: str,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, IngestionRun]]:
    """Create Ingestion Run

    Args:
        workspace_id (str):
        ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, IngestionRun]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        client=client,
        ingestion_config_id=ingestion_config_id,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    ingestion_config_id: str,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, IngestionRun]]:
    """Create Ingestion Run

    Args:
        workspace_id (str):
        ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, IngestionRun]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        ingestion_config_id=ingestion_config_id,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    ingestion_config_id: str,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, IngestionRun]]:
    """Create Ingestion Run

    Args:
        workspace_id (str):
        ingestion_config_id (str):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, IngestionRun]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            client=client,
            ingestion_config_id=ingestion_config_id,
            x_organization_id=x_organization_id,
        )
    ).parsed
