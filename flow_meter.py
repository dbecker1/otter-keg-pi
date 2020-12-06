import time
import random
import RPi.GPIO as GPIO


class FlowMeter():
  SECONDS_IN_A_MINUTE = 60
  MS_IN_A_SECOND = 1000.0
  enabled = True
  clicks = 0
  lastClick = 0
  clickDelta = 0
  hertz = 0.0
  flow = 0 # in Liters per second
  thisPour = 0.0 # in Liters
  totalPour = 0.0 # in Liters
  pin = 0

  def __init__(self, pin):
    self.clicks = 0
    self.lastClick = int(time.time() * FlowMeter.MS_IN_A_SECOND)
    self.clickDelta = 0
    self.hertz = 0.0
    self.flow = 0.0
    self.thisPour = 0.0
    self.totalPour = 0.0
    self.enabled = True
    self.pin = pin

    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(13, GPIO.RISING, callback=self.tick, bouncetime=20)

    print("Flow meter initialized on pin ", pin)

  def tick(self, channel):
    if not self.enabled:
        return
    currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)

    self.clicks += 1
    # get the time delta
    self.clickDelta = max((currentTime - self.lastClick), 1)
    # calculate the instantaneous speed
    if (self.enabled == True and self.clickDelta < 1000):
      self.hertz = FlowMeter.MS_IN_A_SECOND / self.clickDelta
      self.flow = self.hertz / (FlowMeter.SECONDS_IN_A_MINUTE * 7.5)  # In Liters per second
      instPour = self.flow * (self.clickDelta / FlowMeter.MS_IN_A_SECOND)  
      self.thisPour += instPour
      self.totalPour += instPour
    # Update the last click
    self.lastClick = currentTime

  def getFormattedClickDelta(self):
    return str(self.clickDelta) + ' ms'
  
  def getFormattedHertz(self):
    return str(round(self.hertz,3)) + ' Hz'
  
  def getFormattedFlow(self):
    return str(round(self.flow,3)) + ' L/s'
  
  def getFormattedThisPour(self):
    return str(round(self.thisPour,3)) + ' L'
  
  def getFormattedTotalPour(self):
    return str(round(self.totalPour,3)) + ' L'
  
  def resetPour(self):
    self.thisPour = 0

  def clear(self):
    self.thisPour = 0
    self.totalPour = 0

