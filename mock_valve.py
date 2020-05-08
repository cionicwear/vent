# Servo Control
import time
import logging
from multiprocessing import Value

def breath_relay(breathing, seconds):
    '''
    breathing control for binary solenoid controlled by a relay
    '''
    breathing.value = 1
    logging.warning("breathing relay")
    time.sleep(seconds)
    breathing.value = 0

def breath_pwm(breathing, pulse, seconds):
    '''
    breathing control for proportional solenoids
    '''
    breathing.value = 1
    logging.warning("breathing %d for %ds" % (pulse, seconds))
    time.sleep(seconds)
    breathing.value = 0
