import board
import busio
import bme680

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
