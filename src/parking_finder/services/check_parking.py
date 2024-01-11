import os
import time
from typing import List, Dict, Tuple
import base64
from flask import render_template

try:
    import picamera
except ImportError:
    print("Solely working on pi. But we got you covered.")

from roboflow import Roboflow
from roboflow.util.prediction import PredictionGroup

import cv2

rf = Roboflow(api_key=os.environ.get("ROBOFLOW_API_KEY"))
project = rf.workspace().project("smart-parking-system-uiw5u")
model = project.version(1).model

parking_spots = [
    (935, 181, 945, 191),
    (954, 370, 964, 380),
    (974, 585, 984, 595),
    (410, 172, 420, 182),
    (397, 366, 407, 376),
    (377, 584, 387, 594),
]
parking_order = ["p1", "p4", "p2", "p5", "p3", "p6"]
parking_spots_points = {
    "p1": (1403, 1589),
    "p2": (1403, 990),
    "p3": (1403, 378),
    "p4": (2436, 1599),
    "p5": (2436, 1000),
    "p6": (2436, 377),
}
images_path = "../../data/images/"


def take_photo(path: str):
    camera = picamera.PiCamera()
    try:
        time.sleep(2)
        camera.capture(path)
    finally:
        camera.close()


def is_raspberry_pi():
    try:
        with open("/proc/device-tree/model", "r") as f:
            return "Raspberry Pi" in f.read()
    except Exception:
        return False


def get_image_path() -> str:
    # if running on pi take photo and save otherwise return test image
    if is_raspberry_pi():
        print("running on pi")
        path = "capture.jpg"
        take_photo(path)
        return path
    else:
        print("running on non-pi")
        return images_path + "latest3.jpg"


def get_parking_spaces(predictions: List[Dict]):
    cars = [(d["xmin"], d["ymin"], d["xmax"], d["ymax"]) for d in predictions]
    return create_parking_status(cars)


def create_parking_status(cars: List):
    parking_status = []
    for i, spot in enumerate(parking_spots):
        status = "Frei"
        for car in cars:
            if is_occupied(car, spot):
                status = "Belegt"
                break
        parking_status.append({"parkingSpotId": i + 1, "status": status})
    return parking_status


def is_occupied(car: Tuple, parking_spot: Tuple):
    car_x1, car_y1, car_x2, car_y2 = car
    p_x1, p_y1, p_x2, p_y2 = parking_spot
    return not (car_x2 < p_x1 or car_x1 > p_x2 or car_y2 < p_y1 or car_y1 > p_y2)


def predict_parking_spaces(picture_path: str) -> PredictionGroup:
    return model.predict(picture_path, confidence=60, overlap=30).json()


def transform_model_output(model_output: PredictionGroup) -> List[Dict]:
    offset_x = 123
    offset_y = 57
    cars = []

    for prediction in model_output["predictions"]:
        x1, y1 = prediction["x"] - offset_x, prediction["y"] - offset_y
        x2, y2 = x1 + prediction["width"], y1 + prediction["height"]

        car_dict = {"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2}
        cars.append(car_dict)

    return cars


def find_nearest_free_spot(parking_status: List):
    for spot in parking_order:
        if parking_status[int(spot[1:]) - 1]["status"] == "Frei":
            return spot
    return None


def draw_image(nearest_free_spot: str) -> str:
    starting_point = (1919, 2200)
    image_bytes = draw_l_shaped_arrow(
        images_path + "/Parkplatz_overview.png",
        starting_point,
        parking_spots_points[nearest_free_spot],
    )
    return base64.b64encode(image_bytes).decode("utf-8")


def draw_l_shaped_arrow(
    image_path: str, starting_point: Tuple, parking_spot: Tuple
) -> bytes:
    img = cv2.imread(image_path)
    scale_percent = 600 / img.shape[1]
    width = int(img.shape[1] * scale_percent)
    height = int(img.shape[0] * scale_percent)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    start_x, start_y = (
        int(starting_point[0] * scale_percent),
        int(starting_point[1] * scale_percent),
    )
    spot_x, spot_y = (
        int(parking_spot[0] * scale_percent),
        int(parking_spot[1] * scale_percent),
    )

    mid_point = (start_x, spot_y)

    cv2.line(resized, (start_x, start_y), mid_point, (0, 0, 255), 2)
    cv2.arrowedLine(resized, mid_point, (spot_x, spot_y), (0, 0, 255), 2)

    _, image_buffer = cv2.imencode(".png", resized)
    return image_buffer.tobytes()


def detect_parking_spaces() -> str:
    image_path = get_image_path()
    raw_detections = predict_parking_spaces(image_path)
    detections = transform_model_output(raw_detections)
    parking_spots = get_parking_spaces(detections)
    nearest_free_spot = find_nearest_free_spot(parking_spots)
    if nearest_free_spot:
        image_with_arrow = draw_image(nearest_free_spot)
        return render_template(
            "result.html",
            title="Ein freier Parkplatz ist verfügbar.",
            image_data=image_with_arrow,
        )
    else:
        return render_template(
            "no_spot.html",
            title="Leider ist kein freier Parkplatz verfügbar.",
        )
