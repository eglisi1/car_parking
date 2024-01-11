from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def load_env_variables(self):
        try:
            self.username = os.environ["MONGO_DB_USERNAME"]
            self.password = os.environ["MONGO_DB_PASSWORD"]
            self.host = os.environ["MONGO_DB_HOST"]
            self.database_name = os.environ["MONGO_DB_DATABASE_NAME"]
            self.collection_name = os.environ["MONGO_DB_COLLECTION_NAME"]
        except KeyError as e:
            logger.error(f"Environment variable not set: {e}")
            raise

    def connect(self):
        self.load_env_variables()
        try:
            self.client = MongoClient(
                f"mongodb+srv://{self.username}:{self.password}@{self.host}/{self.database_name}?retryWrites=true&w=majority"
            )
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

def get_documents_in_range(collection, date_from: datetime, date_to: datetime):
    return collection.find(
        {
            "timestamp": {
                "$gte": date_from.strftime("%Y-%m-%dT%H:%M:%S"),
                "$lt": date_to.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        }
    )

def get_last_document(collection):
    return collection.find().sort("timestamp", -1).limit(1)