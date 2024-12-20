import logging
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI

from shared.db import get_client, my_init_beanie

from src.api_settings import api_settings
from src.routers import (
    clustering,
    ingestion_configs,
    ingestion_runs,
    starters,
    workspaces,
)

# TODO : API KEY AUTHENTICATION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()

    client = get_client(api_settings.MONGODB_URI.get_secret_value())

    await my_init_beanie(client)

    logger.info("Connected to MongoDB")

    yield

    client.close()


app = FastAPI(
    title="so_insights",
    version="0.0.1",
    contact={
        "name": "SuperMuel",
        "url": "https://github.com/SuperMuel",
    },
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Welcome to so_insights API"}


app.include_router(workspaces.router, prefix="/workspaces")
app.include_router(
    ingestion_configs.router,
    prefix="/workspaces/{workspace_id}/ingestion-configs",
)
app.include_router(
    ingestion_runs.router,
    prefix="/workspaces/{workspace_id}/ingestion-runs",
)

app.include_router(
    clustering.router,
    prefix="/workspaces/{workspace_id}/clustering",
)

app.include_router(
    starters.router,
    prefix="/workspaces/{workspace_id}/starters",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=api_settings.PORT)
