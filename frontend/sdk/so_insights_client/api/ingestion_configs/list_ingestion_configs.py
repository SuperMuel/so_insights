from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rss_ingestion_config import RssIngestionConfig
from ...models.search_ingestion_config import SearchIngestionConfig
from ...types import Response


def _get_kwargs(
    workspace_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/ingestion-configs/",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, List[Union["RssIngestionConfig", "SearchIngestionConfig"]]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:

            def _parse_response_200_item(data: object) -> Union["RssIngestionConfig", "SearchIngestionConfig"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    response_200_item_type_0 = SearchIngestionConfig.from_dict(data)

                    return response_200_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_item_type_1 = RssIngestionConfig.from_dict(data)

                return response_200_item_type_1

            response_200_item = _parse_response_200_item(response_200_item_data)

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
) -> Response[Union[HTTPValidationError, List[Union["RssIngestionConfig", "SearchIngestionConfig"]]]]:
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
) -> Response[Union[HTTPValidationError, List[Union["RssIngestionConfig", "SearchIngestionConfig"]]]]:
    """List Ingestion Configs

    Args:
        workspace_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, List[Union['RssIngestionConfig', 'SearchIngestionConfig']]]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[HTTPValidationError, List[Union["RssIngestionConfig", "SearchIngestionConfig"]]]]:
    """List Ingestion Configs

    Args:
        workspace_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, List[Union['RssIngestionConfig', 'SearchIngestionConfig']]]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[HTTPValidationError, List[Union["RssIngestionConfig", "SearchIngestionConfig"]]]]:
    """List Ingestion Configs

    Args:
        workspace_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, List[Union['RssIngestionConfig', 'SearchIngestionConfig']]]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[HTTPValidationError, List[Union["RssIngestionConfig", "SearchIngestionConfig"]]]]:
    """List Ingestion Configs

    Args:
        workspace_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, List[Union['RssIngestionConfig', 'SearchIngestionConfig']]]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            client=client,
        )
    ).parsed
