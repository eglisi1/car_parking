from collections import defaultdict
from datetime import datetime
import logging

import services.db_service as db_service
from services.db_service import MongoDBClient
import services.plot_service as plot_service

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mongo_client = MongoDBClient()
try:
    mongo_client.connect()
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    exit(1)


def occupancy_trends(date_from: datetime, date_to: datetime) -> str:
    documents = db_service.get_documents_in_range(
        mongo_client.collection, date_from, date_to
    )
    total_parkingspots = len(documents[0]["parkingSpots"]) if documents else 0
    day_period_data = defaultdict(
        lambda: {"total_occupied": 0, "count": 0}
    )  # 07:00-19:00
    night_period_data = defaultdict(
        lambda: {"total_occupied": 0, "count": 0}
    )  # 19:00:01-06:59:59

    for doc in documents:
        timestamp = datetime.strptime(doc["timestamp"], "%Y-%m-%dT%H:%M:%S")
        datee = timestamp.date()
        timee = timestamp.time()

        occupied_spots = sum(spot["status"] == "Belegt" for spot in doc["parkingSpots"])

        # Überprüfe, zu welchem Zeitraum der Zeitstempel gehört, und aktualisiere entsprechend
        if (
            timee >= datetime.strptime("07:00", "%H:%M").time()
            and timee <= datetime.strptime("19:00", "%H:%M").time()
        ):
            day_period_data[datee]["total_occupied"] += occupied_spots
            day_period_data[datee]["count"] += 1
        else:
            night_period_data[datee]["total_occupied"] += occupied_spots
            night_period_data[datee]["count"] += 1

    # Berechne die durchschnittliche Belegungsrate für beide Zeiträume
    day_persiod_average = [
        (datum, (daten["total_occupied"] / (total_parkingspots * daten["count"])) * 100)
        for datum, daten in day_period_data.items()
    ]
    night_period_average = [
        (datum, (daten["total_occupied"] / (total_parkingspots * daten["count"])) * 100)
        for datum, daten in night_period_data.items()
    ]

    return plot_service.create_plot_occupancy_trends(
        day_persiod_average, night_period_average
    )


def occupancy_per_day(date_from: datetime, date_to: datetime) -> str:
    documents = db_service.get_documents_in_range(
        mongo_client.collection, date_from, date_to
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


def occupancy_hours_by_parkingspace(date_from: datetime, date_to: datetime) -> str:
    documents = db_service.get_documents_in_range(
        mongo_client.collection, date_from, date_to
    )
    occupancy_hours = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    for doc in documents:
        for spot in doc["parkingSpots"]:
            if spot["status"] == "Belegt":
                occupancy_hours[
                    spot["parkingSpotId"]
                ] += 0.25  # Jeder Eintrag entspricht 15 Minuten

    # Umrechnen in Stunden
    for spot_id in occupancy_hours:
        occupancy_hours[spot_id] /= 4  # 4*15 Minuten = 1 Stunde

    return plot_service.create_plot_occupancy_hours_by_parkingspace(occupancy_hours)


def capacity_check() -> str:
    try:
        letzter_datensatz = (
            mongo_client.collection.find().sort("timestamp", -1).limit(1)
        )

        # count empty parking spaces
        freie_parkplaetze = 0
        for datensatz in letzter_datensatz:
            for parkplatz in datensatz["parkingSpots"]:
                if parkplatz["status"] == "Frei":
                    freie_parkplaetze += 1

        # Check if spaces are free
        if freie_parkplaetze == 1:
            return "Es ist aktuell noch ein Parkplatz frei"
        if freie_parkplaetze > 0:
            return f"Es sind aktuell noch {freie_parkplaetze} Parkplätze frei"
        else:
            return "Es hat keine freien Parkplätze"

    except Exception as e:
        return f"Fehler bei der Verbindung: {e}"
