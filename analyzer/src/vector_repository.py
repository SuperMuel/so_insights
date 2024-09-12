from pinecone.grpc.index_grpc import GRPCIndex
from pydantic import BaseModel
from itertools import batched


class ArticleEmbedding(BaseModel):
    """
    Represents an article's embedding in vector space.

    Attributes:
        id (str): The unique identifier of the article.
        embedding (list[float]): The vector representation of the article.
    """

    id: str
    embedding: list[float]


class PineconeVectorRepository:
    """
    A repository for fetching article embeddings from a Pinecone vector database.

    This class provides methods to retrieve article embeddings in batches,
    which is useful for efficient querying of large datasets.
    """

    def __init__(self, index: GRPCIndex) -> None:
        self.index = index

    def fetch_vectors(self, ids: list[str], namespace: str) -> list[ArticleEmbedding]:
        """
        Fetch article embeddings from the Pinecone index.

        This method retrieves embeddings for the given article IDs in batches
        to optimize performance when dealing with large numbers of articles.

        Args:
            ids (list[str]): List of article IDs to fetch embeddings for.
            namespace (str): The namespace in the Pinecone index to query.

        Returns:
            list[ArticleEmbedding]: A list of ArticleEmbedding objects containing
                                    the fetched embeddings.

        """

        all_ids: list[str] = []
        all_vectors: list[list[float]] = []

        BATCH_SIZE = 1000

        for batch_ids in batched(ids, BATCH_SIZE):
            response = self.index.fetch(list(batch_ids), namespace=namespace)
            all_ids.extend([x["id"] for x in response["vectors"].values()])
            all_vectors.extend([x["values"] for x in response["vectors"].values()])

        # Ensure we've fetched all requested IDs
        assert len(set(all_ids)) == len(set(ids))
        assert len(all_vectors) == len(ids)

        return [
            ArticleEmbedding(id=id, embedding=vector)
            for id, vector in zip(all_ids, all_vectors)
        ]
