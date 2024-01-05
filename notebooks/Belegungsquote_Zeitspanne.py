from pymongo import MongoClient
import os
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
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

# Berechne die durchschnittliche Belegungsrate für beide Zeiträume
def berechne_durchschnittsrate_nach_zeitraum(documents):
    gesamt_parkplätze = len(documents[0]['parkingSpots']) if documents else 0
    zeitraum1_daten = defaultdict(lambda: {'gesamt_belegt': 0, 'zählung': 0})  # 07:00-19:00
    zeitraum2_daten = defaultdict(lambda: {'gesamt_belegt': 0, 'zählung': 0})  # 19:00:01-06:59:59

    for doc in documents:
        timestamp = datetime.strptime(doc['timestamp'], "%Y-%m-%dT%H:%M:%S")
        datum = timestamp.date()
        uhrzeit = timestamp.time()
        
        belegte_plätze = sum(spot['status'] == "Belegt" for spot in doc['parkingSpots'])
        
        # Überprüfe, zu welchem Zeitraum der Zeitstempel gehört, und aktualisiere entsprechend
        if uhrzeit >= datetime.strptime("07:00", "%H:%M").time() and uhrzeit <= datetime.strptime("19:00", "%H:%M").time():
            zeitraum1_daten[datum]['gesamt_belegt'] += belegte_plätze
            zeitraum1_daten[datum]['zählung'] += 1
        else:
            zeitraum2_daten[datum]['gesamt_belegt'] += belegte_plätze
            zeitraum2_daten[datum]['zählung'] += 1

    # Berechne die durchschnittliche Belegungsrate für beide Zeiträume
    zeitraum1_durchschnitt = [(datum, (daten['gesamt_belegt'] / (gesamt_parkplätze * daten['zählung'])) * 100) for datum, daten in zeitraum1_daten.items()]
    zeitraum2_durchschnitt = [(datum, (daten['gesamt_belegt'] / (gesamt_parkplätze * daten['zählung'])) * 100) for datum, daten in zeitraum2_daten.items()]

    return sorted(zeitraum1_durchschnitt), sorted(zeitraum2_durchschnitt)

# Plotte die tägliche durchschnittliche Belegungsrate für beide Zeiträume
def plotte_belegungsrate(zeitraum1_daten, zeitraum2_daten):
    plt.figure(figsize=(12, 6))

    # Daten für das Plotten vorbereiten
    daten1 = [data[0] for data in zeitraum1_daten]
    raten1 = [data[1] for data in zeitraum1_daten]
    daten2 = [data[0] for data in zeitraum2_daten]
    raten2 = [data[1] for data in zeitraum2_daten]

    # Zeichne beide Linien für die Zeiträume
    plt.plot(daten1, raten1, 'r-', label='07:00-19:00')
    plt.plot(daten2, raten2, 'b-', label='19:01-06:59')

    # X-Achsen-Ticks auf maximal 10 beschränken
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))

    # Beschriftungen und Diagramm-Formatierungen
    plt.ylim(0, 100)
    plt.title('Durchschnittliche Belegungsrate nach Tageszeit')
    plt.xlabel('Datum')
    plt.ylabel('Belegungsrate (%)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.show()

# Hauptprogramm
startzeit = '2023-01-01T00:00:00'
endzeit = '2023-01-30T00:00:00'
documents = lade_daten(startzeit, endzeit)
print(f"Anzahl der Dokumente: {len(documents)}")
zeitraum1_durchschnitt, zeitraum2_durchschnitt = berechne_durchschnittsrate_nach_zeitraum(documents)
plotte_belegungsrate(zeitraum1_durchschnitt, zeitraum2_durchschnitt)
