import time
import os
import RPi.GPIO as GPIO
from flow_meter import *
from database import *

GPIO.setmode(GPIO.BCM)

db = Database()

while db.drinkers == [] or db.kegs == []:
    print("Waiting for init...")

kegs = []

# future state: call this when kegs are changed 
def init_kegs():
    global kegs 
    kegs = []
    for rawKeg in db.kegs:
        keg = {
            "id": rawKeg["id"],
            "position": rawKeg["position"],
            "pin": db.config[rawKeg["position"] + "Pin"]
        }
        pin_key = rawKeg["position"] + "Pin"
        if pin_key in db.config:
            pin = db.config[pin_key]
            keg["pin"] = pin
            keg["meter"] = FlowMeter(pin)
        kegs.append(keg)
    print("Kegs updated. Current value: ", kegs)

init_kegs()

while True:
    currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)

    for keg in kegs:
        meter = keg["meter"]
        if meter.thisPour >= .05:
            if currentTime - meter.lastClick < 2000:
                print("Pouring")
            else:
                print("Pour finished: ", meter.thisPour, " liters")
                meter.resetPour()
    continue