from langchain_pinecone import PineconeVectorStore
from typing import Callable
from itertools import batched
from langchain_core.documents import Document
from src.mongo_db_operations import mark_articles_as_vector_indexed
from langchain_core.embeddings import Embeddings

import logging

from beanie import PydanticObjectId

from shared.models import Article, Workspace

from src.ingester_settings import ingester_settings


logger = logging.getLogger(__name__)


PineconeIndexGetter = Callable[[str | PydanticObjectId], PineconeVectorStore]


def article_to_document(article: Article) -> Document:
    """
    Converts an Article object to a langchain Document object suitable for vector indexing.

    This function creates a Document object with the article's title and body as the main content,
    and includes additional metadata such as URL, timestamps, etc.

    Args:
        article (Article): The Article object to be converted.

    Returns:
        Document: A Document object ready for vector indexing.
    """
    return Document(
        page_content=f"{article.title}\n{article.body}",
        id=str(article.id),
        metadata={
            "title": article.title,
            "url": str(article.url),
            "body": article.body,
            "found_at": article.found_at.timestamp(),
            "date": article.date.timestamp(),
        },
    )


def get_pinecone_index(
    namespace: str | PydanticObjectId,
    embeddings: Embeddings,
) -> PineconeVectorStore:
    """
    Creates and returns a PineconeVectorStore object for a specific namespace.

    Args:
        namespace (str | PydanticObjectId): The namespace (usually a workspace ID) for the Pinecone index.
        embeddings (Embeddings): The embedding model to use for vectorization.

    Returns:
        PineconeVectorStore: A configured PineconeVectorStore object.
    """
    return PineconeVectorStore(
        pinecone_api_key=ingester_settings.PINECONE_API_KEY,
        index_name=ingester_settings.PINECONE_INDEX,
        embedding=embeddings,
        namespace=str(namespace),
    )


async def sync_workspace_with_vector_db(
    workspace: Workspace,
    index: PineconeVectorStore,
    batch_size: int = 1000,
    force: bool = False,
):
    """
    Updates or inserts articles from a specific workspace into the vector database.

    This function can either update all articles (if force=True) or only those not yet indexed.
    It processes articles in batches to manage memory usage and performance, adding them to
    the Pinecone index and marking them as indexed in MongoDB.

    Args:
        workspace (Workspace): The workspace object containing the articles to upsert.
        index (PineconeVectorStore): The Pinecone index to upsert articles into.
        batch_size (int, optional): The number of articles to process in each batch.
        force (bool, optional): If True, updates all articles regardless of their current index status.
                                Defaults to False. Use this option in case of inconsistencies between
                                MongoDB and the vector database.
    """
    assert workspace.id
    logger.info(
        f"Syncing workspace {workspace.id} ({workspace.name}) with vector database. {force=}"
    )

    articles = await Article.find(
        Article.workspace_id == workspace.id,
        *([Article.vector_indexed == False] if not force else []),  # noqa: E712
    ).to_list()

    logger.info(
        f"Found {len(articles)} not indexed articles for workspace {workspace.id}"
    )

    nb_batches = len(articles) // batch_size + 1

    for i, batch in enumerate(batched(articles, batch_size)):
        logger.info(
            f"Upserting articles for workspace {workspace.id} ({i + 1}/{nb_batches})"
        )
        documents = [article_to_document(article) for article in batch]
        await index.aadd_documents(
            documents, ids=[str(article.id) for article in batch]
        )
        await mark_articles_as_vector_indexed(list(batch))

    logger.info(f"Finished upserting articles for workspace {workspace.id}")
