# Servo Control
import time
import logging
import board
import digitalio
import pulseio
import pigpio
from multiprocessing import Value

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
    relay.value = True
    time.sleep(seconds)
    relay.value = False
    breathing.value = 0

def breath_pwm(breathing, pulse, seconds):
    '''
    breathing control for proportional solenoids
    '''
    print("breathing %d for %ds" % (pulse, seconds))
    pi.set_PWM_dutycycle(PWM_PIN, pulse)
    time.sleep(seconds)
    pi.set_PWM_dutycycle(PWM_PIN, 0)

                    
if __name__ == '__main__':
    breathing = Value('i', 0)
    print('Hit <ENTER> to disconnect')
    while True:
        user = input()
        if (user == ""):
            break
        try:
            seconds = int(user)
            breath_relay(seconds)
        except Exception as e:
            print(e)
            
    print('Bye')

