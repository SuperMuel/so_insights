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
from src.clustering_analysis_generator import ClusteringAnalysisSummarizer
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
from shared.models import (
    AnalysisRun,
    AnalysisType,
    Cluster,
    ClusteringAnalysisParams,
    ClusteringAnalysisResult,
    Status,
    Workspace,
)
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
    clustering_analysis_summarizer = ClusteringAnalysisSummarizer(llm=gpt_4o_mini)

    analyzer = Analyzer(
        vector_repository=vector_repository,
        clustering_engine=clustering_engine,
        overview_generator=overview_generator,
        cluster_evaluator=cluster_evaluator,
        starters_generator=starters_generator,
        clustering_summarizer=clustering_analysis_summarizer,
    )

    return mongo_client, analyzer


@app.command()
def create_clustering_analysis_tasks(
    workspace_ids: Optional[list[str]] = typer.Argument(
        None,
        help="List of workspace IDs to analyze. If not provided, all workspaces will be analyzed.",
    ),
    days: int = typer.Option(1, "--days", "-d", help="Number of days to analyze"),
):
    """
    Creates analysis tasks for specified workspaces or all workspaces.

    This command creates a ClusteringAnalysisRun for each workspace, with a "Pending" status. The run will
    be processed by the watch command, which will run the clustering and analysis tasks.
    """

    async def _create_clustering_analysis_tasks():
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
                run = await AnalysisRun(
                    workspace_id=workspace.id,
                    data_start=datetime.now() - timedelta(days=days),
                    data_end=datetime.now(),
                    analysis_type=AnalysisType.CLUSTERING,
                    params=ClusteringAnalysisParams(
                        hdbscan_settings=workspace.hdbscan_settings,
                    ),
                ).save()
                typer.echo(f"Run {run.id} created for workspace {workspace.id}")

        mongo_client.close()

    asyncio.run(_create_clustering_analysis_tasks())


@app.command()
def generate_overviews(
    clustering_runs_ids: list[str],
    only_missing: bool = typer.Option(
        False,
        "--only-missing",
        "-m",
        help="Generate overviews only for clusters without existing overviews",
    ),
):
    """
    Generate cluster overviews for the given run IDs. Use the --only-missing option to only generate overviews for
    clusters that don't already have them.
    """

    async def _generate_overviews():
        mongo_client, analyzer = await setup()

        for run_id in clustering_runs_ids:
            run = await AnalysisRun.get(run_id)
            if not run:
                typer.echo(f"No run found for the given id: {run_id}", err=True)
                continue

            if run.analysis_type != AnalysisType.CLUSTERING:
                raise ValueError(
                    f"This analysis run is not a clustering AnalysisRun: {run_id}"
                )

            workspace = await Workspace.get(run.workspace_id)
            if not workspace:
                typer.echo(f"No workspace found for the given run: {run_id}", err=True)
                continue

            generator = ClusterOverviewGenerator(llm=init_chat_model("gpt-4o-mini"))

            await generator.generate_overviews_for_clustering_run(
                run, only_missing=only_missing
            )
            typer.echo(f"Overviews generated for run: {run_id}")

        mongo_client.close()

    asyncio.run(_generate_overviews())


