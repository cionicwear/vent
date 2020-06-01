# Sensor Manager
import time
from multiprocessing import Process, Queue, Array, Value
import logging

import board
import busio
import bme680
import d6f

import adafruit_lps35hw as LPS
import adafruit_ads1x15.ads1115 as ADS
import adafruit_mprls as MPRLS
from adafruit_ads1x15.analog_in import AnalogIn
import rpi2c
import valve

i2c_in = rpi2c.rpi_i2c(1)
i2c_ex = rpi2c.rpi_i2c(3)

class FlowSensorADS:
    class Data:
        def __init__(self):
            self.rate = 0
            
    def __init__(self, channel=ADS.P0):
        self.adc = ADS.ADS1115(i2c)
        self.chan = AnalogIn(self.adc, channel)
        self.data = self.Data()
        
    def read(self):
        self.data.rate = self.chan.voltage

class PressureSensorBME:
    class Data:
        def __init__(self):
            self.pressure = 0
            self.temperature = 0
            self.humidity = 0
            
    def __init__(self):
        try:
            self.bme = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except IOError:
            self.bme = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        except Exception as e:
            print(e)

        self.data = self.Data()
        self.bme.set_humidity_oversample(bme680.OS_1X)
        self.bme.set_pressure_oversample(bme680.OS_1X)
        self.bme.set_temperature_oversample(bme680.OS_1X)
        self.bme.set_filter(bme680.FILTER_SIZE_1)
        
        #sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
        #sensor.set_gas_heater_temperature(320)
        #sensor.set_gas_heater_duration(150)
        #sensor.select_gas_heater_profile(0)

    def read(self):
        if self.bme.get_sensor_data():
            self.data.pressure = self.bme.data.pressure
            self.data.temperature = self.bme.data.temperature
            self.data.humidity = self.bme.data.humidity

class FlowSensorD6F:
    class Data:
        def __init__(self):
            self.rate = 0

    def __init__(self, i2c):
        self.flow = d6f.D6F70A(i2c)
        self.data = self.Data()

    def read(self):
        self.data.rate = self.flow.read_flow()

class PressureSensorLPS:
    class Data:
        def __init__(self):
            self.pressure = 0
            self.temperature = 0
            self.humidity = 0

    def __init__(self, i2c, address=0x5D):
        self.lps = LPS.LPS35HW(i2c, address=address)
        self.lps.data_rate = LPS.DataRate.RATE_75_HZ
        self.data = self.Data()

    def read(self):
        self.data.pressure = self.lps.pressure
        self.data.temperature = self.lps.temperature

    def zero_pressure(self):
        self.lps.zero_pressure()

class PressureSensorMPRLS:
    class Data:
        def __init__(self):
            self.pressure = 0
            self.temperature = 0
            self.humidity = 0

    def __init__(self, i2c, address=0x5D):
        self.mprls = MPRLS.MPRLS(i2c)
        self.data = self.Data()

    def read(self):
        self.data.pressure = self.mprls.pressure

def check_pressure(pressure, breathing):
    # on negative pressure start breathing process
    if pressure < 1000:
        if breathing.value == 0:
            breathing.value = 1
            p = Process(target=valve.breath_relay, args=(breathing,2))
            p.start()

def sensor_prime(pressure_in_1, pressure_in_2, pressure_ex_1, pressure_ex_2):
    for i in range(0,100):
        time.sleep(0.0001)
        pressure_in_1.read()
        pressure_in_2.read()
        pressure_ex_1.read()
        pressure_ex_2.read()
            
def sensor_loop(times, in_pressure_1, in_pressure_2, in_flow, ex_pressure_1, ex_pressure_2, ex_flow, idx, count, debug):
    # inspiration 
    pressure_in_1 = PressureSensorLPS(i2c_in, address=0x5d)
    pressure_in_2 = PressureSensorLPS(i2c_in, address=0x5c)
    flow_in = FlowSensorD6F(i2c_in)

    # expiration
    pressure_ex_1 = PressureSensorLPS(i2c_ex, address=0x5d)
    pressure_ex_2 = PressureSensorLPS(i2c_ex, address=0x5c)
    flow_ex = FlowSensorD6F(i2c_ex)

    breathing = Value('i', 0)
    dc = 1

    # calibration routine
    sensor_prime(pressure_in_1, pressure_in_2, pressure_ex_1, pressure_ex_2)
    pressure_in_1.zero_pressure()
    pressure_in_2.zero_pressure()
    pressure_ex_1.zero_pressure()
    pressure_ex_2.zero_pressure()
    sensor_prime(pressure_in_1, pressure_in_2, pressure_ex_1, pressure_ex_2)

    while True:
        pressure_in_1.read()
        pressure_in_2.read()
        pressure_ex_1.read()
        pressure_ex_2.read()
        #flow_in.read()
        #flow_ex.read()

        idx.value += 1
        if idx.value >= count.value:
            idx.value = 0

        # update timestamp
        times[idx.value] = time.time()
        
        # inspiration
        p1 = pressure_in_1.data.pressure
        p2 = pressure_in_2.data.pressure
        in_pressure_1[idx.value] = p1
        in_pressure_2[idx.value] = p2
        # in_flow[idx.value] = flow_in.data.rate
        in_flow[idx.value] = 13.75 * (abs(p2-p1)**0.5)
        
        # expiration
        p1 = pressure_ex_1.data.pressure
        p2 = pressure_ex_2.data.pressure
        ex_pressure_1[idx.value] = p1
        ex_pressure_2[idx.value] = p2
        # ex_flow[idx.value] = flow_ex.data.rate
        ex_flow[idx.value] = 9.75 * (abs(p2-p1)**0.5)
                
        #check_pressure(breath_pressure[idx.value], breathing)
        if debug is not None:
            dc -= 1;
            if dc == 0:
                dc = debug
                print("%f %f %f %f %f %f %f" % (
                    times[idx.value],
                    in_pressure_1[idx.value],
                    in_pressure_2[idx.value],
                    in_flow[idx.value],
                    ex_pressure_1[idx.value],
                    ex_pressure_2[idx.value],
                    ex_flow[idx.value]))
             
        time.sleep(0.010) # 75Hz
    
if __name__ == '__main__':
    idx = Value('i', 0)
    count = Value('i', 1000)
    times = Array('d', range(count.value))
    in_pressure_1 = Array('d', range(count.value))
    in_pressure_2 = Array('d', range(count.value))
    in_flow = Array('d', range(count.value))
    ex_pressure_1 = Array('d', range(count.value))
    ex_pressure_2 = Array('d', range(count.value))
    ex_flow = Array('d', range(count.value))
    
    p = Process(target=sensor_loop, args=(
        times,
        in_pressure_1, in_pressure_2, in_flow,
        ex_pressure_1, ex_pressure_2, ex_flow,
        idx, count, 1))

    p.start()
    input()
    p.terminate()


