import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_articles_sort_by import ListArticlesSortBy
from ...models.list_articles_sort_order import ListArticlesSortOrder
from ...models.paginated_response_article import PaginatedResponseArticle
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    *,
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    sort_by: Union[Unset, ListArticlesSortBy] = ListArticlesSortBy.DATE,
    sort_order: Union[Unset, ListArticlesSortOrder] = ListArticlesSortOrder.DESC,
    start_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    content_fetched: Union[None, Unset, bool] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_organization_id, Unset):
        headers["x-organization-id"] = x_organization_id

    params: dict[str, Any] = {}

    params["page"] = page

    params["per_page"] = per_page

    json_sort_by: Union[Unset, str] = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by.value

    params["sort_by"] = json_sort_by

    json_sort_order: Union[Unset, str] = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sort_order"] = json_sort_order

    json_start_date: Union[None, Unset, str]
    if isinstance(start_date, Unset):
        json_start_date = UNSET
    elif isinstance(start_date, datetime.date):
        json_start_date = start_date.isoformat()
    elif isinstance(start_date, datetime.datetime):
        json_start_date = start_date.isoformat()
    else:
        json_start_date = start_date
    params["start_date"] = json_start_date

    json_end_date: Union[None, Unset, str]
    if isinstance(end_date, Unset):
        json_end_date = UNSET
    elif isinstance(end_date, datetime.date):
        json_end_date = end_date.isoformat()
    elif isinstance(end_date, datetime.datetime):
        json_end_date = end_date.isoformat()
    else:
        json_end_date = end_date
    params["end_date"] = json_end_date

    json_content_fetched: Union[None, Unset, bool]
    if isinstance(content_fetched, Unset):
        json_content_fetched = UNSET
    else:
        json_content_fetched = content_fetched
    params["content_fetched"] = json_content_fetched

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/workspaces/{workspace_id}/articles",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PaginatedResponseArticle]]:
    if response.status_code == 200:
        response_200 = PaginatedResponseArticle.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PaginatedResponseArticle]]:
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
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    sort_by: Union[Unset, ListArticlesSortBy] = ListArticlesSortBy.DATE,
    sort_order: Union[Unset, ListArticlesSortOrder] = ListArticlesSortOrder.DESC,
    start_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    content_fetched: Union[None, Unset, bool] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, PaginatedResponseArticle]]:
    """List Articles

     List articles for a given workspace.

    Supports filtering, sorting, and pagination.

    Args:
        workspace_id (str):
        page (Union[Unset, int]):  Default: 1.
        per_page (Union[Unset, int]):  Default: 20.
        sort_by (Union[Unset, ListArticlesSortBy]):  Default: ListArticlesSortBy.DATE.
        sort_order (Union[Unset, ListArticlesSortOrder]):  Default: ListArticlesSortOrder.DESC.
        start_date (Union[None, Unset, datetime.date, datetime.datetime]):
        end_date (Union[None, Unset, datetime.date, datetime.datetime]):
        content_fetched (Union[None, Unset, bool]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PaginatedResponseArticle]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        start_date=start_date,
        end_date=end_date,
        content_fetched=content_fetched,
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
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    sort_by: Union[Unset, ListArticlesSortBy] = ListArticlesSortBy.DATE,
    sort_order: Union[Unset, ListArticlesSortOrder] = ListArticlesSortOrder.DESC,
    start_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    content_fetched: Union[None, Unset, bool] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, PaginatedResponseArticle]]:
    """List Articles

     List articles for a given workspace.

    Supports filtering, sorting, and pagination.

    Args:
        workspace_id (str):
        page (Union[Unset, int]):  Default: 1.
        per_page (Union[Unset, int]):  Default: 20.
        sort_by (Union[Unset, ListArticlesSortBy]):  Default: ListArticlesSortBy.DATE.
        sort_order (Union[Unset, ListArticlesSortOrder]):  Default: ListArticlesSortOrder.DESC.
        start_date (Union[None, Unset, datetime.date, datetime.datetime]):
        end_date (Union[None, Unset, datetime.date, datetime.datetime]):
        content_fetched (Union[None, Unset, bool]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PaginatedResponseArticle]
    """

    return sync_detailed(
        workspace_id=workspace_id,
        client=client,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        start_date=start_date,
        end_date=end_date,
        content_fetched=content_fetched,
        x_organization_id=x_organization_id,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    sort_by: Union[Unset, ListArticlesSortBy] = ListArticlesSortBy.DATE,
    sort_order: Union[Unset, ListArticlesSortOrder] = ListArticlesSortOrder.DESC,
    start_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    content_fetched: Union[None, Unset, bool] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, PaginatedResponseArticle]]:
    """List Articles

     List articles for a given workspace.

    Supports filtering, sorting, and pagination.

    Args:
        workspace_id (str):
        page (Union[Unset, int]):  Default: 1.
        per_page (Union[Unset, int]):  Default: 20.
        sort_by (Union[Unset, ListArticlesSortBy]):  Default: ListArticlesSortBy.DATE.
        sort_order (Union[Unset, ListArticlesSortOrder]):  Default: ListArticlesSortOrder.DESC.
        start_date (Union[None, Unset, datetime.date, datetime.datetime]):
        end_date (Union[None, Unset, datetime.date, datetime.datetime]):
        content_fetched (Union[None, Unset, bool]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PaginatedResponseArticle]]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        start_date=start_date,
        end_date=end_date,
        content_fetched=content_fetched,
        x_organization_id=x_organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 1,
    per_page: Union[Unset, int] = 20,
    sort_by: Union[Unset, ListArticlesSortBy] = ListArticlesSortBy.DATE,
    sort_order: Union[Unset, ListArticlesSortOrder] = ListArticlesSortOrder.DESC,
    start_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.date, datetime.datetime] = UNSET,
    content_fetched: Union[None, Unset, bool] = UNSET,
    x_organization_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, PaginatedResponseArticle]]:
    """List Articles

     List articles for a given workspace.

    Supports filtering, sorting, and pagination.

    Args:
        workspace_id (str):
        page (Union[Unset, int]):  Default: 1.
        per_page (Union[Unset, int]):  Default: 20.
        sort_by (Union[Unset, ListArticlesSortBy]):  Default: ListArticlesSortBy.DATE.
        sort_order (Union[Unset, ListArticlesSortOrder]):  Default: ListArticlesSortOrder.DESC.
        start_date (Union[None, Unset, datetime.date, datetime.datetime]):
        end_date (Union[None, Unset, datetime.date, datetime.datetime]):
        content_fetched (Union[None, Unset, bool]):
        x_organization_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PaginatedResponseArticle]
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            client=client,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            start_date=start_date,
            end_date=end_date,
            content_fetched=content_fetched,
            x_organization_id=x_organization_id,
        )
    ).parsed
