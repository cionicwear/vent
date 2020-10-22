#!/usr/bin/env python3

# Admin script for managing vent

import time
import socket
import requests
import logging
from multiprocessing import Value
import board
import digitalio

from adafruit_motorkit import MotorKit

import rpi2c
from actuator import peep
from sensor import sensor
from sensor.sensor_d6f import FlowSensorD6F
from sensor.sensor_lps import PressureSensorLPS
from actuator.valve import Breather

g_hostname = socket.gethostname()
g_ip_address = socket.gethostbyname(g_hostname)
g_tune_url = "http://%s:3000/tune" % (g_ip_address,)


def admin_help():
    print("Enter cmd")
    print("[c] [percent] calibrate inspiratory flow with percent valve open")
    print("[d] [percent] calibrate expiratory flow with percent valve open")
    print("[t] [percent] set max percent solenoid open")
    print("[x] [cross] set peep crossing threshold")
    print("[y] [steps] set number of steps for peep")
    print("[z] [seconds] set peep step time")
    print("[o] [0|50|100] set precent oxygen mix")
    print("[h] print this help screen")
    print("[] to exit")

def admin_request(setting, value):
    r = requests.post(g_tune_url, json={
        setting:value
    })

def flow_calibrate(bus, percent, count):
    print("runing calibration on bus %d" % (bus,))

    # setup pressure sensors and zero pressure them
    in_p1 = PressureSensorLPS(rpi2c.rpi_i2c(1), address=0x5d)
    in_p2 = PressureSensorLPS(rpi2c.rpi_i2c(1), address=0x5c)
    ex_p1 = PressureSensorLPS(rpi2c.rpi_i2c(3), address=0x5d)
    ex_p2 = PressureSensorLPS(rpi2c.rpi_i2c(3), address=0x5c)
    sensor.pressure_zero(in_p1, in_p2, ex_p1, ex_p2)
    
    flow = FlowSensorD6F(rpi2c.rpi_i2c(1))
    kit = MotorKit(i2c=rpi2c.rpi_i2c(1))
    breather = Breather(kit.motor1, kit.motor2)
    ox = Value('i', 0)

    if bus == 1:
        p1 = in_p1
        p2 = in_p2
    else:
        p1 = ex_p1
        p2 = ex_p2
        
    # open valve
    breather.throttle(percent, ox)
    total = 0
    samples = 0
    vmin = 100
    vmax = 0
    THRESH = 50

    logging.warning("Start calibration")
    for i in range(0,count):
        p1.read()
        p2.read()
        flow.read()
        r = flow.data.rate
        hp = p2.data.pressure
        lp = p1.data.pressure
        if hp > (lp + THRESH):
            vco = r / ((hp-lp)**0.5)
            total += vco
            samples += 1
            vmin = min(vco, vmin)
            vmax = max(vco, vmax)
            logging.warning("%f %f %f %f" % (r, vco, hp, lp))
        
        time.sleep(0.1)

    # close valve
    logging.warning("VCO: %f min %f max %f" % (total/samples, vmin, vmax))
    breather.throttle(0, ox)
    
if __name__ == '__main__':
    print("Connecting to vent @ %s" % (g_ip_address,))
    admin_help()
    while True:
        try:
            user = input()
            if user == "":
                break
            if user == "h":
                admin_help()
                continue
            
            (cmd, val) = user.split()
            if cmd == "c":
                flow_calibrate(1, int(val), 200)
            elif cmd == "d":
                flow_calibrate(3, int(val), 200)
            elif cmd == "t":
                admin_request("top", int(val))
            elif cmd == "x":
                admin_request("pcross", float(val))
            elif cmd == "y":
                admin_request("pstep", int(val))
            elif cmd == "z":
                admin_request("pstept", float(val))
            elif cmd == "o":
                admin_request("oxp", int(val))
        except Exception as e:
            print(e)

