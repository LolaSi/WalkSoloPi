# WalkSoloPi
by [Lola Sirota](https://github.com/LolaSi) & [Rebecca Tashman](https://github.com/tashmanr)

[Watch our demo](https://youtu.be/FM5iu6QRGuI)


The WalkSolo system is our solution to help enable independence for the visually impaired. The system allows the user to receive live updates regarding their surroundings. When using the WalkSolo device and the WalkSolo android app, the user is able to receive the warnings of incoming obstacles through their device.


## Technology implemented:
- Android TalkBalk (Accessibility)
- Android TextToSpeech
- Bluetooth Communication
- Integration with Google Vision API 
- Integration with Google Directions API

## Android Requirements:
- Target API 30

## Hardware Requirements:
- RaspberryPi
- PiCamera
- 2 HC-SR04 sonars
- Breadboard


## Pi Requirements:
- Python3
- PyBluez module
- Picamera module

Link to the raspberryPi code: https://github.com/tashmanr/WalkSolo

## In order to start up the WalkSolo device:
- First time use:
  - modify /etc/systemd/system/dbus-org.bluez.service changing ExecStart=/usr/lib/bluetooth/bluetoothd into ExecStart=/usr/lib/bluetooth/bluetoothd -C
  - sudo sdptool add SP
  - systemctl daemon-reload
  - service bluetooth restart
- run sudo python runService.py
