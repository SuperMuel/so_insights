import asyncio
from typing import Optional
from beanie.odm.queries.update import (
    UpdateResponse,
)
import logging
from datetime import datetime, timedelta
from beanie.operators import Set

from fastapi import FastAPI
from src.cluster_overview_generator import ClusterOverviewGenerator
from src.cluster_evaluator import ClusterEvaluator
from src.session_summary_generator import SessionSummarizer
from src.starters_generator import ConversationStartersGenerator
import typer
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from src.analyzer import Analyzer
from src.analyzer_settings import analyzer_settings
from src.clustering_engine import ClusteringEngine
from src.vector_repository import PineconeVectorRepository
from langchain.chat_models import init_chat_model

from shared.db import get_client, my_init_beanie
from shared.models import Cluster, ClusteringSession, Status, Workspace
import uvicorn

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = typer.Typer(no_args_is_help=True)


async def setup():
    mongo_client = get_client(analyzer_settings.MONGODB_URI.get_secret_value())
    await my_init_beanie(mongo_client)

    pc = Pinecone(api_key=analyzer_settings.PINECONE_API_KEY.get_secret_value())
    index = pc.Index(analyzer_settings.PINECONE_INDEX)
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
def create_analysis_tasks(
    workspace_ids: Optional[list[str]] = typer.Argument(
        None,
        help="List of workspace IDs to analyze. If not provided, all workspaces will be analyzed.",
    ),
    days: int = typer.Option(1, "--days", "-d", help="Number of days to analyze"),
):
    """
    Creates analysis tasks for specified workspaces or all workspaces.

    This command creates a ClusteringSession for each workspace, with a "Pending" status. The session will
    be processed by the watch command, which will run the clustering and analysis tasks.
    """

    async def _create_analysis_tasks():
        mongo_client, analyzer = await setup()

        if workspace_ids is None:
            workspaces = await Workspace.get_active_workspaces().to_list()
        else:
            workspaces = []
            for workspace_id in workspace_ids:
                workspace = await Workspace.get(workspace_id)
                if workspace:
                    workspaces.append(workspace)
                else:
                    typer.echo(
                        f"No workspace found for the given id: {workspace_id}", err=True
                    )

        for workspace in workspaces:
            if workspace is None:
                typer.echo("No cluster found for the given workspace.", err=True)
            else:
                assert workspace.id
                session = await ClusteringSession(
                    workspace_id=workspace.id,
                    data_start=datetime.now() - timedelta(days=days),
                    data_end=datetime.now(),
                    nb_days=days,
                ).save()
                typer.echo(f"Session {session.id} created for workspace {workspace.id}")

        mongo_client.close()

    asyncio.run(_create_analysis_tasks())


@app.command()
def generate_overviews(
    session_ids: list[str],
    only_missing: bool = typer.Option(
        False,
        "--only-missing",
        "-m",
        help="Generate overviews only for clusters without existing overviews",
    ),
):
    """
    Generate cluster overviews for the given session IDs. Use the --only-missing option to only generate overviews for
    clusters that don't already have them.
    """

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
    """
    Evaluates clusters of given session IDs. The clusters should have overviews generated before running this command.

    This will overwrite existing evaluations for the clusters.
    """

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
def generate_starters(
    workspace_ids: Optional[list[str]] = typer.Argument(
        None,
        help="List of workspace IDs to generate starters for. If not provided, starters will be generated for all workspaces.",
    ),
) -> None:
    """
    Generate conversation starters for the given workspace IDs. If no workspace IDs are provided, starters will be generated for all workspaces.

    This will fetch the latest clustering sessions of each workspace and generate conversation starters based on the most recent and relevant cluster overviews.
    """

    async def _generate_starters():
        mongo_client, analyzer = await setup()

        if workspace_ids is None:
            workspaces = await Workspace.get_active_workspaces().to_list()
        else:
            workspaces = []
            for workspace_id in workspace_ids:
                workspace = await Workspace.get(workspace_id)
                if workspace:
                    workspaces.append(workspace)
                else:
                    typer.echo(
                        f"No workspace found for the given id: {workspace_id}", err=True
                    )

        for workspace in workspaces:
            await analyzer.starters_generator.generate_starters_for_workspace(workspace)

        mongo_client.close()

    asyncio.run(_generate_starters())


