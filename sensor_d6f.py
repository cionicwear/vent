import board
import busio
import d6f

class FlowSensorD6F:
    class Data:
        def __init__(self):
            self.rate = 0

    def __init__(self, i2c):
        self.flow = d6f.D6F70A(i2c)
        self.data = self.Data()

    def read(self):
        self.data.rate = self.flow.read_flow()
