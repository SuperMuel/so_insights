import logging
from dotenv import load_dotenv
from shared.db import get_client, my_init_beanie
import typer
from src.clusterer_settings import ClustererSettings


load_dotenv()

settings = ClustererSettings()

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

    return mongo_client


@app.command()
def clusterize():
    logger.info("Clusterize command")


if __name__ == "__main__":
    app()
