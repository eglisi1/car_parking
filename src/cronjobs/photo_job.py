import time
import picamera


def take_photo(path):
    with picamera.PiCamera() as camera:
        time.sleep(2)
        camera.capture(path)


take_photo('/home/admin/photos/latest.jpg')
