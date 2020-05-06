import random
import math
import time

I2C_ADDR_PRIMARY = 1
I2C_ADDR_SECONDARY = 2
OS_1X = 1
FILTER_SIZE_1 = 1
DISABLE_GAS_MEAS = 1

class BME680:
    class mock_data:
        def __init__(self):
            self.pressure = 0
            self.temperature = 0
            self.humidity = 0
            self.pf = random.random()
            self.pa = 4
            self.tf = random.random()
            self.ta = 3
            self.hf = random.random()
            self.ha = 6
        
    def __init__(self, addr):
        random.seed()
        self.addr = addr
        self.data = self.mock_data()

    def sine_data(self, f, a):
        t = time.time()
        return a * math.sin(f*t)

    def get_sensor_data(self):
        time.sleep(0.1) # mimic sensor sampling
        self.data.temperature = self.sine_data(self.data.tf, self.data.ta)
        self.data.humidity = self.sine_data(self.data.hf, self.data.ha)
        self.data.pressure = self.sine_data(self.data.pf, self.data.pa)
        return True

    
    def set_humidity_oversample(self, value):
        pass
    
    def set_pressure_oversample(self, value):
        pass
    
    def set_temperature_oversample(self, value):
        pass
    
    def set_filter(self, value):
        pass
    
    def set_gas_status(self, value):
        pass
    
    def set_gas_heater_temperature(self, value):
        pass
    
    def set_gas_heater_duration(self, value):
        pass
    
    def select_gas_heater_profile(self, value):
        pass
