from picamera import PiCamera
from time import sleep

camera = PiCamera()


try:
    camera.resolution = (640, 480)
    camera.start_preview()
    sleep(5)
    camera.capture('./photos/image.jpg')
    camera.stop_preview()
    
finally:
    camera.close()


#try:
	#camera.start_preview()
	#sleep(10)
    #camera.capture('./photos/image.jpg')
    #camera.stop_preview()

#finally:
	#camera.close()
