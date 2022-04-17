import bluetooth
import subprocess
import os
from PIL import Image
import io

def sendPicture(client_sock):
    print("yay, going to take pic")
    #subprocess.run(["python", "still_pic.py"])
    im = Image.open('./photos/image.jpg')
    im_resize = im.resize((500,500))
    buff = io.BytesIO()
    im_resize.save(buff, format='PNG')
    byte_im = buff.getvalue()
    size = (str(len(byte_im))).encode()
    print(size)
    #client_sock.send(size)
    client_sock.send(byte_im)
    
    
    
    

def main():
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
            if data.decode("utf-8") == "1":
                sendPicture(client_sock)
            print("Received", data)
    except OSError:
        print("Disconnected.")

    client_sock.close()
    server_sock.close()
    print("All done.")

if __name__ == '__main__':
    main()
