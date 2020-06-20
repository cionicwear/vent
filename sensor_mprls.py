
import board
import busio
import adafruit_mprls as MPRLS
        
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
