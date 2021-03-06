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

#set GPIO Pins straight sonar
GPIO_TRIGGER1 = 18
GPIO_ECHO1 = 24
#set GPIO Pins above sonar
GPIO_TRIGGER2 = 25
GPIO_ECHO2 = 8

def takePicture(camera):
	global counter
	try:
		camera.resolution = (640, 480)
		camera.start_preview()
		sleep(5)
		pic_path = './photos/image' + str(counter)+'.png'
		#camera.capture('./photos/image.png')
		camera.capture(pic_path)
		camera.stop_preview()
		counter += 1
	finally:
		return pic_path


def sendPicture(client_sock, camera):
    print("yay, going to take pic")
    pic_path = takePicture(camera)
    #subprocess.run(["python", "still_pic.py"])
    #im = Image.open('./photos/image.png')
    im = Image.open(pic_path)
    im_resize = im.resize((500,500))
    buff = io.BytesIO()
    im_resize.save(buff, format='PNG')
    byte_im = buff.getvalue()
    #size = (str(len(byte_im))).encode()
    size = len(byte_im)
    print("size is:" ,size)
    client_sock.send(str(size).encode())
    client_sock.send(byte_im)
     
    

def get_distance(GPIO_TRIGGER, GPIO_ECHO):
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
    
def clear_directory():
    mydir = './photos'
    for f in os.listdir(mydir):
        os.remove(os.path.join(mydir,f))
        
        
def enable_buzzer():
    print("before subprocess")
    subprocess.run(["python", "buzzer.py"])
    
def main():
    camera = PiCamera()
    clear_directory()
    warning = "branch"
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
                    sendPicture(client_sock, camera)
                if data.decode("utf-8") == "2":
                    while True:
                        dist_ahead = get_distance(GPIO_TRIGGER1, GPIO_ECHO1)
                        print('dist_ahead:', dist_ahead)
                        dist_above = get_distance(GPIO_TRIGGER2, GPIO_ECHO2)
                        print('dist_above:', dist_above)
                        if (dist_above < 30):
                            print('branches')
                        if (dist_ahead < 150):
                            print('take_pic')
                        time.sleep(5)
                        #client_sock.send(warning.encode())
                if data.decode("utf-8") == "3":
                    enable_buzzer()          
        except OSError:
            print("Disconnected.")

        client_sock.close()
        server_sock.close()
    print("All done.")

if __name__ == '__main__':
	#GPIO Mode (BOARD / BCM)
	GPIO.setmode(GPIO.BCM)
	 
	#set GPIO Pins straight sonar
	GPIO_TRIGGER1 = 18
	GPIO_ECHO1 = 24
	
	#set GPIO Pins above sonar
	GPIO_TRIGGER2 = 25
	GPIO_ECHO2 = 8
	 
	#set GPIO direction (IN / OUT)
	GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
	GPIO.setup(GPIO_ECHO1, GPIO.IN)
	GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
	GPIO.setup(GPIO_ECHO2, GPIO.IN)
main()
GPIO.cleanup()
camera.close()
