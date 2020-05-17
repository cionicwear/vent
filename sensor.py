# Sensor Manager
import time
from multiprocessing import Process, Queue, Array, Value
import logging

import board
import busio
import bme680
import adafruit_lps35hw as LPS
import adafruit_ads1x15.ads1115 as ADS
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
        self.data = self.Data()

    def read(self):
        self.data.pressure = self.lps.pressure
        self.data.temperature = self.lps.temperature
        
def check_pressure(pressure, breathing):
    # on negative pressure start breathing process
    if pressure < 1000:
        if breathing.value == 0:
            breathing.value = 1
            p = Process(target=valve.breath_relay, args=(breathing,2))
            p.start()


def sensor_loop(times, tank_pressure, breath_pressure, flow, idx, count):
    flow_sensor = FlowSensor()
    pressure_1 = PressureSensorLPS(address=0x5d)
    pressure_2 = PressureSensorLPS(address=0x5c)
    breathing = Value('i', 0)
    while True:
        flow_sensor.read()
        pressure_1.read()
        pressure_2.read()

        idx.value += 1
        if idx.value >= count.value:
            idx.value = 0
        times[idx.value] = time.time()
        tank_pressure[idx.value] = pressure_1.data.pressure
        breath_pressure[idx.value] = pressure_2.data.pressure
        flow[idx.value] = flow_sensor.data.rate
        
        check_pressure(breath_pressure[idx.value], breathing)
        #print("%f %f %f" % (pressure_1.data.pressure, pressure_2.data.pressure, flow_sensor.data.rate))
             
        time.sleep(0.0001)
    
if __name__ == '__main__':
    idx = Value('i', 0)
    count = Value('i', 1000)
    times = Array('d', range(count.value))
    tank_pressure = Array('d', range(count.value))
    breath_pressure = Array('d', range(count.value))
    temperature = Array('d', range(count.value))
    flow = Array('d', range(count.value))
    
    p = Process(target=sensor_loop, args=(times, tank_pressure, breath_pressure, flow, idx, count))
    p.start()

    last = 0
    print("tank breath flow")
    while True:
        curr = idx.value
        if last > curr:
            tank_pressures = tank_pressure[last:] + tank_pressure[:curr]
            breath_pressures = breath_pressure[last:] + breath_pressure[:curr]
            flows = flow[last:]+flow[:curr]
        else:
            tank_pressures = tank_pressure[last:curr]
            breath_pressures = breath_pressure[last:curr]
            flows = flow[last:curr]
        #if len(flows) > 0 and len(tank_pressures) > 0 and len(breath_pressures):
        #    print("%f %f %f" % (tank_pressures[0], breath_pressures[0], flows[0]))
        last = curr
        time.sleep(1)
        
    print('Bye')

