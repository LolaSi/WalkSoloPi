import bluetooth
import subprocess
import os
from PIL import Image
import io

# Libraries for taking picture
from picamera import PiCamera
from time import sleep

#Libraries for distance
import RPi.GPIO as GPIO
import time

counter = 0
camera = PiCamera()

def takePicture():
	try:
		camera.resolution = (640, 480)
		camera.start_preview()
		sleep(5)
		pic_path = './photos/image' + str(counter)+'.jpg'
		#camera.capture('./photos/image.jpg')
		camera.capture(pic_path)
		camera.stop_preview()
		counter += 1
	finally:
		camera.close()
		return pic_path


def sendPicture(client_sock):
    print("yay, going to take pic")
    pic_path = takePicture()
    #subprocess.run(["python", "still_pic.py"])
    #im = Image.open('./photos/image.jpg')
    im = Image.open(pic_path)
    im_resize = im.resize((500,500))
    buff = io.BytesIO()
    im_resize.save(buff, format='PNG')
    byte_im = buff.getvalue()
    size = (str(len(byte_im))).encode()
    print(size)
    #client_sock.send(size)
    client_sock.send(byte_im)
    
    
def get_distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
    
    #dist = distance()
    #       print ("Measured Distance = %.1f cm" % dist)
    #      time.sleep(1)
    

def main():
	#camera = PiCamera()
    while True:
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", bluetooth.PORT_ANY))
        server_sock.listen(1)

        port = server_sock.getsockname()[1]

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                # protocols=[bluetooth.OBEX_UUID]
                                )
        print("Waiting for connection on RFCOMM channel", port)

        client_sock, client_info = server_sock.accept()
        print("Accepted connection from", client_info)

        try:
            while True:
                data = client_sock.recv(1024)
                print("Received", data)
                if data.decode("utf-8") == "1":
                    sendPicture(client_sock)
                if data.decode("utf-8") == "2":
					while True:
						# set Trigger after 0.1ms
						time.sleep(0.0001)
						sendPicture(client_sock)
						
        except OSError:
            print("Disconnected.")

        client_sock.close()
        server_sock.close()
    print("All done.")

if __name__ == '__main__':
	#GPIO Mode (BOARD / BCM)
	GPIO.setmode(GPIO.BCM)
	 
	#set GPIO Pins
	GPIO_TRIGGER = 18
	GPIO_ECHO = 24
	 
	#set GPIO direction (IN / OUT)
	GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
	GPIO.setup(GPIO_ECHO, GPIO.IN)
  main()
  GPIO.cleanup()
