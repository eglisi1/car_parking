from flask import Flask, render_template, request
from pymongo import MongoClient

import logging
import datetime
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_env_variable(var_name):
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/occupancy_trends")
def occupancy_trends():
    timedelta_days = request.args.get('timedelta', default=7, type=int)
    start_time = datetime.datetime.now() - datetime.timedelta(days=timedelta_days)
    data = collection.find({"timestamp": {"$gte": start_time.isoformat()}})

    trends = {}
    for entry in data:
        time_key = entry["timestamp"][:13]  # Group by hour
        occupied_count = sum(
            1 for spot in entry["parkingSpots"] if spot["status"] == "Belegt"
        )
        trends.setdefault(time_key, []).append(occupied_count)

    avg_occupancy = {time: sum(counts) / len(counts) for time, counts in trends.items()}
    return render_template("occupancy_trends.html", data=avg_occupancy)


if __name__ == "__main__":
    app.run(debug=True)
