import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import SecretStr

from shared.db_settings import db_settings
from shared.models import (
    Article,
    Cluster,
    ClusteringSession,
    IngestionConfig,
    IngestionRun,
    Organization,
    RssIngestionConfig,
    SearchIngestionConfig,
    Starters,
    Workspace,
)

logger = logging.getLogger(__name__)


def get_client(mongodb_uri):
    if isinstance(mongodb_uri, SecretStr):
        mongodb_uri = mongodb_uri.get_secret_value()
    elif isinstance(mongodb_uri, str):
        pass
    else:
        raise ValueError("mongodb_uri must be a string or SecretStr")

    return AsyncIOMotorClient(mongodb_uri)


async def my_init_beanie(client):
    await init_beanie(
        database=client[db_settings.mongodb_database],
        document_models=[
            Organization,
            Workspace,
            IngestionConfig,
            SearchIngestionConfig,
            RssIngestionConfig,
            IngestionRun,
            Cluster,
            ClusteringSession,
            Article,
            Starters,
        ],
    )

    logger.info("Beanie Initialized")
