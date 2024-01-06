from datetime import datetime
import pymongo
from bson.objectid import ObjectId

def is_occupied(car, parking_spot):
    car_x1, car_y1, car_x2, car_y2 = car
    p_x1, p_y1, p_x2, p_y2 = parking_spot
    return not (car_x2 < p_x1 or car_x1 > p_x2 or car_y2 < p_y1 or car_y1 > p_y2)

def create_parking_status(cars, parking_spots):
    parking_status = []
    for i, spot in enumerate(parking_spots):
        status = "Frei"
        for car in cars:
            if is_occupied(car, spot):
                status = "Belegt"
                break
        parking_status.append({"parkingSpotId": i+1, "status": status})
    return parking_status

def save_to_mongodb(data, username, password, host, database_name, collection_name):
    uri = f"mongodb+srv://{username}:{password}@{host}/{database_name}?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]
    collection.insert_one(data)

def check_and_save(detections):
    cars = [(d['xmin'], d['ymin'], d['xmax'], d['ymax']) for d in detections]

    parking_spots = [(804, 102, 1076, 270), (818, 275, 1100, 475), (828, 482, 1131, 698), 
                     (283, 83, 548, 271), (260, 269, 545, 473), (229, 488, 535, 690)]
    
    parking_status = create_parking_status(cars, parking_spots)

    data_to_save = {
        "_id": ObjectId(),
        "timestamp": datetime.now().isoformat(),
        "parkingSpots": parking_status
    }

    username = 'carpark'
    password = 'x'
    host = 'parkinglot.yba45ot.mongodb.net'
    database_name = 'parkinglot'
    collection_name = 'data'

    save_to_mongodb(data_to_save, username, password, host, database_name, collection_name)
    print(f"Data saved to MongoDB collection '{collection_name}' in database '{database_name}'.")

# Output des Modells
model_output = [
    {'xmin': 262, 'ymin': 335, 'xmax': 516, 'ymax': 443},
    {'xmin': 267, 'ymin': 128, 'xmax': 502, 'ymax': 243}, 
    {'xmin': 810, 'ymin': 146, 'xmax': 1038, 'ymax': 253}
]

# Führe den Check aus und speichere das Ergebnis in MongoDB
check_and_save(model_output)
