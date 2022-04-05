# WalkSoloPi

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

in the terminal of pi:
1) modify /etc/systemd/system/dbus-org.bluez.service changing

    ExecStart=/usr/lib/bluetooth/bluetoothd

    into

    ExecStart=/usr/lib/bluetooth/bluetoothd -C
    
2) sudo sdptool add SP
3) systemctl daemon-reload
4) service bluetooth restart
5) sudo hciconfig hci0 piscan


