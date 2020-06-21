# Servo Control
import time
import logging
import board
import digitalio
from multiprocessing import Process, Value
from adafruit_motorkit import MotorKit
import rpi2c
import peep
import constants

class Mixer:
    def __init__(self, gas1_motor, gas2_motor):
        self.gas1_valve = gas1_motor
        self.gas2_valve = gas2_motor
        
        
    def mix(self, gas_1, gas_2):
        self.gas1_valve.throttle = gas_1/100.0
        self.gas2_valve.throttle = gas_2/100.0
        
class Breather:
    def __init__(self, breath_motor):
        self.breath_valve = breath_motor
                
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
        
    def throttle(self, percent):
        self.breath_valve.throttle = percent/100.0

    def cleanup(self, breathing):
        self.throttle(0)
        
    def breath(self, breathing, top):
        # inspire
        breathing.value = constants.INSPIRING
        
        # step up
        t = top.value
        for i in range(self.start, t, 1):
            self.throttle(i)
            time.sleep(self.up_step)

        # hold top
        self.throttle(t)
        time.sleep(self.top_time)
        
        # step down
        for i in range(t, self.down, -1):
            self.throttle(i)
            time.sleep(self.dn_step)

        # expire
        breathing.value = constants.EXPIRING
        self.throttle(self.bottom)

        
def user_int(prompt, default=0):
    print(prompt)
    user = input()
    try:
        duty = int(user)
        return duty
    except Exception as e:
        print(e)
        return default

def peep_cycle(breathing, peeping, peep_steps, peep_step_time, peep_wait):
    p = Process(target=peep.peep_cycle, args=(
        breathing, peeping, peep_steps, peep_step_time, peep_wait))
    p.start()

def valve_loop(breathing, peeping,
               start, start_time,
               top, top_time,
               down, down_time,
               bottom, bottom_time,
               peep_steps, peep_step_time, peep_wait,
               count):
    
    i2c = rpi2c.rpi_i2c(1)
    kit = MotorKit(i2c=i2c)
    
    breather = Breather(kit.motor1)
    breather.set_cycle(
        start, start_time,
        top.value, top_time,
        down, down_time,
        bottom)

    for i in range(0, count):
        # breath
        breather.breath(breathing, top)
        # peep
        peep_cycle(breathing, peeping, peep_steps, peep_step_time, peep_wait)
        # wait
        sleep_time = 0.1
        sleep_count = (int)(bottom_time/sleep_time)
        for i in range(0, sleep_count):
            if breathing.value == constants.INSPIRING:
                break
            time.sleep(sleep_time)
            
    # cleanup
    logging.warn("cleaning up please wait")
    breather.cleanup(breathing)
    peep.peep_cleanup()
    logging.warn("done")

if __name__ == '__main__':
    breathing = Value('i', 0)
    i2c = rpi2c.rpi_i2c(1)
    kit = MotorKit(i2c=i2c)
    mixer = Mixer(kit.motor3, kit.motor4)
    breather = Breather(kit.motor1, kit.motor2)
    
    print('Hit <ENTER> to disconnect')
    while True:
        duty = user_int('Enter Breath duty (0 to exit)')
        mixer.mix(100,0)
        breather.set_cycle(80, 0.1,
                           duty, 1.0,
                           0, 0,
                           0)
        for i in range(0, 5):
            breather.breath(breathing, 500)
            time.sleep(2.0)
        mixer.mix(0,0)
        breather.throttle(0)
    
    print('Bye')

