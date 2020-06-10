# wrapper for multiple i2c busses
import logging
import board
import busio
from adafruit_blinka.microcontroller.generic_linux.i2c import I2C as _I2C
from microcontroller.pin import i2cPorts

def rpi_i2c(port=1, frequency=400000):
    i2c = busio.I2C(board.SCL, board.SDA)
    for portId, portScl, portSda in i2cPorts:
        if portScl == board.SCL and portSda == board.SDA and port == portId:
            i2c._i2c = _I2C(portId, mode=_I2C.MASTER, baudrate=frequency)
    return i2c
