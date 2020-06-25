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

def valve_loop(breathing,
               start, start_time,
               top, top_time,
               down, down_time,
               bottom, bottom_time,
               count):
    
    breathing.value = 1
    logging.warning("breathing %ds" % (top_time,))
    time.sleep(top_time)
    breathing.value = 0
    time.sleep(bottom_time)
