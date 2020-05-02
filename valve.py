# Servo Control
import time
import logging
import board
import digitalio

RELAY_PIN = 26
HIGH = 1
LOW = 0

relay = digitalio.DigitalInOut(board.D26)
relay.direction = digitalio.Direction.OUTPUT


def breath_relay(breathing, seconds):
    '''
    breathing control for binary solenoid controlled by a relay
    '''
    relay.value = True
    time.sleep(seconds)
    relay.value = False
    breathing.value = 0
    
            
if __name__ == '__main__':

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

