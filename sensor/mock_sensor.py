import random
import math
import time

class MockSensor:
    class Data:
        def __init__(self):
            self.pressure_1 = 0
            self.pressure_2 = 0
            self.flow = 0
            self.pf = random.random()
            self.pa = 4
            self.tf = random.random()
            self.ta = 3
            self.hf = random.random()
            self.ha = 6
        
    def __init__(self):
        random.seed()
        self.data = self.Data()

    def sine_data(self, f, a):
        t = time.time()
        return a * math.sin(f*t)

    def get_sensor_data(self):
        time.sleep(0.1) # mimic sensor sampling
        self.data.pressure_1 = self.sine_data(self.data.tf, self.data.ta)
        self.data.pressure_2 = self.sine_data(self.data.hf, self.data.ha)
        self.data.flow = self.sine_data(self.data.pf, self.data.pa)
        self.data.volume = self.sine_data(self.data.pf * 0.5, self.data.pa * 0.28)
        self.data.tidal = 488
        return True

def sensor_loop(times, flow, volume, tidal, o2_percent,
                pmin, pmax, expire, breathing, peeping,
                in_pressure_1, in_pressure_2, in_flow,
                ex_pressure_1, ex_pressure_2, ex_flow,
                idx, count, assist, peepx):

    in_sensor = MockSensor()
    ex_sensor = MockSensor()
    while True:
        in_sensor.get_sensor_data()
        ex_sensor.get_sensor_data()

        i = idx.value + 1
        if i >= count.value:
            i = 0
            
        times[i] = time.time()
        
        in_pressure_1[i] = in_sensor.data.pressure_1
        in_pressure_2[i] = in_sensor.data.pressure_2
        flow[i] = in_sensor.data.flow
        in_flow[i] = in_sensor.data.flow

        ex_pressure_1[i] = ex_sensor.data.pressure_1
        ex_pressure_2[i] = ex_sensor.data.pressure_2
        ex_flow[i] = ex_sensor.data.flow

        volume[i] = in_sensor.data.volume
        tidal[i] = ex_sensor.data.tidal
        pmin[i] = 5.0
        pmax[i] = 14.8
        expire[i] = 2.0
        o2_percent[i] = 21.0

        idx.value = i

        time.sleep(0.0001)
