from beanie import init_beanie
from shared.db_settings import DBSettings
from shared.models import (
    Cluster,
    Workspace,
    SearchQuerySet,
    IngestionRun,
    ClusteringSession,
    Article,
)
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)


def get_client(mongodb_uri):
    return AsyncIOMotorClient(mongodb_uri)


async def my_init_beanie(client):
    await init_beanie(
        database=client[DBSettings().mongodb_database],
        document_models=[
            Workspace,
            SearchQuerySet,
            IngestionRun,
            Cluster,
            ClusteringSession,
            Article,
        ],
    )

    logger.info("Beanie Initialized")