import asyncio
from langchain_voyageai import VoyageAIEmbeddings

from ingester.src.ingester_settings import IngesterSettings


async def main():
    settings = IngesterSettings()
    embeddings = VoyageAIEmbeddings(  # type:ignore # Arguments missing for parameters "_client", "_aclient"PylancereportCallIssue
        voyage_api_key=settings.VOYAGE_API_KEY,
        model=settings.EMBEDDING_MODEL,
        batch_size=settings.EMBEDDING_BATCH_SIZE,
    )


if __name__ == "__main__":
    asyncio.run(main())
