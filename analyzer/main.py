import asyncio
import logging
from dotenv import load_dotenv
from shared.db import get_client, my_init_beanie
from shared.models import Workspace
import typer
from src.analyzer import Analyzer
from src.analyzer_settings import AnalyzerSettings


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

    analyzer = Analyzer()

    return mongo_client, analyzer


@app.command()
def clusterize(workspace_id: str):
    async def _clusterize():
        mongo_client, analyzer = await setup()

        workspace = await Workspace.get(workspace_id)

        if workspace is None:
            typer.echo("No cluster found for the given workspace.", err=True)
        else:
            await analyzer.analyse(workspace)

        mongo_client.close()

    asyncio.run(_clusterize())


if __name__ == "__main__":
    app()
