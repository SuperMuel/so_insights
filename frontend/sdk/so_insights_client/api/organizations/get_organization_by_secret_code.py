from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.organization import Organization
from ...types import UNSET, Response


def _get_kwargs(
    *,
    code: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["code"] = code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/organizations/by-secret-code",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, Organization]]:
    if response.status_code == 200:
        response_200 = Organization.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, Organization]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: str,
) -> Response[Union[HTTPValidationError, Organization]]:
    """Get Organization By Secret Code

     Retrieve an organization by its secret code.
    Returns 404 if none found.

    Args:
        code (str): Organization secret code

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Organization]]
    """

    kwargs = _get_kwargs(
        code=code,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    code: str,
) -> Optional[Union[HTTPValidationError, Organization]]:
    """Get Organization By Secret Code

     Retrieve an organization by its secret code.
    Returns 404 if none found.

    Args:
        code (str): Organization secret code

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Organization]
    """

    return sync_detailed(
        client=client,
        code=code,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: str,
) -> Response[Union[HTTPValidationError, Organization]]:
    """Get Organization By Secret Code

     Retrieve an organization by its secret code.
    Returns 404 if none found.

    Args:
        code (str): Organization secret code

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Organization]]
    """

    kwargs = _get_kwargs(
        code=code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    code: str,
) -> Optional[Union[HTTPValidationError, Organization]]:
    """Get Organization By Secret Code

     Retrieve an organization by its secret code.
    Returns 404 if none found.

    Args:
        code (str): Organization secret code

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Organization]
    """

    return (
        await asyncio_detailed(
            client=client,
            code=code,
        )
    ).parsed