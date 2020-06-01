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

def breath_i2c(breathing, start, duty, end, up, down, maintain=0):
    breathing.value = 1

    up_step = up/(duty-start)
    down_step = down/(duty-end)
    print(up_step, down_step)
    
    # increase flow
    for i in range(start, duty, 1):
        breath_valve.throttle = (i/100.0)
        time.sleep(up_step)

    # decrease flow
    for i in range(duty, end, -1):
        breath_valve.throttle = (i/100.0)
        time.sleep(down_step)

    
    breath_valve.throttle = maintain/100
    breathing.value = 0

def peep_i2c(duty):
    peep_valve.throttle = (duty/100)

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
    breathing = Value('i', 0)

    print('Hit <ENTER> to disconnect')
    while True:
        duty = user_int('Enter PEEP duty')
        peep_i2c(duty)
        duty = user_int('Enter Breath duty (0 to exit)')
        if (duty == 0):
            for i in range(80,100):

                # reasonably good volume control mode
                breath_i2c(breathing, 79, i, i-1, 0.05, 0.95, maintain=0)
                
                # best effort pressure control
                # breath_i2c(breathing, 80, 100, 80, 0.02, 1.08, maintain=0)
                
                time.sleep(2)
            break
        else:
            breath_i2c(breathing, duty-1, duty, duty-1, 0, 1)

    breath_valve.throttle = 0
    peep_valve.throttle = 0
    
    print('Bye')

