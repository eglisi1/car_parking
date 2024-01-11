import cv2

def draw_L_shaped_arrow(image_path, starting_point, parking_spot):
    # Das Bild laden und skalieren
    img = cv2.imread(image_path)
    scale_percent = 600 / img.shape[1]  # Berechnung des Skalierungsfaktors für die Breite von 600px
    width = int(img.shape[1] * scale_percent)
    height = int(img.shape[0] * scale_percent)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    # Die Koordinaten für den Startpunkt und den Parkplatz definieren (angepasst an die Skalierung)
    start_x, start_y = (int(starting_point[0] * scale_percent), int(starting_point[1] * scale_percent))
    spot_x, spot_y = (int(parking_spot[0] * scale_percent), int(parking_spot[1] * scale_percent))

    # Den Mittelpunkt berechnen, wo die Linie biegen soll (angepasst an die Skalierung)
    mid_point = (start_x, spot_y)

    # Eine Linie vom Startpunkt zum Mittelpunkt zeichnen (horizontal)
    cv2.line(resized, (start_x, start_y), mid_point, (0, 0, 255), 2)

    # Einen Pfeil vom Mittelpunkt zum Parkplatz zeichnen (vertikal oder horizontal je nach Position)
    cv2.arrowedLine(resized, mid_point, (spot_x, spot_y), (0, 0, 255), 2)

    # Das Bild speichern
    cv2.imwrite('Parkplatz_with_arrow.png', resized)

    # Das Ergebnis anzeigen
    cv2.imshow('Parkplatz', resized)

    # Auf eine Taste warten, dann alle Fenster schließen
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Parkplatzkoordinaten (Beispielwerte, musst du anpassen)
parking_spots = {
    'p1': (1403, 1589),
    'p2': (1403, 990),
    'p3': (1403, 378),
    'p4': (2436, 1599),
    'p5': (2436, 1000),
    'p6': (2436, 377)
}

# Startpunkt (Beispielwert, musst du anpassen)
starting_point = (1919, 2200)

# Funktion aufrufen, um zum Parkplatz X zu navigieren
draw_L_shaped_arrow('Parkplatz_overview.png', starting_point, parking_spots['p4'])
