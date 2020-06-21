#!/usr/bin/env python3

# Peep stepper motor 
import time
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
    
def peep_cycle(breathing, peeping, steps, step_time, wait):
    peeping.value = constants.OPENED
    peeper.retract(steps, 0)
    sleep_time = 0.05
    sleep_count = (int)(wait/sleep_time)
    for i in range(0, sleep_count):
        if peeping.value == constants.CLOSED:
            break
        time.sleep(sleep_time)
    peeper.extend(steps, step_time)
    peeping.value = constants.CLOSED
    breathing.value = constants.CLOSED

if __name__ == '__main__':
    print("Enter [e] extend [r] retract [number] to cycle")
    while True:
        user = input()
        if user == "":
            break
        elif user == "e":
            peeper.extend(50, 0.001)
        elif user == "r":
            peeper.retract(50, 0.001)
        else:
            steps = int(user)
            for i in range(20):
                peep_cycle(steps, 1.0)

