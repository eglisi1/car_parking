import os
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime

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

# Teste die Verbindung
try:
    client.admin.command('ping')
    print("Verbindung erfolgreich: MongoDB ist erreichbar!")
except Exception as e:
    print("Fehler bei der Verbindung: ", e)

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

# Berechne die Besetzungsstunden für jeden Parkplatz
def berechne_besetzungsstunden(documents):
    belegungsstunden = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    for doc in documents:
        for spot in doc['parkingSpots']:
            if spot['status'] == 'Belegt':
                belegungsstunden[spot['parkingSpotId']] += 0.25  # Jeder Eintrag entspricht 15 Minuten

    # Umrechnen in Stunden
    for spot_id in belegungsstunden:
        belegungsstunden[spot_id] /= 4  # 4*15 Minuten = 1 Stunde

    return belegungsstunden

# Balkendiagramm für die Belegungsstunden erstellen
def erstelle_balkendiagramm(belegungsstunden):
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(belegungsstunden)), list(belegungsstunden.values()), align='center')
    plt.xticks(range(len(belegungsstunden)), list(belegungsstunden.keys()))
    plt.title('Besetzungsstunden pro Parkplatz')
    plt.xlabel('Parkplatz ID')
    plt.ylabel('Stunden')
    plt.show()

# Direkte Eingabe von Start- und Endzeitpunkten
startzeit = '2023-01-01T00:00:00'
endzeit = '2023-01-30T00:00:00'
documents = lade_daten(startzeit, endzeit)
belegungsstunden = berechne_besetzungsstunden(documents)
erstelle_balkendiagramm(belegungsstunden)
