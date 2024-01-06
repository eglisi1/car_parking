from pymongo.collection import Collection
import datetime

import services.plot_service as plot_service


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

    return plot_service.create_plot(trends)
