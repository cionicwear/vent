#!/usr/bin/env python3

# Peep stepper motor 
import time
import constants
import requests
import logging
import board
import digitalio
from multiprocessing import Value
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
import rpi2c
from adafruit_pca9685 import PCA9685
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

PEEP_SLEEP = 20
PEEP_STROKE = 2.0 # seconds for full peep actuator stroke
PEEP_DEBOUNCE = 3

class PeepMock:
    def __init__(self):
        pass

    def extend(self, peeping):
        pass

    def retract(self, peeping):
        pass

class PeepFeedback:
    def __init__(self, peep_motor, peep_adc, channel):
        self.peep = peep_motor
        self.adc = peep_adc
        self.chan = AnalogIn(self.adc, channel)
        self.max_v = 3.3
        self.min_v = 0
        self.debounce = 0

    def curr(self):
        return (self.chan.voltage - self.min_v) * 100 / (self.max_v - self.min_v)
    
    def extend(self, peeping=None, duty=1.0):
        self.peep.throttle = -duty
        sleep_count = PEEP_SLEEP
        sleep_time = PEEP_STROKE/sleep_count
        self.debounce = 0
        for i in range(0, sleep_count):
            # breakout if I hit max
            if self.chan.voltage > self.max_v:
                self.debounce += 1
                if self.debounce > PEEP_DEBOUNCE:
                    break
            else:
                self.debounce = 0
            # sleep
            time.sleep(sleep_time)
        self.peep.throttle = 0
        
    def retract(self, peeping=None, duty=1.0):
        self.peep.throttle = duty
        sleep_count = PEEP_SLEEP
        sleep_time = PEEP_STROKE/sleep_count
        self.debounce = 0
        for i in range(0, sleep_count):
            # breakout early if someone asked for close
            if peeping and peeping.value == constants.CLOSED:
                break
            # breakout if I hit min
            if self.chan.voltage < self.min_v:
                self.debounce += 1
                if self.debounce > PEEP_DEBOUNCE:
                    break
            else:
                self.debounce = 0
            # sleep
            time.sleep(sleep_time)
        self.peep.throttle = 0

    def median(self, count, secs):
        arr = []
        for i in range(0, count):
            arr.append(self.chan.voltage);
            time.sleep(secs)
        srtd = sorted(arr)
        return srtd[int(count/2)]


try:
    i2c = rpi2c.rpi_i2c(1)
    kit = MotorKit(i2c=i2c)
    adc = ADS.ADS1015(i2c)
    peeper = PeepFeedback(kit.motor3, adc, ADS.P0)
except:
    peeper = PeepMock()

def peep_cleanup(peeping):
    time.sleep(PEEP_STROKE)
    peeper.retract()
    time.sleep(PEEP_STROKE)
    peeper.extend()

def peep_calibrate(peeping, err=0.1):
    print("peeper min %f max %f" % (peeper.min_v, peeper.max_v))
    peeper.retract()
    time.sleep(PEEP_STROKE)
    peeper.min_v = peeper.median(10, 0.1) + err
    peeper.extend()
    time.sleep(PEEP_STROKE)
    peeper.max_v = peeper.median(10, 0.1) - err
    print("peeper min %f max %f" % (peeper.min_v, peeper.max_v))
    
def peep_cycle(breathing, peeping, wait):
    w = wait.value
    sleep_time = 0.05
    # let everyone know peep open
    peeping.value = constants.OPENED
    peeper.retract(peeping)
    sleep_count = (int)(w/sleep_time)
    for i in range(0, sleep_count):
        # breakout early if someone asked for close
        if peeping.value == constants.CLOSED:
            print("peep closed")
            break
        time.sleep(sleep_time)
    peeper.extend(peeping)
    # let everyone know peep and breathing closed
    peeping.value = constants.CLOSED
    breathing.value = constants.CLOSED

