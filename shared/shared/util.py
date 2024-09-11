from typing import Any
from urllib.parse import urlparse


def validate_url(url: Any) -> str | None:
    """
    Validates the given URL.

    Args:
        url (Any): The URL to be validated.

    Returns:
        str | None: The validated URL if it is valid, otherwise None.
    """
    if not url:
        return None
    if not isinstance(url, str):
        return None
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return url
    return None
