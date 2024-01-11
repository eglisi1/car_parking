import os
import time
import picamera
import pymongo
import cv2
import tensorflow as tf

from datetime import datetime
from bson.objectid import ObjectId


def take_photo(path):
    with picamera.PiCamera() as camera:
        time.sleep(2)
        camera.capture(path)


def load_and_preprocess_image(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = tf.convert_to_tensor(image, dtype=tf.uint8)

    image = tf.expand_dims(image, 0)
    return image


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
    return parking_status


def save_to_mongodb(data, username, password, host, database_name, collection_name):
    uri = f"mongodb+srv://{username}:{password}@{host}/{database_name}?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]
    collection.insert_one(data)


def check_and_save(detections):
    cars = [(d["xmin"], d["ymin"], d["xmax"], d["ymax"]) for d in detections]

    parking_spots = [
        (804, 102, 1076, 270),
        (818, 275, 1100, 475),
        (828, 482, 1131, 698),
        (283, 83, 548, 271),
        (260, 269, 545, 473),
        (229, 488, 535, 690),
    ]

    parking_status = create_parking_status(cars, parking_spots)

    data_to_save = {
        "_id": ObjectId(),
        "timestamp": datetime.now().isoformat(),
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
    print(
        f'Data saved to MongoDB collection "{collection_name}" in database "{database_name}".'
    )


def detect_objects(image):
    detections = model(image)

    class_names = {}
    detected_objects = []

    with open("../models/coco_labels.txt", "r") as file:
        for i, line in enumerate(file.readlines(), start=1):
            class_names[i] = line.strip()

    boxes = detections["detection_boxes"].numpy()
    classes = detections["detection_classes"].numpy()
    scores = detections["detection_scores"].numpy()

    original_image = cv2.imread("latest.jpg")

    if original_image is None:
        raise ValueError("Image not found or path is incorrect")

    height, width, _ = original_image.shape

    for i in range(boxes.shape[1]):
        score = scores[0, i]
        if score > 0.5:
            class_id = int(classes[0, i])
            label = class_names.get(class_id, "N/A")
            if label in ["2  car", "86  scissors"]:
                ymin, xmin, ymax, xmax = boxes[0, i]
                xmin = int(xmin * width)
                xmax = int(xmax * width)
                ymin = int(ymin * height)
                ymax = int(ymax * height)

                detected_object = {
                    "xmin": xmin,
                    "ymin": ymin,
                    "xmax": xmax,
                    "ymax": ymax,
                }

                detected_objects.append(detected_object)

    return detected_objects


# take a photo
take_photo("/home/admin/photos/latest.jpg")

# load the efficientdet model
# model = tf.saved_model.load('../models/efficientdet_d1_coco17_tpu-32/saved_model')

# preprocess image
# image = load_and_preprocess_image('latest.jpg')

# detect objects and return coordinates
detected_objects = detect_objects(image)

# check coordinates and save data to mongoDB
check_and_save(detected_objects)
