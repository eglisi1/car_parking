import cv2
from datetime import datetime

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

def find_nearest_free_spot(parking_status):
    parking_order = ['p1', 'p4', 'p2', 'p5', 'p3', 'p6']
    for spot in parking_order:
        if parking_status[int(spot[1:]) - 1]['status'] == "Frei":
            return spot
    return None

def draw_L_shaped_arrow(image_path, starting_point, parking_spot):
    img = cv2.imread(image_path)
    scale_percent = 600 / img.shape[1]
    width = int(img.shape[1] * scale_percent)
    height = int(img.shape[0] * scale_percent)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    start_x, start_y = (int(starting_point[0] * scale_percent), int(starting_point[1] * scale_percent))
    spot_x, spot_y = (int(parking_spot[0] * scale_percent), int(parking_spot[1] * scale_percent))

    mid_point = (start_x, spot_y)

    cv2.line(resized, (start_x, start_y), mid_point, (0, 0, 255), 2)
    cv2.arrowedLine(resized, mid_point, (spot_x, spot_y), (0, 0, 255), 2)

    cv2.imwrite('Parkplatz_with_arrow.png', resized)
    cv2.imshow('Parkplatz', resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def check_realtime(model_output):
    cars = [(d['xmin'], d['ymin'], d['xmax'], d['ymax']) for d in model_output]
    parking_spots_coordinates = [(804, 102, 1076, 270), (818, 275, 1100, 475), (828, 482, 1131, 698), 
                                 (283, 83, 548, 271), (260, 269, 545, 473), (229, 488, 535, 690)]
    
    parking_status = create_parking_status(cars, parking_spots_coordinates)
    nearest_spot = find_nearest_free_spot(parking_status)

    if nearest_spot:
        parking_spots = {
            'p1': (1403, 1589), 'p2': (1403, 990), 'p3': (1403, 378),
            'p4': (2436, 1599), 'p5': (2436, 1000), 'p6': (2436, 377)
        }
        starting_point = (1919, 2200)
        draw_L_shaped_arrow('car_parking/notebooks/Parkplatz_overview.png', starting_point, parking_spots[nearest_spot])
    else:
        print("Kein freier Parkplatz verfügbar.")

# Verwendung der Funktion
model_output = [
   {'xmin': 262, 'ymin': 335, 'xmax': 516, 'ymax': 443},
   {'xmin': 267, 'ymin': 128, 'xmax': 502, 'ymax': 243}, 
   {'xmin': 238, 'ymin': 532, 'xmax': 507, 'ymax': 661},
   {'xmin': 810, 'ymin': 146, 'xmax': 1038, 'ymax': 253},
   {'xmin': 833, 'ymin': 561, 'xmax': 1104, 'ymax': 686},
   {'xmin': 821, 'ymin': 328, 'xmax': 1071, 'ymax': 448}, 
]

check_realtime(model_output)
