import asyncio
import logging
from datetime import datetime, timedelta

from src.cluster_overview_generator import ClusterOverviewGenerator
from src.evaluator import Evaluator
import typer
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from src.analyzer import Analyzer
from src.analyzer_settings import AnalyzerSettings
from src.clustering_engine import ClusteringEngine
from src.vector_repository import PineconeVectorRepository
from langchain.chat_models import init_chat_model

from shared.db import get_client, my_init_beanie
from shared.models import ClusteringSession, Workspace

load_dotenv()

settings = AnalyzerSettings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = typer.Typer()


async def setup():
    mongo_client = get_client(settings.MONGODB_URI)
    await my_init_beanie(mongo_client)

    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX)
    vector_repository = PineconeVectorRepository(index)

    clustering_engine = ClusteringEngine(
        min_cluster_size=settings.DEFAULT_MIN_CLUSTER_SIZE,
        min_samples=settings.DEFAULT_MIN_SAMPLES,
    )
    overview_generator = ClusterOverviewGenerator(llm=init_chat_model("gpt-4o-mini"))

    analyzer = Analyzer(
        vector_repository=vector_repository,
        clustering_engine=clustering_engine,
        overview_generator=overview_generator,
    )

    return mongo_client, analyzer


@app.command()
def analyze(workspace_id: str):
    async def _clusterize():
        mongo_client, analyzer = await setup()

        workspace = await Workspace.get(workspace_id)

        if workspace is None:
            typer.echo("No cluster found for the given workspace.", err=True)
        else:
            await analyzer.analyse(
                workspace,
                data_start=datetime.now(),
                data_end=datetime.now() - timedelta(days=1),
            )

        mongo_client.close()

    asyncio.run(_clusterize())


if __name__ == "__main__":
    app()
