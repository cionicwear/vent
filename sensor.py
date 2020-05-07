# Sensor Manager
import time
from multiprocessing import Process, Queue, Array, Value
import logging

try:
    import board
    import bme680
    import valve
except:
    import mock_bme as bme680
    import mock_valve as valve

def init_sensor():
    try:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    except Exception as e:
        print(e)


    sensor.set_humidity_oversample(bme680.OS_1X)
    sensor.set_pressure_oversample(bme680.OS_1X)
    sensor.set_temperature_oversample(bme680.OS_1X)
    sensor.set_filter(bme680.FILTER_SIZE_1)
    #sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
    #sensor.set_gas_heater_temperature(320)
    #sensor.set_gas_heater_duration(150)
    #sensor.select_gas_heater_profile(0)
    return sensor

def check_pressure(pressure, breathing):
    # on negative pressure start breathing process
    if pressure < 1000:
        if breathing.value == 0:
            breathing.value = 1
            p = Process(target=valve.breath_relay, args=(breathing,2))
            p.start()


def sensor_loop(times, pressure, humidity, temperature, idx, count):
    sensor = init_sensor()
    breathing = Value('i', 0)
    while True:
        if sensor.get_sensor_data():
            idx.value += 1
            # circle the circular buffer
            if idx.value >= count.value:
                idx.value = 0
            times[idx.value] = time.time()
            pressure[idx.value] = sensor.data.pressure
            humidity[idx.value] = sensor.data.humidity
            temperature[idx.value] = sensor.data.temperature

            check_pressure(pressure[idx.value], breathing)
                    
        time.sleep(0.0001)
    
if __name__ == '__main__':
    idx = Value('i', 0)
    count = Value('i', 1000)
    times = Array('d', range(count.value))
    pressure = Array('d', range(count.value))
    humidity = Array('d', range(count.value))
    temperature = Array('d', range(count.value))
    
    p = Process(target=sensor_loop, args=(times,pressure,humidity,temperature,idx,count))
    p.start()

    last = 0
    while True:
        curr = idx.value
        if last > curr:
            sub = pressure[last:]+pressure[:curr]
        else:
            sub = pressure[last:curr]
        print(len(sub))
        last = curr
        time.sleep(1)
        
    print('Bye')

