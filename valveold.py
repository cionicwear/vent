# Servo Control
import time
import pigpio
import logging

RELAY_PIN = 26
HIGH = 1
LOW = 0

def orders(pi, min_pulse, max_pulse, count):
    for i in range(0,count):
        pi.set_servo_pulsewidth(17, max_pulse)
        time.sleep(2)
        pi.set_servo_pulsewidth(17, min_pulse)
        time.sleep(2)

def breath_servo(breathing):
    pi = pigpio.pi()
    pi.set_servo_pulsewidth(17, 1500)
    time.sleep(2)
    pi.set_servo_pulsewidth(17, 1200)
    time.sleep(2)
    breathing.value = 0

def breath_relay(breathing):
    pi = pigpio.pi()
    pi.write(RELAY_PIN, HIGH)
    time.sleep(2)
    pi.write(RELAY_PIN, LOW)
    time.sleep(2)
    breathing.value = 0

def test(pi, pulse):
    pi.set_servo_pulsewidth(17, pulse)
    time.sleep(0.5)
    pi.set_servo_pulsewidth(17, 0)
    
            
if __name__ == '__main__':
    pi = pigpio.pi()

    print('Hit <ENTER> to disconnect')
    while True:
        user = input()
        if (user == ""):
            break
        try:
            num = int(user)
            test(pi, num)
        except Exception as e:
            print(e)
            
    print('Bye')

