#!/usr/bin/env python3

# Peep stepper motor 
import time
import requests
import logging
import board
import digitalio
from multiprocessing import Value
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
import rpi2c
from adafruit_pca9685 import PCA9685
import constants

class MockStepper:
    def __init__(self):
        pass

    def step(self, direction, style):
        pass

    def extend(self, steps):
        pass

    def retract(self, steps):
        pass

    def release(self):
        pass

class PeepStepper:
    def __init__(self, peep_stepper):
        self.peep = peep_stepper
        self.release()

    def step(self, direction, style, sleep):
        self.peep.onestep(direction=direction, style=style)
        if sleep > 0:
            time.sleep(sleep)

    def extend(self, steps, step_time):
        for i in range(steps, 0, -1):
            self.step(stepper.BACKWARD, stepper.DOUBLE, step_time)
        self.release()

    def retract(self, steps, step_time):
        for i in range(0, steps, 1):
            self.step(stepper.FORWARD, stepper.DOUBLE, step_time)
        self.release()

    def release(self):
        self.peep.release()


try:
    i2c = rpi2c.rpi_i2c(3)  # stepper driver on i2c 3
    kit = MotorKit(i2c=i2c, steppers_microsteps=32)
    peeper = PeepStepper(kit.stepper1)
except:
    peeper = MockStepper()

def peep_cleanup():
    peeper.retract(100, 0)
    time.sleep(5)
    peeper.extend(100, 0)
    
def peep_cycle(breathing, peeping, steps, step_time, wait):
    s = steps.value
    t = step_time.value
    w = wait.value
    sleep_time = 0.05
    # let everyone know peep open
    peeping.value = constants.OPENED
    peeper.retract(s, 0)
    sleep_count = (int)(w/sleep_time)
    for i in range(0, sleep_count):
        # breakout early if someone asked for close
        if peeping.value == constants.CLOSED:
            break
        time.sleep(sleep_time)
    peeper.extend(s, t)
    # let everyone know peep and breathing closed
    peeping.value = constants.CLOSED
    breathing.value = constants.CLOSED

def peep_help():
    print("Enter cmd")
    print("[e] [steps] to extend")
    print("[r] [steps] to retract")
    print("[t] [percent] to set top")
    print("[x] [cross] to set peep crossing")
    print("[y] [steps] to set peep steps")
    print("[z] [time] to set peep step time")
    print("[h] to print this")

def peep_request(setting, value):
    url = "http://192.168.86.31:3000/tune"
    r = requests.post(url, json={
        setting:value
    })
    
if __name__ == '__main__':
    peep_help()
    while True:
        try:
            user = input()
            if user == "":
                break
            if user == "h":
                peep_help()
                continue
            
            (cmd, val) = user.split()
            if cmd == "e":
                peeper.extend(int(val), 0.001)
            elif cmd == "r":
                peeper.retract(int(val), 0.001)
            elif cmd == "t":
                peep_request("top", int(val))
            elif cmd == "x":
                peep_request("pcross", float(val))
            elif cmd == "y":
                peep_request("pstep", int(val))
            elif cmd == "z":
                peep_request("pstept", float(val))
        except Exception as e:
            print(e)

