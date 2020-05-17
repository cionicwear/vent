import random
import math
import time

class MockSensor:
    class Data:
        def __init__(self):
            self.tank_pressure = 0
            self.breath_pressure = 0
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
        self.data.tank_pressure = self.sine_data(self.data.tf, self.data.ta)
        self.data.breath_pressure = self.sine_data(self.data.hf, self.data.ha)
        self.data.flow = self.sine_data(self.data.pf, self.data.pa)
        return True


def sensor_loop(times, tank_pressure, breath_pressure, flow, idx, count):
    sensor = MockSensor()
    while True:
        if sensor.get_sensor_data():
            idx.value += 1
            if idx.value >= count.value:
                idx.value = 0
            times[idx.value] = time.time()
            tank_pressure[idx.value] = sensor.data.tank_pressure
            breath_pressure[idx.value] = sensor.data.breath_pressure
            flow[idx.value] = sensor.data.flow
        
        time.sleep(0.0001)
