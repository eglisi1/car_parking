from pymongo import MongoClient
import os
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

# Lade Umgebungsvariablen
username = os.getenv('MONGO_DB_USERNAME')
password = os.getenv('MONGO_DB_PASSWORD')
host = os.getenv('MONGO_DB_HOST')
database_name = os.getenv('MONGO_DB_DATABASE_NAME')  
collection_name = os.getenv('MONGO_DB_COLLECTION_NAME')

# MongoDB-Verbindung
uri = f"mongodb+srv://{username}:{password}@{host}/{database_name}?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client[database_name]
collection = db[collection_name]

# Daten aus MongoDB laden mit Zeitraumfilter
def lade_daten(startzeit, endzeit):
    if isinstance(startzeit, str):
        startzeit = datetime.strptime(startzeit, '%Y-%m-%dT%H:%M:%S')
    if isinstance(endzeit, str):
        endzeit = datetime.strptime(endzeit, '%Y-%m-%dT%H:%M:%S')

    documents = collection.find({
        'timestamp': {
            '$gte': startzeit.strftime('%Y-%m-%dT%H:%M:%S'),
            '$lt': endzeit.strftime('%Y-%m-%dT%H:%M:%S')
        }
    })

    return list(documents)

# Berechne die durchschnittliche Belegungsrate pro Wochentag und Zeitraum
def berechne_durchschnittsrate_pro_wochentag(documents):
    gesamt_parkplätze = len(documents[0]['parkingSpots']) if documents else 0
    tageszeiten = {
        "Tag": (datetime.strptime("07:00", "%H:%M").time(), datetime.strptime("19:00", "%H:%M").time()),
        "Nacht": (datetime.strptime("19:01", "%H:%M").time(), datetime.strptime("06:59", "%H:%M").time())
    }
    wochentag_daten = {tag: defaultdict(lambda: {'gesamt_belegt': 0, 'zählung': 0}) for tag in tageszeiten}

    for doc in documents:
        timestamp = datetime.strptime(doc['timestamp'], "%Y-%m-%dT%H:%M:%S")
        wochentag = timestamp.strftime('%A')
        uhrzeit = timestamp.time()
        belegte_plätze = sum(spot['status'] == "Belegt" for spot in doc['parkingSpots'])

        for tageszeit, (start, ende) in tageszeiten.items():
            if (start <= uhrzeit <= ende) or (start > ende and (uhrzeit >= start or uhrzeit <= ende)):
                wochentag_daten[tageszeit][wochentag]['gesamt_belegt'] += belegte_plätze
                wochentag_daten[tageszeit][wochentag]['zählung'] += 1

    durchschnittsrate_pro_wochentag = {
        tageszeit: {
            tag: (daten['gesamt_belegt'] / (gesamt_parkplätze * daten['zählung'])) * 100 if daten['zählung'] > 0 else 0
            for tag, daten in wochen_data.items()
        } for tageszeit, wochen_data in wochentag_daten.items()
    }

    return durchschnittsrate_pro_wochentag

# Plotte die durchschnittliche Belegungsrate pro Wochentag und Zeitraum
def plotte_belegungsrate_pro_wochentag(durchschnittsrate_pro_wochentag):
    tage_der_woche = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plt.figure(figsize=(14, 6))

    for tageszeit, wochen_data in durchschnittsrate_pro_wochentag.items():
        raten = [wochen_data.get(tag, 0) for tag in tage_der_woche]
        plt.plot(tage_der_woche, raten, label=tageszeit)

    # Beschriftungen und Diagramm-Formatierungen
    plt.title('Durchschnittliche Belegungsrate pro Wochentag und Tageszeit')
    plt.xlabel('Wochentag')
    plt.ylabel('Belegungsrate (%)')
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Hauptprogramm
startzeit = '2023-01-01T00:00:00'
endzeit = '2023-01-30T00:00:00'
documents = lade_daten(startzeit, endzeit)
print(f"Anzahl der Dokumente: {len(documents)}")
durchschnittsrate_pro_wochentag = berechne_durchschnittsrate_pro_wochentag(documents)
plotte_belegungsrate_pro_wochentag(durchschnittsrate_pro_wochentag)
