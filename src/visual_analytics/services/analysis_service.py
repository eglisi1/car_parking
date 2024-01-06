from pymongo.collection import Collection

from collections import defaultdict
from datetime import datetime
import logging

import services.plot_service as plot_service

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def occupancy_trends(collection: Collection, timedelta_days=7) -> str:
    start_time = datetime.datetime.now() - datetime.timedelta(days=timedelta_days)
    data = collection.find({"timestamp": {"$gte": start_time.isoformat()}})

    trends = {}
    for entry in data:
        time_key = entry["timestamp"][:13]  # Group by hour
        occupied_count = sum(
            1 for spot in entry["parkingSpots"] if spot["status"] == "Belegt"
        )
        trends.setdefault(time_key, []).append(occupied_count)

    return plot_service.create_plot_occupancy_trends(trends)


def occupancy_per_day(
    collection: Collection, date_from: datetime, date_to: datetime
) -> str:
    documents = collection.find(
        {
            "timestamp": {
                "$gte": date_from.strftime("%Y-%m-%dT%H:%M:%S"),
                "$lt": date_to.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        }
    )
    average_per_day = calculate_average_per_day(documents)
    return plot_service.create_plot_occupancy_per_day(average_per_day)


def calculate_average_per_day(documents):
    total_parking_spots = len(documents[0]["parkingSpots"]) if documents else 0
    daytimes = {
        "Tag": (
            datetime.strptime("07:00", "%H:%M").time(),
            datetime.strptime("19:00", "%H:%M").time(),
        ),
        "Nacht": (
            datetime.strptime("19:01", "%H:%M").time(),
            datetime.strptime("06:59", "%H:%M").time(),
        ),
    }
    weekdays_date = {
        tag: defaultdict(lambda: {"total_occupied": 0, "count": 0}) for tag in daytimes
    }

    for doc in documents:
        timestamp = datetime.strptime(doc["timestamp"], "%Y-%m-%dT%H:%M:%S")
        wochentag = timestamp.strftime("%A")
        uhrzeit = timestamp.time()
        occupied_parking_spots = sum(
            spot["status"] == "Belegt" for spot in doc["parkingSpots"]
        )

        for tageszeit, (start, ende) in daytimes.items():
            if (start <= uhrzeit <= ende) or (
                start > ende and (uhrzeit >= start or uhrzeit <= ende)
            ):
                weekdays_date[tageszeit][wochentag][
                    "total_occupied"
                ] += occupied_parking_spots
                weekdays_date[tageszeit][wochentag]["count"] += 1

    average_per_weekday = {
        daytime: {
            tag: (daten["total_occupied"] / (total_parking_spots * daten["count"]))
            * 100
            if daten["count"] > 0
            else 0
            for tag, daten in week_data.items()
        }
        for daytime, week_data in weekdays_date.items()
    }

    return average_per_weekday
