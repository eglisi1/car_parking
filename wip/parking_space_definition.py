
import cv2

image = cv2.imread('car_parking/notebooks/latest.jpg')

p1 = (804, 102, 1076, 270)
p2 = (818, 275, 1100, 475)
p3 = (828, 482, 1131, 698)
p4 = (283, 83, 548, 271)
p5 = (260, 269, 545, 473)
p6 = (229, 488, 535, 690)
car1 = (855, 144, 1015, 236)
car2 = (320, 120, 500, 217)

parking_spaces = [p1, p2, p3, p4, p5, p6, car1, car2]

# Loop through each parking space
for space in parking_spaces:
    # Extract the coordinates
    x1, y1, x2, y2 = space
    # Draw a rectangle on the image
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

new_width = 800
new_height = 600
resized_image = cv2.resize(image, (new_width, new_height))

cv2.imshow("resized_image", resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()