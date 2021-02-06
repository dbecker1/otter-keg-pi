import time
import random
import RPi.GPIO as GPIO

LITERS_PER_PULSE = .00168

class FlowMeter():
  enabled = True
  pourVolume = 0.0
  pourClicks = 0
  pin = 0
  logger = None
  lastClick = 0

  def __init__(self, pin, logger):
    self.enabled = True
    self.pourVolume = 0.0
    self.pourClicks = 0
    self.pin = pin
    self.logger = logger

    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.RISING, callback=self.tick, bouncetime=20)

    self.logger.info("Flow meter initialized on pin {}".format(pin))

  def tick(self, channel):
    if not self.enabled:
        return

    self.pourClicks += 1
    self.pourVolume += LITERS_PER_PULSE
    self.lastClick = int(time.time() * 1000)

  def resetPour(self):
    self.pourVolume = 0
    self.pourClicks = 0
