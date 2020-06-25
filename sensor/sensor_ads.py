import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

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



