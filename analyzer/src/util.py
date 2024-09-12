import asyncio
import logging
import aiohttp
from pydantic import HttpUrl
from shared.models import Article


logger = logging.getLogger(__name__)


async def get_first_valid_image(articles: list[Article]) -> HttpUrl | None:
    """
    Asynchronously retrieves the first valid image URL from a list of articles.

    This function iterates through the provided articles and checks each article's
    image URL for validity. It returns the first URL that successfully responds
    with an image content type.

    Args:
        articles (list[Article]): A list of Article objects to check for valid image URLs.

    Returns:
        HttpUrl | None: The first valid image URL found, or None if no valid image URL is found.
    """
    timeout = aiohttp.ClientTimeout(total=5)  # 5 seconds timeout for the entire request

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for article in articles:
            if not article.image:
                continue
            try:
                async with session.head(str(article.image)) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if content_type.startswith("image/"):
                            return article.image
            except aiohttp.ClientError:
                continue
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error while fetching image: {e}")
                continue
    return None
