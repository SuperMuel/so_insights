import logging
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI

from shared.db import get_client, my_init_beanie

from src.api_settings import APISettings
from src.routers import search_query_sets, workspaces

# TODO : API KEY AUTHENTICATION

settings = APISettings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()

    client = get_client(settings.MONGODB_URI)

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
    search_query_sets.router,
    prefix="/workspaces/{workspace_id}/search-query-sets",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