@app.command()
def summarize_session(session_id: str) -> None:
    """
    Generate a summary for the given session ID.

    This will generate a summary for the session based on the most relevant clusters within the session.

    This will overwrite any existing summary for the session.
    """

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
    """
    This command attempts to repair clustering sessions by generating missing overviews, evaluations, and session summaries.
    It ensures that all clusters within a session are evaluated and summarized.
    Also generates conversation starters if missing or evaluations are updated.
    """

    async def _repair():
        mongo_client, analyzer = await setup()

        llm = init_chat_model("gpt-4o-mini")

        # Get all clustering sessions
        sessions = await ClusteringSession.find_all().to_list()

        for session in sessions:
            typer.echo(f"Repairing session: {session.id} ({session.pretty_print()})")
            workspace = await Workspace.get(session.workspace_id)
            assert workspace and session.id

            # Get all clusters for the session
            clusters = await Cluster.find(Cluster.session_id == session.id).to_list()

            evaluations_changed = False

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
                await evaluator.evaluate_clusters(
                    clusters_without_evaluation,
                    session_id=str(session.id),
                )
                evaluations_changed = True

            await analyzer.update_relevancy_counts(session)

            if not session.summary or clusters_without_evaluation:
                typer.echo(f"Generating summary for session: {session.id}")
                await analyzer.session_summarizer.generate_summary_for_session(session)

            if evaluations_changed or not (await workspace.get_last_starters()):
                typer.echo(
                    f"Generating conversation starters for workspace: {workspace.id}"
                )
                await analyzer.starters_generator.generate_starters_for_workspace(
                    workspace
                )

            typer.echo(f"Completed repairs for session: {session.id}")

        mongo_client.close()

    asyncio.run(_repair())


api = FastAPI()


@api.get("/")
async def root():
    return {
        "message": "Welcome to so-insights-analyzer",
        "analyzer_settings": analyzer_settings.model_dump(),
    }


@api.get("/healthz")
async def healthz():
    return {"status": "ok"}


async def run_server():
    config = uvicorn.Config(
        app=api, host="0.0.0.0", port=analyzer_settings.PORT, log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


@app.command()
def watch(
    interval: int = typer.Option(
        analyzer_settings.POLLING_INTERVAL_S,
        "--interval",
        "-i",
        help="Check interval in seconds",
    ),
    max_runtime: int = typer.Option(
        analyzer_settings.MAX_RUNTIME_S,
        "--max-runtime",
        "-r",
        help="Maximum runtime in seconds before exiting",
    ),
):
    """Watch for pending clustering sessions and execute them."""

    async def _watch():
        mongo_client, analyzer = await setup()

        logger.info(f"Starting watch loop. Will run for up to {max_runtime} seconds.")
        start_time = datetime.now()

        server_task = asyncio.create_task(run_server())
        try:
            while (datetime.now() - start_time).total_seconds() < max_runtime:
                logger.info("Checking for pending sessions")
                session = await ClusteringSession.find_one(
                    ClusteringSession.status == Status.pending
                ).update_one(
                    Set({ClusteringSession.status: Status.running}),
                    response_type=UpdateResponse.NEW_DOCUMENT,
                )

                assert isinstance(session, ClusteringSession) or session is None

                if not session:
                    await asyncio.sleep(interval)
                    if (datetime.now() - start_time).total_seconds() >= max_runtime:
                        logger.info("Reached maximum runtime. Exiting.")
                        break
                    continue

                logger.info(
                    f"Processing session {session.id} for workspace {session.workspace_id}"
                )

                updated_session = await analyzer.handle_session(session)
                logger.info(f"Completed session {updated_session.id}")

                if (datetime.now() - start_time).total_seconds() >= max_runtime:
                    logger.info("Reached maximum runtime. Exiting.")
                    break

        finally:
            logger.info("Watch function completed. Shutting down server.")
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
            mongo_client.close()

    asyncio.run(_watch())


if __name__ == "__main__":
    load_dotenv()
    app()
