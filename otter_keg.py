import time
import datetime
import os
import RPi.GPIO as GPIO
import logging
from logging.handlers import RotatingFileHandler
import json
from flow_meter import *
from database import *

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
log_file = "/tmp/logs/otter_keg.log"

# File log handler
# log_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
# Command line log handler
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)

GPIO.setmode(GPIO.BCM)

db = Database(logger)

logger.info("Starting Otter Keg")

while db.drinkers == [] or db.kegs == []:
    logger.info("Waiting for database init...")

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
            keg["meter"] = FlowMeter(pin, logger)
        kegs.append(keg)
    logger.info("Keg init")
    logger.info("Kegs value: {}".format(kegs))

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
                    logger.info("Creating new pour with id: {}. {}".format(pour_id, json.dumps(pour)))
                    keg["pour_id"] = new_pour_id
                else:
                    logger.info("Updating pour with id: {}. New Amount: {}".format(pour_id, str(meter.thisPour)))
                    db.update_pour(pour_id, round(meter.thisPour, 2))
            else:
                logger.info("Pour finished: {} liters".format(meter.thisPour))
                if pour_id is not None:
                    db.finish_pour(pour_id)
                    keg["pour_id"] = None
                meter.resetPour()
    continue