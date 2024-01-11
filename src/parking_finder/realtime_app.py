from flask import Flask, render_template, request, url_for
import cv2
import numpy as np
import base64

app = Flask(__name__)

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

    _, image_buffer = cv2.imencode('.png', resized)
    return image_buffer.tobytes()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            model_output = request.form.get('model_output')
            model_output = eval(model_output)  # Achtung: eval() nur in sicherem Kontext verwenden!

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
                image_bytes = draw_L_shaped_arrow('car_parking/notebooks/Parkplatz_overview.png', starting_point, parking_spots[nearest_spot])
                image_encoded = base64.b64encode(image_bytes).decode('utf-8')  # Bild für HTML codieren
                return render_template('result.html', image_data=image_encoded, title="Nächstgelegener Parkplatz")
            else:
                return render_template('no_spot.html', message="Leider ist kein freier Parkplatz verfügbar.")
        except Exception as e:
            return f"Ein Fehler ist aufgetreten: {e}"
    else:
        return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
