import asyncio
import logging
import aiohttp
from pydantic import HttpUrl
from shared.models import Article


logger = logging.getLogger(__name__)


async def get_first_valid_image(articles: list[Article]) -> HttpUrl | None:
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
