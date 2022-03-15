import bluetooth

server_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port=1

server_socket.bind(("",port))
server_socket.listen(1)

client_socket, address = server_socket.accept()
print "Accepted Connection from ", address

while true:
    data = client_socket.recv(1024)
    print "Received: %s" % data
    if (data == "0"):    #if '0' is sent from the Android App, send picture 
        print ("sending pic")
    if (data == "q"):
        print ("Quit")
        break
 
client_socket.close()
server_socket.close()

