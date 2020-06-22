# Sensor Manager
import time
from datetime import datetime
from multiprocessing import Process, Queue, Array, Value
import logging

import board
import busio

import rpi2c
import constants

try:
    import valve
except:
    logging.error("valve not found - using mock")
    import mock_valve as valve

try:
    import oxygen
except:
    logging.error("o2 not found - using mock")
    
    
from sensor_lps import PressureSensorLPS

i2c_in = rpi2c.rpi_i2c(1)
i2c_ex = rpi2c.rpi_i2c(3)

VCO = 2.40256
MAXPA = 4000

def check_spontaneous(pressure, breathing, assist):
    if assist.value > 0 and pressure < -(assist.value) and breathing.value == 0:
        logging.warn("spontaneous breath initiated")
        breathing.value = 1

def check_peep(pressure, breathing, peeping, peepx):
    if breathing.value == constants.EXPIRING and peeping.value != constants.CLOSED and pressure < peepx.value:
        logging.warning("crosssing peepx on expire")
        peeping.value = constants.CLOSED

def sensor_prime(pressure_in_1, pressure_in_2, pressure_ex_1, pressure_ex_2):
    for i in range(0,100):
        time.sleep(0.005)
        pressure_in_1.read()
        pressure_in_2.read()
        pressure_ex_1.read()
        pressure_ex_2.read()


