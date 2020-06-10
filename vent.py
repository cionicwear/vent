#!/usr/bin/env python3                                                                                                                                       

import time
import sys
import signal
import logging
import argparse
from multiprocessing import Process, Queue, Value, Array

try:
    import valve
except:
    import mock_valve as valve

try:
    import ui
except:
    import mock_ui as ui

try:
    import sensor
except:
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

MODE_VC = 0
MODE_PC = 1

class GlobalState():
    idx = Value('i', 0)
    count = Value('i', 10000)
    times = Array('d', range(10000))
    in_pressure_1 = Array('d', range(count.value))
    in_pressure_2 = Array('d', range(count.value))
    in_flow = Array('d', range(count.value))
    ex_pressure_1 = Array('d', range(count.value))
    ex_pressure_2 = Array('d', range(count.value))
    ex_flow = Array('d', range(count.value))
    flow = Array('d', range(count.value))
    breathing = Value('i', 0)
    mode = Value('i', 0)
    rr = Value('i', 0)
    vt = Value('i', 0)
    fio2 = Value('i', 0)
    peep = Value('i', 0)
    
g = GlobalState()

@app.route('/sensors')
def sensors():
    curr = g.idx.value
    last = curr - int(request.args.get('count', '20'))
    if last < 0:
        last = 0
    times = g.times[last:curr]
    values = {
        'samples' : len(times),
        'times' : times,
        'pressure' : g.in_pressure_2[last:curr],
        'flow' : g.flow[last:curr],
        'volume' : g.ex_flow[last:curr]
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
    g.mode = MODE_PC if (args.rampdn > args.inspire/2) else MODE_VC
    g.vt = (int)(args.top * 800)
    g.fio2 = 21
    print("Starting vent %d:rr %d:mode %d:vt %d:fi02" % (g.rr, g.mode, g.vt, g.fio2))
    
    # start sensor process
    p = Process(target=sensor.sensor_loop, args=(
        g.times, g.flow, g.breathing,
        g.in_pressure_1, g.in_pressure_2, g.in_flow,
        g.ex_pressure_1, g.ex_pressure_2, g.ex_flow,
        g.idx, g.count))
    p.start()

    # wait for sensors to initialize
    time.sleep(10)
    
    # start valve process
    v = Process(target=valve.valve_loop, args=(
        g.breathing,
        args.start,  args.rampup,                 # ramp up
        args.top,    args.inspire - args.rampup - args.rampdn,  # hold top
        args.pause,  args.rampdn,                 # ramp down
        args.bottom, args.expire,   # hold bottom
        args.count))
    v.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run vent')
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
    parser.add_argument('-c', '--count',  default=30,   type=int, help='number of breathing cycles')
    # run main loop
    g_args = parser.parse_args(sys.argv[1:])
    main(g_args)
    # start server
    app.run(debug=False, host='0.0.0.0', port=PORT)
    
