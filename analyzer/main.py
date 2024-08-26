import asyncio
import logging
from datetime import datetime, timedelta

from src.cluster_overview_generator import ClusterOverviewGenerator
from src.evaluator import ClusterEvaluator
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
    cluster_evaluator = ClusterEvaluator(llm=init_chat_model("gpt-4o-mini"))

    analyzer = Analyzer(
        vector_repository=vector_repository,
        clustering_engine=clustering_engine,
        overview_generator=overview_generator,
        cluster_evaluator=cluster_evaluator,
    )

    return mongo_client, analyzer


@app.command()
def analyze(
    workspace_id: str,
    days: int = typer.Option(2, "--days", "-d", help="Number of days to analyze"),
):
    async def _clusterize():
        mongo_client, analyzer = await setup()

        workspace = await Workspace.get(workspace_id)

        if workspace is None:
            typer.echo("No cluster found for the given workspace.", err=True)
        else:
            await analyzer.analyse(
                workspace,
                data_start=datetime.now() - timedelta(days=days),
                data_end=datetime.now(),
            )

        mongo_client.close()

    asyncio.run(_clusterize())


@app.command()
def analyze_all(
    days: int = typer.Option(2, "--days", "-d", help="Number of days to analyze"),
):
    async def _clusterize():
        mongo_client, analyzer = await setup()

        workspaces = await Workspace.find_all().to_list()

        for workspace in workspaces:
            await analyzer.analyse(
                workspace,
                data_start=datetime.now() - timedelta(days=days),
                data_end=datetime.now(),
            )

        mongo_client.close()

    asyncio.run(_clusterize())


@app.command()
def generate_overviews(
    session_ids: list[str],
    only_missing: bool = typer.Option(
        False,
        "--only-missing",
        "-m",
        help="Generate overviews only for clusters without overviews",
    ),
):
    async def _generate_overviews():
        mongo_client, analyzer = await setup()

        for session_id in session_ids:
            session = await ClusteringSession.get(session_id)
            if not session:
                typer.echo(f"No session found for the given id: {session_id}", err=True)
                continue

            workspace = await Workspace.get(session.workspace_id)
            if not workspace:
                typer.echo(
                    f"No workspace found for the given session: {session_id}", err=True
                )
                continue

            generator = ClusterOverviewGenerator(llm=init_chat_model("gpt-4o-mini"))
            await generator.generate_overviews_for_session(
                session, only_missing=only_missing
            )
            typer.echo(f"Overviews generated for session: {session_id}")

        mongo_client.close()

    asyncio.run(_generate_overviews())


@app.command()
def evaluate(session_ids: list[str]):
    async def _evaluate():
        mongo_client, analyzer = await setup()

        for session_id in session_ids:
            session = await ClusteringSession.get(session_id)

            if session is None:
                typer.echo(f"No session found for the given id: {session_id}", err=True)
                continue

            evaluator = ClusterEvaluator(llm=init_chat_model("gpt-4o-mini"))
            await evaluator.evaluate_session(session)
            typer.echo(f"Evaluation completed for session: {session_id}")

        mongo_client.close()

    asyncio.run(_evaluate())


if __name__ == "__main__":
    load_dotenv()
    app()