def sensor_loop(times, flow, volume, tidal, o2_percent,
                pmin, pmax, expire, breathing, peeping,
                in_pressure_1, in_pressure_2, in_flow,
                ex_pressure_1, ex_pressure_2, ex_flow,
                idx, count, assist, peepx):

    # inspiration
    pressure_in_1 = PressureSensorLPS(i2c_in, address=0x5d)
    pressure_in_2 = PressureSensorLPS(i2c_in, address=0x5c)

    # expiration
    pressure_ex_1 = PressureSensorLPS(i2c_ex, address=0x5d)
    pressure_ex_2 = PressureSensorLPS(i2c_ex, address=0x5c)

    # oxygen
    o2_sensor = oxygen.OxygenADS(i2c_in)
    
    # calibration routine
    sensor_prime(pressure_in_1, pressure_in_2, pressure_ex_1, pressure_ex_2)
    pressure_in_1.zero_pressure()
    pressure_in_2.zero_pressure()
    pressure_ex_1.zero_pressure()
    pressure_ex_2.zero_pressure()
    sensor_prime(pressure_in_1, pressure_in_2, pressure_ex_1, pressure_ex_2)
    o2_sensor.calibrate()
    
    # open outfile
    fname = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.out")
    f = open(fname, "wb", 0)

    # state management
    state_breathing = 0        # valve open when breathing = 1
    state_volume_sum = 0       # accumulator to track volume (inhalation - exhalation)
    state_sample_sum = 0       # accumulator to track samples
    state_last_samples = 75    # calculated number of samples in last breath 
    state_tidal_sum = 0        # accumulator to track tidal volume (exhalation volume)
    state_last_tidal = 0       # calculated tidal volume of last breath
    state_pmin_min = MAXPA     # minimum pressure per breath cycle
    state_last_pmin = 0        # calculated min pressure in last breath cycle
    state_pmax_max = 0         # maximum pressure per breath cycle
    state_last_pmax = 0        # calculate max pressure in last breath cycle
    state_start_expire = 0     # start of last exspire
    state_last_expire = 0      # calculated expiry time per breath cycle
    
    while True:
        pressure_in_1.read()
        pressure_in_2.read()
        pressure_ex_1.read()
        pressure_ex_2.read()

        i = idx.value + 1
        if i >= count.value:
            i = 0

        # update timestamp
        ts = time.time()
        times[i] = ts
        
        # inspiration
        p1 = pressure_in_1.data.pressure
        p2 = pressure_in_2.data.pressure
        in_pressure_1[i] = p1 / 98.0665 # convert from Pa to cmH2O
        in_pressure_2[i] = p2 / 98.0665 # convert from Pa to cmH2O
        in_flow[i] = VCO * (abs(p2-p1)**0.5)
        
        # expiration
        p1 = pressure_ex_1.data.pressure
        p2 = pressure_ex_2.data.pressure
        ex_pressure_1[i] = p1 / 98.0665 # convert from Pa to cmH2O
        ex_pressure_2[i] = p2 / 98.0665 # convert from Pa to cmH2O
        ex_flow[i] = VCO * (abs(p2-p1)**0.5)
        
        # oxygen
        o2_percent[i] = o2_sensor.read()
        
        if (breathing.value == constants.INSPIRING):
            # transition from expire to inspire reset volume state calculations
            if state_breathing == 0:
                state_breathing = 1
                state_volume_sum = 0
                state_last_tidal = state_tidal_sum
                state_tidal_sum = 0
                state_last_samples = state_sample_sum
                state_sample_sum = 0
                state_last_pmin = state_pmin_min
                state_pmin_min = MAXPA
                state_last_pmax = state_pmax_max
                state_pmax_max = 0
                if state_start_expire > 0:
                    state_last_expire = ts - state_start_expire
                    state_start_expire = 0
            # update inspiration metrics
            state_volume_sum += in_flow[i]
            flow[i] = in_flow[i]

        elif breathing.value == constants.EXPIRING:
            # transition from inspire to expire capture time
            if state_breathing == 1:
                state_breathing = 0
                state_start_expire = ts
            # update expiration metrics            
            state_tidal_sum += ex_flow[i]
            state_volume_sum -= ex_flow[i]
            flow[i] = -ex_flow[i]
            
        else:
            # valves closed clear flow and volume
            flow[i] = 0
            state_volume_sum = 0

        # track min and max pressures
        peep_pressure = ex_pressure_2[i]
        check_peep(peep_pressure, breathing, peeping, peepx)
        state_pmax_max = max(state_pmax_max, peep_pressure)
        state_pmin_min = min(state_pmin_min, peep_pressure)

        state_sample_sum += 1
        volume[i] = state_volume_sum / state_last_samples * 60 # volume changes throughout breathing cycle
        tidal[i] = state_last_tidal / state_last_samples * 60  # tidal volume counted at end of breathing cycle        
        pmin[i] = state_last_pmin                              # minimum pressure at end of last breathing cycle
        pmax[i] = state_last_pmax                              # maximum pressure at end of last breathing cycle
        expire[i] = state_last_expire                          # expiration time of last breath

        check_spontaneous(in_pressure_2[i], breathing, assist)
            
        f.write(bytearray(b"%f %f %f %f %f %f %f %f %f %f\n" % (
            times[i],
            flow[i],
            volume[i],
            tidal[i],
            in_pressure_1[i],
            in_pressure_2[i],
            in_flow[i],
            ex_pressure_1[i],
            ex_pressure_2[i],
            ex_flow[i])))

        idx.value = i
        time.sleep(0.005) 
    
if __name__ == '__main__':
    idx = Value('i', 0)
    count = Value('i', 1000)
    times = Array('d', range(count.value))

    breathing = Value('i', 0)
    flow = Array('d', range(count.value))
    volume = Array('d', range(count.value))
    tidal = Array('d', range(count.value))
    pmin = Array('d', range(count.value))
    
    in_pressure_1 = Array('d', range(count.value))
    in_pressure_2 = Array('d', range(count.value))
    in_flow = Array('d', range(count.value))
    ex_pressure_1 = Array('d', range(count.value))
    ex_pressure_2 = Array('d', range(count.value))
    ex_flow = Array('d', range(count.value))
    
    p = Process(target=sensor_loop, args=(
        times, flow, volume, tidal, pmin, breathing,
        in_pressure_1, in_pressure_2, in_flow,
        ex_pressure_1, ex_pressure_2, ex_flow,
        idx, count))

    p.start()
    input()
    p.terminate()


