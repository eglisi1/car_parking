import picamera
import os
import time
import pymongo

from bson import ObjectId
from roboflow import Roboflow
from datetime import datetime


def load_model():
    rf = Roboflow(api_key=os.environ.get("ROBOFLOW_API_KEY"))
    project = rf.workspace().project("smart-parking-system-uiw5u")
    return project.version(1).model


def take_photo(path):
    camera = picamera.PiCamera()
    try:
        time.sleep(2)
        camera.capture(path)
    finally:
        camera.close()


def detect_parking_spaces(model, path):
    model.predict(path, confidence=60, overlap=30).save("prediction.jpg")
    print(model.predict(path, confidence=60, overlap=30).json())

    return model.predict(path, confidence=60, overlap=30).json()


def transform_model_output(model_output):
    offset_x = 123
    offset_y = 57
    cars = []

    for prediction in model_output["predictions"]:
        x1, y1 = prediction["x"] - offset_x, prediction["y"] - offset_y
        x2, y2 = x1 + prediction["width"], y1 + prediction["height"]

        car_dict = {"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2}

        cars.append(car_dict)

    return cars


def save_to_mongodb(data, username, password, host, database_name, collection_name):
    uri = f"mongodb+srv://{username}:{password}@{host}/{database_name}?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]
    collection.insert_one(data)


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
        parking_status.append({"parkingSpotId": i + 1, "status": status})

    print(f"parking status: {parking_status}")
    return parking_status


def check_and_save(detections):
    cars = [(d["xmin"], d["ymin"], d["xmax"], d["ymax"]) for d in detections]

    parking_spots = [
        (935, 181, 945, 191),
        (954, 370, 964, 380),
        (974, 585, 984, 595),
        (410, 172, 420, 182),
        (397, 366, 407, 376),
        (377, 584, 387, 594),
    ]

    parking_status = create_parking_status(cars, parking_spots)

    data_to_save = {
        "_id": ObjectId(),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "parkingSpots": parking_status,
    }

    username = os.getenv("MONGO_DB_USERNAME")
    password = os.getenv("MONGO_DB_PASSWORD")
    host = "parkinglot.yba45ot.mongodb.net"
    database_name = "parkinglot"
    collection_name = "data"

    save_to_mongodb(
        data_to_save, username, password, host, database_name, collection_name
    )
    print(data_to_save)
    print(
        f'Data saved to MongoDB collection "{collection_name}" in database "{database_name}".'
    )


model = load_model()
take_photo("/home/admin/photos/latest.jpg")
raw_detections = detect_parking_spaces(model, "/home/admin/photos/latest.jpg")
detections = transform_model_output(raw_detections)
check_and_save(detections)
