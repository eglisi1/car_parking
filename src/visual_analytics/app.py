import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend

from flask import Flask, render_template, request
from pymongo import MongoClient
import matplotlib.pyplot as plt

import logging
import datetime
import os
from io import BytesIO
import base64

app = Flask(__name__)

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


def create_plot(trends: dict) -> str:
    x_axis = list(trends.keys())
    y_axis = [sum(counts) / len(counts) for counts in trends.values()]
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, y_axis, label="Occupancy", color="blue")
    plt.xlabel("Timestamp")
    plt.ylabel("Average Occupancy")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    return base64.b64encode(buf.getbuffer()).decode("ascii")


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/occupancy_trends")
def occupancy_trends() -> str:
    timedelta_days = request.args.get("timedelta", default=7, type=int)
    start_time = datetime.datetime.now() - datetime.timedelta(days=timedelta_days)
    data = collection.find({"timestamp": {"$gte": start_time.isoformat()}})

    trends = {}
    for entry in data:
        time_key = entry["timestamp"][:13]  # Group by hour
        occupied_count = sum(
            1 for spot in entry["parkingSpots"] if spot["status"] == "Belegt"
        )
        trends.setdefault(time_key, []).append(occupied_count)

    base64_plot = create_plot(trends)
    return render_template("occupancy_trends.html", plot_url=base64_plot)


if __name__ == "__main__":
    app.run(debug=True)
