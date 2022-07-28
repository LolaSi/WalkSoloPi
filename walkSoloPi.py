import bluetooth
import subprocess
import os
from PIL import Image
import io
import threading

# Libraries for taking picture
from picamera import PiCamera
from time import sleep
#Libraries for distance
import RPi.GPIO as GPIO
import time

# counts number of pictures taken
counter = 0

# is the walk with me btn pressed 
loop_notifications = False

#set GPIO Pins straight sonar
GPIO_TRIGGER1 = 18
GPIO_ECHO1 = 24
#set GPIO Pins above sonar
GPIO_TRIGGER2 = 25
GPIO_ECHO2 = 8

"""
 takes picture with the camera provided
 saves it as ./photos/image/counter.png
 returns the path of the new picture
"""
def takePicture(camera):
	global counter
	try:
		camera.resolution = (640, 480)
		pic_path = './photos/image' + str(counter)+'.png'
		camera.capture(pic_path)
		camera.stop_preview()
		counter += 1
	finally:
		return pic_path


"""
sends a new picture over client_sock
"""
def sendPicture(client_sock, camera, msg_type):
    print("yay, going to take pic")
    pic_path = takePicture(camera)
    im = Image.open(pic_path)
    im_resize = im.resize((500,500))
    buff = io.BytesIO()
    im_resize.save(buff, format='PNG')
    byte_im = buff.getvalue()
    size = len(byte_im)
    print("size is:" ,size)
    msg_type = msg_type + ","
    client_sock.send(str(msg_type).encode())
    client_sock.send(str(size).encode())
    client_sock.send(byte_im)
     
    
"""
enables a specified sonar by GPIO_TRIGGER, GPIO_ECHO
and returns the distance measured with it
"""
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
        

    """
    Sends to client socket notifications about surrounding area;
    if the distance measured ahead is less then the client request, a picture will be sent
    if the distance measured above is less then the client request, the warning will be sent
    parameter client_sock: client socket
    parameter camera: the piCamera object
    parameter client_request: array [service_type, notification_frequency, distance_ahead, distance_above]
    """
def constant_notifications(client_sock, camera, client_request):
    global loop_notifications
    print("in thread loop")
    print(loop_notifications)
    warning = "0,branch"
    print(warning)
    while loop_notifications:
        dist_ahead = get_distance(GPIO_TRIGGER1, GPIO_ECHO1)
        print('dist_ahead:', dist_ahead)
        dist_above = get_distance(GPIO_TRIGGER2, GPIO_ECHO2)
        print('dist_above:', dist_above)
        if (dist_above < int(client_request[3])):
            print('branches')
            client_sock.send(warning.encode())
        if (dist_ahead < int(client_request[2])):
            print('take_pic')
            sendPicture(client_sock, camera, client_request[0])
        time.sleep(int(client_request[1]))


"""
Deletes all pictured in the folder photos
"""
def clear_directory():
    mydir = './photos'
    for f in os.listdir(mydir):
        os.remove(os.path.join(mydir,f))
	


"""
enables the buzzer for the specified duration
"""
def enable_buzzer(duration):
    print("before subprocess")
    subprocess.run(["python", "buzzer.py", duration])
        
    
def main():
    global loop_notifications
    camera = PiCamera()
    clear_directory()
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
                data = data.decode("utf-8")
                #request_data = data.decode("utf-8")
                client_request = data.split(",")
                print(client_request)
                service_type = client_request[0]
                print("service type ", service_type)
                if service_type == "1": #around me btn
                    sendPicture(client_sock, camera, service_type)
                if service_type == "2": #walk with me
                    loop_notifications = True
                    t = threading.Thread(target=constant_notifications, args=(client_sock, camera, client_request))
                    t.start()
                if service_type == "3": # find device btn
                    duration = client_request[1]
                    enable_buzzer(duration)  
                if service_type == "4": #stop walking with me
                    loop_notifications = False  
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
