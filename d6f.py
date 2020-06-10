from micropython import const
import adafruit_bus_device.i2c_device as i2cdevice
from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_bits import RWBits, ROBits
from adafruit_register.i2c_bit import RWBit
import time

_REG_INIT = const(0x0B)


class D6F:
    """Driver for the Omron D6F-A* series flow meter
    """

    def __init__(self, i2c_bus, flow_range, address=0x6C):
        self._flow_range = flow_range
        self._i2c = i2cdevice.I2CDevice(i2c_bus, address)
        self._buffer = bytearray(6)

    def initialize(self):
        # initialize device
        self._buffer[0] = 0x0B
        self._buffer[1] = 0x00
        self._i2c.write(self._buffer, end=2)

    def sensor_control(self):
        # initialize
        self._buffer[0] = 0x00
        self._buffer[1] = 0xD0
        self._buffer[2] = 0x40
        self._buffer[3] = 0x18
        self._buffer[4] = 0x06
        self._i2c.write(self._buffer, end=5)

    def read_temperature(self):
        self.sensor_control()
        time.sleep(0.05)
        
        self._buffer[0] = 0x00
        self._buffer[1] = 0xD0
        self._buffer[2] = 0x61
        self._buffer[3] = 0x2c
        self._buffer[4] = 0x07
        self._i2c.write(self._buffer, end=5)
        self._i2c.readinto(self._buffer)

        raw = self._buffer[4] << 8 | self._buffer[5]
        return (raw - 10214) / 37.39

    def read_flow(self):
        self.sensor_control()
        time.sleep(0.05)

        self._buffer[0] = 0x00
        self._buffer[1] = 0xD0
        self._buffer[2] = 0x51
        self._buffer[3] = 0x2c
        self._buffer[4] = 0x07
        self._i2c.write(self._buffer, end=5)
        self._i2c.readinto(self._buffer)

        raw = self._buffer[4] << 8 | self._buffer[5]
        return (raw - 1024) * self._flow_range / 60000.0

class D6F10A(D6F):
    def __init__(self, i2c_bus, address=0x6C):
        D6F.__init__(self, i2c_bus, 10, address=address)

class D6F20A(D6F):
    def __init__(self, i2c_bus, address=0x6C):
        D6F.__init__(self, i2c_bus, 20, address=address)

class D6F70A(D6F):
    def __init__(self, i2c_bus, address=0x6C):
        D6F.__init__(self, i2c_bus, 70, address=address)
    

if __name__ == '__main__':
    import busio
    import board
    i2c = busio.I2C(board.SCL, board.SDA)
    flow = D6F70A(i2c)
    flow.sensor_control()
    time.sleep(0.05)

    while True:
        t = flow.read_temperature()
        f = flow.read_flow()
        print("temp: %f flow: %f" % (t, f))
        time.sleep(1)
        
    print('Bye')
