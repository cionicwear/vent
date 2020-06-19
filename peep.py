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
        
def user_int(prompt, default=0):
    print(prompt)
    user = input()
    try:
        duty = int(user)
        return duty
    except Exception as e:
        print(e)
        return default

    
if __name__ == '__main__':
    i2c = rpi2c.rpi_i2c(1)
    kit = MotorKit(i2c=i2c, steppers_microsteps=32)
    peep = PeepStepper(kit.stepper1)    

    steps = user_int("Enter steps +10 -10")
    
    for i in range(20):
        for i in range(0, steps, 1):
            peep.step(stepper.FORWARD, stepper.DOUBLE)
        
        for i in range(steps, 0, -1):
            peep.step(stepper.BACKWARD, stepper.DOUBLE)
