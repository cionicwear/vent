# Servo Control
import time
import logging
import board
import digitalio
from multiprocessing import Value
from adafruit_motorkit import MotorKit
import rpi2c

i2c = rpi2c.rpi_i2c(1)

kit = MotorKit(i2c=i2c)
breath_valve = kit.motor1
peep_valve = kit.motor2

RELAY_PIN = 26
HIGH = 1
LOW = 0

relay = digitalio.DigitalInOut(board.D26)
relay.direction = digitalio.Direction.OUTPUT

def breath_relay(breathing, seconds):
    '''
    breathing control for binary solenoid controlled by a relay
    '''
    breathing.value = 1
    relay.value = True
    time.sleep(seconds)
    relay.value = False
    breathing.value = 0

def throttle_i2c(throttle):
    breath_valve.throttle = throttle/100.0
    
def breath_i2c(breathing,
               start, start_time,
               top, top_time,
               down, down_time,
               bottom, bottom_time):
    
    breathing.value = 1

    print("breathing %f %f %f %f %f %f %f %f" %
          (start, start_time,
           top, top_time,
           down, down_time,
           bottom, bottom_time))
    
    start_step = start_time/(top-start)
    down_step = down_time/(top-down)
        
    # step up
    for i in range(start, top, 1):
        breath_valve.throttle = (i/100.0)
        time.sleep(start_step)

    # hold top
    breath_valve.throttle = top/100.0
    time.sleep(top_time)
    
    # step down
    for i in range(top, down, -1):
        breath_valve.throttle = (i/100.0)
        time.sleep(down_step)

    # hold bottom
    breath_valve.throttle = bottom/100.0
    breathing.value = 0
    time.sleep(bottom_time)

def user_int(prompt, default=0):
    print(prompt)
    user = input()
    try:
        duty = int(user)
        return duty
    except Exception as e:
        print(e)
        return default

def valve_loop(breathing,
               start, start_time,
               top, top_time,
               down, down_time,
               bottom, bottom_time,
               count):
    
    for i in range(0, count):
        breath_i2c(
            breathing,
            start, start_time,
            top, top_time,
            down, down_time,
            bottom, bottom_time)

    throttle_i2c(0)
        
if __name__ == '__main__':
    breathing = Value('i', 0)

    print('Hit <ENTER> to disconnect')
    while True:
        duty = user_int('Enter Breath duty (0 to exit)')
        if (duty == 0):
            # reasonably good volume control mode
            valve_loop(
                breathing,
                80, 0.1,   # ramp up
                90, 0.9,   # hold top
                0,  0,     # ramp down
                0,  2.0,    # hold bottom
                20
            )
                
            # best effort pressure control
            # breath_i2c(breathing, 90, 100, 80, 0.02, 1.98, maintain=0)
            break
        else:
            breath_i2c(breathing, duty-1, 0.1, duty, 0.9, 0, 0, 0, 2)

    breath_valve.throttle = 0
    
    print('Bye')

