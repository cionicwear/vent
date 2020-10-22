# Servo Control
import time
import logging
import board
import digitalio
from multiprocessing import Process, Value
from adafruit_motorkit import MotorKit
import rpi2c
from actuator import peep
import constants

class Breather:
    def __init__(self, breath_motor, ox_motor):
        self.breath_valve = breath_motor
        self.ox_valve = ox_motor
                
    def set_cycle(self,
                  start, start_time,
                  top, top_time,
                  down, down_time,
                  bottom):
        self.up_step = start_time/(top-start)
        self.dn_step = down_time/(top-down)
        self.top_time = top_time
        self.start = start
        self.down = down
        self.bottom = bottom
        
    def throttle(self, percent, oxp):
        if oxp.value == 100:
            self.ox_valve.throttle = percent/100.0
            self.breath_valve.throttle = 0
        elif oxp.value == 50:
            self.ox_valve.throttle = percent/120.0
            self.breath_valve.throttle = percent/120.0
        else:
            self.breath_valve.throttle = percent/100.0
            self.ox_valve.throttle = 0
        
    def cleanup(self, breathing, oxp):
        self.throttle(0, oxp)
        
    def breath(self, breathing, top, oxp):
        # inspire
        breathing.value = constants.INSPIRING
        
        # step up
        t = top.value
        for i in range(self.start, t, 1):
            self.throttle(i, oxp)
            time.sleep(self.up_step)

        # hold top
        self.throttle(t, oxp)
        time.sleep(self.top_time)
        
        # step down
        for i in range(t, self.down, -1):
            self.throttle(i, oxp)
            time.sleep(self.dn_step)

        # expire
        breathing.value = constants.EXPIRING
        self.throttle(self.bottom, oxp)

def peep_cycle(breathing, peeping, peep_wait):
    p = Process(target=peep.peep_cycle, args=(
        breathing, peeping, peep_wait))
    p.start()

def valve_loop(breathing, peeping, oxp,
               start, start_time,
               top, top_time,
               down, down_time,
               bottom, bottom_time,
               peep_wait,
               count):
    
    i2c = rpi2c.rpi_i2c(1)
    kit = MotorKit(i2c=i2c)
    
    breather = Breather(kit.motor2, kit.motor1)
    breather.set_cycle(
        start, start_time,
        top.value, top_time,
        down, down_time,
        bottom)

    peep.peep_calibrate(peeping)

    for i in range(0, count):
        # breath
        breather.breath(breathing, top, oxp)
        # peep
        peep_cycle(breathing, peeping, peep_wait)
        # wait
        sleep_time = 0.1
        sleep_count = (int)(bottom_time/sleep_time)
        for i in range(0, sleep_count):
            if breathing.value == constants.INSPIRING:
                break
            time.sleep(sleep_time)
            
    # cleanup
    logging.warn("cleaning up please wait")
    breather.cleanup(breathing, oxp)
    peep.peep_cleanup(peeping)
    logging.warn("done")

