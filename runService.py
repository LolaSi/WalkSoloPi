#!/usr/bin/env python3

import sys
import signal
import logging
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GObject, GLib
import subprocess

BLUEZ_SERVICE_NAME = "org.bluez"
DBUS_OM_IFACE =      "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE =    "org.freedesktop.DBus.Properties"

LOG_FILE = "log_btminder.txt"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
stream = logging.StreamHandler()
stream.setFormatter(logging.Formatter(LOG_FORMAT))
stream.setLevel(logging.DEBUG)

logger.addHandler(stream)

def device_property_changed_cb(iface, changed_props, invalidated_props, path=None, interface=None):
    if iface != "org.bluez.Device1":
        return
    device = dbus.Interface(bus.get_object("org.bluez", path), DBUS_PROP_IFACE)
    properties = device.GetAll("org.bluez.Device1")

# Replace with your code
    if "Connected" in changed_props:
        action = "connected" if properties["Connected"] else "disconnected"
        logger.info("The device {} [{}] is {}".format(properties["Alias"], properties["Address"], action))
        print("before subprocess")
        subprocess.run(["sudo", "hciconfig", "hci0", "piscan"])
        
        subprocess.run(["sudo","python3", "walkSoloPi.py"])

    if "RSSI" in changed_props:
        dBs = properties["RSSI"]
        logger.info("Proximity {}: {} dB".format(properties["Address"], dBs))

def shutdown(signum, frame):
    mainloop.quit()

if __name__ == "__main__":
    # shut down on a TERM signal
    signal.signal(signal.SIGTERM, shutdown)
    logger.info("Starting BTminder to monitor Bluetooth connections")

    # Get the system bus
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
    except Exception as ex:
        logger.error("Unable to get the system bus: {}. Is D-Bus running? Exiting BTminder".format(ex.message))
        sys.exit(1)

    # listen for signals on the Bluez bus
    bus.add_signal_receiver(
            device_property_changed_cb,
            bus_name=BLUEZ_SERVICE_NAME,
            signal_name="PropertiesChanged",
            path_keyword="path",
            interface_keyword="interface")
    try:
        mainloop = GLib.MainLoop.new(None, False)
        mainloop.run()
    except KeyboardInterrupt:
        pass
    except:
        logger.error("Unable to run the GLib.MainLoop")

    logger.info("Shutting down BTminder")
    sys.exit(0)
