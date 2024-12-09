from urllib.parse import urlparse
from pydantic_core import Url


def validate_url(url: str | Url | None) -> str | None:
    """
    Validates the given URL.

    Args:
        url (Any): The URL to be validated.

    Returns:
        str | None: The validated URL if it is valid, otherwise None.
    """
    if not url:
        return None

    if isinstance(url, Url):
        url = str(url)

    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return url
    return None
