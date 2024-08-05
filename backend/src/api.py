import logging
import sys
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI, status
from motor.motor_asyncio import AsyncIOMotorClient

from src.dependencies import ExistingWorkspace
from src.models import Workspace, utc_datetime_factory
from src.schemas import WorkspaceUpdate
from src.settings import AppSettings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

settings = AppSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.mongodb_uri)

    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[Workspace],
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
    return {"message": "Hello World"}


# Workspace routes
@app.post(
    "/workspaces/",
    response_model=Workspace,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_workspace",
)
async def create_workspace(workspace: Workspace):
    await workspace.insert()
    return workspace


@app.get("/workspaces/", response_model=list[Workspace], operation_id="list_workspaces")
async def list_workspaces():
    return await Workspace.find_all().to_list()


@app.get(
    "/workspaces/{workspace_id}", response_model=Workspace, operation_id="get_workspace"
)
async def get_workspace(workspace: ExistingWorkspace):
    return workspace


@app.put(
    "/workspaces/{workspace_id}",
    response_model=Workspace,
    operation_id="update_workspace",
)
async def update_workspace(
    workspace: ExistingWorkspace, workspace_update: WorkspaceUpdate
):
    print(workspace_update)
    req = {
        k: v
        for k, v in workspace_update.model_dump(
            exclude_none=True,
            # exclude_unset=True,
        ).items()
    }

    req["updated_at"] = utc_datetime_factory()

    print(f"{req=}")

    update_query = {"$set": req}

    return await workspace.update(update_query)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
