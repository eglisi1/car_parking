from pymongo import MongoClient
from pymongo.collection import Collection

import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        logger.error(f"Environment variable '{var_name}' not found.")
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value


try:
    username = load_env_variable("MONGO_DB_USERNAME")
    password = load_env_variable("MONGO_DB_PASSWORD")
    host = load_env_variable("MONGO_DB_HOST")
    database_name = load_env_variable("MONGO_DB_DATABASE_NAME")
    collection_name = load_env_variable("MONGO_DB_COLLECTION_NAME")

    client = MongoClient(
        f"mongodb+srv://{username}:{password}@{host}/{database_name}?retryWrites=true&w=majority"
    )
    db = client[database_name]
    collection = db[collection_name]
except EnvironmentError as e:
    logger.error(f"Failed to load environment variables: {e}")
    exit(1)
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    exit(1)

def get_collection() -> Collection:
    return collection

def get_documents_in_range(date_from: datetime, date_to: datetime):
    return collection.find(
        {
            "timestamp": {
                "$gte": date_from.strftime("%Y-%m-%dT%H:%M:%S"),
                "$lt": date_to.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        }
    )