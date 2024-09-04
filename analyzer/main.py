import asyncio
from beanie.odm.queries.update import (
    UpdateResponse,
)
import logging
from datetime import datetime, timedelta
from beanie.operators import Set

from src.cluster_overview_generator import ClusterOverviewGenerator
from src.evaluator import ClusterEvaluator
from src.session_summary_generator import SessionSummarizer
from src.starters_generator import ConversationStartersGenerator
import typer
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from src.analyzer import Analyzer
from src.analyzer_settings import AnalyzerSettings
from src.clustering_engine import ClusteringEngine
from src.vector_repository import PineconeVectorRepository
from langchain.chat_models import init_chat_model

from shared.db import get_client, my_init_beanie
from shared.models import AnalysisTask, Cluster, ClusteringSession, Workspace

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

    clustering_engine = ClusteringEngine()

    gpt_4o_mini = init_chat_model("gpt-4o-mini")

    overview_generator = ClusterOverviewGenerator(llm=gpt_4o_mini)
    cluster_evaluator = ClusterEvaluator(llm=gpt_4o_mini)
    starters_generator = ConversationStartersGenerator(llm=gpt_4o_mini)
    session_summarizer = SessionSummarizer(llm=gpt_4o_mini)

    analyzer = Analyzer(
        vector_repository=vector_repository,
        clustering_engine=clustering_engine,
        overview_generator=overview_generator,
        cluster_evaluator=cluster_evaluator,
        starters_generator=starters_generator,
        session_summarizer=session_summarizer,
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
            await analyzer.analyze_workspace(
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
            await analyzer.analyze_workspace(
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


@app.command()
def generate_starters() -> None:
    async def _generate_starters():
        mongo_client, analyzer = await setup()

        workspaces = await Workspace.find_all().to_list()

        for workspace in workspaces:
            await analyzer.starters_generator.generate_starters_for_workspace(workspace)

        mongo_client.close()

    asyncio.run(_generate_starters())


@app.command()
def summarize_session(session_id: str) -> None:
    async def _summarize_session():
        mongo_client, analyzer = await setup()

        session = await ClusteringSession.get(session_id)

        if session is None:
            typer.echo(f"No session found for the given id: {session_id}", err=True)
            return

        await analyzer.session_summarizer.generate_summary_for_session(session)

        mongo_client.close()

    asyncio.run(_summarize_session())


@app.command()
def repair():
    """Repair clusters by generating missing overviews and evaluations."""

    async def _repair():
        mongo_client, analyzer = await setup()

        llm = init_chat_model("gpt-4o-mini")

        # Get all clustering sessions
        sessions = await ClusteringSession.find_all().to_list()

        for session in sessions:
            typer.echo(f"Repairing session: {session.id} ({session.pretty_print()})")
            workspace = await Workspace.get(session.workspace_id)
            assert workspace

            # Get all clusters for the session
            clusters = await Cluster.find(Cluster.session_id == session.id).to_list()

            # Generate missing overviews
            clusters_without_overview = [c for c in clusters if not c.overview]
            if clusters_without_overview:
                typer.echo(
                    f"Generating {len(clusters_without_overview)} missing overviews"
                )
                generator = ClusterOverviewGenerator(llm=llm)
                await generator.generate_overviews(clusters_without_overview)

            # Generate missing evaluations
            clusters_without_evaluation = [c for c in clusters if not c.evaluation]
            if clusters_without_evaluation:
                typer.echo(
                    f"Generating {len(clusters_without_evaluation)} missing evaluations"
                )
                evaluator = ClusterEvaluator(llm=llm)
                await evaluator.evaluate_clusters(clusters_without_evaluation)
                await analyzer.starters_generator.generate_starters_for_workspace(
                    workspace
                )

            typer.echo(f"Updating relevancy counts for session: {session.id}")
            await analyzer.update_relevancy_counts(session)

            if not session.summary:
                typer.echo(f"Generating summary for session: {session.id}")
                await analyzer.session_summarizer.generate_summary_for_session(session)

            typer.echo(f"Completed repairs for session: {session.id}")

        mongo_client.close()

    asyncio.run(_repair())


@app.command()
def watch(
    interval: int = typer.Option(
        60, "--interval", "-i", help="Check interval in seconds"
    ),
):
    """Watch for pending analysis tasks and execute them."""

    async def _watch():
        mongo_client, analyzer = await setup()

        logger.info(f"Starting watch loop. Checking every {interval} seconds.")

        while True:
            task = await AnalysisTask.find_one(
                AnalysisTask.status == "pending"
            ).update_one(
                Set({AnalysisTask.status: "running"}),
                response_type=UpdateResponse.NEW_DOCUMENT,
            )

            assert isinstance(task, AnalysisTask) or task is None

            if not task:
                try:
                    await asyncio.sleep(interval)
                except KeyboardInterrupt:
                    logger.info("Detected keyboard interrupt. Exiting.")
                    break
                continue

            logger.info(f"Processing task {task.id} for workspace {task.workspace_id}")

            task.status = "running"  # TODO : find a way to ensure that at this point the task is not already being processed by another worker
            await task.save()

            workspace = await Workspace.get(task.workspace_id)
            assert workspace

            try:
                session = await analyzer.analyze_workspace(
                    workspace,
                    data_start=task.data_start,
                    data_end=task.data_end,
                )
                assert session
                task.status = "completed"
                task.session_id = session.id
                await task.save()

                logger.info(f"Completed task {task.id}")

            except Exception as e:
                logger.error(f"Error processing task {task.id}: {str(e)}")
                task.status = "failed"
                task.error = str(e)
                await task.save()

    asyncio.run(_watch())


if __name__ == "__main__":
    load_dotenv()
    app()
