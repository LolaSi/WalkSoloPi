from picamera import PiCamera
from time import sleep

camera = PiCamera()


try:
    camera.resolution = (640, 480)
    camera.start_preview()
    sleep(5)
    camera.capture('./photos/image.png', format='png')
    camera.stop_preview()
    
finally:
    camera.close()
