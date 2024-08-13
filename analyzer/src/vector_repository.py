from pinecone.grpc.index_grpc import GRPCIndex
from pydantic import BaseModel
from itertools import batched


class ArticleEmbedding(BaseModel):
    id: str
    embedding: list[float]


class PineconeVectorRepository:
    def __init__(self, index: GRPCIndex) -> None:
        self.index = index

    def fetch_vectors(self, ids: list[str], namespace: str) -> list[ArticleEmbedding]:
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


if __name__ == "__main__":
    from pinecone.grpc import PineconeGRPC as Pinecone
    from src.analyzer_settings import AnalyzerSettings

    settings = AnalyzerSettings()

    # pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX)

    ids = ["667d1ef6fc45eb48396a6a0c"]
    response = index.fetch(ids, namespace="66a3a6374a283178ee5bc60a")

    _ids = [x["id"] for x in response["vectors"].values()]
    vectors = [x["values"] for x in response["vectors"].values()]

    assert _ids == ids

    repo = PineconeVectorRepository(index)

    vectors = repo.fetch_vectors(ids, namespace="66a3a6374a283178ee5bc60a")

    print(vectors)
