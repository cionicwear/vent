# read oxygen sensor
import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import rpi2c
import logging

class MockOxygen:
    def __init__(self, i2c):
        pass

    def calibrate(self):
        pass

    def read(self):
        return 21.0
    

class OxygenADS:
    def __init__(self, i2c):
        self.i2c = i2c
        
        self.ads = ADS.ADS1015(i2c)
        self.chan = AnalogIn(self.ads, ADS.P0)
        self.calibration = 0
        self.percent = 0
        
    def calibrate(self):
        sample_sum = 0
        num_samples = 50
        for i in range(0,num_samples):
            sample_sum += self.chan.voltage
            time.sleep(0.05)
        self.calibration = sample_sum / num_samples

    def read(self):
        # datasheet : https://cdn.shopify.com/s/files/1/1275/4659/files/SS-26.pdf?867825592994555160
        self.percent = self.chan.voltage * 2000
        return self.percent
        
if __name__ == '__main__':
    i2c = rpi2c.rpi_i2c(3)
    sensor = OxygenADS(i2c)
    sensor.calibrate()
    while True:
        print(sensor.read())
        time.sleep(0.5)

