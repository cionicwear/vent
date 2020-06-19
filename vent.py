#!/usr/bin/env python3                                                                                                                                       

import time
import sys
import signal
import logging
import argparse
from multiprocessing import Process, Queue, Value, Array

try:
    import valve
except Exception as e:
    logging.warn(e)
    import mock_valve as valve

try:
    import ui
except Exception as e:
    logging.warn(e)
    import mock_ui as ui

try:
    import sensor
except Exception as e:
    logging.warning(e)
    import mock_sensor as sensor

    
PORT = 3000


from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'WARNING',
        'handlers': ['wsgi']
    }
})


from flask import Flask, request, render_template, jsonify
app = Flask(__name__, static_folder='static')

MODE_VC = 1
MODE_PC = 2

class GlobalState():
    idx = Value('i', 0)
    count = Value('i', 10000)
    times = Array('d', range(10000))
    # sensor streams
    in_pressure_1 = Array('d', range(count.value))
    in_pressure_2 = Array('d', range(count.value))
    in_flow = Array('d', range(count.value))
    ex_pressure_1 = Array('d', range(count.value))
    ex_pressure_2 = Array('d', range(count.value))
    ex_flow = Array('d', range(count.value))
    # derived metrics
    flow = Array('d', range(count.value))
    volume = Array('d', range(count.value))
    tidal = Array('d', range(count.value))
    pmin = Array('d', range(count.value))
    pmax = Array('d', range(count.value))
    expire = Array('d', range(count.value))
    breathing = Value('i', 0)
    # ventilator settings
    mode = MODE_VC
    inspire = 1
    rr = 60
    ie = 0.2
    vt = 600
    fio2 = 21
    peep = 5
    
g = GlobalState()

def difference(setting, measured):
    return abs(setting-measured) / setting

@app.route('/sensors')
def sensors():
    curr = g.idx.value

    o2 = 21.0 # replace with measured value
    ie = g.ie if g.expire[curr] == 0 else g.expire[curr]/g.inspire
    rr = 60.0/ie
    tidal = g.tidal[curr]
    pmin = g.pmin[curr]
    pmax = g.pmax[curr]
    
    last = curr - int(request.args.get('count', '20'))
    if last < 0:
        times = g.times[last:] + g.times[:curr]
        pressures = g.in_pressure_2[last:] + g.in_pressure_2[:curr]
        flows = g.flow[last:] + g.flow[:curr]
        volumes = g.volume[last:] + g.volume[:curr]
    else:
        times = g.times[last:curr]
        pressures = g.in_pressure_2[last:curr]
        flows = g.flow[last:curr]
        volumes = g.volume[last:curr]

         
    alarm_plat = False
    alarm_power = False
    alarm_pmax = pmax > 30  # verify hw this should be thresholded
    alarm_pmin = difference(g.peep, pmin) > 0.2
    alarm_fio2 = difference(g.fio2, o2) > 0.2
    alarm_tidal = difference(g.vt, tidal) > 0.2
    alarm_rate = difference(g.rr, rr) > 0.2
    
    values = {
        'samples'  : len(times),
        'times'    : times,
        'pressure' : pressures,
        'flow'     : flows,
        'volume'   : volumes,
        'tidal'    : tidal,
        'pmin'     : pmin,
        'pmax'     : pmax,
        'ie'       : (int)(ie),
        'rr'       : (int)(rr),
        'alarms'   : {
            'ppeak'  : alarm_pmax,
            'peep'  : alarm_pmin,
            'plat'  : alarm_plat,
            'fio2'  : alarm_fio2,
            'rate'  : alarm_rate,
            'vt'    : alarm_tidal,
            'power' : alarm_power
        }
    }
    return jsonify(values)

@app.route('/settings', methods=['POST'])
def update_sensors():
    if 'VT' in request.json:
        g.vt = request.json['VT']

    if 'RR' in request.json:
        g.rr = request.json['RR']

    if 'PEEP' in request.json:
        g.peep = request.json['PEEP']

    if 'FiO2' in request.json:
        g.fio2 = request.json['FiO2']

    return jsonify({})

@app.route('/breath', methods=['POST'])
def breath():
    seconds = int(request.form.get('seconds', '0'))
    duty = int(request.form.get('duty', '0'))
    if seconds and duty:
        valve.breath_pwm(g.breathing, duty, seconds)

    return jsonify({})

@app.route('/')
def hello():
    return render_template('index.html')

def main(args):
    # update global state based on params
    g.rr = 60 / (args.inspire + args.expire)
    g.ie = args.expire/args.inspire
    g.inspire = args.inspire
    g.mode = MODE_PC if (args.rampdn > args.inspire/2) else MODE_VC
    g.vt = (int)(args.top * 6)
    g.fio2 = 21
    print("Starting vent %d:rr %d:mode %d:vt %d:fi02" % (g.rr, g.mode, g.vt, g.fio2))

    # start sensor process
    p = Process(target=sensor.sensor_loop, args=(
        g.times, g.flow, g.volume, g.tidal,
        g.pmin, g.pmax, g.expire, g.breathing,
        g.in_pressure_1, g.in_pressure_2, g.in_flow,
        g.ex_pressure_1, g.ex_pressure_2, g.ex_flow,
        g.idx, g.count, args.assist))
    p.start()

    # wait for sensors to initialize
    time.sleep(10)
    
    # start valve process
    v = Process(target=valve.valve_loop, args=(
        g.breathing,
        args.start,  args.rampup,
        args.top,    args.inspire - args.rampup - args.rampdn,
        args.pause,   args.rampdn,
        args.bottom, args.expire,
        args.opens,   args.count))
    v.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run vent')
    # mode
    parser.add_argument('-a', '--assist', default=0, type=float, help='pressure trigger for assist 0 = no assist')
    # times
    parser.add_argument('-i', '--inspire', default=1.0, type=float, help='seconds of inspiration time')
    parser.add_argument('-e', '--expire',  default=2.0, type=float, help='seconds of expiration time')
    parser.add_argument('-u', '--rampup',  default=0.1, type=float, help='seconds to ramp from <start> to <top>')
    parser.add_argument('-d', '--rampdn',  default=0.0, type=float, help='seconds to ramp from <top> to <pause> ')
    # thresholds
    parser.add_argument('-s', '--start',   default=80,  type=int, help='percent open at start of breathing cycle')
    parser.add_argument('-t', '--top',     default=100, type=int, help='percent open at peak of breathing cycle')
    parser.add_argument('-p', '--pause',   default=0,   type=int, help='percent open at pause in breathing cycle')
    parser.add_argument('-b', '--bottom',  default=0,   type=int, help='percent open at end of breathing cycle')
    # counts
    parser.add_argument('-c', '--count',   default=30,  type=int, help='number of breathing cycles')
    parser.add_argument('-o', '--opens',   default=500, type=int, help='number of steps for peep stepper')
    # run main loop
    g_args = parser.parse_args(sys.argv[1:])
    main(g_args)
    # start server
    app.run(debug=False, host='0.0.0.0', port=PORT)
    
