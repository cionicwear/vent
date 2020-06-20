import board
import busio
import adafruit_lps35hw as LPS

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
        # pressure reading in hPa convert to Pa
        self.data.pressure = self.lps.pressure * 100 
        self.data.temperature = self.lps.temperature

    def zero_pressure(self):
        self.lps.zero_pressure()
