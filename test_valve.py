#!/usr/bin/env python3

from multiprocessing import Process, Queue, Array, Value
from actuator import valve
import time
import rpi2c
from adafruit_motorkit import MotorKit
from actuator import valve
import argparse
import sys
        
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
    parser = argparse.ArgumentParser(description='Run vent')
    # times
    parser.add_argument('-i', '--inspire', default=1.0, type=float, help='seconds of inspiration time')
    parser.add_argument('-e', '--expire',  default=2.0, type=float, help='seconds of expiration time')
    parser.add_argument('-u', '--rampup',  default=0.1, type=float, help='seconds to ramp from <start> to <top>')
    parser.add_argument('-d', '--rampdn',  default=0.0, type=float, help='seconds to ramp from <top> to <pause> ')
    # thresholds
    parser.add_argument('-s', '--start',   default=80,  type=int, help='percent open at start of breathing cycle')
    parser.add_argument('-t', '--top',     default=100, type=int, help='percent open at peak of breathing cycle')
    parser.add_argument('-p', '--pause',   default=0,   type=int, help='percent open at pause in breathing cycle')
    parser.add_argument('-b', '--bottom',  default=0,   type=int, help='percent open at end of breathing cycle')
    # counts
    parser.add_argument('-c', '--count',   default=5,  type=int, help='number of breathing cycles')
    # peep
    parser.add_argument('-w', '--pwait',   default=1.0,   type=float, help='seconds to wait before closing peep')
    parser.add_argument('-x', '--pcross',  default=5,     type=float, help='peep crossing threshold')
    # o2
    parser.add_argument('-o', '--oxygen',  default=0, type=int, help='percent oxygen')
    
    args = parser.parse_args(sys.argv[1:])

    count = Value('i', 10)

    # state machine
    breathing = Value('i', 0)
    peeping = Value('i', 0)
    
    # fine grain settings
    top = Value('i', args.top)
    pwait = Value('d', args.pwait)
    pcross = Value('d', args.pcross)
    oxp = Value('i', args.oxygen)
    
    v = Process(target=valve.valve_loop, args=(
            breathing, peeping, oxp,
            args.start,  args.rampup,
            top, (args.inspire - args.rampup - args.rampdn),
            args.pause,  args.rampdn,
            args.bottom, args.expire,
            pwait,
            args.count))
    v.start()
    user = input()
    v.terminate()

