# Servo Control
import time
import logging
import board
import digitalio
from multiprocessing import Value
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
import rpi2c
from adafruit_pca9685 import PCA9685

class PeepStepper:
    def __init__(self, peep_stepper):
        self.peep = peep_stepper

    def step(self, direction, style):
        self.peep.onestep(direction=direction, style=style)

    def cycle(self, steps):
        for i in range(0, steps, 1):
            self.step(stepper.FORWARD, stepper.DOUBLE)
        for i in range(steps, 0, -1):
            self.step(stepper.BACKWARD, stepper.DOUBLE)
        self.release()

    def cal_extend(self, steps):
        for i in range(steps, 0, -1):
            self.step(stepper.BACKWARD, stepper.DOUBLE)
        self.release()

    def cal_retract(self, steps):
        for i in range(0, steps, 1):
            self.step(stepper.FORWARD, stepper.DOUBLE)
        self.release()

    def release(self):
        self.peep.release()

i2c = rpi2c.rpi_i2c(3)  # stepper driver on i2c 3
kit = MotorKit(i2c=i2c, steppers_microsteps=32)
peeper = PeepStepper(kit.stepper2)

def peep_cycle(steps):
    peeper.cycle(steps)

if __name__ == '__main__':
    print("Enter [e] extend [r] retract [number] to cycle")
    while True:
        user = input()
        if user == "":
            break
        elif user == "e":
            peeper.cal_extend(50)
        elif user == "r":
            peeper.cal_retract(50)
        else:
            steps = int(user)
            for i in range(20):
                peep_cycle(steps)

