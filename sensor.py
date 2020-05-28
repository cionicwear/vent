# Sensor Manager
import time
from multiprocessing import Process, Queue, Array, Value
import logging

import board
import busio
import bme680

import adafruit_lps35hw as LPS
import adafruit_ads1x15.ads1115 as ADS
import adafruit_mprls as MPRLS
from adafruit_ads1x15.analog_in import AnalogIn
import valve

i2c = busio.I2C(board.SCL, board.SDA)

class FlowSensor:
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

class PressureSensorLPS:
    class Data:
        def __init__(self):
            self.pressure = 0
            self.temperature = 0
            self.humidity = 0

    def __init__(self, address=0x5D):
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

    def __init__(self, address=0x5D):
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

def sensor_loop(times, tank_pressure, breath_pressure, v1_pressure, v2_pressure, flow, idx, count, debug):
    pressure_1 = PressureSensorLPS(address=0x5d)
    pressure_2 = PressureSensorLPS(address=0x5c)
    pressure_3 = PressureSensorMPRLS()
    breathing = Value('i', 0)
    dc = 1

    # start calibration routine
    for i in range(0,100):
        time.sleep(0.0001)
        pressure_1.read()
        pressure_2.read()
        pressure_3.read()

    # zero out sensors
    pressure_1.zero_pressure()
    pressure_2.zero_pressure()

    # clear readings
    for i in range(0,100):
        time.sleep(0.0001)
        pressure_1.read()
        pressure_2.read()
        pressure_3.read()

    while True:
        pressure_1.read()
        pressure_2.read()
        pressure_3.read()

        idx.value += 1
        if idx.value >= count.value:
            idx.value = 0

        t = time.time()
        p1 = pressure_1.data.pressure
        p2 = pressure_2.data.pressure
        dp = abs(p2-p1)
        f = 7.33656*(dp**0.5)
        bp = pressure_3.data.pressure

        times[idx.value] = t
        tank_pressure[idx.value] = 1.0
        breath_pressure[idx.value] = bp
        v1_pressure[idx.value] = p1
        v2_pressure[idx.value] = p2
        #flow[idx.value] = flow_sensor.data.rate
        flow[idx.value] = f
        
        #check_pressure(breath_pressure[idx.value], breathing)
        if debug is not None:
            dc -= 1;
            if dc == 0:
                dc = debug
                print("%f %f %f %f %f" % (t, p1, p2, f, bp))
             
        time.sleep(0.0001)
    
if __name__ == '__main__':
    idx = Value('i', 0)
    count = Value('i', 1000)
    times = Array('d', range(count.value))
    tank_pressure = Array('d', range(count.value))
    breath_pressure = Array('d', range(count.value))
    v1_pressure = Array('d', range(count.value))
    v2_pressure = Array('d', range(count.value))
    flow = Array('d', range(count.value))
    
    p = Process(target=sensor_loop, args=(times, tank_pressure, breath_pressure, v1_pressure, v2_pressure, flow, idx, count, 1))
    p.start()

    last = 0
    while True:
        curr = idx.value
        if last > curr:
            m_times = times[last:] + times[:curr]
            m_tank_pressure = tank_pressure[last:] + tank_pressure[:curr]
            m_breath_pressure = breath_pressure[last:] + breath_pressure[:curr]
            m_flow = flow[last:]+flow[:curr]
        else:
            m_times = times[last:curr]
            m_tank_pressure = tank_pressure[last:curr]
            m_breath_pressure = breath_pressure[last:curr]
            m_flow = flow[last:curr]
        last = curr
        time.sleep(1)
        
    print('Bye')

