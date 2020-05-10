# Servo Control
import time
import logging
import board
import digitalio
#import pulseio
import pigpio
from multiprocessing import Value
from adafruit_motorkit import MotorKit

kit = MotorKit()
breath_valve = kit.motor1

RELAY_PIN = 26
HIGH = 1
LOW = 0

relay = digitalio.DigitalInOut(board.D26)
relay.direction = digitalio.Direction.OUTPUT

PWM_PIN = 21
pi = pigpio.pi()

def breath_relay(breathing, seconds):
    '''
    breathing control for binary solenoid controlled by a relay
    '''
    breathing.value = 1
    logging.warning("breathing relay for %ds" % (seconds,))
    relay.value = True
    time.sleep(seconds)
    relay.value = False
    breathing.value = 0

def breath_pwm(breathing, pulse, seconds):
    '''
    breathing control for proportional solenoids
    '''
    breathing.value = 1
    logging.warning("breathing %d for %ds" % (pulse, seconds))
    pi.set_PWM_dutycycle(PWM_PIN, pulse)
    time.sleep(seconds)
    pi.set_PWM_dutycycle(PWM_PIN, 0)
    breathing.value = 0

def breath_i2c(breathing, duty, seconds):
    breathing.value = 1
    logging.warning("breathing %d for %ds" % (duty, seconds))
    breath_valve.throttle = (duty/100)
    time.sleep(seconds)
    breath_valve.throttle = 0
    breathing.value = 0
    
if __name__ == '__main__':
    breathing = Value('i', 0)
    print('Enter a duty cycle between 1 and 100')
    print('Hit <ENTER> to disconnect')
    while True:
        user = input()
        if (user == ""):
            for i in range(80,100):
                breath_i2c(breathing, i, 2)
                time.sleep(1)
            break
        try:
            duty = int(user)
            breath_i2c(breathing, duty, 2)
        except Exception as e:
            print(e)
            
    print('Bye')

