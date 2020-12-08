import time
import datetime
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
            "pin": db.config[rawKeg["position"] + "Pin"],
            "pour_id": None
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
        if meter.thisPour >= .02:
            pour_id = keg["pour_id"]
            if currentTime - meter.lastClick < 2000:
                if pour_id is None:
                    pour = {
                        "keg_id": keg["id"],
                        "drinker_id": db.get_active_drinker()["id"],
                        "isCurrent": True,
                        "amount": round(meter.thisPour, 2),
                        "start": str(datetime.datetime.now().isoformat()),
                        "last_update": str(datetime.datetime.now().isoformat())
                    }
                    new_pour_id = db.create_pour(pour)
                    print("Creating new pour with id: ", new_pour_id)
                    print(pour)
                    keg["pour_id"] = new_pour_id
                else:
                    print("Updating pour with id: ", pour_id)
                    print("New value: ", meter.thisPour)
                    db.update_pour(pour_id, round(meter.thisPour, 2))
            else:
                print("Pour finished: ", meter.thisPour, " liters")
                if pour_id is not None:
                    db.finish_pour(pour_id)
                    keg["pour_id"] = None
                meter.resetPour()
    continue