from datetime import UTC, datetime
from urllib.parse import urlparse
from pydantic import HttpUrl
from pydantic_core import Url


# TODO auto change update_at like in https://github.com/naoTimesdev/showtimes/blob/79ed15aa647c6fb8ee9a1f694b54d90a5ed7dda0/showtimes/models/database.py#L24
def utc_datetime_factory():
    return datetime.now(UTC)


def validate_url(url: str | Url | HttpUrl | None) -> HttpUrl | None:
    """
    Validates the given URL.

    Args:
        url (Any): The URL to be validated.

    Returns:
        str | None: The validated URL if it is valid, otherwise None.
    """
    if not url:
        return None

    if isinstance(url, Url | HttpUrl):
        return HttpUrl(str(url))

    try:
        url = HttpUrl(url)
        return url
    except Exception:
        pass
