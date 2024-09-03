import aiohttp
import asyncio

import requests


class ReaderAPI:
    def __init__(self, token: str, base_url: str = "https://r.jina.ai"):
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.base_url = base_url

    def parse(self, page_url: str):
        url = f"{self.base_url}/{page_url}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    async def aparse(self, page_url: str):
        url = f"{self.base_url}/{page_url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.json()


async def main():
    url = "https://blog.langchain.dev/tag/case-studies/"
    # token = "jina_cb561bc887504bff9b7363d7a2dd895d-HJDt6fVAoaXb2Qjwv86lHl2XF8K"
    import getpass

    token = getpass.getpass("Enter your token: ")
    reader_api = ReaderAPI(token)
    response = await reader_api.parse(url)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
