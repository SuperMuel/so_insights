import logging
import sys
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from src.api_settings import ApiSettings
from src.models import (
    Article,
    ClusteringSession,
    IngestionRun,
    SearchQuerySet,
    Workspace,
)
from src.routers import search_query_sets, workspaces

# TODO : API KEY AUTHENTICATION


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

settings = ApiSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.mongodb_uri)

    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[
            Workspace,
            SearchQuerySet,
            IngestionRun,
            ClusteringSession,
            Article,
        ],
    )
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
    search_query_sets.router,
    prefix="/workspaces/{workspace_id}/search-query-sets",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