@app.command()
def evaluate(runs_ids: list[str]):
    """
    Evaluates clusters of given clustering runs IDs. The clusters should have overviews generated before running this command.

    This will overwrite existing evaluations for the clusters.
    """

    async def _evaluate():
        mongo_client, analyzer = await setup()

        for run_id in runs_ids:
            run = await AnalysisRun.get(run_id)

            if run is None:
                typer.echo(f"No run found for the given id: {run_id}", err=True)
                continue

            if run.analysis_type != AnalysisType.CLUSTERING:
                typer.echo(
                    f"This analysis run is not a clustering AnalysisRun: {run_id}",
                    err=True,
                )
                continue

            evaluator = ClusterEvaluator(llm=init_chat_model("gpt-4o-mini"))
            await evaluator.evaluate_clustering_run(run)
            typer.echo(f"Evaluation completed for run: {run_id}")

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

    This will fetch the latest analysis runs of each workspace and generate conversation starters based on the most recent and relevant cluster overviews, or the latest report.
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
def summarize_clustering_run(run_id: str) -> None:
    """
    Generate a summary for the given clustering run ID.

    This will generate a summary for the run based on the most relevant clusters within the run.

    This will overwrite any existing summary for the run.
    """

    async def _summarize_run():
        mongo_client, analyzer = await setup()

        run = await AnalysisRun.get(run_id)

        if run is None:
            typer.echo(f"No run found for the given id: {run_id}", err=True)
            return

        if run.analysis_type != AnalysisType.CLUSTERING:
            typer.echo(
                f"This analysis run is not a clustering AnalysisRun: {run_id}",
                err=True,
            )
            return

        await (
            analyzer.clustering_analysis_summarizer.generate_summary_for_clustering_run(
                run
            )
        )

        mongo_client.close()

    asyncio.run(_summarize_run())


@app.command()
def repair():
    """
    This command attempts to repair clustering runs by generating missing overviews, evaluations, and run summaries.
    It ensures that all clusters within a run are evaluated and summarized.
    Also generates conversation starters if missing or evaluations are updated.
    """

    async def _repair():
        mongo_client, analyzer = await setup()

        llm = init_chat_model("gpt-4o-mini")

        # Get all clustering runs
        runs = await AnalysisRun.find_all().to_list()

        for run in runs:
            typer.echo(f"Repairing run: {run.id} ({run.pretty_print()})")
            workspace = await Workspace.get(run.workspace_id)
            assert workspace and run.id

            if run.analysis_type != AnalysisType.CLUSTERING:
                typer.echo(
                    f"This analysis run is not a clustering AnalysisRun: {run.id}",
                    err=True,
                )
                continue

            # Get all clusters for the run
            clusters = await Cluster.find(Cluster.session_id == run.id).to_list()

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
                    run_id=str(run.id),
                )
                evaluations_changed = True

            await analyzer.update_relevancy_counts(run)

            result = run.result

            assert isinstance(result, ClusteringAnalysisResult)

            if not result.summary or evaluations_changed:
                typer.echo(f"Generating summary for run: {run.id}")
                await analyzer.clustering_analysis_summarizer.generate_summary_for_clustering_run(
                    run
                )

            if evaluations_changed or not (await workspace.get_last_starters()):
                typer.echo(
                    f"Generating conversation starters for workspace: {workspace.id}"
                )
                await analyzer.starters_generator.generate_starters_for_workspace(
                    workspace
                )

            typer.echo(f"Completed repairs for run: {run.id}")

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
    """Watch for pending analysis runs and execute them."""

    async def _watch():
        mongo_client, analyzer = await setup()

        logger.info(f"Starting watch loop. Will run for up to {max_runtime} seconds.")
        start_time = datetime.now()

        server_task = asyncio.create_task(run_server())
        try:
            while (datetime.now() - start_time).total_seconds() < max_runtime:
                logger.info("Checking for pending runs")
                run = await AnalysisRun.find_one(
                    AnalysisRun.status == Status.pending
                ).update_one(
                    Set({AnalysisRun.status: Status.running}),
                    response_type=UpdateResponse.NEW_DOCUMENT,
                )

                assert isinstance(run, AnalysisRun) or run is None

                if not run:
                    await asyncio.sleep(interval)
                    if (datetime.now() - start_time).total_seconds() >= max_runtime:
                        logger.info("Reached maximum runtime. Exiting.")
                        break
                    continue

                logger.info(f"Processing run {run.id} for workspace {run.workspace_id}")

                updated_run = await analyzer.handle_clustering_run(run)
                logger.info(f"Completed run {updated_run.id}")

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
