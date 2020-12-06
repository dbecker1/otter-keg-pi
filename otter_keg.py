import time
import os
import RPi.GPIO as GPIO
from flow_meter import *
from database import *

GPIO.setmode(GPIO.BCM)

kegs = [{
    "meter": FlowMeter(13),
    "name": "Left Beer"
}]

db = Database()

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