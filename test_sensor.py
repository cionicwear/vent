#!/usr/bin/env python3

from multiprocessing import Process, Queue, Array, Value
from sensor import sensor
import time

if __name__ == '__main__':
    idx = Value('i', 0)
    count = Value('i', 1000)
    times = Array('d', range(count.value))

    breathing = Value('i', 0)
    peeping = Value('i', 0)
    flow = Array('d', range(count.value))
    volume = Array('d', range(count.value))
    tidal = Array('d', range(count.value))
    pmin = Array('d', range(count.value))
    pmax = Array('d', range(count.value))
    expire = Array('d', range(count.value))
        
    in_pressure_1 = Array('d', range(count.value))
    in_pressure_2 = Array('d', range(count.value))
    in_flow = Array('d', range(count.value))
    ex_pressure_1 = Array('d', range(count.value))
    ex_pressure_2 = Array('d', range(count.value))
    ex_flow = Array('d', range(count.value))
    o2_percent = Array('d', range(count.value))
    
    pcross = Value('d', 0)
    pstept = Value('d', 0)
    assist = Value('d', 0)
    
    p = Process(target=sensor.sensor_loop, args=(
        times, flow, volume, tidal, o2_percent,
        pmin, pmax, expire, breathing, peeping,
        in_pressure_1, in_pressure_2, in_flow,
        ex_pressure_1, ex_pressure_2, ex_flow,
        idx, count, assist, pcross))

    p.start()
    while True:
        time.sleep(1.0)
        curr = idx.value
        print("o2 %f" % o2_percent[curr]) 
        print("inp1 %f" % in_pressure_1[curr])
        print("inp2 %f" % in_pressure_2[curr])
        print("exp1 %f" % ex_pressure_1[curr])
        print("exp2 %f" % ex_pressure_2[curr])
        
    p.terminate()
